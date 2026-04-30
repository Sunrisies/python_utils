## 优雅的关闭与清理

清单 21-20 中的代码通过线程池异步响应请求，这正是我们所期望的。我们收到了一些关于 `workers`、`id` 和 `thread` 字段的警告，但这些字段并没有被我们直接使用，这提醒我们还没有清理任何东西。当我们使用不太优雅的 <kbd>ctrl</kbd>-<kbd>C</kbd> 方法来停止主线程时，所有其他线程也会立即停止，即使它们正在处理请求中。

接下来，我们将实现 `Drop` 特性，以便在池中的每个线程上调用 `join`，从而让它们在关闭之前完成正在处理的请求。然后，我们将实现一种方法来通知线程应该停止接受新请求并关闭自身。为了观察这段代码的实际效果，我们将修改我们的服务器，使其在优雅地关闭线程池之前只接受两个请求。

需要注意的是：这些内容不会影响那些负责执行闭包的代码部分，因此如果我们使用线程池来实现异步运行时，这里的所有内容都将保持不变。

### 在 `ThreadPool` 上实现 `Drop` 特质

让我们从在我们的线程池中实现 `Drop` 开始。当线程池被释放时，我们的线程应该都加入进来，以确保它们能够完成自己的工作。清单 21-22 展示了对 `Drop` 实现的首次尝试；这段代码目前还无法正常工作。

**清单 21-22:** *src/lib.rs* — 当线程池超出作用域时，如何连接每个线程

```rust,ignore,does_not_compile
impl Drop for ThreadPool {
    fn drop(&mut self) {
        for worker in &mut self.workers {
            println!("Shutting down worker {}", worker.id);

            worker.thread.join().unwrap();
        }
    }
}

```

首先，我们遍历每个线程池 `workers`。我们使用 `&mut` 来进行这个操作，因为 `self` 是一个可变引用，而且我们还需要能够修改 `worker`。对于每一个 `worker`，我们打印一条消息，说明这个特定的 `Worker` 实例正在关闭。然后，我们调用 `join` 来处理那个 `Worker` 实例的线程。如果调用 `join` 失败，我们就使用 `unwrap` 让 Rust 崩溃，从而实现非优雅的关闭。

当我们编译这段代码时，会收到以下错误：

```console
$ cargo check
    Checking hello v0.1.0 (file:///projects/hello)
error[E0507]: cannot move out of `worker.thread` which is behind a mutable reference
  --> src/lib.rs:52:13
   |
52 |             worker.thread.join().unwrap();
   |             ^^^^^^^^^^^^^ ------ `worker.thread` moved due to this method call
   |             |
   |             move occurs because `worker.thread` has type `JoinHandle<()>`, which does not implement the `Copy` trait
   |
note: `JoinHandle::<T>::join` takes ownership of the receiver `self`, which moves `worker.thread`
  --> /rustc/1159e78c4747b02ef996e55082b704c09b970588/library/std/src/thread/mod.rs:1921:17

For more information about this error, try `rustc --explain E0507`.
error: could not compile `hello` (lib) due to 1 previous error

```

这个错误提示我们，由于我们只能拥有每个 `worker` 的可变借用权，而无法调用 `join`。为了解决这个问题，我们需要将线程从拥有 `thread` 的 `Worker` 实例中移出，这样 `join` 就可以接管这个线程。一种方法是采用 Listing 18-15 中描述的方法。如果 `Worker` 持有 `Option<thread::JoinHandle<()>>`，那么我们可以在 `Option` 上调用 `take` 方法，将值从 `Some` 变体中移出，并留下一个 `None` 变体来代替它。换句话说，正在运行的 `Worker` 会在 `thread` 中有一个 `Some` 变体，而当我们想要清理 `Worker` 时，我们会用 `None` 替换 `Some`，这样 `Worker` 就不会再有线程可以运行了。

不过，这种情况只会在删除`Worker`时出现。作为交换，我们必须在访问`worker.thread`时处理`Option<thread::JoinHandle<()>>`。在Rust中，通常使用`Option`作为惯用方法。但是，当你发现自己需要用`Option`来封装那些肯定会出现在`worker.thread`中的内容时，最好寻找其他方法来使代码更加简洁，减少出错的可能性。

在这种情况下，有一个更好的替代方案：`Vec::drain`方法。它接受一个范围参数来指定要从向量中移除哪些元素，并返回一个包含这些元素的迭代器。使用`..`范围语法将移除向量中的*每一个*值。

因此，我们需要像这样更新 `ThreadPool` `drop` 的实现：

<Listing file-name="src/lib.rs">

```rust
impl Drop for ThreadPool {
    fn drop(&mut self) {
        for worker in self.workers.drain(..) {
            println!("Shutting down worker {}", worker.id);

            worker.thread.join().unwrap();
        }
    }
}

```

</Listing>

这解决了编译器的错误，并且不需要对我们的代码进行任何其他修改。需要注意的是，由于 `drop` 可以在 panic 时被调用，因此 `unwrap` 也可能引发 panic，从而导致双重 panic，这会立即使程序崩溃，并终止正在进行的任何清理操作。这对于示例程序来说是可以接受的，但不建议用于生产代码。

### 通知线程停止接收任务

经过我们所做的所有修改之后，我们的代码能够编译出来，而且没有任何警告信息。然而，坏消息是，这段代码目前并没有按照我们的预期运行。问题的关键在于，由 `Worker` 实例的线程所执行的闭包中的逻辑：目前，我们调用的是 `join`，但这并不会关闭这些线程，因为它们会永远不停地寻找任务。如果我们尝试使用当前的 `drop` 实现来移除 `ThreadPool`，那么主线程将会永远等待第一个线程完成，从而导致程序卡住。

为了解决这个问题，我们需要对 `ThreadPool` `drop` 实现进行更改，然后对 `Worker` 循环进行更改。

首先，我们将更改 `ThreadPool` `drop` 的实现，以显式地跳过 `sender`，然后等待线程完成。列表 21-23 展示了对 `ThreadPool` 的更改，以显式地跳过 `sender`。与线程不同的是，在这里我们需要使用 `Option` 来允许 `sender` 通过 `Option::take` 移出 `ThreadPool`。

**清单 21-23:** *src/lib.rs* — 在连接 `Worker` 线程之前，明确弃用 `sender`

```rust,noplayground,not_desired_behavior
pub struct ThreadPool {
    workers: Vec<Worker>,
    sender: Option<mpsc::Sender<Job>>,
}
// --snip--
impl ThreadPool {
    pub fn new(size: usize) -> ThreadPool {
        // --snip--

        ThreadPool {
            workers,
            sender: Some(sender),
        }
    }

    pub fn execute<F>(&self, f: F)
    where
        F: FnOnce() + Send + 'static,
    {
        let job = Box::new(f);

        self.sender.as_ref().unwrap().send(job).unwrap();
    }
}

impl Drop for ThreadPool {
    fn drop(&mut self) {
        drop(self.sender.take());

        for worker in self.workers.drain(..) {
            println!("Shutting down worker {}", worker.id);

            worker.thread.join().unwrap();
        }
    }
}

```

放弃 `sender` 会关闭通道，这意味着将不再发送任何消息。当这种情况发生时，所有由 `Worker` 实例在无限循环中调用 `recv` 的操作都会返回错误。在 Listing 21-24 中，我们将 `Worker` 循环修改为在这种情况下优雅地退出循环，这意味着当 `ThreadPool` `drop` 实现在其上调用 `join` 时，线程将会完成。

**清单 21-24:** *src/lib.rs* — 当 `recv` 返回错误时，明确跳出循环

```rust,noplayground
impl Worker {
    fn new(id: usize, receiver: Arc<Mutex<mpsc::Receiver<Job>>>) -> Worker {
        let thread = thread::spawn(move || {
            loop {
                let message = receiver.lock().unwrap().recv();

                match message {
                    Ok(job) => {
                        println!("Worker {id} got a job; executing.");

                        job();
                    }
                    Err(_) => {
                        println!("Worker {id} disconnected; shutting down.");
                        break;
                    }
                }
            }
        });

        Worker { id, thread }
    }
}

```

为了看到这段代码的实际应用，让我们修改 `main`，使其只接受两个请求，然后在如清单 21-25 所示的情况下优雅地关闭服务器。

**列表 21-25:** *src/main.rs* — 在处理完两个请求后，通过退出循环来关闭服务器

```rust,ignore
fn main() {
    let listener = TcpListener::bind("127.0.0.1:7878").unwrap();
    let pool = ThreadPool::new(4);

    for stream in listener.incoming().take(2) {
        let stream = stream.unwrap();

        pool.execute(|| {
            handle_connection(stream);
        });
    }

    println!("Shutting down.");
}

```

你肯定不希望一个现实世界的网络服务器在只处理了两次请求之后就关闭。这段代码仅仅展示了优雅的关闭和清理过程是正常运作的。

方法 `take` 定义在 `Iterator` 特质中，并且最多将迭代限制在前两项。 `ThreadPool` 将在 `main` 结束时超出作用域，而 `drop` 实现将会运行。

使用 `cargo run` 启动服务器，并发送三个请求。第三个请求应该会出错，在终端中，你应该会看到类似这样的输出：

<!-- manual-regeneration
cd listings/ch21-web-server/listing-21-25
cargo run
curl http://127.0.0.1:7878
curl http://127.0.0.1:7878
curl http://127.0.0.1:7878
third request will error because server will have shut down
copy output below
Can't automate because the output depends on making requests
-->

```console
$ cargo run
   Compiling hello v0.1.0 (file:///projects/hello)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.41s
     Running `target/debug/hello`
Worker 0 got a job; executing.
Shutting down.
Shutting down worker 0
Worker 3 got a job; executing.
Worker 1 disconnected; shutting down.
Worker 2 disconnected; shutting down.
Worker 3 disconnected; shutting down.
Worker 0 disconnected; shutting down.
Shutting down worker 1
Shutting down worker 2
Shutting down worker 3
```

您可能会看到 `Worker` 和消息的排序有所不同。我们可以通过消息来了解这段代码的运作方式： `Worker` 的实例 0 和 3 分别接收了前两个请求。在第二个连接之后，服务器停止接受新的连接；而 `Drop` 的实现在 `ThreadPool` 开始执行之前就已经开始了。去掉 `sender` 会断开所有 `Worker` 实例的连接，并让它们停止工作。当 `Worker` 实例断开连接时，每个实例都会打印一条消息，然后线程池会调用 `join` 来等待每个 `Worker` 线程完成工作。

请注意这次执行过程中有一个有趣的现象： `ThreadPool` 取消了 `sender`，而在 `Worker` 出现错误之前，我们尝试了连接 `Worker 0`。 `Worker 0` 还没有收到来自 `recv` 的错误，因此主线程被阻塞，等待 `Worker 0` 完成。与此同时， `Worker 3` 接收到了一个任务，然后所有线程都收到了错误。当 `Worker 0` 完成后，主线程等待其余的 `Worker` 实例完成。此时，它们都已经退出了各自的循环并停止了运行。

恭喜！我们现在已经完成了项目。我们拥有一个基本的网络服务器，该服务器使用线程池来实现异步响应。我们能够优雅地关闭服务器，从而清理掉线程池中的所有线程。

以下是完整的代码供参考：

<Listing file-name="src/main.rs">

```rust,ignore
use hello::ThreadPool;
use std::{
    fs,
    io::{BufReader, prelude::*},
    net::{TcpListener, TcpStream},
    thread,
    time::Duration,
};

fn main() {
    let listener = TcpListener::bind("127.0.0.1:7878").unwrap();
    let pool = ThreadPool::new(4);

    for stream in listener.incoming().take(2) {
        let stream = stream.unwrap();

        pool.execute(|| {
            handle_connection(stream);
        });
    }

    println!("Shutting down.");
}

fn handle_connection(mut stream: TcpStream) {
    let buf_reader = BufReader::new(&stream);
    let request_line = buf_reader.lines().next().unwrap().unwrap();

    let (status_line, filename) = match &request_line[..] {
        "GET / HTTP/1.1" => ("HTTP/1.1 200 OK", "hello.html"),
        "GET /sleep HTTP/1.1" => {
            thread::sleep(Duration::from_secs(5));
            ("HTTP/1.1 200 OK", "hello.html")
        }
        _ => ("HTTP/1.1 404 NOT FOUND", "404.html"),
    };

    let contents = fs::read_to_string(filename).unwrap();
    let length = contents.len();

    let response =
        format!("{status_line}\r\nContent-Length: {length}\r\n\r\n{contents}");

    stream.write_all(response.as_bytes()).unwrap();
}

```

</Listing>

<Listing file-name="src/lib.rs">

```rust,noplayground
use std::{
    sync::{Arc, Mutex, mpsc},
    thread,
};

pub struct ThreadPool {
    workers: Vec<Worker>,
    sender: Option<mpsc::Sender<Job>>,
}

type Job = Box<dyn FnOnce() + Send + 'static>;

impl ThreadPool {
    /// Create a new ThreadPool.
    ///
    /// The size is the number of threads in the pool.
    ///
    /// # Panics
    ///
    /// The `new` function will panic if the size is zero.
    pub fn new(size: usize) -> ThreadPool {
        assert!(size > 0);

        let (sender, receiver) = mpsc::channel();

        let receiver = Arc::new(Mutex::new(receiver));

        let mut workers = Vec::with_capacity(size);

        for id in 0..size {
            workers.push(Worker::new(id, Arc::clone(&receiver)));
        }

        ThreadPool {
            workers,
            sender: Some(sender),
        }
    }

    pub fn execute<F>(&self, f: F)
    where
        F: FnOnce() + Send + 'static,
    {
        let job = Box::new(f);

        self.sender.as_ref().unwrap().send(job).unwrap();
    }
}

impl Drop for ThreadPool {
    fn drop(&mut self) {
        drop(self.sender.take());

        for worker in &mut self.workers {
            println!("Shutting down worker {}", worker.id);

            if let Some(thread) = worker.thread.take() {
                thread.join().unwrap();
            }
        }
    }
}

struct Worker {
    id: usize,
    thread: Option<thread::JoinHandle<()>>,
}

impl Worker {
    fn new(id: usize, receiver: Arc<Mutex<mpsc::Receiver<Job>>>) -> Worker {
        let thread = thread::spawn(move || {
            loop {
                let message = receiver.lock().unwrap().recv();

                match message {
                    Ok(job) => {
                        println!("Worker {id} got a job; executing.");

                        job();
                    }
                    Err(_) => {
                        println!("Worker {id} disconnected; shutting down.");
                        break;
                    }
                }
            }
        });

        Worker {
            id,
            thread: Some(thread),
        }
    }
}

```

</Listing>

我们还可以做得更多！如果您希望继续改进这个项目，以下是一些建议：

- 为 `ThreadPool` 及其公共方法添加更多文档说明。  
- 对库的功能进行测试。  
- 将 `unwrap` 的调用改为更完善的错误处理机制。  
- 使用 `ThreadPool` 执行除处理网络请求之外的其他任务。  
- 在 [crates.io](https://crates.io/) 上查找一个线程池库，并使用该库实现一个类似的网络服务器。然后，将其 API 和可靠性与我们实现的线程池进行比较。

## 摘要

做得好！你已经读完了这本书！我们想感谢你参与这次关于Rust的之旅。现在，你可以开始实现自己的Rust项目，并帮助其他人的项目了。请记住，这里有一个热情友好的Rust社区，他们很乐意在你学习Rust的过程中帮助你解决任何遇到的问题。