## 将Crate发布到Crates.io

我们使用了来自[crates.io](https://crates.io/)的包作为我们项目的依赖项，但您也可以通过发布自己的包来与他人分享代码。crates.io的包注册表负责分发您的包的源代码，因此这里主要展示的是开源代码。

Rust和Cargo拥有一些功能，能够让人们更容易找到和使用你发布的软件包。接下来我们将讨论其中的一些功能，然后说明如何发布一个软件包。

### 编写有用的文档注释

准确记录你的软件包的信息可以帮助其他用户了解如何以及何时使用它们，因此花时间编写文档是值得的。在第三章中，我们讨论了如何使用两个斜杠 ``//`` 来注释 Rust 代码。Rust 还有一种专门用于文档注释的特殊类型注释，通常被称为“文档注释”，这种注释会生成 HTML 文档。HTML 会显示那些用于公开 API 项的文档注释内容，这些项旨在帮助程序员了解如何“使用”你的软件包，而不是了解你的软件包的“实现方式”。

文档注释使用三个斜杠，即`///`，而不是两个斜杠，并且支持Markdown格式来表示文本的格式。将文档注释放在它们所标注的项目之前即可。列表14-1展示了名为`my_crate`的包中一个`add_one`函数的文档注释。

<Listing number="14-1" file-name="src/lib.rs" caption="关于一个函数的文档注释">

```rust,ignore
{{#rustdoc_include ../listings/ch14-more-about-cargo/listing-14-01/src/lib.rs}}
```

</ Listing>

在这里，我们描述了 `add_one` 函数的功能，接着是一个标题为 `Examples` 的部分，然后提供了使用 `add_one` 函数的代码示例。我们可以通过运行 `cargo doc` 来生成HTML文档。这个命令会调用随Rust一起提供的 `rustdoc` 工具，并将生成的HTML文档存放在 _target/doc_ 目录下。

为了方便起见，运行 `cargo doc --open` 将会生成当前 crate 的文档内容（以及所有依赖项的文档内容），并将结果在网页浏览器中打开。导航到 `add_one` 函数，您将看到文档注释中的文本是如何被渲染的，如图 14-1 所示。

<img alt="`add_one`函数的渲染HTML文档" src="img/trpl14-01.png" class="center" />

<span class="caption">图14-1：`add_one`函数的HTML文档</span>

#### 常用章节

我们在 Listing 14-1 中使用了 `# Examples` Markdown 标题来创建一个名为“示例”的章节。以下是其他一些开发者在文档中常用的章节类型：

- **恐慌情况**：这些是被记录的函数可能会陷入恐慌的场景。那些不希望自己的程序陷入恐慌的调用者，应该确保在这种情况下不要调用该函数。
- **错误**：如果该函数返回了一个`Result`，那么描述可能发生的不同类型的错误以及可能导致这些错误出现的条件，对于调用者来说非常有帮助，这样他们就可以编写代码来应对不同类型的错误。
- **安全性**：如果该函数是`unsafe`才应被调用（我们在第20章中讨论了不安全性问题），那么应该有一个部分来解释为什么该函数是不安全的，并且说明该函数期望调用者遵守哪些不变性条件。

大多数文档注释并不需要所有这些部分，但这是一个很好的清单，可以提醒您用户感兴趣了解的代码相关方面。

#### 文档注释作为测试

在文档注释中添加示例代码块可以帮助演示如何使用你的库，并且还有一个额外的好处：运行`cargo test`时，文档中的代码示例会作为测试运行！没有什么比带有示例的文档更好的了。但是，如果由于代码在编写文档之后发生了变化，导致示例无法正常运行，那可就糟糕了。如果我们使用文档来运行`add_one`函数的`cargo test`，我们会看到测试结果中有一个这样的部分：

<!-- 手动重新生成
cd listings/ch14-more-about-cargo/listing-14-01/
cargo test
复制下面的仅包含文档测试部分的代码
-->

```text
   Doc-tests my_crate

running 1 test
test src/lib.rs - add_one (line 5) ... ok

test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.27s
```

现在，如果我们修改函数或示例中的 `assert_eq!`，使其引发 panic 错误，然后再次运行 `cargo test`，我们会发现文档测试会发现示例和代码之间存在同步问题！

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="commenting-contained-items"></a>

#### 包含的项目注释

doc注释`//!`的风格是将文档信息添加到包含这些注释的项本身，而不是添加到注释之后的其他项中。我们通常将这些doc注释放在库根文件（按照惯例是`_src/lib.rs_`）中，或者在一个模块内，以描述整个库或模块的内容。

例如，为了添加描述包含`add_one`函数的`my_crate` crate的功能说明，我们需要在`_src/lib.rs_`文件的开头添加以`//!`开头的文档注释，如清单14-2所示。

<列表编号="14-2" 文件名称="src/lib.rs" 标题="关于 `my_crate` 这个 crate 的文档">

```rust,ignore
{{#rustdoc_include ../listings/ch14-more-about-cargo/listing-14-02/src/lib.rs:here}}
```

</ Listing>

请注意，最后一行之后并没有以 ``//!``开头的任何代码。因为我们是以 ``//!``而不是 ``///``开始注释的，所以我们实际上是在记录包含这条注释的项目，而不是在这条注释之后的项目。在这种情况下，那个项目就是`_src/lib.rs_`文件，也就是 crate的根目录。这些注释描述了整个 crate 的内容。

当我们运行 `cargo doc --open` 时，这些注释将会显示在 `my_crate` 的文档首页上，位于 crate 中公开项目的列表上方，如图 14-2 所示。

在项目中的文档注释非常有用，尤其是用于描述 crate 和 module 时。使用这些注释来解释容器的整体目的，以帮助用户理解该项目的组织结构。

<img alt="包含整个软件包的HTML文档渲染结果及注释" src="img/trpl14-02.png" class="center" />

<span class="caption">图14-2：`my_crate`的渲染文档，包括描述整个软件包的注释</span>

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="导出一个方便的公共API并支持公众使用"></a>

### 导出便捷的公共API

在发布一个crate时，你的公共API的结构是一个重要的考虑因素。使用你的crate的人可能比你更不熟悉这个结构，如果你的crate中有复杂的模块层次结构，他们可能会难以找到他们想要使用的部分。

在第七章中，我们介绍了如何使用 ``pub`` 关键字将项目设为公开，以及如何使用 ``use`` 关键字将其引入某个作用域。然而，在开发软件库时你认为合适的结构，可能对用户来说并不方便。你可能希望将结构体组织成多层层次结构，但那些需要使用你在深层结构中定义的类型的人可能会遇到查找该类型存在的困难。他们还可能因为必须输入 `use my_crate::some_module::another_module::UsefulType;` rather than `use my_crate::UsefulType;` 这样的代码而感到烦恼。

好消息是，如果某个结构让其他用户难以从其他库中使用，那么您不必重新调整内部组织结构：相反，您可以使用 ``pub use`` 将某些元素重新导出，从而创建一个与您的私有结构不同的公共结构。*重新导出*操作是将某个公共元素从一个位置复制到另一个位置，就好像该元素被定义在那个位置一样。

例如，假设我们创建了一个名为 ``art`` 的库，用于建模艺术概念。在这个库中包含两个模块：一个名为 ``kinds`` 的模块，其中包含两个枚举类型，分别是 ``PrimaryColor`` 和 ``SecondaryColor``；另一个名为 ``utils`` 的模块中包含一个名为 ``mix`` 的函数，如清单 14-3 所示。

<listing number="14-3" file-name="src/lib.rs" caption="一个包含多个模块的`art`库，这些模块被组织成`kinds`和`utils`两个部分">

```rust,noplayground,test_harness
{{#rustdoc_include ../listings/ch14-more-about-cargo/listing-14-03/src/lib.rs:here}}
```

</ Listing>

图14-3展示了由`cargo doc`生成的该软件包文档的首页样式。

<img alt="关于 `art`  crate 的渲染文档，该 crate 列出了 `kinds` 和 `utils` 模块" src="img/trpl14-03.png" class="center" />

<span class="caption">图14-3：`art`文档的首页，其中列出了`kinds`和`utils`模块</span>

请注意，``PrimaryColor``和``SecondaryColor``这两种类型并没有出现在主页上，同样，``mix``这个函数也没有被列出。我们必须点击``kinds``和``utils``才能看到它们。

另一个依赖此库的包需要包含`use`语句，这些语句会将`art`中的内容带入作用域，并指定当前定义的模块结构。列表14-4展示了一个使用`art`库中的`PrimaryColor`和`mix`的示例。

<列表编号="14-4" 文件名称="src/main.rs" 标题="一个使用`art` crate的项的内部结构的crate">

```rust,ignore
{{#rustdoc_include ../listings/ch14-more-about-cargo/listing-14-04/src/main.rs}}
```

</ Listing>

清单14-4中的代码作者使用了`art`这个库，他们需要弄清楚`PrimaryColor`位于`kinds`模块中，而`mix`则位于`utils`模块中。`art`库的模块结构对于使用`art`库的开发者来说更为重要，而不是那些正在使用该库的开发者。其内部结构并不包含任何有助于理解如何使用`art`库的信息，反而会引起混淆，因为使用该库的开发者需要自己找出应该查找的地方，并且必须在`use`语句中明确指定模块名称。

为了从公共API中移除内部组织结构，我们可以修改清单14-3中的`art` crate代码，添加`pub use`语句，以重新导出顶层级别的 items，如清单14-5所示。

<列表编号="14-5" 文件名称="src/lib.rs" 标题="在重新导出的项目中添加 `pub use` 语句">

```rust,ignore
{{#rustdoc_include ../listings/ch14-more-about-cargo/listing-14-05/src/lib.rs:here}}
```

</ Listing>

`cargo doc`为这个 crate生成的API文档现在会在首页上列出并链接到各种重新导出功能，如图14-4所示。这样一来，`PrimaryColor`和`SecondaryColor`类型以及`mix`函数就更容易被找到了。

<img alt="关于 `art`  crate 的渲染文档，以及首页上的导出信息" src="img/trpl14-04.png" class="center" />

<span class="caption">图14-4：`art`文档的首页，列出了相关的重新导出信息</span>

`art`这个库的用户仍然可以查看和使用Listing 14-3中的内部结构，如Listing 14-4所示；或者他们可以使用Listing 14-5中更便捷的结构，如Listing 14-6所示。

<列表编号="14-6" 文件名称="src/main.rs" 标题="一个使用从`art` crate中重新导出的项的程序">

```rust,ignore
{{#rustdoc_include ../listings/ch14-more-about-cargo/listing-14-06/src/main.rs:here}}
```

</ Listing>

在存在许多嵌套模块的情况下，通过在顶层使用 ``pub use`` 重新导出类型，可以显著改善使用该软件包的用户的体验。另一个常见的用途是使用 ``pub use`` 来重新导出依赖库中的定义，从而使该依赖库的定义成为您自己软件包的公开API的一部分。

创建有用的公共API结构更像是一门艺术而非科学，你可以不断尝试以找到最适合用户的API。选择`pub use`可以让你在内部结构上拥有更大的灵活性，并将这种内部结构与用户所看到的界面分离开来。查看一些你已经安装过的软件包的代码，看看它们的内部结构是否与公共API有所不同。

### 创建 Crates.io 账户

在您发布任何 crate 之前，您需要先在[crates.io](https://crates.io/)上创建账户并获取一个 API 令牌。为此，请访问[crates.io](https://crates.io/)的主页，并通过 GitHub 账户登录。（目前使用 GitHub 账户是必需的，但未来该网站可能会支持其他方式的账户创建方式。）登录后，请访问[https://crates.io/me/](https://crates.io/me/)以查看您的账户设置，并获取您的 API 密钥。然后，运行`cargo login`命令，并在提示时输入您的 API 密钥。

```console
$ cargo login
abcdefghijklmnopqrstuvwxyz012345
```

此命令会将您的API令牌告知Cargo，并将其本地存储在`_~/.cargo/credentials.toml_`文件中。请注意，此令牌属于机密信息：切勿与任何人分享。如果您出于任何原因需要与他人共享该令牌，请撤销其权限，并在[crates.io](https://crates.io/)上生成新的令牌。

### 为新 crate 添加元数据

假设您有一个想要发布的 crate。在发布之前，您需要在该 crate 的 _Cargo.toml_ 文件的 `[package]` 部分中添加一些元数据。

你的 crate需要有一个独特的名称。在本地开发过程中，你可以随意为 crate命名。不过，[crates.io](https://crates.io/)上的 crate名称是按照先来先服务的原则进行分配的。一旦某个名称被占用，其他人就无法再使用该名称发布新的 crate了。在尝试发布一个 crate之前，请先搜索你想使用的名称。如果该名称已被使用，你需要另选一个名称，并在 _Cargo.toml_ 文件的 `[package]` 部分下的 `name` 字段中修改该名称，以便能够使用新名称进行发布。

<span class="filename">文件名：Cargo.toml</span>

```toml
[package]
name = "guessing_game"
```

即使您选择了一个独特的名称，在此时运行`cargo publish`来发布该软件包时，您会先收到一个警告，随后会遇到一个错误：

<!-- 手动重新生成
创建一个新包，使用未注册的名称，不再对生成的包进行任何修改，
因此缺少描述和许可证字段。
cargo publish
仅复制下面的相关行
-->

```console
$ cargo publish
    Updating crates.io index
warning: manifest has no description, license, license-file, documentation, homepage or repository.
See https://doc.rust-lang.org/cargo/reference/manifest.html#package-metadata for more info.
--snip--
error: failed to publish to registry at https://crates.io

Caused by:
  the remote server responded with an error (status 400 Bad Request): missing or empty metadata fields: description, license. Please see https://doc.rust-lang.org/cargo/reference/manifest.html for more information on configuring these fields
```

这会导致错误，因为你缺少一些关键信息：需要提供描述和许可证信息，这样人们才能知道你的软件包的功能以及他们可以在什么条件下使用它。在_Cargo.toml_文件中，添加一个描述，内容只需一两句话即可，因为这个描述会与你的软件包一起出现在搜索结果中。对于`license`字段，你需要提供一个_许可证标识符_。Linux基金会的软件包数据交换规范[SPDX]列出了可以用于此字段的标识符。例如，如果你想说明你使用的是MIT许可证来授权你的软件包，那么就在`MIT`字段中添加相应的标识符。

<span class="filename">文件名：Cargo.toml</span>

```toml
[package]
name = "guessing_game"
license = "MIT"
```

如果您想使用在 SPDX 中未出现的许可证，则需要将该许可证的文本放在一个文件中，并将该文件包含在您的项目中。然后，可以使用 ``license-file`` 来指定该文件的名称，而不是使用 ``license`` 键。

关于您的项目应适用哪种许可证的指南超出了本书的范围。Rust社区中的许多人都采用与Rust相同的许可证方式，即使用`MIT OR Apache-2.0`的双重许可证。这种做法表明，您也可以通过`OR`分隔多个许可证标识符，从而为您的项目设置多个许可证。

一个具有独特名称、版本号、描述以及已添加的许可证的`_Cargo.toml_`文件，适用于准备发布的项目，可能如下所示：

<span class="filename">文件名：Cargo.toml</span>

```toml
[package]
name = "guessing_game"
version = "0.1.0"
edition = "2024"
description = "A fun game where you guess what number the computer has chosen."
license = "MIT OR Apache-2.0"

[dependencies]
```

[Cargo的文档](https://doc.rust-lang.org/cargo/)中描述了其他可以指定的元数据，这些元数据有助于他人更轻松地发现和使用你的库。

### 发布到Crates.io

现在你已经创建了一个账户，保存了你的API令牌，为你的软件包选择了名称，并指定了所需的元数据，那么你就已经准备好发布啦！发布一个软件包意味着将特定版本上传到[crates.io](https://crates.io/)供其他人使用。

请注意，发布的内容是永久性的。该版本无法被覆盖，除非在特定情况下，否则代码也无法被删除。Crates.io的主要目标之一就是作为代码的永久存储库，这样所有依赖crates的项目在[crates.io](https://crates.io/)上的构建都能继续正常运行。允许删除版本将使得实现这一目标变得不可能。不过，您可以发布任意数量的crate版本。

再次运行 `cargo publish` 命令。现在应该会成功执行了：

<!-- 手动重新生成
进入某个有效的 crate，发布一个新版本
使用 cargo publish
复制下面相关的代码行
-->

```console
$ cargo publish
    Updating crates.io index
   Packaging guessing_game v0.1.0 (file:///projects/guessing_game)
    Packaged 6 files, 1.2KiB (895.0B compressed)
   Verifying guessing_game v0.1.0 (file:///projects/guessing_game)
   Compiling guessing_game v0.1.0
(file:///projects/guessing_game/target/package/guessing_game-0.1.0)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.19s
   Uploading guessing_game v0.1.0 (file:///projects/guessing_game)
    Uploaded guessing_game v0.1.0 to registry `crates-io`
note: waiting for `guessing_game v0.1.0` to be available at registry
`crates-io`.
You may press ctrl-c to skip waiting; the crate should be available shortly.
   Published guessing_game v0.1.0 at registry `crates-io`
```

恭喜！你现在已经将你的代码分享给了Rust社区，任何人都可以轻松地将你的库作为依赖项添加到他们的项目中。

### 发布现有 crate 的新版本

当你对你的项目进行了修改，并且准备发布一个新版本时，你需要修改 _Cargo.toml_ 文件中指定的 `version` 值，然后重新发布。使用[语义版本控制规则][semver]来确定基于你所做的修改，合适的下一个版本号是什么。之后，运行 `cargo publish` 来上传新版本。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="移除Cratesio中的版本使用Cargo-Yank"></a>
<a id="不再使用Cratesio中的旧版本"></a>

### 从Crates.io中移除不再使用的版本

虽然无法删除某个包的先前版本，但可以阻止未来的项目将其作为新的依赖项添加到项目中。当某个包的版本因某种原因出现问题时，这一点非常有用。在这种情况下，Cargo支持将某个包的版本进行迁移。

**版本拉取**可以阻止新项目依赖该版本，同时允许所有依赖该版本的现有项目继续运行。本质上来说，版本拉取意味着所有包含`_Cargo.lock_`文件的项目都不会受到影响，而未来生成的`_Cargo.lock_`文件将不会使用被拉取的版本。

要在之前已发布的 crate 的目录中复制某个版本，请运行 `cargo yank`，并指定想要复制的版本。例如，如果我们发布了一个名为 `guessing_game` 的 crate，其版本为 1.0.1，并且我们想要复制该版本，那么我们需要在项目目录中运行以下命令来获取 `guessing_game`：

<!-- 手动重新生成：
cargo yank carol-test --version 2.1.0
cargo yank carol-test --version 2.1.0 --undo
-->

```console
$ cargo yank --vers 1.0.1
    Updating crates.io index
        Yank guessing_game@1.0.1
```

通过在命令中添加`--undo`，您还可以撤销“yank”操作，并让项目能够再次根据版本来启动：

```console
$ cargo yank --vers 1.0.1 --undo
    Updating crates.io index
      Unyank guessing_game@1.0.1
```

“Yank”并不会删除任何代码。例如，它无法不小心删除上传的敏感信息。如果发生这种情况，你必须立即重置这些敏感信息。

[spdx]: https://spdx.org/licenses/  
[semver]: https://semver.org/