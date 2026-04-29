## 使用线程同时运行代码

在大多数当前的操作系统中，执行程序的代码会在进程中运行，而操作系统会同时管理多个进程。在一个程序中，也可以有独立的部分同时运行。用来管理这些独立部分的机制被称为“线程”。例如，一个Web服务器可以拥有多个线程，这样它就可以同时响应多个请求。

在程序中将计算任务拆分成多个线程来同时运行多个任务可以提高性能，但这也会增加复杂性。由于线程可以同时进行运行，因此无法保证不同线程上的代码部分会以特定的顺序执行。这可能会导致一些问题，例如：

- 竞争条件，即多个线程以不一致的顺序访问数据或资源
- 死锁，即两个线程相互等待，导致两个线程都无法继续执行
- 某些特定情况下才会出现的错误，这类错误很难重现，也难以可靠地修复

Rust试图减轻使用线程带来的负面影响，但在多线程环境下编程仍然需要仔细考虑，并且需要一种与单线程程序不同的代码结构。

编程语言通过几种不同的方式来实现线程，许多操作系统还提供了API，让编程语言可以调用这些API来创建新的线程。Rust的标准库采用了一种_1:1_的线程实现模型，即每个语言线程对应一个操作系统线程。还有一些库实现了其他类型的线程模型，这些模型在权衡上与1:1模型有所不同。（Rust的异步系统，我们将在下一章中介绍，也提供了一种并发的实现方式。）

### 使用 `spawn` 创建新线程

要创建一个新的线程，我们调用 `thread::spawn` 函数，并传递一个闭包（我们在第13章中讨论过闭包）。这个闭包包含了我们希望在新线程中执行的代码。清单16-1中的示例从主线程打印一些文本，同时从新线程打印其他文本。

<列表编号="16-1" 文件名称="src/main.rs" 标题="创建新线程以执行某项任务，同时主线程执行其他任务">

```rust
{{#rustdoc_include ../listings/ch16-fearless-concurrency/listing-16-01/src/main.rs}}
```

</ Listing>

请注意，当Rust程序的主线程完成时，所有被派生的线程都会被关闭，无论它们是否已经运行完毕。这个程序的输出可能会每次都有所不同，但看起来会与以下示例类似：

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

对 ``thread::sleep`` 的调用会迫使一个线程在短时间内停止执行，从而让另一个线程有机会运行。这些线程可能会轮流执行，但这并不确定，因为这取决于操作系统的线程调度方式。在这次运行中，主线程首先打印出了内容，尽管从子线程中执行的打印语句在代码中出现的顺序应该是先后的。而且，即使我们告诉子线程在 ``i`` 变为 ``9`` 之前一直进行打印操作，但实际上子线程只执行到了 ``5``，之后主线程就停止了执行。

如果您运行这段代码时，只看到主线程的输出，或者看不到任何重叠现象，那么可以尝试增加各个区间的数值，从而为操作系统提供更多机会来在多个线程之间切换。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="等待所有线程完成使用join处理"></a>

### 等待所有线程完成

在 Listing 16-1 中的代码，由于主线程会提前结束，因此大多数情况下都会过早地终止子线程。此外，由于无法保证线程运行的顺序，我们也无法确保子线程能够顺利运行！

我们可以通过将`thread::spawn`的返回值保存到一个变量中来解决子线程无法运行或提前终止的问题。`thread::spawn`的返回类型是`JoinHandle<T>`。`JoinHandle<T>`是一个拥有所有权的变量，当我们调用`join`方法时，会等待其线程完成执行。清单16-2展示了如何使用在清单16-1中创建的线程中的`JoinHandle<T>`，以及如何调用`join`来确保子线程在`main`退出之前完成执行。

<列表编号="16-2" 文件名称="src/main.rs" 标题="将 `JoinHandle<T>` 从 `thread::spawn` 中保存下来，以确保线程能够完整运行">

```rust
{{#rustdoc_include ../listings/ch16-fearless-concurrency/listing-16-02/src/main.rs}}
```

</ Listing>

在句柄上调用`join`会阻塞当前正在运行的线程，直到该句柄所代表的线程终止。阻塞一个线程意味着该线程无法执行任务或退出。由于我们将`join`的调用放在了主线程的`for`循环之后，因此运行清单16-2应该会产生类似以下的输出：

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

但是，让我们看看当我们将 `handle.join()` 移动到 `for` 循环之前的 `main` 时会发生什么，就像这样：

<code listing file-name="src/main.rs">

```rust
{{#rustdoc_include ../listings/ch16-fearless-concurrency/no-listing-01-join-too-early/src/main.rs}}
```

</ Listing>

主线程会等待新创建的线程完成，然后执行其`for`循环，这样输出就不会再被交错显示了，就像这里展示的那样：

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

### 在多线程中使用 `move` 闭包

我们通常会使用 ``move`` 这个关键字来指代传递给 ``thread::spawn`` 的闭包。因为这样，闭包就会拥有它从环境中获取的值的所有权，从而将这些值的所有权从一个线程转移到另一个线程。在第十三章的《捕获引用或转移所有权》一文中，我们讨论了 ``move`` 在闭包上下文中的使用。现在，我们将更专注于 ``move`` 与 ``thread::spawn`` 之间的交互关系。

请注意，在清单16-1中，我们传递给`thread::spawn`的闭包没有任何参数：我们在子线程的代码中没有使用主线程的任何数据。为了在子线程中使用主线程的数据，子线程中的闭包必须捕获所需的数值。清单16-3展示了在主线程中创建一个向量并在子线程中使用的尝试。然而，这目前是行不通的，您稍后会看到原因。

<列表编号="16-3" 文件名称="src/main.rs" 标题="尝试在另一个线程中使用由主线程创建的向量">

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch16-fearless-concurrency/listing-16-03/src/main.rs}}
```

</ Listing>

这个闭包使用了 ``v``，因此它会捕获 ``v``，并将其作为闭包的环境的一部分。由于 ``thread::spawn`` 是在新的线程中运行这个闭包的，我们应该能够在那个新线程内访问 ``v``。但是，当我们编译这个示例时，出现了以下错误：

```console
{{#include ../listings/ch16-fearless-concurrency/listing-16-03/output.txt}}
```

Rust会推断出如何捕获`v`，而因为`println!`只需要对`v`的引用，所以闭包试图借用`v`。然而，存在一个问题：Rust无法知道生成的线程会运行多久，因此它无法确定对`v`的引用是否始终有效。

清单16-4提供了一个可能包含对`v`的引用的场景，这样的引用将不再有效。

<列表编号="16-4" 文件名称="src/main.rs" 标题="一个线程，其中有一个闭包试图从主线程捕获对`v`的引用，而主线程则抛出了`v`">

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch16-fearless-concurrency/listing-16-04/src/main.rs}}
```

</ Listing>

如果Rust允许我们运行这段代码，那么生成的线程很可能会立即被放到后台，根本不会执行。生成的线程内部有一个对`v`的引用，但是主线程会立即丢弃`v`，并且使用了我们在第15章中讨论过的`drop`函数。然后，当生成的线程开始执行时，`v`就不再有效了，因此对其的引用也就无效了。哦不！

为了修复清单16-3中的编译器错误，我们可以使用错误信息中的建议来解决问题。

<!-- 手动重新生成
在自动生成之后，请查看 listings/ch16-fearless-concurrency/listing-16-03/output.txt 文件，并复制相关部分 -->

```text
help: to force the closure to take ownership of `v` (and any other referenced variables), use the `move` keyword
  |
6 |     let handle = thread::spawn(move || {
  |                                ++++
```

通过在闭包之前添加 ``move`` 关键字，我们强制闭包自行管理其所使用的数值，而不是让 Rust 自动推断应该借用这些数值。如清单 16-5 所示，对清单 16-3 所做的修改将会按照我们的预期进行编译和运行。

<列表编号="16-5" 文件名称="src/main.rs" 标题="使用 `move` 关键字强制闭包拥有其使用的数值">

```rust
{{#rustdoc_include ../listings/ch16-fearless-concurrency/listing-16-05/src/main.rs}}
```

</ Listing>

我们可能会想要尝试同样的方法来修复清单16-4中的代码，其中主线程通过`move`闭包调用`drop`。然而，这种修复方法是不可行的，因为清单16-4的这种做法是由于不同的原因而被禁止的。如果我们向闭包中添加`move`，那么`v`就会进入闭包的环境，而我们在主线程中就无法再调用`drop`了。相反，我们会遇到编译错误。

```console
{{#include ../listings/ch16-fearless-concurrency/output-only-01-move-drop/output.txt}}
```

Rust的所有权规则再次帮了我们大忙！由于Listing 16-3中的代码出现了错误，因为Rust采用了保守的策略，只将`v`借给线程使用，这意味着主线程理论上可以使得子线程对`v`的引用失效。通过告诉Rust将`v`的所有权移交给子线程，我们向Rust保证主线程将不再使用`v`。如果我们以同样的方式修改Listing 16-4，那么在主线程中尝试使用`v`时，就会违反所有权规则。而`move`这个关键字则覆盖了Rust默认的保守策略，它不允许我们违反所有权规则。

既然我们已经了解了线程是什么以及线程API提供了哪些方法，接下来让我们看看在哪些情况下可以使用线程。

[capture]: ch13-01-closures.html#捕获引用或转移所有权