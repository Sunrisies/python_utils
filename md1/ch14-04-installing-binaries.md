<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="通过Cargo Install安装Cratesio二进制文件"></a>

## 使用 `cargo install` 安装二进制文件

`cargo install`命令允许你在本地安装和使用二进制库。这并不是为了替代系统包；而是为Rust开发者提供了一种方便的方式，来安装那些在[crates.io](https://crates.io/)上分享的工具。请注意，你只能安装那些具有二进制目标的包。所谓“二进制目标”，指的是可运行的程序，这种程序会在库包含`_src/main.rs_`文件或其他被指定为二进制文件的文件时创建。而“库目标”则是不具备独立运行能力，但适合包含在其他程序中使用的库。通常，库会在README文件中说明该库是库还是二进制目标，或者两者都有。

所有通过`cargo install`安装的二进制文件都存储在安装目录的根目录下的_bin_文件夹中。如果您是使用_rustup_rs_来安装Rust，并且没有进行任何自定义配置，那么这个目录将会是*$HOME/.cargo/bin*。请确保这个目录位于您的`$PATH`目录下，这样您就可以运行通过`cargo install`安装的程序了。

例如，在第十二章中我们提到，有一个名为`ripgrep`的Rust实现工具`grep`，用于搜索文件。要安装`ripgrep`，我们可以运行以下命令：

<!-- 手动重新生成
使用 cargo 安装你缺少的依赖项，将相关的输出内容复制到下方
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

输出的倒数第二行显示了已安装二进制文件的位置和名称，在 `ripgrep` 的情况下，该二进制文件的名称为 `rg`。只要安装目录位于之前提到的 `$PATH` 中，你就可以运行 `rg --help`，从而使用一种更快速、更高效的 Rust 工具来搜索文件！