<!-- Old headings. Do not remove or links may break. -->

<a id="using-message-passing-to-transfer-data-between-threads"></a>

## 通过消息传递在线程之间传输数据

一种越来越受欢迎的确保并发安全的方法就是消息传递。在这种方法中，线程或 Actor 通过发送包含数据的消息来进行通信。以下是从 [Go 语言文档](https://golang.org/doc/effective_go.html#concurrency) 中摘取的一句话来概括这一思想：“不要通过共享内存来进行通信；而是通过通信来共享内存。”

为了实现消息发送的并发性，Rust的标准库提供了通道的实现。通道是一种通用的编程概念，用于将数据从一个线程传输到另一个线程。

在编程中，你可以将通道想象成一条水流的通道，比如一条溪流或河流。如果你把一只橡皮鸭放入河流中，它就会顺流而下，直到到达河流的末端。

一个通道由两部分组成：发送端和接收端。发送端是上游位置，你将橡胶鸭子放入河流中；接收端则是橡胶鸭子最终到达的位置。你的代码中有一部分会调用发送端的方法来发送数据，另一部分则负责检查接收端是否有收到的消息。如果发送端或接收端中的任何一部分被中断，那么这个通道就被认为是“关闭”的。

在这里，我们将编写一个程序，其中一个线程负责生成数值并将它们通过通道发送出去，另一个线程则负责接收这些数值并将其打印出来。我们将使用通道在线程之间传递简单的数值，以此来演示这一功能。一旦你熟悉了这种技术，你就可以将通道用于任何需要相互通信的线程之间，比如聊天系统，或者一个由多个线程分别执行计算任务并将结果发送给一个线程来汇总结果的系统。

首先，在清单 16-6 中，我们将创建一个通道，但不会对其做任何操作。需要注意的是，目前这段代码无法编译，因为 Rust 还无法判断我们希望通过通道发送的是哪种类型的值。

**清单 16-6:** *src/main.rs* — 创建频道并将两部分分别分配给 `tx` 和 `rx`

```rust,ignore,does_not_compile
use std::sync::mpsc;

fn main() {
    let (tx, rx) = mpsc::channel();
}

```

我们使用 `mpsc::channel` 函数创建一个新的通道； `mpsc` 表示“多个生产者，单个消费者”。简而言之，Rust 标准库实现通道的方式意味着，一个通道可以有多个发送端，它们会生成值，但只有一个接收端可以消费这些值。想象一下，多个数据流汇聚成一条大河：所有通过任何数据流发送的数据最终都会流入这条大河。目前我们先从一个生产者开始，但等这个例子运行起来后，我们会添加多个生产者。

函数 `mpsc::channel` 返回一个元组，该元组的第一个元素是发送端——即发射器，第二个元素是接收端——即接收器。在许多领域中，传统上分别使用 `tx` 和 `rx` 来表示发射器和接收器。因此，我们将变量命名为这样的名称，以区分各个端点。我们使用 `let` 语句结合模式来分解元组；关于模式在 `let` 语句中的使用以及解构机制，我们将在第十九章中详细讨论。目前，只需知道以这种方式使用 `let` 语句是一种方便的方法来提取 `mpsc::channel` 返回的元组的各个部分。

让传输端进入一个新创建的线程，并发送一个字符串，这样新创建的线程就可以与主线程进行通信，如清单 16-7 所示。这就像在河流的上游放一只橡皮鸭，或者从一个线程向另一个线程发送聊天消息。

<Listing number="16-7" file-name="src/main.rs" caption='Moving `tx` to a spawned thread and sending `"hi"`'>

```rust
use std::sync::mpsc;
use std::thread;

fn main() {
    let (tx, rx) = mpsc::channel();

    thread::spawn(move || {
        let val = String::from("hi");
        tx.send(val).unwrap();
    });
}

```

</Listing>

再次，我们使用 `thread::spawn` 创建一个新的线程，然后使用 `move` 将 `tx` 移入闭包中，这样新创建的线程就拥有了 `tx`。新创建的线程需要拥有发送器，才能通过通道发送消息。

该发送器有一个 `send` 方法，该方法接收我们想要发送的值。`send` 方法返回一个 `Result<T, E>` 类型，因此如果接收者已经被丢弃，且无法将值发送出去，那么发送操作将会返回错误。在这个例子中，我们调用 `unwrap` 来在出现错误时引发 panic。但在实际应用中，我们会妥善处理这种情况：请回到第9章，了解正确的错误处理策略。

在 Listing 16-8 中，我们将从主线程中的接收者那里获取值。这就像在河流的尽头从水中捞出橡皮鸭，或者接收到一个聊天消息。

<Listing number="16-8" file-name="src/main.rs" caption='Receiving the value `"hi"` in the main thread and printing it'>

```rust
use std::sync::mpsc;
use std::thread;

fn main() {
    let (tx, rx) = mpsc::channel();

    thread::spawn(move || {
        let val = String::from("hi");
        tx.send(val).unwrap();
    });

    let received = rx.recv().unwrap();
    println!("Got: {received}");
}

```

</Listing>

接收端有两个有用的方法： `recv` 和 `try_recv`。我们使用的是 `recv`，即 _接收_ 方法，该方法会阻塞主线程的执行，并等待通道中接收到值。一旦接收到值， `recv` 会将其以 `Result<T, E>` 的形式返回。当发送端关闭时， `recv` 会返回一个错误信号，表示不再会有新的值被发送过来。

` `try_recv`` 方法并不会阻塞程序，而是会立即返回一个 ` `Result<T, E>`` 值。如果有的话，它会返回一个包含消息的 ` `Ok`` 值；如果没有消息，则会返回一个 ` `Err`` 值。如果此线程在等待消息时有其他任务需要执行，使用 ` `try_recv`` 会非常有用。我们可以编写一个循环，定期调用 ` `try_recv``，如果收到消息则处理该消息，否则会执行其他任务一段时间，然后再再次检查。

在这个示例中，我们为了简单起见使用了 `recv`；主线程除了等待消息之外，没有其他工作要做，因此阻塞主线程是合适的。

当我们运行清单 16-8 中的代码时，我们会看到从主线程打印出的数值：

<!-- Not extracting output because changes to this output aren't significant;
the changes are likely to be due to the threads running differently rather than
changes in the compiler -->

```text
Got: hi
```

太好了！

<!-- Old headings. Do not remove or links may break. -->

<a id="channels-and-ownership-transference"></a>

### 通过通道转移所有权

所有权规则在消息发送中起着至关重要的作用，因为它们有助于编写安全且具备并发性的代码。在并发编程中避免错误，正是通过在整个Rust程序中考虑所有权来实现的。让我们来进行一个实验，来展示通道和所有权是如何协同工作以预防问题的：我们将尝试在将某个值通过通道发送之后，在子线程中使用该值。尝试编译清单16-9中的代码，了解为什么这样的做法是不被允许的。

**列表 16-9:** *src/main.rs* — 在将变量通过通道传递后，尝试使用 `val`

```rust,ignore,does_not_compile
use std::sync::mpsc;
use std::thread;

fn main() {
    let (tx, rx) = mpsc::channel();

    thread::spawn(move || {
        let val = String::from("hi");
        tx.send(val).unwrap();
        println!("val is {val}");
    });

    let received = rx.recv().unwrap();
    println!("Got: {received}");
}

```

在这里，我们尝试在通过 `tx.send` 将值发送到通道之后，再打印出 `val`。允许这样做并不是一个好主意：一旦值被发送到另一个线程中，那个线程可能会在我们再次尝试使用该值之前，对其进行修改或丢弃。此外，另一个线程的修改可能会导致错误或意外的结果，因为这些修改可能基于不一致或不存在的数据。然而，如果我们尝试编译 Listing 16-9 中的代码，Rust 会给我们一个错误。

```console
$ cargo run
   Compiling message-passing v0.1.0 (file:///projects/message-passing)
error[E0382]: borrow of moved value: `val`
  --> src/main.rs:10:27
   |
 8 |         let val = String::from("hi");
   |             --- move occurs because `val` has type `String`, which does not implement the `Copy` trait
 9 |         tx.send(val).unwrap();
   |                 --- value moved here
10 |         println!("val is {val}");
   |                           ^^^ value borrowed here after move
   |
   = note: this error originates in the macro `$crate::format_args_nl` which comes from the expansion of the macro `println` (in Nightly builds, run with -Z macro-backtrace for more info)

For more information about this error, try `rustc --explain E0382`.
error: could not compile `message-passing` (bin "message-passing") due to 1 previous error

```

我们的并发处理错误导致了编译时错误。`send`这个函数会占用其参数的所有权，当参数被移动时，接收者会接管该参数的所有权。这一机制确保了我们在发送参数后不会意外地再次使用该参数；所有权系统会确保所有操作都正常进行。

<!-- Old headings. Do not remove or links may break. -->

<a id="sending-multiple-values-and-seeing-the-receiver-waiting"></a>

### 发送多个值

清单 16-8 中的代码已经编译并运行了，但它并没有清楚地显示出两个独立的线程正在通过通道进行通信。

在 Listing 16-10 中，我们进行了一些修改，这些修改将证明 Listing 16-8 中的代码是同时运行的：现在，新创建的线程会发送多个消息，并且在每个消息之间会暂停一秒钟。

**清单 16-10:** *src/main.rs* — 发送多个消息，并在每个消息之间暂停

```rust,noplayground
use std::sync::mpsc;
use std::thread;
use std::time::Duration;

fn main() {
    let (tx, rx) = mpsc::channel();

    thread::spawn(move || {
        let vals = vec![
            String::from("hi"),
            String::from("from"),
            String::from("the"),
            String::from("thread"),
        ];

        for val in vals {
            tx.send(val).unwrap();
            thread::sleep(Duration::from_secs(1));
        }
    });

    for received in rx {
        println!("Got: {received}");
    }
}

```

这次，新创建的线程拥有一个字符串向量，我们需要将这个向量发送给主线程。我们会逐个处理这些字符串，每次处理之间会调用 `thread::sleep` 函数，并将参数值设置为一秒。

在主线程中，我们不再显式调用 `recv` 函数了：相反，我们将 `rx` 视为一个迭代器。对于每一个接收到的值，我们都会将其打印出来。当通道关闭后，迭代就会结束。

当运行清单 16-10 中的代码时，你应该会看到以下输出结果，并且每行输出之间都会有一个一秒的暂停时间。

<!-- Not extracting output because changes to this output aren't significant;
the changes are likely to be due to the threads running differently rather than
changes in the compiler -->

```text
Got: hi
Got: from
Got: the
Got: thread
```

因为我们在主线程中的 `for` 循环中没有任何代码会暂停或延迟，所以我们可以确定主线程正在等待从子线程接收数据。

<!-- Old headings. Do not remove or links may break. -->

<a id="creating-multiple-producers-by-cloning-the-transmitter"></a>

### 创建多个生产者

之前我们提到过，`mpsc`这个缩写代表“多个生产者，单一消费者”的概念。现在让我们运用`mpsc`这个缩写，并扩展清单16-10中的代码，以创建多个线程，这些线程都会向同一个接收器发送值。我们可以通过克隆发送器来实现这一点，如清单16-11所示。

**清单 16-11:** *src/main.rs* — 从多个生产者发送多个消息

```rust,noplayground
    // --snip--

    let (tx, rx) = mpsc::channel();

    let tx1 = tx.clone();
    thread::spawn(move || {
        let vals = vec![
            String::from("hi"),
            String::from("from"),
            String::from("the"),
            String::from("thread"),
        ];

        for val in vals {
            tx1.send(val).unwrap();
            thread::sleep(Duration::from_secs(1));
        }
    });

    thread::spawn(move || {
        let vals = vec![
            String::from("more"),
            String::from("messages"),
            String::from("for"),
            String::from("you"),
        ];

        for val in vals {
            tx.send(val).unwrap();
            thread::sleep(Duration::from_secs(1));
        }
    });

    for received in rx {
        println!("Got: {received}");
    }

    // --snip--

```

这次，在创建第一个子线程之前，我们会对传输器执行 `clone` 操作。这样就能得到一个新的传输器，可以传递给第一个子线程。我们将原来的传输器传递给第二个子线程。这样我们就有了两个线程，每个线程都会向同一个接收器发送不同的消息。

当你运行代码时，输出结果应该看起来像这样：

<!-- Not extracting output because changes to this output aren't significant;
the changes are likely to be due to the threads running differently rather than
changes in the compiler -->

```text
Got: hi
Got: more
Got: from
Got: messages
Got: for
Got: the
Got: thread
Got: you
```

根据您的系统不同，您可能会看到数值的顺序也有所不同。这正是并发行为既有趣又困难的原因。如果您尝试使用`thread::sleep`，并在不同的线程中赋予它不同的数值，那么每次运行的结果都会更加不可预测，从而产生不同的输出。

既然我们已经了解了通道的工作原理，现在让我们来看看另一种并发实现方式。