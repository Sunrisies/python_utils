<!-- Old headings. Do not remove or links may break. -->

<a id="using-trait-objects-that-allow-for-values-of-different-types"></a>

## 使用特质对象来抽象共享行为

在第八章中，我们提到向量的一个局限性是它们只能存储单一类型的数据。我们在 Listing 8-9 中创建了一个解决方案，定义了一个 `SpreadsheetCell` 枚举类型，该枚举类型可以存储整数、浮点数以及文本。这意味着我们可以在每个单元格中存储不同类型的数据，同时仍然使向量能够表示一行的单元格。当我们的可互换项是一组固定的数据类型，并且我们知道代码在编译后的行为时，这是一个非常有效的解决方案。

然而，有时候我们希望我们的库用户能够扩展在特定情况下有效的类型集合。为了展示如何实现这一点，我们将创建一个示例图形用户界面工具，该工具会遍历一个项目列表，并对每个项目调用一个 `draw` 方法，将其绘制到屏幕上——这是图形用户界面工具中的一种常见技术。我们将创建一个名为 `gui` 的库 crate，其中包含图形用户界面库的结构。这个库可能会包含一些供人们使用的类型，例如 `Button` 或 `TextField`。此外，`gui` 用户还希望创建自己可以绘制的类型：例如，一位程序员可能会添加 `Image`，另一位程序员可能会添加 `SelectBox`。

在编写这个库的时候，我们无法预知和定义所有其他程序员可能想要创建的类型。但我们确实知道， `gui` 需要跟踪许多不同类型的数值，并且需要对这些不同类型的数值分别调用 `draw` 方法。它不需要确切知道当我们调用 `draw` 方法时会发生什么，只需要知道该数值拥有可以调用的该方法即可。

为了在具有继承功能的语言中实现这一点，我们可以定义一个名为`Component`的类，该类包含一个名为`draw`的方法。其他类，如`Button`、`Image`和`SelectBox`，将继承自`Component`，从而继承`draw`方法。这些类可以各自覆盖`draw`方法，以定义它们自己的自定义行为。不过，该框架可以将所有类型视为`Component`实例，并调用`draw`方法。但由于Rust没有继承功能，我们需要另一种方式来构建`gui`库，以允许用户创建与库兼容的新类型。

### 定义具有通用行为的特质

为了实现我们希望 `gui` 具有的行为，我们将定义一个名为 `Draw` 的特质，该特质将包含一个名为 `draw` 的方法。然后，我们可以定义一个接受特质对象的向量。一个 _特质对象_ 指向实现我们指定特质的一个类型实例，以及用于在运行时查找该类型上特质方法的表格。我们通过指定某种指针来创建特质对象，例如引用或 `Box<T>` 智能指针，然后加上 `dyn` 关键字，最后指定相关的特质。（我们将在第20章中讨论特质对象必须使用指针的原因。）我们可以使用特质对象来代替通用或具体类型。无论我们在何处使用特质对象，Rust的类型系统都会在编译时确保在该上下文中使用的任何值都实现了特质对象的特质。因此，我们不需要在编译时知道所有可能的类型。

我们已经提到，在Rust中，我们避免将结构体（structs）和枚举（enums）称为“对象”，以将其与其他语言的“对象”区分开来。在结构体或枚举中，结构体字段中的数据和行为是分开的，而在其他语言中，数据和行为被合并为一个概念，通常被称为对象。与其他语言的“对象”相比，特质对象（trait objects）的不同之处在于，我们无法向特质对象添加数据。特质对象并不像其他语言的“对象”那样常用：它们的具体用途是允许对共同行为进行抽象处理。

清单 18-3 展示了如何定义一个名为 `Draw` 的 trait，并为其定义了一个名为 `draw` 的方法。

**清单 18-3:** *src/lib.rs* — `Draw` 特性的定义

```rust,noplayground
pub trait Draw {
    fn draw(&self);
}

```

这种语法结构应该与我们在第10章中关于如何定义特性的讨论很相似。接下来是一些新的语法结构：清单18-4定义了一个名为`Screen`的结构体，该结构体包含一个名为`components`的向量。这个向量的类型是`Box<dyn Draw>`，它是一个特性对象；它代表了在实现了`Draw`特性的`Box`中的任何类型。

**清单 18-4:** *src/lib.rs* — 定义了一个 `Screen` 结构体，该结构体包含一个 `components` 字段，该字段持有一个实现了 `Draw`  trait 的 trait 对象的向量。

```rust,noplayground
pub struct Screen {
    pub components: Vec<Box<dyn Draw>>,
}

```

在 `Screen` 结构体中，我们将定义一个名为 `run` 的方法，该方法会调用其每个 `components` 中的 `draw` 方法，如清单 18-5 所示。

**清单 18-5:** *src/lib.rs* — 一个在 `Screen` 上的 `run` 方法，该方法会调用每个组件上的 `draw` 方法

```rust,noplayground
impl Screen {
    pub fn run(&self) {
        for component in self.components.iter() {
            component.draw();
        }
    }
}

```

这与使用带有 trait 界限的泛型类型来定义结构体有所不同。泛型类型参数一次只能被替换为一种具体类型，而 trait 对象则允许在运行时用多种具体类型来替代 trait 对象。例如，我们可以使用一个泛型类型和一个 trait 界限来定义 `Screen` 结构体，如 Listing 18-6 所示。

**清单 18-6:** *src/lib.rs* — 使用泛型和特质约束的 `Screen` 结构及其 `run` 方法的另一种实现方式

```rust,noplayground
pub struct Screen<T: Draw> {
    pub components: Vec<T>,
}

impl<T> Screen<T>
where
    T: Draw,
{
    pub fn run(&self) {
        for component in self.components.iter() {
            component.draw();
        }
    }
}

```

这限制了我们只能使用具有类型为 `Button` 或 `TextField` 的组件列表的 `Screen` 实例。如果你只能处理同质集合，那么使用泛型和特质约束更为理想，因为定义会在编译时被单态化，从而使用具体的类型。

另一方面，使用 trait 对象的方法时，一个 `Screen` 实例可以包含一个 `Vec<T>`，而 `Vec<T>` 又包含一个 `Box<Button>` 以及一个 `Box<TextField>`。让我们来看看这是如何工作的，然后我们再讨论一下对运行时性能的影响。

### 实现特质

现在，我们将添加一些实现了 `Draw` 特性的类型。我们将提供 `Button` 类型。需要注意的是，实际上实现一个 GUI 库超出了本书的范围，因此 `draw` 方法在其实现中并不会包含任何有用的功能。为了想象一下这个实现可能的样子，一个 `Button` 结构可能会包含 `width`、 `height` 和 `label` 字段，如清单 18-7 所示。

**清单 18-7:** *src/lib.rs* — 一个实现了 `Draw`  trait 的 `Button` 结构体

```rust,noplayground
pub struct Button {
    pub width: u32,
    pub height: u32,
    pub label: String,
}

impl Draw for Button {
    fn draw(&self) {
        // code to actually draw a button
    }
}

```

在 `Button` 上的 `width`、 `height` 和 `label` 字段将与其他组件上的字段有所不同；例如，一个 `TextField` 类型可能包含相同的字段，同时还包含一个 `placeholder` 字段。我们想要在屏幕上显示的每种类型都会实现 `Draw` 特性，但在 `draw` 方法中会使用不同的代码来定义如何绘制该特定类型，正如 `Button` 在这里所做的（如前面提到的，没有实际的 GUI 代码）。例如， `Button` 类型可能还包含一个 `impl` 块，其中包含了与用户点击按钮时发生的事件相关的方法。这些方法并不适用于像 `TextField` 这样的类型。

如果有人使用我们的库来实现一个具有 `width`、`height` 和 `options` 字段的 `Draw` 结构，那么他们还需要在 `SelectBox` 类型上实现 `Draw` 特性，如清单 18-8 所示。

**清单 18-8:** *src/main.rs* — 另一个使用 `gui` 并在 `SelectBox` 结构上实现 `Draw` 特性的 crate

```rust,ignore
use gui::Draw;

struct SelectBox {
    width: u32,
    height: u32,
    options: Vec<String>,
}

impl Draw for SelectBox {
    fn draw(&self) {
        // code to actually draw a select box
    }
}

```

我们的库的用户现在可以编写他们的 `main` 函数来创建一个 `Screen` 实例。对于该 `Screen` 实例，他们可以通过将 `SelectBox` 和 `Button` 分别放入 `Box<T>` 中，从而创建一个 trait 对象。然后，他们可以调用 `Screen` 实例上的 `run` 方法，该方法会分别调用每个组件上的 `draw`。清单 18-9 展示了这种实现。

**清单 18-9:** *src/main.rs* — 使用特征对象来存储实现了相同特征的不同类型的值

```rust,ignore
use gui::{Button, Screen};

fn main() {
    let screen = Screen {
        components: vec![
            Box::new(SelectBox {
                width: 75,
                height: 10,
                options: vec![
                    String::from("Yes"),
                    String::from("Maybe"),
                    String::from("No"),
                ],
            }),
            Box::new(Button {
                width: 50,
                height: 10,
                label: String::from("OK"),
            }),
        ],
    };

    screen.run();
}

```

在编写这个库的时候，我们并不知道可能会有人添加`SelectBox`这种类型，但我们的`Screen`实现能够操作这种新类型并对其进行操作，因为`SelectBox`实现了`Draw`特征，这意味着它也实现了`draw`方法。

这个概念——只关注一个值所响应的消息，而不是该值的具体类型——类似于动态类型语言中的“鸭子类型”概念：如果某个对象的行为像鸭子，叫声也像鸭子，那么它就一定是鸭子！在清单18-5中实现 `run` 对 `Screen` 的操作时， `run` 不需要知道每个组件的具体类型。它不会检查某个组件是 `Button` 的实例还是 `SelectBox` 的实例，而只是调用组件上的 `draw` 方法。通过指定 `Box<dyn Draw>` 作为 `components` 向量中值的类型，我们定义了 `Screen`，使其需要的是我们可以调用 `draw` 方法的对象。

使用特质对象和Rust的类型系统来编写代码的优势在于，这与使用鸭子类型的方式类似。我们永远不必在运行时检查某个值是否实现了某个特定方法，也不必担心如果某个值没有实现某个方法而仍然调用该方法时会出现错误。如果某个值没有实现特质对象所需的特质，Rust不会编译我们的代码。

例如，清单 18-10 展示了如果我们尝试使用一个 `String` 作为组成部分来创建一个 `Screen` 会发生什么情况。

**清单 18-10:** *src/main.rs* — 尝试使用未实现 trait object 该 trait 的类型

```rust,ignore,does_not_compile
use gui::Screen;

fn main() {
    let screen = Screen {
        components: vec![Box::new(String::from("Hi"))],
    };

    screen.run();
}

```

我们会遇到这个错误，因为 `String` 没有实现 `Draw` 特性。

```console
$ cargo run
   Compiling gui v0.1.0 (file:///projects/gui)
error[E0277]: the trait bound `String: Draw` is not satisfied
 --> src/main.rs:5:26
  |
5 |         components: vec![Box::new(String::from("Hi"))],
  |                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^ the trait `Draw` is not implemented for `String`
  |
  = help: the trait `Draw` is implemented for `Button`
  = note: required for the cast from `Box<String>` to `Box<dyn Draw>`

For more information about this error, try `rustc --explain E0277`.
error: could not compile `gui` (bin "gui") due to 1 previous error

```

这个错误告诉我们，要么我们传递给 `Screen` 的数据并非我们本意要传递的，因此应该传递另一种类型的数据；要么我们应该在 `String` 上实现 `Draw`，这样 `Screen` 就能在 `draw` 上调用 `draw`。

<!-- Old headings. Do not remove or links may break. -->

<a id="trait-objects-perform-dynamic-dispatch"></a>

### 执行动态调度

在第十章中，我们讨论了编译器在泛型上执行单态化过程的情况：编译器为我们在泛型类型参数位置使用的每个具体类型生成非泛型的实现。单态化后的代码采用_静态调度_方式，即编译器在编译时就能知道你正在调用哪种方法。这与_Dynamic调度_方式不同，在动态调度情况下，编译器在编译时无法判断你正在调用哪种方法。在动态调度的情况下，编译器会生成在运行时才能决定调用哪种方法的代码。

当我们使用 trait 对象时，Rust 必须使用动态调度。编译器无法知道使用 trait 对象的代码中可能会使用哪些类型，因此它无法知道应该调用哪种类型上的方法。相反，在运行时，Rust 会使用 trait 对象内部的指针来确定应该调用哪种方法。这种查找过程会产生运行时的开销，而静态调度则不会产生这种开销。动态调度还会阻止编译器选择内联方法代码，这反过来又阻止了一些优化。Rust 有一些关于何时可以使用动态调度的规则，这些规则被称为 _dyn 兼容性_。这些规则超出了本次讨论的范围，但你可以阅读更多关于它们的内容。不过，我们在 Listing 18-5 中编写的代码确实获得了额外的灵活性，并且在 Listing 18-9 中能够支持这些灵活性，因此这是一个需要考虑的权衡。

[performance-of-code-using-generics]: ch10-01-syntax.html#performance-of-code-using-generics
[dynamically-sized]: ch20-03-advanced-types.html#dynamically-sized-types-and-the-sized-trait
[dyn-compatibility]: https://doc.rust-lang.org/reference/items/traits.html#dyn-compatibility
