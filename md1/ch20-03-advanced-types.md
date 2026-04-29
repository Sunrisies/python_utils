## 高级类型

Rust的类型系统有一些我们之前提到但尚未详细讨论的特性。首先，我们将总体介绍新类型，探讨它们作为类型的实用性。接着，我们会讨论类型别名，这是一种与新类型类似但语义略有不同的特性。此外，我们还会讨论`!`类型以及动态大小的类型。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="使用新类型模式来实现类型安全和抽象"></a>

### 使用Newtype模式实现类型安全和抽象

本节假设您已经阅读了前面的章节[“使用Newtype模式实现外部特质”][newtype]。Newtype模式对于超出我们目前讨论范围的任务也非常有用，比如确保值不会被混淆，以及指定值的单位。您在Listing 20-16中看到了使用Newtype来表示单位的例子：请注意，`Millimeters`和`Meters`结构体将`u32`的值封装在一个新类型中。如果我们编写一个参数为`Millimeters`类型的函数，那么我们就无法编译出一个程序，该程序可能会错误地尝试使用`Meters`或普通的`u32`类型的值来调用该函数。

我们还可以使用新类型模式来抽象出某个类型的某些实现细节：新类型可以暴露出一个与私有内部类型不同的公共API。

新类型还可以隐藏内部实现。例如，我们可以提供一个`People`类型来封装一个`HashMap<i32, String>`，该`HashMap<i32, String>`用于存储一个人的ID以及他们的名字。使用`People`的代码只会与我们所提供的公共API进行交互，比如将名字字符串添加到`People`集合中的方法；这样的代码不需要知道我们会在内部为名字分配`i32`类型的ID。新类型模式是一种轻量级的方式，可以用来隐藏实现细节，我们在第18章的[“隐藏实现细节的封装”][encapsulation-that-hides-implementation-details]章节中讨论过这一点。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="如何创建类型别名和类型同义词"></a>

### 类型同义词与类型别名

Rust允许我们声明一个类型别名，以便给现有的类型起另一个名字。为此，我们可以使用`type`这个关键字。例如，我们可以创建别名`Kilometers`来代表`i32`，如下所示：

```rust
{{#rustdoc_include ../listings/ch20-advanced-features/no-listing-04-kilometers-alias/src/main.rs:here}}
```

现在，别名 ``Kilometers`` 是 ``i32`` 的一个_同义词_；与我们在 Listing 20-16 中创建的 ``Millimeters`` 和 ``Meters`` 不同，``Kilometers`` 并不是一个独立的、新的类型。具有类型 ``Kilometers`` 的值将被视为与类型 ``i32`` 的值相同。

```rust
{{#rustdoc_include ../listings/ch20-advanced-features/no-listing-04-kilometers-alias/src/main.rs:there}}
```

因为 ``Kilometers`` 和 ``i32`` 是相同类型的，我们可以同时赋予这两种类型的值，并且可以将 ``Kilometers`` 的值传递给那些接受 ``i32`` 参数的函数。然而，使用这种方法，我们无法享受到之前讨论过的新类型模式所带来的类型检查优势。换句话说，如果我们在某些地方混淆了 ``Kilometers`` 和 ``i32`` 的值，编译器不会给我们报错。

类型同义词的主要用途是减少重复。例如，我们可能会有一个像这样的长类型：

```rust,ignore
Box<dyn Fn() + Send + 'static>
```

在函数的签名中以及代码的各个位置都编写如此长的类型信息，既繁琐又容易出错。想象一下，如果项目里充满了像清单20-25那样的代码，那该有多麻烦。

<列表编号="20-25" 标题="在多个地方使用长类型">

```rust
{{#rustdoc_include ../listings/ch20-advanced-features/listing-20-25/src/main.rs:here}}
```

</ Listing>

类型别名通过减少重复代码来使代码更加易于管理。在清单20-26中，我们为冗长的类型引入了一个别名`Thunk`，并且可以将所有对该类型的引用替换为更简短的别名`Thunk`。

<listing number="20-26" caption="介绍一个类型别名 `Thunk`，以减少重复劳动">

```rust
{{#rustdoc_include ../listings/ch20-advanced-features/listing-20-26/src/main.rs:here}}
```

</ Listing>

这段代码更容易阅读和理解！为类型别名选择一个有意义的名称，也有助于传达你的意图。（_thunk_这个词表示代码将在稍后的时间被执行，因此它是一个适合用于存储闭包的合适名称。）

类型别名也常用于 `Result<T, E>` 类型，以减少重复代码。以标准库中的 `std::io` 模块为例，I/O 操作通常会返回一个 `Result<T, E>` 来处理操作失败的情况。该库中有一个 `std::io::Error` 结构体，用于表示所有可能的 I/O 错误。在 `std::io` 中的许多函数都会返回 `Result<T, E>`，其中 `E` 就是 `std::io::Error`。例如，在 `Write` 特质中的这些函数：

```rust,noplayground
{{#rustdoc_include ../listings/ch20-advanced-features/no-listing-05-write-trait/src/lib.rs}}
```

`Result<..., Error>`被多次重复出现。因此，`std::io`有这样的类型别名声明：

```rust,noplayground
{{#rustdoc_include ../listings/ch20-advanced-features/no-listing-06-result-alias/src/lib.rs:here}}
```

由于这个声明位于 ``std::io`` 模块中，我们可以使用完全限定的别名 ``std::io::Result<T>``；也就是说，使用 ``Result<T, E>``，其中 ``E`` 被填充为 ``std::io::Error``。而 ``Write`` 的 trait 函数签名最终看起来是这样的：

```rust,noplayground
{{#rustdoc_include ../listings/ch20-advanced-features/no-listing-06-result-alias/src/lib.rs:there}}
```

类型别名有两大作用：它使得代码更易于编写，同时还能在整个`std::io`中提供一致的接口。由于它是一个别名，因此它实际上也是另一个`Result<T, E>`。这意味着我们可以使用所有适用于`Result<T, E>`的方法，以及像`?`运算符这样的特殊语法。

### 永不返回值的类型

Rust 有一种特殊的类型，名为 ``!``，在类型理论术语中被称为“空类型”，因为它没有任何值。我们更倾向于将其称为“永远类型”，因为当某个函数永远不会返回值时，这个类型就代表了函数的返回类型。以下是一个示例：

```rust,noplayground
{{#rustdoc_include ../listings/ch20-advanced-features/no-listing-07-never-type/src/lib.rs:here}}
```

这段代码的意思是：“函数`bar`永远不会返回任何值。”那些永远不返回值的函数被称为“发散函数”。我们无法创建类型为`!`的值，因此`bar`永远不可能返回任何值。

但是，一个永远无法创建值的类型有什么用呢？回想一下清单2-5中的代码，这部分内容属于数字猜谜游戏的一部分；我们在清单20-27中复制了其中的一部分。

<列表编号="20-27" 标题="一个包含分支的`match`，该分支的终点为`continue`">

```rust,ignore
{{#rustdoc_include ../listings/ch02-guessing-game-tutorial/listing-02-05/src/main.rs:ch19}}
```

</ Listing>

当时，我们省略了这段代码中的一些细节。在第六章的[“`match`控制流构造体”][the-match-control-flow-construct]这一节中，我们讨论了`match`参数必须返回相同的类型。因此，例如，以下代码是无效的：

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch20-advanced-features/no-listing-08-match-arms-different-types/src/main.rs:here}}
```

在这段代码中，`guess`的类型必须同时是整型和一个字符串类型。而Rust要求`guess`只能有一种类型。那么，`continue`到底返回了什么？我们如何能够在一个分支中返回`u32`，同时另一个分支以`continue`结束呢？在Listing 20-27中可以看到这一点。

正如你可能已经猜到的那样，`continue`具有`!`的值。也就是说，当Rust计算`guess`的类型时，它会考虑两个匹配项：前者的值为`u32`，后者的值为`!`。由于`!`永远不可能有值，因此Rust认为`guess`的类型是`u32`。

这种行为的正式描述是：类型为 ``!`` 的表达式可以被强制转换为任何其他类型。我们可以在 `match` 处以 `continue` 结束，因为 `continue` 并不返回任何值；相反，它会将控制权返回到循环的顶部。因此，在 `Err` 的情况下，我们永远不会向 `guess` 赋值任何值。

“never type”这个类型在`panic!`宏中也非常有用。还记得那个`unwrap`函数吗？我们通过`Option<T>`参数来调用这个函数，从而生成某个值或者引发panic。

```rust,ignore
{{#rustdoc_include ../listings/ch20-advanced-features/no-listing-09-unwrap-definition/src/lib.rs:here}}
```

在这段代码中，发生的情况与清单20-27中的`match`相同：Rust会检测到`val`的类型为`T`，而`panic!`的类型为`!`。因此，整个`match`表达式的结果就是`T`。这段代码之所以有效，是因为`panic!`不会产生任何值；它只是终止了程序。在`None`的情况下，我们不会从`unwrap`返回任何值，所以这段代码也是有效的。

最后一个具有类型 ``!`` 的表达式是一个循环：

```rust,ignore
{{#rustdoc_include ../listings/ch20-advanced-features/no-listing-10-loop-returns-never/src/main.rs:here}}
```

在这里，循环永远不会结束，所以`!`就是该表达式的值。不过，如果我们包含`break`的话，情况就不一样了，因为循环会在到达`break`时终止。

### 动态大小类型与`Sized`特性

Rust需要了解其类型的某些细节，比如为特定类型的值分配多少内存。这使得其类型系统在最初时有一个令人困惑的方面：即所谓“动态大小类型”的概念。这类类型有时也被称为“DSTs”或“无大小类型”，它们允许我们编写代码，使用那些在运行时才能确定大小的值。

让我们详细了解一下名为`str`的动态大小类型，我们在整本书中一直都在使用它。没错，不是`&str`，而是单独的`str`。这是一种动态字符串类型。在许多情况下，比如存储用户输入的文本时，我们无法在运行时知道字符串的具体长度。这意味着我们无法创建类型为`str`的变量，也无法接受类型为`str`的参数。考虑以下这段代码，它是不工作的：

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch20-advanced-features/no-listing-11-cant-create-str/src/main.rs:here}}
```

Rust需要知道为特定类型的任何值分配多少内存，并且所有该类型的值必须使用相同数量的内存。如果Rust允许我们这样编写代码，那么这两个`str`值的占用空间就会相同。但实际上它们有不同的长度：`s1`需要12个字节的存储空间，而`s2`则需要15个字节。这就是为什么无法创建一个存储动态大小类型的变量的原因。

那么，我们该怎么办呢？在这种情况下，答案你已经知道了：我们应该将`s1`和`s2`的类型定义为字符串切片（即`&str`），而不是`str`。回想一下第4章中的[“字符串切片”][string-slices]<!-- ignore -->部分，切片数据结构只存储切片的起始位置和长度。因此，虽然`&T`只是一个存储`T`所在内存地址的值，但字符串切片实际上是由两个值构成的：`str`的地址以及它的长度。这样一来，我们可以在编译时知道字符串切片的大小：它是`usize`长度的两倍。也就是说，无论所引用的字符串有多长，我们总能知道字符串切片的大小。通常来说，这就是Rust中动态大小类型的使用方式：它们会额外携带一些元数据，用来存储动态信息的大小。动态大小类型的黄金法则是：我们必须总是将动态大小类型的值放在某种指针之后。

我们可以将 ``str`` 与各种指针结合使用：例如，``Box<str>`` 或 ``Rc<str>``。实际上，你之前已经见过这种情况，只不过当时使用的是一种动态大小的类型——特质。每个特质都是一种动态大小的类型，我们可以通过该特质的名称来引用它。在《第18章：使用特质对象来抽象共享行为》这一节中，我们提到过，要将特质作为特质对象使用，必须将其放在一个指针之后，比如 ``&dyn Trait``，或者 `Box<dyn Trait>` (`` 也是可行的。`Rc<dyn Trait>` 同样适用。

为了与动态尺寸类型（DSTs）进行交互，Rust提供了`Sized`特质，用于确定某个类型的尺寸是否在编译时已知。这个特质会自动应用于所有在编译时已知尺寸的实体。此外，Rust还会隐式地为每个泛型函数添加`Sized`的边界限制。也就是说，像这样的泛型函数定义：

```rust,ignore
{{#rustdoc_include ../listings/ch20-advanced-features/no-listing-12-generic-fn-definition/src/lib.rs}}
```

实际上，它会被当作是我们自己写的那样来处理。

```rust,ignore
{{#rustdoc_include ../listings/ch20-advanced-features/no-listing-13-generic-implicit-sized-bound/src/lib.rs}}
```

默认情况下，泛型函数仅适用于在编译时已知大小的类型。但是，您可以使用以下特殊语法来放宽这一限制：

```rust,ignore
{{#rustdoc_include ../listings/ch20-advanced-features/no-listing-14-generic-maybe-sized/src/lib.rs}}
```

在 ``?Sized`` 上定义的特性意味着“`T` 可能是也可能是不是 `Sized`”，这种表示方式覆盖了通用类型在编译时必须有已知大小的默认规定。具有这种意义的 `?Trait` 语法仅适用于 `Sized`，而不适用于其他任何特性。

另外需要注意的是，我们将 `t` 参数的类型从 `T` 更改为 `&T`。由于该类型可能并不属于 `Sized` 的类型，因此我们需要通过某种指针来引用它。在这种情况下，我们选择了使用引用。

接下来，我们将讨论函数和闭包！

[封装——隐藏实现细节]: ch18-01-what-is-oo.html#encapsulation-that-hides-implementation-details
[字符串切片]: ch04-03-slices.html#string-slices
[匹配控制流结构]: ch06-02-match.html#the-match-control-flow-construct
[使用特质对象来抽象共享行为]: ch18-02-trait-objects.html#using-trait-objects-to-abstract-over-shared-behavior
[新类型]: ch20-02-advanced-traits.html#implementing-external-traits-with-the-newtype-pattern