<!-- Old headings. Do not remove or links may break. -->

<a id="installing-binaries-from-cratesio-with-cargo-install"></a>

## 使用 `cargo install` 安装二进制文件

`cargo install`命令允许你在本地安装和使用二进制包。这并不是为了替代系统包；而是为Rust开发者提供了一种方便的方式来安装那些在[crates.io](https://crates.io/)上分享的工具。请注意，你只能安装那些具有二进制目标的包。所谓“二进制目标”，指的是如果某个包有`src/main.rs`文件或指定了其他作为二进制目标的文件，那么就可以运行的程序。而“库目标”则不适合单独运行，但适合包含在其他程序中。通常，包在README文件中会说明该包是库还是具有二进制目标，或者两者都有。

所有通过 `cargo install` 安装的二进制文件都存储在安装目录的 _bin_ 文件夹中。如果您是使用 _rustup.rs_ 来安装 Rust，并且没有进行任何自定义配置，那么这个目录将会是 *$HOME/.cargo/bin*。请确保这个目录在您的 `$PATH` 中，这样您才能运行通过 `cargo install` 安装的程序。

例如，在第十二章中我们提到，有一个名为 `ripgrep` 的 Rust 实现，它是一款用于文件搜索的工具。要安装 `ripgrep`，我们可以运行以下命令：

<!-- manual-regeneration
cargo install something you don't have, copy relevant output below
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

输出的倒数第二行显示了已安装二进制文件的位置和名称，在 `ripgrep` 的情况下，就是 `rg`。只要安装目录位于你的 `$PATH` 中，正如之前提到的，你就可以运行 `rg --help`，从而使用一种更快速、更高效的 Rust 工具来搜索文件！