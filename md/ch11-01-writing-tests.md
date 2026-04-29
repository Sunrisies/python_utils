## 如何编写测试

**测试**是Rust中的函数，用于验证非测试代码是否按预期方式运行。测试函数的主体通常会执行以下三个操作：

- 设置所需的数据或状态。  
- 运行你想要测试的代码。  
- 确认结果符合你的预期。

让我们来看看Rust专门为编写执行这些操作的测试而提供的功能，其中包括`test`属性、一些宏，以及`should_panic`属性。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="测试函数的结构"></a>

### 测试函数的结构

在Rust中，最简单的测试就是一个带有`test`属性的函数。属性是关于Rust代码的元数据；例如，我们在第5章中使用的`derive`属性用于结构体。要将一个函数转换为测试函数，需要在`fn`之前的行中添加`#[test]`。当你使用`cargo test`命令运行测试时，Rust会构建一个测试运行程序来执行测试。标注了每个测试函数的结果，包括该函数是否通过或未通过。

每当我们使用Cargo创建一个新的库项目时，系统会自动生成一个包含测试函数的测试模块。这个模块为你提供了编写测试的模板，这样每次开始一个新项目时都不需要重新查找具体的结构和语法。你可以根据需要添加任意数量的额外测试函数和测试模块！

在真正测试任何代码之前，我们将通过实验来探索测试的工作原理。然后，我们会编写一些实际中的测试，这些测试会调用我们编写的一些代码，并断言其行为是正确的。

让我们创建一个新的库项目，命名为`adder`，该项目将添加两个数字：

```console
$ cargo new adder --lib
     Created library `adder` project
$ cd adder
```

你的`adder`库中的`_src/lib.rs_`文件的内容应该如下所示：
清单11-1.

<列表编号="11-1" 文件名称="src/lib.rs" 标题="由 `cargo new` 自动生成的代码">

<!-- 手动重新生成
cd listings/ch11-writing-automated-tests
rm -rf listing-11-01
cargo new listing-11-01 --lib --name adder
cd listing-11-01
echo "$ cargo test" > output.txt
RUSTFLAGS="-A unused_variables -A dead_code" RUST_TEST_THREADS=1 cargo test >> output.txt 2>&1
git diff output.txt # 提交所有相关的更改；丢弃不相关的更改
cd ./../..
-->

```rust,noplayground
{{#rustdoc_include ../listings/ch11-writing-automated-tests/listing-11-01/src/lib.rs}}
```

</清单>

该文件以一个示例函数`add`开始，这样我们就有东西可以测试了。

目前，让我们只关注`it_works`这个函数。请注意`#[test]`的注释：这个属性表明这是一个测试函数，因此测试运行器会将其视为测试函数来处理。在`tests`模块中，可能还有一些非测试函数，用于设置常见场景或执行常见操作，因此我们必须始终明确哪些函数是测试函数。

这个示例函数体内使用了 ``assert_eq!`` 宏来断言 ``result`` 的值，其中 ``result`` 是通过将 2 和 2 传递给 ``add`` 得到的结果，该结果等于 4。这个断言展示了典型测试的格式。让我们运行一下这个测试，看看它是否通过。

`cargo test`命令会运行我们项目中的所有测试，如清单11-2所示。

<列表编号="11-2" 标题="运行自动生成的测试后的输出">

```console
{{#include ../listings/ch11-writing-automated-tests/listing-11-01/output.txt}}
```

</清单>

编译后的程序已经运行了测试。我们看到了``running 1 test``这一行。下一行显示了生成的测试函数的名称，即``tests::it_works``，而该测试的运行结果为``ok``。整体测试结果如下：`test_result: ok.` means that all the tests passed, and the portion that reads `1 passed; 0 failed`，其中“1 passed”表示通过的测试数量，“0 failed”表示失败的测试数量。

可以将某个测试标记为忽略，这样在特定的情况下就不会执行该测试；我们将在本章后面的[“除非特别请求，否则忽略测试”][ignoring]<!-- ignore -->部分中详细介绍这一点。由于我们在这里没有进行这样的操作，因此摘要中显示的是`0 ignored`。我们还可以在`cargo test`命令中传递一个参数，以仅运行名称符合特定字符串的测试；这被称为_过滤_，我们将在[“运行测试”]部分中详细讨论这一点。“按名称划分的测试子集”[subset]<!-- 忽略 --> 部分。在这里，我们没有过滤正在运行的测试，因此摘要的末尾显示的是`0 filtered out`。

`0 measured`这个统计指标用于衡量性能的基准测试。  
截至本文撰写时，这种基准测试仅在Rust的夜间版本中可用。如需了解更多信息，请参阅[关于基准测试的相关文档][bench]。

接下来测试输出的部分从`Doc-tests adder`开始，用于记录任何文档测试的结果。目前我们还没有进行任何文档测试，但Rust可以编译我们API文档中出现的任何代码示例。这个功能有助于保持你的文档和代码的一致性！我们将在第十四章的[“将文档注释作为测试”][doc-comments]<!-- ignore -->部分讨论如何编写文档测试。目前，我们忽略`Doc-tests`的输出内容。

让我们开始根据我们的需求自定义测试。首先，将`it_works`函数的名称改为其他名称，例如`exploration`，如下所示：

<span class="filename">文件名：src/lib.rs</span>

```rust,noplayground
{{#rustdoc_include ../listings/ch11-writing-automated-tests/no-listing-01-changing-test-name/src/lib.rs}}
```

然后，再次运行`cargo test`。现在输出的结果是`exploration`，而不是`it_works`：

```console
{{#include ../listings/ch11-writing-automated-tests/no-listing-01-changing-test-name/output.txt}}
```

现在，我们将添加另一个测试，但这次我们会编写一个会失败的测试！当测试函数中的某部分出现异常时，测试就会失败。每个测试都在一个新的线程中运行，当主线程发现某个测试线程已经终止时，该测试就会被标记为失败。在第九章中，我们讨论了最简单的方式来引发异常，那就是调用`panic!`宏。将新的测试作为一个名为`another`的函数来编写，这样你的_src/lib.rs文件看起来就像清单11-3所示。

<列表编号="11-3" 文件名称="src/lib.rs" 标题="添加第二个测试，该测试会失败，因为我们调用了`panic!`宏">

```rust,panics,noplayground
{{#rustdoc_include ../listings/ch11-writing-automated-tests/listing-11-03/src/lib.rs}}
```

</清单>

使用 `cargo test` 再次运行测试。输出结果应该类似于 Listing 11-4，这表明我们的 `exploration` 测试通过了，而 `another` 测试失败了。

<列表编号="11-4" 标题="当一个测试通过，另一个测试失败时的结果">

```console
{{#include ../listings/ch11-writing-automated-tests/listing-11-03/output.txt}}
```

</清单>

<!-- 手动重新生成
rg 恐慌列表/ch11-writing-automated-tests/listing-11-03/output.txt
检查恐慌出现的行数与下一段中的行数是否一致
-->

与`ok`不同，`test tests::another`这一行显示的是`FAILED`。在各个测试结果和总结之间出现了两个新的部分：第一个部分详细说明了每次测试失败的原因。在这个例子中，我们了解到`tests::another`之所以失败，是因为它在_src/lib.rs文件的第17行触发了“使此测试失败”的错误信息。下一个部分则列出了所有失败的测试的名称，当有很多测试失败时，这一点非常有用。包含大量的测试以及详细的失败测试结果。我们可以使用失败的测试名称来单独运行该测试，以便更轻松地进行调试；我们将在“控制测试执行方式”部分详细讨论如何运行测试。

总结行显示在最后：总体而言，我们的测试结果为`FAILED`。我们有一项测试通过，一项测试失败。

现在你已经了解了在不同场景下测试结果的样子，
接下来让我们看看除了`panic!`之外，在测试中还有哪些有用的宏。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="检查结果使用断言宏"></a>

### 使用 `assert!`检查结果

标准库提供的`assert!`宏在需要确保某个测试中的条件结果为`true`时非常有用。我们将`assert!`宏与一个布尔值作为参数。如果该值为`true`__，则不会发生任何事情，测试通过。如果该值为`false`__，则`assert!`宏会调用`panic!`以使测试失败。使用`assert!`宏帮助我们检查代码是否按照我们的预期正常运行。

在第五章的清单5-15中，我们使用了`Rectangle`结构体和`can_hold`方法，这些内容在清单11-5中也有重复。我们将这段代码放在src/lib.rs_文件中，然后使用`assert!`宏来编写一些测试。

<列表编号="11-5" 文件名称="src/lib.rs" 标题="第5章中的`Rectangle`结构体及其`can_hold`方法">

```rust,noplayground
{{#rustdoc_include ../listings/ch11-writing-automated-tests/listing-11-05/src/lib.rs}}
```

</清单>

`can_hold`方法返回一个布尔值，这意味着它是使用`assert!`宏的一个完美例子。在清单11-6中，我们编写了一个测试，通过创建一个宽度为8、高度为7的`Rectangle`实例来测试`can_hold`方法，并验证该实例是否能够容纳另一个宽度为5、高度为1的`Rectangle`实例。

<列表编号="11-6" 文件名称="src/lib.rs" 标题="对`can_hold`的测试，用于检查是否较大的矩形确实能够容纳较小的矩形">

```rust,noplayground
{{#rustdoc_include ../listings/ch11-writing-automated-tests/listing-11-06/src/lib.rs:here}}
```

</清单>

请注意 `tests` 模块内的 `use super::*;` 行。`tests` 也是一个普通的模块，其可见性规则遵循我们在第7章的[“在模块树中引用项目的路径”][paths-for-referring-to-an-item-in-the-module-tree]<!-- ignore -->章节中所介绍的规则。由于 `tests` 是一个内部模块，我们需要将外部模块中的代码带入内部模块的作用域中。我们使用在这里，它是一个全局变量，因此我们在外部模块中定义的所有内容都可以在这个`tests`模块中使用。

我们已经为我们的测试命名为`larger_can_hold_smaller`，并且已经创建了两个`Rectangle`实例。然后，我们调用了`assert!`宏，并将调用`larger.can_hold(&smaller)`的结果传递给了它。这个表达式应该返回`true`，所以我们的测试应该能够通过。让我们来验证一下吧！

```console
{{#include ../listings/ch11-writing-automated-tests/listing-11-06/output.txt}}
```

它确实通过了！让我们再添加一个测试，这次来验证较小的矩形无法容纳较大的矩形：

<span class="filename">文件名：src/lib.rs</span>

```rust,noplayground
{{#rustdoc_include ../listings/ch11-writing-automated-tests/no-listing-02-adding-another-rectangle-test/src/lib.rs:here}}
```

因为在这种情况下，``can_hold``函数的正确结果是``false``，所以在将其传递给``assert!``宏之前，我们需要取该结果的相反数。因此，如果``can_hold``返回``false``，那么我们的测试就会通过。

```console
{{#include ../listings/ch11-writing-automated-tests/no-listing-02-adding-another-rectangle-test/output.txt}}
```

两个测试都通过了！现在让我们看看，当我们在代码中引入一个错误时，测试结果会发生什么变化。我们将修改`can_hold`方法的实现，将用于比较宽度的大于号(`>`)替换为小于号(`<`)

```rust,not_desired_behavior,noplayground
{{#rustdoc_include ../listings/ch11-writing-automated-tests/no-listing-03-introducing-a-bug/src/lib.rs:here}}
```

现在运行测试后，得到以下结果：

```console
{{#include ../listings/ch11-writing-automated-tests/no-listing-03-introducing-a-bug/output.txt}}
```

我们的测试发现了问题！因为`larger.width`等于`8`，而`smaller.width`等于`5`，所以在`can_hold`中对宽度的比较现在返回的是`false`：8并不小于5。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="使用assert_eq和assertneq进行相等性测试">使用assert_eq和assertneq进行相等性测试</a>

### 使用`assert_eq!`和`assert_ne!`进行等价性测试

验证功能的一种常见方法是测试代码运行结果与你期望的代码返回值是否相等。你可以使用`assert!`宏，并通过`==`运算符传递一个表达式来实现这一点。不过，这种测试方法已经非常常见了，因此标准库提供了`assert_eq!`和`assert_ne!`这两个宏，以便更方便地执行此类测试。这些宏可以比较两个参数的相等性。它们还会在断言失败的情况下打印这两个值，这样就能更容易地了解测试为何失败；相反，``assert!``宏只是表明 ``==``表达式得到了``false``的值，而不会打印出导致``false``值的那些具体数值。

在清单11-7中，我们编写了一个名为`add_two`的函数，该函数将其参数中添加`2`，然后我们使用`assert_eq!`宏来测试这个函数。

<列表编号="11-7" 文件名称="src/lib.rs" 标题="使用`assert_eq!`宏测试函数`add_two`">

```rust,noplayground
{{#rustdoc_include ../listings/ch11-writing-automated-tests/listing-11-07/src/lib.rs}}
```

</清单>

让我们检查一下是否通过！

```console
{{#include ../listings/ch11-writing-automated-tests/listing-11-07/output.txt}}
```

我们创建了一个名为 ``result`` 的变量，用于存储调用 ``add_two(2)`` 的结果。然后，我们将 ``result`` 和 ``4`` 作为参数传递给 ``assert_eq!`` 宏。这个测试的输出行是 `test tests::it_adds_two... ok`, and the `ok`，这表明我们的测试通过了！

让我们在代码中引入一个错误，看看当`assert_eq!`出现问题时会是什么样子。将`add_two`函数的实现修改为添加`3`。

```rust,not_desired_behavior,noplayground
{{#rustdoc_include ../listings/ch11-writing-automated-tests/no-listing-04-bug-in-add-two/src/lib.rs:here}}
```

再次运行测试：

```console
{{#include ../listings/ch11-writing-automated-tests/no-listing-04-bug-in-add-two/output.txt}}
```

我们的测试发现了问题！`tests::it_adds_two`测试失败了，消息告诉我们，导致失败的断言是`left == right`，而`left`和`right`的值是多少。这条消息帮助我们开始调试：`left`参数，即调用`add_two(2)`的结果，应该是`5`，但是`right`参数却是`4`。你可以想象，这一点会非常有帮助。当我们进行大量测试时。

请注意，在某些语言和测试框架中，用于相等性断言函数的参数被称为`expected`和`actual`，并且指定参数的顺序非常重要。然而，在Rust中，这些参数的名称分别为`left`和`right`，因此，指定预期值的顺序与代码生成的值的顺序无关。我们可以这样编写这个测试中的断言：`assert_eq!(4, result)`会导致与``相同的错误信息，显示`left == right`失败，``也出现了问题。

如果传递给`assert_ne!`宏的两个值不相等，那么该宏会成功执行；如果这两个值相等，则宏会失败。这个宏在以下情况下非常有用：当我们不确定某个值的实际取值时，但知道该值肯定不会是某种特定的取值。例如，如果我们正在测试一个函数，该函数肯定会以某种方式改变其输入参数，而输入参数的变化方式则取决于我们进行测试的那一天属于一周中的哪一天，那么最好的断言方式可能是……该函数的输出不等于输入。

在表面之下，``assert_eq!``和``assert_ne!``宏分别使用了``==``和``!=``操作符。当断言失败时，这些宏会使用调试格式打印其参数，这意味着被比较的值必须具备``PartialEq``和``Debug``特性。所有基本类型以及标准库中的大多数类型都具备这些特性。对于结构体枚举类型来说……你需要自己定义自己，因此需要实现`PartialEq`来断言这些类型之间的相等性。同时，还需要实现`Debug`以便在断言失败时打印出这些值。由于这两个特性都是可派生的特性，正如第5章中的清单5-12所提到的，通常只需在结构体或枚举的定义中添加`#[derive(PartialEq, Debug)]`注解即可。更多详细信息请参阅附录C中的[“可派生特性”，][derivable-traits]<!-- ignore -->。关于这些以及其他可推导出的特征的详细信息。

### 添加自定义失败信息

您还可以向`assert!`、`assert_eq!`和`assert_ne!`宏添加自定义消息作为可选参数。在必需参数之后指定的任何参数都会被传递给`format!`宏（详见第8章中的“与`+`或`format!`结合使用”），因此您可以传递包含`{}`的格式字符串。占位符以及需要填入这些占位符的值。自定义消息对于记录断言的含义非常有用；当测试失败时，你可以更清楚地了解代码中存在的问题。

例如，假设我们有一个函数，该函数会根据名字来问候人们，我们希望测试传递给该函数的名字是否出现在输出中。

<span class="filename">文件名：src/lib.rs</span>

```rust,noplayground
{{#rustdoc_include ../listings/ch11-writing-automated-tests/no-listing-05-greeter/src/lib.rs}}
```

该程序的各项要求尚未确定，我们非常确定问候语开头的`Hello`文本将会发生变化。我们决定在需求变更时不必更新测试代码，因此，我们不会检查`greeting`函数返回的值是否完全相等，而是只需确保输出中包含输入参数中的文本即可。

现在，让我们通过修改代码中的`greeting`来引入一个错误，同时让`name`被排除在外，以此来观察默认的测试失败情况是什么样子：

```rust,not_desired_behavior,noplayground
{{#rustdoc_include ../listings/ch11-writing-automated-tests/no-listing-06-greeter-with-bug/src/lib.rs:here}}
```

运行此测试后得到的结果如下：

```console
{{#include ../listings/ch11-writing-automated-tests/no-listing-06-greeter-with-bug/output.txt}}
```

这个结果仅仅表明断言失败了，以及断言所在的行数。一个更实用的失败信息应该会打印出来自`greeting`函数的值。让我们添加一个自定义的失败信息，该信息包含一个格式字符串，其中的占位符会被我们从`greeting`函数中获取的实际值所填充。

```rust,ignore
{{#rustdoc_include ../listings/ch11-writing-automated-tests/no-listing-07-custom-failure-message/src/lib.rs:here}}
```

现在，当我们运行测试时，会得到一个更详细的错误信息：

```console
{{#include ../listings/ch11-writing-automated-tests/no-listing-07-custom-failure-message/output.txt}}
```

我们可以查看测试输出中实际得到的值，这有助于我们诊断实际情况与预期情况之间的差异。

### 使用`should_panic`检查是否发生恐慌

除了检查返回值之外，我们还需要确保我们的代码能够按照预期处理错误情况。例如，考虑我们在第9章的Listing 9-13中创建的`Guess`类型。其他使用`Guess`的代码依赖于这样一个前提：`Guess`实例中的值只会介于1到100之间。我们可以编写一个测试，以确保尝试创建超出该范围值的`Guess`实例会导致程序崩溃。

我们通过在测试函数中添加属性 ``should_panic``来实现这一点。如果函数内的代码引发异常，则测试通过；如果函数内的代码没有引发异常，则测试失败。

清单11-8展示了一个测试，用于验证在预期情况下，``Guess::new``是否会出现错误条件。

<列表编号="11-8" 文件名称="src/lib.rs" 标题="测试某个条件是否会引发`panic!`">

```rust,noplayground
{{#rustdoc_include ../listings/ch11-writing-automated-tests/listing-11-08/src/lib.rs}}
```

</清单>

我们将 ``#[should_panic]`` 属性放置在 ``#[test]`` 属性之后，并且位于该属性所应用的测试函数之前。让我们看看当这个测试通过时的结果：

```console
{{#include ../listings/ch11-writing-automated-tests/listing-11-08/output.txt}}
```

看起来不错！现在让我们在代码中引入一个错误，通过移除以下条件来修改代码：如果`new`函数的值大于100，那么这个函数将会引发异常。

```rust,not_desired_behavior,noplayground
{{#rustdoc_include ../listings/ch11-writing-automated-tests/no-listing-08-guess-with-bug/src/lib.rs:here}}
```

当我们运行清单11-8中的测试时，它会失败：

```console
{{#include ../listings/ch11-writing-automated-tests/no-listing-08-guess-with-bug/output.txt}}
```

在这种情况下，我们没有得到非常有用的信息，但是当我们查看测试函数时，发现它被标注了`#[should_panic]`。我们遇到的错误意味着测试函数中的代码并没有引发恐慌。

使用`should_panic`的测试可能不够精确。而使用`should_panic`的测试即使在因其他原因导致测试崩溃的情况下也能通过。为了使`should_panic`的测试更加精确，我们可以在`should_panic`属性中添加可选的`expected`参数。测试框架会确保失败消息中包含所提供的文本。例如：请考虑清单11-9中修改后的``Guess``代码。在該代码中，``new``函數会根据数值是太小还是太大而输出不同的错误信息。

<列表编号="11-9" 文件名称="src/lib.rs" 标题="测试包含指定子字符串的恐慌消息的`panic!`">

```rust,noplayground
{{#rustdoc_include ../listings/ch11-writing-automated-tests/listing-11-09/src/lib.rs:here}}
```

</清单>

这个测试会通过，因为我们把值放入 ``should_panic`` 属性的 ``expected`` 参数中，而这个值是 ``Guess::new`` 函数所引发的异常消息的一个子字符串。我们本可以指定整个预期的异常消息，在这种情况下，就是 `Guess value must be less than or equal to 100, got 200`。您选择具体指定什么内容，取决于异常消息中有多少部分是固定的，或者有多少部分是动态变化的，以及您希望测试有多精确。只要 Panic 消息中的某个子字符串，就足以确保 test 函数中的代码执行 `else if value > 100` 这个情况。

为了看看当带有`expected`消息的`should_panic`测试失败时会发生什么，让我们再次在代码中引入一个错误，方法是交换`if value < 1`和`else if value > 100`块的主体。

```rust,ignore,not_desired_behavior
{{#rustdoc_include ../listings/ch11-writing-automated-tests/no-listing-09-guess-with-panic-msg-bug/src/lib.rs:here}}
```

这次当我们运行`should_panic`测试时，它会失败：

```console
{{#include ../listings/ch11-writing-automated-tests/no-listing-09-guess-with-panic-msg-bug/output.txt}}
```

故障信息表明，正如我们所预期的那样，这个测试确实出现了恐慌现象。不过，恐慌信息中并没有包含预期中的字符串“less than or equal to 100`. The panic message that we did get in this case was `Guess value must be greater than or equal to 1, got 200”。现在我们可以开始找出我们的错误出在哪里了！

### 在测试中使用`Result<T, E>`

到目前为止，我们的所有测试在失败时都会引发恐慌。我们还可以编写使用 ``Result<T, E>`` 的测试！以下是清单 11-1 中的测试，重新编写后使用了 `Result<T, E>` and return an `Err` 而不是引发恐慌：

```rust,noplayground
{{#rustdoc_include ../listings/ch11-writing-automated-tests/no-listing-10-result-in-tests/src/lib.rs:here}}
```

现在，``it_works`` 函数的返回类型变为 ``Result<(), String>``。在函数的主体中，当测试通过时，我们返回 ``Ok(())``；而当测试失败时，则返回一个包含 ``String`` 的 ``Err``。

编写测试时，让它们返回 ``Result<T, E>``，这样你就可以在测试体内使用问号运算符。这是一种方便的方法，可以用来编写那些在测试过程中如果任何操作返回 ``Err`` 的变体时应该会失败的测试。

在使用了`Result<T, E>`. To assert that an operation returns an `Err`变体的测试中，不能使用`#[should_panic]`注释。在`Result<T, E>`值上也不要使用问号运算符，而是应该使用`assert!(value.is_err())`。

现在你已经了解了几种编写测试的方法，让我们来看看当我们运行测试时会发生什么，以及可以使用`cargo test`的哪些不同选项。

[连接操作]: ch08-02-strings.html#concatenating-with--or-format[测试环境]:../unstable-book/library-features/test.html[忽略操作]: ch11-02-running-tests.html#ignoring-tests-unless-specifically-requested[子集测试]: ch11-02-running-tests.html#running-a-subset-of-tests-by-name[控制测试执行方式]: ch11-02-running-tests.html#controlling-how-tests-are-run[可推导特性]: appendix-03-derivable-traits.html[文档评论]: ch14-02-publishing-to-crates-io.html#documentation-comments-as-tests[模块树中用于引用项目的路径]: ch07-03-paths-for-referring-to-an-item-in-the-module-tree.html