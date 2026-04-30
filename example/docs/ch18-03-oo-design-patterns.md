## 实现面向对象的设计模式

_状态模式_是一种面向对象的设计模式。该模式的核心思想是我们定义了一个值可以拥有的状态集合。这些状态由一组_状态对象_来表示，值的的行为会根据其状态而变化。我们将通过一个博客文章结构的例子来详细说明这一模式，该结构包含一个字段来保存其状态，这个状态可以是“草稿”、“评审中”或“已发布”中的任何一种状态对象。

这些状态对象具有共同的功能：在Rust中，我们通常使用结构体和技术特性，而不是对象和继承机制。每个状态对象都负责自己的行为，并负责决定何时切换到另一个状态。持有状态对象的值对状态的不同行为或何时在状态之间转换一无所知。

使用状态模式的优势在于，当程序的业务需求发生变化时，我们不需要修改持有状态的代码或使用该值的代码。我们只需要更新其中一个状态对象内部的代码，以改变其规则，或者可能增加更多的状态对象。

首先，我们将以更传统的面向对象方式来实现状态模式。然后，我们将在 Rust 中使用一种更自然的方法。让我们逐步使用状态模式来实现一篇博客文章的工作流程。

最终的功能将如下所示：

1. 一篇博客文章最初是一个空白的草稿。
2. 当草稿完成后，会请求对文章进行评审。
3. 当文章获得批准后，它就会被发布。
4. 只有已发布的博客文章才会将内容返回到打印状态，这样那些未获批准的文章就不会意外地被发布。

对帖子进行的任何其他修改都不会产生效果。例如，如果我们试图在请求审核之前就批准一篇草稿博客文章，那么该文章应该仍然是一个未发布的草稿。

<!-- Old headings. Do not remove or links may break. -->

<a id="a-traditional-object-oriented-attempt"></a>

### 尝试传统的面向对象风格

解决同一个问题，有多种不同的代码结构方式，每种方式都有不同的权衡。本节的实现采用了传统的面向对象风格，这种风格在 Rust 中也是可以实现的，但并没有充分利用 Rust 的一些优势。稍后，我们将展示另一种解决方案，该方案仍然使用面向对象的设计模式，但其结构可能不太适合那些有面向对象编程经验的程序员。我们将对比这两种解决方案，以体验以不同于其他语言编写 Rust 代码所带来的权衡。

清单18-11展示了这一工作流程的编码形式：这是我们将在名为 `blog` 的库 crate 中实现的 API 的一个使用示例。目前该代码还无法编译，因为我们还没有实现 `blog` 这个 crate。

**列表 18-11:** *src/main.rs* — 演示了我们希望我们的 `blog`  crate 所具有的功能的代码

```rust,ignore,does_not_compile
use blog::Post;

// ANCHOR: here
fn main() {
    let mut post = Post::new();

    post.add_text("I ate a salad for lunch today");
    assert_eq!("", post.content());
    // ANCHOR_END: here

    post.request_review();
    assert_eq!("", post.content());

    post.approve();
    assert_eq!("I ate a salad for lunch today", post.content());
    // ANCHOR: here
}
// ANCHOR_END: here

```

我们希望允许用户使用 `Post::new` 创建一个新的草稿博客文章。我们还希望允许向博客文章中添加文本。如果我们试图在文章获得批准之前立即获取其内容，那么我们应该不会得到任何文本，因为文章仍然只是草稿状态。我们在代码中添加了 `assert_eq!` 用于演示目的。一个很好的单元测试方法就是断言草稿博客文章在 `content` 方法中返回空字符串，但我们不会为这个例子编写测试。

接下来，我们希望启用对帖子的审核请求，并且希望在等待审核期间，`content` 返回空字符串。当帖子获得批准时，它应该被发布，这意味着当调用 `content` 时，将会返回帖子的文本。

请注意，我们从这个包中唯一交互的类型是 `Post` 类型。这个类型将使用状态模式，并持有一个值，该值将代表帖子可能处于的三种状态之一——草稿、审核中或已发布。从一种状态切换到另一种状态将在 `Post` 类型内部进行内部管理。这些状态会根据库的用户对 `Post` 实例调用的方法而发生变化，但它们不必直接管理这些状态的变化。此外，用户不会在状态方面犯错，例如在未审核的情况下就发布帖子。

<!-- Old headings. Do not remove or links may break. -->

<a id="defining-post-and-creating-a-new-instance-in-the-draft-state"></a>

#### 定义 `Post` 并创建一个新的实例

让我们开始实现这个库吧！我们知道我们需要一个公开的结构体，用来存储一些内容，因此我们将从定义这个结构体开始，并附带一个公开的函数，用来创建一个结构体实例，如清单18-12所示。我们还将创建一个私有的特质，用来定义所有状态对象必须具备的行为。

那么， `Post` 将在一个名为 `state` 的私有字段中保存 `Box<dyn State>` 的 trait 对象，该对象将用于保存状态对象。稍后你会明白为什么 `Option<T>` 是必需的。

**清单 18-12:** *src/lib.rs* — 定义了一个 `Post` 结构体，以及一个 `new` 函数，该函数创建一个新的 `Post` 实例、一个 `State` 特质，以及一个 `Draft` 结构体。

```rust,noplayground
pub struct Post {
    state: Option<Box<dyn State>>,
    content: String,
}

impl Post {
    pub fn new() -> Post {
        Post {
            state: Some(Box::new(Draft {})),
            content: String::new(),
        }
    }
}

trait State {}

struct Draft {}

impl State for Draft {}

```

The `State` trait定义了不同帖子状态共有的行为。状态对象分别为 `Draft`、 `PendingReview` 和 `Published`，它们都将实现 `State` trait。目前，这个trait还没有任何方法，我们将首先定义 `Draft` 状态，因为这就是我们希望帖子开始所处的状态。

当我们创建一个新的 `Post` 时，我们会将其 `state` 字段设置为一个 `Some` 值，该值会保持 `Box` 状态。这个 `Box` 指向一个新的 `Draft` 结构实例。这样，每当我们创建一个新的 `Post` 实例时，它都会以草稿状态开始。由于 `Post` 的 `state` 字段是私有的，因此无法以其他状态创建 `Post`！在 `Post::new` 函数中，我们将 `content` 字段设置为一个新的、空的 `String`。

#### 存储帖子内容文本

我们在 Listing 18-11 中看到，我们希望能够调用一个名为 `add_text` 的方法，并传递一个 `&str` 参数，该参数将被作为博客帖子的文本内容。我们通过定义一个方法来实现这一功能，而不是将 `content` 字段暴露为 `pub`。这样，之后我们可以实现一个方法来控制 `content` 字段的数据如何被读取。`add_text` 方法非常简单，因此让我们在 Listing 18-13 中添加该方法的实现到 `impl
Post` 块中。

**清单 18-13:** *src/lib.rs* — 实现 `add_text` 方法以在帖子的 `content` 中添加文本

```rust,noplayground
impl Post {
    // --snip--
    pub fn add_text(&mut self, text: &str) {
        self.content.push_str(text);
    }
}

```

该方法接受一个可变的引用到 `self`，因为我们正在修改在 `add_text` 上调用的 `Post` 实例。然后我们在 `String` 中调用 `push_str`，并将 `text` 参数传递给 add 函数，以添加到保存的 `content` 中。这种行为并不依赖于帖子的状态，因此它不属于状态模式的一部分。 `add_text` 方法根本不与 `state` 字段交互，但它是我们想要支持的行为的一部分。

<!-- Old headings. Do not remove or links may break. -->

<a id="ensuring-the-content-of-a-draft-post-is-empty"></a>

#### 确保草稿帖子内容为空

即使我们调用了 `add_text` 并向我们的帖子添加了一些内容，我们仍然希望 `content` 方法返回一个空字符串切片，因为帖子仍处于草稿状态，正如清单 18-11 中的第一个 `assert_eq!` 所示。目前，让我们用最简单的方式来实现 `content` 方法：始终返回一个空字符串切片。一旦我们能够改变帖子的状态以便发布，我们就会修改这一点。到目前为止，帖子只能处于草稿状态，因此帖子内容应该始终为空。清单 18-14 展示了这个占位符实现。

**清单 18-14:** *src/lib.rs* — 为 `Post` 方法添加一个占位符实现，该方法的 `content` 参数始终返回一个空字符串切片。

```rust,noplayground
impl Post {
    // --snip--
    pub fn content(&self) -> &str {
        ""
    }
}

```

通过添加这个 `content` 方法，列表 18-11 中从第一个 `assert_eq!` 开始的所有内容都能按照预期正常工作。

<!-- Old headings. Do not remove or links may break. -->

<a id="requesting-a-review-of-the-post-changes-its-state"></a>
<a id="requesting-a-review-changes-the-posts-state"></a>

#### 请求审核，这将改变帖子的状态

接下来，我们需要添加功能来请求对帖子的审核，这将使帖子的状态从 `Draft` 变为 `PendingReview`。列表 18-15 展示了这一代码。

**清单 18-15:** *src/lib.rs* — 在 `Post`  trait 上实现 `request_review` 方法和 `State` 方法

```rust,noplayground
impl Post {
    // --snip--
    pub fn request_review(&mut self) {
        if let Some(s) = self.state.take() {
            self.state = Some(s.request_review())
        }
    }
}

trait State {
    fn request_review(self: Box<Self>) -> Box<dyn State>;
}

struct Draft {}

impl State for Draft {
    fn request_review(self: Box<Self>) -> Box<dyn State> {
        Box::new(PendingReview {})
    }
}

struct PendingReview {}

impl State for PendingReview {
    fn request_review(self: Box<Self>) -> Box<dyn State> {
        self
    }
}

```

我们为 `Post` 提供了一个名为 `request_review` 的公共方法，该方法接受一个可变的引用到 `self`。然后，我们在 `Post` 的当前状态下调用一个内部的 `request_review` 方法，这个第二个 `request_review` 方法消耗当前的状态并返回一个新状态。

我们将 `State` 特性添加了一个 `request_review` 方法；所有实现了该特性的类型现在都需要实现 `request_review` 方法。  
请注意，该方法的第一参数不再是 `self`、 `&self` 或 `&mut self`，而是 `self: Box<Self>`。这种语法意味着，只有当该类型被赋值给 `Box` 时，该方法才有效。这种语法会接管 `Box<Self>`，从而使旧的状态失效，使得 `Post` 的状态值能够转换为新的状态。

为了消耗旧的状态， `request_review` 方法需要获取该状态的值。这就是 `state` 字段中的 `Post` 发挥作用的地方：我们调用 `take` 方法来从 `state` 字段中提取 `Some` 值，并保留 `None` 在原位置。因为 Rust 不允许在结构体中存在未初始化的字段。这样，我们就可以将 `state` 值从 `Post` 中移出，而不是借用它。然后，我们将 post 的 `Option`0⊃ 值设置为这个操作的结果。

我们需要暂时将 `state` 设置为 `None`，而不是直接使用像 `self.state = self.state.request_review();` 这样的代码来获取 `state` 的值。这样做可以确保在我们将其转换为新状态之后， `Post` 无法使用旧的 `state` 值。

方法 `request_review` 在 `Draft` 中返回一个新的、被装箱的 `PendingReview` 结构实例，该实例表示帖子等待审核时的状态。 `PendingReview` 结构实现了 `request_review` 方法，但并没有进行任何转换。相反，它返回自身，因为当我们请求对已经处于 `PendingReview` 状态的帖子进行审核时，该帖子应该保持 `PendingReview` 状态。

现在我们可以开始看到状态模式的优势了：无论 `state` 的值为何，`Post` 上的 ⊃`request_review` 方法都是相同的。每个状态都负责自己的规则。

我们将保持 `Post` 中的 `content` 方法不变，该方法返回一个空字符串。现在，我们可以在 `PendingReview` 状态和 `Draft` 状态中都有一个 `Post`，但我们希望在 `PendingReview` 状态中也能实现同样的行为。现在，列表 18-11 可以正常工作，直到第二次调用 `assert_eq!`！

<!-- Old headings. Do not remove or links may break. -->

<a id="adding-the-approve-method-that-changes-the-behavior-of-content"></a>
<a id="adding-approve-to-change-the-behavior-of-content"></a>

#### 添加 `approve` 以改变 `content` 的行为

The `approve`方法将与 `request_review`方法类似：它会将 `state`设置为当前状态在获得批准时应该具有的值，如清单18-16所示。

**清单 18-16:** *src/lib.rs* — 在 `Post` 上实现 `approve` 方法，以及在 `State`  trait 上的实现

```rust,noplayground
impl Post {
    // --snip--
    pub fn approve(&mut self) {
        if let Some(s) = self.state.take() {
            self.state = Some(s.approve())
        }
    }
}

trait State {
    fn request_review(self: Box<Self>) -> Box<dyn State>;
    fn approve(self: Box<Self>) -> Box<dyn State>;
}

struct Draft {}

impl State for Draft {
    // --snip--
    fn approve(self: Box<Self>) -> Box<dyn State> {
        self
    }
}

struct PendingReview {}

impl State for PendingReview {
    // --snip--
    fn approve(self: Box<Self>) -> Box<dyn State> {
        Box::new(Published {})
    }
}

struct Published {}

impl State for Published {
    fn request_review(self: Box<Self>) -> Box<dyn State> {
        self
    }

    fn approve(self: Box<Self>) -> Box<dyn State> {
        self
    }
}

```

我们将 `State` 特性中的 `approve` 方法添加进来，并创建了一个新的结构体来实现 `State`，以及 `Published` 状态。

类似于 `request_review` 在 `PendingReview` 中的工作方式，如果我们调用 `approve` 方法在 `Draft` 上，它将没有任何效果，因为 `approve` 会返回 `self`。当我们调用 `approve` 在 `PendingReview` 上时，它会返回一个新的、封装的 `Published` 结构实例。`Published` 结构实现了 `State` 特征，对于 `request_review` 方法和 `approve` 方法，它都会返回自身，因为在这些情况下，状态应该保持在 `Published` 状态中。

现在我们需要更新 `Post` 上的 `content` 方法。我们希望 `content` 返回的值依赖于 `Post` 的当前状态，因此我们将让 `Post` 委托执行在其 `state` 上定义的 `content` 方法，如清单 18-17 所示。

**清单 18-17:** *src/lib.rs* — 将 `Post` 上的 `content` 方法更新为委托给 `State` 上的 `content` 方法

```rust,ignore,does_not_compile
impl Post {
    // --snip--
    pub fn content(&self) -> &str {
        self.state.as_ref().unwrap().content(self)
    }
    // --snip--
}

```

因为我们的目标是将所有这些规则保留在实现了 `State` 的结构中，所以我们会在 `state` 中的值上调用一个 `content` 方法，并将 `self` 作为该方法的参数。然后，我们返回在 `state` 值上使用 `content` 方法所得到的返回值。

我们调用 `Option` 上的 `as_ref` 方法，是因为我们希望获得对 `Option` 中值的引用，而不是对该值的所有权。因为 `state` 是一个 `Option<Box<dyn State>>`，当我们调用 `as_ref` 时，会返回一个 `Option<&Box<dyn
State>>`。如果我们不调用 `as_ref`，就会出错，因为我们无法将 `state` 移出函数参数所借用的 `&self`。

然后我们调用 `unwrap` 方法，我们知道这个方法永远不会引发 panic，因为我们知道 `Post` 上的方法可以确保，当那些方法执行完毕时， `state` 总是会包含一个 `Some` 值。这是我们在第9章的 [“When You Have More Information Than the
Compiler”][more-info-than-rustc]<!-- ignore --> 部分讨论的情况之一，当时我们知道一个 `None` 值是不可能存在的，尽管编译器无法理解这一点。

此时，当我们对 `&Box<dyn State>` 调用 `content` 时，去引用强制操作将在 `&` 和 `Box` 上生效，这样 `content` 方法最终就会在实现了 `State` trait 的类型上被调用。这意味着我们需要向 `State` trait 定义中添加 `content`，并且我们将在这里编写逻辑，来决定根据我们所拥有的状态返回什么内容，如清单 18-18 所示。

**清单 18-18:** *src/lib.rs* — 在 `State` 特质中添加 `content` 方法

```rust,noplayground
trait State {
    // --snip--
    fn content<'a>(&self, post: &'a Post) -> &'a str {
        ""
    }
}

// --snip--
struct Published {}

impl State for Published {
    // --snip--
    fn content<'a>(&self, post: &'a Post) -> &'a str {
        &post.content
    }
}

```

我们为 `content` 方法添加了一个默认实现，该实现返回一个空的字符串切片。这意味着我们不需要在 `Draft` 和 `PendingReview` 结构体中实现 `content` 方法。`Published` 结构体将覆盖 `content` 方法，并返回 `post.content` 中的值。虽然这样做很方便，但让 `content` 方法来决定 `State` 的内容，实际上模糊了 `State` 和 `Post` 之间的职责划分。

请注意，正如我们在第10章中讨论的那样，这个方法需要生命周期注释。我们接受一个 `post` 类型的引用作为参数，并返回一个 `post` 类型引用的部分，因此返回引用的生命周期与 `post` 参数的生命周期相关联。

我们完成了——现在 Listing 18-11 中的所有内容都运行正常了！我们已经按照博客文章工作流程的规则实现了状态模式。与规则相关的逻辑存储在状态对象中，而不是分散在 `Post` 中。

> ### 为什么不使用枚举？
>
> 你可能想知道为什么我们没有使用枚举来表示不同的状态。这确实是一个可能的解决方案；你可以尝试一下，然后比较最终的结果，看看哪个方案更适合你！使用枚举的一个缺点是，每个需要检查枚举值的位置都需要一个类似 `match` 的表达式来处理每一个可能的状态。这可能会比使用特征对象解决方案更加重复。

<!-- Old headings. Do not remove or links may break. -->

<a id="trade-offs-of-the-state-pattern"></a>

#### 评估状态模式

我们已经证明了Rust能够实现面向对象的状态模式，从而将帖子在不同状态下的各种行为封装起来。`Post` trait上的方法并不了解这些行为的细节。由于我们的代码组织方式，我们只需要在一个地方就能了解发布后的帖子可能表现出的各种行为：即在`Published` struct上的`State` trait的实现。

如果我们创建一个不使用状态模式的替代实现，我们可能会在 `Post` 的方法中使用 `match` 表达式，甚至在 `main` 代码中检查帖子的状态，并在这些地方改变行为。这意味着我们需要查看多个地方，以理解帖子处于已发布状态所带来的所有影响。

使用状态模式时，`Post`方法和我们使用`Post`的地方不需要`match`表达式。要添加一个新的状态，我们只需要在一个地方添加一个新的结构体，并在该结构体上实现相关的特征方法。

使用状态模式来实现功能很容易扩展，从而添加更多功能。为了体验使用状态模式维护代码的简单性，可以试试以下建议：

- 添加一个 `reject` 方法，将帖子的状态从 `PendingReview` 更改为 `Draft`。
- 在状态可以更改为 `Published` 之前，需要调用两次 `approve`。
- 仅当帖子处于 `Draft` 状态时，才允许用户添加文本内容。
  提示：让负责处理内容变化的状态对象负责处理内容，但不负责修改 `Post`。

状态模式的一个缺点是，由于各个状态实现了状态之间的转换，因此有些状态是相互关联的。如果我们再在 `PendingReview` 和 `Published` 之间添加另一个状态，比如 `Scheduled`，那么我们就不得不修改 `PendingReview` 中的代码，使其转换为 `Scheduled`。如果 `PendingReview` 在添加新状态后不需要进行任何修改的话，那么工作量会少一些，但这意味着我们需要切换到另一种设计模式。

另一个缺点是，我们重复了一些逻辑。为了消除这些重复，我们可能会尝试为 `State` 特质上的`request_review` 和 `approve` 方法实现返回 `self` 的默认实现。然而，这样做是行不通的：当使用 `State` 作为特质对象时，该特质无法知道具体的 `self` 会是什么，因此返回类型在编译时是不确定的。（这是之前提到的动态兼容性规则之一。）

其他重复包括在 `Post` 上对 `request_review` 和 `approve` 方法的类似实现。这两种方法都使用 `Option::take` 与 `Post` 的 `state` 字段，如果 `state` 是 `Some`，那么它们会委托给包装值的相同方法的实现，并将新值的 `state` 字段设置为该结果。如果我们有很多遵循这种模式的 `Post` 方法，我们可能会考虑定义一个宏来消除重复（参见第20章中的 [“Macros”][macros]<!-- ignore --> 部分）。

通过严格按照面向对象语言的规范来实施状态模式，我们并没有充分利用 Rust 的优势。让我们来看看我们可以对 `blog` 这个库进行的一些修改，这些修改可以将无效的状态和转换转化为编译时错误。

### 将编码状态和行为视为类型

我们将向您展示如何重新思考状态模式，以获得不同的权衡。与其将状态和转换完全封装起来，使得外部代码无法了解它们，不如将状态编码为不同类型的对象。这样一来，Rust的类型检查系统将通过发出编译错误来阻止尝试使用只有已发布文章才被允许的草稿文章。

让我们来看一下清单18-11中 `main` 的第一部分：

<Listing file-name="src/main.rs">

```rust,ignore
fn main() {
    let mut post = Post::new();

    post.add_text("I ate a salad for lunch today");
    assert_eq!("", post.content());
}

```

</Listing>

我们仍然允许在草稿状态下创建新帖子，使用 `Post::new` 方法。同时，我们还可以向帖子的内容中添加文本。不过，与草稿帖子相关的 `content` 方法将不再返回空字符串，而是根本不存在。这样一来，如果我们尝试获取草稿帖子的内容，将会出现编译器错误，提示该方法是不存在的。因此，在生产环境中，我们不可能不小心显示草稿帖子的内容，因为这样的代码根本无法编译。清单 18-19 展示了 `Post` 结构体和 `DraftPost` 结构体的定义，以及它们各自的方法。

**清单 18-19:** *src/lib.rs* — 一个 `Post`，包含一个 `content` 方法，以及一个 `DraftPost` 方法，但该 `DraftPost` 方法没有 `content` 方法。

```rust,noplayground
pub struct Post {
    content: String,
}

pub struct DraftPost {
    content: String,
}

impl Post {
    pub fn new() -> DraftPost {
        DraftPost {
            content: String::new(),
        }
    }

    pub fn content(&self) -> &str {
        &self.content
    }
}

impl DraftPost {
    pub fn add_text(&mut self, text: &str) {
        self.content.push_str(text);
    }
}

```

Both `Post` 和 `DraftPost` 结构体都有一个私有的 `content` 字段，用于存储博客文章文本。由于我们将状态的编码转移到了结构体的类型中，所以这些结构体不再拥有 `state` 字段。 `Post` 结构体将代表已发布的文章，并且它有一个 `content` 方法，该方法返回 `content`。

我们仍然有一个 `Post::new` 函数，但它返回的不是 `Post` 的实例，而是 `DraftPost` 的实例。由于 `content` 是私有的，而且没有函数能够返回 `Post`，因此目前无法创建 `Post` 的实例。

这个 `DraftPost` 结构体有一个 `add_text` 方法，因此我们可以像以前一样向 `content` 中添加文本。但请注意， `DraftPost` 并没有定义 `content` 方法！所以现在程序确保所有帖子都以草稿状态开始，而草稿帖子的内容无法被显示。任何试图绕过这些限制的行为都会导致编译器错误。

<!-- Old headings. Do not remove or links may break. -->

<a id="implementing-transitions-as-transformations-into-different-types"></a>

那么，我们如何获得一篇已发布的帖子呢？我们希望实施这样的规则：一个草稿帖子在发布之前必须经过审核和批准。处于待审核状态的帖子仍然不应该显示任何内容。我们可以通过添加另一个结构体 `PendingReviewPost` 来实现这些约束，同时定义 `DraftPost` 上的 `request_review` 方法以返回 `PendingReviewPost`，并定义 `PendingReviewPost` 上的 `approve` 方法以返回 `Post`，如清单 18-20 所示。

**清单 18-20:** *src/lib.rs* — 这是一个由调用 `DraftPost` 上的 `request_review` 和 `approve` 方法创建的 `PendingReviewPost` 对象，该方法将 `PendingReviewPost` 转换为已发布的 `Post`。

```rust,noplayground
impl DraftPost {
    // --snip--
    pub fn request_review(self) -> PendingReviewPost {
        PendingReviewPost {
            content: self.content,
        }
    }
}

pub struct PendingReviewPost {
    content: String,
}

impl PendingReviewPost {
    pub fn approve(self) -> Post {
        Post {
            content: self.content,
        }
    }
}

```

`request_review`和`approve`方法会接管`self`的所有权，从而消耗`DraftPost`和`PendingReviewPost`的实例，并将它们分别转换为`PendingReviewPost`和已发布的`Post`。这样一来，在调用`request_review`之后，就不会有任何剩余的`DraftPost`实例存在了。`PendingReviewPost`结构并没有定义任何`content`方法，因此尝试读取其内容会导致编译器错误，就像`DraftPost`一样。因为要获得一个具有`content`方法的已发布的`Post`实例，唯一的办法就是在`PendingReviewPost`上调用`approve`方法；而要获得一个`PendingReviewPost`，唯一的办法就是在`DraftPost`上调用`request_review`方法。现在，我们已经将博客文章的工作流程编码到了类型系统中。

但是，我们也需要对 `main` 进行一些小的修改。`request_review` 和 `approve` 方法返回的是新的实例，而不是修改被调用的结构体，因此我们需要添加更多的 `let post =` 阴影赋值操作来保存返回的实例。此外，我们不能再对草稿和待审核帖子的内容进行空字符串的断言检查，实际上我们也不需要这样做：我们无法再编译那些试图使用这些状态下帖子内容的代码。更新后的代码在 `main` 中展示，如清单 18-21 所示。

**清单 18-21:** *src/main.rs* — 对 `main` 的修改，以使用博客文章工作流程的新实现

```rust,ignore
use blog::Post;

fn main() {
    let mut post = Post::new();

    post.add_text("I ate a salad for lunch today");

    let post = post.request_review();

    let post = post.approve();

    assert_eq!("I ate a salad for lunch today", post.content());
}

```

我们需要对 `main` 进行的一些修改，以重新分配 `post`，这意味着这种实现不再完全遵循面向对象的状态模式：状态之间的转换不再完全封装在 `Post` 实现内部。不过，我们的好处是，由于类型系统和在编译时进行的类型检查，无效的状态现在变得不可能出现！这确保了某些错误，比如显示未发布帖子的内容，能够在它们进入生产环境之前被发现。

请尝试按照本节开头的建议，在 `blog` crate 的基础上完成任务，正如清单 18-21 中所示。这样你可以了解这个代码版本的设计效果如何。请注意，有些任务可能在这个设计中已经完成了。

我们已经看到，尽管 Rust 能够实现面向对象的设计模式，但还有其他模式，比如将状态编码到类型系统中，这些模式在 Rust 中也是可用的。这些模式有不同的权衡。虽然你可能对面向对象模式非常熟悉，但重新思考问题以利用 Rust 的特性会带来好处，比如能够在编译时避免一些错误。由于某些特性，比如所有权机制，面向对象模式并不总是在 Rust 中最佳的解决方案。

## 摘要

无论你在阅读了这一章之后是否认为Rust是一种面向对象的语言，你现在都知道可以使用特征对象来获取Rust中的一些面向对象特性。动态调度可以为你的代码提供一定的灵活性，但代价是牺牲了一些运行时性能。你可以利用这种灵活性来实现有助于代码可维护性的面向对象模式。Rust还拥有其他特性，比如所有权，这些特性是面向对象语言所没有的。虽然面向对象模式并不总是利用Rust优势的最佳方式，但它确实是一个可行的选择。

接下来，我们将探讨模式这一特性，它是 Rust 的另一个功能，能够提供极大的灵活性。在本书中，我们只是简要地介绍了这一特性，但还没有完全领略到它的全部能力。那么，让我们开始吧！

[more-info-than-rustc]: ch09-03-to-panic-or-not-to-panic.html#cases-in-which-you-have-more-information-than-the-compiler
[macros]: ch20-05-macros.html#macros
