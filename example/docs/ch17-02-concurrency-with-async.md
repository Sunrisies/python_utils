<!-- Old headings. Do not remove or links may break. -->

<a id="concurrency-with-async"></a>

## 使用异步技术实现并发处理

在本节中，我们将使用异步编程来解决一些与第16章中通过线程处理过的并发问题。由于我们已经在前面讨论过许多相关概念，因此在本节中，我们将重点讨论线程和future之间的区别。

在许多情况下，使用异步方式处理并发的API与使用线程的API非常相似。但在其他情况下，它们的行为却大相径庭。即使这些API在线程和异步方式下看起来相似，它们的实际行为往往也各不相同，而且性能特征也几乎总是存在差异。

<!-- Old headings. Do not remove or links may break. -->

<a id="counting"></a>

### 使用 `spawn_task` 创建新任务

在第16章的 [“Creating a New Thread with
`spawn`”][thread-spawn]<!-- ignore --> 部分，我们首先在两个独立的线程上进行计数操作。现在，让我们使用异步方式来实现同样的操作。 `trpl` 这个库提供了一个 `spawn_task` 函数，其功能与 `thread::spawn` API 非常相似；此外，还有一个 `sleep` 函数，它是 `thread::sleep` API 的异步版本。我们可以结合使用这些功能来编写计数示例，如清单17-6所示。

<Listing number="17-6" caption="Creating a new task to print one thing while the main task prints something else" file-name="src/main.rs">

```rust
use std::time::Duration;

fn main() {
    trpl::block_on(async {
        trpl::spawn_task(async {
            for i in 1..10 {
                println!("hi number {i} from the first task!");
                trpl::sleep(Duration::from_millis(500)).await;
            }
        });

        for i in 1..5 {
            println!("hi number {i} from the second task!");
            trpl::sleep(Duration::from_millis(500)).await;
        }
    });
}

```

</Listing>

作为我们的起点，我们设置了 `main` 函数，使其包含 `trpl::block_on`，这样我们的顶级函数就可以成为异步函数了。

> 注意：从本章的这一点开始，每个示例都会包含完全相同的包装代码，其格式为 `trpl::block_on` 在 `main` 中。因此，我们通常会跳过这部分代码，就像我们处理 `main` 一样。请记得在代码中包含这部分代码！

然后，我们在该代码块中编写两个循环，每个循环都包含一个 `trpl::sleep` 调用，该调用会等待半秒（500毫秒），然后再发送下一个消息。我们将一个循环放在 `trpl::spawn_task` 的体内，另一个则放在顶层 `for` 循环中。此外，我们还在 `sleep` 调用之后添加了一个 `await`。

这段代码的运行方式与基于线程的实现类似——包括这样一个事实：当你运行这段代码时，你可能在自己的终端中看到消息出现的顺序有所不同。

<!-- Not extracting output because changes to this output aren't significant;
the changes are likely to be due to the threads running differently rather than
changes in the compiler -->

```text
hi number 1 from the second task!
hi number 1 from the first task!
hi number 2 from the first task!
hi number 2 from the second task!
hi number 3 from the first task!
hi number 3 from the second task!
hi number 4 from the first task!
hi number 4 from the second task!
hi number 5 from the first task!
```

这个版本的执行会在主异步块的代码体中的 `for` 循环结束后立即停止，因为由 `spawn_task` 生成的任务会在 `main` 函数结束时被关闭。如果你想让任务一直运行到完成，就需要使用 join 句柄来等待第一个任务的完成。在多线程环境中，我们使用 `join` 方法来“阻塞”线程，直到线程完全运行完毕。在 Listing 17-7 中，我们可以使用 `await` 来实现同样的效果，因为任务句柄本身就是一个 future。它的 `Output` 类型是一个 `Result`，因此在等待它时，我们也需要将其解包。

<Listing number="17-7" caption="Using `await` with a join handle to run a task to completion" file-name="src/main.rs">

```rust
        let handle = trpl::spawn_task(async {
            for i in 1..10 {
                println!("hi number {i} from the first task!");
                trpl::sleep(Duration::from_millis(500)).await;
            }
        });

        for i in 1..5 {
            println!("hi number {i} from the second task!");
            trpl::sleep(Duration::from_millis(500)).await;
        }

        handle.await.unwrap();

```

</Listing>

这个更新后的版本会一直运行，直到两个循环都完成。

<!-- Not extracting output because changes to this output aren't significant;
the changes are likely to be due to the threads running differently rather than
changes in the compiler -->

```text
hi number 1 from the second task!
hi number 1 from the first task!
hi number 2 from the first task!
hi number 2 from the second task!
hi number 3 from the first task!
hi number 3 from the second task!
hi number 4 from the first task!
hi number 4 from the second task!
hi number 5 from the first task!
hi number 6 from the first task!
hi number 7 from the first task!
hi number 8 from the first task!
hi number 9 from the first task!
```

到目前为止，看起来异步处理和多线程处理都能得到类似的结果，只是语法有所不同：在join句柄上使用 `await` 而不是调用 `join`，并且等待 `sleep` 的调用。

更大的区别在于，我们不需要启动另一个操作系统线程来执行这些操作。实际上，我们甚至不需要在这里启动任务。因为异步代码块会被编译成匿名未来函数，我们可以将每个循环放在一个异步代码块中，然后让运行时使用 `trpl::join` 函数来同时执行这两个循环，直到完成。

在第十六章的 [“Waiting for All Threads to Finish”][join-handles]<!-- ignore --> 部分中，我们展示了如何对调用 `std::thread::spawn` 时返回的 `JoinHandle` 类型使用 `join` 方法。`trpl::join` 函数与之类似，但适用于未来值。当你给它两个未来值时，它会生成一个新的未来值，该未来值的输出是一个元组，其中包含你传递的每个未来值完成后的输出结果。因此，在 Listing 17-8 中，我们使用 `trpl::join` 来等待 `fut1` 和 `fut2` 完成。我们不会等待 `fut1` 和 `fut2`，而是等待由 `trpl::join` 生成的新未来值。我们忽略这个未来值的输出，因为它只是一个包含两个单位值的元组。

<Listing number="17-8" caption="Using `trpl::join` to await two anonymous futures" file-name="src/main.rs">

```rust
        let fut1 = async {
            for i in 1..10 {
                println!("hi number {i} from the first task!");
                trpl::sleep(Duration::from_millis(500)).await;
            }
        };

        let fut2 = async {
            for i in 1..5 {
                println!("hi number {i} from the second task!");
                trpl::sleep(Duration::from_millis(500)).await;
            }
        };

        trpl::join(fut1, fut2).await;

```

</Listing>

当我们运行这个程序时，可以看到所有的未来操作都完成了。

<!-- Not extracting output because changes to this output aren't significant;
the changes are likely to be due to the threads running differently rather than
changes in the compiler -->

```text
hi number 1 from the first task!
hi number 1 from the second task!
hi number 2 from the first task!
hi number 2 from the second task!
hi number 3 from the first task!
hi number 3 from the second task!
hi number 4 from the first task!
hi number 4 from the second task!
hi number 5 from the first task!
hi number 6 from the first task!
hi number 7 from the first task!
hi number 8 from the first task!
hi number 9 from the first task!
```

现在，您会看到每次都遵循完全相同的顺序，这与我们在 Listing 17-7 中看到的线程机制以及 `trpl::spawn_task` 的情况有很大不同。这是因为 `trpl::join` 函数是一种“公平”的调度方式，它会对每个任务进行平等的检查，交替进行，并且不会让某个任务抢先另一个任务执行，只要另一个任务已经准备好即可。而在线程机制中，是由操作系统来决定检查哪个线程以及让哪个线程运行多长时间。而在 async Rust 中，则是由运行时来决定检查哪个任务。实际上，细节会比较复杂，因为异步运行时可能会在底层使用操作系统线程来管理并发，因此确保公平性对运行时来说可能更加困难——但仍然是可能的！运行时不必为任何特定操作保证公平性，而且它们通常提供不同的 API，让您可以自行选择是否希望实现公平性。

试试这些等待未来的不同方法，看看它们有什么效果：

- 移除两个循环中的异步代码块。
- 在定义异步代码块后，立即对其进行等待操作。
- 仅将第一个循环包裹在异步代码块中，并在第二个循环的主体之后等待生成的未来值。

为了增加挑战性，试着在运行代码之前，先预测每种情况下的输出结果会是什么！

<!-- Old headings. Do not remove or links may break. -->

<a id="message-passing"></a>
<a id="counting-up-on-two-tasks-using-message-passing"></a>

### 使用消息传递在两个任务之间传递数据

在并发任务之间共享数据也是常见的做法：我们将再次使用消息传递机制，但这次使用的是异步版本的类型和函数。在说明基于线程的并发与基于并发的任务之间的关键差异时，我们将采取与第16章中的 [“Transfer Data Between Threads
with Message Passing”][message-passing-threads]<!-- ignore --> 部分略有不同的方法。在 Listing 17-9 中，我们将从一个单独的异步代码块开始——而不是像之前那样创建单独的线程来启动任务。

<Listing number="17-9" caption="Creating an async channel and assigning the two halves to `tx` and `rx`" file-name="src/main.rs">

```rust
        let (tx, mut rx) = trpl::channel();

        let val = String::from("hi");
        tx.send(val).unwrap();

        let received = rx.recv().await.unwrap();
        println!("received '{received}'");

```

</Listing>

在这里，我们使用 `trpl::channel`，这是一个异步版本的多生产者、单消费者通道接口，我们在第16章中使用了这个接口来处理线程。这个异步版本的接口与基于线程的版本只有很小的区别：它使用可变接收器 `rx`，而不是不可变接收器；它的 `recv` 方法会返回一个未来值，我们需要等待这个未来值，而不是直接返回值。现在，我们可以从发送者向接收者发送消息。请注意，我们不需要单独启动一个线程，甚至不需要启动一个任务；我们只需要等待 `rx.recv` 调用的完成。

在 `std::mpsc::channel` 块中，同步的 `Receiver::recv` 方法会一直等待，直到收到消息为止。而 `trpl::Receiver::recv` 方法则不会等待，因为它采用异步方式运行。它不会阻塞，而是将控制权返回给运行时，直到收到消息或者通道的发送端关闭。相比之下，我们不会等待 `send` 方法的调用，因为它不会阻塞。实际上，它不需要这样做，因为我们发送它的通道是无限制的。

> 注意：由于所有这些异步代码都在一个异步块中运行，并且处于 `trpl::block_on` 调用之下，因此其中的所有操作都可以避免阻塞。然而，位于该代码 _外部_ 的代码将会在 `block_on` 函数返回时阻塞。这就是 `trpl::block_on` 函数的意义所在：它允许你选择在某个异步代码上阻塞，从而可以在同步代码和异步代码之间切换。

请注意这个示例中的两点。首先，消息会立即到达。其次，虽然这里使用了“未来”这个概念，但实际上还没有并发性。列表中的所有操作都是按顺序进行的，就像没有使用“未来”概念一样。

让我们通过发送一系列消息来处理第一部分，并在这些消息之间休眠，如清单17-10所示。

<!-- We cannot test this one because it never stops! -->

<Listing number="17-10" caption="Sending and receiving multiple messages over the async channel and sleeping with an `await` between each message" file-name="src/main.rs">

```rust,ignore
        let (tx, mut rx) = trpl::channel();

        let vals = vec![
            String::from("hi"),
            String::from("from"),
            String::from("the"),
            String::from("future"),
        ];

        for val in vals {
            tx.send(val).unwrap();
            trpl::sleep(Duration::from_millis(500)).await;
        }

        while let Some(value) = rx.recv().await {
            println!("received '{value}'");
        }

```

</Listing>

除了发送消息之外，我们还需要接收这些消息。在这种情况下，因为我们知道会有多少消息传入，我们可以手动调用 `rx.recv().await` 四次来完成这个操作。不过在现实世界中，我们通常会等待未知数量的消息，因此我们需要持续等待，直到确定没有更多的消息了。

在 Listing 16-10 中，我们使用了一个 `for` 循环来处理从同步通道接收到的所有项。不过，Rust 目前还没有办法使用 `for` 循环来处理异步产生的系列项。因此，我们需要使用一种之前未曾见过的循环方式：即 `while let` 条件循环。这种循环是 `if let` 构造的版本，我们在第 6 章的 [“Concise Control Flow with `if
let` and `let...else`”][if-let]<!-- ignore --> 部分已经介绍过它。只要所指定的模式继续与值匹配，这个循环就会持续执行下去。

调用 `rx.recv` 会生成一个未来值，我们需要等待这个未来值。在运行时，系统会暂停这个未来值，直到它准备好为止。一旦有消息到达，未来值就会根据到达的消息数量多次转换为 `Some(message)`。当通道关闭时，无论是否有任何消息到达，未来值都会转换为 `None`，以表示不再有值存在，因此我们应该停止轮询，即停止等待。

这个 `while let` 循环将以上内容整合在一起。如果调用 `rx.recv().await` 的结果就是 `Some(message)`，那么我们就可以访问该消息，并像使用 `if let` 一样在循环体内使用它。如果结果是 `None`，那么循环就会结束。每次循环完成时，都会再次执行 await 操作，因此运行时会暂停循环，直到收到新的消息为止。

现在，代码能够成功发送和接收所有消息了。  
不过，仍然存在一些问题。首先，消息并不是以半秒间隔发送的，而是在我们启动程序后2秒（2000毫秒）内一次性全部到达。其次，这个程序永远无法退出！它一直在等待新的消息。你需要使用 <kbd>ctrl</kbd>-<kbd>C</kbd> 来关闭它。

#### 在一个异步代码块内的代码会线性执行

首先，我们来探讨为什么在完整延迟之后，这些消息会一次性出现，而不是在每次延迟之后才出现。在给定的异步代码块中，`await`关键字在代码中的出现顺序，正是它们在程序运行时被执行的顺序。

在 Listing 17-10 中只有一个异步块，因此其中的所有代码都是线性执行的。仍然没有并发性。所有的 `tx.send` 调用都会发生，同时还有所有的 `trpl::sleep` 调用及其相关的 await 操作。只有当 `while let` 循环处理到了 `recv` 调用中的 `await` 调用时，才会真正开始执行。

为了实现我们期望的行为，即每次发送消息之间都有睡眠延迟，我们需要将 `tx` 和 `rx` 操作放在各自的异步块中，如清单17-11所示。这样，运行时就可以分别执行这两个操作，就像在清单17-8中那样，使用 `trpl::join`。同样，我们等待的是 `trpl::join` 的调用结果，而不是各个未来值的返回结果。如果我们按顺序等待各个未来值，最终就会回到顺序流程中——而这正是我们绝对不想看到的。

<!-- We cannot test this one because it never stops! -->

<Listing number="17-11" caption="Separating `send` and `recv` into their own `async` blocks and awaiting the futures for those blocks" file-name="src/main.rs">

```rust,ignore
        let tx_fut = async {
            let vals = vec![
                String::from("hi"),
                String::from("from"),
                String::from("the"),
                String::from("future"),
            ];

            for val in vals {
                tx.send(val).unwrap();
                trpl::sleep(Duration::from_millis(500)).await;
            }
        };

        let rx_fut = async {
            while let Some(value) = rx.recv().await {
                println!("received '{value}'");
            }
        };

        trpl::join(tx_fut, rx_fut).await;

```

</Listing>

在 Listing 17-11 中更新后的代码中，消息将以 500 毫秒的间隔打印出来，而不是在 2 秒后一次性打印完毕。

#### 将所有权转移到异步代码块中

不过，由于 `while let` 循环与 `trpl::join` 的相互作用方式，该程序始终无法退出。

- 从 `trpl::join` 返回的未来只会在两个都已完成的情况下才完成。
- `tx_fut` 在未来的最后一个消息发送完成后，会完成一次。
- `rx_fut` 的未来只有在 `while let` 循环结束之前不会完成。
- `while let` 循环在等待 `rx.recv` 产生 `None` 之前不会结束。
- 等待 `rx.recv` 的行为只有在通道的另一端关闭后才会再次发生。
- 通道只有在我们调用 `rx.close` 或者当发送方 `tx` 被丢弃时才会关闭。
- 我们不会在任何地方调用 `rx.close`，而 `tx` 只有在传递给 `trpl::block_on` 的最外层异步块结束时才会被丢弃。
- 该块无法结束，因为它被阻塞在 `trpl::join` 完成上，这让我们回到列表的顶部。

目前，我们发送消息的异步块只是进行了“借用”，即 `tx`。因为发送消息并不需要所有权。但如果我们能够将其“移动”到那个异步块中，那么一旦该异步块结束，这些数据就会被丢弃。在第十三章的 [“Capturing References or Moving Ownership”][capture-or-move]<!-- ignore --> 部分，你学习了如何使用 `move` 关键字与闭包进行交互。而在第十六章的 [“Using `move` Closures with
Threads”][move-threads]<!-- ignore --> 部分中，我们了解到在处理线程时，经常需要将数据移入闭包中。同样的基本机制也适用于异步块，因此 `move` 关键字在异步块中的使用方式与在闭包中的使用方式相同。

在 Listing 17-12 中，我们将用于发送消息的代码块从 `async` 改为 `async move`。

<Listing number="17-12" caption="A revision of the code from Listing 17-11 that correctly shuts down when complete" file-name="src/main.rs">

```rust
        let (tx, mut rx) = trpl::channel();

        let tx_fut = async move {
            // --snip--

```

</Listing>

当我们运行这个版本的代码时，在最后一个消息被发送和接收之后，程序会优雅地关闭。接下来，让我们看看需要做出哪些改变才能从一个以上的未来函数发送数据。

#### 使用 `join!` 宏来连接多个期货

这个异步通道也是一个多生产者通道，因此如果我们想从多个未来函数发送消息，就可以在 Listing 17-13 中看到的代码中使用 `tx` 调用 `clone`。

<Listing number="17-13" caption="Using multiple producers with async blocks" file-name="src/main.rs">

```rust
        let (tx, mut rx) = trpl::channel();

        let tx1 = tx.clone();
        let tx1_fut = async move {
            let vals = vec![
                String::from("hi"),
                String::from("from"),
                String::from("the"),
                String::from("future"),
            ];

            for val in vals {
                tx1.send(val).unwrap();
                trpl::sleep(Duration::from_millis(500)).await;
            }
        };

        let rx_fut = async {
            while let Some(value) = rx.recv().await {
                println!("received '{value}'");
            }
        };

        let tx_fut = async move {
            let vals = vec![
                String::from("more"),
                String::from("messages"),
                String::from("for"),
                String::from("you"),
            ];

            for val in vals {
                tx.send(val).unwrap();
                trpl::sleep(Duration::from_millis(1500)).await;
            }
        };

        trpl::join!(tx1_fut, tx_fut, rx_fut);

```

</Listing>

首先，我们克隆 `tx`，在第一个异步块之外创建 `tx1`。我们将 `tx1` 移动到那个块中，就像之前对 `tx` 所做的那样。之后，我们将原始的 `tx` 移到一个新的异步块中，在这个块中，我们以稍慢的延迟发送更多的消息。我们恰好将这个新的异步块放在接收消息的异步块之后，但实际上也可以放在之前。关键在于等待未来的顺序，而不是它们创建的顺序。

这两个用于发送消息的异步块都必须是 `async move` 类型的块，这样当这些块完成时， `tx` 和 `tx1` 就会被丢弃。否则，我们将回到最初出现的那个无限循环中。

最后，我们将从 `trpl::join` 切换到 `trpl::join!`，以处理额外的未来情况：`join!` 宏需要等待任意数量的函数调用，而我们在编译时就能知道这些函数调用的数量。我们将在本章的后面部分讨论如何等待未知数量的函数调用。

现在，我们看到了来自两个发送未来的所有消息。由于发送未来在发送后会有略微不同的延迟，因此这些消息也是以不同的时间间隔被接收的。

<!-- Not extracting output because changes to this output aren't significant;
the changes are likely to be due to the threads running differently rather than
changes in the compiler -->

```text
received 'hi'
received 'more'
received 'from'
received 'the'
received 'messages'
received 'future'
received 'for'
received 'you'
```

我们已经探讨了如何使用消息传递在 futures 之间传输数据，异步代码块中的代码如何按序执行，如何将所有权转移到异步代码块中，以及如何连接多个 futures。接下来，让我们讨论一下为什么以及如何告诉运行时可以切换到另一个任务。

[thread-spawn]: ch16-01-threads.html#creating-a-new-thread-with-spawn
[join-handles]: ch16-01-threads.html#waiting-for-all-threads-to-finish
[message-passing-threads]: ch16-02-message-passing.html
[if-let]: ch06-03-if-let.html
[capture-or-move]: ch13-01-closures.html#capturing-references-or-moving-ownership
[move-threads]: ch16-01-threads.html#using-move-closures-with-threads
