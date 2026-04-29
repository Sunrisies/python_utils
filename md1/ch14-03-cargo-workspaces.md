## Cargo工作空间

在第十二章中，我们构建了一个包含二进制 crate 和库 crate 的包。随着项目的不断发展，你可能会发现库 crate 的体积越来越大，因此你可能需要将包进一步拆分为多个独立的库 crate。Cargo 提供了一个名为 _workspaces_ 的功能，可以帮助管理多个相互关联的包，这些包可以协同开发。

### 创建工作区

一个**工作区**是一组共享同一`Cargo.lock`文件和输出目录的包。让我们使用一个工作区来创建一个项目——我们将使用简单的代码，这样就能专注于工作区的结构了。有多种方式来构建工作区，这里我们只展示一种常见的方式。我们将有一个包含二进制文件和两个库的工作区。提供主要功能的二进制文件依赖于这两个库。其中一个库会提供一个名为``add_one``的函数，另一个库则提供名为``add_two``的函数。这三个库都属于同一个工作区。首先，我们需要为工作区创建一个新的目录：

```console
$ mkdir add
$ cd add
```

接下来，在`_add_`目录下，我们创建`_Cargo.toml_`文件，该文件将配置整个工作区。这个文件中不会包含``[package]``部分。相反，它会以``[workspace]``部分开始，这部分内容允许我们向工作区添加成员。我们还特意设置``resolver``的值为``"3"``，以确保我们的工作区使用Cargo的最新版本的解析算法。

<span class="filename">文件名：Cargo.toml</span>

```toml
{{#include ../listings/ch14-more-about-cargo/no-listing-01-workspace/add/Cargo.toml}}
```

接下来，我们将在`add_目录中运行`cargo new`来创建`adder`二进制依赖库。

<!-- 手动重新生成
cd listings/ch14-more-about-cargo/output-only-01-adder-crate/add
从 Cargo.toml 中删除 `members = ["adder"]`
删除 adder 目录
cargo new adder
复制以下输出内容
-->

```console
$ cargo new adder
     Created binary (application) `adder` package
      Adding `adder` as member of workspace at `file:///projects/add`
```

在工作区中运行 `cargo new` 也会自动将新创建的包添加到工作区中的 `[workspace]` 定义中的 `members` 键中，就像这样：_Cargo.toml_。

```toml
{{#include ../listings/ch14-more-about-cargo/output-only-01-adder-crate/add/Cargo.toml}}
```

此时，我们可以通过运行`cargo build`来构建工作区。你的`_add_`目录中的文件应该如下所示：

```text
├── Cargo.lock
├── Cargo.toml
├── adder
│   ├── Cargo.toml
│   └── src
│       └── main.rs
└── target
```

该工作区在顶层有一个名为`_target_`的目录，编译后的文件将放置在这个目录下；而`adder`这个包并没有自己的`_target_`目录。即使我们从_adder_目录内部运行`cargo build`，编译后的文件仍然会存放在`_add/target`而不是`_add/adder/target`中。Cargo将`_target_`目录组织在工作区内，是因为工作区中的各个包是相互依赖的。如果每个包都有自己独立的`_target_`目录，那么每个包都需要重新编译工作区中的其他包，才能将文件放置在自己的`_target_`目录中。通过共享一个`_target_`目录，各个包可以避免不必要的重新编译。

### 在工作区中创建第二个包

接下来，让我们在工作区中创建另一个成员包，并将其命名为`add_one`。然后生成一个名为`add_one`的新库包：

<!-- 手动重新生成
cd listings/ch14-more-about-cargo/output-only-02-add-one/add
在 Cargo.toml 文件中从 `members` 列表中移除 `"add_one"`
rm -rf add_one
cargo new add_one --lib
复制输出内容到下方
-->

```console
$ cargo new add_one --lib
     Created library `add_one` package
      Adding `add_one` as member of workspace at `file:///projects/add`
```

顶层的`_Cargo.toml_`文件现在会在`__INLINE_CODE__38__`列表中包含`_add_one_`路径。

<span class="filename">文件名：Cargo.toml</span>

```toml
{{#include ../listings/ch14-more-about-cargo/no-listing-02-workspace-with-two-crates/add/Cargo.toml}}
```

您的`add`目录现在应该包含以下目录和文件：

```text
├── Cargo.lock
├── Cargo.toml
├── add_one
│   ├── Cargo.toml
│   └── src
│       └── lib.rs
├── adder
│   ├── Cargo.toml
│   └── src
│       └── main.rs
└── target
```

在`_add_one/src/lib.rs_`文件中，让我们添加一个`__INLINE_CODE__39__`函数：

<span class="filename">文件名：add_one/src/lib.rs</span>

```rust,noplayground
{{#rustdoc_include ../listings/ch14-more-about-cargo/no-listing-02-workspace-with-two-crates/add/add_one/src/lib.rs}}
```

现在，我们可以创建一个名为`adder`的包，该包的二进制依赖项为包含我们库的`add_one`包。首先，我们需要在_adder/Cargo.toml_文件中添加对`add_one`的路径依赖项。

<span class="filename">文件名：adder/Cargo.toml</span>

```toml
{{#include ../listings/ch14-more-about-cargo/no-listing-02-workspace-with-two-crates/add/adder/Cargo.toml:6:7}}
```

Cargo并不假设工作区中的 crate之间会相互依赖，因此我们需要明确这些依赖关系。

接下来，让我们在`adder` crate中使用`add_one`函数（来自`add_one` crate）。打开_adder/src/main.rs_文件，并将`main`函数修改为调用`add_one`函数，如清单14-7所示。

<listing number="14-7" file-name="adder/src/main.rs" caption="使用来自`adder` crate的`add_one`库 crate">

```rust,ignore
{{#rustdoc_include ../listings/ch14-more-about-cargo/listing-14-07/add/adder/src/main.rs}}
```

</ Listing>

让我们通过运行 `cargo build` 在顶级 _add_ 目录中构建工作空间！

<!-- 手动重新生成
cd listings/ch14-more-about-cargo/listing-14-07/add
cargo build
将输出文件复制到下方；该输出文件中的脚本无法正确处理路径中的子目录
-->

```console
$ cargo build
   Compiling add_one v0.1.0 (file:///projects/add/add_one)
   Compiling adder v0.1.0 (file:///projects/add/adder)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.22s
```

要运行来自`_add_`目录的二进制包，我们可以通过使用__`INLINE_CODE_51__`参数来指定想要运行的工作区中的特定包，并通过__`INLINE_CODE_52__`参数来指定该包的名称。

<!-- 手动重新生成
cd listings/ch14-more-about-cargo/listing-14-07/add
cargo run -p adder
在下方复制输出内容；该输出工具无法正确处理路径中的子目录
-->

```console
$ cargo run -p adder
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.00s
     Running `target/debug/adder`
Hello, world! 10 plus one is 11!
```

这将执行位于 _adder/src/main.rs_ 中的代码，该代码依赖于 `add_one` 这个软件包。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="依赖于工作区中的外部包"></a>

### 取决于外部包

请注意，工作区在顶层只有一个_Cargo.lock_文件，而不是在每个依赖包的目录中都有_Cargo.lock_文件。这样可以确保所有依赖包都使用相同的版本。如果我们把`rand`包添加到_adder/Cargo.toml_和_add_one/Cargo.toml_文件中，Cargo会将这些包解析为同一个版本的`rand`，并将这一信息记录在一个_Cargo.lock_文件中。让工作区中的所有依赖包都使用相同的依赖项，意味着这些依赖包之间始终具有兼容性。接下来，我们将`rand`包添加到_add_one/Cargo.toml_文件的`[dependencies]`部分中，这样我们就可以在`add_one`包中使用`rand`包了。

<!-- 在更新 `rand` 的版本时，也需要更新这些文件中使用的 `rand` 的版本，以确保两者一致：
* ch02-00-guessing-game-tutorial.md
* ch07-04-bringing-paths-into-scope-with-the-use-keyword.md
-->

<span class="filename">文件名：add_one/Cargo.toml</span>

```toml
{{#include ../listings/ch14-more-about-cargo/no-listing-03-workspace-with-external-dependency/add/add_one/Cargo.toml:6:7}}
```

现在我们可以将 `use rand;` 添加到 _add_one/src/lib.rs_ 文件中。通过在 _add_ 目录中运行 `cargo build`，可以引入并编译 `rand` 这个 crate。我们会收到一个警告，因为我们没有引用到在作用域内引入的 `rand`。

<!-- 手动重新生成
cd listings/ch14-more-about-cargo/no-listing-03-workspace-with-external-dependency/add
cargo build
将输出文件复制到下方；该输出文件中的更新脚本无法正确处理路径中的子目录
-->

```console
$ cargo build
    Updating crates.io index
  Downloaded rand v0.8.5
   --snip--
   Compiling rand v0.8.5
   Compiling add_one v0.1.0 (file:///projects/add/add_one)
warning: unused import: `rand`
 --> add_one/src/lib.rs:1:5
  |
1 | use rand;
  |     ^^^^
  |
  = note: `#[warn(unused_imports)]` on by default

warning: `add_one` (lib) generated 1 warning (run `cargo fix --lib -p add_one` to apply 1 suggestion)
   Compiling adder v0.1.0 (file:///projects/add/adder)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.95s
```

当前的最高级别 `_Cargo.lock` 文件中包含了 ``add_one`` 依赖于 ``rand`` 的信息。不过，即使 ``rand`` 在工作区中的某个地方被使用，我们也无法在工作区的其他 crate 中使用它，除非我们同时将 ``rand`` 添加到它们的`_Cargo.toml`文件中。例如，如果我们把 ``use rand;`` 添加到 ``adder`` 包的`adder/src/main.rs`文件中，就会遇到错误：

<!-- 手动重新生成
cd listings/ch14-more-about-cargo/output-only-03-use-rand/add
cargo build
将输出文件复制到下方；该输出文件中的脚本无法正确处理路径中的子目录
-->

```console
$ cargo build
  --snip--
   Compiling adder v0.1.0 (file:///projects/add/adder)
error[E0432]: unresolved import `rand`
 --> adder/src/main.rs:2:5
  |
2 | use rand;
  |     ^^^^ no external crate `rand`
```

要解决这个问题，请编辑 `adder` 包的 _Cargo.toml_ 文件，并注明 `rand` 也是该包的依赖项。构建 `adder` 包会将 `rand` 添加到 _Cargo.lock_ 文件中 `adder` 的依赖列表中，但不会下载 `rand` 的其他副本。Cargo 会确保使用 `rand` 包的每个包中的每个 crate 都使用相同的版本，只要它们指定了兼容的 `rand` 版本，从而节省空间并确保工作区中的各个包能够相互兼容。

如果工作区中的 crate 指定了同一依赖项的不兼容版本，Cargo 会分别解析这些版本，但会尽量解析尽可能少的版本。

### 在工作区中添加测试

为了进行进一步的改进，让我们在 `add_one` 这个 crate 中添加一个对 `add_one::add_one` 函数的测试。

<span class="filename">文件名：add_one/src/lib.rs</span>

```rust,noplayground
{{#rustdoc_include ../listings/ch14-more-about-cargo/no-listing-04-workspace-with-tests/add/add_one/src/lib.rs}}
```

现在在顶级目录`_add_`中运行`cargo test`。如果在类似这样的工作区中运行`cargo test`，那么将会运行该工作区中所有 crate 的测试：

<!-- 手动重新生成
cd listings/ch14-more-about-cargo/no-listing-04-workspace-with-tests/add
cargo test
将输出内容复制到下方；该输出更新脚本无法正确处理路径中的子目录
-->

```console
$ cargo test
   Compiling add_one v0.1.0 (file:///projects/add/add_one)
   Compiling adder v0.1.0 (file:///projects/add/adder)
    Finished `test` profile [unoptimized + debuginfo] target(s) in 0.20s
     Running unittests src/lib.rs (target/debug/deps/add_one-93c49ee75dc46543)

running 1 test
test tests::it_works ... ok

test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

     Running unittests src/main.rs (target/debug/deps/adder-3a47283c568d2b6a)

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

   Doc-tests add_one

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s
```

输出的第一部分显示，`add_one` crate中的`it_works`测试通过了。下一部分显示，`adder` crate中没有找到任何测试；最后一部分则显示，`add_one` crate中也没有找到任何文档测试。

我们还可以使用`-p`标志，从顶级目录开始，在工作区中运行某个特定 crate 的测试，同时指定我们想要测试的 crate 的名称。

<!-- 手动重新生成
cd listings/ch14-more-about-cargo/no-listing-04-workspace-with-tests/add
cargo test -p add_one
将输出内容复制下来；该输出脚本无法正确处理路径中的子目录
-->

```console
$ cargo test -p add_one
    Finished `test` profile [unoptimized + debuginfo] target(s) in 0.00s
     Running unittests src/lib.rs (target/debug/deps/add_one-93c49ee75dc46543)

running 1 test
test tests::it_works ... ok

test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

   Doc-tests add_one

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s
```

该输出显示`cargo test`仅运行了`add_one` crate的测试，而没有运行`adder` crate的测试。

如果您将工作区中的 crate 发布到
[crates.io](https://crates.io/)，那么工作区中的每个 crate 都需要单独进行发布。就像 `cargo test` 一样，我们可以通过使用 `-p` 标志，并指定要发布的 crate 的名称，来在自己的工作区中发布特定的 crate。

为了进行更多的练习，请像添加 `add_one` 这个 crate 一样，将 `add_two` 这个 crate 添加到当前工作区中！

随着你的项目不断发展，考虑使用工作区：它可以帮助你处理更小、更易于理解的代码组件，而不是一大块难以理解的代码。此外，将相关库放在一个工作区内，可以更容易地协调那些经常同时被修改的库。