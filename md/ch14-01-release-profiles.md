## 使用发布配置文件自定义构建过程

在Rust中，_发布配置文件_是预定义的、可自定义的配置文件，具有不同的配置选项，使得程序员能够更灵活地控制编译代码的各项参数。每个配置文件都是独立配置的。

Cargo有两个主要的配置文件：`dev`配置文件，当您运行`cargo build`, and the `release` profile Cargo uses when you run `cargo build`或`--release`. The `dev`命令时，Cargo会使用该配置文件。`release`配置文件的默认设置更适合发布版本的建设。

这些配置文件名可能从你的构建输出中熟悉起来：

<!-- 手动生成
在任何地方，运行以下命令：
cargo build
cargo build --release
并确保下面的输出准确无误
-->

```console
$ cargo build
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.00s
$ cargo build --release
    Finished `release` profile [optimized] target(s) in 0.32s
```

`dev`和`release`是编译器使用的两种不同的配置文件。

在项目的_Cargo.toml_文件中，如果没有明确添加任何`[profile.*]`部分，那么每个配置文件都会具有默认设置。如果你为想要自定义的任何一个配置文件添加`[profile.*]`部分，那么你就可以覆盖这些默认设置的一部分。例如，对于`dev`和`release`配置文件的`opt-level`设置的默认值如下：

<span class="filename">文件名：Cargo.toml</span>

```toml
[profile.dev]
opt-level = 0

[profile.release]
opt-level = 3
```

`opt-level`这个设置可以控制Rust对你的代码进行优化的次数，其取值范围为0到3。增加优化次数会延长编译时间，因此如果你处于开发阶段并且经常需要编译代码，那么选择较少的优化次数可以更快地完成编译，即使这样代码的运行速度可能会变慢。因此，对于`dev`来说，默认值是`0`。当你准备发布代码时，最好多花一些时间进行编译。在发布模式下只需编译一次，但实际上你需要多次运行已编译的程序。因此，发布模式以较长的编译时间作为代价，换取了更快的运行速度。这就是为什么对于`release`配置，其默认值`opt-level`实际上被设置为`3`的原因。

您可以通过在_Cargo.toml_中添加不同的值来覆盖默认设置。例如，如果我们希望在开发配置中使用优化级别1，可以在项目的_Cargo.toml_文件中添加以下两行代码：

<span class="filename">文件名：Cargo.toml</span>

```toml
[profile.dev]
opt-level = 1
```

这段代码覆盖了 ``0`` 的默认设置。现在，当我们运行 ``cargo build`` 时，Cargo会使用 ``dev`` 配置文件的默认设置，再加上我们对 ``opt-level`` 所做的自定义调整。由于我们将 ``opt-level`` 设置为 ``1``，因此Cargo会应用比默认设置更多的优化，但数量上不会像在发布版本中那样多。

有关每个配置选项的完整列表以及默认值，请参阅[Cargo的文档](https://doc.rust-lang.org/cargo/reference/profiles.html)。