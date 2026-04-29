## 期货与异步语法

Rust中异步编程的关键元素包括_futures_以及Rust的`async`和`await`关键字。

**未来值**是一种目前可能尚未准备好，但在未来的某个时间点会准备好的事物。（这一概念在许多语言中都有体现，有时被称为**任务**或**承诺**。）Rust提供了一个名为``Future``的特质，作为构建模块，使得不同的异步操作可以使用不同的数据结构来实现，但具有共同的接口。在Rust中，未来值是实现了``Future``特质的类型。每个未来值都包含自己的信息。关于已经取得的进展，以及“准备就绪”的含义。

你可以将 ``async`` 这个关键字应用于代码块和函数中，以指定它们可以被中断和恢复。在异步代码块或异步函数中，你可以使用 ``await`` 关键字来 `_等待一个未来对象_`（即，等待它变得可用）。在任何需要等待未来对象可用的地方，都可以让该代码块或函数暂停并恢复执行。通过检查未来对象的值是否已经准备好这一过程，被称为`_轮询_`。

其他一些语言，如C#和JavaScript，也使用`async`和`await`这两个关键字来进行异步编程。如果你熟悉这些语言，可能会注意到Rust在处理这种语法时存在一些显著的差异。这是有原因的，我们稍后会了解！

在编写异步Rust代码时，我们大多数时候会使用`async`和`await`这两个关键字。Rust会将这些关键字编译成等效的代码，使用的是`Future`特性；同样地，Rust也会将`for`这样的循环结构编译成等效的代码，使用的是`Iterator`特性。不过，由于Rust还提供了`Future`特性，因此当你需要的时候，也可以为自己的数据类型实现这一特性。我们将会看到许多使用这一特性的函数。在本章中，所有返回类型都拥有自己的`Future`实现。我们将在章节末尾回到该特性的定义，并进一步了解其工作原理。不过，这些细节已经足够让我们继续前进了。

这一切可能看起来有些抽象，那么让我们来编写第一个异步程序：一个小型的网页抓取工具。我们将从命令行传入两个URL，同时获取这两个页面的内容，然后返回最先完成处理的那个页面的结果。这个例子会涉及到一些新的语法，不过不用担心——我们会逐步解释所有需要了解的内容。

## 我们的第一个异步程序

为了将本章的重点放在异步编程上，而不是生态系统的各个部分，我们创建了`trpl`这个包（`trpl`是“Rust编程语言”的缩写）。这个包重新导出了你需要的所有类型、特质和函数，这些功能主要来自[futures-crate]<!-- 忽略 -->和[tokio]<!-- 忽略 -->这两个包。`futures`这个包是一个官方的开发环境。用于Rust异步代码实验，而`Future`特质正是基于这个场景设计的。Tokio是当今Rust中最广泛使用的异步运行时，尤其适用于Web应用程序。还有其他优秀的运行时可供选择，它们可能更适合你的需求。我们在底层使用`tokio`crate来实现`trpl`功能，因为它经过充分测试且被广泛使用。

在某些情况下，``trpl``还会重新命名或包装原始API，以便您能够专注于与本章相关的细节。如果您想了解该库的具体功能，我们建议您查看其[源代码]。您将能够看到每个重新导出的库来自哪个库，并且我们留下了详细的注释来解释这些库的功能。

创建一个新的名为`hello-async`的二进制项目，并将`trpl` crate作为依赖项添加到项目中。

```console
$ cargo new hello-async
$ cd hello-async
$ cargo add trpl
```

现在，我们可以使用`trpl`提供的各种代码来编写我们的第一个异步程序。我们将构建一个小型命令行工具，该工具会获取两个网页，从每个网页中提取`<title>`元素，然后打印出最先完成整个过程的那个网页的标题。

### 定义page_title函数

让我们首先编写一个函数，该函数接受一个页面URL作为参数，向该页面发起请求，并返回`<title>`元素的文本（参见清单17-1）。

<list numbering="17-1" file-name="src/main.rs" caption="定义一个异步函数，用于从HTML页面中获取标题元素">

```rust
{{#rustdoc_include ../listings/ch17-async-await/listing-17-01/src/main.rs:all}}
```

</清单>

首先，我们定义一个名为`page_title`的函数，并使用`async`关键字对其进行标记。然后，我们使用`trpl::get`函数来获取传递进来的URL中的内容，并将`await`关键字用于等待响应。为了获取`response`的文本，我们调用其`text`方法，并再次使用`await`关键字来等待响应。这两个步骤都是异步进行的。对于`get`函数，我们有……需要等待服务器发送其响应的第一部分，该部分将包含HTTP头信息、Cookie等，并且可以独立于响应主体进行传输。特别是当响应主体非常大时，可能需要一段时间才能全部接收完毕。由于我们必须等待整个响应到达，因此`text`方法也是异步的。

我们必须显式地等待这两个未来值，因为Rust中的未来值是`lazy`的：除非你使用``await``关键字来调用它们，否则它们不会执行任何操作。（实际上，如果你不使用未来值，Rust会显示一个编译器警告。）这可能会让你想起第13章中“使用迭代器处理一系列项目”部分的讨论。除非你调用它们的``next``方法——无论是直接调用还是通过其他方式。使用 ``for`` 这样的循环或方法，或者使用 ``map`` 这类在底层使用了 ``next`` 的方法。同样地，除非你明确要求，否则未来不会执行任何操作。这种惰性特性使得 Rust 能够避免在实际需要之前运行异步代码。

注意：这与我们在第16章的“使用spawn创建新线程”部分中使用`thread::spawn`时的行为不同。在那一节中，我们传递给另一个线程的闭包会立即开始运行。这也与许多其他语言处理异步方式有所不同。不过，对于Rust来说，能够提供性能保证是非常重要的，就像对迭代器一样。

一旦我们得到了`response_text`，我们就可以使用`Html::parse`将其解析为`Html`类型的实例。现在，我们不再使用原始字符串，而是有了一种可以用来处理HTML的数据类型，使得HTML能够作为更复杂的数据结构来使用。具体来说，我们可以使用`select_first`方法来找到给定CSS选择器的第一个实例。通过传递字符串`"title"`，我们将在文档中找到第一个`<title>`元素，如果有的话。因为可能没有任何匹配的元素。element, `select_first` 返回的是一个 `Option<ElementRef>`。最后，我们使用 `Option::map` 方法，它允许我们在 `Option` 中存在时处理该元素，如果不存在则什么都不做。（我们也可以使用 `match` 表达式，但 `map` 更符合编程习惯。）在提供给 `map` 的函数体内，我们调用 `inner_html` 来处理 `title`，以获取其内容。`String`。归根结底，我们得到的是`Option<String>`。

请注意，Rust中的`await`这个关键字位于等待的表达式之后，而不是之前。也就是说，它是一个后缀关键字。如果你在其他语言中使用过`async`，那么这种用法可能会与你习惯的有所不同。但在Rust中，这种方式使得方法链的处理更加方便。因此，我们可以像清单17-2中所展示的那样，将`page_title`的内容修改为将`trpl::get`和`text`的函数调用与`await`连接在一起。

<列表编号="17-2" 文件名称="src/main.rs" 标题="使用 `await` 关键字进行链式操作">

```rust
{{#rustdoc_include ../listings/ch17-async-await/listing-17-02/src/main.rs:chaining}}
```

</清单>

就这样，我们成功编写了第一个异步函数！在我们在`main`中添加一些代码来调用它之前，让我们再详细了解一下我们所编写的内容以及它的含义。

当Rust遇到带有`async`关键字的`_block_`时，它会将其编译成一个唯一、匿名的数据类型，该数据类型实现了`Future`特性。当Rust遇到带有`async`标记的`_function_`时，它会将其编译成一个非异步函数，该函数的主体是一个异步块。异步函数的返回类型就是编译器为该异步块创建的匿名数据类型的类型。

因此，编写 ``async fn`` 相当于编写一个返回指定返回类型的函数的代码。对于编译器来说，像 Listing 17-1 中的 ``async fn page_title``这样的函数定义，大致等同于这样定义的非异步函数。

```rust
# extern crate trpl; // required for mdbook test
use std::future::Future;
use trpl::Html;

fn page_title(url: &str) -> impl Future<Output = Option<String>> {
    async move {
        let text = trpl::get(url).await.text().await;
        Html::parse(&text)
            .select_first("title")
            .map(|title| title.inner_html())
    }
}
```

让我们逐一分析这个转换后的版本中的每一部分：

它使用了我们在第10章的“Traits as Parameters”部分中讨论过的`impl Trait`语法。返回的值实现了`Future`特质，其关联类型为`Output`。请注意，`Output`的类型是`Option<String>`，这与`async fn`版本中的原始返回类型相同。在原始函数的主体中调用的所有代码都被包裹在……这是一个 ``async move`` 块。记住，这些块实际上就是表达式。整个块就是该函数返回的表达式。- 这个异步块会生成一个类型为 ``Option<String>`` 的值，正如之前所描述的那样。这个值与返回类型中的 ``Output`` 类型相匹配。这和你之前见过的其他块没什么不同。- 新的函数主体是一个 ``async move`` 块，因为它使用了...`url`参数。（我们在本章后面会详细讨论`async`与`async move`的区别。）

现在我们可以在`main`中调用`page_title`。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="确定单页标题"></a>

### 使用运行时执行异步函数

首先，我们将获取单个页面的标题，如清单17-3所示。  
遗憾的是，这段代码目前还无法编译。

<列表编号="17-3" 文件名称="src/main.rs" 标题="使用用户提供的参数从`main`调用`page_title`函数">

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch17-async-await/listing-17-03/src/main.rs:main}}
```

</清单>

我们在第12章的“接受命令行参数”部分中使用了相同的模式来获取命令行参数。然后，我们将URL参数传递给`page_title`，并等待结果。由于未来表达式产生的值是一个`Option<String>`，我们使用`match`表达式来打印不同的消息，以便根据页面是否包含`<title>`来做出相应的处理。

我们唯一可以使用`await`这个关键字的地方是在异步函数或代码块中，而Rust不会允许我们将特殊的`main`函数标记为`async`。

<!-- 手动重新生成
cd listings/ch17-async-await/listing-17-03
cargo build
仅复制编译器产生的错误
-->

```text
error[E0752]: `main` function is not allowed to be `async`
 --> src/main.rs:6:1
  |
6 | async fn main() {
  | ^^^^^^^^^^^^^^^ `main` function is not allowed to be `async`
```

之所以无法将`main`标记为`async`，是因为异步代码需要一个运行时环境：一个能够管理异步代码执行细节的Rust库。程序的`main`函数可以初始化一个运行时环境，但它本身并不是一个完整的运行时系统。（稍后我们会进一步了解为什么会这样。）每个执行异步代码的Rust程序，至少都有一个地方需要设置一个能够执行未来操作的运行时环境。

大多数语言都支持异步捆绑运行时，但Rust并不支持这一点。相反，有许多不同的异步运行时可供选择，每种运行时都针对特定的使用场景做出了不同的权衡。例如，一个具有高吞吐量、拥有大量CPU核心和大量内存的Web服务器，与那些只有单个核心、内存较少且没有堆分配能力的微控制器相比，有着截然不同的需求。提供这些运行时的库也各不相同。提供常见功能的异步版本，例如文件或网络I/O功能。

在本章的其余部分，我们将使用来自`trpl`库的`block_on`函数。该函数接受一个未来对象作为参数，并阻塞当前线程，直到该未来对象执行完毕。在幕后，调用`block_on`会启动一个运行时环境，该环境使用`tokio`库来运行传入的未来对象（`trpl`库的`block_on`功能与之类似）。其他运行时库中的`block_on`函数。一旦未来执行完成，`block_on`就会返回未来所产生的值。

我们可以将`page_title`返回的未来结果直接传递给`block_on`。一旦`block_on`完成，我们就可以匹配到`Option<String>`的结果，就像我们在Listing 17-3中所尝试的那样。然而，对于本章中的大多数示例（以及现实世界中的大多数异步代码），我们进行的操作不仅仅是一次异步函数调用。因此，我们会传递一个`async`块，并显式地等待`page_title`调用的结果，如Listing 17-4所示。

<List listing-number="17-4" caption="等待一个包含`trpl::block_on`的异步块" file-name="src/main.rs">

<!-- should_panic,noplayground 因为 mdbook 测试未通过参数验证 -->

```rust,should_panic,noplayground
{{#rustdoc_include ../listings/ch17-async-await/listing-17-04/src/main.rs:run}}
```

</清单>

当我们运行这段代码时，我们得到了最初预期的行为：

<!-- 手动重新生成
cd listings/ch17-async-await/listing-17-04
cargo build # 跳过所有的构建过程
cargo run -- "https://www.rust-lang.org"
# 将输出文件复制到此处
-->

```console
$ cargo run -- "https://www.rust-lang.org"
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.05s
     Running `target/debug/async_await 'https://www.rust-lang.org'`
The title for https://www.rust-lang.org was
            Rust Programming Language
```

呼——我们终于有一些可以运行的异步代码了！但在我们将这段代码添加到让两个站点相互竞争之前，让我们先简要了解一下`future`是如何工作的。

每一个`_等待点`——也就是说，代码中使用__`INLINE_CODE_127__`的每个位置——都代表一个控制权被返回给运行时的地方。为了实现这一点，Rust需要跟踪与异步代码块相关的状态，这样运行时就可以开始执行其他任务，然后在准备好时再次尝试推进第一个任务。这实际上是一个看不见的状态机，就像你在每个`等待点`处定义了一个枚举来保存当前状态一样：

```rust
{{#rustdoc_include ../listings/ch17-async-await/no-listing-state-machine/src/lib.rs:enum}}
```

手动编写代码来实现各个状态之间的切换会非常繁琐且容易出错，尤其是在需要向代码中添加更多功能以及更多状态时。幸运的是，Rust编译器会自动创建和管理异步代码中的状态机数据结构。关于数据结构的一些常规借用和所有权规则仍然适用，而且令人欣慰的是，编译器还会负责检查这些问题，为我们处理这些工作。有用的错误信息。我们将在章节的后面部分详细讨论其中的一些信息。

最终，必须有一些东西来执行这个状态机，而那个东西就是运行时。（这就是为什么在了解运行时时，可能会遇到“执行器”这个词：执行器是运行时中负责执行异步代码的部分。）

现在您可以理解为什么编译器在 Listing 17-3 中阻止我们将 `main` 本身定义为异步函数了。如果 `main` 是一个异步函数，那么就需要其他代码来管理 `main` 返回的内容的状态机。但是，`main` 才是程序的起点！因此，我们在 `main` 中调用了 `trpl::block_on` 函数来设置运行环境并执行未来的操作。由`async`块返回，直到其完成。

注意：一些运行时提供了宏，因此您可以编写一个异步的``main``函数。这些宏会将``async fn main() { ... }``重写为普通的`fn main`，其实现方式与我们在Listing 17-4中手动编写的方式相同：调用一个函数，该函数会启动一个未来任务以完成操作，就像``trpl::block_on``所做的那样。

现在，让我们把这些部分整合起来，看看如何编写并发代码。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="我们的两个网址相互竞争"></a>

### 同时比较两个URL的优劣

在清单17-5中，我们通过从命令行传递两个不同的URL来调用`page_title`，并通过选择哪个函数先完成来比较它们的执行速度。

<List numbering="17-5" caption="调用 `page_title` 来处理两个 URL，查看哪个会先返回结果" file-name="src/main.rs">

<!-- should_panic,noplayground 因为 mdbook 不传递参数 -->

```rust,should_panic,noplayground
{{#rustdoc_include ../listings/ch17-async-await/listing-17-05/src/main.rs:all}}
```

</清单>

我们首先调用`page_title`来处理每个用户提供的URL。我们将得到的未来值分别保存在`title_fut_1`和`title_fut_2`中。请注意，这些目前还不做任何事情，因为未来值是惰性计算的，我们还没有等待它们完成。然后，我们将这些未来值传递给`trpl::select`，该函数会返回一个值，指示哪个未来值先完成处理。

注意：在底层，``trpl::select`` 是基于 ``futures`` 模块中定义的更通用的 ``select`` 函数构建的。``futures`` 模块的 ``select`` 函数可以执行许多 ``trpl::select`` 函数无法完成的操作，但它也包含一些复杂的特性，目前我们可以暂时忽略这些特性。

要么未来能够真正“获胜”，因此返回`Result`是没有意义的。相反，`trpl::select`返回的是一种我们之前未曾见过的类型。`trpl::Either`这种类型与`Result`有些类似，因为它也有两种情况。不过，与`Result`不同的是，`Either`并没有内置成功或失败的概念。相反，它使用`Left`和`Right`来表示“一种或另一种情况”。

```rust
enum Either<A, B> {
    Left(A),
    Right(B),
}
```

``select``函数会根据第一个参数的结果返回``Left``，而如果两个参数都获胜，则根据第二个参数的结果返回``Right``。这与调用该函数时参数的顺序一致：第一个参数位于第二个参数的左侧。

我们还更新了`page_title`，使其返回与传入相同的URL。这样，如果首先返回的页面没有`<title>`，我们仍然可以打印出有意义的消息。有了这些信息之后，我们最后更新了`println!`的输出，以表明哪个URL先被返回，以及该URL对应的网页的`<title>`是做什么用的。

你现在已经构建了一个功能齐全的网络爬虫了！选择几个网址来运行这个命令行工具。你可能会发现，有些网站的加载速度始终比其他网站快，而在其他情况下，加载速度则因不同的运行环境而有所差异。更重要的是，你已经掌握了使用异步编程的基础知识，现在我们可以进一步了解如何利用异步编程来实现更多功能。

[impl-trait]: ch10-02-traits.html#traits-as-parameters  
[iterators-lazy]: ch13-02-iterators.html  
[thread-spawn]: ch16-01-threads.html#creating-a-new-thread-with-spawn  
[cli-args]: ch12-01-accepting-command-line-arguments.html

<!-- TODO: 如何将源链接版本映射到Rust的版本？ -->

[crate-source]: https://github.com/rust-lang/book/tree/main/packages/trpl  
[futures-crate]: https://crates.io/crates/futures  
[tokio]: https://tokio.rs