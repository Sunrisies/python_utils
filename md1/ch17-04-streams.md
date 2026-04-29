<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="streams"></a>

## 流：序列中的未来值

还记得在本章前面的[“消息传递”][17-02-messages]部分中，我们如何使用接收器来处理异步通道吗？异步`recv`方法会随时间产生一系列数据。这实际上是一种更为通用的模式，被称为_流_。许多概念都可以自然地以流的形式来表示：数据在队列中逐渐可用，当完整的数据集过大而无法存储在计算机内存中时，数据会从文件系统中逐步获取，或者数据会通过网络随时间不断传输进来。由于流本质上是未来，因此我们可以将它们与其他类型的未来元素结合使用，并以有趣的方式将它们组合在一起。例如，我们可以批量处理事件，以避免触发过多的网络调用；为长时间运行的操作设置超时时间；或者限制用户界面事件的触发频率，从而避免不必要的操作。

我们在第13章中讨论过`Iterator`特性时提到过相关内容，当时我们学习了[“The Iterator Trait and the `next` Method”][iterator-trait]这篇文章。不过，迭代器和异步通道接收器之间还是存在两个主要的区别。第一个区别在于时间：迭代器是同步的，而通道接收器则是异步的。第二个区别是API的设计。当我们直接操作`Iterator`时，会调用其同步的`next`方法。而对于`trpl::Receiver`这种流，则调用了异步的`recv`方法。除此之外，这两种API在功能上非常相似，而这种相似性并非偶然。流其实是一种异步的迭代方式。虽然`trpl::Receiver`会专门等待接收消息，但通用流API的功能要广泛得多：它像`Iterator`那样提供下一个元素，但采用的是异步方式。

在Rust中，迭代器和流之间的相似性意味着我们实际上可以从任何迭代器中创建一个流。与迭代器一样，我们可以通过调用流的`next`方法来处理流，然后等待输出结果，就像清单17-21中所做的那样。不过，目前这个代码还无法编译。

<Listing number="17-21" caption="从迭代器中创建流并打印其值" file-name="src/main.rs">

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch17-async-await/listing-17-21/src/main.rs:stream}}
```

</ Listing>

我们首先从一个数字数组开始，将其转换为迭代器，然后调用`map`函数来对所有的数值进行翻倍处理。之后，我们使用`trpl::stream_from_iter`函数将迭代器转换为流。接下来，通过`while let`循环来遍历流中的各项元素。

不幸的是，当我们尝试运行这段代码时，它无法编译，而是显示没有`next`这个方法可用。

<!-- 手动重新生成
cd listings/ch17-async-await/listing-17-21
cargo build
仅复制错误输出内容
-->

```text
error[E0599]: no method named `next` found for struct `tokio_stream::iter::Iter` in the current scope
  --> src/main.rs:10:40
   |
10 |         while let Some(value) = stream.next().await {
   |                                        ^^^^
   |
   = help: items from traits can only be used if the trait is in scope
help: the following traits which provide `next` are implemented but not in scope; perhaps you want to import one of them
   |
1  + use crate::trpl::StreamExt;
   |
1  + use futures_util::stream::stream::StreamExt;
   |
1  + use std::iter::Iterator;
   |
1  + use std::str::pattern::Searcher;
   |
help: there is a method `try_next` with a similar name
   |
10 |         while let Some(value) = stream.try_next().await {
   |                                        ~~~~~~~~
```

正如这个输出所解释的，编译器错误的原因在于我们需要在作用域中使用正确的特质，才能使用`next`方法。根据我们目前的讨论，你可能会认为该特质应该是`Stream`，但实际上它是`StreamExt`。作为扩展的缩写，`Ext`是Rust社区中常用的一种模式，用于通过另一个特质来扩展一个特质。

`Stream` 特性定义了一个低级接口，该接口实际上结合了 `Iterator` 和 `Future` 特性。`StreamExt` 则在 `Stream` 的基础上提供了更高级别的 API，其中包括 `next` 方法以及其他类似于 `Iterator` 特性所提供的实用方法。`Stream` 和 `StreamExt` 目前尚未成为 Rust 标准库的一部分，但大多数生态系统中的库都采用了类似的定义。

解决编译错误的方法是在`trpl::StreamExt`中添加一条`use`语句，如清单17-22所示。

<Listing number="17-22" caption="成功地将迭代器用作流的基础" file-name="src/main.rs">

```rust
{{#rustdoc_include ../listings/ch17-async-await/listing-17-22/src/main.rs:all}}
```

</ Listing>

将所有这些部分组合在一起后，这段代码就按照我们的预期运行了！此外，现在我们已经将`StreamExt`纳入了作用域中，因此我们可以像使用迭代器一样使用它的所有实用方法。

[17-02-messages]: ch17-02-concurrency-with-async.html#message-passing  
[iterator-trait]: ch13-02-iterators.html#the-iterator-trait-and-the-next-method