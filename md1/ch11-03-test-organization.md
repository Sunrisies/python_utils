## 测试组织

正如本章开头所提到的，测试是一门复杂的学科，不同的人会使用不同的术语和组织方式。Rust社区将测试主要分为两类：单元测试和集成测试。单元测试规模较小且更加专注，每次只测试一个模块，并且可以测试私有接口。集成测试则完全独立于你的库进行，以与其他外部代码相同的方式使用你的代码，仅使用公共接口进行测试，并且每个测试可能会涉及多个模块。

编写这两种类型的测试非常重要，以确保你的库中的各个组件能够分别和共同实现你所期望的功能。

### 单元测试

单元测试的目的是将每个代码单元独立地测试，以便快速找出代码是否存在异常行为。您需要在每个包含待测试代码的文件中，将单元测试代码放在`_src_`目录下。通常的做法是在每个文件中创建一个名为``tests``的模块来存放测试函数，并在该模块中添加``cfg(test)``的注释。

#### `tests` 模块与 `#[cfg(test)]`

在 `tests` 模块上添加的 ``#[cfg(test)]`` 注解告诉 Rust，只有在运行 `cargo test` 时，才会编译并运行测试代码，而不是在运行 `cargo build` 时。这样可以在仅构建库的情况下节省编译时间，并且由于测试代码没有被包含在最终编译的产物中，因此还能节省空间。你会注意到，因为集成测试位于不同的目录中，所以不需要使用 ``#[cfg(test)]`` 注解。然而，由于单元测试与代码位于同一文件中，因此需要使用 ``#[cfg(test)]`` 来指定它们不应被包含在编译后的结果中。

回想一下，在本章的第一节中，当我们生成新的`adder`项目时，Cargo为我们生成了这段代码：

<span class="filename">文件名：src/lib.rs</span>

```rust,noplayground
{{#rustdoc_include ../listings/ch11-writing-automated-tests/listing-11-01/src/lib.rs}}
```

在自动生成的 ``tests`` 模块中，属性 ``cfg`` 表示“配置”，它向Rust表明，只有在特定配置选项存在的情况下，才应包含以下内容。在这种情况下，该配置选项是 ``test``，这是Rust为编译和运行测试而提供的功能。通过使用属性 ``cfg``，Cargo仅在我们主动使用 ``cargo test`` 来运行测试时，才会编译我们的测试代码。这包括可能位于该模块中的任何辅助函数，以及那些被标记为 ``#[test]`` 的函数。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="测试私有函数"></a>

#### 私有函数测试

在测试社区中，关于私有函数是否应该被直接测试存在争议，而其他语言则使得对私有函数的测试变得困难甚至不可能。无论你遵循哪种测试理念，Rust的隐私规则确实允许你对私有函数进行测试。请参考清单11-12中的代码，其中包含了私有函数`internal_adder`。

<listing number="11-12" file-name="src/lib.rs" caption="测试一个私有函数">

```rust,noplayground
{{#rustdoc_include ../listings/ch11-writing-automated-tests/listing-11-12/src/lib.rs}}
```

</ Listing>

请注意，`internal_adder`这个函数并没有被标记为`pub`。这些测试只是普通的Rust代码而已，而`tests`模块也只是一个普通的模块。正如我们在[“在模块树中引用项目的方法”][paths]<!-- ignore -->一文中讨论过的，子模块中的项目可以使用其祖先模块中的项目。在这个测试中，我们通过`use super::*`将属于`tests`模块的所有的项目都带入到作用域中，然后测试就可以调用`internal_adder`了。如果你认为私有函数不应该被测试，那么在Rust中并没有什么强制要求你必须这么做。

### 集成测试

在Rust中，集成测试完全独立于你的库。它们以与其他代码相同的方式使用你的库，这意味着它们只能调用属于你库公共API中的函数。它们的目的是测试库中的多个部分是否能够正确协同工作。那些本身能够正常运行的代码单元在集成后可能会出现问题，因此集成代码的测试覆盖度也很重要。要创建集成测试，首先需要创建一个`_tests_`目录。

#### _tests_ 目录

我们在项目目录的顶层创建一个名为`_tests`的目录，该目录位于`_src`目录下。Cargo会知道在这个目录中寻找集成测试文件。然后，我们可以创建任意数量的测试文件，Cargo会将每个文件单独编译成一个独立的软件包。

让我们创建一个集成测试。在清单11-12中的代码仍然位于`src/lib.rs`文件中，请创建一个`_tests_`目录，并创建一个新的文件，名为`tests/integration_test.rs`。你的目录结构应该如下所示：

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

<列表编号="11-13" 文件名称="tests/integration_test.rs" 标题="对`adder` crate中某个函数的集成测试">

```rust,ignore
{{#rustdoc_include ../listings/ch11-writing-automated-tests/listing-11-13/tests/integration_test.rs}}
```

</ Listing>

`_tests_`目录中的每个文件都是一个独立的库，因此我们需要将我们的库引入每个测试库的上下文中。为此，我们在代码的开头添加了`use adder::add_two;`，而在单元测试中并没有使用到这个宏。

我们不需要在`_tests/integration_test.rs_`中标注任何代码，因为`#[cfg(test)]`。Cargo会特别处理`_tests/`目录，并且只有当我们运行`cargo test`时，才会编译该目录中的文件。现在就运行`cargo test`吧：

```console
{{#include ../listings/ch11-writing-automated-tests/listing-11-13/output.txt}}
```

输出的三个部分包括单元测试、集成测试以及文档测试。请注意，如果某个部分的测试失败了，那么后续的部分就不会被执行。例如，如果单元测试失败了，那么集成测试和文档测试就不会被执行，因为只有当所有单元测试都通过之后，这些测试才会被执行。

单元测试的第一部分与我们之前看到的相同：每个单元测试对应一行代码（我们在清单11-12中添加了一个名为`internal`的代码），然后还有一段关于这些单元测试的总结信息。

集成测试部分以 `Running tests/integration_test.rs` 这一行开始。接下来，每个集成测试中的测试函数都有对应的行，而在 ``Doc-tests adder`` 部分开始之前，还有一行用于总结集成测试的结果。

每个集成测试文件都有自己独立的章节，因此如果我们继续在`tests_`目录下添加更多的文件，那么就会有更多的集成测试章节。

我们仍然可以通过将测试函数的名称作为参数传递给`cargo test`来运行特定的集成测试函数。要运行特定集成测试文件中的所有测试，可以使用`cargo test`中的`--test`参数，然后加上该文件的名称。

```console
{{#include ../listings/ch11-writing-automated-tests/output-only-05-single-integration/output.txt}}
```

此命令仅运行`_tests/integration_test.rs_`文件中的测试。

#### 集成测试中的子模块

随着您增加更多的集成测试，您可能需要在`tests_`目录下创建更多文件来组织这些测试；例如，可以根据测试的功能将测试函数分组。如前所述，`tests_`目录中的每个文件都会被编译成独立的软件包，这对于创建不同的作用域以更接近最终用户的实际使用方式非常有用。然而，这意味着`tests_`目录中的文件与`_src_`目录中的文件不会具有相同的行为，正如您在第七章中所学到的那样，关于如何将代码划分为模块和文件的细节。

在多个集成测试文件中使用一组辅助函数时，_tests_目录文件的行为差异最为明显。此时，如果你尝试按照第7章中的“将模块分离到不同文件”部分所述方法，将这些辅助函数提取到一个共同的模块中，就会遇到一些问题。例如，如果我们创建了一个名为`_tests/common.rs`的文件，并在其中定义了一个名为`setup`的函数，那么我们可以在`setup`中添加一些代码，这些代码可以在多个测试文件的多个测试函数中被调用。

<span class="filename">文件名：tests/common.rs</span>

```rust,noplayground
{{#rustdoc_include ../listings/ch11-writing-automated-tests/no-listing-12-shared-test-code-problem/tests/common.rs}}
```

当我们再次运行测试时，会在`common.rs_`文件的测试输出中看到一个新章节，尽管这个文件并不包含任何测试函数，而且我们也没有在任何地方调用过``setup``这个函数。

```console
{{#include ../listings/ch11-writing-automated-tests/no-listing-12-shared-test-code-problem/output.txt}}
```

在测试结果显示出 `common` 的情况下，同时还会显示 `running 0 tests`，这并不是我们想要的。我们只是想与其他集成测试文件共享一些代码而已。为了避免 `common` 出现在测试输出中，我们不会创建 _tests/common.rs_ 文件，而是会创建 _tests/common/mod.rs_。现在项目目录看起来是这样的：

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

这是旧的命名规范，Rust同样理解我们在第7章的[“替代文件路径”][alt-paths]中提到的内容。采用这种命名方式可以告诉Rust不要将`common`模块视为集成测试文件。当我们把`setup`函数的代码移动到`_tests/common/mod.rs_`中，并删除`_tests/common.rs_`文件后，测试输出中的相关部分就不会再出现了。位于`_tests_`目录子目录中的文件不会被编译成独立的crates，也不会在测试输出中出现相关部分。

在创建了`_tests/common/mod.rs_`之后，我们可以在任何集成测试文件中将其作为模块来使用。以下是一个从`_tests/integration_test.rs_`中的__`INLINE_CODE_51__`测试调用__`INLINE_CODE_50__`函数的示例：

<span class="filename">文件名：tests/integration_test.rs</span>

```rust,ignore
{{#rustdoc_include ../listings/ch11-writing-automated-tests/no-listing-13-fix-shared-test-code-problem/tests/integration_test.rs}}
```

请注意，``mod common;``的声明与我们在Listing 7-21中展示的模块声明是相同的。然后，在测试函数中，我们可以调用``common::setup()``这个函数。

#### 二进制包集成测试

如果我们的项目是一个二进制 crate，只包含 _src/main.rs_ 文件，而没有 _src/lib.rs_ 文件，那么我们无法在 _tests_ 目录中创建集成测试，也无法通过 `use` 语句将 _src/main.rs_ 文件中定义的函数引入到代码范围内。只有库级 crate 才需要暴露其他 crate 可以使用的函数；而二进制 crate 则应该独立运行。

这是Rust项目中提供二进制文件的一个原因：它们有一个简单的`_src/main.rs_`文件，该文件调用位于`_src/lib.rs_`文件中的逻辑。采用这种结构后，集成测试可以使用``use``来测试库，从而确保重要的功能能够正常使用。如果重要功能能够正常工作，那么`_src/main.rs_`文件中少量的代码同样也能正常工作，而这部分代码就不需要再进行单独的测试了。

## 总结

Rust的测试功能提供了一种方式，可以指定代码应该如何运行，以确保即使在进行修改的情况下，代码仍然能够按照预期正常工作。单元测试可以分别测试库的不同部分，并且可以测试私有的实现细节。集成测试则检查库的多个部分是否能够正确协同工作，它们会利用库的公共API来测试代码，就像外部代码使用该代码一样。尽管Rust的类型系统和所有权规则有助于避免某些类型的错误，但测试仍然非常重要，因为它们有助于减少与代码预期行为相关的逻辑错误。

让我们结合本章以及之前章节中学到的知识，来开展一个项目吧！

[路径]: ch07-03-paths-for-referring-to-an-item-in-the-module-tree.html  
[将模块分离为不同的文件]: ch07-05-separating-modules-into-different-files.html  
[备用路径]: ch07-05-separating-modules-into-different-files.html#alternate-file-paths