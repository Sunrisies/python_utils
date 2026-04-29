## 宏

在本书中，我们一直使用诸如`println!`这样的宏，但并没有完全探讨什么是宏以及它的工作原理。术语“宏”指的是Rust中的一种功能——带有`macro_rules!`的声明性宏，以及三种过程式宏。

- 自定义 ``#[derive]`` 宏，用于指定通过 ``derive`` 属性添加的代码
  这些代码应用于结构体和集合类型
- 类似属性的宏，用于定义可在任何项目上使用的自定义属性
- 功能类似的宏，看起来像函数调用，但实际上是对作为参数传递的标记进行操作

我们将依次讨论这些内容，但首先，让我们看看为什么在我们已经有函数的情况下，我们还需要宏。

### 宏与函数的区别

从根本上说，宏是一种编写代码的方式，这种代码可以生成其他代码，这被称为“元编程”。在附录C中，我们讨论了`derive`属性，它可以为您生成各种特性的实现。在整本书中，我们也使用了`println!`和`vec!`宏。所有这些宏都可以展开，从而生成比您手动编写的代码更多的代码。

元编程有助于减少需要编写和维护的代码量，这也是函数的功能之一。不过，宏还具有一些函数所没有的额外功能。

函数的签名必须声明该函数所拥有的参数数量和类型。而宏则可以接受任意数量的参数：我们可以调用`println!("hello")`时只使用一个参数，或者调用`println!("hello {}", name)`时使用两个参数。此外，宏在编译器解释代码含义之前就已经被展开，因此宏可以例如在给定类型上实现某个特质。而函数则无法这样做，因为函数是在运行时调用的，而特质的实现则需要在编译时完成。

使用宏而不是函数进行实现的缺点是，宏的定义比函数定义更为复杂，因为你需要编写能够编写Rust代码的Rust代码。由于这种间接性，宏的定义通常比函数定义更难以阅读、理解和维护。

宏与函数的另一个重要区别在于，你必须在一个文件中定义宏或将其置于作用域内，然后才能调用它们。而函数则可以在任何地方定义，也可以在任何地方调用。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="declarative-macros-with-macro_rules-for-general-metaprogramming"></a>

### 用于通用元编程的声明式宏

在Rust中，最广泛使用的宏形式就是声明性宏。这类宏有时也被称为“示例式宏”、“`macro_rules!`宏”，或者简单地称为“宏”。从根本上说，声明性宏允许你编写类似于Rust中的`match`表达式。正如第6章所讨论的那样，`match`表达式是一种控制结构，它接受一个表达式，将该表达式的结果值与某些模式进行比较，然后根据匹配到的模式来执行相应的代码。宏还会将某个值与特定代码相关的模式进行比较：在这种情况下，该值就是传递给宏的Rust源代码；模式则与该源代码的结构进行比对；当某个模式被匹配时，与之对应的代码就会替换传递给宏的代码。所有这些操作都在编译过程中完成。

要定义一个宏，可以使用`macro_rules!`结构。让我们通过查看`vec!`宏的定义来了解如何使用`macro_rules!`。第8章介绍了如何使用`vec!`宏来创建一个具有特定值的向量。例如，以下宏创建了一个包含三个整数的新向量：

```rust
let v: Vec<u32> = vec![1, 2, 3];
```

我们还可以使用 ``vec!`` 宏来创建一个包含两个整数的向量，或者一个包含五个字符串切片的向量。我们无法使用函数来实现同样的功能，因为我们无法在事先知道值的数量或类型的情况下进行操作。

清单20-35展示了`vec!`宏的一个简化定义。

<listing number="20-35" file-name="src/lib.rs" caption="A simplified version of the `vec!` macro definition">

```rust,noplayground
{{#rustdoc_include ../listings/ch20-advanced-features/listing-20-35/src/lib.rs}}
```

</ Listing>

注意：标准库中 ``vec!`` 宏的实际定义包含了一段代码，用于提前分配适当数量的内存。这段代码是一种优化措施，为了简化示例，我们在这里没有包含它。

`#[macro_export]`这个注释表明，每当定义该宏的 crate 被带入作用域时，这个宏就应该被提供出来。如果没有这个注释，那么这个宏就无法被带入作用域。

然后，我们开始宏定义，使用`macro_rules!`作为宏的定义起始标记，并且宏的名称后面不加上感叹号。在这个例子中，宏的名称是`vec`，其后面跟着表示宏定义主体的花括号。

在`vec!`中的结构与`match`表达式的结构类似。这里有一个包含`( $( $x:expr ),* )`模式的分支，随后是`=>`以及与该模式相关的代码块。如果模式匹配成功，那么相关的代码块将被执行。由于这是该宏中唯一的模式，因此只有一种有效的匹配方式；任何其他模式都会导致错误。更复杂的宏会有多个分支。

在宏定义中使用的有效模式语法与第19章中介绍的模式语法不同，因为宏模式是依据Rust代码的结构来匹配的，而不是基于具体的值。让我们来了解一下清单20-29中的各个模式元素的含义；关于完整的宏模式语法，请参阅[Rust参考][ref]。

首先，我们使用一对括号来包围整个模式。我们使用美元符号（`$`）在宏系统中声明一个变量，该变量将包含与模式相匹配的Rust代码。美元符号明确表示这是一个宏变量，而不是普通的Rust变量。接下来是一组括号，用于捕获与模式匹配的值，以便用于替换代码。在`$()`中包含了`$x:expr`，它可以匹配任何Rust表达式，并将该表达式命名为`$x`。

在 `$()` 后面的逗号表示，必须在一个逗号分隔字符之后，放置与 `$()` 中的代码相匹配的代码实例。而 `*` 则指定了该模式可以匹配零个或多个位于 `*` 之前的任何内容。

当我们使用 `vec![1, 2, 3];` 调用这个宏时，`$x` 模式会三次与三个表达式 `1`、`2` 和 `3` 进行匹配。

现在让我们看一下与这个分支相关的代码主体中的模式：  
对于每个与 `$()` 相匹配的部分，都会在 `$()*` 中生成 `temp_vec.push()`。根据模式匹配的次数，这种模式可能会重复出现零次或多次。而 `$x` 则会被所有匹配到的表达式所替换。当我们使用 `vec![1, 2, 3];` 调用这个宏时，生成的代码将会是如下内容：

```rust,ignore
{
    let mut temp_vec = Vec::new();
    temp_vec.push(1);
    temp_vec.push(2);
    temp_vec.push(3);
    temp_vec
}
```

我们定义了一个宏，它可以接受任意数量的任意类型的参数，并能生成代码来创建一个包含指定元素的向量。

如需了解更多关于如何编写宏的信息，请参阅在线文档或其他资源，例如由 Daniel Keep 发起、Lukas Wirth 继续编写的《Rust 宏小书》。

### 用于从属性生成代码的程序式宏

宏的第二种形式就是过程式宏，它的行为更类似于函数（实际上是一种过程）。过程式宏接受一些代码作为输入，对这段代码进行操作，然后产生一些代码作为输出。这与声明式宏通过模式匹配并替换代码的方式不同。过程式宏有三种类型：自定义的内联代码、类似属性的宏以及函数式的宏，它们的运作方式都类似。

在创建过程式宏时，其定义必须位于一个特殊的 crate 中。这一做法是基于一些复杂的技术原因，我们希望在未来能够取消这种限制。在 Listing 20-36 中，我们展示了如何定义一个过程式宏，其中 `some_attribute` 是一个占位符，用于指代特定的宏类型。

<列表编号="20-36" 文件名称="src/lib.rs" 标题="定义一个过程式宏的示例">

```rust,ignore
use proc_macro::TokenStream;

#[some_attribute]
pub fn some_name(input: TokenStream) -> TokenStream {
}
```

</ Listing>

定义过程宏的函数接收一个名为`TokenStream`的参数，并生成一个名为`TokenStream`的输出。`TokenStream`类型是由Rust附带的标准库`proc_macro`定义的，它代表一系列标记。这就是宏的核心：宏操作的源代码就是输入的`TokenStream`，而宏生成出的代码则是输出的`TokenStream`。此外，该函数还附带一个属性，用于指定我们正在创建的是哪种过程宏。在同一个标准库中，我们可以创建多种类型的过程宏。

让我们来看看不同类型的过程式宏。我们先从一个自定义的 ``derive`` 宏开始，然后解释那些使其他形式不同的细微差别。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="如何编写自定义的derive宏"></a>

### 自定义 `derive` 宏

让我们创建一个名为 ``hello_macro`` 的软件包，该软件包定义了一个名为 ``HelloMacro`` 的特质，并附带了一个名为 ``hello_macro`` 的相关函数。与其要求用户为他们的每种类型实现 ``HelloMacro`` 特质，不如提供一个过程式宏，这样用户就可以在他们的类型上标注 ``#[derive(HelloMacro)]``，从而获得 ``hello_macro`` 函数的默认实现。这个默认实现会打印出 `Hello, Macro! My name is TypeName!` where ``。这里的 `TypeName` 是指定义此特质的类型名称。换句话说，我们将编写一个软件包，让其他程序员能够使用我们的软件包来编写类似清单 20-37 这样的代码。

<列表编号="20-37" 文件名称="src/main.rs" 标题="用户在使用我们的过程式宏时可以编写的代码">

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch20-advanced-features/listing-20-37/src/main.rs}}
```

</ Listing>

当我们完成之后，这段代码将会打印出`Hello, Macro! My name is Pancakes!`。第一步是创建一个新的库 crate，就像这样：

```console
$ cargo new hello_macro --lib
```

接下来，在清单20-38中，我们将定义`HelloMacro`特质及其相关的函数。

<列表 file-name="src/lib.rs" number="20-38" caption="一个简单的特性，我们将它与 `derive` 宏一起使用">

```rust,noplayground
{{#rustdoc_include ../listings/ch20-advanced-features/listing-20-38/hello_macro/src/lib.rs}}
```

</ Listing>

我们有一个特质及其相关函数。此时，我们的 crate 用户可以实现该特质，以实现所需的功能，如清单 20-39 所示。

<列表编号="20-39" 文件名称="src/main.rs" 标题="如果用户编写了`HelloMacro` trait的手动实现，会是什么样子">

```rust,ignore
{{#rustdoc_include ../listings/ch20-advanced-features/listing-20-39/pancakes/src/main.rs}}
```

</ Listing>

不过，他们需要对每一种想要与`hello_macro`一起使用的类型编写相应的实现代码；我们希望避免让他们自己来做这项工作。

此外，我们还无法为 ``hello_macro`` 函数提供默认实现，该函数可以打印出该特质所实现的类型的名称。由于 Rust 没有反射功能，因此在运行时无法查询类型的名称。我们需要一个宏来在编译时生成相应的代码。

下一步是定义过程式宏。在撰写本文时，过程式宏需要放在自己的 crate 中。不过，这一限制可能会在未来被取消。关于 crate 和宏 crate 的结构规范如下：对于一个名为 `foo` 的 crate，会有一个自定义的 `derive` 过程式宏 crate，其路径为 `foo_derive`。现在，让我们在我们的 `hello_macro` 项目中创建一个新的 crate，名为 `hello_macro_derive`。

```console
$ cargo new hello_macro_derive --lib
```

我们的两个 crate 之间有着紧密的关联，因此我们将程序宏 crate 创建在 `hello_macro` 目录中。如果我们修改了 `hello_macro` 中的 trait 定义，那么我们就需要在 `hello_macro_derive` 中相应地修改程序宏的实现。这两个 crate 需要分别进行发布，使用这些 crate 的程序员需要将它们都添加到依赖项中，并将其纳入作用域。我们也可以选择让 `hello_macro` crate 以 `hello_macro_derive` 为依赖项，然后重新导出程序宏代码。不过，由于我们项目的结构安排，程序员即使不想使用 `derive` 的功能，也可以继续使用 `hello_macro`。

我们需要将`hello_macro_derive` crate声明为过程式宏 crate。此外，我们还需要使用`syn`和`quote` crate的功能，正如你稍后会看到的，因此我们需要将它们作为依赖项添加到项目中。请在_Cargo.toml_文件中为`hello_macro_derive`添加以下内容：

<listing file-name="hello_macro_derive/Cargo.toml">

```toml
{{#include ../listings/ch20-advanced-features/listing-20-40/hello_macro/hello_macro_derive/Cargo.toml:6:12}}
```

</ Listing>

要开始定义这个过程式宏，请将清单20-40中的代码放入你的`_src/lib.rs_`文件中，该文件属于`hello_macro_derive` crate。请注意，除非我们为`impl_hello_macro`函数添加定义，否则这段代码将无法编译。

<listing number="20-40" file-name="hello_macro_derive/src/lib.rs" caption="大多数过程式宏库在处理Rust代码时都需要使用的代码">

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch20-advanced-features/listing-20-40/hello_macro/hello_macro_derive/src/lib.rs}}
```

</ Listing>

请注意，我们将代码分解为两个函数：`hello_macro_derive`，负责解析`TokenStream`；以及`impl_hello_macro`，负责转换语法树。这样编写过程式宏会更加方便。外部函数(`hello_macro_derive`)中的代码对于您看到的或创建的所有过程式宏来说都是相同的。而内部函数(`impl_hello_macro`)中指定的代码则会根据您所使用的过程式宏的目的而有所不同。

我们引入了三个新的库：`proc_macro`、[`syn`][syn]<!-- 忽略 -->以及[`quote`][quote]<!-- 忽略 -->。`proc_macro`这个库是随Rust一起提供的，因此我们不需要在_Cargo.toml_文件中添加它作为依赖项。而`proc_macro`则是编译器的API，它允许我们读取和操作Rust代码。

`syn`这个库能够将Rust代码从字符串解析成一种数据结构，我们可以在此基础上执行各种操作。而`quote`这个库则可以将这些数据结构重新转换回Rust代码。这些库使得解析我们可能需要处理的任何类型的Rust代码变得更加简单：编写一个完整的Rust代码解析器并非易事。

当我们的库的用户在一个类型上指定了`#[derive(HelloMacro)]`时，`hello_macro_derive`函数将被调用。这是可能的，因为我们已经在`hello_macro_derive`函数上添加了`proc_macro_derive`的注释，并且指定了名称`HelloMacro`，这个名称与我们使用的特质名称相匹配。这是大多数过程式宏所遵循的惯例。

`hello_macro_derive`函数首先将`input`从`TokenStream`格式转换为一种数据结构，这样我们就可以对其进行解析和操作。这时就需要用到`syn`了。在`syn`中的`parse`函数接收一个`TokenStream`参数，并返回一个表示解析后的Rust代码的`DeriveInput`结构体。清单20-41展示了从解析`struct Pancakes;`字符串得到的`DeriveInput`结构体的相关部分。

<列表编号="20-41" 标题="在清单20-37中解析包含宏属性的代码时得到的`DeriveInput`实例">

```rust,ignore
DeriveInput {
    // --snip--

    ident: Ident {
        ident: "Pancakes",
        span: #0 bytes(95..103)
    },
    data: Struct(
        DataStruct {
            struct_token: Struct,
            fields: Unit,
            semi_token: Some(
                Semi
            )
        }
    )
}
```

</ Listing>

该结构体的字段表明，我们解析出的Rust代码是一个单元结构体，其`ident`字段的值为`Pancakes`。该结构体还包含更多字段，用于描述各种Rust代码；如需更多信息，请参阅[`syn`文档]中的`DeriveInput`部分。[syn-docs]

很快我们将定义`impl_hello_macro`这个函数，这是我们想要包含的新Rust代码所在的位置。但在这样做之前，请注意，我们的`derive`宏的输出也是一个`TokenStream`。返回的`TokenStream`会被添加到我们的 crate用户所编写的代码中，因此当他们编译他们的crate时，他们会得到我们在修改后的`TokenStream`中提供的额外功能。

你可能已经注意到，我们调用了 ``unwrap``，以便在调用 ``syn::parse`` 函数出现错误时触发 ``hello_macro_derive`` 函数的 panic 行为。为了使我们的过程式宏在出现错误时能够正确响应，这是必要的做法。因为根据过程式宏的 API 规范，`proc_macro_derive` 函数必须返回 `TokenStream` 而不是 `Result`。我们通过使用 `unwrap` 来简化了这个示例；在实际代码中，你应该使用 `panic!` 或 `expect` 来提供更具体的错误信息，说明发生了什么问题。

现在我们已经有了将带有注释的Rust代码从`TokenStream`转换为`DeriveInput`实例的代码，接下来让我们生成实现`HelloMacro`特性的代码，如清单20-42所示。

<listing number="20-42" file-name="hello_macro_derive/src/lib.rs" caption="使用解析后的Rust代码实现`HelloMacro`特质">

```rust,ignore
{{#rustdoc_include ../listings/ch20-advanced-features/listing-20-42/hello_macro/hello_macro_derive/src/lib.rs:here}}
```

</ Listing>

我们获得了一个包含使用 `ast.ident` 定义的标注类型名称的 `Ident` 结构实例。清单 20-41 中的结构表明，当我们对清单 20-37 中的代码执行 `impl_hello_macro` 函数时，得到的 `ident` 将会包含一个值为 `"Pancakes"` 的 `ident` 字段。因此，清单 20-42 中的 `name` 变量将包含一个 `Ident` 结构实例，当该实例被打印出来时，将会显示字符串 `"Pancakes"`，即清单 20-37 中结构的名称。

`quote!`宏允许我们定义想要返回的Rust代码。编译器期望从`quote!`宏的执行结果中获得不同的信息，因此我们需要将其转换为`TokenStream`格式。我们可以通过调用`into`方法来完成这一转换，该方法接受这种中间表示形式，并返回所需`TokenStream`类型的值。

`quote!`宏还提供了一些非常实用的模板机制：我们可以输入`#name`，而`quote!`会将其替换为`name`变量中的值。你甚至可以像普通宏那样进行重复操作。如需深入了解，请参考[`quote` crate的文档][quote-docs]。

我们希望我们的过程式宏能够生成针对用户标注的类型的一个实现，这个实现是通过使用`#name`获得的。该实现的其中一个函数就是`hello_macro`，其体内包含了我们想要提供的功能：打印`Hello, Macro! My name is`，然后打印被标注类型的名称。

这里使用的 ``stringify!`` 宏是 Rust 内置的。它接受一个 Rust 表达式，比如 ``1 + 2``，并在编译时将该表达式转换为字符串字面量，例如 ``"1 + 2"``。这与 ``format!`` 或 ``println!`` 不同，后者是先计算表达式的值，然后再将其转换为 ``String`` 形式。另外，``#name`` 可能是一个需要直接打印的表达式，因此我们使用 ``stringify!`` 来处理这种情况。而使用 ``stringify!``，还可以通过在编译时将 ``#name`` 转换为字符串字面量来避免内存分配的开销。

此时，`cargo build`应该在`hello_macro`和`hello_macro_derive`中成功完成。让我们把这些 crate 连接到清单20-37中的代码，以观察过程式宏的实际效果！使用`cargo new pancakes`在你的_projects目录下创建一个新的二进制项目。我们需要在`pancakes`的_Cargo.toml_文件中添加`hello_macro`和`hello_macro_derive`作为依赖项。如果你将`hello_macro`和`hello_macro_derive`发布到[crates.io](https://crates.io/)上，那么它们就会成为常规依赖项；如果不是的话，你可以将它们指定为`path`依赖项，具体方式如下：

```toml
{{#include ../listings/ch20-advanced-features/no-listing-21-pancakes/pancakes/Cargo.toml:6:8}}
```

将代码清单20-37中的内容放入`_src/main.rs_`文件中，然后运行__`INLINE_CODE_198__`。应该会打印出__`INLINE_CODE_199__`。程序宏中的__`INLINE_CODE_200__`特性已经实现了，而无需`pancakes`` crate来实现它；同时，``#[derive(HelloMacro)]``还添加了该特性的实现。

接下来，让我们探讨一下其他类型的过程式宏与自定义`derive`宏之间的区别。

### 属性式宏

属性类宏与自定义的 ``derive`` 宏类似，但它们不是生成用于 ``derive`` 属性的代码，而是允许你创建新的属性。此外，这类宏更加灵活：`derive` 仅适用于结构体和集合类型；而属性则可以应用于其他类型，比如函数。下面是一个使用属性类宏的例子。假设你有一个名为 `route` 的属性，该属性可以在使用Web应用程序框架时标注函数。

```rust,ignore
#[route(GET, "/")]
fn index() {
```

这个 ``#[route]`` 属性将由框架定义为一个过程式宏。该宏定义函数的签名如下所示：

```rust,ignore
#[proc_macro_attribute]
pub fn route(attr: TokenStream, item: TokenStream) -> TokenStream {
```

在这里，我们有两个参数，其类型为 ``TokenStream``。第一个参数用于描述该属性的内容，即 ``GET, "/"``部分。第二个参数则是该属性所附加到的元素的主体，在本例中为 ``fn index() {}``以及函数的其余部分。

除此之外，属性类宏的工作原理与自定义的 ``derive`` 宏相同：你可以创建一个使用 ``proc-macro`` 类型的 crate，然后实现一个函数来生成你想要生成的代码！

### 类似函数的宏

类函数的宏是一种看起来像函数调用的宏。与`macro_rules!`宏类似，它们比函数更灵活；例如，它们可以接受未知数量的参数。然而，`macro_rules!`宏只能使用我们在[“声明式宏用于通用元编程”][decl]<!-- ignore -->章节中讨论过的类似match的语法来定义。类函数的宏接受一个`TokenStream`参数，并且它们的定义会像其他两种过程式宏一样，使用Rust代码来操作该`TokenStream`。一个类函数的宏的例子是`sql!`宏，它的调用方式如下：

```rust,ignore
let sql = sql!(SELECT * FROM posts WHERE id=1);
```

这个宏会解析其中的SQL语句，并检查其语法是否正确。这比`macro_rules!`宏所能处理的任务要复杂得多。`sql!`宏的定义如下：

```rust,ignore
#[proc_macro]
pub fn sql(input: TokenStream) -> TokenStream {
```

这个定义与自定义宏 ``derive`` 的签名类似：我们接收括号内的标记，并返回我们想要生成的代码。

## 总结

哇！现在你的工具箱里有一些Rust特性，你可能不会经常使用它们，但你会知道在特定情况下可以使用这些特性。我们介绍了几个复杂的主题，这样当你在错误信息提示或别人的代码中遇到这些概念时，就能识别它们以及相关的语法。可以将这一章作为参考，帮助你找到解决方案。

接下来，我们将把本书中讨论的所有内容付诸实践，再完成一个项目！

[参考链接]:../reference/macros-by-example.html  
[tlborm]: https://veykril.github.io/tlborm/  
[syn]: https://crates.io/crates/syn  
[quote]: https://crates.io/crates/quote  
[syn-docs]: https://docs.rs/syn/2.0/syn/struct.DeriveInput.html  
[quote-docs]: https://docs.rs/quote  
[decl]: #declarative-macros-with-macro_rules-for-general-metaprogramming