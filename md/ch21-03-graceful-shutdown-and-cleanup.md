## 优雅的关闭与清理

清单21-20中的代码正是按照我们的意图，通过线程池来异步处理请求。我们收到了一些关于`workers`、`id`和`thread`字段的警告，这些字段我们没有直接使用，这提醒我们需要进行清理工作。当我们使用不太优雅的<kbd>ctrl</kbd>-<kbd>C</kbd>方法来终止主线程时，所有其他线程也会立即停止，即使它们正在处理某个请求。

接下来，我们将实现 ``Drop`` 特性，以便在池中的每个线程上调用 ``join``，这样它们在关闭之前就能完成正在处理的请求。然后，我们将实现一种机制，让线程知道应该停止接受新请求并关闭自身。为了观察这段代码的实际效果，我们将修改我们的服务器，使其在优雅地关闭线程池之前只处理两个请求。

需要注意的是：这些内容不会影响那些负责执行闭包的代码部分，因此如果我们使用线程池来实现异步运行环境，这里的所有内容都将保持不变。

### 在 `ThreadPool` 上实现 `Drop` 特性

让我们从在线程池中实现`Drop`开始。当线程池被释放时，所有的线程都应该加入该线程池，以确保它们能够完成自己的工作。清单21-22展示了对`Drop`实现的第一种尝试；不过这段代码目前还无法正常工作。

<列表编号="21-22" 文件名称="src/lib.rs" 标题="当线程池超出作用域时连接每个线程">

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch21-web-server/listing-21-22/src/lib.rs:here}}
```

</清单>

首先，我们遍历每个线程池中的`workers`。我们使用`&mut`来实现这一点，因为`self`是一个可变的引用，同时我们还需要能够修改`worker`。对于每一个`worker`实例，我们会打印一条消息，说明这个特定的`Worker`实例正在关闭。然后，我们调用`join`来处理那个`Worker`实例所属的线程。如果调用`join`失败，我们就使用`unwrap`来让Rust执行相应的操作。出现恐慌，导致不优雅的关闭。

当我们编译这段代码时，会遇到以下错误：

```console
{{#include ../listings/ch21-web-server/listing-21-22/output.txt}}
```

该错误提示我们无法调用`join`，因为我们只有一个可变的引用，而`worker`和`join`分别拥有它们各自的参数。为了解决这个问题，我们需要将线程从拥有`thread`的`Worker`实例中移出，这样`join`就可以处理这个线程了。一种方法是采用清单18-15中的方法。如果`Worker`持有某个……`Option<thread::JoinHandle<()>>`,我们可以在`Option`上调用`take`方法，将值从`Some`变体中移出，并在其位置留下一个`None`变体。换句话说，正在运行的`Worker`会在`thread`中有一个`Some`变体。当我们想要清理`Worker`时，我们会用`None`替换`Some`，这样`Worker`就不会有线程在运行了。

不过，这种情况只会出现在删除`Worker`的时候。作为交换，我们必须在任何访问`worker.thread`的地方处理`Option<thread::JoinHandle<()>>`。Rust中的惯用做法是使用`Option`相当频繁，但当你发现需要某种变通方法，而这种方法表明`Option`中必定包含某些内容时，那么寻找其他方法来使代码更简洁、减少错误的发生是个好主意。

在这种情况下，有一个更好的替代方案：`Vec::drain`方法。它接受一个范围参数来指定要从向量中移除哪些元素，并返回一个包含这些元素的迭代器。使用`..`的范围语法将移除向量中的*所有*元素。

因此，我们需要像这样更新 `ThreadPool` `drop` 的实现：

<listing file-name="src/lib.rs">

```rust
{{#rustdoc_include ../listings/ch21-web-server/no-listing-04-update-drop-definition/src/lib.rs:here}}
```

</清单>

这解决了编译器的错误，并且不需要对我们的代码进行任何其他修改。需要注意的是，由于`drop`函数在出现恐慌时可以被调用，因此`unwrap`函数也可能出现恐慌，从而导致双重恐慌，这会立即使程序崩溃，并终止正在进行的任何清理操作。这对于示例程序来说是可以接受的，但不建议用于生产代码。

### 通知线程停止接收任务

经过所有这些修改之后，我们的代码可以顺利编译，没有出现任何警告。不过，坏消息是，这段代码并没有按照我们的预期运行。问题的关键在于``Worker``实例由线程执行的逻辑：目前，我们调用了``join``，但这并不会关闭线程，因为线程会继续不断地执行``loop``来寻找任务。如果我们试图停止这些线程……使用我们当前的实现方式，即`drop`，主线程将会永远阻塞，等待第一个线程完成。

为了解决这个问题，我们需要修改 `ThreadPool` 和 `drop` 的实现，同时还需要修改 `Worker` 中的循环结构。

首先，我们将`ThreadPool`和`drop`的实现改为在等待线程完成之前显式地移除`sender`。清单21-23展示了对`ThreadPool`的修改，以显式地移除`sender`。与线程的情况不同，在这里我们需要使用`Option`来将`sender`从`ThreadPool`中移出，同时使用`Option::take`来实现这一操作。

<列表编号="21-23" 文件名称="src/lib.rs" 标题="在合并 `Worker` 线程之前显式删除 `sender`">

```rust,noplayground,not_desired_behavior
{{#rustdoc_include ../listings/ch21-web-server/listing-21-23/src/lib.rs:here}}
```

</清单>

放弃`sender`会关闭通道，这意味着不会再发送任何消息。当这种情况发生时，所有由`Worker`实例在无限循环中调用的`recv`都会返回错误。在清单21-24中，我们修改了`Worker`循环，使其在那种情况下能够优雅地退出循环，这意味着当`ThreadPool`调用`drop`时，线程将会完成它们的任务。

<列表编号="21-24" 文件名称="src/lib.rs" 标题="当`recv`返回错误时显式跳出循环">

```rust,noplayground
{{#rustdoc_include ../listings/ch21-web-server/listing-21-24/src/lib.rs:here}}
```

</清单>

为了看到这段代码的实际应用，让我们修改 `main`，使其只能接受两个请求，然后像清单21-25中所示，优雅地关闭服务器。

<列表编号="21-25" 文件名称="src/main.rs" 标题="在处理两个请求后通过退出循环来关闭服务器">

```rust,ignore
{{#rustdoc_include ../listings/ch21-web-server/listing-21-25/src/main.rs:here}}
```

</清单>

你肯定不希望一个现实世界的网络服务器在只处理了两次请求之后就关闭。这段代码仅仅证明了优雅的关闭和清理操作是正常工作的。

`take`方法定义在`Iterator` trait中，并且最多将迭代限制在前两项上。`ThreadPool`将在`main`结束时退出作用域，而`drop`的实现将会运行。

使用`cargo run`启动服务器，并发送三个请求。第三个请求应该会引发错误，在终端中，你应该能看到类似这样的输出：

<!-- 手动重新生成
cd listings/ch21-web-server/listing-21-25
cargo run
curl http://127.0.0.1:7878
curl http://127.0.0.1:7878
curl http://127.0.0.1:7878
第三次请求会出错，因为服务器已经关闭了
将输出内容复制下来
无法自动化处理，因为输出结果取决于请求的发送
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

您可能会看到`Worker`的ID和消息的排序方式有所不同。从消息中可以了解到这段代码的工作原理：`Worker`实例0和3分别处理了前两个请求。在第二个连接之后，服务器停止接受新的连接；而`ThreadPool`上的`Drop`实现在`Worker 3`开始执行之前就已经开始执行了。删除`sender`会导致所有连接都被断开。调用`Worker`实例，并指示它们关闭。当`Worker`实例断开连接时，每个实例都会打印一条消息，然后线程池会调用`join`，等待每个`Worker`线程完成工作。

请注意这次执行的一个有趣之处：`ThreadPool`先抛出了`sender`；在`Worker`出现错误之前，我们尝试了`Worker 0`的合并操作。`Worker 0`尚未从`recv`那里收到错误，因此主线程被阻塞，等待`Worker 0`完成。与此同时，`Worker 3`收到了一个任务，然后所有线程都出现了错误。当`Worker 0`完成后……主线程等待其余的`Worker`实例完成。在那时，它们都已经退出了各自的循环并停止了运行。

恭喜！我们现在已经完成了项目。我们拥有一个基本的Web服务器，该服务器使用线程池来异步响应请求。我们能够优雅地关闭服务器，从而清理掉线程池中的所有线程。

以下是完整的代码供参考：

<listing file-name="src/main.rs">

```rust,ignore
{{#rustdoc_include ../listings/ch21-web-server/no-listing-07-final-code/src/main.rs}}
```

</清单>

<listing file-name="src/lib.rs">

```rust,noplayground
{{#rustdoc_include ../listings/ch21-web-server/no-listing-07-final-code/src/lib.rs}}
```

</清单>

我们还可以做得更多！如果您希望继续完善这个项目，以下是一些建议：

- 为 ``ThreadPool`` 及其公共方法添加更多文档说明。  
- 对库的功能进行测试。  
- 改进对 ``unwrap`` 的调用方式，以提供更强大的错误处理功能。  
- 使用 ``ThreadPool`` 来执行除处理网络请求之外的其他任务。  
- 在[crates.io](https://crates.io/)上查找一个线程池库，并使用该库实现一个类似的Web服务器。然后，将其API和可靠性与我们实现的线程池进行比较。

## 摘要

干得好！你已经读完了这本书！我们想感谢你加入我们的Rust之旅。现在你可以开始实现自己的Rust项目，并帮助其他人完成他们的项目。请记住，还有一群热情的Rust开发者愿意在你遇到任何挑战时为你提供帮助。