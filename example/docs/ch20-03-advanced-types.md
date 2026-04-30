## 高级类型

Rust的类型系统有一些我们目前已经提到但尚未详细讨论的特性。首先，我们将从整体上讨论新类型，了解它们作为类型的实用性。接着，我们会探讨类型别名，这是一种与新类型类似但语义略有不同的特性。此外，我们还将讨论 `!` 类型以及动态大小的类型。

<!-- Old headings. Do not remove or links may break. -->

<a id="using-the-newtype-pattern-for-type-safety-and-abstraction"></a>

### 使用Newtype模式实现类型安全和抽象

本节假设您已经阅读了前面的内容 [“Implementing External
Traits with the Newtype Pattern”][newtype]<!-- ignore -->。新类型模式对于超出我们目前讨论范围的任务也非常有用，包括静态地确保值不会被混淆，以及指示值的单位。您在 Listing 20-16 中看到了使用新类型来指示单位的例子：请注意， `Millimeters` 和 `Meters` 结构体使用新类型来封装 `u32` 值。如果我们编写一个参数为 `Millimeters` 类型的函数，那么我们就无法编译出一个程序，该程序可能会错误地尝试使用 `Meters` 类型或普通的 `u32` 类型来调用该函数。

我们还可以使用新类型模式来抽象掉某个类型的某些实现细节：新类型可以暴露出一个与私有内部类型不同的公共API。

新类型还可以隐藏内部实现。例如，我们可以提供一个`People`类型来封装一个 `HashMap<i32, String>`，该类型用于存储与人的名字相关的ID。使用 `People` 的代码只会与我们所提供的公共API进行交互，比如将一个名字字符串添加到 `People` 集合中；这样的代码不需要知道我们是在内部为名字分配一个 `i32` ID。这种新类型模式是一种轻量级的方式，可以用来隐藏实现细节，我们在第18章的 [“Encapsulation that
Hides Implementation
Details”][encapsulation-that-hides-implementation-details]<!-- ignore --> 部分中讨论过这一点。

<!-- Old headings. Do not remove or links may break. -->

<a id="creating-type-synonyms-with-type-aliases"></a>

### 类型同义词与类型别名

Rust 提供了声明 _类型别名_ 的功能，以便为现有类型赋予另一个名称。为此，我们使用 `type` 关键字。例如，我们可以创建别名 `Kilometers` 为 `i32`，如下所示：

```rust
    type Kilometers = i32;

```

现在，别名 `Kilometers` 是 `i32` 的_同义词_；与我们在 Listing 20-16 中创建的 `Millimeters` 和 `Meters` 类型不同， `Kilometers` 并不是一个独立的、新的类型。具有 `Kilometers` 类型的值将被视为与 `i32` 类型的值相同。

```rust
    // ANCHOR: here
    type Kilometers = i32;
    // ANCHOR_END: here

    let x: i32 = 5;
    let y: Kilometers = 5;

    println!("x + y = {}", x + y);

```

因为 `Kilometers` 和 `i32` 属于同一类型，我们可以同时添加这两种类型的值，并且可以将 `Kilometers` 类型的值传递给那些需要 `i32` 参数的函数。然而，使用这种方法，我们无法获得之前讨论过的新类型模式所带来的类型检查优势。换句话说，如果我们在某些地方混淆了 `Kilometers` 和 `i32` 的值，编译器并不会报错。

类型同义词的主要用途是减少重复。例如，我们可能会有一个像这样的冗长类型：

```rust,ignore
Box<dyn Fn() + Send + 'static>
```

在函数的签名和代码的类型注解中编写如此长的类型信息可能会很繁琐，并且容易出错。想象一下，项目中有很多这样的代码，就像 Listing 20-25 中的那样。

<Listing number="20-25" caption="Using a long type in many places">

```rust
    let f: Box<dyn Fn() + Send + 'static> = Box::new(|| println!("hi"));

    fn takes_long_type(f: Box<dyn Fn() + Send + 'static>) {
        // --snip--
    }

    fn returns_long_type() -> Box<dyn Fn() + Send + 'static> {
        // --snip--
    }

```

</Listing>

类型别名通过减少重复代码，使得代码更加易于管理。在清单20-26中，我们为冗长的类型引入了一个别名 `Thunk`，并且可以用这个更简洁的别名 `Thunk` 来替代所有对该类型的引用。

<Listing number="20-26" caption="Introducing a type alias, `Thunk`, to reduce repetition">

```rust
    type Thunk = Box<dyn Fn() + Send + 'static>;

    let f: Thunk = Box::new(|| println!("hi"));

    fn takes_long_type(f: Thunk) {
        // --snip--
    }

    fn returns_long_type() -> Thunk {
        // --snip--
    }

```

</Listing>

这段代码更容易阅读和理解！为类型别名选择一个有意义的名称，有助于传达你的意图。（_thunk_这个词表示代码将在以后进行评估，因此它是存储的闭包的合适名称。）

类型别名也常用于 `Result<T, E>` 类型，以减少重复代码。以标准库中的 `std::io` 模块为例，I/O 操作通常会返回一个 `Result<T, E>` 来处理操作失败的情况。该库有一个 `std::io::Error` 结构，用于表示所有可能的 I/O 错误。 `std::io` 中的许多函数将返回一个 `Result<T, E>`，其中 `E` 就是 `std::io::Error`，例如 `Write`  trait 中的这些函数：

```rust,noplayground
use std::fmt;
use std::io::Error;

pub trait Write {
    fn write(&mut self, buf: &[u8]) -> Result<usize, Error>;
    fn flush(&mut self) -> Result<(), Error>;

    fn write_all(&mut self, buf: &[u8]) -> Result<(), Error>;
    fn write_fmt(&mut self, fmt: fmt::Arguments) -> Result<(), Error>;
}

```

<!-- Old headings. Do not remove or links may break. -->这个占位符被多次重复使用。因此，<!-- ignore -->这个占位符也有这样的类型别名声明：

```rust,noplayground
type Result<T> = std::result::Result<T, std::io::Error>;

```

由于这个声明位于 `std::io` 模块中，我们可以使用完全限定的别名 `std::io::Result<T>`；也就是说，a `Result<T, E>` 中的 `E` 被替换为 `std::io::Error`。而 `Write` 特征函数的签名最终看起来就像这样：

```rust,noplayground
pub trait Write {
    fn write(&mut self, buf: &[u8]) -> Result<usize>;
    fn flush(&mut self) -> Result<()>;

    fn write_all(&mut self, buf: &[u8]) -> Result<()>;
    fn write_fmt(&mut self, fmt: fmt::Arguments) -> Result<()>;
}

```

类型别名在两个方面提供帮助：它使得代码更易于编写，同时在整个 `std::io` 范围内提供一致的接口。由于它是一个别名，因此它只是另一个 `Result<T, E>`，这意味着我们可以使用所有适用于 `Result<T, E>` 的方法来处理它，还可以使用像 `?` 这样的特殊语法。

### 永不返回的类型

Rust 有一个特殊的类型，名为 `!`，在类型理论术语中被称为“空类型”，因为它没有任何值。我们更倾向于称之为“永无类型”，因为它代表了当函数永远无法返回值时函数的返回类型。以下是一个例子：

```rust,noplayground
fn bar() -> ! {
    // --snip--
}

```

这段代码的意思是“函数 `bar` 永远不返回任何值”。那些永远不返回任何值的函数被称为_发散函数_。我们无法创建 `!` 类型的值，因此 `bar` 也永远不可能返回任何值。

但是，一个永远无法为其创建值的类型，又有什么用呢？回想一下清单2-5中的代码，这部分内容属于数字猜测游戏的一部分；我们在清单20-27中复制了其中的一部分。

<Listing number="20-27" caption="A `match` with an arm that ends in `continue`">

```rust,ignore
        let guess: u32 = match guess.trim().parse() {
            Ok(num) => num,
            Err(_) => continue,
        };

```

</Listing>

在那个时候，我们省略了这段代码中的一些细节。在第六章的 [“The `match`
Control Flow Construct”][the-match-control-flow-construct]<!-- ignore --> 部分中，我们讨论了 `match` 中的所有函数必须返回相同的类型。因此，例如，以下代码是无效的：

```rust,ignore,does_not_compile
    let guess = match guess.trim().parse() {
        Ok(_) => 5,
        Err(_) => "hello",
    };

```

在这段代码中，类型 `guess` 必须同时是整型和一个字符串。此外，Rust 要求 `guess` 只能有一种类型。那么， `continue` 会返回什么呢？在 Listing 20-27 中，我们如何能够从一个分支返回 `u32`，同时让另一个分支以 `continue` 结尾呢？

正如你可能已经猜到的那样， `continue` 有一个 `!` 值。也就是说，当 Rust 计算 `guess` 的类型时，它会考虑两个匹配项：前者的值为 `u32`，后者的值为 `!`。由于 `!` 永远不可能有值，Rust 决定 `guess` 的类型是 `u32`。

这种行为的正式描述方式是：类型为 `!` 的表达式可以被强制转换为任何其他类型。我们可以以 `match` 结尾，因为 `continue` 并不返回值；相反，它会将控制权返回到循环的顶部。所以在 `Err` 的情况下，我们永远不会为 `guess` 分配一个值。

“Never type”这个特性在使用 `panic!` 宏时也非常有用。回想一下我们调用 `Option<T>` 值的 `unwrap` 函数，以此来产生一个值，或者以这种方式引发 panic。

```rust,ignore
impl<T> Option<T> {
    pub fn unwrap(self) -> T {
        match self {
            Some(val) => val,
            None => panic!("called `Option::unwrap()` on a `None` value"),
        }
    }
}

```

在这段代码中，发生的情况与 Listing 20-27 中的 `match` 相同：Rust 会注意到 `val` 的类型为 `T`，而 `panic!` 的类型为 `!`。因此，整个 `match` 表达式的结果就是 `T`。这段代码之所以有效，是因为 `panic!` 并不会产生任何值；它只是终止了程序。在 `None` 的情况下，我们不会从 `unwrap` 中返回任何值，所以这段代码是有效的。

最后一个具有类型 `!` 的表达式是一个循环：

```rust,ignore
    print!("forever ");

    loop {
        print!("and ever ");
    }

```

在这里，循环永远不会结束，所以 `!` 就是这个表达式的值。然而，如果我们加入 `break`，情况就不一样了，因为循环会在到达 `break` 时终止。

### 动态大小类型与 `Sized` 特质

Rust需要了解其类型的某些细节，比如为特定类型的变量分配多少内存。这使得其类型系统的某个方面在最初看起来有些混乱：即所谓_动态大小类型_的概念。这些类型有时也被称为_DSTs或_无大小类型_，它们允许我们编写代码，使用在运行时才能确定大小的值。

让我们详细了解一下名为 `str` 的动态大小类型，我们在整本书中都使用了它。没错，不是 `&str`，而是单独的 `str`，它是一个 DST。在许多情况下，比如存储用户输入的文本时，我们在运行时无法知道字符串的长度。这意味着我们无法创建类型为 `str` 的变量，也无法接受类型为 `str` 的参数。请看下面这段代码，它无法正常工作：

```rust,ignore,does_not_compile
    let s1: str = "Hello there!";
    let s2: str = "How's it going?";

```

Rust需要知道为某个特定类型的任何值分配多少内存，而且所有该类型的值必须使用相同数量的内存。如果Rust允许我们编写这样的代码，那么这两个不同的 `str` 值将需要占用相同的存储空间。但实际上，它们的长度是不同的： `s1` 需要12个字节的存储空间，而 `s2` 则需要15个字节。这就是为什么无法创建一个存储动态大小类型的变量的原因。

那么，我们该怎么办呢？在这种情况下，你已经知道答案了：我们创建的是 `s1` 和 `s2` 字符串切片（`&str`），而不是 `str`。回想一下第4章中的 [“String Slices”][string-slices]<!-- ignore --> 部分，切片数据结构只存储切片的起始位置和长度。因此，虽然 `&T` 是一个单独的值，用于存储 `T` 的内存地址，但字符串切片实际上是由两个值组成的：`str` 的地址和它的长度。因此，我们可以在编译时知道字符串切片的大小：它是 `usize` 长度的两倍。也就是说，无论所引用的字符串有多长，我们总能知道字符串切片的大小。一般来说，这就是Rust中动态大小类型的使用方式：它们具有额外的元数据，用于存储动态信息的大小。动态大小类型的黄金法则是，我们必须始终将动态大小类型的值放在某种指针之后。

我们可以将 `str` 与各种指针结合起来：例如， `Box<str>` 或 `Rc<str>`。实际上，你之前已经见过这种情况，只不过当时使用的是动态大小的类型——特质。每一个特质都是一种动态大小的类型，我们可以通过使用该特质的名称来引用它。在第十八章的 [“Using Trait Objects to Abstract over
Shared Behavior”][using-trait-objects-to-abstract-over-shared-behavior]<!--
ignore --> 这一部分中，我们提到过，要将特质作为特质对象使用时，必须将其放在指针之后，比如 `&dyn Trait` 或 `Box<dyn
Trait>`（`Rc<dyn Trait>` 同样适用）。

为了与智能指针打交道，Rust提供了 `Sized` 这个特质，用于确定某个类型的尺寸在编译时是否已知。这个特质会自动应用于所有在编译时已知尺寸的类型。此外，Rust还会隐式地为每个泛型函数添加一个界限，即 `Sized`。也就是说，像这样的泛型函数定义：

```rust,ignore
fn generic<T>(t: T) {
    // --snip--
}

```

实际上，它会被当作我们这样写的：

```rust,ignore
fn generic<T: Sized>(t: T) {
    // --snip--
}

```

默认情况下，通用函数仅适用于在编译时已知大小的类型。然而，你可以使用以下特殊语法来放宽这一限制：

```rust,ignore
fn generic<T: ?Sized>(t: &T) {
    // --snip--
}

```

在 `?Sized` 上的 trait 绑定意味着“`T` 可能等于 `Sized`，也可能不等于”，这种表示法覆盖了通用类型在编译时必须有已知大小的默认规则。具有这种含义的 `?Trait` 语法仅适用于 `Sized`，不适用于其他任何 trait。

另外需要注意的是，我们将 `t` 参数的类型从 `T` 更改为 `&T`。由于该类型可能不是 `Sized` 类型，我们需要通过某种指针来引用它。在这种情况下，我们选择了使用引用。

接下来，我们将讨论函数和闭包！

[encapsulation-that-hides-implementation-details]: ch18-01-what-is-oo.html#encapsulation-that-hides-implementation-details
[string-slices]: ch04-03-slices.html#string-slices
[the-match-control-flow-construct]: ch06-02-match.html#the-match-control-flow-construct
[using-trait-objects-to-abstract-over-shared-behavior]: ch18-02-trait-objects.html#using-trait-objects-to-abstract-over-shared-behavior
[newtype]: ch20-02-advanced-traits.html#implementing-external-traits-with-the-newtype-pattern
