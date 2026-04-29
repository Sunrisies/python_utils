## 你好，Cargo！

Cargo是Rust的构建系统和包管理器。大多数Rust开发者使用这个工具来管理他们的Rust项目，因为Cargo可以自动处理许多任务，比如编译代码、下载代码所依赖的库，以及编译这些库。（我们称代码所需的那些库为“依赖项”。）

最简单的Rust程序，比如我们目前编写的那个程序，没有任何依赖项。如果我们使用Cargo来构建“Hello, world!”这个项目，那么Cargo只会负责代码编译的部分工作。当你编写更复杂的Rust程序时，就需要添加各种依赖项。而如果你一开始就使用Cargo来创建项目，那么添加依赖项就会变得容易得多。

因为绝大多数Rust项目都使用Cargo，所以本书的其余部分也假设您同样在使用Cargo。如果您使用了在[“安装”][installation]这一节中讨论的官方安装程序，那么Cargo将会随Rust一起安装。如果您是通过其他方式安装Rust的，请在终端中输入以下命令来检查是否安装了Cargo：

```console
$ cargo --version
```

如果你看到版本号，那就说明你已经安装了！如果你看到错误提示，比如“command not found”，那么请查阅相关安装文档，了解如何单独安装 Cargo。

### 使用 Cargo 创建项目

让我们使用Cargo创建一个新的项目，然后看看它与我们原来的“Hello, world!”项目有何不同。回到你的_projects目录中（或者你决定存储代码的任何地方）。然后，在任何操作系统上，运行以下命令：

```console
$ cargo new hello_cargo
$ cd hello_cargo
```

第一个命令创建了一个名为`_hello_cargo_`的新目录和项目。我们将项目命名为`_hello_cargo_`，而Cargo会在同名目录下创建相关文件。

进入 `_hello_cargo_`目录，查看其中的文件。你会看到Cargo为我们生成了两个文件和一个目录：一个`_Cargo.toml_`文件，以及一个包含`_main.rs_`文件的`_src_`目录。

此外，系统还初始化了一个新的Git仓库以及一个_.gitignore_文件。如果你在现有的Git仓库中运行`cargo new`，就不会生成相关的Git文件；你可以使用`cargo new --vcs=git`来覆盖这一行为。

注意：Git是一种常用的版本控制系统。您可以使用`--vcs`标志来将`cargo new`替换为使用其他版本的版本控制系统，或者完全不使用任何版本控制系统。运行`cargo new --help`可以查看可用的选项。

在您选择的文本编辑器中打开 `_Cargo.toml` 文件。它的样子应该与清单1-2中的代码类似。

<Listing number="1-2" file-name="Cargo.toml" caption="*Cargo.toml* 文件中的内容，由 `cargo new` 生成">

```toml
[package]
name = "hello_cargo"
version = "0.1.0"
edition = "2024"

[dependencies]
```

</ Listing>

此文件采用[_TOML_][toml]<!-- ignore --> (_Tom’s Obvious, Minimal Language_)格式，这是Cargo的配置文件格式。

第一行 ``[package]`` 是一个章节标题，表示接下来的语句是用来配置一个包的。随着我们向这个文件添加更多信息，我们会添加更多的章节。

接下来的三行设置了Cargo在编译程序时需要使用的配置信息：程序的名称、版本以及要使用的Rust版本。我们将在[附录E][appendix-e]中讨论`edition`键的相关内容。

最后一行 ``[dependencies]`` 是一个用于列出项目依赖项的区域。在Rust中，代码包被称为`_crates_`。对于这个项目来说，我们不需要其他crates，但在第2章的第一个项目中会用到其他crates，所以届时我们会使用这个依赖项部分来列出它们。

现在打开 `_src/main.rs_`文件，看看里面的内容：

<span class="filename">文件名：src/main.rs</span>

```rust
fn main() {
    println!("Hello, world!");
}
```

Cargo已经为你生成了一个“Hello, world!”程序，就像我们在清单1-1中编写的那个程序一样！到目前为止，我们的项目与Cargo生成的项目之间的区别在于，Cargo将代码放置在了`_src_`目录下，而我们的项目则会在顶级目录中有一个`_Cargo.toml_`配置文件。

Cargo要求你的源文件必须位于`_src_`目录下。顶层项目目录主要用于存放README文件、许可证信息、配置文件以及与代码无关的其他内容。使用Cargo可以帮助你更好地组织项目。每个东西都有它自己的位置，所有东西都放在了正确的地方。

如果你启动了一个不使用 Cargo 的项目，就像我们处理“Hello, world!”项目那样，你可以将其转换为一个使用 Cargo 的项目。将项目代码移动到 _src_ 目录中，并创建一个合适的 _Cargo.toml_ 文件。获取该 _Cargo.toml_ 文件的简单方法是运行 `cargo init`，它会自动为你创建这个文件。

### 构建并运行Cargo项目

现在让我们看看使用Cargo构建并运行“Hello, world!”程序时有什么不同！从你的`_hello_cargo_`目录中，通过输入以下命令来构建你的项目：

```console
$ cargo build
   Compiling hello_cargo v0.1.0 (file:///projects/hello_cargo)
    Finished dev [unoptimized + debuginfo] target(s) in 2.85 secs
```

此命令会创建一个可执行文件，存放于`_target/debug/hello_cargo_`目录下（在Windows系统中则存放在`Target\debug\hello_cargo.exe`文件中），而不是当前目录中。由于默认构建方式为调试版本，因此Cargo会将二进制文件放置于名为`_debug_`的目录下。您可以使用以下命令来运行这个可执行文件：

```console
$ ./target/debug/hello_cargo # or .\target\debug\hello_cargo.exe on Windows
Hello, world!
```

如果一切顺利，`Hello, world!`应该会显示在终端上。第一次运行`cargo build`时，Cargo还会在顶层创建一个新文件：_Cargo.lock_。这个文件记录了项目中依赖库的精确版本。由于这个项目没有依赖库，所以这个文件的内容相对简单。你永远不需要手动修改这个文件；Cargo会自动管理其内容。

我们刚刚使用`cargo build`构建了一个项目，并使用`./target/debug/hello_cargo`来运行它。不过，我们也可以使用`cargo run`来编译代码，然后一次性命令就运行出最终的可执行文件：

```console
$ cargo run
    Finished dev [unoptimized + debuginfo] target(s) in 0.0 secs
     Running `target/debug/hello_cargo`
Hello, world!
```

使用 ``cargo run`` 比需要记住运行 `cargo build__` 和 `cargo run` 要方便得多。

请注意，这次我们没有看到表明Cargo正在编译的输出信息。Cargo判断出文件没有发生变化，因此没有重新构建项目，而是直接运行了二进制文件。如果您修改了源代码，Cargo会在运行之前重新构建项目，这时您就会看到这样的输出信息。

```console
$ cargo run
   Compiling hello_cargo v0.1.0 (file:///projects/hello_cargo)
    Finished dev [unoptimized + debuginfo] target(s) in 0.33 secs
     Running `target/debug/hello_cargo`
Hello, world!
```

Cargo还提供了一个名为`cargo check`的命令。这个命令可以快速检查你的代码，确保它能够编译，但不会生成可执行文件。

```console
$ cargo check
   Checking hello_cargo v0.1.0 (file:///projects/hello_cargo)
    Finished dev [unoptimized + debuginfo] target(s) in 0.32 secs
```

为什么你不想要一个可执行文件呢？通常，`cargo check`比`cargo build`快得多，因为它省去了生成可执行文件的步骤。如果你在编写代码时不断检查自己的工作情况，使用`cargo check`可以加快通知你项目是否仍在编译的过程！因此，许多Rust开发者在编写程序时会定期运行`cargo check`来确保程序能够成功编译。然后，当他们准备使用可执行文件时，就会运行`cargo build`。

让我们回顾一下到目前为止我们学到的关于Cargo的知识：

- 我们可以使用 `cargo new` 来创建一个项目。  
- 我们可以使用 `cargo build` 来构建项目。  
- 我们可以使用 `cargo run` 一步完成项目的构建和运行。  
- 我们可以使用 `cargo check` 来构建项目，而无需生成二进制文件以检查错误。  
- 与将构建结果保存在与代码相同的目录中不同，Cargo会将构建结果存储在 _target/debug_ 目录下。

使用Cargo的另一个优势是，无论你使用的是哪种操作系统，相关的命令都是相同的。因此，目前我们不再提供针对Linux和macOS与Windows的具体操作指南了。

### 构建发布版本

当您的项目终于准备好发布时，您可以使用`cargo build --release`命令来优化编译过程。该命令会生成位于`_target/release_`目录中的可执行文件，而不是`_target/debug_`目录中的文件。虽然优化可以使得Rust代码的运行速度更快，但启用优化也会延长程序的编译时间。因此，存在两种不同的编译配置：一种用于开发阶段，此时需要频繁地重新构建程序；另一种则用于最终版本的构建，这种版本将不会被反复重新构建，并且会尽可能快地运行。如果您正在对代码的运行时间进行基准测试，请务必使用`_target/release_`目录中的可执行文件来进行测试。

<a id="cargo-as-convention"></a>

### 利用 Cargo 的规范

对于简单的项目来说，Cargo并没有比直接使用`rustc`提供更多的价值，但随着程序变得越来越复杂，Cargo的优势就显现出来了。一旦程序需要扩展到多个文件或者依赖其他库时，让Cargo来协调构建过程会变得更加简单。

尽管`hello_cargo`这个项目很简单，但它现在使用了许多你在后续的Rust开发过程中会使用的工具。实际上，要处理任何现有的项目，你可以使用以下命令来检出代码：使用Git，进入该项目的目录，然后进行构建。

```console
$ git clone example.org/someproject
$ cd someproject
$ cargo build
```

如需了解更多关于Cargo的信息，请查阅其[文档][cargo]。

## 总结

你的Rust学习之旅已经取得了良好的开端！在这一章中，你学习了如何：

- 使用 `rustup` 安装最新稳定的 Rust 版本。  
- 更新到更新的 Rust 版本。  
- 打开本地安装的文档。  
- 直接使用 `rustc` 编写并运行 “Hello, world!” 程序。  
- 按照 Cargo 的规范创建并运行一个新的项目。

现在是时候构建一个更完整的程序了，以便逐渐习惯阅读和理解Rust代码。因此，在第二章中，我们将开发一个猜谜游戏程序。如果你更愿意先了解常见的编程概念在Rust中的实现方式，可以先阅读第三章，然后再回到第二章。

[安装]: ch01-01-installation.html#installation  
[toml]: https://toml.io  
[附录E]: appendix-05-editions.html  
[Cargo]: https://doc.rust-lang.org/cargo/