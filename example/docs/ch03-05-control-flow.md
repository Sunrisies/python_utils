## 控制流

根据条件是否为 `true` 来运行某些代码，以及在条件为 `true` 时重复运行某些代码的能力，是大多数编程语言的基本构建块。在 Rust 代码中，能够控制执行流程的最常见结构就是 `if` 表达式和循环。

### `if` 表达式

一个 `if` 表达式允许您根据条件来分支代码。您提供一个条件，然后声明：“如果这个条件满足，就运行这个代码块。如果条件不满足，则不要运行这个代码块。”

在你的`_projects_`目录下创建一个新的项目，名为`_branches_`，以探索`if`表达式。在`_src/main.rs_`文件中，输入以下内容：

<span class="filename"> 文件名: src/main.rs</span>

```rust
fn main() {
    let number = 3;

    if number < 5 {
        println!("condition was true");
    } else {
        println!("condition was false");
    }
}

```

在 `if` 表达式中，所有表达式都以关键字 `if` 开头，随后是一个条件判断。在这种情况下，该条件用于检查变量 `number` 的值是否小于 5。如果条件满足，即 `true`，那么就会立即在花括号内执行相应的代码块。在 `if` 表达式中，与条件判断相关的代码块有时被称为 _arms_，就像我们在第 2 章的 [“比较猜测数与秘密数字”][comparing-the-guess-to-the-secret-number]<!--
ignore --> 部分所讨论的闭包一样。

此外，我们还可以包含一个 `else` 表达式，我们选择在这里使用这个表达，以便在条件评估为 `false` 时，程序可以执行另一个代码块。如果您不提供 `else` 表达式，而条件是 `false`，那么程序将跳过 `if` 块，直接继续执行下一段代码。

请尝试运行这段代码；你应该会看到如下输出：

```console
$ cargo run
   Compiling branches v0.1.0 (file:///projects/branches)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.31s
     Running `target/debug/branches`
condition was true

```

让我们尝试将 `number` 的值改为一个能使条件 `false` 成立的值，看看会发生什么。

```rust,ignore
    let number = 7;

```

再次运行程序，然后查看输出结果：

```console
$ cargo run
   Compiling branches v0.1.0 (file:///projects/branches)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.31s
     Running `target/debug/branches`
condition was false

```

同样值得注意的是，这段代码中的条件必须是一个 `bool`。如果条件不是 `bool`，我们将会收到错误。例如，尝试运行以下代码：

<span class="filename"> 文件名: src/main.rs</span>

```rust,ignore,does_not_compile
fn main() {
    let number = 3;

    if number {
        println!("number was three");
    }
}

```

此时，`if`条件的取值为`3`，Rust会抛出错误：

```console
$ cargo run
   Compiling branches v0.1.0 (file:///projects/branches)
error[E0308]: mismatched types
 --> src/main.rs:4:8
  |
4 |     if number {
  |        ^^^^^^ expected `bool`, found integer

For more information about this error, try `rustc --explain E0308`.
error: could not compile `branches` (bin "branches") due to 1 previous error

```

这个错误表明，Rust期望得到一个 `bool` 类型的值，但实际上得到的是一个整数。与 Ruby 和 JavaScript 等语言不同，Rust 不会自动将非布尔类型转换为布尔类型。你必须明确指定，并且始终将 `if` 作为条件，并为其提供一个布尔类型的值。例如，如果我们希望 `if` 代码块仅在某个数字不等于 `0` 时运行，那么我们可以将 `if` 表达式修改为如下形式：

<span class="filename"> 文件名: src/main.rs</span>

```rust
fn main() {
    let number = 3;

    if number != 0 {
        println!("number was something other than zero");
    }
}

```

运行这段代码将会输出 `number was something other than zero`。

#### 使用 `else if` 处理多个条件

您可以通过在 `else if` 表达式中组合 `if` 和 `else` 来使用多个条件。例如：

<span class="filename"> 文件名: src/main.rs</span>

```rust
fn main() {
    let number = 6;

    if number % 4 == 0 {
        println!("number is divisible by 4");
    } else if number % 3 == 0 {
        println!("number is divisible by 3");
    } else if number % 2 == 0 {
        println!("number is divisible by 2");
    } else {
        println!("number is not divisible by 4, 3, or 2");
    }
}

```

这个程序有四种可能的执行路径。运行后，你应该看到以下输出：

```console
$ cargo run
   Compiling branches v0.1.0 (file:///projects/branches)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.31s
     Running `target/debug/branches`
number is divisible by 3

```

当这个程序执行时，它会依次检查每一个 `if` 表达式，并执行第一个满足条件且值为 `true` 的主体。需要注意的是，尽管 6 可以被 2 整除，但我们并没有看到输出 `number is divisible by 2`，也没有看到来自 `else` 块的 `number is not divisible by 4, 3, or 2` 文本。这是因为 Rust 只会执行第一个 `true` 条件的块，一旦找到满足条件的条件，它就不会再检查其余的条件了。

使用过多的 `else if` 表达式会让代码变得混乱，因此如果你使用了多个这样的表达式，可能需要对代码进行重构。第6章介绍了一种强大的Rust分支构造方式，称为 `match`，适用于这种情况。

#### 在 `let` 语句中使用 `if`

因为 `if` 是一个表达式，我们可以在 `let` 语句的右侧使用它，将结果赋值给一个变量，如清单3-2所示。

<Listing number="3-2" file-name="src/main.rs" caption="Assigning the result of an `if` expression to a variable">

```rust
fn main() {
    let condition = true;
    let number = if condition { 5 } else { 6 };

    println!("The value of number is: {number}");
}

```

</Listing>

变量 `number` 将根据 `if` 表达式的结果来绑定一个值。运行这段代码来看看会发生什么：

```console
$ cargo run
   Compiling branches v0.1.0 (file:///projects/branches)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.30s
     Running `target/debug/branches`
The value of number is: 5

```

请记住，代码块的最终计算结果取决于其中最后一个表达式的值，而数字本身也是一种表达式。在这种情况下，整个 `if` 表达式的值取决于哪个代码块被执行。这意味着 `if` 的每个分支可能产生的结果必须是相同类型的。在 Listing 3-2 中， `if` 和 `else` 分支的结果都是 `i32` 整数类型。如果类型不匹配，就像下面的例子一样，就会出错。

<span class="filename"> 文件名: src/main.rs</span>

```rust,ignore,does_not_compile
fn main() {
    let condition = true;

    let number = if condition { 5 } else { "six" };

    println!("The value of number is: {number}");
}

```

当我们尝试编译这段代码时，会遇到一个错误。`if`和`else`这两个分支中的值类型是不兼容的，Rust会明确指出问题所在的位置。

```console
$ cargo run
   Compiling branches v0.1.0 (file:///projects/branches)
error[E0308]: `if` and `else` have incompatible types
 --> src/main.rs:4:44
  |
4 |     let number = if condition { 5 } else { "six" };
  |                                 -          ^^^^^ expected integer, found `&str`
  |                                 |
  |                                 expected because of this

For more information about this error, try `rustc --explain E0308`.
error: could not compile `branches` (bin "branches") due to 1 previous error

```

`if`块中的表达式计算结果为整数，而`else`块中的表达式计算结果为字符串。这种写法是行不通的，因为变量必须具有单一类型，而Rust需要在编译时明确知道`number`变量的类型。了解`number`的类型可以让编译器验证`number`在任何地方使用的类型都是有效的。如果`number`的类型仅在运行时才确定，Rust就无法实现这一点；在这种情况下，编译器会变得更加复杂，并且对于代码的可靠性也会降低，因为它需要跟踪任何变量的多种可能类型。

### 循环中的重复操作

多次执行一段代码通常是非常有用的。为此，Rust提供了多种循环结构，这些结构会依次执行循环体内的代码，直到最后，然后再立即从开始处重新开始。为了尝试使用循环结构，让我们创建一个新的项目，命名为 _loops_。

Rust 有三种循环结构：`loop`、`while` 和 `for`。让我们分别尝试每一种。

#### 使用 `loop` 重复代码

关键字 `loop` 告诉Rust重复执行一段代码，可以永远执行，也可以直到你明确指示停止为止。

例如，将您在 _loops_ 目录中的 _src/main.rs_ 文件更改为如下形式：

<span class="filename"> 文件名: src/main.rs</span>

```rust,ignore
fn main() {
    loop {
        println!("again!");
    }
}

```

当我们运行这个程序时，会看到 `again!` 不断被打印出来，直到我们手动停止程序。大多数终端都支持键盘快捷键<kbd>ctrl</kbd>-<kbd>C</kbd>来中断那些陷入无限循环的程序。试试看吧：

<!-- manual-regeneration
cd listings/ch03-common-programming-concepts/no-listing-32-loop
cargo run
CTRL-C
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

您可能会看到，也可能不会看到单词 `again!` 被打印在 `^C` 之后，这取决于代码在循环中接收到中断信号时的位置。

幸运的是，Rust还提供了一种通过代码来跳出循环的方法。你可以在循环内部添加 `break` 关键字，以此来告诉程序何时停止执行循环。回想一下，在第二章的“猜对后退出”部分，我们就是使用这种方法在用户猜对数字后退出程序的。

在猜谜游戏中，我们还使用了 `continue` 这个符号。它会在循环中告诉程序跳过本次循环中所有剩余的代码，直接进入下一次循环。

#### 从循环中返回值

`loop`的一个用途是重新尝试一个可能失败的操作，比如检查一个线程是否已经完成了它的任务。你可能还需要将该操作的结果从循环中传递出去，以便让其他代码能够使用它。为此，你可以在使用的`break`表达式之后添加你想要返回的值；这个值将会从循环中返回，从而可以被其他代码使用，如下所示：

```rust
fn main() {
    let mut counter = 0;

    let result = loop {
        counter += 1;

        if counter == 10 {
            break counter * 2;
        }
    };

    println!("The result is {result}");
}

```

在循环之前，我们声明一个名为 `counter` 的变量，并将其初始化为 `0`。然后，我们声明一个名为 `result` 的变量，用于存储循环返回的值。在循环的每次迭代中，我们将 `1` 添加到 `counter` 变量中，然后检查 `counter` 是否等于 `10`。当它们相等时，我们使用 `break` 关键字，并将值 `counter * 2` 赋给该变量。循环结束后，我们使用分号来结束将值赋给 `result` 的语句。最后，我们打印 `result` 中的值，在这个案例中，该值为 `20`。

您也可以在循环内部使用 `return`。而 `break` 仅会退出当前循环，而 `return` 则会退出当前函数。

<!-- Old headings. Do not remove or links may break. -->
<a id="loop-labels-to-disambiguate-between-multiple-loops"></a>

#### 使用循环标签进行歧义消除

如果你在循环内部还有循环，那么 `break` 和 `continue` 将适用于该循环中的最内层循环。你可以选择性地为某个循环指定一个 _循环标签_，然后可以使用 `break` 或 `continue` 来指定这些关键字适用于该带有标签的循环，而不是最内层的循环。循环标签必须以单引号开头。以下是一个包含两个嵌套循环的示例：

```rust
fn main() {
    let mut count = 0;
    'counting_up: loop {
        println!("count = {count}");
        let mut remaining = 10;

        loop {
            println!("remaining = {remaining}");
            if remaining == 9 {
                break;
            }
            if count == 2 {
                break 'counting_up;
            }
            remaining -= 1;
        }

        count += 1;
    }
    println!("End count = {count}");
}

```

外部循环有一个标签为 `'counting_up`，它将从0计数到2。  
没有标签的内部循环则从10计数到9。第一个没有指定标签的 `break` 语句只会退出内部循环。而 `break
'counting_up;` 语句则会退出外部循环。这段代码会输出：

```console
$ cargo run
   Compiling loops v0.1.0 (file:///projects/loops)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.58s
     Running `target/debug/loops`
count = 0
remaining = 10
remaining = 9
count = 1
remaining = 10
remaining = 9
count = 2
remaining = 10
End count = 2

```

<!-- Old headings. Do not remove or links may break. -->
<a id="conditional-loops-with-while"></a>

#### 使用 while 简化条件循环

程序通常需要在循环中评估某个条件。当条件满足 `true` 时，循环会继续运行。当条件不再满足 `true` 时，程序会调用 `break` 来终止循环。可以使用 `loop`、 `if`、 `else` 和 `break` 的组合来实现这样的行为；如果你愿意，现在就可以在程序中尝试这样做。不过，这种模式非常常见，Rust 为此提供了一种内置的语言结构，称为 `while` 循环。在清单 3-3 中，我们使用 `while` 来循环执行程序三次，每次循环都会递减计数，然后在循环结束后打印一条消息并退出程序。

<Listing number="3-3" file-name="src/main.rs" caption="Using a `while` loop to run code while a condition evaluates to `true`">

```rust
fn main() {
    let mut number = 3;

    while number != 0 {
        println!("{number}!");

        number -= 1;
    }

    println!("LIFTOFF!!!");
}

```

</Listing>

这种构造方式消除了使用`loop`、`if`、`else`和`break`时所需的许多嵌套结构，使得代码更加清晰。当条件评估结果为`true`时，代码会执行；否则，循环会终止。

#### 使用 `for` 遍历集合

您可以选择使用 `while` 结构来遍历集合中的元素，例如数组。例如，清单 3-4 中的循环会打印出数组 `a` 中的每个元素。

<Listing number="3-4" file-name="src/main.rs" caption="Looping through each element of a collection using a `while` loop">

```rust
fn main() {
    let a = [10, 20, 30, 40, 50];
    let mut index = 0;

    while index < 5 {
        println!("the value is: {}", a[index]);

        index += 1;
    }
}

```

</Listing>

在这里，代码会遍历数组中的元素。它从索引`0`开始，然后循环直到到达数组的最后一个索引(即`index < 5` is no longer `true`). Running this code will print every
element in the array:

```console
$ cargo run
   Compiling loops v0.1.0 (file:///projects/loops)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.32s
     Running `target/debug/loops`
the value is: 10
the value is: 20
the value is: 30
the value is: 40
the value is: 50

```

All five array values appear in the terminal, as expected. Even though `index`
will reach a value of `5` at some point, the loop stops executing before trying
to fetch a sixth value from the array.

However, this approach is error-prone; we could cause the program to panic if
the index value or test condition is incorrect. For example, if you changed the
definition of the `a` array to have four elements but forgot to update the
condition to `while index < 4`, the code would panic. It’s also slow, because
the compiler adds runtime code to perform the conditional check of whether the
index is within the bounds of the array on every iteration through the loop.

As a more concise alternative, you can use a `for` loop and execute some code
for each item in a collection. A `for` loop looks like the code in Listing 3-5.

<Listing number="3-5" file-name="src/main.rs" caption="Looping through each element of a collection using a `for` loop">

```rust
fn main() {
    let a = [10, 20, 30, 40, 50];

    for element in a {
        println!("the value is: {element}");
    }
}

```

</Listing>

When we run this code, we’ll see the same output as in Listing 3-4. More
importantly, we’ve now increased the safety of the code and eliminated the
chance of bugs that might result from going beyond the end of the array or not
going far enough and missing some items. Machine code generated from `for`
loops can be more efficient as well because the index doesn’t need to be
compared to the length of the array at every iteration.

Using the `for` loop, you wouldn’t need to remember to change any other code if
you changed the number of values in the array, as you would with the method
used in Listing 3-4.

The safety and conciseness of `for` loops make them the most commonly used loop
construct in Rust. Even in situations in which you want to run some code a
certain number of times, as in the countdown example that used a `while` loop
in Listing 3-3, most Rustaceans would use a `for` loop. The way to do that
would be to use a `Range`, provided by the standard library, which generates
all numbers in sequence starting from one number and ending before another
number.

Here’s what the countdown would look like using a `for` loop and another method
we’ve not yet talked about, `rev`, to reverse the range:

<span class="filename">Filename: src/main.rs</span>

```rust
fn main() {
    for number in (1..4).rev() {
        println!("{number}!");
    }
    println!("LIFTOFF!!!");
}

```

This code is a bit nicer, isn’t it?

## Summary

You made it! This was a sizable chapter: You learned about variables, scalar
and compound data types, functions, comments, `if表达式。为了练习本章所讨论的概念，可以尝试编写程序来实现以下操作：

- 将温度从华氏度转换为摄氏度。  
- 生成第 *n* 个斐波那契数。  
- 打印圣诞颂歌《十二日圣诞颂歌》的歌词，利用歌曲中的重复结构进行优化。

当您准备好继续前进时，我们将讨论一个在Rust中独有的概念——所有权。这个概念在其他编程语言中并不常见。

[comparing-the-guess-to-the-secret-number]: ch02-00-guessing-game-tutorial.html#comparing-the-guess-to-the-secret-number
[quitting-after-a-correct-guess]: ch02-00-guessing-game-tutorial.html#quitting-after-a-correct-guess
