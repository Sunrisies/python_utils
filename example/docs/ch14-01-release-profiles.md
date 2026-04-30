## 通过发布配置文件自定义构建过程

在Rust中，_发布配置文件_是预定义的、可自定义的配置文件，它们具有不同的配置选项，使得程序员能够更灵活地控制代码编译过程中的各种选项。每个配置文件都是独立配置的。

Cargo 主要有两种配置文件：当您运行 `cargo
build` 时使用的 `dev` 配置文件，以及当您运行 `cargo build
--release` 时使用的 `release` 配置文件。 `dev` 配置文件为开发场景提供了良好的默认设置，而 `release` 配置文件则提供了良好的发布构建默认设置。

这些配置文件名可能从你的构建输出中熟悉起来：

<!-- manual-regeneration
anywhere, run:
cargo build
cargo build --release
and ensure output below is accurate
-->

```console
$ cargo build
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.00s
$ cargo build --release
    Finished `release` profile [optimized] target(s) in 0.32s
```

`dev`和`release`是编译器使用的两种不同的配置文件。

在项目的_Cargo.toml_文件中，如果没有明确添加任何 `[profile.*]` 部分，Cargo 会为各个配置文件提供默认设置。如果你为想要自定义的配置文件添加 `[profile.*]` 部分，那么就会覆盖这些默认设置的一部分。例如，对于 `dev` 和 `release` 配置文件， `opt-level` 设置的默认值是这样的：

<span class="filename">文件名: Cargo.toml</span>

```toml
[profile.dev]
opt-level = 0

[profile.release]
opt-level = 3
```

`opt-level` 这个设置可以控制 Rust 对代码进行的优化次数，其取值范围为 0 到 3。增加优化次数会延长编译时间，因此如果你处于开发阶段并且经常需要编译代码，那么为了减少编译时间，你应该选择较少的优化级别，即使这样代码运行速度会较慢。因此，`dev` 的默认优化级别是`0`。当你准备发布代码时，最好多花一些时间进行编译。你只会在发布模式下编译一次，但之后会多次运行已编译的程序，因此发布模式是以较长的编译时间换取运行速度更快的代码。这就是为什么`release` 的默认优化级别是`3`的原因。

您可以通过在_Cargo.toml_中添加不同的值来覆盖默认设置。例如，如果我们希望在开发配置中使用优化级别1，可以在项目的_Cargo.toml_文件中添加以下两行代码：

<span class="filename">文件名: Cargo.toml</span>

```toml
[profile.dev]
opt-level = 1
```

这段代码覆盖了 `0` 的默认设置。现在当我们运行 `cargo build` 时，Cargo 将会使用 `dev` 配置文件的默认设置，再加上我们对 `opt-level` 所做的自定义设置。由于我们将 `opt-level` 设置为 `1`，因此 Cargo 会应用比默认设置更多的优化，但数量上不如发布版本中的优化那么多。

有关每个配置选项的完整列表以及默认值，请参阅[Cargo的文档](https://doc.rust-lang.org/cargo/reference/profiles.html)。