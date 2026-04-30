## Cargo工作空间

在第十二章中，我们构建了一个包含二进制 crate 和库 crate 的包。随着项目的不断发展，你可能会发现库 crate 的体积越来越大，因此你可能需要将包进一步拆分为多个库 crate。Cargo 提供了一个名为 _workspaces_ 的功能，可以帮助管理多个相互关联的包。

### 创建工作区

一个_工作区_是一组共享同一_Cargo.lock_和输出目录的包。让我们使用一个工作区来创建一个项目——我们将使用简单的代码，这样我们就可以专注于工作区的结构。有多种方式来构建工作区，这里我们只展示一种常见的方式。我们将创建一个包含一个二进制文件和两个库的工作区。提供主要功能的二进制文件将依赖于这两个库。其中一个库会提供一个 `add_one` 函数，另一个库会提供一个 `add_two` 函数。这三个库将属于同一个工作区。首先，我们需要为工作区创建一个新的目录：

```console
$ mkdir add
$ cd add
```

接下来，在 _add_ 目录下，我们创建 _Cargo.toml_ 文件，该文件将配置整个工作区。这个文件不会包含 `[package]` 部分。相反，它会以一个 `[workspace]` 部分开始，这部分允许我们向工作区添加成员。我们还注意到了一个要点：通过设置 `resolver` 的值为 `"3"`，可以在我们的工作区中使用 Cargo 的最新版本的解码器算法。

<span class="filename">文件名: Cargo.toml</span>

```toml
[workspace]
resolver = "3"

```

接下来，我们将在`add_目录中运行`cargo new`来创建`adder`这个二进制包。

<!-- manual-regeneration
cd listings/ch14-more-about-cargo/output-only-01-adder-crate/add
remove `members = ["adder"]` from Cargo.toml
rm -rf adder
cargo new adder
copy output below
-->

```console
$ cargo new adder
     Created binary (application) `adder` package
      Adding `adder` as member of workspace at `file:///projects/add`
```

在工作区中运行 `cargo new` 也会自动将新创建的包添加到 `[workspace]` 定义中的 `members` 键中，比如 _Cargo.toml_ 中就是这样操作的。

```toml
[workspace]
resolver = "3"
members = ["adder"]

```

此时，我们可以通过运行 `cargo build` 来构建工作区。你的 _add_ 目录中的文件应该如下所示：

```text
├── Cargo.lock
├── Cargo.toml
├── adder
│   ├── Cargo.toml
│   └── src
│       └── main.rs
└── target
```

该工作区在顶层有一个名为`_target_`的目录，编译后的工件将被放置到这个目录中；而`adder`这个包并没有自己的`_target_`目录。即使我们从`_adder_`目录内部运行`cargo build`，编译后的工件仍然会存放在`_add/target_`而不是`_add/adder/target_`中。Cargo将`_target_`目录组织在工作区中，是因为工作区内的各个包是相互依赖的。如果每个包都有自己的`_target_`目录，那么每个包都需要重新编译工作区中的其他包，才能将工件放置在自己的`_target_`目录中。通过共享一个`_target_`目录，各个包可以避免不必要的重新编译。

### 在工作区中创建第二个包

接下来，让我们在工作区中创建另一个成员包，并将其命名为`add_one`。然后生成一个名为`add_one`的新库 crate。

<!-- manual-regeneration
cd listings/ch14-more-about-cargo/output-only-02-add-one/add
remove `"add_one"` from `members` list in Cargo.toml
rm -rf add_one
cargo new add_one --lib
copy output below
-->

```console
$ cargo new add_one --lib
     Created library `add_one` package
      Adding `add_one` as member of workspace at `file:///projects/add`
```

顶级 `_Cargo.toml` 文件现在会在 ``members`` 列表中包含 `_add_one` 路径。

<span class="filename">文件名: Cargo.toml</span>

```toml
[workspace]
resolver = "3"
members = ["adder", "add_one"]

```

您的 _add_ 目录现在应该包含以下目录和文件：

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

在 _add_one/src/lib.rs_ 文件中，让我们添加一个 `add_one` 函数：

<span class="filename"> 文件名: add_one/src/lib.rs</span>

```rust,noplayground
pub fn add_one(x: i32) -> i32 {
    x + 1
}

```

现在，我们可以拥有一个名为 `adder` 的包，该包的二进制依赖项依赖于 `add_one` 这个包，而 `add_one` 包则包含了我们的库。首先，我们需要在 _adder/Cargo.toml_ 文件中添加对 `add_one` 的路径依赖项。

<span class="filename">文件名: adder/Cargo.toml</span>

```toml

```

Cargo并不假设工作区中的 crate之间会相互依赖，因此我们需要明确这些依赖关系。

接下来，让我们在`adder` crate中使用`add_one`函数（来自`add_one` crate）。打开_adder/src/main.rs_文件，并将`main`函数修改为调用`add_one`函数，如清单14-7所示。

<Listing number="14-7" file-name="adder/src/main.rs" caption="Using the `add_one` library crate from the `adder` crate">

```rust,ignore
fn main() {
    let num = 10;
    println!("Hello, world! {num} plus one is {}!", add_one::add_one(num));
}

```

</Listing>

让我们通过在顶级目录中运行 `cargo build` 来创建工作区！

<!-- manual-regeneration
cd listings/ch14-more-about-cargo/listing-14-07/add
cargo build
copy output below; the output updating script doesn't handle subdirectories in paths properly
-->

```console
$ cargo build
   Compiling add_one v0.1.0 (file:///projects/add/add_one)
   Compiling adder v0.1.0 (file:///projects/add/adder)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.22s
```

要运行来自 _add_ 目录的二进制包，我们可以通过使用 `-p` 参数来指定要在工作区中运行的包，然后使用 `cargo run` 来指定具体的包名。

<!-- manual-regeneration
cd listings/ch14-more-about-cargo/listing-14-07/add
cargo run -p adder
copy output below; the output updating script doesn't handle subdirectories in paths properly
-->

```console
$ cargo run -p adder
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.00s
     Running `target/debug/adder`
Hello, world! 10 plus one is 11!
```

这将执行位于 _adder/src/main.rs_ 中的代码，该代码依赖于 `add_one` 这个包。

<!-- Old headings. Do not remove or links may break. -->

<a id="depending-on-an-external-package-in-a-workspace"></a>

### 取决于外部包

请注意，工作区中只有一个位于顶层级别的_Cargo.lock_文件，而不是在每个依赖包的目录中都有_Cargo.lock_文件。这样做可以确保所有依赖包都使用相同的依赖版本。如果我们把`rand`包添加到_adder/Cargo.toml_和_add_one/Cargo.toml_文件中，Cargo会将这些依赖项解析为同一个版本`rand`，并将这一信息记录在一个_Cargo.lock_文件中。让工作区中的所有依赖包都使用相同的依赖版本意味着这些依赖包之间始终具有兼容性。接下来，我们将`rand`包添加到_add_one/Cargo.toml_文件的`[dependencies]`部分中，这样我们就可以在`add_one`包中使用`rand`包了。

<!-- When updating the version of `rand` used, also update the version of
`rand` used in these files so they all match:
* ch02-00-guessing-game-tutorial.md
* ch07-04-bringing-paths-into-scope-with-the-use-keyword.md
-->

<span class="filename">文件名: add_one/Cargo.toml</span>

```toml

```

我们现在可以在 _add_one/src/lib.rs_ 文件中添加 `use rand;`，然后在 _add_ 目录下运行 `cargo build` 来构建整个工作区，从而引入并编译 `rand` 这个 crate。我们会收到一个警告，因为我们没有引用到已经引入范围内的 `rand`。

<!-- manual-regeneration
cd listings/ch14-more-about-cargo/no-listing-03-workspace-with-external-dependency/add
cargo build
copy output below; the output updating script doesn't handle subdirectories in paths properly
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

当前的最高级别 _Cargo.lock_ 文件中包含了关于`add_one`依赖项`rand`的信息。不过，即使`rand`在工作区中的某个地方被使用，我们也无法在工作区中的其他crates中使用它，除非我们同时将`rand`添加到它们的_Cargo.toml_文件中。例如，如果我们把`use rand;`添加到`adder`包对应的_adder/src/main.rs_文件中，就会出错。

<!-- manual-regeneration
cd listings/ch14-more-about-cargo/output-only-03-use-rand/add
cargo build
copy output below; the output updating script doesn't handle subdirectories in paths properly
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

要解决这个问题，请编辑 `adder` 包对应的 _Cargo.toml_ 文件，并注明 `rand` 也是该包的依赖项。构建 `adder` 包会将 `rand` 添加到 _Cargo.lock_ 中 `adder` 的依赖列表中，但不会下载额外的 `rand` 版本。只要指定了 `rand` 的兼容版本，Cargo就会确保使用 `rand` 包的每个包都使用相同的版本，从而节省空间并确保工作区中的各个包能够相互兼容。

如果工作区中的 crate 指定了同一依赖项的不兼容版本，Cargo 会分别处理这些版本，但会尽量只解析尽可能少的版本。

### 在工作区中添加测试

为了进一步改进，让我们在 `add_one` 这个 crate 中添加对 `add_one::add_one` 函数的测试。

<span class="filename"> 文件名: add_one/src/lib.rs</span>

```rust,noplayground
pub fn add_one(x: i32) -> i32 {
    x + 1
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn it_works() {
        assert_eq!(3, add_one(2));
    }
}

```

现在在顶级 _add_ 目录中运行 `cargo test`。在像这样的工作区中运行 `cargo test`，将会运行该工作区中所有 crate 的测试。

<!-- manual-regeneration
cd listings/ch14-more-about-cargo/no-listing-04-workspace-with-tests/add
cargo test
copy output below; the output updating script doesn't handle subdirectories in
paths properly
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

输出的第一部分表明，在 `add_one` 目录下的 `it_works` 测试通过了。接下来的部分显示，在 `adder` 目录下没有发现任何测试。最后一部分则表明，在 `add_one` 目录下也没有发现任何文档测试。

我们还可以使用 `-p` 标志，从顶级目录开始，在工作区中测试某个特定的 crate，只需指定我们想要测试的 crate 的名称即可。

<!-- manual-regeneration
cd listings/ch14-more-about-cargo/no-listing-04-workspace-with-tests/add
cargo test -p add_one
copy output below; the output updating script doesn't handle subdirectories in paths properly
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

该输出显示，只有针对 `add_one` 包进行了测试，而没有对 `adder` 包进行测试。

如果您将工作区中的包发布到[crates.io](https://crates.io/)<!-- ignore -->，那么工作区中的每个包都需要单独发布。就像`cargo test`一样，我们可以通过使用`-p`标志并指定要发布的包的名称来发布工作区中的特定包。

为了进行额外的练习，请以与添加 `add_one` crate 类似的方式，将 `add_two` crate 添加到这个工作区中！

随着你的项目不断发展，考虑使用工作区：它可以帮助你处理更小、更易于理解的代码组件，而不是一大块难以理解的代码。此外，将相关库放在一个工作区中，可以更容易地协调那些经常同时被修改的库。