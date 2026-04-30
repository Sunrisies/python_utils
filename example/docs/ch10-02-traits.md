<!-- Old headings. Do not remove or links may break. -->

<a id="traits-defining-shared-behavior"></a>

## 使用特质定义共享行为

**特质**定义了某个特定类型所具有的功能，并且该类型可以与其他类型共享这些功能。我们可以使用特质来以抽象的方式定义共享的行为。我们还可以通过**特质边界**来指定一个泛型类型可以是任何具有特定行为的类型。

注意：特性与其他语言中常被称为“接口”的功能类似，尽管两者之间存在一些差异。

### 定义特质

一个类型的行为指的是我们可以对该类型调用的方法。如果我们可以在所有这些类型上调用相同的方法，那么不同的类型就具有相同的行为。特质定义是一种将方法签名组合在一起的方式，以此来定义实现某种功能所需的一系列行为。

例如，假设我们有多个结构体，它们分别存储不同类型和数量的文本：一个结构体 `a `NewsArticle`` 用于存储存放在特定位置的新闻报道；另一个结构体 `a `SocialPost`` 最多可以存储280个字符，并且带有元数据，用于指示该报道是新的帖子、重复发布的帖子，还是对另一篇帖子的回复。

我们想要创建一个名为 `aggregator` 的媒体聚合库，它能够显示可能存储在 `NewsArticle` 或 `SocialPost` 实例中的数据摘要。为此，我们需要每种类型的数据摘要，我们将通过调用实例上的 `summarize` 方法来获取这些摘要。列表 10-12 展示了实现这一行为的公共 `Summary` 特质的定义。

<Listing number="10-12" file-name="src/lib.rs" caption="A `Summary` trait that consists of the behavior provided by a `summarize` method">

```rust,noplayground
pub trait Summary {
    fn summarize(&self) -> String;
}

```

</Listing>

在这里，我们使用 `trait` 关键字来声明一个特质，然后是该特质的名称，在这个例子中是 `Summary`。我们还将该特质声明为 `pub`，这样依赖于这个 crate 的其他 crate 也可以使用这个特质，我们将在几个例子中看到这一点。在花括号内部，我们声明了描述实现这个特质类型的类型的行为的方法签名，在这个例子中是 `fn summarize(&self) -> String`。

在方法签名之后，我们不使用花括号来提供实现，而是使用分号。每个实现此特性的类型都必须为该方法的内容提供自己的自定义行为。编译器会确保任何具有 `Summary` 特性的类型都会以这种签名来定义 `summarize` 方法。

一个特质可以在其体内包含多个方法：这些方法签名每行一个，并且每行以分号结尾。

### 在类型上实现 trait

既然我们已经定义了 `Summary`  trait 方法的期望签名，那么就可以在媒体聚合器中的类型上实现它了。列表 10-13 展示了在 `NewsArticle` 结构上的 `Summary` trait 的实现，该实现使用标题、作者和位置来创建 `summarize` 的返回值。对于 `SocialPost` 结构，我们定义 `summarize` 为用户名，后面跟着帖子的完整文本，前提是帖子的内容已经被限制在 280 个字符以内。

<Listing number="10-13" file-name="src/lib.rs" caption="Implementing the `Summary` trait on the `NewsArticle` and `SocialPost` types">

```rust,noplayground
pub struct NewsArticle {
    pub headline: String,
    pub location: String,
    pub author: String,
    pub content: String,
}

impl Summary for NewsArticle {
    fn summarize(&self) -> String {
        format!("{}, by {} ({})", self.headline, self.author, self.location)
    }
}

pub struct SocialPost {
    pub username: String,
    pub content: String,
    pub reply: bool,
    pub repost: bool,
}

impl Summary for SocialPost {
    fn summarize(&self) -> String {
        format!("{}: {}", self.username, self.content)
    }
}

```

</Listing>

在类型上实现 trait 与实现普通方法类似。不同之处在于，在 `impl` 之后，我们需要输入想要实现的 trait 名称，然后使用 `for` 关键字，接着指定想要为哪种类型实现该 trait 的类型名称。在 `impl` 块内，我们需要输入 trait 定义中定义的方法签名。不需要在每个签名后面加上分号，而是使用花括号来填写方法体，具体描述 trait 的方法对于特定类型应有的行为。

现在，该库已经在 `NewsArticle` 和 `SocialPost` 上实现了 `Summary` trait。因此，使用该库的用户可以在 `NewsArticle` 和 `SocialPost` 的实例上调用 trait 方法，就像调用普通方法一样。唯一的区别是，用户必须同时将 trait 以及相关类型带入作用域。以下是一个示例，说明一个二进制 crate 如何使用我们的 `aggregator` 库。

```rust,ignore
use aggregator::{SocialPost, Summary};

fn main() {
    let post = SocialPost {
        username: String::from("horse_ebooks"),
        content: String::from(
            "of course, as you probably already know, people",
        ),
        reply: false,
        repost: false,
    };

    println!("1 new post: {}", post.summarize());
}

```

这段代码会输出 `1 new post: horse_ebooks: of course, as you probably already
know, people`。

其他依赖于 `aggregator` 的软件包也可以将 `Summary` 特性引入，以便在自己的类型上实现 `Summary`。需要注意的是，我们只能在特性或类型本身，或者两者都属于我们的软件包范围内时，才能在类型上实现某个特性。例如，我们可以在自定义类型 `SocialPost` 上实现标准库中的特性 `Display`，因为类型 `SocialPost` 属于我们的 `aggregator` 软件包。同样，我们也可以在我们的 `aggregator` 软件包中实现 `Summary`，因为特性 `Summary` 属于我们的 `aggregator` 软件包。

但是，我们无法在外部类型上实现外部特性。例如，我们无法在我们的 `aggregator` 包中实现对 `Vec<T>` 的 `Display` trait，因为 `Display` 和 `Vec<T>` 都定义在标准库中，并不属于我们的 `aggregator` 包。这种限制是 _一致性_ 属性的一部分，更具体地说，就是 _孤儿规则_。这个规则之所以如此命名，是因为父类型并不存在。这一规则确保了其他人的代码不会破坏你的代码，反之亦然。如果没有这一规则，两个包可能会为同一个类型实现相同的特性，而 Rust 将无法判断应该使用哪个实现。

<!-- Old headings. Do not remove or links may break. -->

<a id="default-implementations"></a>

### 使用默认实现

有时候，为某个或某些方法在 trait 中设置默认行为会很有用，这样就不需要在每个类型上为所有方法都提供具体的实现。因此，当我们在一个特定类型上实现该 trait 时，我们可以保留或覆盖每个方法的默认行为。

在列表10-14中，我们为`Summary` trait的`summarize`方法指定了一个默认字符串，而不是像在列表10-12中那样只定义该方法签名。

<Listing number="10-14" file-name="src/lib.rs" caption="Defining a `Summary` trait with a default implementation of the `summarize` method">

```rust,noplayground
pub trait Summary {
    fn summarize(&self) -> String {
        String::from("(Read more...)")
    }
}

```

</Listing>

为了使用默认实现来总结 `NewsArticle` 的实例，我们需要使用一个空的 `impl` 块，并附加 `impl Summary for NewsArticle {}`。

尽管我们不再直接在 `NewsArticle` 上定义 `summarize` 方法，但我们提供了默认的实现，并明确指出 `NewsArticle` 实现了 `Summary` 特性。因此，我们仍然可以在 `NewsArticle` 的实例上调用 `summarize` 方法，就像这样：

```rust,ignore
    let article = NewsArticle {
        headline: String::from("Penguins win the Stanley Cup Championship!"),
        location: String::from("Pittsburgh, PA, USA"),
        author: String::from("Iceburgh"),
        content: String::from(
            "The Pittsburgh Penguins once again are the best \
             hockey team in the NHL.",
        ),
    };

    println!("New article available! {}", article.summarize());

```

这段代码会输出 `New article available! (Read more...)`。

创建默认实现并不需要我们对清单10-13中 `Summary` 在 `SocialPost` 上的实现进行任何修改。因为覆盖默认实现的语法与实现没有默认实现的 trait 方法的语法是相同的。

默认实现可以调用同一特质中的其他方法，即使这些其他方法没有默认实现。通过这种方式，一个特质可以提供许多有用的功能，而只需要实现者指定其中的一小部分功能。例如，我们可以定义 `Summary` 这个特质，使其包含一个需要实现的 `summarize_author` 方法，然后定义一个 `summarize` 方法，该方法的默认实现会调用 `summarize_author` 方法。

```rust,noplayground
pub trait Summary {
    fn summarize_author(&self) -> String;

    fn summarize(&self) -> String {
        format!("(Read more from {}...)", self.summarize_author())
    }
}

```

要使用这个版本的 `Summary`，我们只需要在一个类型上实现该特质时定义 `summarize_author`。

```rust,ignore
impl Summary for SocialPost {
    fn summarize_author(&self) -> String {
        format!("@{}", self.username)
    }
}

```

在我们定义了 `summarize_author` 之后，我们可以在 `SocialPost` 结构的实例上调用 `summarize`，而 `summarize` 的默认实现会调用我们提供的 `summarize_author` 的定义。由于我们已经实现了 `summarize_author`，因此 `Summary` 特质为我们提供了 `summarize` 方法的行为，而无需我们编写更多的代码。以下是具体的实现方式：

```rust,ignore
    let post = SocialPost {
        username: String::from("horse_ebooks"),
        content: String::from(
            "of course, as you probably already know, people",
        ),
        reply: false,
        repost: false,
    };

    println!("1 new post: {}", post.summarize());

```

这段代码会输出 `1 new post: (Read more from @horse_ebooks...)`。

请注意，无法从同一方法的覆盖实现中调用默认实现。

<!-- Old headings. Do not remove or links may break. -->

<a id="traits-as-parameters"></a>

### 将特质作为参数使用

现在您已经学会了如何定义和实现 trait，我们可以探讨如何利用 trait 来定义能够接受多种不同类型的数据的函数。在 Listing 10-13 中，我们将使用在 `NewsArticle` 和 `SocialPost` 类型上实现的 `Summary` trait，来定义一个 `notify` 函数。该函数的功能是在其 `item` 参数上调用 `summarize` 方法，而 `item` 参数则是一个实现了 `Summary` trait 的类型。为了实现这一点，我们将使用 `impl Trait` 语法，如下所示：

```rust,ignore
pub fn notify(item: &impl Summary) {
    println!("Breaking news! {}", item.summarize());
}

```

instead of using a specific type for the `item` parameter, we specify the `impl` keyword and the trait name. This parameter can accept any type that implements the specified trait. In the body of `notify`, we can call any methods on `item` that come from the `Summary` trait, such as `summarize`. We can also call `notify` and pass in any instance of `NewsArticle` or `SocialPost`. Code that uses `item` with any other type, such as `String` or `i32`, will not compile, because those types do not implement `Summary`.

<!-- Old headings. Do not remove or links may break. -->

<a id="fixing-the-largest-function-with-trait-bounds"></a>

#### 特质绑定语法

`impl Trait`这种语法适用于简单的情况，但实际上它是更长形式的一种语法糖，被称为“特质绑定”。它的样子如下：

```rust,ignore
pub fn notify<T: Summary>(item: &T) {
    println!("Breaking news! {}", item.summarize());
}
```

这种较长的形式与上一节中的示例相当，但内容更为详细。我们会在冒号之后，并将 trait 约束与泛型类型参数的声明放在尖括号内。

`impl Trait`语法在简单情况下非常方便，能够使得代码更加简洁。而在其他情况下，更完整的特征绑定语法则能够表达更复杂的逻辑。例如，我们可以有两个实现`Summary`的参数。使用`impl Trait`语法时，这样的实现看起来就像这样：

```rust,ignore
pub fn notify(item1: &impl Summary, item2: &impl Summary) {
```

如果我们希望这个函数允许 `item1` 和 `item2` 拥有不同的类型（只要这两种类型都实现了 `Summary`），那么使用 `impl Trait` 是合适的。然而，如果我们希望强制两个参数具有相同的类型，那么我们必须使用 trait 绑定，如下所示：

```rust,ignore
pub fn notify<T: Summary>(item1: &T, item2: &T) {
```

泛型类型 `T` 被指定为 `item1` 和 `item2` 的参数类型。这限制了函数的行为，使得作为 `item1` 和 `item2` 参数的具体类型必须相同。

<!-- Old headings. Do not remove or links may break. -->

<a id="specifying-multiple-trait-bounds-with-the--syntax"></a>

#### 使用 `+` 语法定义多个 trait 边界

我们还可以指定多个特性约束。假设我们希望 `notify` 也能使用显示格式，同时 `item` 也能使用 `summarize`：我们可以在 `notify` 的定义中指定 `item` 必须同时实现 `Display` 和 `Summary`。我们可以使用 `+` 语法来实现这一点。

```rust,ignore
pub fn notify(item: &(impl Summary + Display)) {
```

`+`语法在泛型类型的特征边界中也是有效的：

```rust,ignore
pub fn notify<T: Summary + Display>(item: &T) {
```

在指定了这两个 trait 边界之后， `notify` 的主体可以调用 `summarize`，并且可以使用 `{}` 来格式化 `item`。

#### 使用 `where` 子句使 trait 边界更加清晰

使用过多的 trait 约束有其缺点。每个泛型类型都有自己对应的 trait 约束，因此具有多个泛型类型参数的函数会在函数名和参数列表之间包含大量的 trait 约束信息，这会使函数签名难以阅读。因此，Rust 提供了另一种语法，用于在函数签名之后的 `where` 子句中指定 trait 约束。所以，与其这样写：

```rust,ignore
fn some_function<T: Display + Clone, U: Clone + Debug>(t: &T, u: &U) -> i32 {
```

我们可以使用一个 `where` 子句，就像这样：

```rust,ignore
fn some_function<T, U>(t: &T, u: &U) -> i32
where
    T: Display + Clone,
    U: Clone + Debug,
{

```

这个函数的签名更加简洁：函数名、参数列表和返回类型紧密排列在一起，类似于没有大量特征限定的函数。

### 返回实现了特定特征的类型

我们还可以使用 `impl Trait` 语法在返回位置返回一个实现了某个 trait 的值，如下所示：

```rust,ignore
fn returns_summarizable() -> impl Summary {
    SocialPost {
        username: String::from("horse_ebooks"),
        content: String::from(
            "of course, as you probably already know, people",
        ),
        reply: false,
        repost: false,
    }
}

```

通过使用 `impl Summary` 作为返回类型，我们指定了 `returns_summarizable` 函数返回一个实现了 `Summary` 特性的类型，但并未具体说明该类型的具体形式。在这种情况下， `returns_summarizable` 返回一个 `SocialPost`，但调用此函数的代码无需知道这一细节。

仅通过函数实现的特质来指定返回类型的能力，在闭包和迭代器的上下文中特别有用。这些概念我们将在第13章中详细讨论。闭包和迭代器创建的类型只有编译器才知道，或者这些类型的指定非常冗长。`impl Trait`语法允许你简洁地指定一个函数返回实现了`Iterator`特质的某种类型，而无需写出非常冗长的类型说明。

不过，只有当你返回单一类型时才能使用 `impl Trait`。例如，以下代码如果返回的是 `NewsArticle` 或 `SocialPost`，并且返回类型被指定为 `impl Summary`，那么这种代码是无效的。

```rust,ignore,does_not_compile
fn returns_summarizable(switch: bool) -> impl Summary {
    if switch {
        NewsArticle {
            headline: String::from(
                "Penguins win the Stanley Cup Championship!",
            ),
            location: String::from("Pittsburgh, PA, USA"),
            author: String::from("Iceburgh"),
            content: String::from(
                "The Pittsburgh Penguins once again are the best \
                 hockey team in the NHL.",
            ),
        }
    } else {
        SocialPost {
            username: String::from("horse_ebooks"),
            content: String::from(
                "of course, as you probably already know, people",
            ),
            reply: false,
            repost: false,
        }
    }
}

```

由于编译器在实现 `impl Trait` 语法时的限制，返回 `NewsArticle` 或 `SocialPost` 是不被允许的。我们将在第十八章的“使用特质对象来抽象共享行为”部分，介绍如何编写具有这种行为的函数。

### 使用特质边界来条件性地实现方法

通过使用带有 `impl` 块的特质绑定，该块使用了泛型类型参数，我们可以为实现了指定特质的类型有条件地实现方法。例如，在 Listing 10-15 中的 `Pair<T>` 类型总是会实现 `new` 函数，该函数会返回 `Pair<T>` 的新实例（回想一下第 5 章的 “方法语法” 部分，其中 `Self` 是 `impl` 块中类型的别名，在这种情况下就是 `Pair<T>`）。但在下一个 `impl` 块中， `Pair<T>` 只有在其内部类型 `T` 实现了允许比较的 `PartialOrd` 特质以及允许打印的 `Display` 特质时，才会实现 `cmp_display` 方法。

<Listing number="10-15" file-name="src/lib.rs" caption="Conditionally implementing methods on a generic type depending on trait bounds">

```rust,noplayground
use std::fmt::Display;

struct Pair<T> {
    x: T,
    y: T,
}

impl<T> Pair<T> {
    fn new(x: T, y: T) -> Self {
        Self { x, y }
    }
}

impl<T: Display + PartialOrd> Pair<T> {
    fn cmp_display(&self) {
        if self.x >= self.y {
            println!("The largest member is x = {}", self.x);
        } else {
            println!("The largest member is y = {}", self.y);
        }
    }
}

```

</Listing>

我们还可以有条件地为一个实现了另一个特性的类型实现该特性。对于满足某个特性的任何类型，其上的特性实现被称为“泛化实现”，在Rust标准库中得到了广泛的应用。例如，标准库会在实现了`Display`特性的任何类型上实现`ToString`特性。标准库中的`impl`块看起来类似于以下代码：

```rust,ignore
impl<T: Display> ToString for T {
    // --snip--
}
```

由于标准库提供了这种通用的实现，我们可以在任何实现了 `Display` 特性的类型上调用由 `ToString` 特性定义的 `to_string` 方法。例如，我们可以将整数转换为相应的 `String` 值，因为整数实现了 `Display` 特性。

```rust
let s = 3.to_string();
```

在文档的“Implementors”部分中，会看到关于该 trait 的通用实现。

特质和特质边界让我们能够编写使用泛型类型参数的代码，从而减少重复代码，同时向编译器明确表明我们希望该泛型类型具有特定的行为。编译器可以利用特质边界的信息来确保所有在代码中使用的具体类型都表现出正确的行为。在动态类型语言中，如果我们对一个没有定义该方法的类型调用某个方法，那么在运行时就会出错。但Rust将这些错误提前到了编译时，这样我们就必须在代码运行之前就解决这些问题。此外，我们不必编写在运行时检查行为的代码，因为我们已经在编译时进行了检查。这样做可以提高性能，同时又不牺牲泛型的灵活性。

[trait-objects]: ch18-02-trait-objects.html#using-trait-objects-to-abstract-over-shared-behavior
[methods]: ch05-03-method-syntax.html#method-syntax
