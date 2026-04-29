## 宏指令

在本书中，我们使用了诸如`println!`这样的宏，但并没有完全探讨什么是宏以及它的工作原理。术语“宏”指的是Rust中的一种功能集合——包括声明性宏`macro_rules!`以及三种过程式宏。

- 自定义 ``#[derive]`` 宏，用于指定通过 ``derive`` 属性添加的代码
  该属性用于结构体和结构体枚举类型
- 类似属性的宏，用于定义可在任何项目上使用的自定义属性
- 类似函数的宏，看起来像函数调用，但实际上是对作为参数指定的标记进行操作

我们将依次讨论这些内容，但首先，让我们看看为什么在我们已经有函数的情况下，我们还需要宏。

### 宏与函数的区别

从根本上说，宏是一种编写代码的方式，这种代码可以生成其他代码，这被称为“元编程”。在附录C中，我们讨论了`derive`属性，它可以为您生成各种特性的实现代码。在整本书中，我们也使用了`println!`和`vec!`宏。所有这些宏在展开后都会生成比您手动编写的代码更多的代码。

元编程有助于减少需要编写和维护的代码量，这也是函数的功能之一。然而，宏具有一些函数所没有的额外功能。

函数的签名必须声明该函数所拥有的参数数量和类型。而宏则可以接受任意数量的参数：我们可以调用`println!("hello")`时只使用一个参数，或者调用`println!("hello {}", name)`时使用两个参数。此外，宏在编译器解释代码含义之前就已经被展开，因此宏可以例如在给定类型上实现某个特征。而函数则无法这样做，因为函数是在运行时调用的，而特征则需要编译时实现。

采用宏而不是函数进行实现的缺点是，宏的定义比函数的定义更为复杂，因为你需要编写能够编写Rust代码的Rust代码。由于这种间接性，宏的定义通常比函数的定义更难以阅读、理解和维护。

宏与函数的另一个重要区别在于，你必须先定义宏或将其置于作用域内，然后才能在文件中调用它们。而函数则可以在任何地方定义，也可以在任何地方调用。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="声明式宏与宏规则用于通用元编程"></a>

### 用于通用元编程的声明式宏

在Rust中，最广泛使用的宏形式是**声明性宏**。这些宏有时也被称为“示例式宏”、“`macro_rules!`宏”，或者简单地称为“宏”。从根本上说，声明性宏允许你编写类似于Rust中的`match`表达式的内容。正如第6章所讨论的，`match`表达式是一种控制结构，它接受一个表达式，将该表达式的结果值与某种模式进行比较，然后根据比较结果执行相应的代码。使用相应的模式。宏还会将值与特定代码相关的模式进行比较：在这种情况下，值是传递给宏的纯Rust源代码；模式会与该源代码的结构进行比对；当某个模式与源代码结构匹配时，与该模式相关联的代码就会替换传递给宏的代码。所有这些操作都在编译过程中完成。

要定义一个宏，可以使用`macro_rules!`结构。让我们通过查看`vec!`宏的定义来了解如何使用`macro_rules!`。第8章介绍了如何使用`vec!`宏来创建一个具有特定值的向量。例如，以下宏会创建一个包含三个整数的新向量：

```rust
let v: Vec<u32> = vec![1, 2, 3];
```

我们还可以使用 ``vec!`` 宏来创建一个由两个整数组成的向量，或者一个由五个字符串切片组成的向量。我们无法使用函数来实现同样的功能，因为我们无法提前知道值的数量或类型。

清单20-35展示了`vec!`宏的简化定义。

<列表编号="20-35" 文件名称="src/lib.rs" 标题="`vec!`宏定义的简化版本">

```rust,noplayground
{{#rustdoc_include ../listings/ch20-advanced-features/listing-20-35/src/lib.rs}}
```

</清单>

注意：标准库中`vec!`宏的实际定义包含了一段代码，用于预先分配适当数量的内存。这段代码是一种优化措施，为了简化示例，我们在这里没有包含它。

`#[macro_export]`这个注释表示，每当定义该宏的 crate 被带入作用域时，这个宏就应该被提供出来。如果没有这个注释，那么这个宏就无法被带入作用域。

然后，我们开始宏定义，使用`macro_rules!`作为宏的定义起始标记，并且宏的名称后面不加上感叹号。在这个例子中，宏的名称是`vec`。紧接着就是表示宏定义主体的花括号。

在`vec!`结构体中，其结构类似于`match`表达式的结构。这里有一个以`( $( $x:expr ),* )`为模式的分支，随后是`=>`以及与该模式相关的代码块。如果模式匹配成功，那么相关的代码块将被执行。由于这是该宏中唯一的模式，因此只有一种有效的匹配方式；任何其他模式都会导致错误。更复杂的宏会包含多个分支。

在宏定义中使用的有效模式语法与第19章中介绍的模式语法不同，因为宏模式是依据Rust代码的结构来匹配的，而不是基于具体的值。让我们来了解一下清单20-29中的各个模式元素的含义；关于完整的宏模式语法，请参阅[Rust参考][ref]。

首先，我们使用一对括号来包围整个模式。我们使用美元符号（``$``）在宏系统中声明一个变量，该变量将包含与模式匹配的Rust代码。美元符号表明这是一个宏变量，而不是普通的Rust变量。接下来是一组括号，用于捕获与模式匹配的值，以便用于替换代码。在``$()``中包含了``$x:expr``，它匹配任何符合模式的数值。Rust表达式会为该表达式赋予名称`$x`。

在`$()`后面的逗号表示，必须在一个逗号分隔字符出现之后，才能与`$()`中的代码相匹配。而`*`则表明，该模式可以匹配零个或多个位于`*`之前的任何内容。

当我们使用`vec![1, 2, 3];`调用这个宏时，`$x`模式会与三个表达式`1`、`2`和`3`进行三次匹配。

现在让我们看看与这个部分相关的代码主体中的模式：对于每个与模式`$()`匹配的部分，都会在`$()*`中生成`temp_vec.push()`。根据模式匹配的次数，`temp_vec.push()`可能会出现零次或多次。而`$x`则会被匹配到的每个表达式所替换。当我们使用`vec![1, 2, 3];`调用这个宏时，生成的代码将会是如下内容：

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

如需了解更多关于如何编写宏的信息，请参阅在线文档或其他资源，例如由Daniel Keep发起、Lukas Wirth继续编写的《Rust宏小书》。

### 基于属性生成代码的程序宏

第二种宏的类型是过程式宏，它的作用更类似于函数（实际上是一种过程）。过程式宏接受一些代码作为输入，对这段代码进行操作，然后产生一些代码作为输出，而不是像声明式宏那样通过匹配模式来替换代码。过程式宏有三种类型：自定义`derive`、属性式以及函数式，它们的运作方式都类似。

在创建过程性宏时，其定义必须位于一个特殊的 crate 中。这一做法是基于一些复杂的技术原因，我们希望在未来能够消除这种需求。在 Listing 20-36 中，我们展示了如何定义一个过程性宏，其中 `some_attribute` 是一个占位符，用于指代特定的宏类型。

<列表编号="20-36" 文件名称="src/lib.rs" 标题="定义一个过程性宏的示例">

```rust,ignore
use proc_macro::TokenStream;

#[some_attribute]
pub fn some_name(input: TokenStream) -> TokenStream {
}
```

</清单>

该函数定义了一个过程式宏，它接受一个名为`TokenStream`的参数作为输入，并生成一个名为`TokenStream`的输出。类型`TokenStream`是由Rust所包含的`proc_macro`库定义的，它代表一系列标记。这就是宏的核心：宏所操作的源代码构成了输入`TokenStream`，而宏生成的代码则是输出`TokenStream`。此外，该函数还附带了一个属性。这指定了我们正在创建哪种类型的过程式宏。在同一 crate 中，我们可以拥有多种类型的过程式宏。

让我们来看看不同类型的过程式宏。我们先从自定义的``derive``宏开始，然后解释那些使其他形式不同的细微差别。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="如何编写自定义的Derive宏"></a>

### 自定义 `derive` 宏

让我们创建一个名为 ``hello_macro`` 的软件包，该软件包定义了一个名为 ``HelloMacro`` 的特质，并且有一个与之关联的函数，名为 ``hello_macro``。与其让用户为他们的每种类型实现 ``HelloMacro`` 特质，不如提供一个过程式宏，这样用户就可以在他们的类型上添加 ``#[derive(HelloMacro)]`` 来获得 ``hello_macro`` 函数的默认实现。默认实现会打印出 `Hello, Macro! My name is``` where `TypeName`是定义此特性的类型名称。换句话说，我们将编写一个框架，让其他程序员能够使用我们的框架来编写像清单20-37这样的代码。

<列表编号="20-37" 文件名称="src/main.rs" 标题="用户在使用我们的过程式宏时可以编写的代码">

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch20-advanced-features/listing-20-37/src/main.rs}}
```

</清单>

这段代码会在我们完成之后打印出`Hello, Macro! My name is Pancakes!`。第一步是创建一个新的库包，如下所示：

```console
$ cargo new hello_macro --lib
```

接下来，在清单20-38中，我们将定义`HelloMacro`特性及其相关的函数。

<列表文件名称="src/lib.rs" 编号="20-38" 标题="一个简单的特性，我们将使用`derive`宏">

```rust,noplayground
{{#rustdoc_include ../listings/ch20-advanced-features/listing-20-38/hello_macro/src/lib.rs}}
```

</清单>

我们有一个特质及其功能。目前，我们的库用户可以实现这个特质，以达成所需的功能，如清单20-39所示。

<列表编号="20-39" 文件名称="src/main.rs" 标题="如果用户编写了`HelloMacro`特性的手动实现，效果会是什么样子">

```rust,ignore
{{#rustdoc_include ../listings/ch20-advanced-features/listing-20-39/pancakes/src/main.rs}}
```

</清单>

不过，他们需要对每种想要使用的类型编写实现代码块，即使用`hello_macro`；我们希望让他们不必自己完成这项工作。

此外，我们还无法提供`hello_macro`函数的默认实现，该函数能够打印出该特质所实现的类型的名称。由于Rust没有反射功能，因此在运行时无法查询类型的名称。我们需要一个宏来在编译时生成相应的代码。

下一步是定义过程宏。在撰写本文时，过程宏需要放在自己的子包中。不过，这一限制可能会在未来被取消。关于子包和宏子包的结构规范如下：对于名为`foo`的子包，会有一个自定义的`derive`过程宏子包，其路径为`foo_derive`。现在，我们在`hello_macro`项目内创建一个新的子包，名为`hello_macro_derive`。

```console
$ cargo new hello_macro_derive --lib
```

我们的两个 crate 之间有着紧密的关联，因此我们将 procedural macro crate 创建在 `hello_macro` crate 的目录中。如果我们修改了 `hello_macro` 中的 traitdefinition，那么我们就需要在 `hello_macro_derive` 中修改 procedural macro 的实现。这两个 crate 需要分别进行发布，使用这些 crate 的程序员需要将它们都添加到依赖项中，并将它们纳入作用域。我们也可以选择……我们将`hello_macro` crate作为依赖项，并使用`hello_macro_derive`作为依赖项，同时重新导出该过程宏代码。然而，由于我们的项目结构安排，程序员即使不想使用`derive`的功能，也可以使用`hello_macro`。

我们需要将`hello_macro_derive` crate声明为过程式宏 crate。同时，我们还需要使用`syn`和`quote` crate的功能，正如你稍后会看到的，因此我们需要将它们作为依赖项添加到项目中。请在_Cargo.toml_文件中为`hello_macro_derive`添加以下内容：

<listing file-name="hello_macro_derive/Cargo.toml">

```toml
{{#include ../listings/ch20-advanced-features/listing-20-40/hello_macro/hello_macro_derive/Cargo.toml:6:12}}
```

</清单>

要开始定义这个过程式宏，请将清单20-40中的代码放入你的`_src/lib.rs_`文件中，该文件属于`hello_macro_derive` crate。请注意，在为我们添加`impl_hello_macro`函数的定义之前，这段代码是无法编译的。

<listing number="20-40" file-name="hello_macro_derive/src/lib.rs" caption="大多数过程式宏库在处理Rust代码时所需的代码">

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch20-advanced-features/listing-20-40/hello_macro/hello_macro_derive/src/lib.rs}}
```

</清单>

请注意，我们将代码分解为两个函数：`hello_macro_derive`，负责解析`TokenStream`；以及`impl_hello_macro`函数，负责转换语法树。这样编写过程式宏会更加方便。在外部函数中（本例为`hello_macro_derive`），几乎所有您所见或创建的过程式宏的代码都是相同的。您在函数体内指定的代码则有所不同。内部函数（在本例中为`impl_hello_macro`）会根据你的过程式宏的用途而有所不同。

我们引入了三个新的 crate：`proc_macro`、[`syn`][syn]<!-- 忽略 -->以及[`quote`][quote]<!-- 忽略 -->。`proc_macro`这个 crate是随 Rust 一起提供的，因此我们不需要在 _Cargo.toml_ 文件中添加它作为依赖项。而`proc_macro`则是编译器的 API，它允许我们从代码中读取和操作 Rust 代码。

`syn`这个库能够将字符串中的Rust代码解析成一种数据结构，我们可以在此基础上执行各种操作。而`quote`这个库则可以将这些数据结构重新转换回Rust代码。这两个库使得解析我们可能需要处理的任何类型的Rust代码变得更加简单：编写一个完整的Rust代码解析器并非易事。

当我们的库的用户在类型上指定了`#[derive(HelloMacro)]`时，将会调用`hello_macro_derive`函数。这是可能的，因为我们在`hello_macro_derive`函数上添加了`proc_macro_derive`的注释，并且指定了名称`HelloMacro`，这个名称与我们使用的特性名称相匹配。这是大多数过程性宏所遵循的惯例。

`hello_macro_derive`函数首先将`input`从`TokenStream`格式转换为一种数据结构，这样我们就可以对其进行解析和操作。这时，`syn`就发挥作用了。`syn`中的`parse`函数接收一个`TokenStream`参数，并返回一个表示解析后的Rust代码的`DeriveInput`结构体。列表20-41展示了`DeriveInput`的相关部分。从解析 `struct Pancakes;` 字符串中得到的结构体。

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

</清单>

这个结构体的字段表明，我们解析出的Rust代码是一个单元结构体。其中，``ident``的标识符为``Pancakes``。这个结构体还包含更多字段，用于描述各种Rust代码；如需更多信息，请参阅[`syn`文档](syn-docs)。

很快我们将定义`impl_hello_macro`函数，这是我们想要包含的新Rust代码所在的位置。但在这样做之前，请注意，我们的`derive`宏的返回值也是一个`TokenStream`。返回的`TokenStream`会被添加到我们的 crate用户所编写的代码中，因此当他们编译他们的crate时，他们会得到我们在修改后的`TokenStream`中提供的额外功能。

您可能已经注意到，我们调用了`unwrap`来在`syn::parse`函数调用失败的情况下触发`hello_macro_derive`函数的异常。这样做是为了让我们的过程式宏能够在出现错误时抛出异常，因为`proc_macro_derive`函数必须返回`TokenStream`而不是`Result`，这样才能符合过程式宏的API规范。我们通过使用`unwrap`来简化了这个示例；在实际代码中，应该提供更具体的错误信息。关于使用`panic!`或`expect`时出现了什么问题。

现在我们已经有了将带有注释的Rust代码从`TokenStream`转换为`DeriveInput`实例的代码，接下来让我们生成实现`HelloMacro`特性的代码，如清单20-42所示。

<Listing number="20-42" file-name="hello_macro_derive/src/lib.rs" caption="使用解析后的Rust代码实现`HelloMacro`特性">

```rust,ignore
{{#rustdoc_include ../listings/ch20-advanced-features/listing-20-42/hello_macro/hello_macro_derive/src/lib.rs:here}}
```

</清单>

我们得到了一个包含使用`ast.ident`定义的注解类型名称的`Ident`结构体实例。清单20-41中的结构体表明，当我们对清单20-37中的代码执行`impl_hello_macro`函数时，得到的`ident`将包含一个值为`"Pancakes"`的`ident`字段。因此，清单20-42中的`name`变量将包含一个`Ident`结构体实例。当打印出来时，将会是字符串`"Pancakes"`，这是清单20-37中结构名的名称。

`quote!`宏允许我们定义想要返回的Rust代码。编译器期望的是`quote!`宏执行后的直接结果之外的东西，因此我们需要将其转换为`TokenStream`格式。我们可以通过调用`into`方法来完成这一转换，该方法会接受这种中间表示形式，并返回所需`TokenStream`类型的值。

`quote!`宏还提供了一些非常实用的模板机制：我们可以输入`#name`，而`quote!`会将其替换为变量`name`中的值。你甚至可以像使用普通宏那样进行重复操作。如需深入了解，请查阅[`quote`框架的文档][quote-docs]。

我们希望我们的过程式宏能够生成针对用户标注的类型的一个实现，这个实现可以通过使用`#name`来获取。该 trait 的实现包含一个名为`hello_macro`的函数，该函数体内包含了我们想要提供的功能：打印`Hello, Macro! My name is`，然后打印被标注类型的名称。

这里使用的`stringify!`宏是Rust内置的。它接受一个Rust表达式，比如`1 + 2`，并在编译时将该表达式转换为字符串字面量，例如`"1 + 2"`。这与`format!`或`println!`不同，后者是评估表达式后将结果转换为`String`的宏。有可能`#name`输入会...为了直接打印出表达式的值，我们使用`stringify!`。同时，使用`stringify!`还可以在编译时将`#name`转换为字符串字面量，从而节省内存分配的开销。

此时，`cargo build`应该在`hello_macro`和`hello_macro_derive`中成功完成。让我们把这些 crate 连接到 Listing20-37 中的代码，以观察 procedural macro 的实际效果！使用`cargo new pancakes`在你的_projects目录下创建一个新的二进制项目。我们需要在`pancakes`crate的_Cargo.toml_文件中添加`hello_macro`和`hello_macro_derive`作为依赖项。如果你正在发布`hello_macro`的版本，那么……将以下内容链接到[crates.io](https://crates.io/)上。它们将是常规的依赖项；如果不是的话，你可以按照以下方式将它们指定为`path`依赖项：

```toml
{{#include ../listings/ch20-advanced-features/no-listing-21-pancakes/pancakes/Cargo.toml:6:8}}
```

将清单20-37中的代码放入`_src/main.rs_`文件中，然后运行__`INLINE_CODE_198__`。应该会打印出__`INLINE_CODE_199__`。程序宏中的__`INLINE_CODE_200__`特性已经实现了，而无需``pancakes``依赖库来实现它；``#[derive(HelloMacro)]``则添加了该特性的实现。

接下来，让我们探讨一下其他类型的过程式宏与自定义`derive`宏之间的区别。

### 类似属性的宏

属性类宏与自定义的``derive``宏类似，但它们不是生成用于``derive``属性的代码，而是允许你创建新的属性。此外，它们更加灵活：``derive``仅适用于结构体和数据类型；而属性则可以应用于其他对象，比如函数。以下是一个使用属性类宏的示例。假设你有一个名为``route``的属性，该属性可以在使用Web应用程序框架时标注函数。

```rust,ignore
#[route(GET, "/")]
fn index() {
```

这个 ``#[route]`` 属性会被框架定义为一个过程式宏。宏定义函数的签名如下所示：

```rust,ignore
#[proc_macro_attribute]
pub fn route(attr: TokenStream, item: TokenStream) -> TokenStream {
```

在这里，我们有两个类型为`TokenStream`的参数。第一个参数用于描述该属性的内容，即`GET, "/"`部分。第二个参数则是该属性所附加到的元素的主体，在本例中，就是`fn index() {}`以及函数的其余部分。

除此之外，属性类宏的工作原理与自定义``derive``宏相同：你可以创建一个使用``proc-macro``类型的 crate，然后实现一个函数来生成你想要生成的代码！

### 类似函数的宏

类函数的宏定义方式类似于函数调用。与`macro_rules!`宏类似，它们比普通函数更灵活；例如，它们可以接受任意数量的参数。不过，`macro_rules!`宏只能使用我们在[“Declarative Macros for General Metaprogramming”][decl]这一节中讨论的匹配语法来定义。类函数的宏会接受一个`TokenStream`参数，并且它们的定义方式也与此类似。使用Rust代码来操作`TokenStream`，就像其他两种过程式宏一样。一个类似函数的宏是`sql!`宏，它的调用方式如下：

```rust,ignore
let sql = sql!(SELECT * FROM posts WHERE id=1);
```

这个宏会解析其中的SQL语句，并检查其语法是否正确。这比`macro_rules!`宏所能处理的复杂得多。`sql!`宏的定义如下：

```rust,ignore
#[proc_macro]
pub fn sql(input: TokenStream) -> TokenStream {
```

这个定义与自定义宏 ``derive`` 的签名类似：我们接收括号内的标记，并返回我们想要生成的代码。

## 摘要

哇！现在你的工具箱里有一些Rust特性，你可能不会经常使用它们，但你会知道在特定的情况下可以使用这些特性。我们介绍了几个复杂的主题，这样当你在错误消息、建议或者别人的代码中遇到这些概念时，就能识别它们以及相关的语法。可以将这一章作为参考，帮助你找到解决方案。

接下来，我们将把本书中讨论的所有内容付诸实践，再完成一个项目！

[参考]:../reference/macros-by-example.html  
[tlborm]: https://veykril.github.io/tlborm/  
[syn]: https://crates.io/crates/syn  
[quote]: https://crates.io/crates/quote  
[syn-docs]: https://docs.rs/syn/2.0/syn/struct.DeriveInput.html  
[quote-docs]: https://docs.rs/quote  
[decl]: #declarative-macros-with-macro_rules-for-general-metaprogramming