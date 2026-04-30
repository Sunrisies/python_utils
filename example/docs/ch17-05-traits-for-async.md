<!-- Old headings. Do not remove or links may break. -->

<a id="digging-into-the-traits-for-async"></a>

## 深入了解异步相关的特性

在整章内容中，我们多次使用了 `Future`、 `Stream` 和 `StreamExt` 这些特性。不过，到目前为止，我们并没有深入讨论它们的工作原理或它们之间的相互作用细节，这对于日常 Rust 编程来说已经足够了。不过，有时候你可能会遇到需要了解这些特性更多细节的情况，同时还需要了解 `Pin` 类型和 `Unpin` 特性。在这一部分中，我们将简要介绍这些细节，以帮助那些需要深入了解的情况，而更深入的内容则可以在其他文档中找到。

<!-- Old headings. Do not remove or links may break. -->

<a id="future"></a>

### 特性 `Future`

让我们先仔细看看 `Future` 这个特质是如何工作的。以下是 Rust 的定义方式：

```rust
use std::pin::Pin;
use std::task::{Context, Poll};

pub trait Future {
    type Output;

    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Self::Output>;
}
```

那个特性定义包含了一组新的类型，还有一些我们之前从未见过的语法。因此，让我们逐步解析这个定义。

首先， `Future` 的关联类型 `Output` 决定了未来的结果。这类似于 `Iterator` 特质下的 `Item` 关联类型。其次， `Future` 拥有一个 `poll` 方法，该方法需要一个特殊的 `Pin` 引用作为其 `self` 参数，以及一个对 `Context` 类型的可变引用，并且该方法返回一个 `Poll<Self::Output>`。我们稍后会进一步讨论 `Pin` 和 `Context`。目前，让我们先关注该方法返回的内容，即 `Poll` 类型。

```rust
pub enum Poll<T> {
    Ready(T),
    Pending,
}
```

这种 `Poll` 类型与 `Option` 类似。它有一个具有特定值的变体，即 `Ready(T)`，还有一个没有该值的变体，即 `Pending`。不过， `Poll` 的含义与 `Option` 完全不同！ `Pending` 变体表示未来还有工作要做，因此调用者需要稍后再次检查。而 `Ready` 变体则表示 `Future` 已经完成了其工作，现在 `T` 的值就可以使用了。

> 注意：很少需要直接调用 `poll`，但如果你确实需要这样做，请记住，对于大多数未来值，调用者不应在future返回 `Ready` 之后再次调用 `poll`。许多未来值在再次被查询时会引发异常。那些可以安全再次被查询的未来值会在其文档中明确说明这一点。这与 `Iterator::next` 的行为类似。

当你看到使用 `await` 的代码时，Rust 会在后台将其编译成调用 `poll` 的代码。如果你再看一下 Listing 17-4，在那里我们在一个 URL 解析完成后，会打印出对应的页面标题。Rust 会将其编译成类似这样的代码（虽然不完全相同）：

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

当未来仍然处于「`Pending`」状态时，我们应该怎么做呢？我们需要一种方法，可以一次又一次地尝试，直到未来最终准备好为止。换句话说，我们需要一个循环机制。

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

如果Rust将其编译成这样的代码，那么每一个 `await` 都会造成阻塞——这与我们想要的完全相反！相反，Rust确保循环能够将控制权交给某个可以暂停当前任务、去处理其他任务，然后再重新检查这个任务的处理器。正如我们所看到的，那个处理器就是一个异步运行时，而这种调度和协调工作正是它的主要功能之一。

在 [“Sending Data Between Two Tasks Using Message
Passing”][message-passing]<!-- ignore --> 这一部分中，我们描述了等待`rx.recv`的过程。`recv`调用会返回一个未来值，而等待这个未来值时，程序会对其进行查询。我们注意到，当通道关闭时，运行时会暂停这个未来值，直到它准备好为止，这可以通过`Some(message)`或`None`来实现。通过更深入地了解`Future`特性，特别是`Future::poll`，我们可以理解其工作原理。当`Poll::Pending`返回时，运行时就知道未来值尚未准备好。相反，当`poll`返回`Poll::Ready(Some(message))`或`Poll::Ready(None)`时，运行时就知道未来值已经准备好，并继续处理后续操作。

关于运行时如何实现这一功能的具体细节超出了本书的范围，但关键在于理解 futures 的基本机制：运行时会逐一查询它所负责的每个 future，当某个 future 尚未准备好时，就会将其重新置于睡眠状态。

<!-- Old headings. Do not remove or links may break. -->

<a id="pinning-and-the-pin-and-unpin-traits"></a>
<a id="the-pin-and-unpin-traits"></a>

### `Pin` 类型和 `Unpin` 特性

在清单17-13中，我们使用 `trpl::join!` 宏来等待三个未来值。然而，通常我们会有一个集合，比如一个向量，其中包含了一些在运行时才可知的未来值。让我们将清单17-13中的代码替换为清单17-23中的代码，这样就把这三个未来值放入了一个向量中，并调用了 `trpl::join_all` 函数。不过，目前这个代码还无法编译。

<Listing number="17-23" caption="Awaiting futures in a collection"  file-name="src/main.rs">

```rust,ignore,does_not_compile
        let tx_fut = async move {
            // --snip--
        };

        let futures: Vec<Box<dyn Future<Output = ()>>> =
            vec![Box::new(tx1_fut), Box::new(rx_fut), Box::new(tx_fut)];

        trpl::join_all(futures).await;

```

</Listing>

我们将每个未来时态都封装在一个 `Box` 中，从而将其转化为 _特质对象_，就像我们在第12章的“从 `run` 返回错误”部分所做的那样。（我们将在第18章中详细讨论特质对象。）使用特质对象可以让我们将这些类型产生的匿名未来时态视为同一种类型，因为所有这些未来时态都实现了 `Future` 特质。

这可能会让人感到惊讶。毕竟，所有的异步块都不会返回任何值，因此每个异步块都会产生一个 `Future<Output = ()>`。不过，请记住 `Future` 是一个特质，而且编译器会为每个异步块生成唯一的枚举类型，即使它们的输出类型相同。就像你不能将两个不同的结构体放入 `Vec` 中一样，你也不能混合使用编译器生成的枚举类型。

然后，我们将这些未来函数的集合传递给 `trpl::join_all` 函数，并等待结果。然而，这无法编译；以下是错误信息的相关部分。

<!-- manual-regeneration
cd listings/ch17-async-await/listing-17-23
cargo build
copy *only* the final `error` block from the errors
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

这条错误信息提示我们，应该使用 `pin!` 宏来固定这些值。这意味着需要将这些值放在 `Pin` 类型中，这样就能确保这些值在内存中不会被移动。错误信息指出，需要固定这些值是因为 `dyn Future<Output = ()>` 需要实现 `Unpin` 特性，而目前它还没有实现这一特性。

函数 `trpl::join_all` 返回一个名为 `JoinAll` 的结构体。该结构体是一个泛型结构，其类型 `F` 被约束为必须实现 `Future` 特性。该函数还会隐式地等待一个带有 `await` 的将来时态。因此，我们不需要在需要等待将来时态的地方到处使用 `pin!`。

不过，我们并不是直接等待未来的某个时间点。相反，我们通过将一系列未来时态对象传递给 `join_all` 函数，来构造一个新的未来时态对象 JoinAll。对于 `join_all` 函数的签名要求，集合中的各个项目的类型都必须实现 `Future` 特质；而 `Box<T>` 特质则只有在它所包裹的未来时态对象实现了 `Unpin` 特质的情况下才会被实现。

这确实有很多需要理解的！为了真正理解它，让我们进一步探讨一下 `Future` trait 的实际工作原理，特别是关于固定功能的部分。再看一下 `Future` trait 的定义：

```rust
use std::pin::Pin;
use std::task::{Context, Poll};

pub trait Future {
    type Output;

    // Required method
    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Self::Output>;
}
```

参数 `cx` 及其类型 `Context`，是运行时如何在实际中判断何时需要检查某个未来的关键所在，同时还能保持惰性。再次强调，其具体实现细节超出了本章的讨论范围，通常只有在编写自定义 `Future` 实现时才需要关注这一点。我们接下来将重点讨论 `self` 的类型，因为这是我们第一次看到 `self` 具有类型注释的方法。 `self` 的类型注释与其他函数参数的类型注释类似，但有两个关键区别：

它告诉Rust，为了使该方法能够被调用，类型必须满足 `self` 的条件。  
这个类型不能随便选择，而是仅限于实现该方法的类型本身，或者是对该类型的引用或智能指针，或者是一个包装了该类型引用的 `Pin`。

我们将在 [Chapter 18][ch-18]<!-- ignore --> 中进一步了解这种语法。目前，我们只需要知道，如果我们想要查询一个未来值，以检查它是否为 `Pending` 或 `Ready(Output)`，我们需要一个 `Pin` 包裹的可变引用来指向该类型。

`Pin`是一种用于指针类型（如 `&`、`&mut`、`Box` 和 `Rc`）的封装工具。  
从技术上讲，`Pin`可以处理那些实现了 `Deref` 或 `DerefMut` 特性的类型，但实际上这等同于仅使用引用和智能指针来处理这些类型。`Pin`本身并不是一种指针，也没有像 `Rc` 和 `Arc` 那样通过引用计数来维护自身状态；它纯粹是编译器用来强制约束指针使用的工具而已。

回想一下， `await` 是通过调用 `poll` 来实现的，这正好解释了我们之前看到的错误信息。不过，这里使用的是 `Unpin`，而不是 `Pin`。那么， `Pin` 究竟与 `Unpin` 有什么关系呢？另外，为什么 `Future` 需要 `self` 处于 `Pin` 的类型中，才能调用 `poll` 呢？

请记住，在本章前面的内容中提到过，一系列在异步代码中的`await`操作会被编译成一个状态机。编译器会确保该状态机遵循Rust中所有关于安全性的规则，包括借用和所有权方面的规则。为了实现这一点，Rust会分析在从一个`await`点到下一个`await`点或者异步代码块的末尾之间需要哪些数据。然后，Rust会在编译后的状态机中创建相应的状态。每个状态都会获得访问该部分代码中使用的数据的权限，这可以通过获取该数据的所有权，或者获得对该数据的可变或不可变引用来实现。

到目前为止，一切正常：如果我们对某个异步块中的所有权或引用处理不当，借用检查器会给出提示。但是，当我们想要移动与那个块相对应的未来时——比如将其移动到 `Vec` 中，然后再传递给 `join_all`——情况就变得复杂了。

当我们移动一个未来值时——无论是将其放入数据结构中作为迭代器使用，还是将其从函数中返回——这实际上意味着移动 Rust 为我们创建的状态机。与 Rust 中的大多数其他类型不同，Rust 为异步块创建的未来值可能会在任何给定变体的字段中包含对自身的引用，如图 17-4 中的简化示意图所示。

<figure>

<img alt="A single-column, three-row table representing a future, fut1, which has data values 0 and 1 in the first two rows and an arrow pointing from the third row back to the second row, representing an internal reference within the future." src="img/trpl17-04.svg" class="center" />

<!-- Old headings. Do not remove or links may break. -->⊃图17-4：一种自引用数据类型<!-- Old headings. Do not remove or links may break. -->⊃

</figure>

不过，默认情况下，任何包含对自身引用的对象都是不可移动的，因为引用始终指向它们所引用的实际内存地址（参见图17-5）。如果你移动了数据结构本身，那么这些内部引用仍然会指向旧的位置。然而，那个内存地址现在已经无效了。一方面，当你对数据结构进行更改时，该地址的值不会得到更新。另一方面，更重要的是，计算机现在可以重新使用那块内存用于其他目的！之后你可能会读到完全无关的数据。

<figure>

<img alt="Two tables, depicting two futures, fut1 and fut2, each of which has one column and three rows, representing the result of having moved a future out of fut1 into fut2. The first, fut1, is grayed out, with a question mark in each index, representing unknown memory. The second, fut2, has 0 and 1 in the first and second rows and an arrow pointing from its third row back to the second row of fut1, representing a pointer that is referencing the old location in memory of the future before it was moved." src="img/trpl17-05.svg" class="center" />

<!-- Old headings. Do not remove or links may break. -->⊃图17-5：移动自引用数据类型时的不安全结果<!-- Old headings. Do not remove or links may break. -->⊃

</figure>

理论上，Rust编译器可以在对象被移动时尝试更新所有对其的引用。但这可能会带来大量的性能开销，尤其是当需要更新大量的引用时。如果我们能够确保所涉及的数据结构在内存中不会移动，那么我们就无需更新任何引用了。这正是Rust的借用检查器的作用：在安全的代码中，它可以防止你移动有任何带有活动引用的对象。

`Pin` 在此基础上，为我们提供了所需的精确保障。当我们通过将指向某个值的指针包装在 `Pin` 中，来“固定”该值时，该指针就无法再移动了。因此，如果你拥有 `Pin<Box<SomeType>>`，那么你实际上固定的是 `SomeType` 的值，而不是 `Box` 的指针。图17-6展示了这一过程。

<figure>

<img alt="Three boxes laid out side by side. The first is labeled “Pin”, the second “b1”, and the third “pinned”. Within “pinned” is a table labeled “fut”, with a single column; it represents a future with cells for each part of the data structure. Its first cell has the value “0”, its second cell has an arrow coming out of it and pointing to the fourth and final cell, which has the value “1” in it, and the third cell has dashed lines and an ellipsis to indicate there may be other parts to the data structure. All together, the “fut” table represents a future which is self-referential. An arrow leaves the box labeled “Pin”, goes through the box labeled “b1” and terminates inside the “pinned” box at the “fut” table." src="img/trpl17-06.svg" class="center" />

图17-6：固定一个指向自引用未来类型的 `Box`，该未来类型指向一个 </figcaption>

</figure>

实际上，`Box`指针仍然可以自由移动。记住：我们关注的是确保最终被引用的数据保持不动。如果指针移动了，但它所指向的数据仍然位于同一个位置，就像图17-7所示，就不会出现任何问题。（作为一个独立的练习，可以查阅相关类型的文档以及`std::pin`模块，试着思考如何用`Pin`包裹`Box`来实现这一点。）关键在于，自引用类型本身不能移动，因为它仍然被固定住了。

<figure>

<img alt="Four boxes laid out in three rough columns, identical to the previous diagram with a change to the second column. Now there are two boxes in the second column, labeled “b1” and “b2”, “b1” is grayed out, and the arrow from “Pin” goes through “b2” instead of “b1”, indicating that the pointer has moved from “b1” to “b2”, but the data in “pinned” has not moved." src="img/trpl17-07.svg" class="center" />

图17-7：移动一个指向自引用未来类型的`Box`，该类型指向的是</figcaption>

</figure>

不过，大多数类型在移动时都是完全安全的，即使它们位于 `Pin` 指针之后。我们只有在遇到内部引用时才会需要考虑固定这些类型。像数字和布尔值这样的基本值是非常安全的，因为它们显然没有任何内部引用。在 Rust 中，大多数你常用的类型也是安全的。例如，你可以自由移动 `Vec`，无需担心任何问题。根据我们目前所见的情况，如果你有一个 `Pin<Vec<String>>`，那么你只能通过 `Pin` 提供的安全但有限制的 API 来进行操作，尽管如果没有其他引用存在的话， `Vec<String>` 总是可以安全移动的。我们需要一种方式来告诉编译器，在这种情况下移动这些类型是完全可以的——这就是 `Unpin` 发挥作用的地方。

`Unpin` 是一种标记特质，类似于我们在第16章中看到的 `Send` 和 `Sync` 特质。因此，它本身并没有任何功能。标记特质的存在只是为了告诉编译器，在特定上下文中使用实现了某个特质的类型是安全的。而 `Unpin` 则告诉编译器，某个类型**不需要**提供任何关于所讨论的值是否可以安全移动的保证。

<!--
  The inline `<code>` in the next block is to allow the inline `<em>` inside it,
  matching what NoStarch does style-wise, and emphasizing within the text here
  that it is something distinct from a normal type.
-->

就像 `Send` 和 `Sync` 一样，编译器会自动为所有能够证明其安全的类型实现 `Unpin`。另一个特殊情况，类似于 `Send` 和 `Sync`，就是对于某些类型，无法实现 `Unpin`。这种情况的表示方法是 <code>impl !Unpin，用于 <em>SomeType</em></code>。而 <code><em>SomeType</em></code> 则指的是那种在 `Pin` 中使用指向该类型的指针时，必须确保安全的类型。

换句话说，关于 `Pin` 和 `Unpin` 之间的关系，有两点需要注意。首先， `Unpin` 是“正常”的情况，而 `!Unpin` 则是特殊情况。其次，当使用指向该类型的固定指针时，比如 <code>Pin<&mut
<em>SomeType</em>></code>，那么类型是否实现了 `Unpin` 或 `!Unpin` _仅_ 这一点的表现就变得非常重要了。

具体来说，想象一下 `String`：它有一个长度，以及构成它的 Unicode 字符。我们可以像图 17-8 中所示，将 `String` 包裹在 `Pin` 中。然而， `String` 会自动实现 `Unpin` 的功能，Rust 中的大多数其他类型也是如此。

<figure>

<img alt="A box labeled “Pin” on the left with an arrow going from it to a box labeled “String” on the right. The “String” box contains the data 5usize, representing the length of the string, and the letters “h”, “e”, “l”, “l”, and “o” representing the characters of the string “hello” stored in this String instance. A dotted rectangle surrounds the “String” box and its label, but not the “Pin” box." src="img/trpl17-08.svg" class="center" />

图17-8：固定 `String`；虚线表示 `String` 实现了 `Unpin` 特性，因此不会被固定</figcaption>

</figure>

因此，我们可以执行那些如果由 `String` 实现的话就会被视为非法的操作。例如，可以在内存中完全相同的位置替换两个字符串，就像在图17-9中那样。这样做并不违反 `Pin` 的契约，因为 `String` 没有内部引用，因此无法被随意移动。这正是它采用 `Unpin` 而不是 `!Unpin` 的原因。

<figure>

<img alt="The same “hello” string data from the previous example, now labeled “s1” and grayed out. The “Pin” box from the previous example now points to a different String instance, one that is labeled “s2”, is valid, has a length of 7usize, and contains the characters of the string “goodbye”. s2 is surrounded by a dotted rectangle because it, too, implements the Unpin trait." src="img/trpl17-09.svg" class="center" />

<!-- Old headings. Do not remove or links may break. -->⊃图17-9：在内存中将 `String` 替换为完全不同的 `String`</figcaption>

</figure>

现在我们已经了解到了关于 Listing 17-23 中那个 `join_all` 调用的错误。我们最初试图将异步块产生的未来值移动到 `Vec<Box<dyn Future<Output = ()>>>` 中，但正如我们所见，这些未来值可能包含内部引用，因此它们不会自动实现 `Unpin` 的功能。一旦我们将这些未来值固定下来，我们就可以将得到的 `Pin` 类型传递给 `Vec`，并且可以确信这些未来值中的底层数据不会被移动。Listing 17-24 展示了如何通过调用 `pin!` 宏来修复代码，该宏定义了三个未来值，并调整了 trait 对象类型。

<Listing number="17-24" caption="Pinning the futures to enable moving them into the vector">

```rust
use std::pin::{Pin, pin};

// --snip--

        let tx1_fut = pin!(async move {
            // --snip--
        });

        let rx_fut = pin!(async {
            // --snip--
        });

        let tx_fut = pin!(async move {
            // --snip--
        });

        let futures: Vec<Pin<&mut dyn Future<Output = ()>>> =
            vec![tx1_fut, rx_fut, tx_fut];

```

</Listing>

这个示例现在可以编译并运行了。我们可以在运行时向向量中添加或删除未来元素，然后将它们全部连接在一起。

`Pin` 和 `Unpin` 主要用于构建底层库，或者当你在构建运行时本身时，而不是用于日常 Rust 代码编写。不过，当你在错误信息中看到这些特性时，你就更清楚如何修复你的代码了！

> 注意：这种 `Pin` 和 `Unpin` 的组合使得在 Rust 中安全地实现一系列复杂的类型成为可能。这些类型本身具有自引用特性，因此很难实现。需要 `Pin` 的类型在如今的异步 Rust 中最为常见，不过偶尔也会在其他上下文中出现。

> `Pin` 和 `Unpin` 的具体工作原理以及它们必须遵守的规则，都在 `std::pin` 的 API 文档中有详细说明。如果你有兴趣了解更多，那将是很好的起点。

> 如果你想要更详细地了解这些机制的工作原理，可以参考 [2][under-the-hood]<!-- ignore --> 和 [4][pinning]<!-- ignore --> 章节，以及 [_Asynchronous Programming in Rust_][async-book] 的相关内容。

### 特性 `Stream`

既然您已经更深入地了解了 `Future`、 `Pin` 和 `Unpin` 这些特质，那么我们可以把注意力转向 `Stream` 这个特质。正如您在本章前面所学到的，流与异步迭代器类似。不过，与 `Iterator` 和 `Future` 不同，截至本文撰写时， `Stream` 在标准库中并没有明确定义。但是， `futures` 这个包中有一个非常常见的定义，它被整个生态系统所采用。

在探讨如何将一个 `Stream` 特质与 `Iterator` 特质进行合并之前，我们先来回顾一下 `Iterator` 和 `Future` 特质的定义。从 `Iterator` 特质出发，我们得到了序列的概念：其 `next` 方法提供了一个 `Option<Self::Item>`。而从 `Future` 特质出发，我们得到了随时间逐渐准备好的概念：其 `poll` 方法提供了一个 `Poll<Self::Output>`。为了表示一系列随时间逐渐准备好的项目，我们定义了一个 `Stream` 特质，它将这些特性整合在一起。

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

``Stream`` 这个特征定义了一个名为 ``Item`` 的相关类型，该类型用于描述由该流产生的项目的类型。这与 ``Iterator`` 类似，后者可能包含零个到多个项目；而 ``Future`` 则不同，因为 ``Future`` 总是包含一个单一的 ``Output``，即使该类型是单位类型 ``()``。

`Stream`还定义了一个用于获取这些项的方法。我们将其称为`poll_next`，以便明确它采用与`Future::poll`相同的方式进行轮询，并且以与`Iterator::next`相同的方式生成一系列项。它的返回类型结合了`Poll`和`Option`的特点。外部类型是`Poll`，因为需要像检查未来值一样来确认其是否准备好。内部类型则是`Option`，因为它需要像迭代器那样来指示是否还有更多消息需要处理。

与这个定义非常相似的内容很可能会成为 Rust 标准库的一部分。与此同时，它也是大多数运行时工具集的一部分，因此你可以放心使用它。接下来我们介绍的内容通常都是适用的！

在我们在 [“Streams: Futures in Sequence”][streams]<!--
ignore --> 这一节中看到的例子中，我们并没有使用 `poll_next` 或 `Stream`，而是使用了 `next` 和 `StreamExt`。当然，我们也可以直接通过手写自己的 `Stream` 状态机来使用 `poll_next` API，或者直接使用 futures 的 `poll` 方法。不过，使用 `await` 会更方便，而且 `StreamExt` 特质提供了 `next` 方法，这样我们就可以直接使用它了。

```rust
trait StreamExt: Stream {
    async fn next(&mut self) -> Option<Self::Item>
    where
        Self: Unpin;

    // other methods...
}

```

<!--
TODO: update this if/when tokio/etc. update their MSRV and switch to using async functions
in traits, since the lack thereof is the reason they do not yet have this.
-->

> 注意：我们在本章前面使用的定义与现在的定义略有不同，因为当时的版本还不支持在特质中使用异步函数。因此，当时的定义是这样的：

> ```rust,ignore
> fn next(&mut self) -> Next<'_, Self> where Self: Unpin;
> ```

而 `Next` 这种类型实际上实现了 `struct`，并且允许我们使用 `Future` 来命名对 `self` 的引用生命周期，从而让 `await` 能够使用这种方法。

`StreamExt` 这个特质也是所有与流相关的有趣方法的所在地。 `StreamExt` 会自动为每一个实现了 `Stream` 的类型而存在，但这些特质是分开定义的，目的是让社区能够在不影响基础特质的情况下，不断改进便捷的应用程序接口。

在 `trpl`  crate 中使用的 `StreamExt` 版本中，该 trait 不仅定义了 `next` 方法，还提供了 `next` 的默认实现，该实现能够正确处理调用 `Stream::poll_next` 的细节。这意味着，即使你需要自己编写流式数据类型的实现，也只需要实现 `Stream`，那么使用你定义的数据类型的任何人都可以自动地使用 `StreamExt` 及其方法。

这就是我们关于这些特性中较低级别细节的全部内容了。最后，让我们来探讨一下未来（包括流）、任务以及线程是如何协同工作的！

[message-passing]: ch17-02-concurrency-with-async.md#sending-data-between-two-tasks-using-message-passing
[ch-18]: ch18-00-oop.html
[async-book]: https://rust-lang.github.io/async-book/
[under-the-hood]: https://rust-lang.github.io/async-book/02_execution/01_chapter.html
[pinning]: https://rust-lang.github.io/async-book/04_pinning/01_chapter.html
[first-async]: ch17-01-futures-and-syntax.html#our-first-async-program
[any-number-futures]: ch17-03-more-futures.html#working-with-any-number-of-futures
[streams]: ch17-04-streams.html
