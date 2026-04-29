## 你好，世界！

现在你已经安装了Rust，是时候编写你的第一个Rust程序了。  
在学习新语言时，通常会编写一个小程序来打印文本`Hello, world!`到屏幕上，我们也会这样做！

注意：本书假设读者已经基本熟悉命令行操作。Rust对用户的编辑工具或代码存储位置没有特殊要求，因此如果您更喜欢使用集成开发环境而不是命令行，请随时使用您喜欢的IDE。现在许多IDE都提供了一定程度的Rust支持；请查阅相关IDE的文档以获取详细信息。Rust团队一直致力于通过`rust-analyzer`来实现出色的IDE支持。更多详情请参阅[附录D][devtools]<!-- ignore -->。

<!-- 旧的标题。不要删除，否则链接可能会失效。 -->
<a id="创建项目目录"></a>

### 项目目录设置

首先，你需要创建一个目录来存放你的Rust代码。对于Rust来说，代码存储的位置并不重要，但针对本书中的练习和项目，我们建议在你的主目录中创建一个`_projects_`目录，并将所有的项目都放在那里。

打开终端并输入以下命令，以创建一个名为`_projects_`的目录，以及在该目录中用于存放“Hello, world!”项目的子目录。

对于Linux、macOS以及Windows上的PowerShell系统，请输入以下内容：

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

<!-- 旧的标题。不要删除，否则链接可能会失效。 -->
<a id="writing-and-running-a-rust-program"></a>

### Rust 程序基础

接下来，创建一个新的源文件，并将其命名为_main.rs_。Rust文件的扩展名通常为_.rs_。如果你在文件名中使用了多个单词，按照惯例使用下划线来分隔它们。例如，应该使用_hello_world.rs_而不是_helloworld.rs_。

现在打开你刚刚创建的`_main.rs_`文件，并在其中输入清单1-1中的代码。

<列表编号="1-1" 文件名称="main.rs" 标题="一个打印 `Hello, world!` 的程序">

```rust
fn main() {
    println!("Hello, world!");
}
```

</ Listing>

保存文件后，回到 `_~/projects/hello_world_`目录中的终端窗口。在Linux或MacOS系统中，输入以下命令来编译并运行该文件：

```console
$ rustc main.rs
$ ./main
Hello, world!
```

在Windows系统中，请输入命令`.\main`而不是`./main`：

```powershell
> rustc main.rs
> .\main
Hello, world!
```

无论您使用什么操作系统，字符串 `Hello, world!` 都应该显示在终端上。如果您看不到这个输出，请参考安装部分的“故障排除”部分，了解获取帮助的方法。

如果 `Hello, world!` 真的被打印出来了，那真是太好了！你正式编写了一个Rust程序。这让你成为了一名Rust程序员——欢迎加入这个大家庭！

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="rust程序的构成"></a>

### Rust程序的构成要素

让我们详细回顾一下这个“Hello, world!”程序。这就是问题的第一个部分：

```rust
fn main() {

}
```

这些行定义了一个名为 ``main``的函数。``main``这个函数很特别：它总是每个可执行的Rust程序中首先运行的代码。在这里，第一行定义了一个名为 ``main``的函数，该函数没有参数，也不返回任何值。如果有参数存在，它们会放在括号内（``()``）。

该函数体被封装在`{}`中。Rust要求所有函数体都用大括号包围。将开大括号放在与函数声明相同的行上，并且两者之间保持一个空格，这是一种良好的编程习惯。

注意：如果您希望在整个Rust项目中保持统一的代码风格，可以使用一个名为`rustfmt`的自动格式化工具来按照特定格式对代码进行格式化。关于`rustfmt`的更多信息，请参阅[附录D][devtools]<!-- ignore -->。Rust团队已经将这一工具包含在标准Rust发行版中，因为`rustc`也是标准组件之一，所以应该已经安装在您的计算机上！

`main`函数的主体包含以下代码：

```rust
println!("Hello, world!");
```

这一行代码完成了这个小程序的所有工作：它将文本打印到屏幕上。这里有三个需要注意的重要细节。

首先，`println!`调用了一个Rust宏。如果它调用的是函数的话，那么代码就会以`println`的形式呈现（不包括`!`）。Rust宏是一种用来编写能够生成扩展Rust语法的代码的方式，我们将在[第20章][ch20-macros]中详细讨论它们。目前，你只需要知道使用`!`意味着你调用的是一个宏而不是普通的函数，而且宏并不总是遵循与函数相同的规则。

其次，你会看到 `"Hello, world!"` 这个字符串。我们将这个字符串作为参数传递给 `println!`，然后该字符串会被打印到屏幕上。

第三，我们在行尾加上一个分号（`;`），这表示这一表达式已经结束，下一个表达式可以开始了。大多数Rust代码的行都是以分号结尾的。

<a id="编译和运行是分开的步骤"></a>

### 编译与执行

您刚刚运行了一个新创建的程序，现在让我们逐一检查这个过程中的每个步骤。

在运行一个Rust程序之前，你必须使用Rust编译器对其进行编译。具体操作是输入`rustc`命令，并传递你的源文件名，如下所示：

```console
$ rustc main.rs
```

如果你有C或C++的背景知识，你会注意到这与`gcc`或`clang`类似。成功编译后，Rust会生成二进制可执行文件。

在 Linux、macOS 以及 Windows 上的 PowerShell 中，您可以通过在shell中输入 `ls` 命令来查看可执行文件。

```console
$ ls
main  main.rs
```

在 Linux 和 macOS 上，你会看到两个文件。而在 Windows 上使用 PowerShell 时，你会看到与使用 CMD 时相同的三个文件。在使用 Windows 上的 CMD 时，你需要输入以下内容：

```cmd
> dir /B %= the /B option says to only show the file names =%
main.exe
main.pdb
main.rs
```

这里展示了带有_.rs_扩展名的源代码文件、可执行文件（在Windows系统是`_main.exe_，而在其他平台上则是`_main_`），以及在使用Windows系统时，还包含带有_.pdb_扩展名的调试信息文件。从这里开始，你可以像这样运行`_main_`或`_main.exe`文件：

```console
$ ./main # or .\main on Windows
```

如果你的 `_main.rs_`文件就是你的“Hello, world!”程序，那么这一行代码会在你的终端中打印出`Hello, world!`。

如果你更熟悉像Ruby、Python或JavaScript这样的动态语言，你可能不习惯将程序的编译和运行分开进行。Rust是一种_提前编译_的语言，这意味着你可以先编译程序，然后将生成的可执行文件交给其他人，他们甚至不需要安装Rust就可以运行该程序。如果你给某人一个.rb、.py或.js文件，那么对方就需要安装相应的Ruby、Python或JavaScript实现。但在这些语言中，你只需要一条命令就能编译并运行程序。在语言设计中，一切都是权衡的结果。

对于简单的程序来说，仅使用`rustc`进行编译是可行的，但随着项目的增长，你需要管理所有相关选项，并且要方便地分享你的代码。接下来，我们将向您介绍Cargo工具，它可以帮助您编写实际的Rust程序。

[故障排除]: ch01-01-installation.html#troubleshooting
[开发工具]: appendix-04-useful-development-tools.html
[第20章-宏]: ch20-05-macros.html