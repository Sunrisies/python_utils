## 你好，世界！

既然你已经安装了Rust，现在是时候编写你的第一个Rust程序了。  
在学习新语言时，通常会先编写一个小程序，将文本“ `Hello, world!` ”打印到屏幕上。我们也会这样做！

注意：本书假设读者已经基本熟悉命令行操作。Rust对用户的编辑工具或代码存储位置没有特定要求，因此如果您更喜欢使用集成开发环境（IDE）而不是命令行，请随意选择您喜欢的IDE。如今许多IDE都提供了一定程度的Rust支持；请查阅IDE的文档以获取详细信息。Rust团队一直致力于通过 `rust-analyzer` 来提供出色的IDE支持。更多详情请参见[附录D][devtools]<!-- ignore -->。

<!-- Old headings. Do not remove or links may break. -->
<a id="creating-a-project-directory"></a>

### 项目目录设置

首先，你需要创建一个目录来存放你的 Rust 代码。对于 Rust 来说，代码存储的位置并不重要，但针对本书中的练习和项目，我们建议在你的主目录中创建一个 _projects_ 目录，并将所有的项目都放在那里。

打开终端并输入以下命令，以创建一个名为`_projects_`的目录，以及在该目录中用于存放“Hello, world!”项目的子目录。

对于Linux、macOS以及Windows上的PowerShell，请输入以下内容：

```console
$ mkdir ~/projects
$ cd ~/projects
$ mkdir hello_world
$ cd hello_world
```

在Windows CMD下，请输入以下内容：

```cmd
> mkdir "%USERPROFILE%\projects"
> cd /d "%USERPROFILE%\projects"
> mkdir hello_world
> cd hello_world
```

<!-- Old headings. Do not remove or links may break. -->
<a id="writing-and-running-a-rust-program"></a>

### Rust 程序基础

接下来，创建一个新的源文件，并将其命名为_main.rs_。Rust文件的扩展名通常为_.rs_。如果你在文件名中使用了多个单词，通常可以使用下划线来分隔它们。例如，应该使用_hello_world.rs_而不是_helloworld.rs_。

现在打开你刚刚创建的`_main.rs`文件，并输入列表1-1中的代码。

<Listing number="1-1" file-name="main.rs" caption="A program that prints `Hello, world!`">

```rust
fn main() {
    println!("Hello, world!");
}
```

</Listing>

保存文件后，回到 `_~/projects/hello_world_`目录中的终端窗口。在Linux或MacOS系统中，输入以下命令来编译并运行该文件：

```console
$ rustc main.rs
$ ./main
Hello, world!
```

在Windows系统中，请输入命令 `.\main` 而不是 `./main`。

```powershell
> rustc main.rs
> .\main
Hello, world!
```

无论您使用什么操作系统，字符串 `Hello, world!` 都应该显示在终端上。如果您看不到这个输出，请参考安装部分的[“故障排除”][troubleshooting]<!-- ignore -->章节，了解获取帮助的方法。

如果 `Hello, world!` 确实被打印出来了，恭喜！你正式编写了一个 Rust 程序。这使你成为了一名 Rust 程序员——欢迎加入！

<!-- Old headings. Do not remove or links may break. -->

<a id="anatomy-of-a-rust-program"></a>

### Rust 程序的构成

让我们详细回顾一下这个“Hello, world!”程序。这就是问题的第一个部分：

```rust
fn main() {

}
```

这些行定义了一个名为 `main` 的函数。而 `main` 这个函数很特别：它总是每个可执行的 Rust 程序中首先运行的部分。在这里，第一行定义了一个名为 `main` 的函数，该函数没有参数，并且不返回任何值。如果该函数有参数，那么参数将会放在括号中 (`()`)。

函数体被包裹在 `{}` 中。Rust 要求所有函数体都用大括号包围。将开大括号放在与函数声明相同的行上，并且两者之间保留一个空格，这是一种良好的编程风格。

注意：如果您希望在整个 Rust 项目中保持统一的风格，可以使用一个名为 `rustfmt` 的自动格式化工具来按照特定格式对代码进行格式化。关于 `rustfmt` 的更多信息，请参见[附录 D][devtools]<!-- ignore -->。Rust 团队已经将这一工具作为标准 Rust 发行版的一部分包含进来，因此它应该已经安装在您的计算机上！

`main`函数的主体包含以下代码：

```rust
println!("Hello, world!");
```

这一行代码完成了这个小程序的所有工作：它将文本打印到屏幕上。这里有三个需要注意的重要细节。

首先，`println!` 是一个 Rust 宏。如果它实际上调用的是函数，那么就会被表示为 `println`（而不是 `!`）。Rust 宏是一种编写代码的方式，可以生成扩展 Rust 语法的代码。我们将在[第 20 章][ch20-macros]<!-- ignore -->中详细讨论它们。目前，你只需要知道使用 `!` 意味着你调用的是宏而不是普通函数，而且宏并不总是遵循与函数相同的规则。

其次，你会看到 `"Hello, world!"` 这个字符串。我们将这个字符串作为参数传递给 `println!`，然后该字符串会被打印到屏幕上。

第三，我们在行尾加上一个分号（`;`），这表示这一行已经结束，下一行可以开始了。大多数Rust代码的行都是以分号结尾的。

<!-- Old headings. Do not remove or links may break. -->
<a id="compiling-and-running-are-separate-steps"></a>

### 编译与执行

你刚刚运行了一个新创建的程序，现在让我们逐一检查这个过程中的每个步骤。

在运行一个 Rust 程序之前，你必须使用 Rust 编译器来编译它。具体操作是输入 `rustc` 命令，并传递你的源文件名，如下所示：

```console
$ rustc main.rs
```

如果你有C或C++的背景知识，你会注意到这与`gcc`或`clang`类似。成功编译后，Rust会生成二进制可执行文件。

在 Linux、macOS 以及 Windows 上的 PowerShell 中，您可以通过在 shell 中输入 `ls` 命令来查看可执行文件。

```console
$ ls
main  main.rs
```

在 Linux 和 macOS 上，你会看到两个文件。而在 Windows 上使用 PowerShell 时，你会看到与使用 CMD 时相同的三个文件。在 Windows 上使用 CMD 时，你需要输入以下内容：

```cmd
> dir /B %= the /B option says to only show the file names =%
main.exe
main.pdb
main.rs
```

这里展示了带有 `.rs_` 扩展名的源代码文件、可执行文件（在 Windows 系统是 `_main.exe_`，而在其他平台上则是 `_main_`），以及在使用 Windows 系统时，还包含带有 `.pdb_` 扩展名的调试信息的文件。从这里，你可以像这样运行 `_main_`或`_main.exe`文件。

```console
$ ./main # or .\main on Windows
```

如果你的 _main.rs_ 文件是你的“Hello, world!”程序，那么这一行代码会在你的终端中输出 `Hello,
world!`。

如果你更熟悉像 Ruby、Python 或 JavaScript 这样的动态语言，你可能不习惯将程序的编译和运行分开进行。Rust 是一种 _提前编译_ 的语言，这意味着你可以先编译程序，然后将生成的可执行文件交给其他人，他们甚至不需要安装 Rust 就能运行该程序。如果你给某人一个 `.rb`、`.py` 或 `.js` 文件，那么他们就需要安装相应的 Ruby、Python 或 JavaScript 实现。但在这些语言中，你只需要一条命令就能编译并运行程序。在语言设计中，一切都是权衡的结果。

对于简单的程序来说，使用 `rustc` 进行编译是可行的，但随着项目的增长，你需要管理所有相关选项，并且要方便地分享你的代码。接下来，我们将向您介绍 Cargo 工具，它可以帮助您编写实际的 Rust 程序。

[troubleshooting]: ch01-01-installation.html#troubleshooting
[devtools]: appendix-04-useful-development-tools.html
[ch20-macros]: ch20-05-macros.html
