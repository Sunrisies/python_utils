## 控制流

能够根据条件是否为``true``来运行某些代码，以及在条件为``true``时重复运行某些代码的能力，是大多数编程语言的基本构建块。在Rust代码中，能够控制执行流程的最常见结构就是``if``表达式和循环。

### `if` 表达式

一个 ``if`` 表达式允许您根据条件来分支代码。您需要提供一个条件，然后声明：“如果这个条件满足，就运行这个代码块。如果不满足条件，则不要运行这个代码块。”

在你的`_projects_`目录下创建一个名为`_branches_`的新项目，以探索`if`表达式。在`_src/main.rs_`文件中，输入以下内容：

<span class="filename">文件名：src/main.rs</span>

```rust
{{#rustdoc_include ../listings/ch03-common-programming-concepts/no-listing-26-if-true/src/main.rs}}
```

所有 `if` 表达式都以关键字 `if` 开头，随后是一个条件判断。在这种情况下，该条件用于检查变量 `number` 的值是否小于 5。如果条件满足，就会执行 `true` 中的代码块。在条件判断之后，我们会立即将需要执行的代码块放在大括号内。在 `if` 表达式中，与条件判断相关的代码块有时被称为 _臂_，就像我们在第 2 章的[“比较猜测数字与秘密数字”][comparing-the-guess-to-the-secret-number]<!-- 忽略 --> 部分讨论过的 `match` 表达式中的“臂”一样。

此外，我们还可以包含一个`else`表达式，我们选择在这里使用这个表达，以便在条件评估结果为`false`时，程序可以执行另一段代码。如果您不提供`else`表达式，而条件是`false`，那么程序将直接跳过`if`块，继续执行下一段代码。

请尝试运行这段代码；你应该会看到如下输出：

```console
{{#include ../listings/ch03-common-programming-concepts/no-listing-26-if-true/output.txt}}
```

让我们尝试将 `number` 的值改为一个能使条件 `false` 成立的值，看看会发生什么：

```rust,ignore
{{#rustdoc_include ../listings/ch03-common-programming-concepts/no-listing-27-if-false/src/main.rs:here}}
```

再次运行程序，然后查看输出结果：

```console
{{#include ../listings/ch03-common-programming-concepts/no-listing-27-if-false/output.txt}}
```

同样值得注意的是，这段代码中的条件必须是一个__INLINE_CODE__42__。如果条件不是__INLINE_CODE__42__，我们就会遇到错误。例如，尝试运行以下代码：

<span class="filename">文件名：src/main.rs</span>

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch03-common-programming-concepts/no-listing-28-if-condition-must-be-bool/src/main.rs}}
```

这次，`if`条件的值为`3`，Rust抛出了一个错误：

```console
{{#include ../listings/ch03-common-programming-concepts/no-listing-28-if-condition-must-be-bool/output.txt}}
```

该错误表明Rust期望的是`bool`的值，但实际上得到了整数。与Ruby和JavaScript等语言不同，Rust不会自动将非布尔类型转换为布尔类型。我们必须明确指定，并且始终将`if`的返回值设置为布尔类型。例如，如果我们希望`if`代码块仅在数字不等于`0`时运行，我们可以将`if`表达式修改为如下形式：

<span class="filename">文件名：src/main.rs</span>

```rust
{{#rustdoc_include ../listings/ch03-common-programming-concepts/no-listing-29-if-not-equal-0/src/main.rs}}
```

运行这段代码将会打印出`number was something other than zero`。

#### 使用 `else if`处理多个条件

您可以通过在`else if`表达式中结合使用`if`和`else`来实现多个条件的组合。例如：

<span class="filename">文件名：src/main.rs</span>

```rust
{{#rustdoc_include ../listings/ch03-common-programming-concepts/no-listing-30-else-if/src/main.rs}}
```

这个程序有四种可能的执行路径。运行之后，你应该会看到如下输出：

```console
{{#include ../listings/ch03-common-programming-concepts/no-listing-30-else-if/output.txt}}
```

当这个程序执行时，它会依次检查每个`if`表达式，并执行第一个满足条件`true`的主体。需要注意的是，尽管6可以被2整除，但我们并没有看到输出`number is divisible by 2`，也没有看到来自`else`块的`number is not divisible by 4, 3, or 2`文本。这是因为Rust只会执行第一个满足条件的`true`块，一旦找到满足条件的条件，它就不会再检查其余的条件了。

使用过多的 ``else if`` 表达式会使代码变得混乱，因此如果你使用了多个这样的表达式，可能需要对代码进行重构。第6章介绍了一种强大的Rust分支构造方法，称为 ``match``，适用于这种情况。

#### 在 ``let`` 语句中使用 ``if``

因为 ``if`` 是一个表达式，我们可以在 ``let`` 语句的右侧使用它，将结果赋值给一个变量，如清单3-2所示。

<列表编号="3-2" 文件名称="src/main.rs" 标题="将 `if` 表达式的结果赋值给变量">

```rust
{{#rustdoc_include ../listings/ch03-common-programming-concepts/listing-03-02/src/main.rs}}
```

</ Listing>

变量`number`将根据`if`表达式的结果被绑定到一个值。运行这段代码来看看会发生什么：

```console
{{#include ../listings/ch03-common-programming-concepts/listing-03-02/output.txt}}
```

请记住，代码块的最终计算结果取决于其中最后一个表达式的值，而数字本身也是一种表达式。在这种情况下，整个`if`表达式的值取决于哪个代码块被执行。这意味着，`if`的每个分支可能产生的结果必须具有相同的类型。在清单3-2中，`if`和`else`分支的结果都是`i32`类型的整数。如果类型不匹配，就像下面的例子一样，就会出错：

<span class="filename">文件名：src/main.rs</span>

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch03-common-programming-concepts/no-listing-31-arms-must-return-same-type/src/main.rs}}
```

当我们尝试编译这段代码时，会遇到一个错误。`if`和`else`这两个变数包含的是不相容的值类型，Rust会明确指出问题所在的位置：

```console
{{#include ../listings/ch03-common-programming-concepts/no-listing-31-arms-must-return-same-type/output.txt}}
```

在 ``if`` 块中的表达式的值为整数，而在 ``else`` 块中的表达式的值为字符串。这样的做法是不行的，因为变量必须具有单一类型，而Rust需要在编译时明确知道 ``number`` 变量的类型。了解 ``number`` 的类型可以让编译器验证该类型在我们使用 ``number`` 的所有地方都是有效的。如果 ``number`` 的类型只在运行时才确定，Rust就无法实现这一点；在这种情况下，编译器的复杂性会增加，而且对于代码的可靠性也会降低，因为它需要跟踪任意变量的多种可能类型。

### 循环中的重复操作

多次执行一段代码通常是非常有用的。为此，Rust提供了多种循环结构，这些结构会依次执行循环体内的代码，直到最后，然后再立即从开始处重新开始。为了尝试使用循环结构，让我们创建一个新的项目，命名为“loops”。

Rust中有三种循环方式：`loop`、`while`和`for`。让我们分别尝试每一种。

#### 使用 `loop`重复代码

``loop``这个关键字告诉Rust重复执行一段代码，可以永远执行下去，或者直到你明确指示它停止为止。

例如，将你的 `_loops_`目录中的`_src/main.rs_`文件改为如下格式：

<span class="filename">文件名：src/main.rs</span>

```rust,ignore
{{#rustdoc_include ../listings/ch03-common-programming-concepts/no-listing-32-loop/src/main.rs}}
```

当我们运行这个程序时，会看到`again!`不断被打印出来，直到我们手动停止程序。大多数终端都支持使用键盘快捷键<kbd>ctrl</kbd>-<kbd>C</kbd>来中断陷入无限循环的程序。不妨试试看：

<!-- 手动重新生成
cd listings/ch03-common-programming-concepts/no-listing-32-loop
cargo run
按 CTRL-C 退出
-->

```console
$ cargo run
   Compiling loops v0.1.0 (file:///projects/loops)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.08s
     Running `target/debug/loops`
again!
again!
again!
again!
^Cagain!
```

符号 `^C` 表示您按下 <kbd>ctrl</kbd>-<kbd>C</kbd> 的位置。

您可能会看到，也可能不会看到 "`^C`"之后打印着 "`again!`"这个词，这取决于代码在循环中接收到中断信号时的位置。

幸运的是，Rust还提供了一种通过代码来跳出循环的方法。你可以在循环内部放置 ``break`` 这个关键字，以此来告诉程序何时停止执行循环。回想一下，在第二章的“猜对后退出”部分，我们就是使用这种方法在用户猜对数字后退出程序的。

我们在猜谜游戏中还使用了 ``continue``。这个代码会在一个循环中告诉程序跳过本次循环中的剩余代码，直接进行下一次迭代。

#### 从循环中返回值

``loop``的一个用途是重试一个可能失败的操作，例如检查线程是否已经完成其任务。您可能还需要将该操作的结果从循环中传递出去，以便让其他代码能够使用它。为此，可以在使用的``break``表达式之后添加希望返回的值；该值将从循环中返回，从而可以被其他代码使用，如下所示：

```rust
{{#rustdoc_include ../listings/ch03-common-programming-concepts/no-listing-33-return-value-from-loop/src/main.rs}}
```

在循环之前，我们声明一个名为`counter`的变量，并将其初始化为`0`。然后，我们声明一个名为`result`的变量，用于存储循环返回的值。在循环的每次迭代中，我们将`1`添加到`counter`变量中，然后检查`counter`是否等于`10`。当它们相等时，我们使用`break`关键字，并将值设为`counter * 2`。在循环结束后，我们使用分号来结束将值赋给`result`的语句。最后，我们打印出位于`result`中的值，在这个案例中，该值为`20`。

您还可以从循环内部调用 `return`。虽然 `break` 只会退出当前的循环，但 `return` 则总是会退出当前函数。

<a id="使用循环标签来消除多个循环之间的歧义"></a>

#### 使用循环标签进行歧义消除

如果你在循环内部还有循环，那么`break`和`continue`将适用于最内层的循环。你可以选择性地为循环指定一个_循环标签_，然后可以使用`break`或`continue`来指定这些关键词适用于该带有标签的循环，而不是最内层的循环。循环标签必须以单引号开头。以下是一个包含两个嵌套循环的示例：

```rust
{{#rustdoc_include ../listings/ch03-common-programming-concepts/no-listing-32-5-loop-labels/src/main.rs}}
```

外部循环有一个标签为 ``'counting_up``，它的循环次数从0开始，一直到2。  
内部循环没有标签，它的循环次数是从10开始，一直到9。第一个没有指定标签的 ``break`` 只会退出内部循环。而 `break counting_up;` 语句则会使外部循环终止。这段代码会输出：

```console
{{#rustdoc_include ../listings/ch03-common-programming-concepts/no-listing-32-5-loop-labels/output.txt}}
```

<a id="条件循环与while循环"></a>

#### 使用 while 简化条件循环

程序通常需要在循环中评估某个条件。当这个条件满足时，循环会继续执行；当条件不再满足时，程序会调用某个特定的代码，从而终止循环。这种行为可以通过结合使用`loop`、`if`、`else`和`break`来实现。如果你愿意，现在就可以在程序中尝试这样做。不过，这种模式非常常见，Rust为此提供了一种内置的语言结构，称为`while`循环。在清单3-3中，我们使用`while`让程序循环三次，每次循环都进行倒计时，然后在循环结束后打印一条消息并退出程序。

<列表编号="3-3" 文件名称="src/main.rs" 标题="使用 `while` 循环在条件满足时执行代码 `true`">

```rust
{{#rustdoc_include ../listings/ch03-common-programming-concepts/listing-03-03/src/main.rs}}
```

</ Listing>

这种构造方式消除了使用 ``loop``, ``if``, ``else``, 和 ``break`` 时所需的许多嵌套结构，使得代码更加清晰。当条件评估结果为 ``true`` 时，代码会执行；否则，循环就会终止。

#### 使用 `for`遍历集合

您可以选择使用 ``while`` 结构来遍历集合中的元素，例如数组。例如，清单3-4中的循环会打印出数组 ``a`` 中的每个元素。

<Listing number="3-4" file-name="src/main.rs" caption="使用`while`循环遍历集合中的每个元素">

```rust
{{#rustdoc_include ../listings/ch03-common-programming-concepts/listing-03-04/src/main.rs}}
```

</ Listing>

在这里，代码会遍历数组中的元素。它从索引`0`开始，然后循环直到到达数组的最后一个索引（即当`index < 5`不再等于`true`时）。运行这段代码将会打印出数组中的每一个元素：

```console
{{#include ../listings/ch03-common-programming-concepts/listing-03-04/output.txt}}
```

正如预期的那样，五个数组值都出现在终端中。尽管`index`会在某个时刻达到`5`的值，但循环在尝试从数组中获取第六个值时会停止执行。

然而，这种方法容易出错；如果索引值或测试条件不正确，可能会导致程序崩溃。例如，如果你将`a`数组的定义改为包含四个元素，但却忘记更新`while index < 4`的条件，那么代码就会崩溃。此外，这种方法效率也很低，因为编译器会在每次循环时添加运行时代码来检查索引是否在数组的范围内。

作为一个更简洁的替代方案，你可以使用一个`for`循环来为集合中的每个项目执行一些代码。`for`循环的结构类似于清单3-5中的代码。

<Listing number="3-5" file-name="src/main.rs" caption="使用`for`循环遍历集合中的每个元素">

```rust
{{#rustdoc_include ../listings/ch03-common-programming-concepts/listing-03-05/src/main.rs}}
```

</ Listing>

当我们运行这段代码时，会看到与清单3-4中相同的输出。更重要的是，我们现在提高了代码的安全性，消除了因超出数组范围或未能访问到某些元素而可能导致错误的风险。由`for`循环生成的机器代码也会更加高效，因为每次迭代时都不需要比较索引与数组长度的关系。

通过使用 ``for`` 循环，如果你更改了数组中值的数量，就不需要记得修改其他代码，这与 Listing 3-4 中使用的那种方法相比更加方便。

`for`循环在安全性和简洁性方面表现优异，因此成为Rust中最常用的循环结构。即使是在需要重复执行某些代码的情况下，比如清单3-3中使用的倒计时示例中所用的`while`循环，大多数Rust开发者也会选择使用`for`循环。要实现这一点，可以使用标准库提供的`Range`循环结构，该结构能够按顺序生成所有数字，从数字1开始，并在某个数字之前结束。

如果使用一个`for`循环，以及另一种我们尚未讨论的方法——`rev`来反转该范围，那么倒计时将会呈现如下效果：

<span class="filename">文件名：src/main.rs</span>

```rust
{{#rustdoc_include ../listings/ch03-common-programming-concepts/no-listing-34-for-range/src/main.rs}}
```

这段代码看起来更简洁了，不是吗？

## 总结

你成功了！这一章的内容相当丰富：你学习了变量、标量及复合数据类型、函数、注释、``if``表达式以及循环！为了练习本章所讨论的概念，试着编写程序来实现以下任务：

- 将温度从华氏度转换为摄氏度。  
- 生成第*n*个斐波那契数。  
- 利用歌曲中的重复结构，打印出圣诞颂歌《十二天的圣诞节》的歌词。

当你准备继续前进时，我们将讨论一个在Rust中独有的概念——所有权。这个概念在其他编程语言中并不常见。

[将猜测结果与正确答案进行比较]: ch02-00-guessing-game-tutorial.html#comparing-the-guess-to-the-secret-number
[在猜对后退出游戏]: ch02-00-guessing-game-tutorial.html#quitting-after-a-correct-guess