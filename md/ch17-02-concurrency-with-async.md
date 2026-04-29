<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="并发处理异步任务"></a>

## 使用异步技术实现并发处理

在本节中，我们将使用异步技术来解决一些与第16章中通过线程处理过的并发问题。由于我们已经讨论了很多关键概念，因此在本节中，我们将重点讨论线程和期货之间的区别。

在许多情况下，使用异步方式处理并发的API与使用线程的API非常相似。但在其他情况下，它们的行为却大相径庭。即使在不同线程和异步环境中，这些API看起来相似，但它们的行为往往存在差异，而且性能特征也几乎总是不同的。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="counting"></a>

### 使用`spawn_task`创建新任务

在第十六章的[“使用`spawn`创建新线程”][thread-spawn]<!-- 忽略 -->部分，我们首先尝试在两个独立的线程中进行计数操作。现在，让我们使用异步方式来实现同样的操作。`trpl`库提供了一个`spawn_task`函数，该函数与`thread::spawn` API非常相似；此外，还有`sleep`函数，它是`thread::sleep` API的异步版本。我们可以请结合使用这些方法来实现计数示例，如清单17-6所示。

<List numbering="17-6" caption="创建一个新的任务，在主任务执行时打印其他内容" file-name="src/main.rs">

```rust
{{#rustdoc_include ../listings/ch17-async-await/listing-17-06/src/main.rs:all}}
```

</清单>

作为我们的起点，我们使用`trpl::block_on`来定义我们的`main`函数，这样我们的顶级函数就可以是异步的。

注意：从本章的这一点开始，每个示例都将包含完全相同的包装代码，其中`trpl::block_on`被包含在`main`中。因此，我们通常会跳过这部分代码，就像处理`main`一样。请确保在您的代码中包含这部分代码！

然后，我们在该代码块中编写两个循环，每个循环都包含一个`trpl::sleep`调用，该调用会等待半秒（500毫秒），然后再发送下一个消息。我们将一个循环放在`trpl::spawn_task`的内部，另一个则放在顶层`for`循环中。此外，我们还在`sleep`调用之后添加了一个`await`。

这段代码的运行方式与基于线程的实现类似——包括这样一个事实：当你运行它时，你可能在自己的终端中看到消息出现的顺序有所不同。

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

这个版本会在主异步块的代码体中的`for`循环结束之后立即停止，因为由`spawn_task`启动的任务会在`main`函数结束时被关闭。如果你想让任务一直运行到完成，就需要使用join处理程序来等待第一个任务完成。在使用线程时，我们使用`join`方法来“阻塞”，直到线程完成。在清单17-7中，我们可以使用`await`来实现同样的功能，因为任务处理程序本身就是一个未来值。它的`Output`类型实际上是一个`Result`对象，因此在等待它时，我们也可以将其解包。

<List numbering="17-7" caption="使用`await`与连接句柄来完成任务直至完成" file-name="src/main.rs">

```rust
{{#rustdoc_include ../listings/ch17-async-await/listing-17-07/src/main.rs:handle}}
```

</清单>

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

到目前为止，看起来异步处理和线程处理都能得到类似的结果，只是语法有所不同：在join处理中，使用`await`而不是调用`join`，并且等待`sleep`的调用。

更大的区别在于，我们不需要再启动另一个操作系统线程来执行这些操作。实际上，我们甚至不需要在这里启动任务。因为异步代码块会被编译成匿名未来函数，我们可以将每个循环放在一个异步代码块中，然后让运行时使用`trpl::join`函数来同时执行这两个循环直至完成。

在第十六章的[“等待所有线程完成”][join-handles]<!-- 忽略 -->部分中，我们展示了如何对调用`std::thread::spawn`时返回的`JoinHandle`类型使用`join`方法。`trpl::join`函数与此类似，但适用于未来操作。当给该函数两个未来对象时，它会生成一个新的未来对象，该对象的输出是一个元组，其中包含传入的每个未来对象的输出结果，前提是这两个未来对象都已完成。因此，在Listing 17-8中，我们使用了这种方法。`trpl::join`需要等待`fut1`和`fut2`完成。我们不会等待`fut1`和`fut2`，而是等待由`trpl::join`产生的新的未来事件。我们忽略这个输出，因为它只是一个包含两个单位值的元组而已。

<List numbering="17-8" caption="使用 `trpl::join` 来等待两个匿名未来函数" file-name="src/main.rs">

```rust
{{#rustdoc_include ../listings/ch17-async-await/listing-17-08/src/main.rs:join}}
```

</清单>

当我们运行这个程序时，可以看到两个未来任务都完成了：

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

现在，您会看到每次都是完全相同的顺序，这与我们在Listing 17-7中看到的线程以及`trpl::spawn_task`的情况有很大不同。这是因为`trpl::join`函数是一种“公平”的调度方式，它平等地检查每个任务，交替进行任务执行，并且不会让某个任务抢先运行，除非另一个任务已经准备好。在多线程系统中，操作系统决定检查哪个线程以及让哪个线程运行多长时间。而在异步Rust中，则是运行时来决定如何调度这些任务。需要检查的任务。（实际上，细节会变得更加复杂，因为异步运行时可能会在后台使用操作系统线程来处理并发问题，因此确保公平性对异步运行时来说可能更加困难——但仍然是可能的！）异步运行时不必为任何特定操作保证公平性，而且它们通常提供不同的API，让你可以选择是否希望实现公平性。

试试这些不同的方式来等待未来，看看它们会产生什么效果：

- 移除围绕其中一个或两个循环中的异步代码块。  
- 在定义每个异步代码块后，立即对其进行等待处理。  
- 仅将第一个循环包装在异步代码块中，并在第二个循环的主体之后等待相应的未来结果。

为了增加挑战性，试着在运行代码之前就预测每种情况下的输出结果会是什么！

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="消息传递"></a>  
<a id="使用消息传递进行双任务计数"></a>

### 使用消息传递在两个任务之间传输数据

在 futures 之间共享数据也是常见的做法：我们将再次使用消息传递机制，但这次使用的是异步版本的类和函数。我们的实现方式会与第16章中“通过消息传递在线程之间传输数据”这一节有所不同，以此来说明基于线程的并发与基于 futures 的并发之间的主要区别。在Listing 17-9中，我们将从仅使用一个 futures 开始。异步块——并没有像创建独立线程那样启动一个独立的任务。

<List numbering="17-9" caption="创建异步通道并将两部分分别分配给`tx`和`rx`" file-name="src/main.rs">

```rust
{{#rustdoc_include ../listings/ch17-async-await/listing-17-09/src/main.rs:channel}}
```

</清单>

在这里，我们使用`trpl::channel`，这是一个异步版本的多个生产者、单个消费者通道API，我们在第16章中使用了这个API来处理线程。这个异步版本的API与基于线程的版本只有很小的区别：它使用可变的接收者而不是不可变的接收者`rx`，并且它的`recv`方法会生成一个未来，我们需要等待这个未来，而不是直接返回值。现在，我们可以从发送者向接收者发送消息了。请注意，我们并没有……我们需要启动一个独立的线程，甚至是一个任务；我们只需要等待`rx.recv`的调用。

在`std::mpsc::channel`块中，同步的`Receiver::recv`方法会一直执行下去，直到收到一条消息为止。而`trpl::Receiver::recv`方法则不会阻塞，因为它采用的是异步方式。它不会阻塞程序，而是将控制权返回给运行时系统，直到收到消息或者通道的发送端关闭。相比之下，我们不会等待`send`方法的调用，因为它并不阻塞。实际上，它不需要这样做，因为我们所发送的通道是无限长度的。

注意：由于所有这些异步代码都在``trpl::block_on``调用的异步块中运行，因此其中的所有代码都可以避免阻塞。然而，位于该代码外部的代码将会在返回``block_on``函数的地方被阻塞。这就是``trpl::block_on``函数的意义所在：它允许你选择在某些异步代码上发生阻塞的位置，从而可以在同步代码和异步代码之间切换。

请注意这个示例中的两点。首先，消息会立即到达。其次，虽然我们在这里使用了“未来”，但实际上还没有并发的情况。列表中的所有操作都是按顺序进行的，就像没有使用“未来”一样。

让我们通过发送一系列消息来处理第一部分，并在这些消息之间休息，如清单17-10所示。

<!-- 我们无法测试这一项，因为它永不停歇！ -->

<Listing number="17-10" caption="通过异步通道发送和接收多个消息，并在每个消息之间使用`await`进行休眠" file-name="src/main.rs">

```rust,ignore
{{#rustdoc_include ../listings/ch17-async-await/listing-17-10/src/main.rs:many-messages}}
```

</清单>

除了发送消息之外，我们还需要接收这些消息。在这种情况下，因为我们知道有多少消息正在进入系统，我们可以通过调用`rx.recv().await`四次来手动处理这些消息。然而在现实世界中，我们通常会等待未知数量的消息，因此我们需要持续等待，直到确定没有更多的消息了为止。

在清单16-10中，我们使用了一个`for`循环来处理从异步通道接收到的所有项目。不过，Rust目前还没有办法使用`for`循环来处理异步产生的项目序列。因此，我们需要使用一种之前未曾见过的循环方式：`while let`条件循环。这是一种`if let`结构的变体，我们在[“使用`if`实现简洁的控制流”一节中已经介绍过这种结构。在第六章中提到了“let` and `let...else`”][if-let]<!-- 忽略 -->这一节。只要所指定的模式继续与值匹配，循环就会持续执行。

`rx.recv`调用会生成一个未来对象，我们需要等待这个未来对象的完成。运行时会暂停这个未来对象，直到它准备好为止。一旦有消息到达，未来对象将会根据到达的消息数量多次指向`Some(message)`。当通道关闭时，无论是否有任何消息到达，未来对象都会指向`None`，以表示不再有值可以获取，因此我们应该停止轮询——也就是说，停止等待。

`while let`循环将这一切整合在一起。如果调用`rx.recv().await`的结果等于`Some(message)`，那么我们就可以访问该消息，并在循环体内使用它，就像使用`if let`一样。如果结果等于`None`，那么循环就会结束。每次循环完成时，都会再次执行await操作，因此运行时会暂停循环，直到收到另一个消息为止。

现在，代码能够成功发送和接收所有消息了。  
不过，仍然存在一些问题。首先，消息并不是以半秒间隔发送的，而是在我们启动程序后2秒钟（2000毫秒）内一次性全部到达。其次，这个程序永远无法退出！它会一直等待新的消息。你需要使用<kbd>ctrl</kbd>-<kbd>C</kbd>来关闭它。

#### 位于同一个异步块内的代码会线性执行

让我们先来看看为什么这些消息会在完整的延迟之后一次性出现，而不是在每次延迟之后才出现。在给定的异步代码块中，`await`关键字在代码中出现的顺序，正是它们在程序运行时被执行的顺序。

在Listing 17-10中只有一个异步块，因此其中的所有代码都是线性执行的。仍然没有并发性。所有的`tx.send`调用都会发生，同时还有所有的`trpl::sleep`调用及其相关的await操作。只有当`while let`循环处理到`recv`调用中的某个`await`点时，才会开始执行后续的操作。

为了实现我们想要的行为，即每次发送消息之间都有延迟，我们需要将`tx`和`rx`操作放在各自的异步块中，如清单17-11所示。这样，运行时就可以分别使用`trpl::join`来执行这两个操作，就像在清单17-8中所做的那样。同样，我们需要等待调用`trpl::join`的结果，而不是单独等待各个未来操作的结果。如果我们继续按照顺序进行，最终还是会回到一个连续的流程中——这正是我们绝对不想看到的。

<!-- 我们无法测试这一项，因为它永不停歇！ -->

<listing number="17-11" caption="将`send`和`recv`分别放入各自的`async`块中，并等待这些块的后续操作" file-name="src/main.rs">

```rust,ignore
{{#rustdoc_include ../listings/ch17-async-await/listing-17-11/src/main.rs:futures}}
```

</清单>

通过更新后的代码，如清单17-11所示，消息将以500毫秒的间隔打印出来，而不是在2秒后一次性打印完毕。

#### 将所有权移入异步模块中

不过，由于`while let`循环与`trpl::join`的相互作用方式，该程序始终无法退出。

- 来自`trpl::join`的future在两者都完成之后才会结束。  
- `tx_fut`中的future在发送完`vals`中的最后一条消息后，会完成其任务。  
- `rx_fut`中的future在`while let`循环结束之前不会完成。  
- `while let`中的循环在等待`rx.recv`产生`None`之前不会结束。- 等待`rx.recv`会在通道的另一端关闭后才会返回`None`。  
- 只有当我们调用`rx.close`或者当发送方`tx`被丢弃时，通道才会关闭。  
- 我们不会在任何地方调用`rx.close`，而`tx`在传递给`trpl::block_on`的最外层异步块结束之前不会被丢弃。  
- 该块无法结束，因为它依赖于`trpl::join`的完成。这让我们回到了这个列表的顶部。

目前，我们发送消息的异步块只是“借用”了`tx`，因为发送消息并不需要拥有该代码。但如果我们可以将`tx`移入到那个异步块中，那么当该块结束时，这些代码就会被丢弃。在《捕获引用或移动所有权》这一章节中的[capture-or-move]<!-- ignore -->部分，你学习了如何使用`move`关键字与闭包一起使用，并且，如[“使用`move`闭包”]中所讨论的那样……在第十六章的“线程”部分中，我们经常需要将数据移动到闭包中，以便在处理线程时使用。同样的基本机制也适用于异步块，因此``move``这个关键字在异步块和闭包中都是适用的。

在清单17-12中，我们将用于发送消息的代码块从`async`更改为`async move`。

<listing number="17-12" caption="对代码进行修订，使其在完成后能够正确关闭" file-name="src/main.rs">

```rust
{{#rustdoc_include ../listings/ch17-async-await/listing-17-12/src/main.rs:with-move}}
```

</清单>

当我们运行这个版本的代码时，在最后一个消息被发送和接收之后，程序会优雅地关闭。接下来，让我们看看需要做出哪些改变才能从多个未来节点发送数据。

#### 使用 `join!` 宏来连接多个期货

这个异步通道也是一个多生产者通道，因此如果我们想要从多个未来协程发送消息，就可以在`tx`上调用`clone`，如清单17-13所示。

<List numbering="17-13" caption="使用多个生产者与异步块" file-name="src/main.rs">

```rust
{{#rustdoc_include ../listings/ch17-async-await/listing-17-13/src/main.rs:here}}
```

</清单>

首先，我们克隆了`tx`，并在第一个异步块之外创建了`tx1`。我们将`tx1`移动到那个异步块中，就像之前对`tx`所做的那样。之后，我们将原始的`tx`移到一个新的异步块中，在那里我们以稍慢的延迟发送更多的消息。这个新的异步块恰好位于接收消息的异步块之后，但实际上也可以放在之前。关键在于……等待期货的顺序，而不是它们被创建的顺序。

这两个用于发送消息的异步块都需要是`async move`类型的块，这样当这些块执行完毕后，`tx`和`tx1`也能被处理完毕。否则，我们将再次陷入最初出现的无限循环之中。

最后，我们将``trpl::join``替换为``trpl::join!``，以处理额外的未来情况。在``join!``中，需要等待任意数量的未来操作，而我们在编译时就能知道未来操作的具体数量。我们将在本章的后面部分讨论如何等待未知数量的操作。

现在我们可以看到所有来自发送期货的消息。由于发送期货在发送后会有略微不同的延迟时间，因此这些消息也会在不同的时间间隔被接收：

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

我们已经探讨了如何使用消息传递在多个未来任务之间传输数据，异步代码块中的代码如何按序执行，如何将所有权转移给异步代码块，以及如何将多个未来任务合并在一起。接下来，让我们讨论一下为什么以及如何告诉运行时可以切换到另一个任务。

[线程创建]: ch16-01-threads.html#使用-spawn创建新线程  
[加入处理程序]: ch16-01-threads.html#等待所有线程完成  
[消息传递线程]: ch16-02-message-passing.html  
[if-let]: ch06-03-if-let.html  
[捕获或移动]: ch13-01-closures.html#捕获引用或移动所有权  
[移动线程]: ch16-01-threads.html#在线程中使用移动闭包