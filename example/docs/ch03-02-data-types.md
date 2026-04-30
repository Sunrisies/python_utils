那么，如何确定使用哪种整数类型呢？如果你不确定，Rust的默认设置通常是一个很好的起点：整数类型的默认值是 `i32`。而使用 `isize` 或 `usize` 的主要情况是在索引某种集合时。

> ##### 整数溢出  
> 假设你有一个类型为 `u8` 的变量，该变量可以存储 0 到 255 之间的数值。如果你尝试将变量的值设置为该范围之外的数值，例如 256，就会发生 _整数溢出_。这种情况下，程序可能会出现两种行为之一。  
> 在调试模式下编译时，Rust 会进行整数溢出检查，如果发生了溢出，程序会在运行时引发 _panic_ 异常。当程序因错误退出时，Rust 会使用 “panic” 这一术语来描述这种情况。我们将在第九章的 [“不可恢复的错误与 `panic!`”][unrecoverable-errors-with-panic]<!-- ignore --> 部分详细讨论 panic 现象。  
> 在发布模式下编译时，如果设置了 `--release` 标志，Rust 不会进行整数溢出检查，以避免引发 panic 异常。如果发生溢出，Rust 会采用 _二进制补数包装_ 的方式处理：即大于类型最大值的数值会被“包装”到类型最小值的范围内。例如，256 会被包装为 0，257 会被包装为 1，依此类推。程序不会引发 panic 异常，但变量的值可能会与你的预期不符。依赖整数溢出的包装行为被视为一种错误。  
> 为了明确处理溢出情况，你可以使用标准库为基本数值类型提供的方法：  
> - 在所有模式下使用 `wrapping_*` 方法进行处理，例如 `wrapping_add`。  
> - 使用 `None` 方法在发生溢出时返回相应的值。  
> - 使用 `checked_*` 方法返回溢出发生与否的布尔值。  
> - 使用 `overflowing_*` 方法在数值的最小值或最大值处进行饱和处理。

#### 浮点类型

Rust还提供了两种用于表示_浮点数字_的原始类型，这些数字具有小数点。Rust的浮点类型分别是`f32`和`f64`，它们的位数分别达到32位和64位。默认类型是`f64`，因为在现代CPU上，它的运行速度与`f32`大致相同，但能够提供更高的精度。所有的浮点类型都是带符号的。

以下是一个展示浮点数使用的例子：

<span class="filename"> 文件名: src/main.rs</span>

```rust
fn main() {
    let x = 2.0; // f64

    let y: f32 = 3.0; // f32
}

```

浮点数是按照 IEEE-754 标准来表示的。

#### 数值运算

Rust支持所有数字类型所期望的基本数学运算：加法、减法、乘法、除法和取余数。整数除法会向零方向截断，结果取最接近的整数。以下代码展示了如何在 `let` 语句中使用这些数值运算：

<span class="filename"> 文件名: src/main.rs</span>

```rust
fn main() {
    // addition
    let sum = 5 + 10;

    // subtraction
    let difference = 95.5 - 4.3;

    // multiplication
    let product = 4 * 30;

    // division
    let quotient = 56.7 / 32.2;
    let truncated = -5 / 3; // Results in -1

    // remainder
    let remainder = 43 % 5;
}

```

这些语句中的每个表达式都使用了一个数学运算符，并且会计算出一个单一的值，然后这个值会被绑定到一个变量上。[附录 B][appendix_b]<!-- ignore --> 包含了 Rust 提供的所有运算符的列表。

#### 布尔类型

与大多数其他编程语言一样，Rust中的布尔类型有两种可能的值：`true`和`false`。布尔类型的大小为1字节。Rust中的布尔类型使用`bool`来表示。例如：

<span class="filename"> 文件名: src/main.rs</span>

```rust
fn main() {
    let t = true;

    let f: bool = false; // with explicit type annotation
}

```

使用布尔值的主要方式是通过条件语句，例如 `if` 这样的表达式。我们将在[“控制流”][control-flow]<!-- ignore -->这一节中介绍 `if` 表达式在 Rust 中的用法。

#### 字符类型

Rust中的⊂PH0类型是该语言中最基础的字母类型。以下是一些声明⊂PH1值的例子：

<span class="filename"> 文件名: src/main.rs</span>

```rust
fn main() {
    let c = 'z';
    let z: char = 'ℤ'; // with explicit type annotation
    let heart_eyed_cat = '😻';
}

```

请注意，我们使用单引号来表示 `char` 字面量，而字符串字面量则使用双引号。Rust 中的 `char` 类型大小为 4 个字节，代表一个 Unicode 标量值，这意味着它可以表示的内容远不止 ASCII 字符。带重音的字母、中文、日文和韩文字符、表情符号以及零宽度空格都是 Rust 中有效的 `char` 值。Unicode 标量值的范围从 `U+0000` 到 `U+D7FF`，以及 `U+E000` 到 `U+10FFFF`（包括这两个端点）。不过，在 Unicode 中，“字符”并不是一个严格的概念，因此你对“字符”的理解可能与 Rust 中的 `char` 的含义并不一致。我们将在第八章的[“使用字符串存储 UTF-8 编码的文本”][strings]<!-- ignore --> 中详细讨论这个话题。

### 复合类型

_复合类型_可以将多个值组合成一个类型。Rust 有两种基本的复合类型：元组数组和数组。

#### 元组类型

元组是一种将多种类型的值组合在一起的方式。元组具有固定的长度：一旦声明，其大小就不能改变或缩小。

我们通过在括号内编写逗号分隔的值列表来创建一个元组。元组中的每个位置都有一个类型，而元组中的不同值的类型不必相同。在这个示例中，我们添加了可选的类型注释：

<span class="filename"> 文件名: src/main.rs</span>

```rust
fn main() {
    let tup: (i32, f64, u8) = (500, 6.4, 1);
}

```

变量 `tup` 绑定到整个元组，因为元组被视为一个单一的复合元素。要获取元组的各个值，我们可以使用模式匹配来分解元组的值，如下所示：

<span class="filename"> 文件名: src/main.rs</span>

```rust
fn main() {
    let tup = (500, 6.4, 1);

    let (x, y, z) = tup;

    println!("The value of y is: {y}");
}

```

该程序首先创建一个元组，并将其绑定到变量 `tup` 上。然后，使用带有 `let` 的模式来提取 `tup`，并将其拆分为三个独立的变量：`x`、`y` 和 `z`。这种操作被称为“解构”，因为它将单个元组拆分成三个部分。最后，程序打印出变量 `y` 的值，该值为 `6.4`。

我们也可以通过使用点号（`.`）加上想要访问的值的索引来直接访问元组中的元素。例如：

<span class="filename"> 文件名: src/main.rs</span>

```rust
fn main() {
    let x: (i32, f64, u8) = (500, 6.4, 1);

    let five_hundred = x.0;

    let six_point_four = x.1;

    let one = x.2;
}

```

该程序首先创建了一个元组 `x`，然后按照各自的索引访问该元组中的每个元素。与大多数编程语言一样，元组中的第一个索引是 0。

没有任何值的元组有一个特殊的名称，叫做_unit_。这个值和相应的类型都被表示为`()`，它们分别表示空值或空返回类型。如果表达式不返回任何其他值，那么它会隐式地返回单位值。

#### 数组类型

另一种存储多个值的集合的方式是使用_数组_。与元组不同，数组中的每个元素必须具有相同的类型。此外，与某些其他语言的数组不同，Rust中的数组具有固定的长度。

我们将数组中的值以逗号分隔列表的形式，放在方括号内表示：

<span class="filename"> 文件名: src/main.rs</span>

```rust
fn main() {
    let a = [1, 2, 3, 4, 5];
}

```

数组在你需要将数据存储在栈上时非常有用，这与我们迄今为止看到的其他类型一样，而不是存储在堆上（我们将在[第4章][stack-and-heap]<!-- ignore -->中更详细地讨论栈和堆）。此外，当你希望始终拥有固定数量的元素时，数组也非常适用。不过，数组的灵活性不如向量类型。向量是标准库提供的一种类似的集合类型，其大小可以动态变化，因为其内容存储在堆上。如果你不确定应该使用数组还是向量，那么建议使用向量。[第8章][vectors]<!-- ignore -->会详细讨论向量。

然而，当你知道数组中的元素数量不会发生变化时，数组会更加有用。例如，如果你在程序中使用月份的名称，你可能会选择使用数组而不是向量，因为你知道它总是会包含12个元素。

```rust
let months = ["January", "February", "March", "April", "May", "June", "July",
              "August", "September", "October", "November", "December"];
```

你可以通过使用方括号来定义数组的类型，括号内依次列出每个元素的类型，然后在每个元素类型后面加上分号，最后再注明数组中的元素数量，格式如下：

```rust
let a: [i32; 5] = [1, 2, 3, 4, 5];
```

在这里，`i32`表示每个元素的类型。在分号之后，数字`5`表示该数组包含五个元素。

您还可以通过指定初始值，然后加上分号，最后在方括号中指定数组的长度，来初始化一个数组，使得数组中的每个元素都包含相同的值，如下所示：

```rust
let a = [3; 5];
```

名为 `a` 的数组将包含 `5` 个元素，这些元素最初都会被设置为值`3`。这相当于用更简洁的方式书写 `let a = [3, 3, 3, 3, 3];`。

<!-- Old headings. Do not remove or links may break. -->
<a id="accessing-array-elements"></a>

#### 数组元素访问

数组是一种固定大小的内存块，可以存储在栈上。你可以使用索引来访问数组中的元素，如下所示：

<span class="filename"> 文件名: src/main.rs</span>

```rust
fn main() {
    let a = [1, 2, 3, 4, 5];

    let first = a<!-- ignore -->;
    let second = a<!-- ignore
-->;
}

```

在这个示例中，名为 `first` 的变量将获得值 `1`，因为那是数组中索引为 `[0]` 的位置的值。而名为 `second` 的变量将获得来自数组索引 `[1]` 的值 `2`。

#### 无效的数组元素访问

让我们看看，如果你尝试访问数组中的一个元素，而该元素位于数组的末尾时，会发生什么。假设你运行这段代码，类似于第2章中的猜数游戏，从用户那里获取一个数组索引：

<span class="filename"> 文件名: src/main.rs</span>

```rust,ignore,panics
use std::io;

fn main() {
    let a = [1, 2, 3, 4, 5];

    println!("Please enter an array index.");

    let mut index = String::new();

    io::stdin()
        .read_line(&mut index)
        .expect("Failed to read line");

    let index: usize = index
        .trim()
        .parse()
        .expect("Index entered was not a number");

    let element = a[index];

    println!("The value of the element at index {index} is: {element}");
}

```

这段代码可以成功编译。如果你使用 `cargo run` 来运行这段代码，并且输入 `0`、`1`、`2`、`3` 或 `4`，程序将会打印出数组中对应索引的值。如果你输入的数字超过了数组的末尾，比如 `10`，那么你将看到这样的输出：

<!-- manual-regeneration
cd listings/ch03-common-programming-concepts/no-listing-15-invalid-array-access
cargo run
10
-->

```console
thread 'main' panicked at src/main.rs:19:19:
index out of bounds: the len is 5 but the index is 10
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace
```

该程序在尝试使用无效值进行索引操作时出现了运行时错误。程序因错误信息而终止，并未执行最后的 `println!` 语句。当您尝试通过索引访问元素时，Rust 会检查指定的索引是否小于数组的长度。如果索引大于或等于数组长度，Rust 将会引发 panic 错误。这种检查必须在运行时进行，尤其是在这种情况下，因为编译器无法预知用户在稍后运行代码时可能会输入什么值。

这是 Rust 内存安全原则的实际应用示例。在许多低级语言中，这种检查并不进行，当你提供错误的索引时，可能会访问无效的内存。Rust 通过立即终止程序来防止这种错误，而不是允许程序继续运行并访问内存。第9章将进一步讨论 Rust 的错误处理机制，以及如何编写既可读又安全的代码，避免程序崩溃或允许无效的内存访问。

[comparing-the-guess-to-the-secret-number]: ch02-00-guessing-game-tutorial.html#comparing-the-guess-to-the-secret-number
[twos-complement]: https://en.wikipedia.org/wiki/Two%27s_complement
[control-flow]: ch03-05-control-flow.html#control-flow
[strings]: ch08-02-strings.html#storing-utf-8-encoded-text-with-strings
[stack-and-heap]: ch04-01-what-is-ownership.html#the-stack-and-the-heap
[vectors]: ch08-01-vectors.html
[unrecoverable-errors-with-panic]: ch09-01-unrecoverable-errors-with-panic.html
[appendix_b]: appendix-02-operators.md
