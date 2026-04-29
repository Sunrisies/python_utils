## 使用线程同时运行代码

在大多数当前的操作系统中，执行程序的代码会在**进程**中运行，操作系统会同时管理多个进程。在程序中，也可以有独立的部分同时运行。用于管理这些独立部分的机制被称为**线程**。例如，一个Web服务器可以拥有多个线程，从而能够同时响应多个请求。

将程序中的计算任务分割成多个线程来同时运行多个任务可以提高性能，但这也会增加复杂性。由于线程可以同时进行运行，因此无法保证不同线程上的代码部分会以特定的顺序执行。这可能会导致一些问题，例如：

- 竞争条件，即多个线程以不一致的顺序访问数据或资源
- 死锁，即两个线程相互等待，导致两个线程都无法继续执行
- 某些特定情况下才会出现的错误，这类错误很难重现，也难以可靠地修复

Rust试图减轻使用线程带来的负面影响，但在多线程环境下编程仍然需要仔细考虑，并且需要一种与单线程程序不同的代码结构。

编程语言以几种不同的方式实现线程，许多操作系统提供了API，让编程语言可以调用这些API来创建新的线程。Rust标准库采用了一种_1:1_的线程实现模型，即每个语言线程对应一个操作系统线程。还有一些库实现了其他类型的线程模型，这些模型在1:1模型的基础上做出了不同的权衡。（例如Rust的异步系统）在下一章中将会看到，这提供了一种处理并发问题的另一种方法。）

### 使用`spawn`创建新线程

要创建一个新的线程，我们调用`thread::spawn`函数，并传递一个闭包（我们在第13章中讨论过闭包），该闭包包含我们希望在新线程中执行的代码。清单16-1中的示例从主线程打印一些文本，同时从新线程打印其他文本。

<列表编号="16-1" 文件名称="src/main.rs" 标题="创建新线程以打印内容，同时主线程执行其他操作">

```rust
{{#rustdoc_include ../listings/ch16-fearless-concurrency/listing-16-01/src/main.rs}}
```

</清单>

请注意，当Rust程序的主线程完成时，所有子线程都会被关闭，无论它们是否已经运行完毕。这个程序的输出可能会每次都有所不同，但看起来会与以下示例类似：

<!-- 不提取输出内容，因为对该输出的修改并不显著；
这些修改可能是由于线程运行方式的不同所导致的，而非编译器的变化 -->

```text
hi number 1 from the main thread!
hi number 1 from the spawned thread!
hi number 2 from the main thread!
hi number 2 from the spawned thread!
hi number 3 from the main thread!
hi number 3 from the spawned thread!
hi number 4 from the main thread!
hi number 4 from the spawned thread!
hi number 5 from the spawned thread!
```

对`thread::sleep`的调用会强制一个线程在短时间内停止执行，从而让另一个线程能够运行。这些线程可能会交替执行，但这并不确定：这取决于你的操作系统如何调度这些线程。在这次运行中，主线程首先被打印出来，尽管从子线程中执行的print语句在代码中出现得更早。尽管我们告诉子线程一直打印到`i`等于`9`为止，但它只执行到了`5`之后，主线程才关闭。

如果您运行这段代码，却只看到主线程的输出，或者看不到任何重叠现象，那么请尝试增加各个范围中的数值，以便操作系统有更多的机会在多个线程之间切换。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="等待所有线程完成使用连接处理"></a>

### 等待所有线程完成

在清单16-1中的代码，由于主线程的终止，大多数情况下都会提前终止子线程的运行。此外，由于无法保证线程运行的顺序，我们也无法确保子线程能够顺利运行！

我们可以通过将`thread::spawn`的返回值保存到一个变量中来解决子线程无法运行或提前终止的问题。`thread::spawn`的返回类型是`JoinHandle<T>`。`JoinHandle<T>`是一个被拥有的值，当我们调用`join`方法时，它会等待该线程完成。清单16-2展示了如何使用在清单16-1中创建的线程的`JoinHandle<T>`，以及如何调用`join`来确保……在`main`退出之前，该线程就已经结束了。

<列表编号="16-2" 文件名称="src/main.rs" 标题="将`JoinHandle<T>`从`thread::spawn`中保存下来，以确保线程能够完整运行">

```rust
{{#rustdoc_include ../listings/ch16-fearless-concurrency/listing-16-02/src/main.rs}}
```

</清单>

在句柄上调用`join`会阻塞当前正在运行的线程，直到该句柄所代表的线程终止为止。阻塞一个线程意味着该线程无法执行任务或退出。由于我们将`join`的调用放在了主线程的`for`循环之后，因此运行清单16-2应该会产生类似以下的输出：

<!-- 不提取输出内容，因为对该输出的修改并不显著；
这些修改可能是由于线程运行方式的不同所导致的，而非编译器的变化 -->

```text
hi number 1 from the main thread!
hi number 2 from the main thread!
hi number 1 from the spawned thread!
hi number 3 from the main thread!
hi number 2 from the spawned thread!
hi number 4 from the main thread!
hi number 3 from the spawned thread!
hi number 4 from the spawned thread!
hi number 5 from the spawned thread!
hi number 6 from the spawned thread!
hi number 7 from the spawned thread!
hi number 8 from the spawned thread!
hi number 9 from the spawned thread!
```

这两个线程继续交替运行，但由于调用了`handle.join()`，主线程会等待，直到子线程完成工作之后才会结束。

但是，让我们看看当我们将`handle.join()`移到`for`循环之前的`main`中时会发生什么，就像这样：

<listing file-name="src/main.rs">

```rust
{{#rustdoc_include ../listings/ch16-fearless-concurrency/no-listing-01-join-too-early/src/main.rs}}
```

</清单>

主线程会等待新创建的线程完成，然后执行其`for`循环，这样输出就不会再出现交错的情况了，就像这里展示的那样：

<!-- 不提取输出内容，因为对该输出的修改并不显著；
这些修改可能是由于线程运行方式的不同所导致的，而非编译器的变化 -->

```text
hi number 1 from the spawned thread!
hi number 2 from the spawned thread!
hi number 3 from the spawned thread!
hi number 4 from the spawned thread!
hi number 5 from the spawned thread!
hi number 6 from the spawned thread!
hi number 7 from the spawned thread!
hi number 8 from the spawned thread!
hi number 9 from the spawned thread!
hi number 1 from the main thread!
hi number 2 from the main thread!
hi number 3 from the main thread!
hi number 4 from the main thread!
```

一些细节，比如`join`在何处被调用，会影响你的线程是否能够同时运行。

### 在多线程中使用`move`闭包

我们通常会使用 ``move`` 这个关键字来与闭包一起使用，因为这样闭包就会拥有它从环境中获取的值，从而将这些值的所有权从一个线程转移到另一个线程。在《捕获引用或转移所有权》这一章节中，我们讨论了 ``move`` 在闭包上下文中的使用。现在，我们将更专注于 ``move`` 与 ``thread::spawn`` 之间的交互。

请注意，在清单16-1中，我们传递给`thread::spawn`的闭包没有任何参数：我们在子线程的代码中并没有使用主线程的任何数据。为了在子线程中使用主线程的数据，子线程中的闭包必须捕获所需的值。清单16-3展示了在主线程中创建一个向量并在子线程中使用的尝试。然而，这目前是行不通的，您稍后会看到原因。

<列表编号="16-3" 文件名称="src/main.rs" 标题="尝试在另一个线程中使用由主线程创建的向量">

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch16-fearless-concurrency/listing-16-03/src/main.rs}}
```

</清单>

这个闭包使用了`v`，因此它会捕获`v`，并将其作为闭包的环境的一部分。由于`thread::spawn`是在一个新的线程中运行这个闭包的，我们应该能够在那个新线程中访问`v`。但是，当我们编译这个示例时，会出现以下错误：

```console
{{#include ../listings/ch16-fearless-concurrency/listing-16-03/output.txt}}
```

Rust会推断出如何捕获`v`，而因为`println!`只需要对`v`的引用，所以闭包试图借用`v`。然而，存在一个问题：Rust无法知道新创建的线程会运行多久，因此它无法确定对`v`的引用是否始终有效。

清单16-4提供了一个可能包含对`v`的引用的场景，这样的引用将不再有效。

<列表编号="16-4" 文件名称="src/main.rs" 标题="一个线程，其中有一个闭包试图从主线程捕获对`v`的引用，而主线程会抛出一个`v`">

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch16-fearless-concurrency/listing-16-04/src/main.rs}}
```

</清单>

如果Rust允许我们运行这段代码，那么生成的线程很可能会立即被放到后台，根本不会执行。生成的线程内部有一个对`v`的引用，但是主线程会立即丢弃`v`，并且使用了我们在第15章中讨论过的`drop`函数。因此，当生成的线程开始执行时，`v`就不再是有效的了，所以对这个引用的引用也就无效了。哦不！

为了修复清单16-3中的编译器错误，我们可以使用错误信息中的建议来解决问题。

<!-- 手动重新生成
在自动生成之后，请查看 listings/ch16-fearless-concurrency/listing-16-03/output.txt 文件，并复制相关部分
-->

```text
help: to force the closure to take ownership of `v` (and any other referenced variables), use the `move` keyword
  |
6 |     let handle = thread::spawn(move || {
  |                                ++++
```

通过在闭包之前添加 ``move`` 关键字，我们强制闭包自行管理其所使用的数值，而不是让 Rust 自动推断应该借用这些数值。如清单 16-5 所示，对清单 16-3 的修改将会按照我们的预期进行编译和运行。

<列表编号="16-5" 文件名称="src/main.rs" 标题="使用 `move` 关键字来强制闭包拥有其使用的数值">

```rust
{{#rustdoc_include ../listings/ch16-fearless-concurrency/listing-16-05/src/main.rs}}
```

</清单>

我们可能会想要尝试同样的方法来修复清单16-4中的代码，其中主线程通过`move`闭包调用`drop`。然而，这种修复方法是无效的，因为清单16-4的尝试存在另一个不允许的原因。如果我们向闭包中添加`move`，那么`v`就会进入闭包的环境，而我们在主线程中就无法再调用`drop`了。这样我们就会遇到编译错误。

```console
{{#include ../listings/ch16-fearless-concurrency/output-only-01-move-drop/output.txt}}
```

Rust的所有权规则再次帮了我们大忙！因为在Listing 16-3中的代码出现了错误，因为Rust采取了保守的做法，只将`v`借给线程使用，这意味着主线程理论上可以使得子线程对`v`的引用失效。通过告诉Rust将`v`的所有权移交给子线程，我们向Rust保证了主线程将不再使用`v`了。如果我们以同样的方式修改清单16-4，那么在主线程中尝试使用`v`时，就会违反所有权规则。`move`关键字会覆盖Rust默认的保守借用机制；它不允许我们违反所有权规则。

现在我们已经了解了线程是什么以及线程API提供了哪些方法，接下来我们来看看在哪些情况下可以使用线程。

[capture]: ch13-01-closures.html#捕获引用或转移所有权