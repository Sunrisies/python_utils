<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="使用允许不同类型值的特性对象"></a>

## 使用特质对象来抽象共享行为

在第八章中，我们提到向量的一个局限性是它们只能存储单一类型的元素。我们在清单8-9中找到了一种解决方法，其中定义了一个`SpreadsheetCell`枚举类型，该枚举类型包含整数、浮点数和文本三种变体。这样，我们就可以在每个单元格中存储不同类型的数据，同时仍然保持向量能够表示一系列单元格的结构。当我们的可互换项目是已知固定类型的集合时，这是一个非常有效的解决方案，而且当代码被编译时，这种处理方式也是安全的。

然而，有时候我们希望我们的库用户能够扩展在特定情况下有效的类型集合。为了说明如何实现这一点，我们将创建一个示例图形用户界面工具，该工具会遍历一个项目列表，并对每个项目调用`draw`方法来将其绘制到屏幕上——这是图形用户界面工具的常见技术。我们将创建一个名为`gui`的库，其中包含图形用户界面库的结构。这个库可能会包含一些供人们使用的类型，例如`Button`或`TextField`。此外，用户可能还会想要创建自己的可绘制类型：例如，一位程序员可能会添加`Image`，另一位程序员可能会添加`SelectBox`。

在编写这个库的时候，我们无法预知或定义其他程序员可能想要创建的所有类型。但我们知道，`gui`需要跟踪多种不同类型的值，并且需要对这些不同类型的值分别调用`draw`方法。我们不需要确切知道当我们调用`draw`方法时会发生什么，只需要知道这些值都有这个方法可供我们使用即可。

在具有继承的语言中，我们可以定义一个名为`Component`的类，该类包含一个名为`draw`的方法。其他类，如`Button`、`Image`和`SelectBox`，将继承自`Component`，从而继承`draw`方法。这些类可以各自覆盖`draw`方法，以定义自己的自定义行为，但框架可以将所有这些类型视为`Component`的实例，并调用`draw`方法。但由于Rust没有继承机制，我们需要另一种方式来构建`gui`库，以便用户能够创建与库兼容的新类型。

### 定义具有共同行为的特质

为了实现我们希望`gui`具有的行为，我们将定义一个名为`Draw`的特质，该特质包含一个名为`draw`的方法。然后，我们可以定义一个接受特质对象的向量。一个_特质对象_既指向实现了我们指定特质的类型的一个实例，也指向用于在运行时查找该类型上特质方法的表。我们通过指定某种指针来创建特质对象，例如引用或`Box<T>`智能指针，然后是`dyn`关键字，最后指定相关的特质。（关于为什么特质对象必须使用指针的问题，我们将在《动态大小类型与`Sized`特质》第20章中讨论。）我们可以使用特质对象来代替泛型或具体类型。无论何时使用特质对象，Rust的类型系统都会在编译时确保在该上下文中使用的任何值都实现了该特质对象的特质。因此，我们不需要在编译时知道所有可能的类型。

我们已经提到过，在Rust中，我们不会将结构体（structs）和枚举（enums）称为“对象”，以此来区分它们与其他语言的“对象”。在结构体中，结构体的字段中的数据以及位于`impl`块中的行为是相互分离的；而在其他语言中，数据和行为通常被合并为一个概念，这种概念通常被称为对象。与其它语言中的对象不同，特质对象无法添加数据到特质对象中。特质对象不像其他语言中的对象那样具有广泛的实用性：它们的具体用途是允许对共同的行为进行抽象化处理。

清单18-3展示了如何定义一个名为`Draw`的特质，该特质包含一个名为`draw`的方法。

<列表编号="18-3" 文件名称="src/lib.rs" 标题="`Draw` 特性的定义">

```rust,noplayground
{{#rustdoc_include ../listings/ch18-oop/listing-18-03/src/lib.rs}}
```

</ Listing>

这种语法在我们讨论如何在第10章中定义特质时已经见过。接下来是一些新的语法：清单18-4定义了一个名为`Screen`的结构体，该结构体包含一个名为`components`的向量。这个向量属于`Box<dyn Draw>`类型，而`Box<dyn Draw>`实际上是一个特质对象；它代表了`Box`中任何实现了`Draw`特质的数据类型的替代品。

<listing number="18-4" file-name="src/lib.rs" caption="定义 `Screen` 结构体，该结构体包含一个 `components` 字段，该字段持有一个实现 `Draw` 特性的 trait 对象的向量">

```rust,noplayground
{{#rustdoc_include ../listings/ch18-oop/listing-18-04/src/lib.rs:here}}
```

</ Listing>

在 `Screen` 结构上，我们将定义一个名为 `run` 的方法，该方法会调用其每个 `components` 中的 `draw` 方法，如清单 18-5 所示。

<listing number="18-5" file-name="src/lib.rs" caption="一个位于`Screen`中的`run`方法，该方法会调用位于每个组件上的`draw`方法">

```rust,noplayground
{{#rustdoc_include ../listings/ch18-oop/listing-18-05/src/lib.rs:here}}
```

</ Listing>

这与使用带有特质限定的泛型参数来定义结构体有所不同。泛型参数一次只能被一个具体类型替代，而特质对象则允许在运行时用多个具体类型来替代该特质对象。例如，我们可以使用泛型参数和特质限定来定义`Screen`结构体，如清单18-6所示。

<列表编号="18-6" 文件名称="src/lib.rs" 标题="使用泛型和特质约束的`Screen`结构及其`run`方法的另一种实现">

```rust,noplayground
{{#rustdoc_include ../listings/ch18-oop/listing-18-06/src/lib.rs:here}}
```

</ Listing>

这限制了我们只能使用一个 ``Screen`` 实例，该实例中的组件全部是类型 ``Button`` 或者都是类型 ``TextField``。如果你只能处理同构的集合，那么使用泛型和技术约束更为合适，因为定义会在编译时被单态化，从而使用具体的类型。

另一方面，使用 trait 对象的方法时，一个 `Screen` 实例可以包含一个 `Vec<T>`，而 `Vec<T>` 又包含了一个 `Box<Button>` 以及一个 `Box<TextField>`。让我们来看看这是如何工作的，然后我们再讨论一下对运行时性能的影响。

### 实现特质

现在，我们将添加一些实现了 ``Draw`` 特性的类型。我们会提供 ``Button`` 类型。实际上，实现一个GUI库超出了本书的范围，因此 ``draw`` 方法在其实现中并不会包含任何有用的代码。为了想象一下这个实现可能的样子，一个 ``Button`` 结构体可能会包含 ``width``、``height`` 和 ``label`` 字段，如清单 18-7 所示。

<listing number="18-7" file-name="src/lib.rs" caption="一个实现了`Draw` trait的`Button`结构体">

```rust,noplayground
{{#rustdoc_include ../listings/ch18-oop/listing-18-07/src/lib.rs:here}}
```

</ Listing>

在 `Button` 中的 `width`、`height` 和 `label` 字段与其他组件中的字段有所不同；例如，`TextField` 类型可能包含相同的字段，同时还包含 `placeholder` 字段。我们想要在屏幕上显示的每种类型都会实现 `Draw` 特性，但在 `draw` 方法中会使用不同的代码来定义如何显示该特定类型，正如 `Button` 中所描述的那样（不包括实际的 GUI 代码）。例如，`Button` 类型可能还包含一个 `impl` 块，其中包含了与用户点击按钮时发生的事件相关的处理方法。这类方法并不适用于像 `TextField` 这样的类型。

如果有人使用我们的库，并决定实现一个包含`width`、`height`和`options`字段的`SelectBox`结构体，那么他们也会在`SelectBox`类型上实现`Draw`特性，如清单18-8所示。

<listing number="18-8" file-name="src/main.rs" caption="另一个使用 `gui` 并在 `SelectBox` 结构体中实现 `Draw` 特性的 crate">

```rust,ignore
{{#rustdoc_include ../listings/ch18-oop/listing-18-08/src/main.rs:here}}
```

</ Listing>

我们的库的用户现在可以编写他们的`main`函数来创建`Screen`实例。对于`Screen`实例，他们可以通过将`SelectBox`和`Button`分别放入`Box<T>`中，从而创建一个 trait 对象。然后，他们可以在`Screen`实例上调用`run`方法，该方法会分别调用每个组件上的`draw`方法。清单18-9展示了这种实现方式。

<列表编号="18-9" 文件名称="src/main.rs" 标题="使用特质对象存储实现相同特质的不同类型的值">

```rust,ignore
{{#rustdoc_include ../listings/ch18-oop/listing-18-09/src/main.rs:here}}
```

</ Listing>

在编写这个库的时候，我们并不知道可能会有人添加`SelectBox`这种类型。不过，我们的`Screen`实现能够操作这种新类型，并将其绘制出来，因为`SelectBox`实现了`Draw`特性，这意味着它也实现了`draw`方法。

这个概念——只关注一个值所响应的消息，而不是该值的具体类型——类似于动态类型语言中的“鸭子类型”概念：如果某事物看起来像鸭子并且发出鸭叫声，那么它就一定是鸭子！在清单18-5中，对`Screen`的`run`实现中，`run`不需要知道每个组件的具体类型。它不会检查某个组件是`Button`还是`SelectBox`的实例，而只是调用该组件上的`draw`方法。通过指定`Box<dyn Draw>`作为`components`向量中值的类型，我们定义了`Screen`需要能够调用`draw`方法的数值。

使用特质对象以及Rust的类型系统来编写代码的优势在于：与基于鸭子类型的代码相比，我们永远不必在运行时检查某个值是否实现了特定的方法，也不必担心如果某个值没有实现某个方法但仍然被调用时会出现错误。如果某个值没有实现特质对象所需的特质，Rust会无法编译我们的代码。

例如，清单18-10展示了如果我们尝试使用`String`作为组件来创建`Screen`时会发生什么。

<列表编号="18-10" 文件名称="src/main.rs" 标题="尝试使用未实现该特质对象的类型">

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch18-oop/listing-18-10/src/main.rs}}
```

</ Listing>

我们会遇到这个错误，因为 ``String`` 没有实现 ``Draw`` 这个特质：

```console
{{#include ../listings/ch18-oop/listing-18-10/output.txt}}
```

这个错误告诉我们，要么我们向`Screen`传递了不该传递的数据，因此应该传递其他类型的数据；要么我们应该在`String`上实现`Draw`的功能，这样`Screen`就可以在其上调用`draw`。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id=" trait-objects-perform-dynamic-dispatch"></a>

### 执行动态调度

在第十章的[“使用泛型实现代码的性能”][performance-of-code-using-generics]一文中，我们讨论了编译器对泛型代码进行单态化处理的过程：编译器会为所使用的每种具体类型生成非泛型的函数和方法的实现，这些实现替代了泛型类型参数。通过单态化得到的代码采用_静态调度_机制，这意味着在编译时编译器就能确定正在调用的是哪种方法。这与_Dynamic调度_不同，在动态调度的情况下，编译器无法在编译时确定正在调用的是哪种方法。在动态调度的场景中，编译器会生成在运行时才能决定要调用哪种方法的代码。

当我们使用特质对象时，Rust必须使用动态调度。编译器无法知道所有可能用于带有特质对象的代码中的类型，因此它无法确定应该在哪种类型上调用哪种方法。相反，在运行时，Rust会利用特质对象内部的指针来确定应该调用哪种方法。这种查找过程会带来运行时的开销，而静态调度则不会产生这种开销。动态调度还会阻止编译器对方法的代码进行内联优化，这也限制了某些优化措施的实施。此外，Rust有一些关于何时可以使用动态调度的规则，这些规则被称为“_dyn兼容性”。这些规则超出了本次讨论的范围，但你可以阅读更多相关信息[在参考手册中][dyn-compatibility]<!-- 忽略 -->。不过，我们在Listing 18-5中编写的代码确实获得了更多的灵活性，并且在Listing 18-9中能够实现相应的功能，因此这是一个需要考虑的权衡。

[使用泛型提高代码性能]: ch10-01-syntax.html#performance-of-code-using-generics  
[动态大小类型]: ch20-03-advanced-types.html#dynamically-sized-types-and-the-sized-trait  
[动态兼容性]: https://doc.rust-lang.org/reference/items/traits.html#dyn-compatibility