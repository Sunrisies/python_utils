## 包和 crate

我们将首先介绍模块系统中的两个基本概念：包和 crate。

一个“crate”是Rust编译器在某一时刻会考虑的最小代码单位。即使你运行的是 `rustc` 而不是 `cargo`，并且只传递一个源代码文件（就像我们在第1章的[“Rust程序基础”][basics]<!-- ignore
-->中做的那样），编译器仍然会将该文件视为一个crate。一个crate可以包含多个模块，而这些模块可能定义在其他文件中，并且这些文件也会随着crate一起被编译，我们将在后续章节中详细了解这一点。

crate 有两种形式：二进制 crate 和 library crate。
_二进制 crate_ 是可以编译成可执行文件并运行的程序，比如命令行程序或服务器。每个二进制 crate 都必须有一个名为`main`的函数，该函数定义了可执行文件运行时会发生什么。到目前为止，我们创建的所有 crate 都是二进制 crate。

库包并没有 `main` 这个函数，它们也不会编译成可执行文件。相反，它们定义了旨在与多个项目共享的功能。例如，我们在[第2章][rand]<!-- ignore -->中使用的 `rand` 库，提供了生成随机数的功能。大多数时候，当 Rustaceans 提到“crate”时，他们指的是库包，并且他们会将“crate”与“库”这一常见的编程概念互换使用。

`_crate root_`是一个源文件，Rust编译器从它开始编译，它构成了你的crate的根模块（我们将在[“使用模块控制作用域和隐私”][modules]<!-- ignore -->中详细解释模块）。

一个**包**是由一个或多个 crate组成的集合，这些 crate共同提供一组功能。一个包包含一个`Cargo.toml`文件，该文件描述了如何构建这些 crate。实际上，Cargo本身就是一个包，它包含了用于构建代码的命令行工具的二进制 crate。Cargo包还包含一个库 crate，而该二进制 crate依赖于这个库 crate。其他项目也可以依赖Cargo库 crate，以使用与Cargo命令行工具相同的逻辑。

一个包可以包含任意数量的二进制包，但最多只能包含一个库包。一个包必须至少包含一个包，无论是库包还是二进制包。

让我们来看看创建包时会发生什么。首先，我们输入命令 `cargo new my-project`:

```console
$ cargo new my-project
     Created binary (application) `my-project` package
$ ls my-project
Cargo.toml
src
$ ls my-project/src
main.rs
```

在我们运行 `cargo new my-project` 之后，我们使用 `ls` 来查看 Cargo 创建了什么。在 _my-project_ 目录下，有一个 _Cargo.toml_ 文件，它定义了一个包。此外，还有一个 _src_ 目录，其中包含了 _main.rs_ 文件。打开 _Cargo.toml_ 文件，你会注意到其中并没有提到 _src/main.rs_ 这样的路径。Cargo 遵循这样的约定：_src/main.rs_ 是一个二进制包的根目录，该包的名称与所定义的包名称相同。同样地，如果包目录中包含 _src/lib.rs_ 文件，那么包就包含一个与包名称相同的库包，而 _src/lib.rs_ 就是该库包的根目录。Cargo 会将这些根目录文件传递给 `rustc` 以构建库或二进制文件。

在这里，我们有一个仅包含 _src/main.rs_ 的包，这意味着它只包含一个名为 `my-project` 的二进制包。如果一个包同时包含 _src/main.rs_ 和 _src/lib.rs_，那么这个包就包含两个包：一个二进制包和一个库包，这两个包的名称都与该包相同。通过在 _src/bin_ 目录下放置文件，一个包可以包含多个二进制包：每个文件都将成为一个独立的二进制包。

[basics]: ch01-02-hello-world.html#rust-program-basics
[modules]: ch07-02-defining-modules-to-control-scope-and-privacy.html
[rand]: ch02-00-guessing-game-tutorial.html#generating-a-random-number
