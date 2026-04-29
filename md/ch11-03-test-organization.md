## 测试组织

正如本章开头所提到的，测试是一门复杂的学科，不同的人会使用不同的术语和组织方式。Rust社区将测试主要分为两类：单元测试和集成测试。单元测试规模较小，针对性较强，每次只测试一个模块，并且可以测试私有的接口。而集成测试则完全独立于你的库进行，以与其他外部代码相同的方式使用你的代码。代码将仅使用公共接口，并且每个测试可能会调用多个模块。

编写这两种类型的测试非常重要，以确保你的库中的各个组件能够分别和共同实现你所期望的功能。

### 单元测试

单元测试的目的是将每个代码单元与其余代码分离开来进行测试，以便快速找出代码是否存在异常。您需要在每个包含待测试代码的文件中，将单元测试代码放在`_src_`目录下。通常的做法是在每个文件中创建一个名为``tests``的模块来存放测试函数，并在该模块中添加``cfg(test)``的注释。

#### `tests`模块和`#[cfg(test)]`

在 `tests` 模块上使用了 `#[cfg(test)]` 注释，这告诉 Rust 仅在您运行 `cargo test` 时才会编译和运行测试代码，而不是在运行 `cargobuild` 时。这样可以在仅构建库的情况下节省编译时间，并且由于测试代码没有被包含在最终编译的文件中，因此还可以节省存储空间。您会注意到，因为集成测试位于不同的目录中，所以它们不需要 `#[cfg(test)]` 注释。不过，因为单元测试……测试代码与代码文件放在同一个文件中，你可以使用 ``#[cfg(test)]`` 来指定它们不应该被包含在编译后的结果中。

回想一下，在本章的第一部分中，当我们生成新的`adder`项目时，Cargo为我们生成了这段代码：

<span class="filename">文件名：src/lib.rs</span>

```rust,noplayground
{{#rustdoc_include ../listings/ch11-writing-automated-tests/listing-11-01/src/lib.rs}}
```

在自动生成的`tests`模块中，属性`cfg`表示“configuration_”，它向Rust表明，只有在特定配置选项存在的情况下，才应该包含以下元素。在这种情况下，配置选项是`test`，这是Rust为编译和运行测试而提供的功能。通过使用`cfg`属性，Cargo仅在我们主动运行测试时才会编译我们的测试代码。包括`cargo test`在内的所有辅助函数。此外，还包括可能位于该模块内的任何辅助函数，以及被标记为`#[test]`的函数。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="测试私有功能"></a>

#### 私有函数测试

在测试领域，存在关于是否应该直接测试私有函数的争论。其他语言使得测试私有函数变得困难甚至不可能。无论你遵循哪种测试理念，Rust的隐私规则确实允许你测试私有函数。请参考清单11-12中的代码，其中包含了私有函数`internal_adder`。

<列表编号="11-12" 文件名称="src/lib.rs" 标题="测试一个私有函数">

```rust,noplayground
{{#rustdoc_include ../listings/ch11-writing-automated-tests/listing-11-12/src/lib.rs}}
```

</清单>

请注意，`internal_adder`这个函数并没有被标记为`pub`。这些测试只是简单的Rust代码，而`tests`模块也只是另一个模块而已。正如我们在“在模块树中引用项目的路径”一文中讨论的那样，子模块中的项目可以使用其祖先模块中的项目。在这个测试中，我们将属于`tests`模块的所有的项目都带入了……使用`use super::*`来定义作用域，然后测试可以调用`internal_adder`。如果你认为私有函数不应该被测试，那么在Rust中没有任何东西会迫使你这么做。

### 集成测试

在Rust中，集成测试完全独立于你的库。它们以与其他代码相同的方式使用yourlibrary，这意味着它们只能调用属于你的库公共API中的函数。它们的目的是测试你的库的多个部分是否能够正确地协同工作。那些能够独立正常运行的代码单元在集成后可能会出现问题，因此集成代码的测试覆盖率也很重要。为了创建集成测试……在编写测试时，首先需要创建一个`_tests_`目录。

#### _tests_ 目录

我们在项目目录的顶层创建一个名为`_tests`的目录，该目录位于`_src`的旁边。Cargo会知道在这个目录中寻找集成测试文件。然后，我们可以创建任意数量的测试文件，Cargo会将每个文件分别编译成一个独立的包。

让我们创建一个集成测试。在Listing 11-12中的代码仍然位于`src/lib.rs`文件中时，创建一个`_tests_`目录，并创建一个新的文件，名为`tests/integration_test.rs`。你的目录结构应该如下所示：

```text
adder
├── Cargo.lock
├── Cargo.toml
├── src
│   └── lib.rs
└── tests
    └── integration_test.rs
```

将清单11-13中的代码输入到`_tests/integration_test.rs_`文件中。

<列表编号="11-13" 文件名称="tests/integration_test.rs" 标题="对`adder` crate中一个函数的集成测试">

```rust,ignore
{{#rustdoc_include ../listings/ch11-writing-automated-tests/listing-11-13/tests/integration_test.rs}}
```

</清单>

`_tests_`目录中的每个文件都是一个独立的库，因此我们需要将我们的库引入每个测试库的上下文中。为此，我们在代码的开头添加了`use adder::add_two;`，而在单元测试中并不需要这一行代码。

我们不需要在`_tests/integration_test.rs_`中标注任何代码，因为``#[cfg(test)]``。Cargo会特别处理`_tests/`目录，并且只有当我们运行``cargo test``时，才会编译该目录中的文件。现在就运行``cargo test``吧：

```console
{{#include ../listings/ch11-writing-automated-tests/listing-11-13/output.txt}}
```

输出的三个部分包括单元测试、集成测试以及文档测试。请注意，如果某个部分的测试失败，那么后续的部分将不会运行。例如，如果单元测试失败，那么集成测试和文档测试就不会有输出，因为这些测试只有在所有单元测试都通过之后才会运行。

单元测试的第一部分与我们之前看到的相同：每个单元测试对应一行代码（我们在清单11-12中添加了一个名为`internal`的测试），然后还有一段关于这些单元测试的总结信息。

集成测试部分以`Running tests/integration_test.rs`这一行开始。接下来，每个集成测试中的测试函数都有对应的行，而在``Doc-tests adder``部分开始之前，还有一行用于总结集成测试的结果。

每个集成测试文件都有自己独立的章节，因此如果我们继续在`tests_`目录下添加更多的文件，那么就会有更多的集成测试章节。

我们仍然可以通过将测试函数的名称作为参数传递给`cargo test`来运行特定的集成测试函数。要运行某个特定集成测试文件中的所有测试，可以使用`cargo test`的`--test`参数，然后加上该文件的名称。

```console
{{#include ../listings/ch11-writing-automated-tests/output-only-05-single-integration/output.txt}}
```

此命令仅运行`_tests/integration_test.rs_`文件中的测试。

#### 集成测试中的子模块

随着您增加更多的集成测试，您可能需要在tests_目录下创建更多文件来帮助组织这些测试；例如，可以根据测试的功能来分组测试函数。如前所述，tests_目录中的每个文件都会被编译成独立的crate，这对于创建不同的环境以更接近最终用户的实际使用方式非常有用。不过，这意味着tests_目录中的文件不会……就像你在第7章中学到的那样，将代码分割成模块和文件时，这些文件的行为应该与`_src_`中的文件相同。

在多个集成测试文件中使用一组辅助函数时，_tests_目录文件的行为差异最为明显。此时，如果我们尝试按照第7章中的“将模块分离到不同的文件中”这一章节的指导原则，将这些辅助函数提取到一个共同的模块中，就会遇到一些问题。例如，如果我们创建了`_tests/common.rs`文件，并在其中定义了一个名为``setup``的函数，那么我们可以在``setup``中添加一些代码……我们希望在多个测试文件中，从多个测试函数中调用这些函数：

<span class="filename">文件名：tests/common.rs</span>

```rust,noplayground
{{#rustdoc_include ../listings/ch11-writing-automated-tests/no-listing-12-shared-test-code-problem/tests/common.rs}}
```

当我们再次运行测试时，会在`common.rs_`文件的测试输出中看到一个新章节，尽管这个文件并不包含任何测试函数，而且我们也没有在任何地方调用过``setup``这个函数。

```console
{{#include ../listings/ch11-writing-automated-tests/no-listing-12-shared-test-code-problem/output.txt}}
```

在测试结果显示出`common`的情况下，同时还会显示`running 0 tests`，这并不是我们想要的。我们只是想与其他集成测试文件共享一些代码而已。为了避免`common`出现在测试输出中，我们不会创建_tests/common.rs_，而是会创建_tests/common/mod.rs_。现在项目目录看起来是这样的：

```text
├── Cargo.lock
├── Cargo.toml
├── src
│   └── lib.rs
└── tests
    ├── common
    │   └── mod.rs
    └── integration_test.rs
```

这是较旧的命名规范，Rust也支持这种命名方式，我们在第7章的“替代文件路径”部分中提到过这一点。通过这种方式命名文件，可以告诉Rust不要将`common`模块视为集成测试文件。当我们把`setup`函数的代码移动到`_tests/common/mod.rs_`中，并删除`_tests/common.rs_`文件后，测试输出中的相关部分将不再出现。位于`_tests`目录子目录中的文件不会被编译。在测试输出中分别列出不同的包或各个部分。

在我们创建了`_tests/common/mod.rs_`之后，就可以在任何集成测试文件中将其作为模块来使用。以下是一个从`_tests/integration_test.rs_`中的``it_adds_two``测试调用``setup``函数的示例：

<span class="filename">文件名：tests/integration_test.rs</span>

```rust,ignore
{{#rustdoc_include ../listings/ch11-writing-automated-tests/no-listing-13-fix-shared-test-code-problem/tests/integration_test.rs}}
```

请注意，``mod common;``的声明与我们在Listing 7-21中展示的模块声明相同。然后，在测试函数中，我们可以调用``common::setup()``函数。

#### 二进制包集成测试

如果我们的项目是一个二进制包，只包含`_src/main.rs_`文件，而没有`_src/lib.rs_`文件，那么我们无法在`tests_`目录下创建集成测试，也无法通过``use``语句将`_src/main.rs_`文件中定义的函数引入到测试范围内。只有库级包才会暴露其他包可以使用的函数；二进制包则旨在独立运行。

这是为什么那些提供二进制文件的Rust项目都有一个简单的`_src/main.rs_`文件，该文件调用了位于`_src/lib.rs_`文件中的逻辑。采用这种结构后，集成测试可以使用``use``来测试库，从而确保重要的功能能够正常使用。如果重要功能能够正常工作，那么`_src/main.rs_`文件中的少量代码也会正常运行，而这部分代码就不需要再进行单独的测试了。

## 摘要

Rust的测试功能提供了一种方式，可以指定代码应该如何运行，从而确保在进行更改时代码仍能按照预期正常工作。单元测试可以分别测试库的不同部分，并且可以测试私有的实现细节。集成测试则检查库的多个部分是否能够正确协同工作，它们使用库的公共API来测试代码，就像外部代码使用它一样。尽管Rust的类型系统……所有权规则有助于预防某些类型的错误，测试对于减少与代码预期行为相关逻辑错误仍然非常重要。

让我们把本章以及之前章节中学到的知识结合起来，来开展一个项目吧！

[路径]: ch07-03-paths-for-referring-to-an-item-in-the-module-tree.html  
[将模块分离为文件]: ch07-05-separating-modules-into-different-files.html  
[备用路径]: ch07-05-separating-modules-into-different-files.html#alternate-file-paths