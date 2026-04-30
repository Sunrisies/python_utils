## 宏

在本书中，我们一直使用像 `println!` 这样的宏，但并没有完全探讨什么是宏以及它的工作原理。术语“宏”指的是 Rust 中一系列特性——包括带有 `macro_rules!` 的声明性宏，以及三种类型的过程性宏：

- 自定义宏，用于指定添加了 `derive` 属性的代码
  这些宏适用于结构和枚举类型
- 类似属性的宏，用于定义可在任何项目上使用的自定义属性
- 函数式宏，看起来像函数调用，但实际上是对作为参数传递的标记进行操作

我们将依次讨论这些内容，但首先，让我们看看为什么在我们已经有函数的情况下，我们仍然需要宏。

### 宏与函数的区别

从根本上说，宏是一种编写其他代码的方式，这被称为_元编程_。在附录C中，我们讨论了 `derive` 属性，它可以为你生成各种特性的实现。在整本书中，我们也使用了 `println!` 和 `vec!` 宏。所有这些宏都能生成比你手动编写的代码更多的代码。

元编程有助于减少需要编写和维护的代码量，这也是函数的功能之一。然而，宏还具有函数所没有的一些额外功能。

函数签名必须声明函数的参数数量和类型。而宏则可以接受任意数量的参数：我们可以调用 `println!("hello")` 时只使用一个参数，或者调用 `println!("hello {}", name)` 时使用两个参数。此外，宏在编译器解释代码含义之前就已经被展开，因此宏可以例如在给定的类型上实现某个特性。而函数则无法做到这一点，因为函数是在运行时被调用的，而特性则需要在编译时实现。

采用宏而不是函数进行实现的缺点是，宏的定义比函数定义更为复杂，因为你需要编写Rust代码来编写Rust代码。由于这种间接性的原因，宏定义通常比函数定义更难以阅读、理解和维护。

宏和函数的另一个重要区别在于，你必须先定义宏或将其带入作用域，然后才能在文件中调用它们。而函数则可以随时随地定义和调用。

<!-- Old headings. Do not remove or links may break. -->

<a id="declarative-macros-with-macro_rules-for-general-metaprogramming"></a>

### 用于通用元编程的声明式宏

在Rust中，最广泛使用的宏形式就是声明性宏。这些宏有时也被称为“示例宏”、“`macro_rules!`宏”，或者简单地称为“宏”。从根本上说，声明性宏允许你编写类似于Rust `match`表达式的内容。正如第6章所讨论的，`match`表达式是一种控制结构，它接受一个表达式，将该表达式的结果值与某些模式进行比较，然后执行与匹配模式相关的代码。宏还会将值与特定代码相关的模式进行比较：在这种情况下，值就是传递给宏的Rust源代码字面量；模式则与该源代码的结构进行比较；当某个模式匹配时，与该模式相关的代码会替换传递给宏的代码。所有这些都在编译过程中完成。

要定义一个宏，可以使用 `macro_rules!` 构造符。让我们通过查看 `vec!` 宏的定义来学习如何使用 `macro_rules!`。第8章介绍了如何使用 `vec!` 宏来创建一个具有特定值的向量。例如，以下宏会创建一个包含三个整数的新向量：

```rust
let v: Vec<u32> = vec![1, 2, 3];
```

我们还可以使用 `vec!` 宏来创建一个由两个整数组成的向量，或者一个包含五个字符串切片的向量。我们无法使用函数来实现同样的功能，因为我们无法在事先知道数值的数量或类型的情况下进行运算。

清单20-35展示了一个稍微简化的`vec!`宏的定义。

**清单 20-35:** *src/lib.rs* — `vec!` 宏定义的简化版本

```rust,noplayground
#[macro_export]
macro_rules! vec {
    ( $( $x:expr ),* ) => {
        {
            let mut temp_vec = Vec::new();
            $(
                temp_vec.push($x);
            )*
            temp_vec
        }
    };
}

```

>注意：标准库中 `vec!` 宏的实际定义包括预先分配适当内存的代码。为了简化示例，我们在这里省略了这部分代码，因为它属于优化措施。

注解「 `#[macro_export]` 」表示，只要定义了该宏的 crate 被带入到作用域中，这个宏就应该被启用。如果没有这个注解，那么这个宏就无法被带入到作用域中。

然后，我们以 `macro_rules!` 开始宏定义，并指定我们正在定义的宏的名称，同时省略了感叹号。在这种情况下，宏的名称是 `vec`，随后是表示宏定义主体的花括号。

在 `vec!` 体内的结构与 `match` 表达式的结构类似。这里我们有一个包含 `( $( $x:expr ),* )` 模式的臂，接着是 `=>` 以及与该模式相关的代码块。如果模式匹配，那么相关的代码块将被输出。由于这是该宏中唯一的模式，因此只有一种有效的匹配方式；任何其他模式都会导致错误。更复杂的宏会有多个臂。

在宏定义中使用的有效模式语法与第19章中介绍的模式语法不同，因为宏模式是依据Rust代码的结构来匹配的，而不是依据具体的值。让我们来了解一下清单20-29中的模式元素所代表的含义；关于完整的宏模式语法，请参阅 [Rust
Reference][ref] 部分。

首先，我们使用一组括号来包围整个模式。我们使用美元符号 (`$`) 在宏系统中声明一个变量，该变量将包含与模式匹配的Rust代码。美元符号明确表示这是一个宏变量，而不是普通的Rust变量。接下来是一组括号，用于捕获与括号内模式匹配的值，以便用于替换代码。在 `$()` 中，有 `$x:expr`，它匹配任何Rust表达式，并将该表达式命名为 `$x`。

在 `$()` 之后的逗号表示，一个实际的逗号分隔字符必须出现在 `$()` 中匹配的代码实例之间。 `*` 表示该模式匹配零个或多个在 `*` 之前的任何内容。

当我们使用 `vec![1, 2, 3];` 调用这个宏时，`$x` 模式会匹配三次，对应的三个表达式分别是 `1`、`2` 和 `3`。

现在让我们看一下与这个模式相关的代码体中的模式：
`temp_vec.push()` 在 `$()*` 中生成，适用于与 `$()` 匹配的每个部分。
根据模式匹配的次数，该模式会在零次或多次出现。`$x` 会被匹配到的每个表达式替换掉。当我们使用 `vec![1, 2, 3];` 调用这个宏时，生成的代码将会是如下内容：

```rust,ignore
{
    let mut temp_vec = Vec::new();
    temp_vec.push(1);
    temp_vec.push(2);
    temp_vec.push(3);
    temp_vec
}
```

我们定义了一个宏，它可以接受任意数量的任意类型的参数，并能够生成代码来创建一个包含指定元素的向量。

如需了解更多关于如何编写宏的信息，请查阅在线文档或其他资源，例如由 Daniel Keep 发起、Lukas Wirth 继续编写的文档。

### 基于属性生成代码的 procedural 宏

第二种宏的形式是过程式宏，它的行为更类似于函数（实际上是一种过程）。过程式宏接受一些代码作为输入，对这段代码进行操作，然后产生一些代码作为输出。与声明式宏不同的是，过程式宏不是通过匹配模式来替换代码，而是直接对代码进行操作。过程式宏有三种类型：自定义过程式宏、类似属性的过程式宏以及类似函数的过程式宏。这三种类型的工作方式都类似。

在创建过程性宏时，其定义必须位于一个专门的 crate 中，且该 crate 具有特殊的类型。这一做法出于复杂的技术原因，我们希望在未来能够取消这一做法。在 Listing 20-36 中，我们展示了如何定义一个过程性宏，其中 `some_attribute` 是用于使用特定宏类型的占位符。

**清单 20-36:** *src/lib.rs* — 定义一个过程性宏的示例

```rust,ignore
use proc_macro::TokenStream;

#[some_attribute]
pub fn some_name(input: TokenStream) -> TokenStream {
}
```

定义过程宏的函数接收一个 `TokenStream` 作为输入，并生成一个 `TokenStream` 作为输出。 `TokenStream` 类型是由 Rust 中包含的 `proc_macro` crate 定义的，它代表一系列标记。这是宏的核心：宏操作的源代码构成了输入 `TokenStream`，而宏生成的代码则是输出 `TokenStream`。该函数还附带一个属性，用于指定我们正在创建的是哪种过程宏。在同一个 crate 中，我们可以拥有多种类型的过程宏。

让我们来看看不同类型的过程式宏。我们首先从自定义的 `derive` 宏开始，然后解释那些使其他形式不同的细微差别。

<!-- Old headings. Do not remove or links may break. -->

<a id="how-to-write-a-custom-derive-macro"></a>

### 自定义 `derive` 宏

让我们创建一个名为 `hello_macro` 的 crate，该 crate 定义了一个名为 `HelloMacro` 的 trait，并附带了一个名为 `hello_macro` 的函数。与其让用户为他们的每种类型实现 `HelloMacro` trait，不如提供一个过程式宏，这样用户就可以用 `#[derive(HelloMacro)]` 来注释他们的类型，从而获得 `hello_macro` 函数的默认实现。默认实现会打印出 `Hello, Macro! My name is
TypeName!`，其中 `TypeName` 是定义该 trait 的类型名称。换句话说，我们将创建一个 crate，让其他程序员能够使用我们的 crate 编写像 Listing 20-37 这样的代码。

**列表 20-37:** *src/main.rs* — 当用户使用我们的过程式宏时，可以编写的代码

```rust,ignore,does_not_compile
use hello_macro::HelloMacro;
use hello_macro_derive::HelloMacro;

#[derive(HelloMacro)]
struct Pancakes;

fn main() {
    Pancakes::hello_macro();
}

```

这段代码会在我们完成时打印出 `Hello, Macro! My name is Pancakes!`。第一步是创建一个新的库 crate，就像这样：

```console
$ cargo new hello_macro --lib
```

接下来，在清单 20-38 中，我们将定义 `HelloMacro` 特征及其相关函数。

<Listing file-name="src/lib.rs" number="20-38" caption="A simple trait that we will use with the `derive` macro">

```rust,noplayground
pub trait HelloMacro {
    fn hello_macro();
}

```

</Listing>

我们有一个特质及其函数。此时，我们的 crate 用户可以实现该特质，以达成所需的功能，如清单 20-39 所示。

**列表 20-39:** *src/main.rs* — 如果用户编写了 `HelloMacro` trait 的手动实现，它会是什么样子

```rust,ignore
use hello_macro::HelloMacro;

struct Pancakes;

impl HelloMacro for Pancakes {
    fn hello_macro() {
        println!("Hello, Macro! My name is Pancakes!");
    }
}

fn main() {
    Pancakes::hello_macro();
}

```

不过，他们需要对每一种他们想要使用的类型编写实现代码，即 `hello_macro`; 我们希望避免让他们自己来完成这项工作。

此外，我们还无法为 `hello_macro` 函数提供默认实现，该函数能够打印出该特质所实现的类型的名称。因为在 Rust 中并没有反射功能，所以无法在运行时查询类型的名称。我们需要一个宏来在编译时生成相应的代码。

下一步是定义过程式宏。在撰写本文时，过程式宏需要位于自己的 crate 中。不过，这一限制可能会在未来被取消。构建 crate 和宏 crate 的惯例如下：对于一个名为 `foo` 的 crate，会创建一个名为 `foo_derive` 的自定义过程式宏 crate。让我们在 `hello_macro` 项目内创建一个新的 crate，名为 `hello_macro_derive`。

```console
$ cargo new hello_macro_derive --lib
```

我们的两个 crate 之间有着紧密的关联，因此我们在 `hello_macro` crate 的目录中创建了 procedural macro crate。如果我们修改 `hello_macro` 中的 trait 定义，那么我们就需要在 `hello_macro_derive` 中修改 procedural macro 的实现。这两个 crate 需要分别发布，使用这些 crate 的程序员需要将其都添加为依赖项，并将其纳入他们的代码范围。我们也可以选择让 `hello_macro` crate 以 `hello_macro_derive` 为依赖项，并重新导出 procedural macro 代码。然而，由于我们项目的结构设计，即使程序员不希望使用 `derive` 的功能，他们仍然可以使用 `hello_macro`。

我们需要将 `hello_macro_derive` crate 声明为一个过程性宏 crate。此外，我们还需要 `syn` 和 `quote` crates 中的功能，正如你稍后会看到的，因此我们需要将它们作为依赖项添加到 _Cargo.toml_ 文件中。在 _Cargo.toml_ 文件中添加以下内容以引用 `hello_macro_derive`：

<Listing file-name="hello_macro_derive/Cargo.toml">

```toml
[lib]
proc-macro = true

[dependencies]
syn = "2.0"
quote = "1.0"

```

</Listing>

要开始定义这个过程性宏，请将清单20-40中的代码放入你的`_src/lib.rs_`文件中，该文件用于 `hello_macro_derive` crate。请注意，这段代码在添加 `impl_hello_macro` 函数的定义之前是无法编译的。

**清单 20-40:** *hello_macro_derive/src/lib.rs* — 大多数过程式宏库在处理 Rust 代码时都需要使用的代码

```rust,ignore,does_not_compile
use proc_macro::TokenStream;
use quote::quote;

#[proc_macro_derive(HelloMacro)]
pub fn hello_macro_derive(input: TokenStream) -> TokenStream {
    // Construct a representation of Rust code as a syntax tree
    // that we can manipulate.
    let ast = syn::parse(input).unwrap();

    // Build the trait implementation.
    impl_hello_macro(&ast)
}

```

请注意，我们将代码分解为 `hello_macro_derive` 函数，该函数负责解析 `TokenStream`，以及 `impl_hello_macro` 函数，该函数负责转换语法树。这样做使得编写过程式宏更加方便。外部函数中的代码（在这种情况下为 `hello_macro_derive`）对于您看到的或创建的大多数过程式宏 crate 来说都是相同的。而在内部函数的主体中指定的代码（在这种情况下为 `impl_hello_macro`）则会根据您的过程式宏的目的而有所不同。

我们引入了三个新的库：`proc_macro`、[`syn`][syn]<!-- ignore -->和[`quote`][quote]<!-- ignore -->。`proc_macro`库是随Rust一起提供的，因此我们不需要在_Cargo.toml_中将其添加到依赖项中。`proc_macro`库是编译器的API，它允许我们读取和操作Rust代码。

The `syn` crate 能够将 Rust 代码从字符串解析为我们可以操作的数据结构。而 `quote` crate 则可以将这些数据结构重新转换为 Rust 代码。这些工具使得解析任何类型的 Rust 代码变得更加简单：为 Rust 代码编写完整的解析器并非易事。

当我们的库的用户在某种类型上指定 `#[derive(HelloMacro)]` 时，将会调用 `hello_macro_derive` 函数。这是可能的，因为我们已经在 `hello_macro_derive` 函数上添加了 `proc_macro_derive` 注释，并指定了名称 `HelloMacro`，这个名称与我们使用的特性名称相匹配。这是大多数过程性宏所遵循的惯例。

函数 `hello_macro_derive` 首先将 `input` 转换为一种数据结构，我们可以对其进行解析并对其进行操作。这时， `syn` 就发挥作用了。 `parse` 函数在 `syn` 中接收一个 `TokenStream`，并返回一个 `DeriveInput` 结构体，用于表示解析后的 Rust 代码。列表 20-41 展示了从解析 `struct Pancakes;` 字符串中得到的 `DeriveInput` 结构体的相关部分。

<Listing number="20-41" caption="The `DeriveInput` instance we get when parsing the code that has the macro’s attribute in Listing 20-37">

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

</Listing>

这个结构的字段表明，我们解析出的 Rust 代码是一个单元结构，其名称为 `ident`(_identifier_, 即名称) `Pancakes`。这个结构还有更多的字段，用于描述各种 Rust 代码；如需更多信息，请参考 [`syn`
documentation for `DeriveInput`][syn-docs]。

很快我们将定义 `impl_hello_macro` 函数，这是我们构建新 Rust 代码的地方。但在那之前，请注意 `derive` 宏的输出也是一个 `TokenStream`。返回的 `TokenStream` 会被添加到我们的 crate 用户所编写的代码中，因此当他们编译他们的 crate 时，他们将获得我们在修改后的 `TokenStream` 中提供的额外功能。

你可能已经注意到，我们调用 `unwrap` 是为了在调用 `syn::parse` 函数失败时，让 `hello_macro_derive` 函数产生 panic 错误。出于程序性宏的需求，当发生错误时让这些函数产生 panic 是必须的，因为 `proc_macro_derive` 函数必须返回 `TokenStream` 而不是 `Result`，这样才能符合程序性宏的 API 规范。我们通过使用 `unwrap` 来简化了这个示例；在实际代码中，你应该使用 `panic!` 或 `expect` 来提供更具体的错误信息，说明发生了什么错误。

现在我们已经有了将注释过的 Rust 代码从 `TokenStream` 转换为 `DeriveInput` 实例的代码，接下来我们将生成在注释过的类型上实现 `HelloMacro` 特性的代码，如 Listing 20-42 所示。

**清单 20-42:** *hello_macro_derive/src/lib.rs* — 使用解析后的 Rust 代码实现 `HelloMacro` 特性

```rust,ignore
fn impl_hello_macro(ast: &syn::DeriveInput) -> TokenStream {
    let name = &ast.ident;
    let generated = quote! {
        impl HelloMacro for #name {
            fn hello_macro() {
                println!("Hello, Macro! My name is {}!", stringify!(#name));
            }
        }
    };
    generated.into()
}

```

我们得到了一个包含使用 `ast.ident` 标记的注释类型名称的 `Ident` 结构实例。清单 20-41 中的结构表明，当我们对清单 20-37 中的代码运行 `impl_hello_macro` 函数时，我们得到的 `ident` 将包含一个值为 `"Pancakes"` 的 `ident` 字段。因此，清单 20-42 中的 `name` 变量将包含一个 `Ident` 结构实例，当打印该实例时，将会显示字符串 `"Pancakes"`，即清单 20-37 中结构的名称。

在 `quote!` 宏中，我们可以定义我们想要返回的 Rust 代码。编译器期望的是 `quote!` 宏执行后的直接结果之外的东西，因此我们需要将其转换为 `TokenStream` 形式。我们可以通过调用 `into` 方法来完成这一转换，该方法接受这种中间表示形式，并返回所需 `TokenStream` 类型的值。

这个 `quote!` 宏还提供了一些非常酷的模板机制：我们可以输入 `#name`，而 `quote!` 会将其替换为变量 `name` 中的值。你甚至可以像普通宏那样进行重复操作。想要深入了解的话，可以查看 [the `quote` crate’s docs][quote-docs] 的相关介绍。

我们希望我们的过程式宏能够生成针对用户标注的类型的一个实现，这个实现可以通过使用 `#name` 来获取。该实现包含一个名为 `hello_macro` 的函数，该函数的体内包含了我们想要提供的功能：打印 `Hello, Macro! My name is` 以及被标注类型的名称。

这里使用的 `stringify!` 宏是 Rust 内置的。它接受一个 Rust 表达式，例如 `1 + 2`，并在编译时将该表达式转换为字符串字面量，例如 `"1 + 2"`。这与 `format!` 或 `println!` 不同，后者是宏，它们先评估表达式，然后将结果转换为 `String`。需要注意的是， `#name` 的输入可能是一个需要直接打印的表达式，因此我们使用 `stringify!`。使用 `stringify!` 还可以通过在编译时将 `#name` 转换为字符串字面量来避免内存分配的开销。

此时， `cargo build` 应该在 `hello_macro` 和 `hello_macro_derive` 中成功完成。让我们把这些 crate 连接到 Listing 20-37 中的代码，以观察这个过程性宏的效果！在 _projects_ 目录下使用 `cargo new pancakes` 创建一个新的二进制项目。我们需要在 `pancakes` crate 的 _Cargo.toml_ 文件中添加 `hello_macro` 和 `hello_macro_derive` 作为依赖项。如果你将 `hello_macro` 和 `hello_macro_derive` 的版本发布到 [crates.io](https://crates.io/)<!-- ignore -->，那么它们将是常规依赖项；如果不是这样，你可以将它们指定为 `path` 依赖项，具体方法如下：

```toml
[dependencies]
hello_macro = { path = "../hello_macro" }
hello_macro_derive = { path = "../hello_macro/hello_macro_derive" }

```

将代码清单20-37中的内容放入`_src/main.rs_`文件中，然后运行`cargo run`: 应该会输出`Hello, Macro! My name is Pancakes!`。程序宏中的`HelloMacro` trait的实现被直接包含了进来，而无需`pancakes` crate来具体实现它；此外，还添加了`#[derive(HelloMacro)]` trait的实现。

接下来，让我们探讨一下其他类型的过程性宏与自定义宏之间的区别。

### 属性式宏

类似属性的宏与自定义宏类似，但它们不是生成用于 `derive` 属性的代码，而是允许你创建新的属性。此外，这类宏更加灵活： `derive` 仅适用于结构体和集合类型；属性也可以应用于其他元素，比如函数。下面是一个使用类似属性的宏的例子。假设你有一个名为 `route` 的属性，当使用Web应用程序框架时，它可以对函数进行标注。

```rust,ignore
#[route(GET, "/")]
fn index() {
```

这个 `#[route]` 属性会被框架定义为一个过程式宏。宏定义函数的签名如下所示：

```rust,ignore
#[proc_macro_attribute]
pub fn route(attr: TokenStream, item: TokenStream) -> TokenStream {
```

在这里，我们有两个类型为 `TokenStream` 的参数。第一个参数用于属性中的内容：即 `GET, "/"` 部分。第二个参数则是该属性所附加的元素的主体：在这种情况下，就是 `fn index() {}`，以及函数的其余主体。

除此之外，属性类宏的工作方式与自定义 `derive` 宏相同：你创建一个使用 `proc-macro` 类型的 crate，然后实现一个函数来生成你想要生成的代码！

### 函数式宏

类函数的宏定义的是看起来像函数调用的宏。与 `macro_rules!` 宏类似，它们比函数更灵活；例如，它们可以接受未知数量的参数。然而， `macro_rules!` 宏只能使用我们在 [“Declarative
Macros for General Metaprogramming”][decl]<!-- ignore --> 部分讨论过的类似 match 的语法来定义。类函数的宏接受一个 `TokenStream` 参数，并且它们的定义使用 Rust 代码来操作那个 `TokenStream`，就像其他两种过程式宏一样。类函数的宏的一个例子是一个 `sql!` 宏，它的调用方式如下：

```rust,ignore
let sql = sql!(SELECT * FROM posts WHERE id=1);
```

这个宏会解析其中的SQL语句，并检查其语法正确性，这比一个`macro_rules!`宏要复杂得多。`sql!`宏的定义如下：

```rust,ignore
#[proc_macro]
pub fn sql(input: TokenStream) -> TokenStream {
```

这个定义与自定义的 `derive` 宏的签名类似：我们接收括号内的标记，并返回我们想要生成的代码。

## 摘要

哇！现在你的工具箱里有一些Rust特性，虽然你可能不会经常使用它们，但你会知道这些特性在特定情况下是可用的。我们介绍了几个复杂的主题，这样当你在错误消息、建议或者别人的代码中遇到这些主题时，你就能识别这些概念和语法。把这一章当作一个参考，帮助你找到解决方案。

接下来，我们将把本书中讨论的所有内容付诸实践，
再完成一个项目！

[ref]: ../reference/macros-by-example.html
[tlborm]: https://veykril.github.io/tlborm/
[syn]: https://crates.io/crates/syn
[quote]: https://crates.io/crates/quote
[syn-docs]: https://docs.rs/syn/2.0/syn/struct.DeriveInput.html
[quote-docs]: https://docs.rs/quote
[decl]: #declarative-macros-with-macro_rules-for-general-metaprogramming
