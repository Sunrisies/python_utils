## 定义枚举类型

结构体能够让你将相关的字段和数据组合在一起，比如一个`Rectangle`包含`width`和`height`。而枚举则允许我们表示一个值属于一组可能的取值之一。例如，我们可能希望表示`Rectangle`是多种可能的形状中的一种，这些形状还包括`Circle`和`Triangle`。为了实现这一点，Rust允许我们将这些可能性编码为一个枚举。

让我们来看一个可能需要在代码中表达的情况，并了解为什么在这种情况下枚举比结构体更实用且更合适。假设我们需要处理IP地址。目前，有两种主要的IP地址标准：版本四和版本六。由于这些是我们程序可能会遇到的唯一可能的IP地址形式，因此我们可以列举出所有可能的变体，这就是“枚举”名称的由来。

任何IP地址都可以是版本四或版本六的地址，但不能同时拥有这两种特性。这种IP地址的特性使得枚举数据结构变得合适，因为枚举值只能是其其中一个变体。无论是版本四还是版本六的地址，本质上都是IP地址，因此在代码处理适用于任何类型IP地址的情况时，应该将它们视为同一类型。

我们可以通过定义 ``IpAddrKind`` 枚举，并列出 IP 地址可能的类型 `V4` 和 `V6` 来用代码表达这个概念。这些是该枚举的变体：

```rust
{{#rustdoc_include ../listings/ch06-enums-and-pattern-matching/no-listing-01-defining-enums/src/main.rs:def}}
```

`IpAddrKind`现在是一种自定义数据类型，我们可以在代码的其他部分使用它。

### 枚举值

我们可以像这样创建两种变体中的每一种``IpAddrKind``的实例：

```rust
{{#rustdoc_include ../listings/ch06-enums-and-pattern-matching/no-listing-01-defining-enums/src/main.rs:instance}}
```

请注意，枚举的变体是以其标识符为前缀进行命名的，我们使用双冒号来分隔这两个部分。这样做很有用，因为现在`IpAddrKind::V4`和`IpAddrKind::V6`都是同一类型：`IpAddrKind`。然后，我们可以定义一个函数，该函数可以接受任何`IpAddrKind`作为参数。

```rust
{{#rustdoc_include ../listings/ch06-enums-and-pattern-matching/no-listing-01-defining-enums/src/main.rs:fn}}
```

我们可以以这两种方式调用这个函数：

```rust
{{#rustdoc_include ../listings/ch06-enums-and-pattern-matching/no-listing-01-defining-enums/src/main.rs:fn_call}}
```

使用枚举类型还有更多的优势。再仔细想想我们的IP地址类型，目前我们并没有办法存储实际的IP地址数据；我们只能知道它的类型。鉴于你在第5章中刚刚学习了结构体，你可能会想用结构体来解决这个问题，如清单6-1所示。

<列表编号="6-1" 标题="存储数据以及使用 `struct` 表示IP地址的 `IpAddrKind` 变体">

```rust
{{#rustdoc_include ../listings/ch06-enums-and-pattern-matching/listing-06-01/src/main.rs:here}}
```

</ Listing>

在这里，我们定义了一个名为 ``IpAddr`` 的结构体，该结构体包含两个字段：一个类型为 ``IpAddrKind`` 的字段（``kind``），以及一个类型为 ``String`` 的字段（``address``）。这个结构体有两个实例。第一个实例是 ``home``，它的 ``kind`` 字段的值为 ``IpAddrKind::V4``，并且与之关联的地址数据为 ``127.0.0.1``。第二个实例是 ``loopback``，它的 ``kind`` 字段的值为另一种类型 ``IpAddrKind`` 的变量 ``V6``，并且与之关联的地址为 ``::1``。我们使用了一个结构体来将 ``kind`` 和 ``address`` 的值组合在一起，这样现在这两个值就与同一个变量关联了。

不过，使用枚举来表示相同的概念会更加简洁：  
与其将枚举放在结构体内，我们可以直接将数据放入每个枚举的变体中。这种对`IpAddr`枚举的新定义意味着，`V4`和`V6`这两个变体都将拥有与之对应的`String`值。

```rust
{{#rustdoc_include ../listings/ch06-enums-and-pattern-matching/no-listing-02-enum-with-data/src/main.rs:here}}
```

我们直接将数据附加到枚举的每个变体上，因此不需要额外的结构体。这里还可以更清楚地看到枚举的工作原理：我们定义的每个枚举变体的名称实际上也是一个函数，该函数用于构造枚举的一个实例。也就是说，`IpAddr::V4()`是一个函数调用，它接受一个`String`类型的参数，并返回一个`IpAddr`类型的实例。当我们定义枚举时，这个构造函数函数会自动被定义为一个结果。

使用枚举而不是结构体的另一个优势是：每个变体可以拥有不同的类型以及相关的数据量。第四版IP地址总是包含四个数字组件，这些组件的值介于0到255之间。如果我们想要将`V4`地址存储为四个`u8`值，同时又能将`V6`地址表示为一个`String`值，那么使用结构体会无法实现这一点。而枚举则可以轻松处理这种情况。

```rust
{{#rustdoc_include ../listings/ch06-enums-and-pattern-matching/no-listing-03-variants-with-different-data/src/main.rs:here}}
```

我们已经展示了几种不同的方法来定义数据结构，用于存储版本四和版本六的IP地址。然而，事实证明，存储IP地址并标识其类型是非常常见的需求，以至于标准库已经提供了一个我们可以使用的定义！让我们看看标准库是如何定义`IpAddr`的。它包含了我们定义和使用的完全相同的枚举和变体，但是它将地址数据嵌入到这些变体中，并以两种不同的结构体形式呈现，每种变体对应的结构体也是不同的。

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

这段代码展示了你可以将任何类型的数据放入枚举变体中：例如字符串、数值类型或结构体。你甚至还可以包含另一个`enum!`。此外，标准库中的类型通常并不比你自己设计的类型复杂多少。

请注意，尽管标准库中包含了 ``IpAddr`` 的定义，但我们仍然可以创建并使用自己的定义，而不会引发冲突，因为我们并没有将标准库的定义引入到我们的作用域中。我们将在第七章中进一步讨论如何将类型引入作用域。

让我们来看一下清单6-2中另一个枚举的例子：这个枚举的变体中包含多种类型。

<列表编号="6-2" 标题="一个 `Message` 枚举，其各个变体分别存储不同数量和类型的数值">

```rust
{{#rustdoc_include ../listings/ch06-enums-and-pattern-matching/listing-06-02/src/main.rs:here}}
```

</ Listing>

这个枚举包含四种不同的类型：

- `Quit`: 没有任何相关数据
- `Move`: 具有命名字段，类似于结构体
- `Write`: 包含一个 `String`
- `ChangeColor`: 包含三个 `i32` 值

定义带有变体的枚举，如清单6-2中的示例，与定义不同类型的结构体类似。不过，枚举不会使用``struct``这个关键字，而且所有变体都被归类在``Message``类型下。以下的结构体可以持有与前面的枚举变体相同的数据：

```rust
{{#rustdoc_include ../listings/ch06-enums-and-pattern-matching/no-listing-04-structs-similar-to-message-enum/src/main.rs:here}}
```

但是，如果我们使用不同的结构体，每个结构体都有自己独立的类型，那么我们就无法像使用 Listing 6-2 中定义的 `Message` 枚举那样，轻松地为这些不同类型的消息定义函数了。因为 `Message` 枚举是一个单一的类型。

枚举类型和结构体之间还有一个相似之处：就像我们可以在结构体上定义使用`impl`的方法一样，我们也可以在枚举类型上定义方法。这里有一个名为`call`的方法，我们可以在我们的`Message`枚举类型上定义这个方法。

```rust
{{#rustdoc_include ../listings/ch06-enums-and-pattern-matching/no-listing-05-methods-on-enums/src/main.rs:here}}
```

该方法的主体会使用 ``self`` 来获取我们在调用该方法时传入的值。在这个例子中，我们创建了一个变量 ``m``，它的值为 `__INLINE_CODE_76`；当 ``m.call()`` 执行时，``self`` 在 ``call`` 方法的主体中就会引用到这个变量。

让我们来看看标准库中另一个非常常见且有用的枚举类型：`Option`。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="选项枚举及其相较于空值的优势"></a>

### `Option` 枚举

本节将探讨一个关于 `Option` 的案例研究。`Option` 是标准库中定义的另一个枚举类型。`Option` 类型描述了一种非常常见的场景：一个值可以是某种东西，也可以什么都不是。

例如，如果您请求一个非空列表中的第一个元素，那么你会得到一个值。而如果你请求一个空列表中的第一个元素，那么你将得不到任何东西。用类型系统来表达这个概念意味着编译器可以检查你是否处理了所有应该处理的情况；这种功能可以防止在其他编程语言中非常常见的错误。

编程语言的设计通常从所包含的功能来考虑，但被排除的功能同样重要。Rust没有许多其他语言中存在的null特性。_Null_是一个表示没有值的数值。在具有null特性的语言中，变量总是处于两种状态之一：null或非null。

在2009年的演讲《空引用：价值数十亿美元的错误》中，空引用的发明者托尼·霍尔说：

我将其称为“我的十亿美元错误”。当时，我正在为面向对象语言设计第一个全面的引用类型系统。我的目标是确保所有对引用的使用都是绝对安全的，并且由编译器自动进行安全检查。但我无法抗拒编写一个空引用这一诱惑，因为这样做非常容易实现。这导致了无数错误、漏洞以及系统崩溃，在过去四十年里，这可能造成了数十亿美元的损失和损害。

null值的问题在于，如果你试图将null值当作非null值来使用，就会引发某种错误。由于这种关于null或非null属性的情况非常普遍，因此很容易犯这样的错误。

不过，null试图表达的概念仍然很有用：null是一个当前因某种原因无效或不存在的值。

问题并不在于概念本身，而在于具体的实现方式。因此，Rust中并没有所谓的“null”值，但它有一个枚举类型，可以用来表示某个值是否存在。这个枚举类型是`Option<T>`，并且由标准库[选项]<!-- ignore -->定义如下：

```rust
enum Option<T> {
    None,
    Some(T),
}
```

`Option<T>`枚举非常有用，甚至被包含在序言中；你无需显式地将其引入作用域。它的变体也被包含在序言中：你可以直接使用`Some`和`None`，而无需使用`Option::`前缀。`Option<T>`枚举仍然只是一个普通的枚举，而`Some(T)`和`None`仍然是类型`Option<T>`的变体。

`<T>`语法是Rust中的一个特性，我们之前还没有讨论过。它是一个泛型类型参数，我们将在第十章中更详细地介绍泛型概念。目前，你需要知道的是，`<T>`表示`Option`枚举中的`Some`变体可以存储任意类型的数据，而每个实际使用的类型都会使整体`Option<T>`类型变成不同的类型。以下是一些使用`Option`值来存储数字类型和字符类型的例子：

```rust
{{#rustdoc_include ../listings/ch06-enums-and-pattern-matching/no-listing-06-option-examples/src/main.rs:here}}
```

`some_number`的类型是`Option<i32>`。而`some_char`的类型是`Option<char>`，这是一个不同的类型。Rust能够推断出这些类型，因为我们在`Some`变体中指定了一个值。对于`absent_number`来说，Rust要求我们为整个`Option`类型进行注解：编译器无法仅通过查看`None`的值来推断出相应的`Some`变体将持有什么类型。在这里，我们告诉Rust，我们希望`absent_number`具有`Option<i32>`的类型。

当我们有一个`Some`值时，我们知道存在一个值，而且这个值被存储在`Some`中。而当我们有一个`None`值时，从某种意义上讲，它和null的含义是一样的：我们没有有效的数值。那么，为什么拥有`Option<T>`会比拥有null更好呢？

简而言之，因为`Option<T>`和`T`（其中`T`可以是任何类型）是不同类型的，编译器不会允许我们将`Option<T>`的值当作一个有效的数值来使用。例如，这段代码无法编译，因为它试图将`i8`添加到`Option<i8>`上。

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch06-enums-and-pattern-matching/no-listing-07-cant-use-option-directly/src/main.rs:here}}
```

如果我们运行这段代码，就会得到如下错误信息：

```console
{{#include ../listings/ch06-enums-and-pattern-matching/no-listing-07-cant-use-option-directly/output.txt}}
```

非常严重！实际上，这条错误信息表明Rust无法理解如何添加`i8`和`Option<i8>`这两个值，因为它们属于不同的类型。在Rust中，当我们有一个像`i8`这样的类型的值时，编译器会确保我们始终拥有有效的值。因此，我们可以放心地使用这些值，无需在使用前检查它们是否为null。只有当我们遇到`Option<i8>`或其他类型的值时，才需要担心可能不存在该值的情况，此时编译器会确保在使用该值之前处理这种情况。

换句话说，在能够使用 `T` 进行操作之前，你必须先将一个 `Option<T>` 转换为 `T`。通常，这样做有助于避免最常见的空指针问题之一：错误地认为某个对象不是空指针，而实际上它确实是空指针。

消除错误假设非空值的风险，有助于您更加自信地编写代码。为了允许存在可能为空的数值，您必须通过将其类型设置为`Option<T>`来明确启用该特性。因此，在使用该值时，您需要显式地处理值为空的情况。只要某个值的类型不是`Option<T>`，就可以放心地假设该值不为空。这是Rust的一项刻意设计决策，旨在限制空值的普遍性，从而提高Rust代码的安全性。

那么，如何从一个类型为 `Some` 的变量中获取 `T` 的值呢？如果你有一个类型为 `Option<T>` 的值，那么你就可以使用这个值了。`Option<T>` 枚举包含了许多在多种情况下非常有用的方法；你可以在[其文档][docs]中查看这些方法。熟悉 `Option<T>` 上的方法将对你学习 Rust 非常有帮助。

一般来说，为了使用`Option<T>`这个值，你需要编写一些代码来处理每一种情况。你还需要一些代码，这些代码只有在拥有`Some(T)`这个值时才会运行，而且这些代码可以访问内部的`T`数据。另外，还有一些代码只有在拥有`None`这个值时才会运行，而此时`None`无法访问`T`的数据。`match`是一个控制流结构，当与枚举类型一起使用时，它可以根据枚举中的不同值来执行不同的代码，并且这些代码可以访问匹配值内的数据。

[IpAddr]:../std/net/enum.IpAddr.html  
[option]:../std/option/enum.Option.html  
[docs]:../std/option/enum.Option.html