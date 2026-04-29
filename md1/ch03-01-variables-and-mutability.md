## 变量与可变性

如[“使用变量存储值”][storing-values-with-variables]节所述，默认情况下，变量是不可变的。这是Rust提供的一种机制，旨在帮助你以充分利用其安全性和并发性的方式编写代码。不过，你仍然可以选择使变量变为可变的。接下来，我们将探讨为什么Rust鼓励你使用不可变性，以及为什么有时你可能希望选择使用可变变量。

当一个变量是不可变的时，一旦某个值被绑定到一个名称上，你就无法改变那个值。为了说明这一点，请使用`cargo new variables`在你的_projects目录下创建一个名为_variables_的新项目。

然后，在你的新的`_variables_`目录下，打开`_src/main.rs_`文件，并用以下代码替换其中的代码。不过，目前这段代码是无法编译的：

<span class="filename">文件名：src/main.rs</span>

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch03-common-programming-concepts/no-listing-01-variables-are-immutable/src/main.rs}}
```

使用`cargo run`保存并运行程序。你应该会收到一个关于不可变性错误的错误消息，如下所示：

```console
{{#include ../listings/ch03-common-programming-concepts/no-listing-01-variables-are-immutable/output.txt}}
```

这个例子展示了编译器如何帮助您发现程序中的错误。  
编译器错误可能会让人感到沮丧，但实际上，这些错误只是意味着您的程序还没有完全按照预期运行；它们并不意味着您不是一个优秀的程序员！经验丰富的Rust开发者仍然会遇到编译器错误。

您收到了错误信息：“``”无法将值赋给不可变变量“`x`”，因为您试图将第二个值赋给不可变的变量“`x`”。

当我们尝试修改被声明为不可变的值时，能够产生编译时错误是非常重要的，因为这种情况本身就可能导致错误。如果代码中的一部分假设某个值永远不会改变，而另一部分代码却改变了该值，那么第一部分代码可能无法按照预期执行。这种错误的根源在事后很难追踪，尤其是当第二部分代码只是偶尔改变该值时。Rust编译器保证，当你声明某个值不会改变时，它确实不会改变，因此你不必自己跟踪这个值。这样一来，你的代码就更容易理解了。

但是，可变性非常有用，可以让代码更易于编写。虽然变量默认是不可变的，但你可以通过在变量名称前添加`mut`来使其变为可变变量，就像在[第2章][使用变量存储值]中所做的那样。同时添加`mut`还可以向代码的未来读者传达意图，表明代码的其他部分将会改变这个变量的值。

例如，让我们将 `_src/main.rs_`改为如下内容：

<span class="filename">文件名：src/main.rs</span>

```rust
{{#rustdoc_include ../listings/ch03-common-programming-concepts/no-listing-02-adding-mut/src/main.rs}}
```

现在当我们运行这个程序时，会得到这样的结果：

```console
{{#include ../listings/ch03-common-programming-concepts/no-listing-02-adding-mut/output.txt}}
```

当使用`mut`时，我们被允许将绑定到`x`的值从`5`更改为`6`。是否使用可变性取决于你的判断，以及你认为在特定情况下哪种方式更为清晰。

<a id="constants"></a>

### 声明常量

与不可变变量类似，常量也是被绑定到一个名称的值，并且不允许进行更改。不过，常量和变量之间还是有一些区别的。

首先，不允许在常量中使用`mut`。常量默认是不可变的——它们始终都是不可变的。你应该使用`const`关键字来声明常量，而不是`let`关键字。此外，常量的值类型必须被标注出来。关于类型和类型标注的细节，我们将在下一节中讨论，即[“数据类型”][data-types]，所以现在不必担心这些细节。只需记住，你必须始终对类型进行标注即可。

常量可以在任何作用域中声明，包括全局作用域，这使得它们适用于那些需要被代码中的多个部分所知晓的值。

最后一个区别在于，常量只能被设置为常量表达式，而不能是只能在运行时计算的值的结果。

以下是一个常量声明的例子：

```rust
const THREE_HOURS_IN_SECONDS: u32 = 60 * 60 * 3;
```

这个常量的名称是 ``THREE_HOURS_IN_SECONDS``，其值是通过将60（一分钟中的秒数）乘以60（一小时中的分钟数）再乘以3（我们在这段程序中想要计算的小时数）得到的结果。Rust中常量的命名规范是使用全大写字母，并且单词之间使用下划线分隔。编译器能够在编译时执行有限的一组运算，这使我们能够以一种更易于理解和验证的方式来表示这个值，而不是将这个常量设置为10,800。有关在声明常量时可以使用的运算方式的更多信息，请参阅[Rust参考手册中关于常量评估的部分][const-eval]。

常量在整个程序运行期间都是有效的，它们仅在声明它们的作用域内有效。这一特性使得常量适用于应用程序领域中那些可能被程序的多个部分需要知道的值，例如游戏中玩家允许获得的最大分数，或者光速等。

在程序中将硬编码的值命名为常量，有助于向未来的维护者传达该值的含义。此外，这样做还可以确保代码中只有一个需要修改的地方，这样如果将来需要对硬编码的值进行更新，就可以轻松地进行修改。

### 遮蔽

正如你在[第2章][比较猜测与秘密数字]中的猜谜游戏教程中看到的那样，你可以声明一个与之前变量名称相同的新变量。Rustaceans称第一个变量被第二个变量“遮蔽”，这意味着当你使用变量名时，编译器会看到的是第二个变量。实际上，第二个变量会覆盖第一个变量，使得任何对变量名的引用都指向它自己，直到第二个变量也被遮蔽或者作用域结束。我们可以通过使用同一个变量名，并重复使用`let`关键字来遮蔽一个变量：

<span class="filename">文件名：src/main.rs</span>

```rust
{{#rustdoc_include ../listings/ch03-common-programming-concepts/no-listing-03-shadowing/src/main.rs}}
```

该程序首先将 ``x`` 绑定到 ``5`` 的值上。然后，通过重复执行 ``let x =``，创建一个新的变量__`INLINE_CODE_29__`，并将原始值加上__`INLINE_CODE_31__`，使得__`INLINE_CODE_32__`的值变为__`INLINE_CODE_33__`。接着，在由大括号定义的内部作用域内，第三个__`INLINE_CODE_34__`语句也会遮蔽__`INLINE_CODE_35__`，并创建一个新的变量，将之前的值乘以__`INLINE_CODE_36__`，从而使__`INLINE_CODE_37__`的值为__`INLINE_CODE_38__`。当该作用域结束时，内部遮蔽就结束了，__`INLINE_CODE_39__`又变回了__`INLINE_CODE_40__`。当我们运行这个程序时，它会输出以下内容：

```console
{{#include ../listings/ch03-common-programming-concepts/no-listing-03-shadowing/output.txt}}
```

影子作用与将变量标记为 ``mut`` 是不同的，因为如果我们不小心尝试重新赋值给这个变量，而不使用 ``let`` 关键字，将会引发编译时错误。通过使用 ``let``，我们可以对一个值进行一些转换操作，但在这些转换完成后，该变量仍然是不可变的。

`mut`与影子机制的另一个区别在于，当我们再次使用`let`关键字时，实际上会创建一个新的变量。因此，我们可以改变该变量的值的类型，但可以使用相同的名称。例如，假设我们的程序要求用户输入某个文本之间所需的空格数，然后我们希望将这个输入存储为一个数字。

```rust
{{#rustdoc_include ../listings/ch03-common-programming-concepts/no-listing-04-shadowing-can-change-types/src/main.rs:here}}
```

第一个变量`spaces`是字符串类型，而第二个变量`spaces`是数字类型。通过影子变量，我们不必使用不同的名称，比如`spaces_str`和`spaces_num`；相反，我们可以使用更简单的名称`spaces`。然而，如果我们尝试像这里那样使用`mut`，将会出现编译时错误：

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch03-common-programming-concepts/no-listing-05-mut-cant-change-types/src/main.rs:here}}
```

错误信息显示我们不允许修改变量的类型：

```console
{{#include ../listings/ch03-common-programming-concepts/no-listing-05-mut-cant-change-types/output.txt}}
```

既然我们已经了解了变量的工作原理，接下来让我们看看它们还可以拥有哪些数据类型。

[比较猜测与正确答案]: ch02-00-guessing-game-tutorial.html#comparing-the-guess-to-the-secret-number
[数据类型]: ch03-02-data-types.html#data-types
[使用变量存储值]: ch02-00-guessing-game-tutorial.html#storing-values-with-variables
[常量求值]:../reference/const_eval.html