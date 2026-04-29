## 控制测试的执行方式

正如`cargo run`会编译你的代码并运行生成的二进制文件一样，`cargo test`会在测试模式下编译你的代码，并运行相应的测试二进制文件。由`cargo test`生成的二进制文件的默认行为是并行运行所有测试，并捕获测试过程中产生的输出，从而避免输出被显示出来，使得与测试结果相关的输出更容易阅读。不过，你可以指定命令行选项来更改这一默认行为。

一些命令行选项会传递给`cargo test`，而另一些则会被传递到最终的测试二进制文件。为了区分这两种类型的参数，你需要先列出那些会传递给`cargo test`的参数，然后使用分隔符`--`来分隔它们，最后列出那些会传递到测试二进制文件的参数。运行`cargo test --help`可以显示你可以与`cargo test`一起使用的选项，而运行`cargo test -- --help`则可以显示在分隔符之后可以使用的选项。这些选项也在《`rustc`手册》的“测试”章节中有详细说明[tests]。

[测试代码]: https://doc.rust-lang.org/rustc/tests/index.html

### 并行或连续地运行测试

当你运行多个测试时，默认情况下，这些测试会使用线程并行执行，这意味着它们会更快完成，并且你可以更快地获得反馈。由于测试是同时进行的，因此你必须确保测试之间不会相互依赖，也不会依赖于任何共享状态，包括共享环境，比如当前的工作目录或环境变量。

例如，假设每个测试都会运行一些代码，这些代码会在磁盘上创建一个名为`_test-output.txt`的文件，并将一些数据写入该文件。然后，每个测试都会读取该文件中的数据，并断言文件中包含特定的值，而这些值在每次测试中都是不同的。由于测试是同时运行的，一个测试可能会在另一个测试写入和读取文件之间的时间内覆盖该文件。这样一来，第二个测试就会失败，但这不是因为代码本身有问题，而是因为测试在并行运行时相互干扰了。一种解决方案是确保每个测试写入不同的文件；另一种解决方案则是一次只运行一个测试。

如果您不想并行运行测试，或者希望对使用的线程数量进行更精细的控制，可以向测试二进制文件发送 ``--test-threads`` 标志以及您希望使用的线程数量。请看下面的示例：

```console
$ cargo test -- --test-threads=1
```

我们将测试线程的数量设置为`1`，这样程序就不会使用任何并行处理。使用单个线程进行测试会比并行测试花费更长的时间，但如果测试之间共享状态的话，它们就不会互相干扰。

### 显示函数输出

默认情况下，如果测试通过，Rust的测试库会捕获所有打印到标准输出的内容。例如，如果我们在一个测试中调用`println!`，并且测试通过了，我们不会在终端看到`println!`的输出内容，而只会看到表示测试通过的行。如果测试失败，我们会看到所有打印到标准输出的内容，以及失败的其余信息。

例如，清单11-10中有一个简单的功能，它打印出其参数的值，并返回10。此外，还有一个通过测试的例子和一个未通过测试的例子。

<列表编号="11-10" 文件名称="src/lib.rs" 标题="对调用 `println!` 的函数进行测试">

```rust,panics,noplayground
{{#rustdoc_include ../listings/ch11-writing-automated-tests/listing-11-10/src/lib.rs}}
```

</ Listing>

当我们使用`cargo test`运行这些测试时，将会看到如下输出：

```console
{{#include ../listings/ch11-writing-automated-tests/listing-11-10/output.txt}}
```

请注意，在这个输出中并没有看到`I got the value 4`，这个代码会在通过测试的测试用例运行时被打印出来。该输出已经被捕获了。而失败的测试用例的输出，即`I got the value 8`，则出现在测试总结输出的相应部分，其中还显示了导致测试失败的原因。

如果我们还想看到通过测试时的打印输出值，我们可以告诉Rust使用`--show-output`来显示成功测试的输出。

```console
$ cargo test -- --show-output
```

当我们再次使用 ``--show-output`` 标志运行清单 11-10 中的测试时，我们得到了如下输出：

```console
{{#include ../listings/ch11-writing-automated-tests/output-only-01-show-output/output.txt}}
```

### 根据名称运行部分测试

运行整个测试套件有时可能需要很长时间。如果你正在某个特定区域进行代码开发，你可能只想运行与那些代码相关的测试。你可以通过传递`cargo test`作为参数来选择要运行的测试。

为了演示如何运行部分测试，我们将首先为我们的`add_two`函数创建三个测试，如清单11-11所示，然后选择要运行的测试。

<listing number="11-11" file-name="src/lib.rs" caption="三个测试，每个都有不同的名称">

```rust,noplayground
{{#rustdoc_include ../listings/ch11-writing-automated-tests/listing-11-11/src/lib.rs}}
```

</ Listing>

如果我们在不传递任何参数的情况下运行测试，正如我们之前看到的那样，所有测试都将并行运行：

```console
{{#include ../listings/ch11-writing-automated-tests/listing-11-11/output.txt}}
```

#### 运行单个测试

我们可以将任何测试函数的名称传递给`cargo test`，以仅运行该测试：

```console
{{#include ../listings/ch11-writing-automated-tests/output-only-02-single-test/output.txt}}
```

只有名为`one_hundred`的测试运行了；其他两个测试的名称与那个名称不匹配。测试输出显示，还有更多的测试没有运行，因为在最后面显示了`2 filtered out`。

我们无法以这种方式指定多个测试的名称；只有给`cargo test`的第一个值会被使用。不过，还是有办法来运行多个测试。

#### 过滤以运行多个测试

我们可以指定测试名称的一部分，任何名称与该值匹配的测试都会被运行。例如，因为我们的两个测试名称中都包含`add`，我们可以通过运行`cargo test add`来运行这两个测试。

```console
{{#include ../listings/ch11-writing-automated-tests/output-only-03-multiple-tests/output.txt}}
```

该命令执行了所有包含 ``add`` 名称的测试，并过滤掉了名为 ``one_hundred`` 的测试。另外需要注意的是，某个测试所在的模块也会成为该测试名称的一部分，因此我们可以通过过滤模块名称来运行某个模块中的所有测试。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="除非特别要求，否则忽略某些测试"></a>

### 除非特别要求，否则忽略测试

有时候，一些特定的测试执行起来会非常耗时，因此你可能希望在运行`cargo test`时排除这些测试。与其将所有需要运行的测试作为参数列出，不如使用`ignore`属性来标注那些耗时的测试，从而将其排除在外，如下所示：

<span class="filename">文件名：src/lib.rs</span>

```rust,noplayground
{{#rustdoc_include ../listings/ch11-writing-automated-tests/no-listing-11-ignore-a-test/src/lib.rs:here}}
```

在 `#[test]` 之后，我们会在想要排除的测试中添加 `#[ignore]` 这一行代码。现在，当我们运行测试时，`it_works` 会执行，但 `expensive_test` 则不会被执行。

```console
{{#include ../listings/ch11-writing-automated-tests/no-listing-11-ignore-a-test/output.txt}}
```

`expensive_test`这个函数被列在`ignored`中。如果我们只想运行那些被忽略的测试，可以使用`cargo test -- --ignored`。

```console
{{#include ../listings/ch11-writing-automated-tests/output-only-04-running-ignored/output.txt}}
```

通过控制哪些测试会运行，你可以确保你的`cargo test`结果能够尽快得到返回。当你认为检查`ignored`测试的结果是有意义的，并且你有时间等待这些结果时，你可以选择运行`cargo test -- --ignored`。如果你想运行所有测试，无论它们是否被忽略，你可以运行`cargo test -- --include-ignored`。