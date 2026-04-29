## 数据类型

在Rust中，每个值都具有一定的_数据类型_，这个类型告诉Rust所指定的数据是什么类型，从而让Rust知道如何处理这些数据。我们将探讨两种数据类型：标量型和复合型。

请注意，Rust是一种_静态类型_的语言，这意味着在编译时必须知道所有变量的类型。编译器通常可以根据值和我们使用方式来推断我们想要使用的类型。在可能出现多种类型的情况下，例如在第2章的[“比较猜测与秘密数字”][comparing-the-guess-to-the-secret-number]部分中，当我们使用`parse`将一个`String`转换为数值类型时，我们必须添加类型注解，如下所示：

```rust
let guess: u32 = "42".parse().expect("Not a number!");
```

如果我们不在前面的代码中添加 ``: u32`` 这种类型注解，Rust将会显示以下错误，这意味着编译器需要我们从我们这里获得更多信息，以了解我们想要使用的类型是什么：

```console
{{#include ../listings/ch03-common-programming-concepts/output-only-01-no-type-annotations/output.txt}}
```

你会看到其他数据类型的不同的类型注解。

### 标量类型

**标量类型**表示单个值。Rust主要有四种标量类型：整数、浮点数、布尔值和字符。这些类型在其他编程语言中也很常见。现在让我们来看看它们在Rust中的实现方式。

#### 整数类型

整数是一种没有小数部分的数字。我们在第2章中使用了一种整数类型，即`u32`类型。这种类型声明表示与之关联的值应该是一个无符号整数（有符号整数类型的起始符号是`i`而不是`u`），并且它占用32位的空间。表3-1展示了Rust中的内置整数类型。我们可以使用这些类型中的任何一种来声明整数值的类型。

<span class="caption">表3-1：Rust中的整数类型</span>

| 长度 | 签名 | 无符号 |
| ------- | ------- | -------- |
| 8位 | `i8` | `u8` |
| 16位 | `i16` | `u16` |
| 32位 | `i32` | `u32` |
| 64位 | `i64` | `u64` |
| 128位 | `i128` | `u128` |
| 依赖于架构 | `isize` | `usize` |  
每个变体可以是有符号的或无符号的，并且具有明确的大小。  
“有符号”和“无符号”指的是该数字是否可能为负数——换句话说，该数字是否需要带有符号（有符号），还是只能是正数，因此无需显示符号（无符号）。这就像在纸上书写数字：当符号很重要时，数字会加上加号或减号来表示；而当可以假设数字一定是正数时，则不需要显示符号。  
有符号数字使用[二进制补码][twos-complement]表示法来存储。

每个有符号变体可以存储从−(2<sup>n − 1</sup>)到2<sup>n − 1</sup>−1之间的数字，其中_n_表示该变体使用的位数。因此，`i8`可以存储从−(2<sup>7</sup>)到2<sup>7</sup>−1之间的数字，即从−128到127。无符号变体可以存储从0到2<sup>n</sup>−1之间的数字，所以`u8`可以存储从0到2<sup>8</sup>−1之间的数字，即从0到255。

此外，`isize`和`usize`这两个类型取决于程序运行的计算机架构：如果你使用的是64位架构，则为64位；如果你使用的是32位架构，则为32位。

您可以使用表3-2中所示的任何形式来编写整数字面量。请注意，能够表示多种数字类型的数字字面量可以使用类型后缀来表示，例如`57u8`。此外，数字字面量也可以使用`_`作为视觉分隔符，以便更易于阅读，例如`1_000`，其值与明确指定为`1000`时相同。

<span class="caption">表3-2：Rust中的整数字面量</span>

那么，如何确定使用哪种整数类型呢？如果你不确定，Rust的默认设置通常是一个很好的起点：整数类型的默认值是`i32`。主要情况下，你会在索引某种集合时使用`isize`或`usize`。

> ##### 整数溢出  
> 假设有一个类型为 ``u8`` 的变量，它可以存储0到255之间的数值。如果你尝试将该变量的值设置为超出此范围的值，例如256，就会发生**整数溢出**。这种情况下，程序可能会出现两种行为之一。  
> 在调试模式下编译时，Rust会进行整数溢出的检测，如果发生了这种情况，程序会在运行时引发**panic**异常。当程序因错误而退出时，Rust会使用“panic”这一术语来描述这种情况；我们将在第九章的[“无法恢复的异常与`panic!`”][unrecoverable-errors-with-panic]<!-- ignore -->章节中详细讨论panic现象。  
> 在发布模式下编译时，如果使用了`--release`标志，Rust不会进行整数溢出的检测，以避免引发panic。相反，如果发生溢出，Rust会采用**二进制补数包装**的方式来处理。简单来说，大于类型所能容纳的最大值会被“包装”到该类型所能容纳的最小值上。以`u8`为例，值256会变成0，值257会变成1，依此类推。程序不会引发panic，但变量的值可能不符合你的预期。依赖整数溢出的包装行为被视为一种错误。  
> 为了明确处理溢出情况，你可以使用标准库为基本数值类型提供的一系列方法：  
> - 在所有模式下使用`wrapping_*`系列方法进行包装，例如`wrapping_add`。  
> - 如果发生了溢出，可以使用`checked_*`系列方法返回`None`的值。  
> - 可以使用`overflowing_*`系列方法同时返回实际值以及一个布尔值，以表明是否发生了溢出。  
> - 还可以使用`saturating_*`系列方法将数值饱和到其最小值或最大值。

#### 浮点类型

Rust还提供了两种用于表示_浮点数_的原始类型，这些数值带有小数点。Rust的浮点类型分别是`f32`和`f64`，它们的位数分别为32位和64位。默认类型是`f64`，因为在现代CPU上，它的运行速度与`f32`大致相同，但能够提供更高的精度。所有的浮点类型都是带符号的。

以下是一个展示浮点数使用的例子：

<span class="filename">文件名：src/main.rs</span>

```rust
{{#rustdoc_include ../listings/ch03-common-programming-concepts/no-listing-06-floating-point/src/main.rs}}
```

浮点数是按照IEEE-754标准来表示的。

#### 数值运算

Rust支持所有数字类型所期望的基本数学运算：加法、减法、乘法、除法以及取余数。整数除法会向零方向截断，结果取最接近的整数。以下代码展示了如何在`let`语句中使用这些数值运算：

<span class="filename">文件名：src/main.rs</span>

```rust
{{#rustdoc_include ../listings/ch03-common-programming-concepts/no-listing-07-numeric-operations/src/main.rs}}
```

这些语句中的每个表达式都使用了一个数学运算符，并且会计算出一个单一的值，然后这个值会被绑定到一个变量上。[附录 B][appendix_b]中列出了 Rust 提供的所有运算符。

#### 布尔类型

与大多数其他编程语言一样，Rust中的布尔类型有两种可能的值：`true`和`false`。布尔类型的大小为1字节。在Rust中，布尔类型是通过`bool`来定义的。例如：

<span class="filename">文件名：src/main.rs</span>

```rust
{{#rustdoc_include ../listings/ch03-common-programming-concepts/no-listing-08-boolean/src/main.rs}}
```

使用布尔值的主要方式是通过条件语句，例如 `if` 表达式。我们将在[“控制流”][control-flow]部分介绍 `if` 表达式在Rust中的工作原理。

#### 字符类型

Rust中的`char`类型是该语言中最基础的字母型数据。以下是一些声明`char`值的例子：

<span class="filename">文件名：src/main.rs</span>

```rust
{{#rustdoc_include ../listings/ch03-common-programming-concepts/no-listing-09-char/src/main.rs}}
```

请注意，我们使用单引号来指定 `char` 字面量，而字符串字面量则使用双引号。Rust 中的 `char` 类型大小为4字节，代表一个Unicode标量值，这意味着它可以表示的内容远不止ASCII字符。带重音字母、中文、日文、韩文字符、表情符号以及零宽度空格都是有效的 `char` 值。Unicode标量值的范围从 `U+0000` 到 `U+D7FF`，以及 `U+E000` 到 `U+10FFFF`（包括这两个值）。不过，在Unicode中，“字符”并不是一个严格的概念，因此你对“字符”的理解可能与Rust中的`char`的含义并不一致。我们将在第八章的[“使用字符串存储UTF-8编码的文本”][strings]部分详细讨论这个话题。

### 复合类型

_复合类型_可以将多个值组合成一个类型。Rust有两种基本的复合类型：元组数组和数组。

#### 元组类型

元组是一种将多种类型的值组合在一起的方式。元组的长度是固定的：一旦声明，其大小就不会发生变化。

我们通过在括号内编写逗号分隔的值列表来创建一个元组。元组的每个位置都有一个类型，而元组中的不同值的类型不必相同。在这个示例中，我们添加了可选的类型注解：

<span class="filename">文件名：src/main.rs</span>

```rust
{{#rustdoc_include ../listings/ch03-common-programming-concepts/no-listing-10-tuples/src/main.rs}}
```

变量 ``tup`` 绑定到整个元组，因为元组被视为一个单一的复合元素。要获取元组的各个值，我们可以使用模式匹配来分解元组的值，如下所示：

<span class="filename">文件名：src/main.rs</span>

```rust
{{#rustdoc_include ../listings/ch03-common-programming-concepts/no-listing-11-destructuring-tuples/src/main.rs}}
```

该程序首先创建一个元组，并将其绑定到变量`tup`上。然后，使用`let`进行模式匹配，将`tup`拆分成三个独立的变量：`x`、`y`和`z`。这种操作被称为“解构”，因为它将单个元组拆分成三个部分。最后，程序打印出`y`的值，该值为`6.4`。

我们还可以直接使用点符号（`.`）来访问元组中的元素，然后加上我们想要访问的值的索引。例如：

<span class="filename">文件名：src/main.rs</span>

```rust
{{#rustdoc_include ../listings/ch03-common-programming-concepts/no-listing-12-tuple-indexing/src/main.rs}}
```

该程序首先创建了一个元组 ``x``，然后按照各自的索引访问该元组的每个元素。与大多数编程语言一样，元组中的第一个索引是0。

没有任何值的元组有一个特殊的名称，叫做`_unit_`。这个值和相应的类型都被标记为`()`，它们分别表示空值或空的返回类型。如果表达式没有返回任何其他值，那么它会隐式地返回单位值。

#### 数组类型

另一种存储多个值的集合的方式是使用_数组_。与元组不同，数组中的每个元素必须具有相同的类型。与其他一些语言的数组不同，Rust中的数组具有固定的长度。

我们将数组中的值以逗号分隔的形式放在方括号内表示：

<span class="filename">文件名：src/main.rs</span>

```rust
{{#rustdoc_include ../listings/ch03-common-programming-concepts/no-listing-13-arrays/src/main.rs}}
```

数组在你需要将数据存储在栈上时非常有用，这与我们迄今为止所见的其他类型一样，而不是存储在堆上（我们将在[第4章][stack-and-heap]<!-- ignore -->中详细讨论栈和堆）。此外，当你希望始终拥有固定数量的元素时，数组也很有用。不过，数组的灵活性不如向量类型。向量是标准库提供的一种类似的集合类型，其大小可以动态增加或减少，因为其内容存储于堆上。如果你不确定应该使用数组还是向量，那么建议使用向量。[第8章][vectors]<!-- ignore -->对向量进行了更详细的介绍。

然而，当你知道数组中的元素数量不会发生变化时，数组会更加有用。例如，如果你在程序中使用月份的名称，那么使用数组会比向量更合适，因为你知道它总是会包含12个元素：

```rust
let months = ["January", "February", "March", "April", "May", "June", "July",
              "August", "September", "October", "November", "December"];
```

你可以通过使用方括号来定义数组的类型，括号内依次列出每个元素的类型，然后在末尾加上分号，最后再注明数组中元素的数量，格式如下：

```rust
let a: [i32; 5] = [1, 2, 3, 4, 5];
```

在这里，`i32`表示每个元素的类型。在分号之后，数字`5`表示该数组包含五个元素。

您还可以通过指定初始值，然后加上分号，最后在方括号内指定数组的长度，来初始化一个数组，使得数组中的每个元素都包含相同的值，如下所示：

```rust
let a = [3; 5];
```

名为`a`的数组将包含`5`个元素，这些元素最初都会被设置为`3`的值。这与编写`let a = [3, 3, 3, 3, 3];`的方式相同，但更加简洁。

<a id="访问数组元素"></a>

#### 数组元素访问

数组是一种固定大小的内存块，可以存储在栈上。你可以使用索引来访问数组中的元素，如下所示：

<span class="filename">文件名：src/main.rs</span>

```rust
{{#rustdoc_include ../listings/ch03-common-programming-concepts/no-listing-14-array-indexing/src/main.rs}}
```

在这个示例中，名为`first`的变量将获得值`1`，因为那是数组中索引为`[0]`的元素的值。而名为`second`的变量将从数组中的索引`[1]`处获取值`2`。

#### 无效的数组元素访问

让我们看看，如果你尝试访问数组中的一个元素，而该元素位于数组的末尾时会发生什么。假设你运行这段代码，类似于第2章中的猜数游戏，从用户那里获取一个数组索引：

<span class="filename">文件名：src/main.rs</span>

```rust,ignore,panics
{{#rustdoc_include ../listings/ch03-common-programming-concepts/no-listing-15-invalid-array-access/src/main.rs}}
```

这段代码可以成功编译。如果你使用 ``cargo run`` 来运行这段代码，并且输入 ``0``、``1``、``2``、``3`` 或 ``4``，程序将会打印出数组中相应索引处的数值。如果你输入的是数组末尾之后的数字，比如 ``10``，那么你将看到这样的输出：

<!-- 手动重新生成
cd listings/ch03-common-programming-concepts/no-listing-15-invalid-array-access
cargo run
10
-->

```console
thread 'main' panicked at src/main.rs:19:19:
index out of bounds: the len is 5 but the index is 10
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace
```

该程序在尝试使用无效值进行索引操作时出现了运行时错误。程序因错误信息而终止，并未执行最终的``println!``语句。当您尝试通过索引访问元素时，Rust会检查指定的索引是否小于数组的长度。如果索引大于或等于数组长度，Rust将会引发panic。这种检查必须在运行时进行，尤其是在这种情况下，因为编译器无法知道用户在稍后运行代码时可能会输入什么值。

这是一个展示Rust内存安全原则的实际应用示例。在许多低级语言中，这种检查并不进行，当你提供错误的索引时，可能会访问无效的内存。Rust通过立即终止程序来防止这种错误，而不是允许程序继续运行并访问内存。第9章将进一步讨论Rust的错误处理机制，以及如何编写既可读又安全的代码，避免程序崩溃或允许无效的内存访问。

[比较猜测与正确答案]: ch02-00-guessing-game-tutorial.html#comparing-the-guess-to-the-secret-number  
[二进制补码]: https://en.wikipedia.org/wiki/Two%27s_complement  
[控制流]: ch03-05-control-flow.html#control-flow  
[字符串处理]: ch08-02-strings.html#storing-utf-8-encoded-text-with-strings  
[栈与堆]: ch04-01-what-is-ownership.html#the-stack-and-the-heap  
[向量]: ch08-01-vectors.html  
[不可恢复的错误与恐慌]: ch09-01-unrecoverable-errors-with-panic.html  
[附录B]: appendix-02-operators.md