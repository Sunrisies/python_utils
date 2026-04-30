## 变量与可变性

如[“使用变量存储值”][storing-values-with-variables]<!-- ignore -->章节所述，默认情况下，变量是不可变的。这是Rust提供的一种机制，旨在帮助你以充分利用Rust所提供的安全性和便捷并发性的方式编写代码。不过，你仍然可以选择使变量成为可变的。接下来，我们将探讨Rust为何鼓励你使用不可变性，以及为什么有时你可能需要选择使用可变变量。

当某个变量是不可变的时，一旦某个值被绑定到一个名称上，就无法再改变该值。为了说明这一点，请使用 `cargo new variables` 在 _projects_ 目录下创建一个新的项目，命名为 _variables_。

然后，在你的新的`_variables_`目录下，打开`_src/main.rs_`文件，并用以下代码替换其中的代码。不过，目前这段代码是无法编译的：

<span class="filename"> 文件名: src/main.rs</span>

```rust,ignore,does_not_compile
fn main() {
    let x = 5;
    println!("The value of x is: {x}");
    x = 6;
    println!("The value of x is: {x}");
}

```

使用 `cargo run` 保存并运行该程序。你应该会收到一个关于不可变性错误的错误消息，如下所示：

```console
$ cargo run
   Compiling variables v0.1.0 (file:///projects/variables)
error[E0384]: cannot assign twice to immutable variable `x`
 --> src/main.rs:4:5
  |
2 |     let x = 5;
  |         - first assignment to `x`
3 |     println!("The value of x is: {x}");
4 |     x = 6;
  |     ^^^^^ cannot assign twice to immutable variable
  |
help: consider making this binding mutable
  |
2 |     let mut x = 5;
  |         +++

For more information about this error, try `rustc --explain E0384`.
error: could not compile `variables` (bin "variables") due to 1 previous error

```

这个例子展示了编译器如何帮助您发现程序中的错误。编译器错误可能会让人感到沮丧，但实际上，这些错误只是意味着您的程序还没有能够安全地执行您期望它做的事情；它们并不意味着您不是一个优秀的程序员！经验丰富的Rust开发者仍然会遇到编译器错误。

您收到了以下错误信息：`` cannot assign twice to immutable variable `x` `` because you tried to assign a second value to the immutable `x` variable.

It’s important that we get compile-time errors when we attempt to change a
value that’s designated as immutable, because this very situation can lead to
bugs. If one part of our code operates on the assumption that a value will
never change and another part of our code changes that value, it’s possible
that the first part of the code won’t do what it was designed to do. The cause
of this kind of bug can be difficult to track down after the fact, especially
when the second piece of code changes the value only _sometimes_. The Rust
compiler guarantees that when you state that a value won’t change, it really
won’t change, so you don’t have to keep track of it yourself. Your code is thus
easier to reason through.

But mutability can be very useful and can make code more convenient to write.
Although variables are immutable by default, you can make them mutable by
adding `mut` in front of the variable name as you did in [Chapter
2][storing-values-with-variables]<!-- ignore -->. Adding `mut` also conveys
intent to future readers of the code by indicating that other parts of the code
will be changing this variable’s value.

For example, let’s change _src/main.rs_ to the following:

<span class="filename">Filename: src/main.rs</span>

```rust
fn main() {
    let mut x = 5;
    println!("The value of x is: {x}");
    x = 6;
    println!("The value of x is: {x}");
}

```

When we run the program now, we get this:

```console
$ cargo run
   Compiling variables v0.1.0 (file:///projects/variables)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.30s
     Running `target/debug/variables`
The value of x is: 5
The value of x is: 6

```

We’re allowed to change the value bound to `x` from `5` to `6` when `mut` is
used. Ultimately, deciding whether to use mutability or not is up to you and
depends on what you think is clearest in that particular situation.

<!-- Old headings. Do not remove or links may break. -->
<a id="constants"></a>

### Declaring Constants

Like immutable variables, _constants_ are values that are bound to a name and
are not allowed to change, but there are a few differences between constants
and variables.

First, you aren’t allowed to use `mut` with constants. Constants aren’t just
immutable by default—they’re always immutable. You declare constants using the
`const` keyword instead of the `let` keyword, and the type of the value _must_
be annotated. We’ll cover types and type annotations in the next section,
[“Data Types”][data-types]<!-- ignore -->, so don’t worry about the details
right now. Just know that you must always annotate the type.

Constants can be declared in any scope, including the global scope, which makes
them useful for values that many parts of code need to know about.

The last difference is that constants may be set only to a constant expression,
not the result of a value that could only be computed at runtime.

Here’s an example of a constant declaration:

```rust
const THREE_HOURS_IN_SECONDS: u32 = 60 * 60 * 3;
```

The constant’s name is `THREE_HOURS_IN_SECONDS⊃PH13⊃let` keyword as follows:

<span class="filename">Filename: src/main.rs</span>

```rust
fn main() {
    let x = 5;

    let x = x + 1;

    {
        let x = x * 2;
        println!("The value of x in the inner scope is: {x}");
    }

    println!("The value of x is: {x}");
}

```

This program first binds `x` to a value of `5`. Then, it creates a new variable
`x` by repeating `let x =`, taking the original value and adding `1` so that
the value of `x` is `6`. Then, within an inner scope created with the curly
brackets, the third `let` statement also shadows `x` and creates a new
variable, multiplying the previous value by `2` to give `x` a value of `12`.
When that scope is over, the inner shadowing ends and `x` returns to being `6`.
When we run this program, it will output the following:

```console
$ cargo run
   Compiling variables v0.1.0 (file:///projects/variables)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.31s
     Running `target/debug/variables`
The value of x in the inner scope is: 12
The value of x is: 6

```

Shadowing is different from marking a variable as `mut` because we’ll get a
compile-time error if we accidentally try to reassign to this variable without
using the `let` keyword. By using `let`, we can perform a few transformations
on a value but have the variable be immutable after those transformations have
completed.

The other difference between `mut` and shadowing is that because we’re
effectively creating a new variable when we use the `let` keyword again, we can
change the type of the value but reuse the same name. For example, say our
program asks a user to show how many spaces they want between some text by
inputting space characters, and then we want to store that input as a number:

```rust
    let spaces = "   ";
    let spaces = spaces.len();

```

The first `spaces` variable is a string type, and the second `spaces` variable
is a number type. Shadowing thus spares us from having to come up with
different names, such as `spaces_str` and `spaces_num`; instead, we can reuse
the simpler `spaces` name. However, if we try to use `mut`。出现此错误的原因如下：

```rust,ignore,does_not_compile
    let mut spaces = "   ";
    spaces = spaces.len();

```

错误信息提示我们不允许修改变量的类型。

```console
$ cargo run
   Compiling variables v0.1.0 (file:///projects/variables)
error[E0308]: mismatched types
 --> src/main.rs:3:14
  |
2 |     let mut spaces = "   ";
  |                      ----- expected due to this value
3 |     spaces = spaces.len();
  |              ^^^^^^^^^^^^ expected `&str`, found `usize`

For more information about this error, try `rustc --explain E0308`.
error: could not compile `variables` (bin "variables") due to 1 previous error

```

既然我们已经了解了变量的工作原理，接下来让我们看看它们还可以拥有哪些数据类型。

[comparing-the-guess-to-the-secret-number]: ch02-00-guessing-game-tutorial.html#comparing-the-guess-to-the-secret-number
[data-types]: ch03-02-data-types.html#data-types
[storing-values-with-variables]: ch02-00-guessing-game-tutorial.html#storing-values-with-variables
[const-eval]: ../reference/const_eval.html
