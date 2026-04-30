## 所有地方都可以使用模式

在 Rust 中，模式出现在许多地方，而你可能一直在不知不觉中使用它们！本节将讨论所有允许使用模式的场景。

### `match` 武器

如第6章所述，我们在 `match` 表达式的臂部使用模式。  
正式来说， `match` 表达式被定义为关键字 `match`，它代表要匹配的值，以及一个或多个匹配臂，这些匹配臂由模式和表达式组成，当值匹配该臂的模式时，就会执行相应的操作。

<!--
  Manually formatted rather than using Markdown intentionally: Markdown does not
  support italicizing code in the body of a block like this!
-->

<pre><code>match <em>VALUE</em> {
    <em>PATTERN</em> => <em>EXPRESSION</em>,
    <em>PATTERN</em> => <em>EXPRESSION</em>,
    <em>PATTERN</em> => <em>EXPRESSION</em>,
}</code></pre>

例如，这是来自清单6-5中的 `match` 表达式，它匹配变量 `x` 中的 `Option<i32>` 值。

```rust,ignore
match x {
    None => None,
    Some(i) => Some(i + 1),
}
```

这个 `match` 表达式中的模式就是每个箭头左边的 `None` 和 `Some(i)`。

对于 `match` 表达式的一个要求是，它们必须涵盖所有可能性，也就是说， `match` 表达式中所有可能的值都必须被考虑进去。确保涵盖所有可能性的一种方法是为最后一个分支设置一个通用的模式。例如，一个与任何值匹配的变量名永远不会失败，因此能够涵盖所有剩余的情况。

特定的模式 `_` 可以匹配任何内容，但它永远不会绑定到某个变量，因此它经常被用于最后的匹配操作中。模式 `_` 在你想忽略未指定的值时非常有用。我们将在本章后面的 [“Ignoring Values in a
Pattern”][ignoring-values-in-a-pattern]<!-- ignore --> 中更详细地介绍模式 `_`。

### 语句

在本章之前，我们仅明确讨论了如何使用`match`和`if let`模式，但实际上，我们也在其他地方使用了模式，包括在`let`语句中。例如，考虑这样一个简单的变量赋值操作，使用的是`let`模式。

```rust
let x = 5;
```

每次你使用这样的 `let` 语句时，你实际上都是在使用模式，
尽管你可能没有意识到这一点！更正式地说，一个 `let` 语句看起来是这样的：

<!--
  Manually formatted rather than using Markdown intentionally: Markdown does not
  support italicizing code in the body of a block like this!
-->

<pre>  
<code> let <em> PATTERN</em> = <em> EXPRESSION</em> ;</code>  
</pre>

在像 `let x = 5;` 这样的语句中，当变量名位于 PATTERN 位置时，该变量名实际上是一种特别简单的模式。Rust 会将表达式与模式进行比较，并分配任何匹配到的名称。因此，在 `let x = 5;` 示例中，`x` 这个模式意味着“将在这里匹配到的内容绑定到变量 `x`”。由于 `x` 这个名称代表了整个模式，所以这个模式实际上意味着“将任何内容绑定到变量 `x`，无论其值是什么”。

为了更清楚地了解 `let` 的模式匹配特性，请参考清单 19-1。该示例使用了带有 `let` 的模式来重构元组。

<Listing number="19-1" caption="Using a pattern to destructure a tuple and create three variables at once">

```rust
    let (x, y, z) = (1, 2, 3);

```

</Listing>

在这里，我们将一个元组与模式进行匹配。Rust会比较值 `(1, 2, 3)` 与模式 `(x, y, z)`，并判断两者是否匹配——也就是说，两个元组中的元素数量相同。因此，Rust会将 `1` 绑定到 `x`，将 `2` 绑定到 `y`，将 `3` 绑定到 `z`。你可以将这种元组模式看作是在其内部嵌套了三个单独的变量模式。

如果模式中的元素数量与元组中的元素数量不匹配，那么整体类型就不会匹配，我们将会收到编译器错误。例如， Listing 19-2 展示了一种尝试将包含三个元素的元组拆分成两个变量的尝试，这种尝试是行不通的。

<Listing number="19-2" caption="Incorrectly constructing a pattern whose variables don’t match the number of elements in the tuple">

```rust,ignore,does_not_compile
    let (x, y) = (1, 2, 3);

```

</Listing>

尝试编译这段代码时出现了这种类型错误：

```console
$ cargo run
   Compiling patterns v0.1.0 (file:///projects/patterns)
error[E0308]: mismatched types
 --> src/main.rs:2:9
  |
2 |     let (x, y) = (1, 2, 3);
  |         ^^^^^^   --------- this expression has type `({integer}, {integer}, {integer})`
  |         |
  |         expected a tuple with 3 elements, found one with 2 elements
  |
  = note: expected tuple `({integer}, {integer}, {integer})`
             found tuple `(_, _)`

For more information about this error, try `rustc --explain E0308`.
error: could not compile `patterns` (bin "patterns") due to 1 previous error

```

为了修复这个错误，我们可以使用`_`或`..`来忽略元组中的一个或多个值，正如你在[“Ignoring Values in a
Pattern”][ignoring-values-in-a-pattern]<!-- ignore -->部分中看到的那样。如果问题是由于模式中的变量过多导致的，那么解决方案就是通过移除变量来使类型匹配，这样变量的数量就会等于元组中的元素数量。

### 条件式 `if let` 表达式

在第六章中，我们讨论了如何使用 `if let` 表达式，它主要作为一种更简洁的方式来表达 `match` 的等效代码，后者只能匹配一种情况。可选地，当 `if let` 中的模式不匹配时，可以有一个相应的 `if let`，其中包含要执行的代码。

清单19-3展示了，我们还可以混合使用 `if let`、 `else
if` 和 `else if let` 表达式。这样做比使用仅包含一个值的 `match` 表达式提供了更大的灵活性，因为我们可以表达多个值来与模式进行比较。此外，Rust 并不要求一系列 `if
let`、 `else if` 和 `else if let` 条件之间必须相互关联。

清单 19-3 中的代码根据一系列条件检查来确定背景颜色。在这个例子中，我们创建了几个带有硬编码值的变量，这些值可能是真实程序从用户输入中获得的。

**列表 19-3:** *src/main.rs* — 混合了 `if let`、 `else if`、 `else if let` 和 `else`

```rust
fn main() {
    let favorite_color: Option<&str> = None;
    let is_tuesday = false;
    let age: Result<u8, _> = "34".parse();

    if let Some(color) = favorite_color {
        println!("Using your favorite color, {color}, as the background");
    } else if is_tuesday {
        println!("Tuesday is green day!");
    } else if let Ok(age) = age {
        if age > 30 {
            println!("Using purple as the background color");
        } else {
            println!("Using orange as the background color");
        }
    } else {
        println!("Using blue as the background color");
    }
}

```

如果用户指定了喜欢的颜色，那么该颜色将被用作背景颜色。  
如果没有指定喜欢的颜色，且今天是星期二，那么背景颜色将是绿色。否则，如果用户以字符串形式指定了他们的年龄，并且我们能够成功将其解析为数字，那么背景颜色将是紫色或橙色，具体取决于该数字的值。如果以上条件都不适用，那么背景颜色将是蓝色。

这个条件结构使我们能够支持复杂的需求。使用这里硬编码的值，这个例子将会打印出 `Using purple as the
background color`。

可以看到， `if let` 也可以引入新的变量，这些新变量会以与 `match` 相同的方式遮蔽现有的变量。例如， `if let Ok(age) = age` 这一行会引入一个新的 `age` 变量，该变量包含 `Ok` 变体中的值，从而遮蔽现有的 `age` 变量。这意味着我们需要将 `if age >
30` 条件放在该块内：我们不能将这两个条件合并为 `if
let Ok(age) = age && age > 30`。我们想要用来比较的新 `age` 在范围以花括号开始时才有效。

使用 `if let` 表达式的缺点是编译器不会检查其穷尽性，而使用 `match` 表达式时则会进行这样的检查。如果我们省略了最后一个 `else` 块，从而忽略了某些情况的处理，编译器就不会提醒我们可能存在逻辑错误。

### `while let` 条件循环

与 `if let` 的结构类似， `while let` 条件循环允许 `while` 循环在模式持续匹配的情况下继续运行。在 Listing 19-4 中，我们展示了一个 `while let` 循环，该循环会等待线程之间发送的消息，但在这种情况下，它使用的是 `Result` 而不是 `Option` 来进行检查。

<Listing number="19-4" caption="Using a `while let` loop to print values for as long as `rx.recv()` returns `Ok`">

```rust
    let (tx, rx) = std::sync::mpsc::channel();
    std::thread::spawn(move || {
        for val in [1, 2, 3] {
            tx.send(val).unwrap();
        }
    });

    while let Ok(value) = rx.recv() {
        println!("{value}");
    }

```

</Listing>

这个示例会打印出 `1`、 `2`，然后是 `3`。 `recv` 方法会从通道的接收端取出第一条消息，并返回一个 `Ok(value)`。在第十六章中，当我们第一次看到 `recv` 时，我们直接解除了错误，或者使用 `for` 循环来对其进行处理。然而，正如 Listing 19-4 所示，我们也可以使用 `while let`，因为 `recv` 方法在每次有消息到达时都会返回一个 `Ok`，只要发送者存在的话。而当发送端断开连接时，就会生成一个 `Err`。

### 循环结构 `for`

在 `for` 循环中，紧跟在 `for` 关键字之后的值是一个模式。例如，在 `for x in y` 中，`x` 就是该模式。列表 19-5 展示了如何在 `for` 循环中利用模式来分解元组，作为 `for` 循环的一部分。

<Listing number="19-5" caption="Using a pattern in a `for` loop to destructure a tuple">

```rust
    let v = vec!['a', 'b', 'c'];

    for (index, value) in v.iter().enumerate() {
        println!("{value} is at index {index}");
    }

```

</Listing>

清单 19-5 中的代码将输出以下内容：

```console
$ cargo run
   Compiling patterns v0.1.0 (file:///projects/patterns)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.52s
     Running `target/debug/patterns`
a is at index 0
b is at index 1
c is at index 2

```

我们使用 `enumerate` 方法对迭代器进行适配，以便它能够生成一个值以及该值的索引，并将它们组合成一个元组。首先生成的值是元组 `(0, 'a')`。当这个值与模式 `(index,
value)` 匹配时，索引将会是 `0`，而值将会是 `'a'`，此时就会打印出输出的第一行内容。

### 函数参数

函数参数也可以是一种模式。清单19-6中的代码，定义了一个名为 `foo` 的函数，该函数接受一个名为 `x` 的参数，该参数的类型为 `i32`，现在应该看起来比较熟悉了。

<Listing number="19-6" caption="A function signature using patterns in the parameters">

```rust
fn foo(x: i32) {
    // code goes here
}

```

</Listing>

其中的 `x` 部分其实是一个模式！就像我们对 `let` 所做的那样，我们可以在函数参数中匹配一个元组与这个模式。列表19-7展示了在将元组的值传递给函数时，如何将其拆分成多个值。

**清单 19-7:** *src/main.rs* — 一个带有参数的函数，该函数用于解构元组

```rust
fn print_coordinates(&(x, y): &(i32, i32)) {
    println!("Current location: ({x}, {y})");
}

fn main() {
    let point = (3, 5);
    print_coordinates(&point);
}

```

这段代码会输出 `Current location: (3, 5)`。值 `&(3, 5)` 符合模式 `&(x, y)`，因此 `x` 就是值 `3`，而 `y` 就是值 `5`。

我们也可以在闭包参数列表中使用模式，其方式与函数参数列表中的使用方式相同。因为闭包与函数类似，这一点在第十三章中有详细讨论。

到目前为止，你已经看到了几种使用模式的方法，但是模式在我们需要使用它们的各种情况下表现并不相同。在某些情况下，模式必须是不可辩驳的；而在其他情况下，它们则可以被反驳。接下来我们将讨论这两个概念。

[ignoring-values-in-a-pattern]: ch19-03-pattern-syntax.html#ignoring-values-in-a-pattern
