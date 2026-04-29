<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="streams"></a>

## 流：序列中的未来

还记得在本章的[“消息传递”][17-02-messages]<!-- ignore -->部分中，我们如何使用接收器来处理异步通道吗？async`recv`方法会随时间产生一系列数据项。这实际上是一种更为通用的模式，被称为“流”。许多概念都可以自然地表示为流：数据项在队列中逐渐可用，或者当完整的数据集无法一次性获取时，从文件系统中逐步提取数据块。对于计算机的内存来说，数据量很大；或者随着时间的推移，通过网络传输的数据量也在不断增加。由于流代表了未来的状态，我们可以将其与其他类型的未来时态结合使用，以创造有趣的效果。例如，我们可以将事件分批处理，以避免触发过多的网络调用；为长时间运行的操作设置超时时间；或者限制用户界面事件的触发频率，从而避免不必要的操作。

我们在第13章中讨论过`IteratorTrait`时，提到了[“Iterator Trait与`next`方法”][iterator-trait]<!--ignore-->这一节。不过，迭代器与`theasync`通道接收器之间还是存在两个区别。第一个区别在于时间：迭代器是同步的，而通道接收器则是异步的。第二个区别在于API设计。当直接操作`Iterator`时，我们会发现它是同步的。使用`next`方法。特别是对于`trpl::Receiver`流，我们调用了异步的`recv`方法。否则，这些API看起来非常相似，而这种相似性并非偶然。流就像是一种异步的迭代方式。虽然`trpl::Receiver`会专门等待接收消息，但通用流API的范围要广泛得多：它以与`Iterator`相同的方式提供下一个元素，但采用的是异步方式。

在Rust中，迭代器和流之间的相似性意味着我们实际上可以从任何迭代器创建一个流。与迭代器一样，我们可以通过调用流的`next`方法来处理流，然后等待输出结果，如清单17-21所示，不过目前这个代码还无法编译。

<List numbering="17-21" caption="从迭代器创建流并打印其值" file-name="src/main.rs">

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch17-async-await/listing-17-21/src/main.rs:stream}}
```

</清单>

我们首先从一个数字数组开始，将其转换为迭代器，然后调用`map`函数来将所有的数值加倍。接着，我们使用`trpl::stream_from_iter`函数将迭代器转换为流。接下来，通过`while let`循环来遍历流中的各项元素。

不幸的是，当我们尝试运行这段代码时，它无法编译，反而显示没有`next`这个方法可用。

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

正如这个输出所解释的那样，编译器出现错误的原因是，我们需要在当前作用域中拥有正确的特质，才能使用`next`方法。根据我们之前的讨论，你可能会认为该特质应该是`Stream`，但实际上它是`StreamExt`。作为扩展的缩写，`Ext`是Rust社区中常用的一种模式，用于通过另一个特质来扩展一个特质。

`Stream` 特性定义了一个低级接口，它实际上结合了 `Iterator` 和 `Future` 特性。`StreamExt` 则在 `Stream` 的基础上提供了更高级别的 API，包括 `next` 方法以及其他类似于 `Iterator` 特性所提供的实用方法。`Stream` 和 `StreamExt` 目前还不是 Rust 标准库的一部分，但大多数生态系统中的库都使用了类似的定义。

解决编译错误的方法是在`trpl::StreamExt`中添加一条`use`语句，如清单17-22所示。

<List numbering="17-22" caption="成功地将迭代器作为流的基础" file-name="src/main.rs">

```rust
{{#rustdoc_include ../listings/ch17-async-await/listing-17-22/src/main.rs:all}}
```

</清单>

将所有这些部分组合在一起后，这段代码就按照我们的预期运行了！此外，现在我们已经将`StreamExt`纳入了作用域中，因此我们可以像使用迭代器一样使用它的所有实用方法。

[17-02-消息]: ch17-02-并发与异步.html#消息传递  
[迭代器特性]: ch13-02-迭代器.html#迭代器特性与next方法