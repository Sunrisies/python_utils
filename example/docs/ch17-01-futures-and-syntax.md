## 未来与异步语法

Rust中异步编程的关键元素包括_futures_以及Rust的`async`和`await`关键字。

**未来值**是一种目前可能尚未准备好，但在未来的某个时间点会准备好的值。（这个概念在许多语言中都有体现，有时被称为**任务**或**承诺**。）Rust提供了一个名为``Future``的特质，作为实现这一概念的基石，使得不同的异步操作可以使用不同的数据结构来实现，但都具有相同的接口。在Rust中，未来值是一种实现了``Future``特质的类型。每个未来值都包含关于当前进展的信息，以及“准备好”的具体含义。

你可以将 `async` 关键字应用于代码块和函数中，以指定这些代码可以被中断和恢复。在异步代码块或异步函数中，你可以使用 `await` 关键字来 _等待一个未来值_（即等待它变得可用）。在异步代码块或函数中，任何需要等待未来值出现的位置，都是该代码块或函数可以暂停和恢复的潜在点。通过检查未来值来判断其值是否已经可用的过程，被称为 _轮询_。

其他一些语言，比如C#和JavaScript，也使用 `async` 和 `await` 作为异步编程的关键字。如果你熟悉这些语言，可能会注意到Rust在处理这种语法时存在一些显著的不同。这是有原因的，我们稍后会看到！

在编写异步Rust代码时，我们大多数时候都会使用 `async` 和 `await` 这两个关键字。Rust会利用 `Future` 特性将它们编译成等效的代码，就像它利用 `Iterator` 特性将 `for` 循环编译成等效代码一样。不过，由于Rust提供了 `Future` 特性，因此当你需要的时候，也可以为自己的数据类型实现这一特性。在本章中，我们将看到许多函数返回的类型都拥有自己的 `Future` 实现。我们将在章节末尾再次讨论这一特性的定义，并进一步了解其工作原理，但这些细节已经足以让我们继续前进了。

这些内容可能看起来有些抽象，那么让我们来编写第一个异步程序吧：一个小型的网页抓取工具。我们将从命令行传入两个URL，同时获取这两个URL的内容，然后返回第一个完成任务的那个的结果。这个例子会涉及到一些新的语法，不过不用担心——我们会边讲解边演示，让你能够轻松理解所有需要了解的内容。

## 我们的第一个异步程序

为了保持本章的重点在于学习异步编程，而不是处理生态系统的各个部分，我们创建了 `trpl`  crate（`trpl` 是 “Rust 编程语言” 的缩写）。它重新导出了你所需要的所有类型、特质和函数，这些资源主要来自 [`futures`][futures-crate]<!-- ignore --> 和 [`tokio`][tokio]<!-- ignore --> crate。 `futures` crate 是进行异步代码实验的官方平台，实际上 `Future` 特质也是在这里设计的。Tokio 是当今 Rust 中最广泛使用的异步运行时，尤其适用于 Web 应用程序。还有其他优秀的运行时，它们可能更适合你的需求。我们在底层使用 `tokio` crate 来实现 `trpl`，因为它经过充分测试且被广泛使用。

在某些情况下， `trpl` 还会重新命名或封装原始API，以便您专注于与本章相关的细节。如果您想了解该包的具体功能，我们建议您查看 [its source code][crate-source]。您将能够看到每个重新导出的包来自哪个包，并且我们留下了详细的注释来解释这些包的功能。

创建一个新的名为 `hello-async` 的二进制项目，并将 `trpl`  crate 作为依赖项添加到项目中。

```console
$ cargo new hello-async
$ cd hello-async
$ cargo add trpl
```

现在，我们可以使用 `trpl` 提供的各种元素来编写我们的第一个异步程序。我们将构建一个小型命令行工具，该工具可以获取两个网页，从每个网页中提取 `<title>` 元素，并输出最先完成整个过程的那个网页的标题。

### 定义 page_title 函数

让我们首先编写一个函数，该函数接受一个页面URL作为参数，对该页面发起请求，然后返回该页面中的 `<title>` 元素的文本（参见 Listing 17-1）。

**清单 17-1:** *src/main.rs* — 定义一个异步函数，用于从HTML页面中获取标题元素

```rust
use trpl::Html;

async fn page_title(url: &str) -> Option<String> {
    let response = trpl::get(url).await;
    let response_text = response.text().await;
    Html::parse(&response_text)
        .select_first("title")
        .map(|title| title.inner_html())
}

```

首先，我们定义一个名为 `page_title` 的函数，并使用 `async` 关键字对其进行标记。然后，我们使用 `trpl::get` 函数来获取传递的 URL 内容，并添加 `await` 关键字来等待响应。为了获取 `response` 的文本，我们调用其 `text` 方法，并再次使用 `await` 关键字来等待响应。这两个步骤都是异步的。对于 `get` 函数，我们必须等待服务器返回其响应的第一部分，这部分内容会包含 HTTP 头信息、Cookie 等，这些内容可以独立于响应主体进行传输。如果响应主体非常大，那么所有内容都传输完成可能需要一些时间。因为我们必须等待整个响应到达，所以 `text` 方法也是异步的。

我们必须显式地等待这两个未来函数，因为Rust中的未来函数具有“惰性”特性：除非你使用 `await` 关键字来请求它们执行，否则它们不会做任何事情。实际上，如果你不使用未来函数，Rust会显示一个编译器警告。这可能会让你想起第13章中关于迭代器的讨论。除非你直接调用迭代器的 `next` 方法，或者通过使用 `for` 循环或 `map` 这类在底层使用 `next` 的方法，否则迭代器也不会执行任何操作。同样，除非你显式地请求，否则未来函数也不会执行任何操作。这种惰性特性使得Rust能够避免在实际需要之前运行异步代码。

> 注意：这与我们在第16章的 [“Creating a New Thread with spawn”][thread-spawn]<!-- ignore --> 部分看到的行为不同。在那里，我们传递给另一个线程的闭包会立即开始运行。这也与许多其他语言处理异步编程的方式不同。不过，对于Rust来说，能够提供性能保证是非常重要的，就像对迭代器一样。

一旦我们得到了 `response_text`，我们就可以使用 `Html::parse` 将其解析为 `Html` 类型的实例。现在，我们不再使用原始字符串，而是有了一种可以用来处理 HTML 的数据类型，从而能够更灵活地处理数据。具体来说，我们可以使用 `select_first` 方法来找到给定 CSS 选择器的第一个实例。通过传递 `"title"` 字符串，我们可以获取文档中第一个 `<title>` 元素，如果有的话。由于可能没有任何匹配的元素， `select_first` 会返回一个 `Option<ElementRef>`。最后，我们可以使用 `Option::map` 方法来处理 `Option` 中的项目，如果该项目存在的话，否则就什么都不做。（我们也可以使用 `match` 表达式，但 `map` 更符合惯用法。）在提供给 `map` 的函数体中，我们对 `title` 调用 `inner_html` 以获取其内容，该内容是一个 `String`。最终，我们得到了一个 `Option<String>`。

请注意，Rust中的`await`这个关键字应该放在你正在等待的表达式之后，而不是之前。也就是说，它是一个后置关键字。如果你在其他语言中习惯使用`async`，那么这种用法可能会与你以往的习惯有所不同。但在Rust中，这种方式使得方法的链式调用更加易于使用。因此，我们可以将`page_title`的体部分成几个部分，将`trpl::get`和`text`函数调用串联在一起，并在它们之间插入`await`，如清单17-2所示。

**列表 17-2:** *src/main.rs* — 使用 `await` 关键字进行链式操作

```rust
    let response_text = trpl::get(url).await.text().await;

```

就这样，我们成功编写了第一个异步函数！在添加一些代码来调用它之前，让我们再详细了解一下我们所编写的内容以及它的含义。

当 Rust 遇到带有 `async` 关键字的 _block_ 时，它会将其编译成一个唯一、匿名的数据类型，该数据类型实现了 `Future` 特质。当 Rust 遇到带有 `async` 的 _function_ 时，它会将其编译成一个非异步函数，该函数的主体是一个异步块。异步函数的返回类型，就是编译器为该异步块所创建的匿名数据类型的类型。

因此，编写 `async fn` 相当于编写一个返回指定返回类型变量的函数。对于编译器来说，像 Listing 17-1 中的 `async fn page_title` 这样的函数定义，大致相当于这样定义的非异步函数：

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

让我们逐一分析这个转换后的版本的各个部分：

- 它使用了我们在第10章的 [“Traits as Parameters”][impl-trait]<!-- ignore --> 部分中讨论过的 `impl Trait` 语法。  
- 返回的值实现了 `Future` 特性，其关联类型为 `Output`。请注意， `Output` 的类型实际上是 `Option<String>`，这与 `async fn` 版本的 `page_title` 的原始返回类型相同。  
- 原始函数体内调用的所有代码都被包裹在一个 `async move` 块中。记住，块是一种表达式。整个块就是函数返回的表达式。  
- 这个异步块会返回一个类型为 `Option<String>` 的值，正如之前所描述的那样。该值的类型与返回类型中的 `Output` 相匹配。这与其他你见过的块类似。  
- 新的函数体是一个 `async move` 块，因为它使用了 `url` 参数。（我们会在本章后面进一步讨论 `async` 与 `async move` 的区别。）

现在我们可以在 `main` 中调用 `page_title`。

<!-- Old headings. Do not remove or links may break. -->

<a id ="determining-a-single-pages-title"></a>

### 使用运行时执行异步函数

首先，我们将获取单个页面的标题，如清单17-3所示。  
遗憾的是，这段代码目前还无法编译。

**清单 17-3:** *src/main.rs* — 使用用户提供的参数调用从 `main` 到 `page_title` 的函数

```rust,ignore,does_not_compile
async fn main() {
    let args: Vec<String> = std::env::args().collect();
    let url = &args[1];
    match page_title(url).await {
        Some(title) => println!("The title for {url} was {title}"),
        None => println!("{url} had no title"),
    }
}

```

我们在第12章的[“Accepting Command Line Arguments”][cli-args]<!-- ignore -->部分遵循了获取命令行参数的相同模式。然后，我们将URL参数传递给`page_title`，并等待结果。由于未来函数返回的值是一个`Option<String>`，我们使用`match`表达式来打印不同的消息，以区分页面是否具有`<title>`特性。

我们唯一可以使用 `await` 这个关键字的场合是在异步函数或代码块中，而且Rust不会允许我们将特殊的 `main` 函数标记为 `async`。

<!-- manual-regeneration
cd listings/ch17-async-await/listing-17-03
cargo build
copy just the compiler error
-->

```text
error[E0752]: `main` function is not allowed to be `async`
 --> src/main.rs:6:1
  |
6 | async fn main() {
  | ^^^^^^^^^^^^^^^ `main` function is not allowed to be `async`
```

之所以不能将 `main` 标记为 `async`，是因为异步代码需要一个 _运行时_：  
一个负责管理异步代码执行细节的 Rust 库。一个程序的 `main` 函数可以 _初始化_ 一个运行时，但它本身并不是运行时。（稍后我们会进一步了解为什么会这样。）每个执行异步代码的 Rust 程序都至少有一个地方需要设置一个能够执行这些未来操作的运行时。

大多数支持异步编程的语言都提供了相应的运行时环境，但Rust并不提供这样的环境。相反，有许多不同的异步运行时可供选择，每种运行时都针对不同的应用场景做出了不同的权衡。例如，一个具有多个CPU核心和大量内存的高性能Web服务器，与只有一个核心、内存较少且没有堆分配功能的微控制器有着截然不同的需求。提供这些运行时环境的库通常还会提供常见的异步功能版本，比如文件或网络I/O操作。

在本章的其余部分，我们将使用来自 `trpl` 库中的 `block_on` 函数。该函数接受一个未来值作为参数，并阻塞当前线程，直到该未来值执行完毕。在幕后，调用 `block_on` 会启动一个运行时环境，该环境用于执行传入的未来值（ `trpl` 库的 `block_on` 功能与其他运行时库中的 `block_on` 函数类似）。一旦未来值执行完毕，`block_on` 就会返回该未来值所产生的值。

我们可以将 `page_title` 返回的未来结果直接传递给 `block_on`，一旦该过程完成，我们就可以像在 Listing 17-3 中那样，对得到的 `Option<String>` 进行匹配。然而，对于本章中的大多数示例（以及现实世界中的大多数异步代码），我们通常会调用多个异步函数。因此，我们会传递一个 `async` 块，并显式地等待 `page_title` 调用的结果，如 Listing 17-4 所示。

<Listing number="17-4" caption="Awaiting an async block with `trpl::block_on`" file-name="src/main.rs">

<!-- should_panic,noplayground because mdbook test does not pass args -->

```rust,should_panic,noplayground
fn main() {
    let args: Vec<String> = std::env::args().collect();

    trpl::block_on(async {
        let url = &args[1];
        match page_title(url).await {
            Some(title) => println!("The title for {url} was {title}"),
            None => println!("{url} had no title"),
        }
    })
}

```

</Listing>

当我们运行这段代码时，我们得到了最初预期的行为。

<!-- manual-regeneration
cd listings/ch17-async-await/listing-17-04
cargo build # skip all the build noise
cargo run -- "https://www.rust-lang.org"
# copy the output here
-->

```console
$ cargo run -- "https://www.rust-lang.org"
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.05s
     Running `target/debug/async_await 'https://www.rust-lang.org'`
The title for https://www.rust-lang.org was
            Rust Programming Language
```

呼——我们终于有一些可以运行的异步代码了！但在我们将代码添加到让两个站点相互竞争之前，让我们先简要了解一下未来是如何工作的。

每一个`_await点_——也就是说，每一个代码使用`await`这个关键字的地点——都代表着控制权被返回给运行时的地方。为了让这一机制正常工作，Rust需要跟踪与异步代码块相关的状态，这样运行时就可以开始执行其他任务，然后在准备好之后再次尝试推进第一个异步任务。这实际上是一个看不见的状态机，就像你在每个await点处定义了一个枚举来保存当前状态一样。

```rust
enum PageTitleFuture<'a> {
    Initial { url: &'a str },
    GetAwaitPoint { url: &'a str },
    TextAwaitPoint { response: trpl::Response },
}

```

手动编写代码来实现状态之间的切换是非常繁琐且容易出错的，尤其是当后来需要为代码添加更多功能以及更多状态时。幸运的是，Rust编译器会自动创建和管理异步代码中的状态机数据结构。关于数据结构的数据借用和所有权规则仍然适用，而且编译器还会自动处理这些规则，并提供有用的错误信息。我们会在本章的后面部分详细讨论其中的一些内容。

最终，必须有一些东西来执行这个状态机，而那个东西就是运行时。这就是为什么在探讨运行时时，可能会遇到“执行器”这个概念：执行器是运行时中负责执行异步代码的部分。

现在你可以理解为什么编译器在 Listing 17-3 中阻止我们将 `main` 本身定义为异步函数了。如果 `main` 是一个异步函数，那么就需要其他机制来管理 `main` 所返回的结果的状态机，但 `main` 才是程序的起点！相反，我们在 `main` 中调用 `trpl::block_on` 函数来设置运行环境，并持续执行 `async` 块中定义的未来操作，直到其完成。

> 注意：一些运行时提供了宏，因此你可以编写异步函数。这些宏将 `async fn main() { ... }` 重写为普通的 `fn
> main`，其实现方式与 Listing 17-4 中手动编写的方式相同：调用一个函数，该函数会像 `trpl::block_on` 那样完成对未来的处理。

现在，让我们把这些部分整合起来，看看如何编写并发代码。

<!-- Old headings. Do not remove or links may break. -->

<a id="racing-our-two-urls-against-each-other"></a>

### 同时比较两个URL的异同

在 Listing 17-5 中，我们调用了 `page_title`，并从命令行传递了两个不同的 URL，然后通过选择哪个函数先完成来对比它们的执行速度。

<Listing number="17-5" caption="Calling `page_title` for two URLs to see which returns first" file-name="src/main.rs">

<!-- should_panic,noplayground because mdbook does not pass args -->

```rust,should_panic,noplayground
use trpl::{Either, Html};

fn main() {
    let args: Vec<String> = std::env::args().collect();

    trpl::block_on(async {
        let title_fut_1 = page_title(&args[1]);
        let title_fut_2 = page_title(&args<!-- ignore -->);

        let (url, maybe_title) =
            match trpl::select(title_fut_1, title_fut_2).await {
                Either::Left(left) => left,
                Either::Right(right) => right,
            };

        println!("{url} returned first");
        match maybe_title {
            Some(title) => println!("Its page title was: '{title}'"),
            None => println!("It had no title."),
        }
    })
}

async fn page_title(url: &str) -> (&str, Option<String>) {
    let response_text = trpl::get(url).await.text().await;
    let title = Html::parse(&response_text)
        .select_first("title")
        .map(|title| title.inner_html());
    (url, title)
}

```

</Listing>

我们首先对每个用户提供的 URL 调用 `page_title` 函数。我们将得到的未来值分别保存为 `title_fut_1` 和 `title_fut_2`。请注意，这些未来值目前还不会执行任何操作，因为未来值是惰性计算的，我们还没有等待它们完成。之后，我们将这些未来值传递给 `trpl::select` 函数，该函数会返回一个值，指示哪个未来值先完成。

> 注意：在底层实现中， `trpl::select` 是基于更通用的 `select` 函数构建的。该 `select` 函数定义在 `futures`  crate 中。而 `futures` crate 的 `select` 函数能够完成 `trpl::select` 函数无法完成的许多功能。不过， `futures` crate 的 `select` 函数也存在一些额外的复杂性，这些复杂性我们可以暂时忽略。

要么“未来”能够真正“获胜”，因此返回`Result`是没有意义的。相反，`trpl::select`返回的是一种我们之前未曾见过的类型，即`trpl::Either`。`Either`这种类型与`Result`有些类似，因为它也有两种情况。不过，与`Result`不同的是，`Either`并没有内置成功或失败的概念。相反，它使用`Left`和`Right`来表示“两者之一”。

```rust
enum Either<A, B> {
    Left(A),
    Right(B),
}
```

函数 `select` 会在第一个参数获胜时返回 `Left`，并且如果第二个参数获胜，则返回第二个参数的输出 `Right`。这与调用函数时参数的顺序一致：第一个参数位于第二个参数的左侧。

我们还更新了 `page_title`，使其返回相同的传入 URL。这样，如果首先返回的页面没有可以解析的 `<title>`，我们仍然可以打印出有意义的消息。有了这些信息之后，我们最后更新了 `println!` 的输出，以表明哪个 URL 先被返回，以及该 URL 对应的网页的 `<title>` 是什么。

你现在已经构建了一个功能齐全的网页抓取工具！选择几个URL并运行这个命令行工具。你可能会发现，有些网站的抓取速度始终比其他网站快，而另一些网站的速度则每次运行时都会有所不同。更重要的是，你已经掌握了使用未来主义的基本技巧，现在我们可以进一步了解如何利用异步编程了。

[impl-trait]: ch10-02-traits.html#traits-as-parameters
[iterators-lazy]: ch13-02-iterators.html
[thread-spawn]: ch16-01-threads.html#creating-a-new-thread-with-spawn
[cli-args]: ch12-01-accepting-command-line-arguments.html

<!-- TODO: map source link version to version of Rust? -->

[crate-source]: https://github.com/rust-lang/book/tree/main/packages/trpl
[futures-crate]: https://crates.io/crates/futures
[tokio]: https://tokio.rs
