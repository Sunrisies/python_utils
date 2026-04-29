<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="深入了解异步处理的特性">深入了解异步处理的特性</a>

## 深入了解异步相关的特性

在整章内容中，我们以不同的方式使用了`Future`、`Stream`和`StreamExt`这些特质。不过，到目前为止，我们并没有深入讨论它们的工作原理或它们之间的相互作用细节，这对于日常Rust编程来说已经足够了。不过，有时候你会遇到需要了解这些特质更多细节的情况，同时还需要了解`Pin`类型和`Unpin`特质。在这一部分中，我们将提供足够的介绍来帮助解决这些问题，而更深入的探讨则留到其他相关文档中。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="未来"></a>

### `Future` 特质

让我们先仔细看看 ``Future`` 这个特质是如何工作的。以下是 Rust 对它的定义：

```rust
use std::pin::Pin;
use std::task::{Context, Poll};

pub trait Future {
    type Output;

    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Self::Output>;
}
```

那个特性定义包含了一组新的类型，还有一些我们之前从未见过的语法。因此，让我们逐步解析这个定义。

首先，`Future`的关联类型`Output`决定了未来的具体实现。这类似于`Iterator` trait的关联类型`Item`。其次，`Future`拥有`poll`方法，该方法需要一个特殊的`Pin`引用作为其`self`参数，以及一个对`Context`类型的可变引用，并且该方法返回一个`Poll<Self::Output>`。我们稍后会进一步讨论`Pin`和`Context`。目前，让我们先关注该方法返回的内容，即`Poll`类型。

```rust
pub enum Poll<T> {
    Ready(T),
    Pending,
}
```

这个`Poll`类型与`Option`类似。它有一个具有特定值的变体，即`Ready(T)`，还有一个没有该值的变体，即`Pending`。而`Poll`的含义则与`Option`完全不同！`Pending`变体表示未来还有工作要做，因此调用者需要稍后再进行确认。而`Ready`变体则表示`Future`已经完成了其任务，现在`T`的值就可以使用了。

注意：很少需要直接调用 ``poll``，但如果确实需要的话，请记住，对于大多数未来操作，调用者不应在future返回`Ready`之后再次调用`poll`。许多未来操作在准备好后会因再次被查询而引发panic。那些可以再次被查询的未来操作会在其文档中明确说明这一点。这与`Iterator::next`的行为类似。

当你看到使用`await`的代码时，Rust会在后台将其编译成调用`poll`的代码。如果你再看一下Listing 17-4，在那里我们在某个URL解析完成后打印出页面标题，Rust会将其编译成类似这样的代码（尽管不完全相同）：

```rust,ignore
match page_title(url).poll() {
    Ready(page_title) => match page_title {
        Some(title) => println!("The title for {url} was {title}"),
        None => println!("{url} had no title"),
    }
    Pending => {
        // But what goes here?
    }
}
```

当未来仍然处于`Pending`状态时，我们应该怎么做呢？我们需要一种方法，不断尝试，直到未来最终准备好为止。换句话说，我们需要一个循环来不断重复这个过程。

```rust,ignore
let mut page_title_fut = page_title(url);
loop {
    match page_title_fut.poll() {
        Ready(value) => match page_title {
            Some(title) => println!("The title for {url} was {title}"),
            None => println!("{url} had no title"),
        }
        Pending => {
            // continue
        }
    }
}
```

如果Rust将其编译成这样的代码，那么所有的`await`都会产生阻塞——这与我们期望的结果完全相反！相反，Rust确保循环能够将控制权交给某个可以暂停当前任务、去处理其他任务，然后再重新检查这个任务的组件。正如我们所看到的，那个组件就是一个异步运行时，而这种调度和协调工作正是它的主要功能之一。

在[“使用消息传递在两个任务之间发送数据”][message-passing]这一节中，我们描述了等待`rx.recv`的过程。`recv`调用会返回一个future，而等待这个future则意味着持续监听它的状态变化。我们注意到，当通道关闭时，运行时会暂停future，直到它准备好为止，这可以通过`Some(message)`或`None`来实现。通过更深入地了解`Future`特性，特别是`Future::poll`，我们可以理解其工作原理。当`Poll::Pending`返回时，运行时就知道future尚未准备好。相反地，当`poll`返回`Poll::Ready(Some(message))`或`Poll::Ready(None)`时，运行时就会知道future已经准备好，并继续执行后续操作。

关于运行时如何实现这一功能的具体细节超出了本书的范围，但关键在于理解未来值的基本机制：运行时会逐一“轮询”它所负责的每个未来值，并在未来值尚未准备好时将其重新置于睡眠状态。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="pinning-and-the-pin-and-unpin-traits"></a>
<a id="the-pin-and-unpin-traits"></a>

### `Pin`类型与`Unpin`特质

在清单17-13中，我们使用`trpl::join!`宏来等待三个未来值。然而，通常我们会有一个集合，比如一个向量，其中包含了一些在未来运行时才会得知的未来值。让我们将清单17-13中的代码替换为清单17-23中的代码，这样就把这三个未来值放入了一个向量中，并且调用了`trpl::join_all`函数。不过，目前这个代码还无法编译。

<Listing number="17-23" caption="等待集合中的未来操作" file-name="src/main.rs">

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch17-async-await/listing-17-23/src/main.rs:here}}
```

</ Listing>

我们将每个未来任务放在 ``Box`` 中，从而将它们转换为 _特质对象_，就像我们在第12章的“从 ``run`` 返回错误”部分所做的那样。（我们将在第18章详细讨论特质对象。）使用特质对象可以让我们将这些由这些类型产生的匿名未来任务视为同一种类型，因为它们都实现了 ``Future`` 特质。

这可能会让人感到惊讶。毕竟，所有的异步块都不会返回任何东西，因此每个异步块都会产生一个`Future<Output = ()>`。不过，请记住`Future`是一个特质，而且编译器会为每个异步块生成一个唯一的枚举类型，即使它们的输出类型是相同的。就像你不能将两个不同的手写结构体放在同一个`Vec`中一样，你也不能混合使用编译器生成的枚举类型。

然后，我们将这些未来函数的集合传递给`trpl::join_all`函数，并等待结果。然而，这无法编译；以下是错误信息的相关部分。

<!-- 手动重新生成
cd listings/ch17-async-await/listing-17-23
cargo build
仅复制最后一个 `error` 代码块到 errors 目录中
-->

```text
error[E0277]: `dyn Future<Output = ()>` cannot be unpinned
  --> src/main.rs:48:33
   |
48 |         trpl::join_all(futures).await;
   |                                 ^^^^^ the trait `Unpin` is not implemented for `dyn Future<Output = ()>`
   |
   = note: consider using the `pin!` macro
           consider using `Box::pin` if you need to access the pinned value outside of the current scope
   = note: required for `Box<dyn Future<Output = ()>>` to implement `Future`
note: required by a bound in `futures_util::future::join_all::JoinAll`
  --> file:///home/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/futures-util-0.3.30/src/future/join_all.rs:29:8
   |
27 | pub struct JoinAll<F>
   |            ------- required by a bound in this struct
28 | where
29 |     F: Future,
   |        ^^^^^^ required by this bound in `JoinAll`
```

这条错误信息提示我们，应该使用 ``pin!`` 宏来固定这些值。这意味着需要将这些值放在 ``Pin`` 类型中，这样就能确保这些值在内存中不会被移动。错误信息指出，需要进行固定操作是因为 ``dyn Future<Output = ()>`` 需要实现 ``Unpin`` 特性，而目前它还没有实现这一特性。

`trpl::join_all`函数返回一个名为`JoinAll`的结构体。该结构体是一个泛型类型，其约束条件要求`F`必须实现`Future`特性。通过`await`直接等待一个未来，会隐式地挂起该未来。因此，我们不必在需要等待未来的所有地方都使用`pin!`。

不过，我们并不是直接等待未来的某个事件。相反，我们通过将一系列未来时态传递给`join_all`函数，来创建一个新的未来时态，即JoinAll。`join_all`函数的签名要求，集合中的各项类型都必须实现`Future`特质；而`Box<T>`只有在它所包裹的`T`实现了`Unpin`特质时，才会实现`Future`特质。

这确实有很多需要理解的内容！为了真正掌握它，让我们进一步深入了解`Future` trait的工作原理，特别是关于固定功能的部分。再看一下`Future` trait的定义：

```rust
use std::pin::Pin;
use std::task::{Context, Poll};

pub trait Future {
    type Output;

    // Required method
    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Self::Output>;
}
```

`cx`参数及其`Context`类型，是运行时如何判断何时需要检查某个给定的未来值的关键所在，同时还能保持惰性执行。不过，这一机制的具体实现细节超出了本章的讨论范围，通常只有在编写自定义的`Future`实现时才需要关注这一点。我们接下来将重点讨论`self`的类型，因为这是我们第一次见到一个方法，其中`self`带有类型注解。`self`的类型注解与其他函数参数的类型注解类似，但有两个关键的区别：

它告诉Rust，`self`这个类型必须是什么，才能调用该方法。  
它不能只是任意的类型。它仅限于实现该方法的类型、对该类型的引用或智能指针，或者是一个包装了该类型引用的`Pin`。

我们将在[第18章][ch-18]中详细了解这种语法。目前，我们只需要知道，如果我们想要查询一个未来值，以判断它是`Pending`还是`Ready(Output)`，那么我们需要一个包含`Pin`的可变引用来指向该类型。

`Pin`是一种用于指针类类型的包装器，比如`&`、`&mut`、`Box`和`Rc`。  
从技术上讲，`Pin`可以处理那些实现了`Deref`或`DerefMut`特性的类型，但实际上这等同于只能使用引用和智能指针来处理这些类型。) `Pin`本身并不是一个真正的指针，它也没有像`Rc`和`Arc`那样通过引用计数来维护自身的行为；它纯粹是编译器用来对指针使用进行约束的工具而已。

回想一下，`await`是通过调用`poll`来实现的，这解释了我们之前看到的错误信息。不过，那是在`Unpin`的上下文中发生的，而不是在`Pin`的上下文中。那么，`Pin`究竟与`Unpin`有什么关系呢？另外，为什么`Future`需要`self`处于`Pin`的类型中才能调用`poll`呢？

请记住，在本章前面的内容中提到过，一系列在异步代码中的`await`操作会被编译成一个状态机。编译器会确保该状态机遵循Rust中所有关于安全性的规则，包括借用和所有权方面的规则。为了实现这一点，Rust会分析从一个`await`点到下一个`await`点或者异步代码块末尾之间需要哪些数据。然后，Rust会在编译后的状态机中创建相应的变体。每个变体都会获得访问该部分代码中使用的数据的权限，这可以通过获取该数据的所有权，或者获得对该数据的可变或不可变引用来实现。

到目前为止，一切正常：如果我们对某个异步代码块中的所有权或引用处理不当，借用检查器会给出提示。但是，当我们想要移动与那个代码块对应的未来对象时——比如将其移动到`Vec`中，然后再传递给`join_all`——情况就变得复杂了。

当我们移动一个未来值时——无论是将其放入数据结构中作为``join_all``的迭代器，还是从函数中返回它——这实际上意味着我们改变了Rust为我们创建的状态机。与Rust中的大多数其他类型不同，Rust为异步块创建的未来值可能会在任何给定变体的字段中包含对自身的引用，如图17-4中的简化示意图所示。

<图>

<img alt="一个单栏三行的表格，代表一个未来，名为 fut1。该表格的前两行分别包含数据值 0 和 1，第三行有一个箭头指向第二行，表示未来内部的引用关系。" src="img/trpl17-04.svg" class="center" />

<figcaption>图17-4：一种自引用数据类型</figcaption>

</figure>

不过，默认情况下，任何包含对自身引用的对象在移动时都是不安全的，因为引用始终指向它们所引用的实际内存地址（参见图17-5）。如果你移动了数据结构本身，那么那些内部引用仍然会指向旧的位置。然而，那个内存位置现在已经无效了。一方面，当你对数据结构进行更改时，该位置的值不会得到更新。另一方面，更重要的是，计算机现在可以重新使用那块内存用于其他目的！之后你可能会读到完全无关的数据。

<图>

<img alt="两张表格，分别展示了两个未来值 fut1 和 fut2。每个未来值都有一列三行，表示将一个未来值从 fut1 移动到 fut2 后的结果。其中，fut1以灰色显示，每个索引位置都有一个问号，表示未知的内存区域。fut2的第一行和第二行分别有 0 和 1，并且第三行指向 fut1 的第二行，这表示该指针引用了未来值在移动之前所在的内存位置。" src="img/trpl17-05.svg" class="center" />

<figcaption>图17-5：移动自引用数据类型时的不安全结果</figcaption>

</figure>

理论上，Rust编译器可以在对象被移动时尝试更新所有对其的引用。但这可能会带来大量的性能开销，尤其是当需要更新大量引用时。如果我们能够确保所涉及的数据结构在内存中不会移动，那么我们就无需更新任何引用了。这正是Rust的借用检查器的作用：在安全代码中，它可以防止你移动有任何带有活动引用的对象。

`Pin`在此基础上进一步提供了我们所需的精确保证。当我们通过将指向该值的指针包装在`Pin`中来实现对值的“固定”时，该值就无法再移动了。因此，如果你拥有`Pin<Box<SomeType>>`，那么你实际上固定的是`SomeType`的值，而不是`Box`指针。图17-6展示了这一过程。

<图>

<img alt="三个盒子并排排列。第一个标有‘Pin’，第二个为‘b1’，第三个为‘pinned’。在‘pinned’内部有一个标有‘fut’的表格，该表格包含单列；它代表一个未来，其中每个数据结构的组成部分都有一个对应的单元格。其第一个单元格的值为‘0’，第二个单元格中有一个箭头指向第四个也是最后一个单元格，该单元格的值为‘1’。第三个单元格中有虚线和省略号，表示数据结构可能还有其他部分。总体而言，‘fut’表格代表的是一个自引用的未来。箭头从标有‘Pin’的盒子出发，穿过标有‘b1’的盒子，最终在‘pinned’盒内的‘fut’表格处终止。” src="img/trpl17-06.svg" class="center" />

<figcaption>图17-6：固定一个指向自引用未来类型的`Box`</figcaption>

</figure>

实际上，`Box`指针仍然可以自由移动。记住：我们关注的是确保最终被引用的数据保持原位。如果指针在移动，但它所指向的数据仍然位于同一位置，就像图17-7所示，那么就不会有潜在的问题。（作为一个独立的练习，可以查阅相关类型的文档，以及`std::pin`模块，尝试了解如何使用`Pin`来包装`Box`。）关键在于，自引用类型本身不能移动，因为它仍然处于固定状态。

<图>

<img alt="四个盒子以三个粗略的列排列，与之前的图表相同，只是第二列有所变化。现在第二列中有两个盒子，分别标记为‘b1’和‘b2’。‘b1’被标记成灰色，箭头从‘Pin’指向‘b2’，而不是‘b1’，这表明指针已从‘b1’移动到‘b2’，但‘pinned’中的数据并未移动。” src="img/trpl17-07.svg" class="center" />

<figcaption>图17-7：移动一个指向自引用未来类型的`Box`</figcaption>

</figure>

不过，大多数类型在移动时都是完全安全的，即使它们位于`Pin`指针之后。我们只需要考虑在元素具有内部引用时才需要固定它们。像数字和布尔值这样的基本值是非常安全的，因为它们显然没有任何内部引用。在Rust中，大多数你通常使用的类型也是安全的。例如，你可以移动`Vec`，而不用担心什么。根据我们目前所看到的，如果你有一个`Pin<Vec<String>>`，那么你只能通过`Pin`提供的安全但有限制的API来进行操作，尽管如果没有其他引用，`Vec<String>`总是可以安全移动的。我们需要一种方式来告诉编译器，在这种情况下移动元素是安全的——这就是`Unpin`发挥作用的地方。

`Unpin` 是一个标记特质，类似于我们在第16章中看到的`Send`和`Sync`特质。因此，它本身并没有任何功能。标记特质的存在只是为了告诉编译器，在特定上下文中使用实现了某个特质的类型是安全的。而`Unpin`则向编译器表明，某个类型并不需要保证所涉及的数值可以安全地被移动。

<!--
  在下一个块中，内联的 ``<code>`` 的作用是让内部的 ``<em>`` 能够正常显示，
   这与 NoStarch的设计风格一致，并且在这里强调这是与普通类型不同的东西。
>
-->

就像 `Send` 和 `Sync` 一样，编译器会自动为所有能够证明其安全的类型实现 `Unpin`。另一个特殊情况，类似于 `Send` 和 `Sync`，就是对于那些类型来说 `Unpin` 并未被实现。这种情况的表示方法是 <code>impl!Unpin for <em>SomeType</em></code>，其中 <code><em>SomeType</em></code> 是指那些在 `Pin` 中使用指针时必须保持安全性的类型名称。

换句话说，关于`Pin`与`Unpin`之间的关系，有两点需要注意。首先，`Unpin`是“正常”的情况，而`!Unpin`则是特殊情况。其次，当一个类型实现了`Unpin`或`!Unpin`时，只有在使用指向该类型的固定指针时才会起作用，比如使用<code>Pin<&mut<em>SomeType</em>>></code>这样的语法。

具体来说，想象一个`String`：它有一个长度，以及构成它的Unicode字符。我们可以将`String`包裹在`Pin`中，如图17-8所示。然而，`String`会自动实现`Unpin`的功能，Rust中的大多数其他类型也是如此。

<图>

<img alt="左侧有一个标记为“Pin”的框，右侧有一个从“Pin”指向“String”的箭头。在“String”框中包含了数据5usize，表示字符串的长度；同时，字母“h”、“e”、“l”、“l”和“o”代表了存储在当前String实例中的字符串“hello”的各个字符。一个虚线矩形围绕着“String”框及其标签，但不包括“Pin”框。"></src="img/trpl17-08.svg" class="center" />

<figcaption>图17-8：固定`String`；虚线表示`String`实现了`Unpin`特质，因此不会被固定</figcaption>

</figure>

因此，我们可以执行那些如果由`String`来实现`!Unpin`的话，就会被视为非法的行为。例如，可以在内存中的完全相同位置替换一个字符串，就像在图17-9中那样。这样做并不违反`Pin`的契约，因为`String`没有任何内部引用，使得对其进行移动操作不会造成安全隐患。这正是为什么它选择实现`Unpin`而不是`!Unpin`的原因。

<图>

<img alt="与前一个示例相同的“hello”字符串数据，现在被标记为“s1”并且颜色变为灰色。前一个示例中的“Pin”框现在指向另一个String实例，该实例被标记为“s2”，它是有效的，长度为7usize，包含字符串“goodbye”的字符。s2被一个虚线矩形包围，因为它也实现了Unpin特质。” src="img/trpl17-09.svg" class="center" />

<figcaption>图17-9：在内存中将`String`替换为完全不同的`String`</figcaption>

</figure>

现在我们已经了解到了关于 `join_all` 调用的错误信息。最初，我们试图将异步块产生的未来值移动到 `Vec<Box<dyn Future<Output = ()>>>` 中，但正如我们所看到的，这些未来值可能包含内部引用，因此它们不会自动实现 `Unpin` 的功能。一旦我们将这些未来值固定下来，我们就可以将生成的 `Pin` 类型传递给 `Vec`，并且可以确信这些未来值中的底层数据不会被移动。清单 17-24 展示了如何通过调用 `pin!` 宏来修复代码，其中三个未来值都被定义在该宏中，同时调整了 trait 对象类型。

<列表编号="17-24" 标题="固定未来值以将其移动到向量中">

```rust
{{#rustdoc_include ../listings/ch17-async-await/listing-17-24/src/main.rs:here}}
```

</ Listing>

这个示例现在可以编译并运行了。我们可以在运行时向向量中添加或删除未来值，并将它们全部连接在一起。

`Pin`和`Unpin`主要应用于构建底层库，或者当你在构建运行时系统时，而不是用于日常Rust代码编写中。不过，当你在错误信息中看到这些特性时，你就更清楚如何修复你的代码了！

> 注意：将 `Pin` 与 `Unpin` 结合使用，可以安全地实现一系列复杂的类型。在Rust中，由于这些类型具有自引用特性，因此很难实现。需要 `Pin` 的类型在当今的异步Rust代码中最为常见，不过偶尔也会在其他上下文中出现。

> `Pin` 和 `Unpin` 的具体工作原理以及它们必须遵守的规则，都在`std::pin`的API文档中有详细说明。如果你有兴趣了解更多，那是一个很好的起点。

> 如果你想更详细地了解底层的工作原理，可以参考[_Asynchronous Programming in Rust_][async-book]中的第[2][底层原理]章和第[4][锁定机制]章。

### `Stream` 特质

现在您已经更深入地了解了`Future`、`Pin`和`Unpin`这些特性，我们可以把注意力转向`Stream`这个特性。正如您在章节中早先学到的那样，流与异步迭代器类似。不过，与`Iterator`和`Future`不同，`Stream`在标准库中目前还没有定义。但是，`futures`这个库中有一个非常常见的定义，它被整个生态系统所使用。

让我们先回顾一下 `Iterator` 和 `Future` 这两个特性的定义，然后再看看 `Stream` 特性如何将它们结合起来。从 `Iterator` 开始，我们得到了序列的概念：它的 `next` 方法提供了一个 `Option<Self::Item>`。而从 `Future` 开始，我们得到了随时间逐渐准备好的概念：它的 `poll` 方法提供了一个 `Poll<Self::Output>`。为了表示一系列随着时间逐渐准备好的项目，我们定义了一个 `Stream` 特性，它将这些功能整合在一起。

```rust
use std::pin::Pin;
use std::task::{Context, Poll};

trait Stream {
    type Item;

    fn poll_next(
        self: Pin<&mut Self>,
        cx: &mut Context<'_>
    ) -> Poll<Option<Self::Item>>;
}
```

`Stream` 这个特质定义了一个关联类型，名为 `Item`，用于由该流产生的项目的类型。这与 `Iterator` 类似，在 `Iterator` 中，可能存在零个到多个项目；而与 `Future` 不同，在 `Future` 中，总是只有一个 `Output`，即使它是单位类型 `()`。

`Stream`还定义了一个用于获取这些项的方法。我们将其命名为`poll_next`，以便明确它采用与`Future::poll`相同的方式进行轮询，并且以与`Iterator::next`相同的方式生成一系列项。其返回类型结合了`Poll`和`Option`的功能。外部类型是`Poll`，因为需要像处理未来值一样检查其是否准备好。内部类型则是`Option`，因为它需要像迭代器那样指示是否有更多消息需要处理。

与这个定义非常相似的内容很可能会成为 Rust 标准库的一部分。与此同时，它也是大多数运行时工具集的一部分，因此你可以放心使用它。接下来我们介绍的所有内容通常都是适用的！

在我们在[“Streams: Futures in Sequence”][streams]这个章节中看到的例子中，虽然我们没有使用`poll_next`或`Stream`，而是使用了`next`和`StreamExt`。当然，我们也可以直接通过`poll_next` API来编写自己的`Stream`状态机，或者直接使用futures的`poll`方法。不过，使用`await`会更方便一些，而且`StreamExt`特质提供了`next`方法，因此我们可以直接利用这个方法来实现我们的需求。

```rust
{{#rustdoc_include ../listings/ch17-async-await/no-listing-stream-ext/src/lib.rs:here}}
```

<!--
待办事项：如果tokio等库更新了MSRV规范，并且开始在_traits中使用异步函数，请更新此内容。
由于目前_traits中尚未引入异步函数，因此暂时没有这一规范。
-->

> 注意：我们在本章前面使用的定义与这个版本略有不同，因为该定义支持那些尚未支持在特质中使用异步函数的Rust版本。因此，其实现方式如下：

> ```rust,ignore
> fn next(&mut self) -> Next<'_, Self> where Self: Unpin;
> ```

> 那个`Next`类型实际上是一个实现了`Future`的`struct`类型。通过这种方式，我们可以使用`Next<'_, Self>`来命名对`self`的引用生命周期，从而让`await`能够使用这种方法。

`StreamExt`这个特质也是所有与流相关的有趣方法的所在地。对于每一个实现了`Stream`的类型，`StreamExt`都会自动被实现。不过，这些特质是分开定义的，这样社区就可以在不影响基础特质的情况下，不断改进便捷的应用程序接口。

在 `trpl` 项目中使用的 `StreamExt` 版本中，该特质不仅定义了 `next` 方法，还提供了 `next` 的默认实现，从而能够正确处理调用 `Stream::poll_next` 的细节。这意味着，即使你需要自己编写流式数据类型的实现，也只需要实现 `Stream`；之后，任何使用你的数据类型的人都可以自动地使用 `StreamExt` 及其方法。

这就是我们关于这些特性中较低级别细节的全部内容了。最后，让我们来探讨一下未来元素（包括流）、任务以及线程是如何协同工作的！

[消息传递]: ch17-02-concurrency-with-async.md#使用消息传递在两个任务之间传输数据
[章节-18]: ch18-00-oop.html
[异步书籍]: https://rust-lang.github.io/async-book/
[底层原理]: https://rust-lang.github.io/async-book/02_execution/01_chapter.html
[固定操作]: https://rust-lang.github.io/async-book/04_pinning/01_chapter.html
[第一个异步示例]: ch17-01-futures-and-syntax.html#我们的第一个异步程序
[任意数量的异步对象]: ch17-03-more-futures.html#处理任意数量的异步对象
[流]: ch17-04-streams.html