<!-- Old headings. Do not remove or links may break. -->

<a id="streams"></a>

## 流：序列中的未来值

请回想一下，在本章的 [“Message Passing”][17-02-messages]<!-- ignore --> 部分中，我们是如何使用接收器来处理异步通道的。异步`recv`方法会随时间产生一系列数据项。这实际上是一种更为通用的模式，被称为“流”。许多概念都可以自然地以流的形式来表示：数据项在队列中依次被处理，当完整的数据集过大而无法存储在计算机内存中时，数据会分批从文件系统中获取，或者数据会通过网络随时间逐渐传输过来。由于流本质上是未来，因此我们可以将流与其他类型的未来进行结合，以创造有趣的效果。例如，我们可以批量处理事件，从而避免触发过多的网络调用；为长时间运行的操作设置超时时间；或者限制用户界面事件的触发频率，以避免不必要的操作。

我们在第13章中讨论过Iterator trait时提到过一些内容，不过迭代器和异步通道接收器之间确实存在两个关键区别。第一个区别是时间上的差异：迭代器是同步的，而通道接收器则是异步的。第二个区别是API的设计差异。当直接处理 `Iterator` 时，我们调用的是其同步的 `next` 方法。而针对 `trpl::Receiver` 流，我们则调用了异步的 `recv` 方法。除此之外，这些API在功能上非常相似，这种相似性并非偶然。流其实是一种异步的迭代方式。虽然 `trpl::Receiver` 会专门等待接收消息，但通用流API的功能要广泛得多：它像 `Iterator` 一样提供下一个元素，但采用的是异步方式。

在Rust中，迭代器和流之间的相似性意味着我们实际上可以从任何迭代器创建一个流。与迭代器一样，我们可以通过调用流的 `next` 方法来处理流，然后等待输出结果，就像在Listing 17-21中所做的那样。不过，目前这个代码还无法编译。

<Listing number="17-21" caption="Creating a stream from an iterator and printing its values" file-name="src/main.rs">

```rust,ignore,does_not_compile
        let values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
        let iter = values.iter().map(|n| n * 2);
        let mut stream = trpl::stream_from_iter(iter);

        while let Some(value) = stream.next().await {
            println!("The value was: {value}");
        }

```

</Listing>

我们首先从一个数字数组开始，将其转换为迭代器，然后调用 `map` 函数来将所有数值翻倍。之后，我们使用 `trpl::stream_from_iter` 函数将迭代器转换为流。接下来，通过 `while let` 循环来遍历流中的各项元素。

不幸的是，当我们尝试运行这段代码时，它无法编译，反而显示没有 `next` 这个方法的存在。

<!-- manual-regeneration
cd listings/ch17-async-await/listing-17-21
cargo build
copy only the error output
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

正如这个输出所解释的，编译器出现错误的原因是，我们需要在作用域中使用正确的特质，才能使用 `next` 方法。根据我们目前的讨论，你可能会认为该特质应该是 `Stream`，但实际上它是 `StreamExt`。 `Ext` 是 _扩展_ 的缩写，在 Rust 社区中，这是一种常用的方法，用于通过一个特质来扩展另一个特质。

`Stream` trait 定义了一个低级别的接口，实际上结合了`Iterator`和`Future` trait的功能。`StreamExt`则提供了更高级别的API，这些API建立在`Stream`的基础上，包括`next`方法以及其他类似于`Iterator` trait所提供的实用方法。`Stream`和`StreamExt`目前尚未成为Rust标准库的一部分，但大多数生态系统库都采用了类似的定义。

解决编译错误的方法是在`trpl::StreamExt`语句中添加一个 `use`语句，如清单17-22所示。

<Listing number="17-22" caption="Successfully using an iterator as the basis for a stream" file-name="src/main.rs">

```rust
use trpl::StreamExt;

fn main() {
    trpl::block_on(async {
        let values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
        // --snip--

```

</Listing>

将所有这些部分组合在一起后，这段代码就按照我们的预期运行了！此外，现在我们已经在作用域中获得了 `StreamExt`，因此我们可以像使用迭代器一样使用它的所有实用方法。

[17-02-messages]: ch17-02-concurrency-with-async.html#message-passing
[iterator-trait]: ch13-02-iterators.html#the-iterator-trait-and-the-next-method
