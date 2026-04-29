<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="并发与异步"></a>

## 使用异步实现并发处理

在本节中，我们将使用异步编程来解决一些与第16章中通过线程处理过的并发问题。由于我们已经在前面讨论过许多相关概念，因此在本节中，我们将重点讨论线程和 Futures之间的区别。

在许多情况下，使用异步方式处理并发的API与直接使用线程的API非常相似。但在其他情况下，这两种方式的API却有很大差异。即使在不同线程和异步环境下，API的界面看起来相似，它们的实际行为往往也各不相同——而且它们的性能特征也几乎总是存在差异。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="counting"></a>

### 使用 `spawn_task` 创建新任务

在第十六章的[“使用`spawn`创建新线程”][thread-spawn]<!-- ignore -->部分，我们首先在两个独立的线程上进行计数操作。现在，让我们使用异步方式来实现同样的操作。`trpl`这个库提供了一个`spawn_task`函数，该函数与`thread::spawn` API非常相似；同时还有一个`sleep`函数，它是`thread::sleep` API的异步版本。我们可以结合使用这些功能来编写计数示例，如清单17-6所示。

<Listing number="17-6" caption="创建一个新的任务，用于打印某事物，而主任务则打印其他内容" file-name="src/main.rs">

```rust
{{#rustdoc_include ../listings/ch17-async-await/listing-17-06/src/main.rs:all}}
```

</ Listing>

作为我们的起点，我们通过设置 `main` 函数中的 `trpl::block_on` 来实现这一目标，这样我们的顶级函数就可以成为异步函数了。

注意：从本章的这一点开始，每个示例都会包含完全相同的包装代码，其中`trpl::block_on`被包含在`main`中。因此，我们通常会跳过这部分代码，就像我们处理`main`一样。请确保在您的代码中包含这部分代码！

然后，我们在该代码块中编写两个循环，每个循环都包含一个`trpl::sleep`调用，这些调用会等待半秒（500毫秒），然后再发送下一个消息。我们将一个循环放在`trpl::spawn_task`的内部，另一个则放在顶层`for`循环中。此外，我们还在`sleep`调用之后添加了一个`await`。

这段代码的运行方式与基于线程的实现类似——包括这样一个事实：当你运行这段代码时，你可能在自己的终端中看到消息出现的顺序有所不同。

<!-- 不提取输出内容，因为对该输出的修改并不显著；
这些修改可能是由于线程运行方式的不同所导致的，而非编译器的变化 -->

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

这个版本的执行会在主异步代码块体内的`for`循环结束之后立即停止，因为由`spawn_task`生成的任务会在`main`函数结束时被关闭。如果你想让任务一直运行到完成，就需要使用join句柄来等待第一个任务的完成。在多线程环境中，我们使用`join`方法来“阻塞”，直到线程运行完毕。在Listing 17-7中，我们可以使用`await`来实现同样的效果，因为任务句柄本身就是一个future。它的`Output`类型是一个`Result`对象，因此在等待它时，我们也需要将其解包。

<Listing number="17-7" caption="使用 `await` 与连接句柄来运行任务直至完成" file-name="src/main.rs">

```rust
{{#rustdoc_include ../listings/ch17-async-await/listing-17-07/src/main.rs:handle}}
```

</ Listing>

这个更新后的版本会一直运行，直到两个循环都完成。

<!-- 不提取输出内容，因为对该输出的修改并不显著；
这些修改可能是由于线程运行方式的不同所导致的，而非编译器的变化 -->

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

到目前为止，看起来异步处理和线程使用的方法效果相似，只是语法不同：在join句柄上调用的是`await`而不是`join`，并且需要等待`sleep`的调用。

更大的区别在于，我们不需要启动另一个操作系统线程来执行这个操作。实际上，我们甚至不需要在这里启动任务。因为异步代码块会被编译成匿名未来函数，我们可以将每个循环放在一个异步代码块中，然后让运行时使用`trpl::join`函数来同时执行这两个循环直到完成。

在《等待所有线程完成》这一章节中，我们展示了如何对`JoinHandle`类型使用`join`方法，而`JoinHandle`是调用`std::thread::spawn`时返回的。`trpl::join`函数与之类似，但适用于未来操作。当你给它两个未来对象时，它会生成一个新的未来对象，该对象的输出是一个元组，其中包含传入的每个未来对象的输出结果，前提是这两个未来对象都已完成。因此，在Listing 17-8中，我们使用`trpl::join`来等待`fut1`和`fut2`完成。我们并不等待`fut1`和`fut2`的结果，而是等待由`trpl::join`生成的新未来对象的结果。我们忽略了这个元组的输出，因为它只是一个包含两个单位值的元组而已。

<Listing number="17-8" caption="使用 `trpl::join` 来等待两个匿名未来函数" file-name="src/main.rs">

```rust
{{#rustdoc_include ../listings/ch17-async-await/listing-17-08/src/main.rs:join}}
```

</ Listing>

当我们运行这个程序时，可以看到所有的未来操作都完成了：

<!-- 不提取输出内容，因为对该输出的修改并不显著；
这些修改可能是由于线程运行方式的不同所导致的，而非编译器的变化 -->

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

现在，每次你都会看到完全相同的执行顺序，这与我们在使用线程以及 Listing 17-7 中的 `trpl::spawn_task` 时所看到的顺序截然不同。这是因为 `trpl::join` 函数是一种“公平”的处理方式，它会对每个任务进行平等的检查，交替进行各个任务的执行，并且不会让某个任务优先运行，除非另一个任务已经准备好。在多线程环境中，操作系统负责决定在哪个线程上进行检查，以及该线程可以运行多长时间。而在异步 Rust 中，则是运行时来决定要检查哪个任务。（实际上，细节会比较复杂，因为异步运行时可能会在底层使用操作系统线程来管理并发，因此确保公平性对运行时来说可能更加困难——但仍然是可能的！）运行时不必为任何特定操作保证公平性，而且它们通常提供不同的 API，让你可以选择是否希望实现公平性。

试试这些等待未来的不同方法，看看它们有什么效果：

- 移除围绕其中一个或两个循环中的异步代码块。  
- 在定义异步代码块后立即等待其执行完毕。  
- 仅将第一个循环包装在异步代码块中，并在第二个循环的主体之后等待生成的未来值。

为了增加挑战性，试着在运行代码之前，先预测每种情况下的输出结果会是什么！

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="消息传递"></a>  
<a id="使用消息传递进行双任务计数"></a>

### 使用消息传递在两个任务之间传输数据

在并发任务之间共享数据也是常见的做法：我们将再次使用消息传递机制，但这次使用的是异步版本的数据类型和函数。我们采用的路径与第16章中“通过消息传递在线程之间传输数据”部分的做法略有不同，以此来说明基于线程和基于并发的一些关键差异。在Listing 17-9中，我们将从一个简单的异步代码块开始——而不是像之前那样创建单独的线程来启动任务。

<Listing number="17-9" caption="创建异步通道并将两部分分别赋值给`tx`和`rx`" file-name="src/main.rs">

```rust
{{#rustdoc_include ../listings/ch17-async-await/listing-17-09/src/main.rs:channel}}
```

</ Listing>

在这里，我们使用`trpl::channel`，这是一个异步版本的多个生产者、单个消费者通道接口。这个接口与我们在第16章中使用的线程相关。异步版本的接口与基于线程的版本只有细微差别：它使用可变的接收者而不是不可变的接收者`rx`，并且其`recv`方法会返回一个未来值，我们需要等待该未来值才能获取结果，而不是直接返回数值。

现在，我们可以从发送者向接收者发送消息。请注意，我们不需要单独启动一个线程或任务；我们只需要等待`rx.recv`的调用即可。

在`std::mpsc::channel`块中，同步的`Receiver::recv`方法会一直等待，直到收到一条消息为止。而`trpl::Receiver::recv`方法则不会等待，因为它是一个异步操作。它不会阻塞，而是将控制权返回给运行时，直到收到消息或者通道的发送端关闭。相比之下，我们不会等待`send`方法的调用，因为它不会阻塞。实际上，也不需要这样做，因为我们发送消息的通道是无边界的。

注意：由于所有这些异步代码都在 ``trpl::block_on`` 调用中的异步块中运行，因此其中的所有操作都可以避免阻塞。然而，位于该代码外部的代码将会阻塞在返回值的 ``block_on`` 函数上。这就是 ``trpl::block_on`` 函数的意义所在：它允许你选择在某个异步代码执行时阻塞的位置，从而可以在同步代码和异步代码之间切换。

请注意这个示例中的两点。首先，消息会立即到达。其次，虽然这里使用了“未来”的概念，但实际上还没有并发性。列表中的所有操作都是按顺序进行的，就像没有使用“未来”概念一样。

让我们通过发送一系列消息并在这之间休眠来处理第一部分，如清单17-10所示。

<!-- 我们无法测试这一内容，因为它永不停息！ -->

<Listing number="17-10" caption="通过异步通道发送和接收多个消息，并在每个消息之间使用 `await` 进行休眠" file-name="src/main.rs">

```rust,ignore
{{#rustdoc_include ../listings/ch17-async-await/listing-17-10/src/main.rs:many-messages}}
```

</ Listing>

除了发送消息之外，我们还需要接收这些消息。在这种情况下，因为我们知道会有多少消息传入，我们可以通过调用`rx.recv().await`四次来手动处理这些消息。不过在现实世界中，我们通常会等待未知数量的消息，因此我们需要持续等待，直到确定没有更多的消息了为止。

在清单16-10中，我们使用了一个`for`循环来处理从同步通道接收到的所有数据。不过，Rust目前还没有办法使用`for`循环来处理异步产生的数据序列。因此，我们需要使用一个之前未曾见过的循环：`while let`条件循环。这个循环实际上是`if let`构造的版本，我们在第6章的[“使用`if let` and `let...else`”][if-let]<!-- ignore -->部分中已经介绍过它。只要所指定的模式继续与值相匹配，这个循环就会持续执行下去。

`rx.recv`调用会生成一个未来值，我们需要等待这个未来值的解决。在运行时，程序会暂停这个未来值，直到它准备好为止。一旦有消息到达，未来值就会根据到达的消息数量多次指向`Some(message)`。当通道关闭时，无论是否有任何消息到达，未来值都会改为指向`None`，以表示不再有值可以获取，因此我们应该停止轮询——也就是说，停止等待。

`while let`循环将这一切整合在一起。如果调用`rx.recv().await`的结果等于`Some(message)`，那么我们就可以访问该消息，并在循环体内使用它，就像使用`if let`一样。如果结果等于`None`，那么循环就会结束。每次循环完成时，都会再次执行await操作，因此运行时会暂停循环，直到收到另一个消息为止。

现在，代码能够成功发送和接收所有消息了。  
不过，仍然存在一些问题。首先，消息并不是以半秒间隔发送的，而是一次性同时到达的，在我们启动程序后2秒钟（2000毫秒）时就已经全部到达了。其次，这个程序永远无法退出！它只会一直等待新的消息的到来。你需要使用<kbd>ctrl</kbd>-<kbd>C</kbd>来关闭它。

#### 在一个异步块内的代码会线性执行

让我们先来看看为什么在完整延迟之后，这些消息会一次性出现，而不是在每次延迟之后才出现。在给定的异步代码块中，`await`这个关键词在代码中出现的顺序，正是它们在程序运行时被执行的顺序。

在 Listing 17-10 中只有一个异步块，因此其中的所有代码都是线性执行的。仍然没有并发性。所有的 ``tx.send`` 调用都会执行，同时还有所有的 ``trpl::sleep`` 调用及其相关的 `await` 操作也会依次执行。只有当 ``while let`` 循环能够访问到 ``recv`` 调用中的各个 ``await`` 时，才会开始执行后续的操作。

为了实现我们期望的行为，即让睡眠延迟在每个消息之间发生，我们需要将`tx`和`rx`操作放在各自的异步块中，如清单17-11所示。这样，运行时就可以分别使用`trpl::join`来执行这两个操作，就像在清单17-8中所做的那样。同样，我们需要等待调用`trpl::join`的结果，而不是单独等待各个未来值。如果我们按顺序等待各个未来值，最终就会回到顺序流程中——而这正是我们绝对不想发生的。

<!-- 我们无法测试这一内容，因为它永不停息！ -->

<listing number="17-11" caption="将 `send` 和 `recv` 分别放入各自的 `async` 块中，并等待这些块的执行结果" file-name="src/main.rs">

```rust,ignore
{{#rustdoc_include ../listings/ch17-async-await/listing-17-11/src/main.rs:futures}}
```

</ Listing>

通过更新后的代码（如清单17-11所示），消息将以500毫秒的间隔打印出来，而不是在2秒后一次性全部打印出来。

#### 将所有权移动到异步代码块中

不过，由于 `while let` 循环与 `trpl::join` 的交互方式，程序始终无法退出。

- 来自`trpl::join`的未来执行只会在一个完成之后才返回，前提是传递给它的两个未来操作都已完成。
- `tx_fut`中的未来执行在发送完`vals`中的最后一个消息后才会完成。
- `rx_fut`中的未来执行只有在`while let`循环结束之前不会完成。
- `while let`中的循环只有在等待`rx.recv`产生`None`时才会结束。
- 等待`rx.recv`的操作只有在通道的另一端被关闭后才会返回`None`。
- 通道只有在我们调用`rx.close`或者当发送方`tx`被丢弃时才会关闭。
- 我们不会在任何地方调用`rx.close`，而`tx`则不会在传递给`trpl::block_on`的最外层异步块结束之前被丢弃。
- 该块无法结束，因为它被阻塞在`trpl::join`的执行上，而这又让我们回到这个列表的顶部。

目前，我们发送消息的异步代码块只是_借用`tx`——因为发送消息并不需要所有权。但如果我们能够_移动`tx`到那个异步代码块中，那么一旦该代码块结束，`tx`就会被释放。在第十三章的[“捕获引用或移动所有权”][capture-or-move]<!-- ignore -->部分中，你学习了如何使用`move`关键字与闭包进行交互。而在第十六章的[“使用`move`闭包与线程”][move-threads]<!-- ignore -->部分中，我们经常需要在处理线程时将数据移入闭包中。同样的基本机制也适用于异步代码块，因此`move`关键字在异步代码块中的使用方式与在闭包中的使用方式相同。

在 Listing 17-12 中，我们将用于发送消息的代码块从 `async` 更改为 `async move`。

<Listing number="17-12" caption="对代码进行修订，使其在完成后能够正确关闭" file-name="src/main.rs">

```rust
{{#rustdoc_include ../listings/ch17-async-await/listing-17-12/src/main.rs:with-move}}
```

</ Listing>

当我们运行这个版本的代码时，在最后一个消息被发送和接收之后，程序会优雅地关闭。接下来，让我们看看需要做出哪些改变才能从一个以上的未来对象发送数据。

#### 使用 `join!` 宏来连接多个期货

这个异步通道也是一个多生产者通道，因此如果我们想要从多个未来协程发送消息，就可以在 `tx` 上调用 `clone`，如清单 17-13 所示。

<Listing number="17-13" caption="使用多个生产者与异步块" file-name="src/main.rs">

```rust
{{#rustdoc_include ../listings/ch17-async-await/listing-17-13/src/main.rs:here}}
```

</ Listing>

首先，我们克隆了`tx`，同时在第一个异步代码块之外创建了`tx1`。我们将`tx1`移动到那个异步代码块中，就像之前对`tx`所做的那样。之后，我们将原始的`tx`移到一个新的异步代码块中，并在稍慢一些的延迟时间内发送更多的消息。有趣的是，这个新的异步代码块被放在了接收消息的异步代码块之后，但实际上也可以放在前面。关键在于等待未来的顺序，而不是它们创建的顺序。

这两个用于发送消息的异步块都需要是`async move`类型的块，这样当这些块执行完毕后，`tx`和`tx1`也能被正确删除。否则，我们就会回到最初出现的那个无限循环中。

最后，我们将代码从 ``trpl::join`` 切换至 ``trpl::join!``，以处理额外的未来操作：宏 ``join!`` 需要等待任意数量的未来操作，而我们在编译时就能知道未来操作的具体数量。关于如何等待未知数量的操作，我们将在本章的后面部分进行讨论。

现在我们可以看到来自两个发送未来的所有消息。由于发送未来在发送后会有略微不同的延迟，因此这些消息也是以不同的时间间隔被接收的：

<!-- 不提取输出内容，因为对该输出的修改并不显著；
这些修改可能是由于线程运行方式的不同所导致的，而非编译器的变化 -->

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

我们已经探讨了如何使用消息传递在异步Future之间传输数据，如何在异步代码块内按顺序执行代码，如何将所有权转移给异步代码块，以及如何连接多个异步Future。接下来，让我们讨论一下如何以及为什么告诉运行时可以切换到另一个任务。

[线程创建]: ch16-01-threads.html#使用-spawn创建新线程  
[join-handles]: ch16-01-threads.html#等待所有线程完成  
[消息传递线程]: ch16-02-message-passing.html  
[if-let]: ch06-03-if-let.html  
[capture-or-move]: ch13-01-closures.html#捕获引用或转移所有权  
[移动线程]: ch16-01-threads.html#在线程中使用移动闭包