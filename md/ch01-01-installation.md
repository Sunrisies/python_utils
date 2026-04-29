## 安装

第一步是安装Rust。我们将通过`rustup`下载Rust，这是一个用于管理Rust版本及相关工具的命令行工具。下载时需要网络连接。

注意：如果您出于某种原因不想使用`rustup`，请参考[其他Rust安装方法页面][otherinstall]以获取更多选项。

以下步骤用于安装最新稳定的Rust编译器版本。  
Rust的稳定性保证了本书中所有示例在较新的Rust版本下仍能正常编译。不同版本之间的输出可能会有一些差异，因为Rust通常会改进错误信息和警告功能。换句话说，通过这些步骤安装的任何较新且稳定的Rust版本都应该能够正常使用本书中的内容。

> ### 命令行格式说明  
在本章以及整本书中，我们会展示在终端中使用的某些命令。需要在终端中输入的行均以`$`开头。您无需输入`$`字符；它只是用来指示每个命令开始的命令行提示符。不以`$`开头的行通常显示的是上一个命令的输出结果。此外，还有针对PowerShell的特定格式说明。> 在示例中，将会使用`>`而不是`$`。

### 在Linux或macOS上安装`rustup`

如果您使用的是Linux或macOS，请打开终端并输入以下命令：

```console
$ curl --proto '=https' --tlsv1.2 https://sh.rustup.rs -sSf | sh
```

该命令会下载一个脚本，并开始安装`rustup`工具，该工具可以安装最新稳定的Rust版本。系统可能会提示您输入密码。如果安装成功，将会出现以下信息：

```text
Rust is installed now. Great!
```

您还需要一个链接器，这是一个程序，Rust用它来将编译后的输出文件合并成一个文件。很可能您已经拥有这样的工具了。如果您遇到链接器错误，那么您需要安装一个C语言编译器，通常C语言编译器也会包含链接器功能。使用C语言编译器也是很有用的，因为一些常见的Rust软件包依赖于C代码，因此需要使用C语言编译器来构建这些软件包。

在macOS上，可以通过运行以下命令来获取C编译器：

```console
$ xcode-select --install
```

根据用户的发行版文档，Linux用户通常应该安装GCC或Clang。例如，如果您使用的是Ubuntu，可以安装`build-essential`包。

### 在Windows操作系统上安装`rustup`

在Windows系统中，请访问[https://www.rust-lang.org/tools/install][install]进行安装，并按照说明操作。在安装过程中，系统会提示您安装Visual Studio。Visual Studio提供了链接器和编译程序所需的原生库。如果您需要更多关于此步骤的帮助，请参考[https://rust-lang.github.io/rustup/installation/windows-msvc.html][msvc]。

本书的其余部分使用的命令既可以在 _cmd.exe_ 中运行，也可以在 PowerShell 中运行。如果有特定的区别，我们会说明应该使用哪种工具。

### 故障排除

要检查您的Rust是否已正确安装，请打开终端并输入以下命令：

```console
$ rustc --version
```

您应该会看到最新稳定版本的版本号、提交哈希值和提交日期，其格式如下：

```text
rustc x.y.z (abcabcabc yyyy-mm-dd)
```

如果您看到了这条信息，说明您已经成功安装了Rust！如果没有看到这条信息，请检查您的系统变量中是否包含``%PATH%``，以确保Rust已正确安装。

在Windows的CMD中，使用：

```console
> echo %PATH%
```

在PowerShell中，使用：

```powershell
> echo $env:Path
```

在Linux和macOS系统中，使用：

```console
$ echo $PATH
```

如果以上信息都是正确的，但Rust仍然无法正常工作，那么你可以向多个地方寻求帮助。可以在[社区页面]上了解如何与其他Rust开发者联系（这是我们给自己起的幽默昵称）。

### 更新与卸载

一旦通过`rustup`安装了Rust，更新到最新版本就变得非常简单了。在您的终端中，运行以下更新脚本：

```console
$ rustup update
```

要卸载Rust和`rustup`，请在shell中运行以下卸载脚本：

```console
$ rustup self uninstall
```

<!-- 旧的标题。不要删除，否则链接可能会失效。 -->
<a id="local-documentation"></a>

### 阅读本地文档

安装Rust时，还会包含一份文档的本地副本，这样你就可以在离线状态下阅读文档。运行`rustup doc`可以在浏览器中打开本地文档。

每当标准库提供了某种类型或函数，而您不确定其用途或如何使用时，请使用应用程序编程接口（API）文档来了解相关信息！

<a id="文本编辑器与集成开发环境">文本编辑器与集成开发环境</a>

### 使用文本编辑器和集成开发环境

这本书并不对您使用哪些工具来编写Rust代码做出任何假设。几乎任何文本编辑器都能胜任这项任务！不过，许多文本编辑器和集成开发环境（IDE）都内置了Rust的支持功能。您可以在Rust网站的[工具页面][tools]上找到许多编辑器和IDE的当前列表。

### 使用这本书进行离线学习

在几个示例中，我们将使用标准库之外的Rust包。要完成这些示例，您需要连接互联网，或者提前下载这些依赖项。要提前下载依赖项，您可以运行以下命令。（我们稍后会详细解释`cargo`是什么，以及这些命令的具体功能。）

```console
$ cargo new get-dependencies
$ cd get-dependencies
$ cargo add rand@0.8.5 trpl@0.2.0
```

这将缓存这些包的下载内容，因此您无需在之后再次下载它们。一旦执行了此命令，就不需要保留`get-dependencies`文件夹了。如果您已经执行了此命令，可以在本书的其余部分中使用`--offline`标志，并结合所有`cargo`命令来使用这些缓存版本，而无需尝试通过网络进行下载。

[其他安装方法]: https://forge.rust-lang.org/infra/other-installation-methods.html  
[安装指南]: https://www.rust-lang.org/tools/install  
[Windows版安装]: https://rust-lang.github.io/rustup/installation/windows-msvc.html  
[社区资源]: https://www.rust-lang.org/community  
[工具与资源]: https://www.rust-lang.org/tools