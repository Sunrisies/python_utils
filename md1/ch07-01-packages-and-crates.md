## 软件包与包

我们将首先介绍模块系统中的两个基本概念：包和 crate。

一个“crate”是Rust编译器在某一时刻会考虑的最小代码单位。即使您运行的是`rustc`而不是`cargo`，并且只传递一个源代码文件（就像我们在第一章的[“Rust程序基础”][basics]中所做的那样），编译器仍然会将该文件视为一个crate。Crates可以包含模块，而这些模块可能定义在其他文件中，并且这些文件也会随crate一起被编译，我们将在后续章节中详细了解这一点。

crate有两种形式：二进制 crate 和库 crate。  
_二进制 crate_ 是可以编译成可执行文件并运行的程序，比如命令行程序或服务器。每个二进制 crate 都必须有一个名为 `main` 的函数，该函数定义了可执行文件运行时会发生什么。到目前为止，我们创建的所有 crate 都是二进制 crate。

这些库没有`main`这个函数，它们也不会编译成可执行文件。相反，它们定义了旨在与多个项目共享的功能。例如，我们在[第2章][rand]<!-- ignore -->中使用的`rand`库提供了生成随机数的功能。大多数时候，当Rustaceans提到“crate”时，他们指的是库库，并且他们会将“crate”与“库”这一常见的编程概念互换使用。

`_crate根_是一个源文件，Rust编译器从这里开始编译，它构成了你的crate的根模块（我们将在[“使用模块控制作用域和隐私”][modules]中详细解释模块）。

一个**包**是由一个或多个 crate组成的集合，它们共同提供一组功能。每个包都包含一个`Cargo.toml`文件，该文件描述了如何构建这些crate。实际上，Cargo本身就是一个包，它包含了用于构建代码的命令行工具的二进制crate。此外，Cargo包还包含了一个库crate，而该二进制crate依赖于这个库crate。其他项目也可以依赖Cargo的库crate，以使用与Cargo命令行工具相同的逻辑。

一个包可以包含任意数量的二进制包，但最多只能包含一个库包。一个包必须至少包含一个包，无论是库包还是二进制包。

让我们来看看创建包时会发生什么。首先，我们执行命令`cargo new my-project`：

```console
$ cargo new my-project
     Created binary (application) `my-project` package
$ ls my-project
Cargo.toml
src
$ ls my-project/src
main.rs
```

在我们执行 `cargo new my-project` 之后，我们使用 `ls` 来查看 Cargo 会创建什么。在 _my-project_ 目录下，有一个 _Cargo.toml_ 文件，它定义了一个包。此外，还有一个 _src_ 目录，其中包含了 _main.rs_ 文件。打开 _Cargo.toml_ 文件，你会注意到里面并没有提到 _src/main.rs_ 这样的结构。Cargo 遵循一种约定：_src/main.rs_ 被视为同名二进制包的包根。同样地，如果包目录中包含 _src/lib.rs_ 文件，那么包就包含一个与包同名的内置库包，而 _src/lib.rs_ 就是该内置库的包根。Cargo 会将包根文件传递给 `rustc` 以构建库或二进制文件。

在这里，我们有一个仅包含`_src/main.rs_`的包，这意味着它只包含一个名为`my-project`的二进制包。如果一个包同时包含`_src/main.rs_`和`_src/lib.rs`，那么它就有两个包：一个二进制包和一个库，这两个包的名称都与该包相同。通过在`_src/bin_`目录下放置文件，一个包可以拥有多个二进制包：每个文件都将成为一个独立的二进制包。

[基础知识]: ch01-02-hello-world.html#rust-program-basics
[模块介绍]: ch07-02-defining-modules-to-control-scope-and-privacy.html
[随机数生成]: ch02-00-guessing-game-tutorial.html#generating-a-random-number