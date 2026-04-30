## 定义枚举类型

结构体能够让你将相关的字段和数据组合在一起，比如用 `Rectangle` 来表示，同时还有 `width` 和 `height`。而枚举则可以用来表示某个值属于一组可能的取值之一。例如，我们可能希望表示 `Rectangle` 是包含 `Circle` 和 `Triangle` 的一组可能的形状之一。为了实现这一点，Rust 允许我们将这些可能性编码为枚举类型。

让我们来看一个可能需要在代码中表达的情况，并了解为什么在这种情况下枚举比结构体更实用且更合适。假设我们需要处理IP地址。目前，有两种主要的IP地址标准：版本4和版本6。由于这些是我们程序可能遇到的唯一IP地址格式，因此我们可以枚举所有可能的变体，这就是枚举名称的由来。

任何IP地址都可以是版本四或版本六的地址，但不能同时拥有这两种特性。这种IP地址的特性使得枚举数据结构变得合适，因为枚举值只能是其其中一个变体。无论是版本四还是版本六的地址，本质上都是IP地址，因此在代码处理适用于任何类型IP地址的情况时，应该将它们视为同一类型。

我们可以通过定义一种名为 `IpAddrKind` 的枚举类型，并列出 IP 地址可能的种类 `V4` 和 `V6`，来用代码表达这个概念。这些就是该枚举的两种变体。

```rust
enum IpAddrKind {
    V4,
    V6,
}

```

`IpAddrKind`现在是一种自定义数据类型，我们可以在代码的其他地方使用它。

### 枚举值

我们可以像这样创建 `IpAddrKind` 这两种变体的实例：

```rust
    let four = IpAddrKind::V4;
    let six = IpAddrKind::V6;

```

请注意，枚举的变体是以其标识符为前缀的，我们使用双冒号来分隔这两个部分。这样做很有用，因为现在`IpAddrKind::V4`和`IpAddrKind::V6`都是同一类型：`IpAddrKind`。然后，我们可以定义一个函数，该函数可以接受任何`IpAddrKind`。

```rust
    route(IpAddrKind::V4);
    route(IpAddrKind::V6);
fn route(ip_kind: IpAddrKind) {}

```

我们可以以这两种方式调用这个函数：

```rust
    route(IpAddrKind::V4);
    route(IpAddrKind::V6);

```

使用枚举类型还有更多的优势。再仔细想想我们的IP地址类型，目前我们并没有办法存储实际的IP地址数据；我们只知道它的类型而已。鉴于你刚刚学习了第5章中的结构体知识，你可能会想用结构体来解决这个问题，如清单6-1所示。

<Listing number="6-1" caption="Storing the data and `IpAddrKind` variant of an IP address using a `struct`">

```rust
    enum IpAddrKind {
        V4,
        V6,
    }

    struct IpAddr {
        kind: IpAddrKind,
        address: String,
    }

    let home = IpAddr {
        kind: IpAddrKind::V4,
        address: String::from("127.0.0.1"),
    };

    let loopback = IpAddr {
        kind: IpAddrKind::V6,
        address: String::from("::1"),
    };

```

</Listing>

在这里，我们定义了一个结构体 `IpAddr`，它包含两个字段：一个类型为 `IpAddrKind` 的字段（即我们之前定义的枚举类型），以及一个类型为 `String` 的字段。我们有了这个结构体的两个实例。第一个实例是 `home`，它的 `kind` 值为 `IpAddrKind::V4`，并且关联了 `127.0.0.1` 的地址数据。第二个实例是 `loopback`，它的 `kind` 值为 `IpAddrKind`，并且关联了 `::1` 的地址数据。我们使用结构体来将 `kind` 和 `address` 的值组合在一起，这样该变体就与相应的值相关联了。

不过，使用枚举来表示相同的概念会更加简洁：  
与其将枚举放在结构体内，我们可以直接将数据放入每个枚举的变体中。这种对 `IpAddr` 枚举的新定义意味着 `V4` 和 `V6` 变体都将拥有相关的 `String` 值。

```rust
    enum IpAddr {
        V4(String),
        V6(String),
    }

    let home = IpAddr::V4(String::from("127.0.0.1"));

    let loopback = IpAddr::V6(String::from("::1"));

```

我们直接将数据附加到枚举的每个变体上，因此不需要额外的结构体。这里还可以更清楚地看到枚举的工作原理：我们定义的每个枚举变体的名称实际上也是一个函数，该函数用于构造枚举的实例。也就是说，`IpAddr::V4()`是一个函数调用，它接受一个`String`参数，并返回`IpAddr`类型的实例。当我们定义枚举时，这个构造函数函数会自动被定义下来。

使用枚举而不是结构还有一个优点：每个变体可以拥有不同的类型以及不同的关联数据量。第四版的IP地址总是包含四个数字组件，这些组件的值介于0到255之间。如果我们想要将 `V4` 类型的地址存储为四个 `u8` 值，同时还能将 `V6` 类型的地址表示为一个 `String` 值，那么使用结构是无法实现的。而枚举则可以轻松处理这种情况。

```rust
    enum IpAddr {
        V4(u8, u8, u8, u8),
        V6(String),
    }

    let home = IpAddr::V4(127, 0, 0, 1);

    let loopback = IpAddr::V6(String::from("::1"));

```

我们已经展示了几种不同的方法来定义数据结构，用于存储版本四和版本六的IP地址。不过，事实证明，存储IP地址并标识其类型是非常常见的需求，以至于标准库已经提供了一个我们可以使用的定义！让我们来看看标准库是如何定义 `IpAddr` 的。它包含了与我们定义和使用的完全相同的枚举和变体，但是它将地址数据嵌入到这些变体中，并以两种不同的结构体形式呈现，这两种结构体的定义方式因每个变体而异。

```rust
struct Ipv4Addr {
    // --snip--
}

struct Ipv6Addr {
    // --snip--
}

enum IpAddr {
    V4(Ipv4Addr),
    V6(Ipv6Addr),
}
```

这段代码展示了你可以将任何类型的数据放入枚举变量中，例如字符串、数值类型或结构体。你甚至还可以包含另一个`enum!`。此外，标准库中的类型通常并不比你自己设计的类型复杂多少。

请注意，尽管标准库中包含了一个 `IpAddr` 的定义，但我们仍然可以创建并使用自己的定义，而不会引发冲突，因为我们没有将标准库的定义引入到我们的作用域中。我们将在第七章中进一步讨论如何将类型引入作用域。

让我们来看一下清单6-2中另一个枚举的例子：这个枚举的变体中包含了多种类型。

<Listing number="6-2" caption="A `Message` enum whose variants each store different amounts and types of values">

```rust
enum Message {
    Quit,
    Move { x: i32, y: i32 },
    Write(String),
    ChangeColor(i32, i32, i32),
}

```

</Listing>

这个枚举包含四种不同的类型：

- `Quit`: 没有任何相关数据
- `Move`: 具有命名字段，类似于结构体
- `Write`: 包含一个 `String`
- `ChangeColor`: 包含三个 `i32` 值

定义带有变体的枚举，就像清单6-2中的那样，与定义不同类型的结构体类似。不过，枚举不会使用`struct`这个关键字，所有变体都被归类在`Message`这个类型下。以下结构体可以包含与前面的枚举变体相同的数据：

```rust
struct QuitMessage; // unit struct
struct MoveMessage {
    x: i32,
    y: i32,
}
struct WriteMessage(String); // tuple struct
struct ChangeColorMessage(i32, i32, i32); // tuple struct

```

但是，如果我们使用不同的结构体，每个结构体都有自己独立的类型，那么我们就无法像使用 Listing 6-2 中定义的 `Message` enum 那样，轻松地定义一个可以处理这些类型消息的函数。因为 `Message` enum 是一个单一的类型。

枚举类型和结构体之间还有一个相似之处：就像我们可以在结构体上定义方法一样，我们也可以在枚举类型上定义方法。这里有一个名为 `call` 的方法，我们可以在我们的 `Message` 枚举类型上定义这个方法。

```rust
    impl Message {
        fn call(&self) {
            // method body would be defined here
        }
    }

    let m = Message::Write(String::from("hello"));
    m.call();

```

该方法的主体部分会使用 `self` 来获取我们调用该方法的对象的值。在这个例子中，我们创建了一个变量 `m`，该变量的值为 `Message::Write(String::from("hello"))`。而当 `m.call()` 运行时， `self` 就会处于 `call` 方法的主体部分。

让我们来看看标准库中另一个非常常见且有用的枚举类型：`Option`。

<!-- Old headings. Do not remove or links may break. -->

<a id="the-option-enum-and-its-advantages-over-null-values"></a>

### `Option` 枚举类型

本节探讨了一个关于 `Option` 的案例研究，这是一种由标准库定义的枚举类型。 `Option` 类型描述了一种非常常见的场景：一个值可以是某种东西，也可以什么都不是。

例如，如果您请求一个非空列表中的第一个元素，那么你会得到一个值。而如果你请求一个空列表中的第一个元素，那么你将得不到任何东西。用类型系统来表达这个概念意味着编译器可以检查你是否处理了所有应该处理的情况；这种功能可以避免在其他编程语言中非常常见的错误。

编程语言的设计通常从所包含的功能来考虑，但被排除的功能同样重要。Rust没有许多其他语言所拥有的`null`特性。`Null`是一个表示没有值的变量。在那些有`null`特性的语言中，变量总是处于两种状态之一：null或not-null。

在2009年的演讲《空引用：价值十亿美元的错误》中，作为“空引用”概念的发明者，Tony Hoare这样说道：

我将其称为“我的十亿美元错误”。当时，我正在为面向对象语言设计第一个全面的引用类型系统。我的目标是确保所有对引用的使用都是绝对安全的，并且由编译器自动进行检查。但我无法抗拒将空引用加入其中的诱惑，因为这样做非常容易实现。这一错误导致了无数错误、漏洞以及系统崩溃，这些后果在过去四十年里可能造成了十亿美元的损失和损害。

null值的问题在于，如果你试图将null值当作not-null值来使用，就会引发某种错误。由于这种not-null属性非常普遍，因此很容易出现这种错误。

不过，null试图表达的概念仍然很有用：null是一个当前因某种原因无效或不存在的值。

问题并不在于概念本身，而在于具体的实现方式。因此，Rust中并没有所谓的“null”值，但它有一个枚举类型，可以用来表示某个值是否存在。这个枚举类型是`Option<T>`，并且它是由标准库[option]<!-- ignore -->定义的，具体如下所示：

```rust
enum Option<T> {
    None,
    Some(T),
}
```

`Option<T>`这个枚举非常有用，甚至被包含在prelude中；你不需要显式地将其引入作用域。它的变体也被包含在prelude中：你可以直接使用`Some`和`None`，而无需使用`Option::`作为前缀。`Option<T>`这个枚举仍然只是一个普通的枚举，而`Some(T)`和`None`则是类型`Option<T>`的变体。

`<T>`语法是Rust中的一个特性，我们之前还没有讨论过。它是一个泛型类型参数，我们将在第十章中更详细地介绍泛型。目前，你需要知道的是，`<T>`表示`Some`这个枚举的变体可以存储任何类型的单个数据，而每一个实际使用的类型都会使得整体`Option<T>`类型成为一个不同的类型。以下是一些使用`Option`值来存储数字类型和字符类型的例子：

```rust
    let some_number = Some(5);
    let some_char = Some('e');

    let absent_number: Option<i32> = None;

```

`some_number`的类型是`Option<i32>`。`some_char`的类型是`Option<char>`，这是一个不同的类型。Rust能够推断出这些类型，因为我们在`Some`变体中指定了一个值。对于`absent_number`，Rust要求我们注释整个`Option`类型：编译器无法仅通过查看`None`值来推断出相应的`Some`变体将持有什么类型。在这里，我们告诉Rust，我们希望`absent_number`具有`Option<i32>`类型。

当我们有一个 `Some` 值时，我们知道存在一个值，而且这个值被存储在 `Some` 中。当我们有一个 `None` 值时，从某种意义上讲，它和 null 的含义是一样的：我们没有有效的数值。那么，为什么拥有 `Option<T>` 比拥有 null 要好呢？

简而言之，因为 `Option<T>` 和 `T`（其中 `T` 可以是任何类型）是不同类型的，编译器不会允许我们将 `Option<T>` 的值当作一个有效的数值来使用。例如，这段代码无法编译，因为它试图将一个 `i8` 加到 `Option<i8>` 上。

```rust,ignore,does_not_compile
    let x: i8 = 5;
    let y: Option<i8> = Some(5);

    let sum = x + y;

```

如果我们运行这段代码，就会得到如下错误信息：

```console
$ cargo run
   Compiling enums v0.1.0 (file:///projects/enums)
error[E0277]: cannot add `Option<i8>` to `i8`
 --> src/main.rs:5:17
  |
5 |     let sum = x + y;
  |                 ^ no implementation for `i8 + Option<i8>`
  |
  = help: the trait `Add<Option<i8>>` is not implemented for `i8`
  = help: the following other types implement trait `Add<Rhs>`:
            `&i8` implements `Add<i8>`
            `&i8` implements `Add`
            `i8` implements `Add<&i8>`
            `i8` implements `Add`

For more information about this error, try `rustc --explain E0277`.
error: could not compile `enums` (bin "enums") due to 1 previous error

```

非常严重！实际上，这条错误信息意味着Rust无法理解如何添加 `i8` 和 `Option<i8>`，因为它们属于不同的类型。当我们在Rust中有一个属于 `i8` 类型的数值时，编译器会确保我们始终拥有有效的数值。因此，我们可以放心地使用该数值，无需在使用前检查它是否为null。只有当我们拥有 `Option<i8>` 类型（或任何其他类型的数值）时，才需要担心可能不存在该数值的情况，而编译器会确保在使用该数值之前处理这种情况。

换句话说，在对其进行 `T` 操作之前，你必须先将 `Option<T>` 转换为 `T`。通常，这样做有助于发现关于空值的最常见问题之一：即错误地认为某个对象不是空值，而实际上它是空值。

消除错误假设非空值的风险，有助于您更加自信地编写代码。为了允许存在可能为 null 的值，您必须通过使该值的类型满足 `Option<T>` 的条件来明确启用这一特性。因此，在使用该值时，您需要明确处理值为 null 的情况。在那些值的类型不符合 `Option<T>` 的情况下，您可以安全地假设该值不为 null。这是 Rust 的设计决策之一，旨在限制 null 的普遍性，从而提高 Rust 代码的安全性。

那么，当您有一个类型为 `Option<T>` 的值时，如何从这个 `Some` 的变体中获取 `T` 的值，以便能够使用该值呢？ `Option<T>` 枚举提供了许多在多种情况下非常有用的方法；您可以在 [其文档][docs]<!-- ignore --> 中查看这些方法的详细信息。熟悉 `Option<T>` 中的这些方法，将对您学习 Rust 的过程非常有帮助。

一般来说，为了使用 `Option<T>` 类型的值，你需要编写能够处理每种变体的代码。你还需要编写一些代码，这些代码只有在拥有 `Some(T)` 类型的值时才会运行，并且这些代码可以访问内部的 `T` 数据。另外，还需要编写一些代码，这些代码只有在拥有 `None` 类型的值时才会运行，而此时 `T` 类型的数据是无法使用的。 `match` 表达式是一种控制流结构，当与枚举类型一起使用时，它可以根据枚举中的不同变体来执行不同的代码，并且这些代码可以访问匹配值中的数据。

[IpAddr]: ../std/net/enum.IpAddr.html
[option]: ../std/option/enum.Option.html
[docs]: ../std/option/enum.Option.html
