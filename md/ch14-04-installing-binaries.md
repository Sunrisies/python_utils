<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="通过Cargo Install安装二进制文件"></a>

## 使用`cargo install`安装二进制文件

``cargo install``命令允许你在本地安装和使用二进制包。这并不是为了替代系统包；而是为Rust开发者提供了一种方便的方式来安装那些在[crates.io](https://crates.io/)上分享的工具。请注意，你只能安装具有二进制目标的包。所谓“二进制目标”，指的是如果某个包有`src/main.rs`文件或其他指定文件，那么就可以运行的程序。作为一种二进制文件，与那些不能独立运行但适合包含在其他程序中的库目标不同。通常，这些软件包在README文件中会说明该软件包是作为库使用还是具有二进制目标，或者两者兼有。

所有通过`cargo install`安装的二进制文件都存储在安装目录的根目录下，即_bin_文件夹。如果你是使用_rustup_rs_来安装Rust的，并且没有进行任何自定义配置，那么这个目录将会是*$HOME/.cargo/bin*。请确保这个目录在你的`$PATH`中，这样你就可以运行通过`cargo install`安装的程序了。

例如，在第十二章中我们提到，有一个Rust实现的工具`grep`，名为`ripgrep`，用于搜索文件。要安装`ripgrep`，我们可以运行以下命令：

<!-- 手动重新生成
在项目中安装缺失的依赖，将相关的输出内容复制到下方
-->

```console
$ cargo install ripgrep
    Updating crates.io index
  Downloaded ripgrep v14.1.1
  Downloaded 1 crate (213.6 KB) in 0.40s
  Installing ripgrep v14.1.1
--snip--
   Compiling grep v0.3.2
    Finished `release` profile [optimized + debuginfo] target(s) in 6.73s
  Installing ~/.cargo/bin/rg
   Installed package `ripgrep v14.1.1` (executable `rg`)
```

输出的倒数第二行显示了已安装二进制文件的位置和名称，对于`ripgrep`来说，就是`rg`。只要安装目录位于之前提到的`$PATH`中，你就可以运行`rg --help`，从而使用一种更快速、更高效的Rust工具来搜索文件！