<!-- Old headings. Do not remove or links may break. -->

<a id="turning-our-single-threaded-server-into-a-multithreaded-server"></a>
<a id="from-single-threaded-to-multithreaded-server"></a>

## 从单线程到多线程服务器

目前，服务器会依次处理每个请求，这意味着直到第一个请求的处理完成之后，服务器才会处理第二个请求。如果服务器接收到的请求数量不断增加，这种串行处理方式会变得越来越不理想。如果服务器接收到需要长时间处理的请求，那么后续的请求将不得不等待该请求完成，即使这些新请求可以很快被处理。我们需要解决这个问题，但在那之前，我们先来看看实际情况。

<!-- Old headings. Do not remove or links may break. -->

<a id="simulating-a-slow-request-in-the-current-server-implementation"></a>

### 模拟慢速请求

我们将探讨一个处理速度较慢的请求如何影响对当前服务器实现的其他请求。清单 21-10 展示了如何处理对 _/sleep_ 的请求，该请求会模拟一个缓慢的响应，导致服务器在响应之前休眠五秒钟。

**列表 21-10:** *src/main.rs* — 通过等待五秒来模拟慢速请求

```rust,no_run
use std::{
    fs,
    io::{BufReader, prelude::*},
    net::{TcpListener, TcpStream},
    thread,
    time::Duration,
};
// --snip--

fn handle_connection(mut stream: TcpStream) {
    // --snip--

    let (status_line, filename) = match &request_line[..] {
        "GET / HTTP/1.1" => ("HTTP/1.1 200 OK", "hello.html"),
        "GET /sleep HTTP/1.1" => {
            thread::sleep(Duration::from_secs(5));
            ("HTTP/1.1 200 OK", "hello.html")
        }
        _ => ("HTTP/1.1 404 NOT FOUND", "404.html"),
    };

    // --snip--
}

```

既然我们有了三种情况，我们就从 `if` 切换到 `match`。我们需要显式地匹配 `request_line` 的切片，以便与字符串字面量进行模式匹配；而 `match` 并不像相等性方法那样进行自动引用和解除引用操作。

第一个分支与 Listing 21-9 中的 `if` 块相同。第二个分支匹配一个对 _/sleep_ 的请求。当接收到该请求时，服务器会休眠五秒钟，然后才渲染成功的 HTML 页面。第三个分支与 Listing 21-9 中的 `else` 块相同。

你可以看到我们的服务器是多么的简陋：真正的库会以更简洁的方式来处理多个请求的识别问题！

使用 `cargo run` 启动服务器。然后，打开两个浏览器窗口：一个用于 http://127.0.0.1:7878_，另一个用于 http://127.0.0.1:7878/sleep_。如果你像之前一样多次输入 _/_ URI，你会看到它能够快速响应。但是，如果你先输入 _/sleep_，然后再加载 _/_，你会发现 _//_ 会等待 `sleep` 完全睡五秒之后才会继续加载。

我们有多种技术可以用来避免慢速请求导致请求积压，包括像第17章那样使用异步处理；我们将要实现的是线程池技术。

### 使用线程池提升吞吐量

线程池是一组已经创建并准备好处理任务的线程。当程序接收到新的任务时，它会将线程池中的一个线程分配给该任务，该线程将负责处理该任务。在第一个线程处理任务的过程中，线程池中的其余线程仍然可以处理其他任务。当第一个线程完成其任务后，它会返回到空闲线程池中，准备处理新的任务。线程池允许你同时处理多个任务，从而提高服务器的吞吐量。

我们将限制池中的线程数量，使其保持在较低水平，以此来防范DoS攻击。如果我们让程序在接收到每个请求时都创建一个新的线程，那么向我们的服务器发送1000万次请求的人可能会耗尽所有服务器资源，导致请求处理完全停止。

与其创建无限数量的线程，不如限制线程的数量。等待的线程数量也是固定的。新产生的请求会被发送到这些线程中进行处理。线程池会维护一个请求队列。池中的每个线程会从队列中取出一个请求进行处理，然后向队列中请求另一个请求。通过这种设计，我们可以同时处理 _`N`_ 个请求，其中 _`N`_ 是线程的数量。如果每个线程都在处理一个耗时较长的请求，那么后续的请求仍然可以排队等待，但我们能够处理的耗时较长的请求数量已经增加了。

这种技术只是提高网络服务器吞吐量方法的其中之一。你还可以尝试使用分叉/合并模型、单线程异步I/O模型和多线程异步I/O模型。如果你对这个话题感兴趣，可以阅读更多关于其他解决方案的内容，并尝试实现它们；使用像Rust这样的低级语言，所有这些选项都是可行的。

在开始实现线程池之前，我们先来了解一下使用线程池应该是什么样的。在设计代码时，首先编写客户端接口可以帮助指导你的设计思路。编写代码的API，使其以你希望调用它的方式结构化；然后，在该结构内实现功能，而不是先实现功能后再设计公共API。

与我们在第12章中在项目中使用测试驱动开发的方式类似，我们在这里也会使用编译器驱动开发。我们将编写调用我们想要调用的函数的代码，然后通过分析编译器的错误信息来确定接下来需要修改哪些部分，以使代码能够正常工作。然而，在这样做之前，我们将先探讨一下我们不会使用的技术作为起点。

<!-- Old headings. Do not remove or links may break. -->

<a id="code-structure-if-we-could-spawn-a-thread-for-each-request"></a>

#### 为每个请求创建一个线程

首先，让我们探讨一下，如果我们的代码为每个连接都创建一个新的线程，那么代码会是什么样子。如前所述，由于可能存在无限创建线程的问题，这并不是我们的最终方案。不过，这确实是一个起点，可以帮助我们先实现一个功能完备的多线程服务器。之后，我们会引入线程池作为改进措施，这样对比这两种解决方案就会更加容易了。

清单21-11展示了为了在 `for` 循环中为每个流创建一个新的线程而需要对 `main` 所做的修改。

**清单 21-11:** *src/main.rs* — 为每个流创建一个新的线程

```rust,no_run
fn main() {
    let listener = TcpListener::bind("127.0.0.1:7878").unwrap();

    for stream in listener.incoming() {
        let stream = stream.unwrap();

        thread::spawn(|| {
            handle_connection(stream);
        });
    }
}

```

正如你在第16章中学到的那样，`thread::spawn`会创建一个新的线程，然后在新线程中运行闭包中的代码。如果你运行这段代码，并在浏览器中加载_/sleep_，那么在另外两个浏览器标签页中加载_/_，你确实会看到对_/_的请求不必等待_/sleep_完成。然而，正如我们之前提到的，这样做最终会使系统不堪重负，因为你会无限制地创建新线程。

你可能还记得第17章中的内容，这正是那种异步和等待技术发挥作用的场景！在构建线程池时，请记住这一点，并思考如果采用异步处理，情况会如何变化，或者仍然保持不变。

<!-- Old headings. Do not remove or links may break. -->

<a id="creating-a-similar-interface-for-a-finite-number-of-threads"></a>

#### 创建有限数量的线程

我们希望我们的线程池能够以类似且熟悉的方式运行，这样在从线程切换到线程池时，不会对使用我们API的代码进行大的修改。列表21-12展示了我们希望使用的 `ThreadPool` 结构的假设性接口。

**清单 21-12:** *src/main.rs* — 我们理想的 `ThreadPool` 接口

```rust,ignore,does_not_compile
fn main() {
    let listener = TcpListener::bind("127.0.0.1:7878").unwrap();
    let pool = ThreadPool::new(4);

    for stream in listener.incoming() {
        let stream = stream.unwrap();

        pool.execute(|| {
            handle_connection(stream);
        });
    }
}

```

我们使用 `ThreadPool::new` 来创建一个具有可配置线程数的新线程池，在这个例子中是四个线程。然后，在 `for` 循环中， `pool.execute` 的接口与 `thread::spawn` 类似，它接受一个闭包，该闭包指定了线程池应该为每个流运行。我们需要实现 `pool.execute`，以便它能够接受这个闭包，并将其传递给线程池中的某个线程来运行。这段代码目前还不能编译，但我们会尝试编译，以便编译器能够指导我们如何修复它。

<!-- Old headings. Do not remove or links may break. -->

<a id="building-the-threadpool-struct-using-compiler-driven-development"></a>

#### 使用编译器驱动的开发方式构建 `ThreadPool`

请对 Listing 21-12 中的代码进行以下修改，将其保存在 _src/main.rs_ 文件中。然后，我们可以利用 `cargo check` 产生的编译错误来指导我们的开发过程。这是我们遇到的第一个错误：

```console
$ cargo check
    Checking hello v0.1.0 (file:///projects/hello)
error[E0433]: failed to resolve: use of undeclared type `ThreadPool`
  --> src/main.rs:11:16
   |
11 |     let pool = ThreadPool::new(4);
   |                ^^^^^^^^^^ use of undeclared type `ThreadPool`

For more information about this error, try `rustc --explain E0433`.
error: could not compile `hello` (bin "hello") due to 1 previous error

```

太好了！这个错误告诉我们我们需要一个 `ThreadPool` 类型或模块，所以我们现在就创建一个。我们的 `ThreadPool` 实现将不受我们的网络服务器正在执行的工作类型的影响。因此，我们将 `hello`  crate 从二进制 crate 更改为库 crate，以便存放我们的 `ThreadPool` 实现。在改为库 crate 之后，我们还可以使用单独的线程池库来处理任何需要使用线程池的工作，而不仅仅是为了处理网络请求。

请创建一个 `_src/lib.rs` 文件，其中包含以下代码，这是目前我们能够定义的最简单的 `ThreadPool` 结构的定义：

<Listing file-name="src/lib.rs">

```rust,noplayground
pub struct ThreadPool;

```

</Listing>

然后，编辑 _main.rs_ 文件，将 `ThreadPool` 从 crate 库中引入，方法是在 _src/main.rs_ 文件的顶部添加以下代码：

<Listing file-name="src/main.rs">

```rust,ignore
use hello::ThreadPool;

```

</Listing>

这段代码仍然无法运行，但让我们再次检查一下，以找出我们需要解决的下一个错误。

```console
$ cargo check
    Checking hello v0.1.0 (file:///projects/hello)
error[E0599]: no function or associated item named `new` found for struct `ThreadPool` in the current scope
  --> src/main.rs:12:28
   |
12 |     let pool = ThreadPool::new(4);
   |                            ^^^ function or associated item not found in `ThreadPool`

For more information about this error, try `rustc --explain E0599`.
error: could not compile `hello` (bin "hello") due to 1 previous error

```

这个错误表明，接下来我们需要为 `ThreadPool` 创建一个名为 ⊃`new` 的相关函数。我们还知道，⊃`new` 需要有一个参数，该参数能够接受 `4` 作为参数，并且应该返回一个 `ThreadPool` 实例。让我们来实现一个最简单的具有这些特性的 `new` 函数：

<Listing file-name="src/lib.rs">

```rust,noplayground
pub struct ThreadPool;

impl ThreadPool {
    pub fn new(size: usize) -> ThreadPool {
        ThreadPool
    }
}

```

</Listing>

我们选择 `usize` 作为 `size` 参数的类型，因为我们知道，线程数量为零是没有意义的。我们还知道，我们将使用 `4` 来表示线程集合中的元素数量，正如在第三章的 [“Integer Types”][integer-types]<!--
ignore --> 部分所讨论的， `usize` 类型正是用于这个目的。

让我们再次检查这段代码：

```console
$ cargo check
    Checking hello v0.1.0 (file:///projects/hello)
error[E0599]: no method named `execute` found for struct `ThreadPool` in the current scope
  --> src/main.rs:17:14
   |
17 |         pool.execute(|| {
   |         -----^^^^^^^ method not found in `ThreadPool`

For more information about this error, try `rustc --explain E0599`.
error: could not compile `hello` (bin "hello") due to 1 previous error

```

现在出现错误的原因是我们在 `ThreadPool` 上没有 `execute` 方法。  
回想一下在 [“创建有限数量的线程”](#creating-a-finite-number-of-threads)<!-- ignore --> 部分的内容，我们决定让线程池具有类似于 `thread::spawn` 的接口。此外，我们还将实现 `execute` 函数，该函数接收给定的闭包，并将其分配给线程池中的空闲线程来运行。

我们将在 `ThreadPool` 上定义 `execute` 方法，该方法接受一个闭包作为参数。回顾第13章中的 [“Moving Captured Values Out of
Closures”][moving-out-of-closures]<!-- ignore -->，我们知道可以用三种不同的特征来接受闭包作为参数： `Fn`、 `FnMut` 和 `FnOnce`。我们需要决定在这里使用哪种类型的闭包。我们知道最终会采用类似于标准库 `thread::spawn` 的实现方式，因此我们可以查看 `thread::spawn` 的签名对其参数的限制。文档中提供了以下信息：

```rust,ignore
pub fn spawn<F, T>(f: F) -> JoinHandle<T>
    where
        F: FnOnce() -> T,
        F: Send + 'static,
        T: Send + 'static,
```

在这里，我们关注的是 `F` 类型参数；而 `T` 类型参数则与返回值相关，我们并不关心这一点。我们可以看到， `spawn` 使用 `FnOnce` 作为 `F` 的特质绑定。这很可能正是我们所需要的，因为最终我们会将 `execute` 中得到的参数传递给 `spawn`。我们可以更有信心地认为 `FnOnce` 就是我们想要使用的特质，因为执行请求的任务只会执行一次该请求的闭包，这与 `Once` 在 `FnOnce` 中的行为是一致的。

这种 `F` 类型参数还具有 `Send` 特征绑定和 `'static` 生命周期绑定，这在我们的场景中非常有用：我们需要 `Send` 来将闭包从一个线程转移到另一个线程，同时还需要 `'static`，因为我们不知道线程执行所需的时间。让我们在 `ThreadPool` 上创建一个 `execute` 方法，该方法将接受一个类型为 `F` 的通用参数，并且具有这些绑定：

<Listing file-name="src/lib.rs">

```rust,noplayground
impl ThreadPool {
    // --snip--
    pub fn execute<F>(&self, f: F)
    where
        F: FnOnce() + Send + 'static,
    {
    }
}

```

</Listing>

我们仍然在 `FnOnce` 之后使用 `FnOnce`，因为 `FnOnce` 代表一个闭包，它不接受任何参数，并且返回单位类型 `()`。就像函数定义一样，返回类型可以从签名中省略，但即使我们没有参数，仍然需要括号。

再次说明，这是 `execute` 方法的最简单实现：它实际上并没有做什么实质性的操作，但我们只是想让代码能够编译出来而已。让我们再检查一下吧：

```console
$ cargo check
    Checking hello v0.1.0 (file:///projects/hello)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.24s

```

它已经编译成功了！不过请注意，如果您尝试使用 `cargo run`，并在浏览器中发起请求，您将会看到我们在章节开头看到的那些错误。实际上，我们的库还没有调用传递给 `execute` 的闭包！

>注意：关于那些使用严格编译器的语言，比如Haskell和Rust，人们常说“如果代码能够编译出来，那就说明它是正确的”。不过，这句话并不适用于所有情况。我们的项目虽然能够编译出来，但实际上它根本没有任何功能！如果我们正在构建一个真正完整的项目，现在正是开始编写单元测试的时候，以验证代码不仅能够编译出来，而且其行为符合我们的期望。

请考虑：如果我们执行的是未来操作，而不是闭包操作，会有什么不同？

#### 验证 `new` 中线程的数量

我们并没有对 `new` 和 `execute` 参数做任何操作。让我们按照想要的行为来实现这些函数的主体部分。首先，让我们来思考一下 `new`。之前我们为 `size` 参数选择了一个无符号类型，因为拥有负数线程数是不可能的。同样地，拥有零线程数也是不合适的，不过零仍然是一个完全有效的 `usize`。我们将添加代码来检查 `size` 是否大于零，然后再返回 `ThreadPool` 的实例。如果使用 `assert!` 宏来接收零值，程序将会出现 panic 错误，如清单 21-13 所示。

**列表 21-13:** *src/lib.rs* — 实现 `ThreadPool::new`，如果 `size` 为零则触发 panic 异常

```rust,noplayground
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

        ThreadPool
    }

    // --snip--
}

```

我们还为我们的 `ThreadPool` 添加了一些文档说明，并使用了文档注释。请注意，我们遵循了良好的文档编写规范，添加了一个部分来指出我们的函数可能会陷入恐慌的情况，这一点在第14章中有详细讨论。尝试运行 `cargo doc --open`，并点击 `ThreadPool` 结构体，看看 `new` 生成的文档是什么样子吧！

与其像这里那样添加 `assert!` 宏，我们不如将 `new` 改为 `build`，并像在 Listing 12-9 中的 I/O 项目中那样返回 `Result`，就像我们对 `Config::build` 所做的那样。但在这种情况下，我们决定尝试创建一个没有线程的线程池将是一个无法恢复的错误。如果你有雄心壮志，可以尝试编写一个名为 `build` 的函数，其签名如下，以便与 `new` 函数进行比较：

```rust,ignore
pub fn build(size: usize) -> Result<ThreadPool, PoolCreationError> {
```

#### 创建存储线程的空间

现在我们已经有了一种方法来判断是否有足够数量的线程可以存储到该池中，那么我们就可以创建这些线程，并将它们存储到 `ThreadPool` 结构中，然后再返回这个结构。但是，我们该如何“存储”一个线程呢？让我们再仔细看看 `thread::spawn` 的签名：

```rust,ignore
pub fn spawn<F, T>(f: F) -> JoinHandle<T>
    where
        F: FnOnce() -> T,
        F: Send + 'static,
        T: Send + 'static,
```

函数 `spawn` 返回一个 `JoinHandle<T>`，其中 `T` 是闭包返回的类型。让我们尝试使用 `JoinHandle` 看看会发生什么。在我们的例子中，我们传递给线程池的闭包将负责处理连接，并不会返回任何内容，因此 `T` 将是一个单位类型 `()`。

Listing 21-14 中的代码可以编译，但目前它并没有创建任何线程。  
我们修改了 `ThreadPool` 的定义，使其能够存储一个包含 `thread::JoinHandle<()>` 实例的向量，并为该向量分配了 `size` 的容量，同时设置了一个 `for` 循环来运行代码以创建线程，最后返回了一个包含这些线程的 `ThreadPool` 实例。

**清单 21-14:** *src/lib.rs* — 创建一个向量，用于存放线程，该向量属于 `ThreadPool` 类型

```rust,ignore,not_desired_behavior
use std::thread;

pub struct ThreadPool {
    threads: Vec<thread::JoinHandle<()>>,
}

impl ThreadPool {
    // --snip--
    pub fn new(size: usize) -> ThreadPool {
        assert!(size > 0);

        let mut threads = Vec::with_capacity(size);

        for _ in 0..size {
            // create some threads and store them in the vector
        }

        ThreadPool { threads }
    }
    // --snip--
}

```

我们在库代码中引入了 `std::thread`，因为我们使用 `thread::JoinHandle` 作为 `ThreadPool` 中向量的元素类型。

一旦接收到有效的尺寸，我们的 `ThreadPool` 会创建一个新的向量，该向量能够容纳 `size` 元素。 `with_capacity` 函数执行的任务与 `Vec::new` 相同，但有一个重要的区别：它会在向量中预先分配空间。因为我们知道需要在向量中存储 `size` 元素，所以这种预先分配空间的方式比在插入元素时动态调整大小的 `Vec::new` 更高效。

当你再次运行 `cargo check` 时，应该会成功。

<!-- Old headings. Do not remove or links may break. -->
<a id ="a-worker-struct-responsible-for-sending-code-from-the-threadpool-to-a-thread"></a>

#### 将代码从 `ThreadPool` 发送到线程

我们在 Listing 21-14 中的 `for` 循环中留下了一条关于线程创建的注释。在这里，我们将探讨如何实际创建线程。标准库提供了 `thread::spawn` 方法来创建线程，而 `thread::spawn` 则期望在线程创建后能够立即运行某些代码。然而，在我们的案例中，我们希望创建线程并让它们 _等待_ 稍后发送的代码。标准库对线程的实现并没有提供这样的功能；我们必须手动实现它。

我们将通过在`ThreadPool`和负责管理这种新行为的线程之间引入一种新的数据结构来实现这种行为。我们将这种数据结构称为_Worker_，这是池化实现中常用的术语。`Worker`负责获取需要运行的代码，并在其线程中执行这些代码。

想象一下餐厅厨房里的工作人员：他们等待顾客下单，然后负责处理这些订单并制作相应的菜肴。

与其在线程池中存储一个 `JoinHandle<()>` 实例的向量，我们将存储 `Worker` 结构的实例。每个 `Worker` 将存储一个单独的 `JoinHandle<()>` 实例。然后，我们将在 `Worker` 上实现一个方法，该方法会接收一个用于执行的代码闭包，并将其发送到已经运行的线程中进行执行。此外，我们还会为每个 `Worker` 提供一个 `id`，以便在日志记录或调试时区分线程池中的不同 `Worker` 实例。

这是当我们创建 `ThreadPool` 时将会发生的新过程。在通过这种方式设置 `Worker` 之后，我们将实现将闭包发送到线程的代码：

1. 定义一个 `Worker` 结构体，该结构体包含一个 `id` 和一个 `JoinHandle<()>`。
2. 将 `ThreadPool` 修改为包含一个 `Worker` 实例的向量。
3. 定义一个 `Worker::new` 函数，该函数接受一个 `id` 数字，并返回一个 `Worker` 实例，该实例包含 `id`，并且该实例所生成的线程具有一个空的闭包。
4. 在 `ThreadPool::new` 中，使用 `for` 循环计数器来生成一个 `id`，创建一个新的 `Worker` 使用该 `id`，并将 `Worker` 存储在该向量中。

如果你愿意接受挑战，请在查看 Listing 21-15 中的代码之前，尝试自己实现这些更改。

准备好了吗？以下是 Listing 21-15，它展示了进行上述修改的一种方法。

**清单 21-15:** *src/lib.rs* — 修改 `ThreadPool` 以持有 `Worker` 实例，而不是直接持有线程

```rust,noplayground
use std::thread;

pub struct ThreadPool {
    workers: Vec<Worker>,
}

impl ThreadPool {
    // --snip--
    pub fn new(size: usize) -> ThreadPool {
        assert!(size > 0);

        let mut workers = Vec::with_capacity(size);

        for id in 0..size {
            workers.push(Worker::new(id));
        }

        ThreadPool { workers }
    }
    // --snip--
}

struct Worker {
    id: usize,
    thread: thread::JoinHandle<()>,
}

impl Worker {
    fn new(id: usize) -> Worker {
        let thread = thread::spawn(|| {});

        Worker { id, thread }
    }
}

```

我们将 `ThreadPool` 字段的名称从 `threads` 更改为 `workers`，因为现在它存储的是 `Worker` 实例，而不是 `JoinHandle<()>` 实例。我们在 `for` 循环中使用计数器作为 `Worker::new` 的参数，并将每个新的 `Worker` 存储在名为 `workers` 的向量中。

外部代码（比如我们的服务器在`_src/main.rs_`中）不需要了解在`_src/main.rs_`中使用`_src/main.rs_`内定义的`_src/main.rs_`的实现细节。因此，我们将`_src/main.rs_`中的`_src/main.rs_`定义为私有变量，同时将其函数也定义为私有函数。`_src/main.rs_`中的`_src/main.rs_`函数会使用我们提供的`_src/main.rs_`，并创建一个通过空闭包创建的新线程来生成的私有实例。

>注意：如果操作系统由于系统资源不足而无法创建线程，那么 `thread::spawn` 将会引发恐慌。这将导致整个服务器陷入恐慌状态，尽管某些线程的创建可能成功。为了简单起见，这种行为是可以接受的，但在实际的生产环境线程池实现中，你通常会使用 [`std::thread::Builder`][builder]<!-- ignore --> 及其返回 `Result` 的 [`spawn`][builder-spawn]<!-- ignore --> 方法。

这段代码将会被编译，并将存储我们作为参数传递给 `ThreadPool::new` 的 `Worker` 实例的数量。但是，我们仍然没有处理在 `execute` 中得到的闭包。接下来，让我们看看如何解决这个问题。

#### 通过通道向线程发送请求

接下来我们要解决的问题是，给 `thread::spawn` 提供的闭包根本没有任何作用。目前，我们能够得到想要在 `execute` 方法中执行的闭包。但是，在创建 `ThreadPool` 时，我们需要给 `thread::spawn` 一个闭包，以便在 `Worker` 被创建时运行。

我们希望刚刚创建的 `Worker` 结构体能够从 `ThreadPool` 中持有的队列中获取要运行的代码，并将该代码发送到相应的线程中进行运行。

我们在第16章中了解的通道——一种在两个线程之间进行通信的简单方式——非常适合这种应用场景。我们将使用通道作为任务队列，而 `execute` 会将任务从 `ThreadPool` 发送到 `Worker` 实例，后者会将任务分配给相应的线程进行处理。以下是具体的实施方案：

1. 该 `ThreadPool` 会创建一个通道，并保留发送者信息。
2. 每个 `Worker` 会保留接收者信息。
3. 我们将创建一个新的 `Job` 结构体，用来保存我们想通过通道发送的开闭包。
4. `execute` 方法会通过发送者来发送它想要执行的任务。
5. 在其线程中， `Worker` 会遍历其接收者，并执行接收到的任何任务的开闭包。

让我们首先在 `ThreadPool::new` 中创建一个通道，并将发送者保存在 `ThreadPool` 实例中，如清单 21-16 所示。目前 `Job` 结构并不包含任何内容，但将来它将是我们通过通道发送内容的类型。

**清单 21-16:** *src/lib.rs* — 修改 `ThreadPool` 以存储发送通道的发送者，该通道传输 `Job` 实例

```rust,noplayground
use std::{sync::mpsc, thread};

pub struct ThreadPool {
    workers: Vec<Worker>,
    sender: mpsc::Sender<Job>,
}

struct Job;

impl ThreadPool {
    // --snip--
    pub fn new(size: usize) -> ThreadPool {
        assert!(size > 0);

        let (sender, receiver) = mpsc::channel();

        let mut workers = Vec::with_capacity(size);

        for id in 0..size {
            workers.push(Worker::new(id));
        }

        ThreadPool { workers, sender }
    }
    // --snip--
}

```

在 `ThreadPool::new` 中，我们创建了新的通道，并让 pool 对象持有发送者。这样就能成功编译了。

让我们尝试将通道的接收者传递给每个 `Worker`，这样线程池在创建通道时就可以使用这个接收者。我们知道，我们希望在生成 `Worker` 实例的线程中使用这个接收者，因此我们将在闭包中引用 `receiver` 参数。Listing 21-17 中的代码目前还不能编译成功。

**清单 21-17:** *src/lib.rs* — 将接收者传递给每个 `Worker`

```rust,ignore,does_not_compile
impl ThreadPool {
    // --snip--
    pub fn new(size: usize) -> ThreadPool {
        assert!(size > 0);

        let (sender, receiver) = mpsc::channel();

        let mut workers = Vec::with_capacity(size);

        for id in 0..size {
            workers.push(Worker::new(id, receiver));
        }

        ThreadPool { workers, sender }
    }
    // --snip--
}

// --snip--

impl Worker {
    fn new(id: usize, receiver: mpsc::Receiver<Job>) -> Worker {
        let thread = thread::spawn(|| {
            receiver;
        });

        Worker { id, thread }
    }
}

```

我们进行了一些简单直接的修改：我们将接收者传递给`Worker::new`，然后在闭包内部使用它。

当我们尝试检查这段代码时，出现了以下错误：

```console
$ cargo check
    Checking hello v0.1.0 (file:///projects/hello)
error[E0382]: use of moved value: `receiver`
  --> src/lib.rs:26:42
   |
21 |         let (sender, receiver) = mpsc::channel();
   |                      -------- move occurs because `receiver` has type `std::sync::mpsc::Receiver<Job>`, which does not implement the `Copy` trait
...
25 |         for id in 0..size {
   |         ----------------- inside of this loop
26 |             workers.push(Worker::new(id, receiver));
   |                                          ^^^^^^^^ value moved here, in previous iteration of loop
   |
note: consider changing this parameter type in method `new` to borrow instead if owning the value isn't necessary
  --> src/lib.rs:47:33
   |
47 |     fn new(id: usize, receiver: mpsc::Receiver<Job>) -> Worker {
   |        --- in this method       ^^^^^^^^^^^^^^^^^^^ this parameter takes ownership of the value
help: consider moving the expression out of the loop so it is only moved once
   |
25 ~         let mut value = Worker::new(id, receiver);
26 ~         for id in 0..size {
27 ~             workers.push(value);
   |

For more information about this error, try `rustc --explain E0382`.
error: could not compile `hello` (lib) due to 1 previous error

```

这段代码试图将 `receiver` 传递给多个 `Worker` 实例。这是不可行的，正如你在第16章《通道实现》中所了解的那样，Rust 提供的通道是多个 _生产者_，单个 _消费者_。这意味着我们不能通过克隆通道的接收端来修复这个问题。同时，我们也不希望向多个消费者发送多次消息；我们希望有一个消息列表，其中包含多个 `Worker` 实例，这样每条消息都能被处理一次。

此外，将某个任务从通道队列中移除会涉及到对`receiver`的修改，因此线程需要一种安全的方式来共享和修改`receiver`；否则，我们可能会遇到竞态条件（如第16章中所介绍的）。

请回顾第16章中讨论的线程安全智能指针：用于在多个线程之间共享所有权，并允许线程修改值。为此，我们需要使用 `Arc<Mutex<T>>` 类型。 `Arc` 类型允许多个 `Worker` 实例共享接收者，而 `Mutex` 则确保一次只有一个 `Worker` 实例从接收者处获取数据。列表21-18展示了我们需要进行的修改。

**清单 21-18:** *src/lib.rs* — 使用 `Arc` 和 `Mutex` 在 `Worker` 实例之间共享接收者

```rust,noplayground
use std::{
    sync::{Arc, Mutex, mpsc},
    thread,
};
// --snip--

impl ThreadPool {
    // --snip--
    pub fn new(size: usize) -> ThreadPool {
        assert!(size > 0);

        let (sender, receiver) = mpsc::channel();

        let receiver = Arc::new(Mutex::new(receiver));

        let mut workers = Vec::with_capacity(size);

        for id in 0..size {
            workers.push(Worker::new(id, Arc::clone(&receiver)));
        }

        ThreadPool { workers, sender }
    }

    // --snip--
}

// --snip--

impl Worker {
    fn new(id: usize, receiver: Arc<Mutex<mpsc::Receiver<Job>>>) -> Worker {
        // --snip--
    }
}

```

在 `ThreadPool::new` 中，我们将接收者放入 `Arc` 和 `Mutex` 中。对于每个新的 `Worker`，我们克隆 `Arc` 以增加引用计数，这样 `Worker` 实例就可以共享接收者的所有权。

经过这些修改后，代码已经可以编译了！我们即将成功！

#### 实现 `execute` 方法

让我们最终在 `ThreadPool` 上实现 `execute` 方法。我们还将把 `Job` 从结构体改为类型别名，用于表示一个持有 `execute` 接收的闭包类型的特征对象。正如第20章中的 [“Type Synonyms and Type
Aliases”][type-aliases]<!-- ignore --> 部分所讨论的，类型别名可以帮助我们使较长的类型更简洁，便于使用。请查看 Listing 21-19。

**清单 21-19:** *src/lib.rs* — 为包含多个闭包的 `Box` 类型创建一个 `Job` 类型别名，然后通过通道传递任务。

```rust,noplayground
// --snip--

type Job = Box<dyn FnOnce() + Send + 'static>;

impl ThreadPool {
    // --snip--

    pub fn execute<F>(&self, f: F)
    where
        F: FnOnce() + Send + 'static,
    {
        let job = Box::new(f);

        self.sender.send(job).unwrap();
    }
}

// --snip--

```

在使用闭包创建新的 `Job` 实例之后，我们将该实例发送到通道的发送端。如果发送失败，我们会调用 `unwrap` 来处理这种情况。这种情况可能发生在我们停止所有线程执行的时候，也就是说，接收端不再接收新的消息。目前，我们无法停止线程的执行：只要线程池存在，我们的线程就会继续执行。我们使用 `unwrap` 的原因是我们知道这种失败情况不会发生，但编译器并不清楚这一点。

但是，我们还没有完成！在 `Worker` 中，我们的闭包被传递给 `thread::spawn`，但它仍然只是_引用_通道的接收端。相反，我们需要让闭包永远循环下去，向通道的接收端请求任务，并在接收到任务时执行该任务。让我们在 Listing 21-20 中进行的修改，使其变为 `Worker::new`。

**列表 21-20:** *src/lib.rs* — 在 `Worker` 实例的线程中接收并执行任务

```rust,noplayground
// --snip--

impl Worker {
    fn new(id: usize, receiver: Arc<Mutex<mpsc::Receiver<Job>>>) -> Worker {
        let thread = thread::spawn(move || {
            loop {
                let job = receiver.lock().unwrap().recv().unwrap();

                println!("Worker {id} got a job; executing.");

                job();
            }
        });

        Worker { id, thread }
    }
}

```

首先，我们调用 `receiver` 来获取互斥锁，然后调用 `unwrap` 来处理任何错误。如果互斥锁处于 _中毒_ 状态，获取锁可能会失败。这种情况可能发生在其他线程在持有锁时没有释放锁的情况下导致自身 panic。在这种情况下，调用 `unwrap` 让该线程 panic 是正确的操作。你可以自由地将 `unwrap` 替换为 `expect`，并在其中添加对你有意义的错误信息。

如果我们成功获得了互斥锁的锁定，就会调用 `recv` 来从通道中接收 `Job`。最后的 `unwrap` 可以处理这里可能出现的任何错误，这些错误可能发生在持有发送者的线程关闭时。类似于 `send` 方法在接收者关闭时返回 `Err` 的情况。

调用 `recv` 会阻塞线程，因此如果没有任务可用，当前线程将等待，直到有任务可用为止。 `Mutex<T>` 则确保一次只有一个 `Worker` 线程尝试请求任务。

我们的线程池现在处于正常工作状态！给它施加 `cargo run` 并发起一些请求：

<!-- manual-regeneration
cd listings/ch21-web-server/listing-21-20
cargo run
make some requests to 127.0.0.1:7878
Can't automate because the output depends on making requests
-->

```console
$ cargo run
   Compiling hello v0.1.0 (file:///projects/hello)
warning: field `workers` is never read
 --> src/lib.rs:7:5
  |
6 | pub struct ThreadPool {
  |            ---------- field in this struct
7 |     workers: Vec<Worker>,
  |     ^^^^^^^
  |
  = note: `#[warn(dead_code)]` on by default

warning: fields `id` and `thread` are never read
  --> src/lib.rs:48:5
   |
47 | struct Worker {
   |        ------ fields in this struct
48 |     id: usize,
   |     ^^
49 |     thread: thread::JoinHandle<()>,
   |     ^^^^^^

warning: `hello` (lib) generated 2 warnings
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 4.91s
     Running `target/debug/hello`
Worker 0 got a job; executing.
Worker 2 got a job; executing.
Worker 1 got a job; executing.
Worker 3 got a job; executing.
Worker 0 got a job; executing.
Worker 2 got a job; executing.
Worker 1 got a job; executing.
Worker 3 got a job; executing.
Worker 0 got a job; executing.
Worker 2 got a job; executing.
```

成功！我们现在拥有一个能够异步执行连接的线程池。
创建的线程数量永远不会超过四个，因此如果服务器接收到大量请求，我们的系统也不会出现负载过重的情况。如果我们向 _/sleep_ 发起请求，服务器可以通过让另一个线程来处理这些请求来继续服务其他请求。

>注意：如果您同时在多个浏览器窗口中打开 _/sleep_ 功能，它们可能会以每五秒一次的频率依次加载。某些网络浏览器出于缓存原因，会顺序执行同一请求的多个实例。这种限制并非由我们的网络服务器引起的。

现在是一个很好的时机，让我们暂停一下，思考一下如果使用 futures 而不是闭包来完成任务的话，Listings 21-18、21-19 和 21-20 中的代码会有哪些不同。哪些类型会发生变化？方法签名会有什么不同，如果有的话？代码的哪些部分会保持不变？

在了解了第17章和第19章中的 `while let` 循环之后，你可能会想知道为什么我们没有像 Listing 21-21 中那样编写 `Worker` 线程代码。

**清单 21-21:** *src/lib.rs* — 使用 `while let` 的 `Worker::new` 的另一种实现方式

```rust,ignore,not_desired_behavior
// --snip--

impl Worker {
    fn new(id: usize, receiver: Arc<Mutex<mpsc::Receiver<Job>>>) -> Worker {
        let thread = thread::spawn(move || {
            while let Ok(job) = receiver.lock().unwrap().recv() {
                println!("Worker {id} got a job; executing.");

                job();
            }
        });

        Worker { id, thread }
    }
}

```

这段代码可以编译并运行，但并不能实现预期的线程处理行为：一个处理速度较慢的请求仍然会导致其他请求等待处理。原因有些微妙：这个 `Mutex` 结构体没有公开的 `unlock` 方法，因为锁的所有权是基于该 `MutexGuard<T>` 在 `LockResult<MutexGuard<T>>` 中的生命周期来决定的，而 `lock` 方法就返回在这个 `LockResult<MutexGuard<T>>` 中。在编译时，借用检查器可以强制执行这样的规则：除非我们持有锁，否则不能访问由 `Mutex` 保护的资源。然而，如果我们不注意 `MutexGuard<T>` 的生命周期，这种实现也可能导致锁被持有的时间超过预期。

Listing 21-20 中的代码使用 `let job =
receiver.lock().unwrap().recv().unwrap();`，其工作原理是：在 `let` 的情况下，等号右侧表达式中所使用的任何临时值在 `let` 语句结束时会被立即丢弃。然而，在 `while
let`（以及 `if let` 和 `match`）的情况下，临时值直到相关代码块结束才会被丢弃。在 Listing 21-21 中，锁在整个调用 `job()` 期间仍然保持锁定状态，这意味着其他 `Worker` 实例无法接收任务。

[type-aliases]: ch20-03-advanced-types.html#type-synonyms-and-type-aliases
[integer-types]: ch03-02-data-types.html#integer-types
[moving-out-of-closures]: ch13-01-closures.html#moving-captured-values-out-of-closures
[builder]: ../std/thread/struct.Builder.html
[builder-spawn]: ../std/thread/struct.Builder.html#method.spawn
