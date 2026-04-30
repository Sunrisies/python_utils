## 使用结构体编写的一个示例程序

为了理解何时需要使用结构体，让我们编写一个计算矩形面积的程序。首先，我们将使用单个变量，然后逐步重构程序，最终使用结构体来替代单个变量。

让我们使用 Cargo 创建一个新的二进制项目，名为 _rectangles_。该项目将接收以像素为单位指定的矩形的宽度和高度，并计算出该矩形的面积。清单 5-8 展示了一个简短的程序，展示了如何在我们的项目的 _src/main.rs_ 文件中实现这一功能。

<Listing number="5-8" file-name="src/main.rs" caption="Calculating the area of a rectangle specified by separate width and height variables">

```rust
fn main() {
    let width1 = 30;
    let height1 = 50;

    println!(
        "The area of the rectangle is {} square pixels.",
        area(width1, height1)
    );
}

// ANCHOR: here
fn area(width: u32, height: u32) -> u32 {
    // ANCHOR_END: here
    width * height
}

```

</Listing>

现在，使用 `cargo run` 运行这个程序：

```console
$ cargo run
   Compiling rectangles v0.1.0 (file:///projects/rectangles)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.42s
     Running `target/debug/rectangles`
The area of the rectangle is 1500 square pixels.

```

这段代码通过调用`area`函数来计算矩形的面积，该函数需要传入每个维度的数值。不过，我们还可以采取更多措施来使这段代码更加清晰易读。

这段代码的问题在于 `area` 的签名中存在问题。

```rust,ignore
fn area(width: u32, height: u32) -> u32 {

```

`area`函数本应用于计算一个矩形的面积，但我们所编写的函数有两个参数，而且在我们的程序中没有任何地方说明这两个参数之间存在关联。将宽度和高度合并在一起会使代码更易于阅读和管理。我们已经在第三章的[“元组类型”][the-tuple-type]<!-- ignore -->部分讨论过一种实现这一功能的方法，那就是使用元组。

### 使用元组进行重构

列表5-9展示了另一个使用元组版本的我们的程序。

<Listing number="5-9" file-name="src/main.rs" caption="Specifying the width and height of the rectangle with a tuple">

```rust
fn main() {
    let rect1 = (30, 50);

    println!(
        "The area of the rectangle is {} square pixels.",
        area(rect1)
    );
}

fn area(dimensions: (u32, u32)) -> u32 {
    dimensions.0 * dimensions.1
}

```

</Listing>

从某种意义上说，这个程序更好。元组让我们增加了一些结构，现在我们只需要传递一个参数。但从另一个角度来看，这个版本不够直观：元组不会为元素命名，因此我们必须通过索引来访问元组中的各个部分，这使得我们的计算过程不够清晰。

在面积计算中，混合宽度和高度并不会产生问题，但如果我们想要在屏幕上绘制矩形，这就很重要了！我们必须记住，`width`是元组索引，而`0`和`height`则是另一个元组索引。对于其他人来说，理解这一点会更加困难，如果他们使用我们的代码，就更难以记住这些细节。因为我们没有在代码中明确说明数据的含义，所以现在更容易出现错误。

<!-- Old headings. Do not remove or links may break. -->

<a id="refactoring-with-structs-adding-more-meaning"></a>

### 使用结构体进行重构

我们使用结构体来为数据添加意义，通过为数据命名来实现。我们可以将当前使用的元组转换为一个结构体，该结构体包含整个数据的名称以及各个部分的名称，如清单5-10所示。

<Listing number="5-10" file-name="src/main.rs" caption="Defining a `Rectangle` struct">

```rust
struct Rectangle {
    width: u32,
    height: u32,
}

fn main() {
    let rect1 = Rectangle {
        width: 30,
        height: 50,
    };

    println!(
        "The area of the rectangle is {} square pixels.",
        area(&rect1)
    );
}

fn area(rectangle: &Rectangle) -> u32 {
    rectangle.width * rectangle.height
}

```

</Listing>

在这里，我们定义了一个结构体，并将其命名为 `Rectangle`。在花括号内部，我们定义了两个字段，分别为 `width` 和 `height`，这两个字段的类型都是 `u32`。接着，在 `main` 中，我们创建了一个 `Rectangle` 的特定实例，该实例的宽度为 `30`，高度为 `50`。

我们的 `area` 函数现在只有一个参数，我们将其命名为`rectangle`。该参数的类型是一个不可变的、指向结构`Rectangle`实例的借用。正如第4章中提到的，我们希望只是借用该结构，而不是拥有它。这样，`main`仍然保持所有权，可以继续使用`rect1`。这就是为什么在函数签名以及调用函数时使用了`&`的原因。

函数 `area` 访问了 `Rectangle` 实例中的 `width` 和 `height` 字段。需要注意的是，访问一个已借用结构体的字段并不会改变该字段的值，这就是为什么我们经常看到结构体被借用的情况。现在，函数 `area` 的签名清楚地表达了我们的意图：计算 `Rectangle` 的面积，使用其 `width` 和 `height` 字段。这样就能明确表示宽度和高度是相互关联的，并且为这些值提供了描述性的名称，而不是使用 `0` 和 `1` 的元组索引值。这样的设计更加清晰明了。

<!-- Old headings. Do not remove or links may break. -->

<a id="adding-useful-functionality-with-derived-traits"></a>

### 通过派生特征添加功能

在调试程序时，能够打印出 `Rectangle` 的实例，并查看其所有字段的值，这将非常有用。列表 5-11 尝试使用 [`println!` 宏][println]<!-- ignore -->，就像我们在前面章节中使用的那样。然而，这样做是行不通的。

<Listing number="5-11" file-name="src/main.rs" caption="Attempting to print a `Rectangle` instance">

```rust,ignore,does_not_compile
struct Rectangle {
    width: u32,
    height: u32,
}

fn main() {
    let rect1 = Rectangle {
        width: 30,
        height: 50,
    };

    println!("rect1 is {rect1}");
}

```

</Listing>

当我们编译这段代码时，会收到一个包含以下核心信息的错误：

```text
error[E0277]: `Rectangle` doesn't implement `std::fmt::Display`
  --> src/main.rs:12:25
   |
12 |     println!("rect1 is {rect1}");
   |                        -^^^^^-
   |                        ||
   |                        |`Rectangle` cannot be formatted with the default formatter
   |                        required by this formatting parameter
   |
   = help: the trait `std::fmt::Display` is not implemented for `Rectangle`
   = note: in format strings you may be able to use `{:?}` (or {:#?} for pretty-print) instead
   = note: this error originates in the macro `$crate::format_args_nl` which comes from the expansion of the macro `println` (in Nightly builds, run with -Z macro-backtrace for more info)

For more information about this error, try `rustc --explain E0277`.
error: could not compile `rectangles` (bin "rectangles") due to 1 previous error

```

`println!`宏可以执行多种格式处理操作。默认情况下，花括号会指示`println!`使用一种名为`Display`的格式方式，这种格式适用于直接供最终用户使用的输出。到目前为止，我们所看到的原始类型默认就是按照`Display`格式来呈现的，因为展示原始类型的方式只有一种。但是，对于结构体来说，`println!`应该如何格式化输出就变得不那么明确了，因为存在更多的显示可能性：是否要使用逗号？是否要显示花括号？是否所有字段都应该被显示？由于这种不确定性，Rust不会尝试猜测我们的需求，而且结构体并没有提供专门的实现来与`println!`和`{}`占位符一起使用。

如果我们继续阅读这些错误信息，我们会发现这条有用的提示：

```text
   |                        |`Rectangle` cannot be formatted with the default formatter
   |                        required by this formatting parameter

```

让我们试试看！现在，`println!`宏调用看起来就像`println!("rect1 is
{rect1:?}");`。在花括号内放入`:?`这个指定符，表示我们想要使用一种名为`Debug`的输出格式。`Debug`特质让我们能够以对开发者有用的方式打印我们的结构体，这样在调试代码时就能看到它的价值。

请使用这个修改后的代码进行编译。真遗憾！我们仍然遇到了错误：

```text
error[E0277]: `Rectangle` doesn't implement `Debug`
  --> src/main.rs:12:31
   |
12 |     println!("rect1 is {:?}", rect1);
   |                        ----   ^^^^^ `Rectangle` cannot be formatted using `{:?}` because it doesn't implement `Debug`
   |                        |
   |                        required by this formatting parameter
   |
   = help: the trait `Debug` is not implemented for `Rectangle`
   = note: add `#[derive(Debug)]` to `Rectangle` or manually `impl Debug for Rectangle`
   = note: this error originates in the macro `$crate::format_args_nl` which comes from the expansion of the macro `println` (in Nightly builds, run with -Z macro-backtrace for more info)
help: consider annotating `Rectangle` with `#[derive(Debug)]`
   |
 1 + #[derive(Debug)]
 2 | struct Rectangle {
   |

For more information about this error, try `rustc --explain E0277`.
error: could not compile `rectangles` (bin "rectangles") due to 1 previous error

```

不过，编译器还是给出了一些有用的提示：

```text
   |                        required by this formatting parameter
   |

```

Rust确实提供了打印调试信息的功能，但我们需要显式地启用这一功能，才能使我们的结构体能够使用这一功能。为此，我们在结构体定义之前添加了一个外部属性 `#[derive(Debug)]`，如清单5-12所示。

<Listing number="5-12" file-name="src/main.rs" caption="Adding the attribute to derive the `Debug` trait and printing the `Rectangle` instance using debug formatting">

```rust
#[derive(Debug)]
struct Rectangle {
    width: u32,
    height: u32,
}

fn main() {
    let rect1 = Rectangle {
        width: 30,
        height: 50,
    };

    println!("rect1 is {rect1:?}");
}

```

</Listing>

现在当我们运行这个程序时，就不会出现任何错误，我们会看到以下输出：

```console
$ cargo run
   Compiling rectangles v0.1.0 (file:///projects/rectangles)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.48s
     Running `target/debug/rectangles`
rect1 is Rectangle { width: 30, height: 50 }

```

不错！虽然这不是最美观的输出方式，但它能够显示该实例中所有字段的值，这在调试过程中非常有帮助。当处理更大的结构体时，拥有更易于阅读的输出会非常有用；在这种情况下，我们可以在 `println!` 字符串中使用 `{:#?}` 样式，而不是 `{:?}`。在这个示例中，使用 `{:#?}` 样式会输出以下内容：

```console
$ cargo run
   Compiling rectangles v0.1.0 (file:///projects/rectangles)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.48s
     Running `target/debug/rectangles`
rect1 is Rectangle {
    width: 30,
    height: 50,
}

```

另一种使用 `Debug` 格式打印值的方法是使用 [`dbg!`
宏][dbg]<!-- ignore -->。该宏会获取表达式的所有权（与 `println!` 不同，后者只是获取引用），打印出代码中调用 `dbg!` 宏的位置及对应的文件行号，同时还会返回该表达式的结果值。

注意：调用 `dbg!` 宏会将输出打印到标准错误控制台流中（`stderr`），而 `println!` 则会将输出打印到标准输出控制台流中（`stdout`）。我们将在《第12章》“将错误重定向到标准错误”部分进一步讨论 `stderr` 和 `stdout` 的相关内容。[err]<!-- ignore -->

以下是一个例子，其中我们感兴趣的是被赋值给`width`字段的值，以及整个struct在`rect1`中的值：

```rust
#[derive(Debug)]
struct Rectangle {
    width: u32,
    height: u32,
}

fn main() {
    let scale = 2;
    let rect1 = Rectangle {
        width: dbg!(30 * scale),
        height: 50,
    };

    dbg!(&rect1);
}

```

我们可以在表达式 `30 * scale` 周围加上 `dbg!`。由于 `dbg!` 会获取该表达式值的所有权，因此 `width` 字段将获得与没有 `dbg!` 调用时相同的数值。我们不想让 `dbg!` 获取 `rect1` 的所有权，因此在下一次调用中，我们使用对 `rect1` 的引用。这个示例的输出如下所示：

```console
$ cargo run
   Compiling rectangles v0.1.0 (file:///projects/rectangles)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.61s
     Running `target/debug/rectangles`
[src/main.rs:10:16] 30 * scale = 60
[src/main.rs:14:5] &rect1 = Rectangle {
    width: 60,
    height: 50,
}

```

我们可以看到，第一个输出结果来自 _src/main.rs_ 文件的第10行，那里我们正在调试表达式 `30 * scale`，其最终值为 `60`。对于整数来说，`Debug` 的格式化方式只是打印出它们的值而已。在 _src/main.rs_ 文件的第14行，调用了 `dbg!`，它输出的是 `&rect1` 的值，而 `&rect1` 对应的是 `Rectangle` 结构体。这个输出使用了 `Debug` 类型的漂亮格式化方式。当试图了解代码的功能时，`dbg!` 宏会非常有帮助！

除了 `Debug` 特性之外，Rust还提供了许多其他特性，这些特性可以与 `derive` 属性一起使用，从而为我们的自定义类型添加有用的功能。这些特性及其功能在[附录C][app-c]<!--
ignore -->中有详细说明。我们将在第十章中介绍如何实现这些带有自定义特性的特性，以及如何创建自己的特性。除了 `derive` 之外，还有许多其他属性；如需更多信息，请参阅Rust参考手册中的“属性”部分[attributes]。

我们的 `area` 函数非常具体：它只计算矩形的面积。  
将这种行为与我们的 `Rectangle` 结构联系起来会更有帮助，因为其他类型的数据是无法使用这个函数的。让我们看看如何通过将 `area` 函数转换为定义在 `Rectangle` 类型上的 `area` 方法，来继续重构这段代码。

[the-tuple-type]: ch03-02-data-types.html#the-tuple-type
[app-c]: appendix-03-derivable-traits.md
[println]: ../std/macro.println.html
[dbg]: ../std/macro.dbg.html
[err]: ch12-06-writing-to-stderr-instead-of-stdout.html
[attributes]: ../reference/attributes.html
