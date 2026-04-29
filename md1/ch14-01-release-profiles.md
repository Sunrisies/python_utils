## 通过发布配置文件自定义构建过程

在Rust中，_发布配置文件_是预定义的、可自定义的配置文件，它们具有不同的配置选项，使得程序员能够更灵活地控制代码编译过程中的各种参数。每个配置文件都是独立配置的，彼此之间不会相互影响。

Cargo提供了两个主要的配置文件：一个是`dev`配置文件，当你运行`cargo build`, and the `release` profile Cargo uses when you run `cargo build`或`--release`. The `dev`命令时，Cargo会默认使用这个配置文件。`release`配置文件则适用于发布版本的构建，同样具有良好的默认设置。

这些配置文件名可能从你的构建输出中熟悉：

<!-- 手动重新生成
在任何地方，运行以下命令：
cargo build
cargo build --release
并确保以下输出信息准确无误
-->

```console
$ cargo build
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.00s
$ cargo build --release
    Finished `release` profile [optimized] target(s) in 0.32s
```

`dev`和`release`是编译器使用的两种不同的配置文件。

在项目的_Cargo.toml_文件中，如果没有明确添加任何`[profile.*]`部分，Cargo会为各个配置文件提供默认设置。如果你要为任何想要自定义的配置文件添加`[profile.*]`部分，那么你就可以覆盖这些默认设置的一部分。例如，对于`dev`和`release`配置文件，`opt-level`设置的默认值如下：

<span class="filename">文件名：Cargo.toml</span>

```toml
[profile.dev]
opt-level = 0

[profile.release]
opt-level = 3
```

`opt-level`这个设置决定了Rust会对代码进行多少优化，其取值范围为0到3。进行更多的优化会延长编译时间，因此如果你处于开发阶段并且经常需要编译代码，那么为了更快地编译代码，你应该选择较少的优化级别，即使这样会导致代码运行速度变慢。因此，对于`dev`来说，默认值是`0`。当你准备发布代码时，最好多花一些时间进行编译。你只会在发布模式下编译一次，但你需要多次运行已经编译好的程序，所以发布模式是以更长的编译时间为代价来确保代码的运行速度更快。这就是为什么对于`release`来说，默认值是`3`的原因。

您可以通过在_Cargo.toml_中添加不同的值来覆盖默认设置。例如，如果我们希望在开发配置中使用优化级别1，可以在项目的_Cargo.toml_文件中添加以下两行代码：

<span class="filename">文件名：Cargo.toml</span>

```toml
[profile.dev]
opt-level = 1
```

这段代码覆盖了 ``0`` 的默认设置。现在，当我们运行 ``cargo build`` 时，Cargo会使用 ``dev`` 配置文件的默认设置，再加上我们对 ``opt-level`` 所做的自定义修改。由于我们将 ``opt-level`` 设置为 ``1``，因此Cargo会应用比默认设置更多的优化，但数量上不会像在发布版本中那样多。

有关每个配置选项的完整列表以及默认值，请参阅[Cargo的文档](https://doc.rust-lang.org/cargo/reference/profiles.html)。