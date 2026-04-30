## 附录D：有用的开发工具

在这个附录中，我们将讨论Rust项目提供的一些有用的开发工具。我们将探讨自动格式化功能、快速应用警告修复的方法、代码检查工具，以及如何与集成开发环境进行集成。

### 使用 `rustfmt` 实现自动格式化

⊂PH0工具会根据社区的代码风格来重新格式化你的代码。许多协作项目都使用⊂PH1工具，以避免在编写Rust代码时产生关于使用哪种风格的争论：每个人都会使用这个工具来格式化他们的代码。

Rust 默认包含 `rustfmt`，因此你的系统上应该已经安装了 `rustfmt` 和 `cargo-fmt` 这两个程序。这两个命令与 `rustc` 和 `cargo` 类似，因为 `rustfmt` 提供了更精细的控制能力，而 `cargo-fmt` 则遵循使用 Cargo 的编程规范。要格式化任何 Cargo 项目，请输入以下命令：

```console
$ cargo fmt
```

运行此命令会重新格式化当前 crate 中的所有 Rust 代码。这只会改变代码风格，而不会改变代码的语义。有关 `rustfmt` 的更多信息，请参见 [其文档][rustfmt]。

### 使用 `rustfix` 修复你的代码

`rustfix`工具随Rust安装一起提供，能够自动修复那些有明确修复方法的编译器警告，这些修复方法很可能正是您所需要的。您可能之前见过编译器警告。例如，考虑以下代码：

<span class="filename"> 文件名: src/main.rs</span>

```rust
fn main() {
    let mut x = 42;
    println!("{x}");
}
```

在这里，我们将变量 `x` 定义为可变的，但实际上我们并没有对其进行任何修改。Rust 会对此发出警告：

```console
$ cargo build
   Compiling myprogram v0.1.0 (file:///projects/myprogram)
warning: variable does not need to be mutable
 --> src/main.rs:2:9
  |
2 |     let mut x = 0;
  |         ----^
  |         |
  |         help: remove this `mut`
  |
  = note: `#[warn(unused_mut)]` on by default
```

该警告建议我们移除 `mut` 这个关键字。我们可以通过运行 `cargo
fix` 命令，使用 `rustfix` 工具来自动执行该建议。

```console
$ cargo fix
    Checking myprogram v0.1.0 (file:///projects/myprogram)
      Fixing src/main.rs (1 fix)
    Finished dev [unoptimized + debuginfo] target(s) in 0.59s
```

当我们再次查看 _src/main.rs_ 文件时，会发现 `cargo fix` 已经改变了代码：

<span class="filename"> 文件名: src/main.rs</span>

```rust
fn main() {
    let x = 42;
    println!("{x}");
}
```

变量 `x` 现在是不可变的了，警告也消失了。

您还可以使用 `cargo fix` 命令在不同的 Rust 版本之间切换代码。有关各个版本的信息，请参见[附录 E][editions]<!--
ignore -->。

### 更多与Clippy相关的Lints工具

Clippy工具是一系列用于分析代码的工具，可以帮助您发现常见的错误并改进您的Rust代码。Clippy是标准Rust安装程序的一部分。

要在任何 Cargo 项目上运行 Clippy 的 lints 工具，请输入以下命令：

```console
$ cargo clippy
```

例如，假设你编写了一个程序，该程序使用了数学常数（如π）的近似值，就像这个程序所做的那样：

<Listing file-name="src/main.rs">

```rust
fn main() {
    let x = 3.1415;
    let r = 8.0;
    println!("the area of the circle is {}", x * r * r);
}
```

</Listing>

在项目中运行 `cargo clippy` 会导致以下错误：

```text
error: approximate value of `f{32, 64}::consts::PI` found
 --> src/main.rs:2:13
  |
2 |     let x = 3.1415;
  |             ^^^^^^
  |
  = note: `#[deny(clippy::approx_constant)]` on by default
  = help: consider using the constant directly
  = help: for further information visit https://rust-lang.github.io/rust-clippy/master/index.html#approx_constant
```

这个错误提示你，Rust已经定义了一个更精确的 `PI` 常量。如果你使用这个常量，你的程序会更准确。因此，你需要将代码修改为使用 `PI` 常量。

以下代码不会在Clippy中产生任何错误或警告。

<Listing file-name="src/main.rs">

```rust
fn main() {
    let x = std::f64::consts::PI;
    let r = 8.0;
    println!("the area of the circle is {}", x * r * r);
}
```

</Listing>

有关Clippy的更多信息，请参阅[其文档][clippy]。

### 使用 `rust-analyzer` 实现 IDE 集成

为了帮助集成到集成开发环境（IDE）中，Rust社区建议使用[rust-analyzer]。该工具是一组以编译器为中心的实用工具，它们遵循[lsp]协议，这是一种用于规范IDE与编程语言之间通信的协议。不同的客户端可以使用该工具，例如为Visual Studio Code提供的Rust分析器插件。

请访问 `rust-analyzer` 项目的 [主页][rust-analyzer]<!-- ignore -->，获取安装说明。然后，在您特定的集成开发环境中安装该语言服务器支持。您的集成开发环境将获得诸如自动完成、跳转到定义位置以及内联错误等功能。

[rustfmt]: https://github.com/rust-lang/rustfmt
[editions]: appendix-05-editions.md
[clippy]: https://github.com/rust-lang/rust-clippy
[rust-analyzer]: https://rust-analyzer.github.io
[lsp]: http://langserver.org/
[vscode]: https://marketplace.visualstudio.com/items?itemName=rust-lang.rust-analyzer
