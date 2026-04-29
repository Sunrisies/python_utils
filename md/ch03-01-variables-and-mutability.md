## 变量与可变性

如["使用变量存储值"](ch02-00-guessing-game-tutorial.html#storing-values-with-variables)节所述，默认情况下，变量是不可变的。这是Rust提供的一种机制，旨在帮助你以充分利用其安全性和便捷并发性的方式编写代码。不过，你仍然可以选择使变量变为可变的。接下来，我们将探讨为什么Rust鼓励你采用不可变性，以及为什么有时你可能希望放弃这种特性。

当一个变量是不可变的时，一旦某个值被绑定到一个名称上，就无法再更改该值。为了说明这一点，请使用`cargo new variables`在你的_projects目录下创建一个名为_variables_的新项目。

然后，在你的新的`_variables_`目录下，打开`_src/main.rs`文件，并用以下代码替换其中的代码。不过，目前这段代码还无法编译。

<span class="filename">文件名：src/main.rs</span>

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch03-common-programming-concepts/no-listing-01-variables-are-immutable/src/main.rs}}
```

使用`cargo run`保存并运行程序。你应该会收到一个关于不可变性错误的错误消息，如此输出所示：

```console
{{#include ../listings/ch03-common-programming-concepts/no-listing-01-variables-are-immutable/output.txt}}
```

这个例子展示了编译器如何帮助您发现程序中的错误。  
编译器错误可能会让人感到沮丧，但实际上，它们只是意味着您的程序还没有能够安全地完成您期望它做的事情；这并不意味着您不是一个优秀的程序员！经验丰富的Rust开发者仍然会遇到编译器错误。

您收到了错误信息：``不能将值赋给不可变变量`x` ``，因为您试图将第二个值赋给不可变的`x`变量。

当我们尝试更改被指定为不可变的值时，必须避免编译时错误，因为这种情况可能导致错误。如果代码的一部分假设某个值永远不会改变，而另一部分代码改变了该值，那么代码的第一部分可能无法实现它设计时的效果。这种 bug 的原因在事后很难追溯，尤其是当第二段代码改变了值时。

但是，可变性非常有用，可以让代码更易于编写。虽然默认情况下变量是不可变的，但你可以通过在变量名称前添加`mut`来使其变为可变状态，就像在[第2章][使用变量存储值]中所做的那样。同时添加`mut`还可以向代码的未来读者传达意图，表明代码的其他部分将会改变这个变量的值。

例如，让我们将`_src/main.rs_`改为如下内容：

<span class="filename">文件名：src/main.rs</span>

```rust
{{#rustdoc_include ../listings/ch03-common-programming-concepts/no-listing-02-adding-mut/src/main.rs}}
```

现在当我们运行这个程序时，我们得到这样的结果：

```console
{{#include ../listings/ch03-common-programming-concepts/no-listing-02-adding-mut/output.txt}}
```

当使用`mut`时，我们被允许将绑定到`x`的值从`5`更改为`6`。最终，是否使用可变性取决于你的判断，以及你认为在特定情况下哪种方式更为清晰。

<!-- 旧的标题。不要删除，否则链接可能会失效。 -->
<a id="constants"></a>

### 声明常量

与不可变变量类似，常量也是绑定到一个名称的值，并且不允许改变。不过，常量和变量之间还是有一些区别的。

首先，不允许在常量中使用`mut`。常量默认是不可变的——它们始终都是不可变的。你应该使用`const`关键字来声明常量，而不是`let`关键字。此外，常量的值类型必须被注释说明。关于类型和类型注释的详细信息，我们将在下一节中讨论，即[“数据类型”][data-types]<!-- ignore -->，所以现在不必担心这些细节。只需记住，你必须始终对类型进行注释说明即可。

常量可以在任何作用域中声明，包括全局作用域，这使得它们对于代码中的多个部分都需要知道的值非常有用。

最后一个区别在于，常量只能被设置为一个常量表达式，而不能是只能在运行时计算得到的值的结果。

以下是一个常量声明的例子：

```rust
const THREE_HOURS_IN_SECONDS: u32 = 60 * 60 * 3;
```

这个常量的名称是 ``THREE_HOURS_IN_SECONDS``，其值是通过将60（一分钟的秒数）乘以60（一小时中的分钟数）再乘以3（我们在这个程序中想要计算的小时数）得到的结果。Rust中常量的命名规范是使用全大写字母，并且单词之间使用下划线来分隔。编译器能够在编译时评估有限的一组操作，这使我们能够自行编写出这个表达式的值。采用更易于理解和验证的方式，而不是将这个常量设置为10800。有关在声明常量时可以使用哪些操作的更多信息，请参阅[Rust参考手册中关于常量评估的部分][const-eval]。

常量在整个程序运行期间都是有效的，且仅在它们被声明的作用域内有效。这一特性使得常量适用于应用程序领域中那些可能被程序的多个部分需要知道的值，例如游戏中玩家允许获得的最大分数，或者光速等数值。

在程序中将硬编码的值命名为常量，有助于向未来的维护人员传达该值的含义。此外，这样做还可以确保代码中只有一个需要修改的地方，从而避免在将来需要更新硬编码值时进行多次修改。

### 影子行为

正如你在[第2章][比较猜测与秘密数字]中的猜谜游戏教程中看到的那样，你可以重新声明一个具有相同名称的变量。Rustaceans称第一个变量被第二个变量“遮蔽”，这意味着当你使用该变量的名称时，编译器会看到的是第二个变量。实际上，第二个变量会覆盖第一个变量，从而占据所有对该变量的使用机会。变量名称会一直指向自身，直到该变量被遮蔽或者作用域结束。我们可以通过使用相同的变量名称，并重复使用`let`关键字来遮蔽一个变量，如下所示：

<span class="filename">文件名：src/main.rs</span>

```rust
{{#rustdoc_include ../listings/ch03-common-programming-concepts/no-listing-03-shadowing/src/main.rs}}
```

该程序首先将`x`绑定到`5`的值。然后，通过重复`let x =`来创建一个新的变量`x`，将原始值加上`1`，使得`x`的值变为`6`。接着，在由大括号创建的内部作用域内，第三个`let`语句也会覆盖`x`，并创建一个新的变量。变量将前一个值乘以`2`，从而让`x`获得`12`的值。当这个作用域结束时，内部遮蔽就终止了，而`x`又恢复为`6`。当我们运行这个程序时，它会输出以下内容：

```console
{{#include ../listings/ch03-common-programming-concepts/no-listing-03-shadowing/output.txt}}
```

影子操作与将变量标记为`mut`是不同的，因为如果我们不小心尝试重新赋值给这个变量，而不使用`let`关键字，将会引发编译时错误。通过使用`let`，我们可以对值进行一些转换，但在这些转换完成后，该变量仍然是不可变的。

`mut`与影子作用的其他区别在于，当我们再次使用`let`关键字时，实际上会创建一个新的变量，因此我们可以改变值的类型，但可以使用相同的名称。例如，假设我们的程序要求用户输入某个文本之间所需的空格数，然后我们希望将这些输入存储为一个数字。

```rust
{{#rustdoc_include ../listings/ch03-common-programming-concepts/no-listing-04-shadowing-can-change-types/src/main.rs:here}}
```

第一个变量`spaces`是字符串类型，而第二个变量`spaces`是数字类型。通过影子作用域，我们不必为变量起不同的名称，比如`spaces_str`和`spaces_num`；相反，我们可以使用更简单的名称`spaces`。然而，如果我们尝试像这里那样使用`mut`，将会出现编译时错误。

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch03-common-programming-concepts/no-listing-05-mut-cant-change-types/src/main.rs:here}}
```

错误信息显示我们不允许修改变量的类型。

```console
{{#include ../listings/ch03-common-programming-concepts/no-listing-05-mut-cant-change-types/output.txt}}
```

现在我们已经了解了变量是如何工作的，接下来让我们看看它们还可以拥有哪些数据类型。

[将猜测结果与正确答案进行比较]: ch02-00-guessing-game-tutorial.html#comparing-the-guess-to-the-secret-number
[数据类型]: ch03-02-data-types.html#data-types
[使用变量存储值]: ch02-00-guessing-game-tutorial.html#storing-values-with-variables
[常量与eval]:../reference/const_eval.html