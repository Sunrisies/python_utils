## 使用结构体编写的一个示例程序

为了理解何时需要使用结构体，让我们编写一个计算矩形面积的程序。首先，我们将使用单个变量，然后逐步重构程序，最终使用结构体来替代它们。

让我们使用Cargo创建一个新的二进制项目，名为`_rectangles_`。该项目将接收以像素为单位指定的矩形的宽度和高度，然后计算该矩形的面积。清单5-8展示了一个简短的程序，展示了如何在我们的项目的`_src/main.rs_`中实现这一功能。

<列表编号="5-8" 文件名称="src/main.rs" 标题="使用独立的宽度和高度变量计算矩形的面积">

```rust
{{#rustdoc_include ../listings/ch05-using-structs-to-structure-related-data/listing-05-08/src/main.rs:all}}
```

</ Listing>

现在，使用 `cargo run` 运行这个程序：

```console
{{#include ../listings/ch05-using-structs-to-structure-related-data/listing-05-08/output.txt}}
```

这段代码通过调用`area`函数并将每个维度的数值作为参数传入，成功计算出了矩形的面积。不过，我们还可以采取更多措施来使这段代码更加清晰易读。

这段代码的问题在于 `area` 的签名中体现出来的问题。

```rust,ignore
{{#rustdoc_include ../listings/ch05-using-structs-to-structure-related-data/listing-05-08/src/main.rs:here}}
```

`area`这个函数应该是用来计算一个矩形的面积的，但是我们所写的这个函数有两个参数，而且在我们程序的任何地方都没有明确说明这两个参数是有关系的。将宽度和高度合并在一起会使代码更易于阅读和管理。我们已经在第三章的“元组类型”部分讨论过一种实现这一功能的方法，那就是使用元组。

### 使用元组进行重构

清单5-9展示了另一个使用元组版本的我们的程序。

<列表编号="5-9" 文件名称="src/main.rs" 标题="使用元组指定矩形的宽度和高度">

```rust
{{#rustdoc_include ../listings/ch05-using-structs-to-structure-related-data/listing-05-09/src/main.rs}}
```

</ Listing>

从某种意义上说，这个程序更好。元组让我们增加了一些结构感，现在我们只需要传递一个参数。但从另一个角度来看，这个版本不够直观：元组不会为元素命名，因此我们必须通过索引来访问元组中的各个部分，这使得我们的计算过程不够清晰。

在面积计算中，混合宽度和高度并不会产生问题，但如果我们想要在屏幕上绘制矩形，这就很重要了！我们必须记住，`width`是元组中的索引，而`0`和`height`则是元组中的其他索引。对于其他人来说，理解这一点会更加困难，如果他们使用我们的代码的话，就更难记住这些细节了。因为我们没有在代码中明确说明数据的含义，所以现在更容易引入错误。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="重构结构体以增添更多意义"></a>

### 使用结构体进行重构

我们使用结构体来为数据添加意义，通过为数据贴上标签来实现。我们可以将当前使用的元组转换为一个结构体，该结构体包含整个数据的名称以及各个部分的名称，如清单5-10所示。

<listing number="5-10" file-name="src/main.rs" caption="定义 `Rectangle` 结构体">

```rust
{{#rustdoc_include ../listings/ch05-using-structs-to-structure-related-data/listing-05-10/src/main.rs}}
```

</ Listing>

在这里，我们定义了一个结构体，并将其命名为`Rectangle`。在花括号内，我们定义了两个字段，分别为`width`和`height`，这两个字段的类型都是`u32`。然后，在`main`中，我们创建了一个特定实例的`Rectangle`，该实例的宽度为`30`，高度为`50`。

我们的 ``area`` 函数现在定义了一个参数，我们将其命名为 ``rectangle``。该参数的类型是一个不可变的、对结构体 ``Rectangle`` 实例的借用。正如第4章中提到的，我们希望只是借用这个结构体，而不是拥有它。这样，``main`` 仍然保持自己的所有权，可以继续使用 `__INLINE_CODE_36`。这就是为什么我们在函数签名中使用 ``&`` 来调用这个函数的原因。

`area`函数访问了`Rectangle`实例中的`width`和`height`字段（需要注意的是，访问一个已借用结构体的字段并不会移动该字段的值，这就是为什么经常看到结构体被借用的情况）。我们现在对`area`的函数签名明确表示了我们的意图：计算`Rectangle`的面积，使用其`width`和`height`字段。这样就能清楚地表明宽度和高度是相互关联的，并且为这些值提供了描述性的名称，而不是使用`0`和`1`的元组索引值。这样的设计确实提高了代码的可读性。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="通过派生特性添加实用功能"></a>

### 通过派生特征添加功能

在调试程序时，能够打印出`Rectangle`的实例，并查看其所有字段的值，这将非常有用。清单5-11中尝试使用[`println!`宏][println]<!-- ignore -->，就像我们在前面章节中使用的那样。不过，这样做是行不通的。

<列表编号="5-11" 文件名称="src/main.rs" 标题="尝试打印一个 `Rectangle` 实例">

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch05-using-structs-to-structure-related-data/listing-05-11/src/main.rs}}
```

</ Listing>

当我们编译这段代码时，会收到一个包含以下核心信息的错误：

```text
{{#include ../listings/ch05-using-structs-to-structure-related-data/listing-05-11/output.txt:3}}
```

`println!`宏可以执行多种格式化操作。默认情况下，大括号会指示`println!`使用一种名为`Display`的格式化方式：这种格式化的内容是为直接供最终用户使用的。到目前为止，我们所看到的原始类型默认都实现了`Display`格式，因为展示`1`或其他原始类型的方式只有一种。但是，对于结构体来说，`println!`应该如何格式化输出就变得不那么明确了，因为存在更多的显示可能性：是否要使用逗号？是否要显示大括号？所有字段是否都应该被显示？由于这种不确定性，Rust不会尝试猜测我们的需求，而且结构体并没有提供专门的实现来与`println!`以及`{}`占位符一起使用。

如果我们继续阅读这些错误信息，我们会发现这条有用的提示：

```text
{{#include ../listings/ch05-using-structs-to-structure-related-data/listing-05-11/output.txt:9:10}}
```

让我们试试看！现在，``println!``宏的调用看起来像这样：`println!("rect1 is {rect1:?}");`. Putting the specifier `:?`。大括号内的内容告诉``println!``我们想要使用一个名为``Debug``的输出格式。``Debug``特性使我们能够以对开发者有用的方式打印我们的结构体，这样在调试代码时我们就可以看到其值。

请使用这个修改后的代码进行编译。真遗憾！我们仍然遇到了错误：

```text
{{#include ../listings/ch05-using-structs-to-structure-related-data/output-only-01-debug/output.txt:3}}
```

不过，编译器还是给出了一个有用的提示：

```text
{{#include ../listings/ch05-using-structs-to-structure-related-data/output-only-01-debug/output.txt:9:10}}
```

Rust确实提供了打印调试信息的功能，但我们需要显式地启用这一功能，才能使我们的结构体能够使用这一功能。为此，我们在结构体的定义之前添加了一个外部属性 ``#[derive(Debug)]``，如清单5-12所示。

<listing number="5-12" file-name="src/main.rs" caption="添加属性以派生 `Debug` 特质，并使用调试格式打印 `Rectangle` 实例">

```rust
{{#rustdoc_include ../listings/ch05-using-structs-to-structure-related-data/listing-05-12/src/main.rs}}
```

</ Listing>

现在当我们运行这个程序时，就不会遇到任何错误了，我们会看到如下输出：

```console
{{#include ../listings/ch05-using-structs-to-structure-related-data/listing-05-12/output.txt}}
```

不错！虽然这不是最美观的输出方式，但它能够显示该实例中所有字段的值，这在调试过程中非常有帮助。当我们处理更大的结构体时，拥有更易于阅读的输出会很有用；在这种情况下，我们可以在 `println!` 字符串中使用 `{:#?}` 而不是 `{:?}`。在这个示例中，使用 `{:#?}` 风格将会输出以下内容：

```console
{{#include ../listings/ch05-using-structs-to-structure-related-data/output-only-02-pretty-debug/output.txt}}
```

另一种使用 ``Debug`` 格式打印值的方法是使用 [`dbg!`macro][dbg]<!-- 忽略 -->。该宏会接管某个表达式的所有权（与接受引用的 `println!` 不同），并打印出该宏在代码中调用的位置以及该表达式的结果值，同时返回该值的所有权。

注意：调用 ``dbg!`` 宏会将输出打印到标准错误控制台流中；而 ``stderr`` 则会将输出打印到标准输出控制台流中。至于 ``println!``，它也会将输出打印到标准输出控制台流中。我们将在《第12章》的[“将错误重定向到标准错误”部分][err]中进一步讨论 ``stderr`` 和 ``stdout`` 的功能。

以下是一个例子，其中我们感兴趣的是被赋值给`width`字段的值，以及整个结构体在`rect1`中的值：

```rust
{{#rustdoc_include ../listings/ch05-using-structs-to-structure-related-data/no-listing-05-dbg-macro/src/main.rs}}
```

我们可以在表达式 `30 * scale` 周围加上 `dbg!`。由于 `dbg!` 会返回该表达式值的所有权，因此 `width` 字段将获得与没有 `dbg!` 的情况相同的数值。我们不想让 `dbg!` 获得 `rect1` 的所有权，因此在下一次调用中使用了对 `rect1` 的引用。这个示例的输出如下所示：

```console
{{#include ../listings/ch05-using-structs-to-structure-related-data/no-listing-05-dbg-macro/output.txt}}
```

我们可以看到，第一个输出结果来自 _src/main.rs_ 文件的第10行，那里我们正在调试表达式 `30 * scale`，其最终值就是 `60`。（整数类型的 `Debug` 格式只是打印出它们的值。）在 _src/main.rs_ 文件的第14行，对 `dbg!` 的调用会输出 `&rect1` 的值，而 `&rect1` 正是 `Rectangle` 结构体的实例。这个输出使用了 `Rectangle` 类型的漂亮 `Debug` 格式。当你试图了解代码的功能时，`dbg!` 宏会非常有帮助！

除了`Debug`特质之外，Rust还提供了许多其他特质，这些特质可以与`derive`属性一起使用，从而为我们的自定义类型增添有用的功能。这些特质及其功能在[附录C][app-c]中有详细说明。我们将在第10章中介绍如何实现这些带有自定义功能的特质，以及如何创建自己的特质。除了`derive`之外，还有许多其他属性；如需更多信息，请参阅Rust参考手册中的“属性”部分。[attributes]

我们的 ``area`` 函数非常具体：它只计算矩形的面积。  
将这种行为与我们的 ``Rectangle`` 结构体更紧密地联系起来会很有帮助，因为其他类型的数据是无法使用这个函数的。让我们看看如何通过将 ``area`` 函数重构为定义在 ``Rectangle`` 类型上的 ``area`` 方法，来继续重构这段代码。

[元组类型]: ch03-02-data-types.html#the-tuple-type  
[应用程序]: appendix-03-derivable-traits.md  
[println]:../std/macro.println.html  
[dbg]:../std/macro.dbg.html  
[err]: ch12-06-writing-to-stderr-instead-of-stdout.html  
[属性]:../reference/attributes.html