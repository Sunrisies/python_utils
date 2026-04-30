## 高级函数和闭包

本节探讨了与函数和闭包相关的一些高级特性，包括函数指针和返回闭包。

### 函数指针

我们已经讨论过如何将闭包传递给函数；你也可以将普通函数传递给函数！这种技术在你想要传递已经定义好的函数时非常有用，而不是需要重新定义一个新的闭包。函数类型被强制为 `fn` 类型（使用小写的 _f_ 表示），不要与 `Fn` 闭包特性混淆。这种类型被称为 _函数指针_。通过函数指针传递函数，你可以将函数作为其他函数的参数来使用。

指定一个参数是函数指针的语法与闭包的语法类似，如清单20-28所示。在这里，我们定义了一个函数 `add_one`，该函数将其参数加1。函数 `do_twice` 接受两个参数：一个指向任何接受参数 `i32` 的函数且返回 `i32` 值的函数指针，以及一个 `i32` 值。函数 `do_twice` 会两次调用函数 `f`，并将 `arg` 值传递给它，然后将这些函数调用结果相加。函数 `main` 会使用参数 `add_one` 和 `5` 来调用函数 `do_twice`。

**清单 20-28:** *src/main.rs* — 使用 `fn` 类型来接受函数指针作为参数

```rust
fn add_one(x: i32) -> i32 {
    x + 1
}

fn do_twice(f: fn(i32) -> i32, arg: i32) -> i32 {
    f(arg) + f(arg)
}

fn main() {
    let answer = do_twice(add_one, 5);

    println!("The answer is: {answer}");
}

```

这段代码会输出 `The answer is: 12`。我们指定 `do_twice` 中的参数 `f` 是一个接受类型为 `i32` 的参数的 `fn`，并且返回一个 `i32`。然后我们可以在 `do_twice` 的主体中调用 `f`。在 `main` 中，我们可以将函数名 `add_one` 作为第一个参数传递给 `do_twice`。

与闭包不同， `fn` 是一种类型，而不是一种特质。因此，我们直接指定 `fn` 作为参数类型，而不是使用 `Fn` 特质中的某个作为特质绑定来声明一个通用类型参数。

函数指针实现了所有三种闭包特性（`Fn`、`FnMut`和`FnOnce`），这意味着你可以始终将函数指针作为参数传递给那些需要闭包的函数。最好使用通用类型以及其中一种闭包特性来编写函数，这样你的函数就可以接受函数或闭包。

不过，有一个例子说明为什么只接受 `fn` 而不接受闭包是：在与没有闭包的外部代码交互时。C 语言的函数可以接受其他函数作为参数，但 C 语言本身并不支持闭包。

作为使用内联定义的闭包或命名函数的例子，让我们来看一个标准库中 `Iterator` 特质提供的 `map` 方法的应用。为了使用 `map` 方法将数字向量转换为字符串向量，我们可以使用闭包，如清单 20-29 所示。

<Listing number="20-29" caption="Using a closure with the `map` method to convert numbers to strings">

```rust
    let list_of_numbers = vec![1, 2, 3];
    let list_of_strings: Vec<String> =
        list_of_numbers.iter().map(|i| i.to_string()).collect();

```

</Listing>

或者，我们可以将某个函数作为 `map` 的参数，而不是闭包。列表 20-30 展示了这种方式的实现效果。

<Listing number="20-30" caption="Using the `String::to_string` function with the `map` method to convert numbers to strings">

```rust
    let list_of_numbers = vec![1, 2, 3];
    let list_of_strings: Vec<String> =
        list_of_numbers.iter().map(ToString::to_string).collect();

```

</Listing>

请注意，我们必须使用在[“Advanced Traits”][advanced-traits]<!-- ignore -->部分提到的完全限定语法，因为存在多个名为⊃`to_string`的函数可供使用。

在这里，我们使用在 `ToString` trait 中定义的函数 `to_string`，标准库已经为任何实现了 `Display` 的类型实现了这个函数。

请回想一下第6章中 [“Enum Values”][enum-values]<!-- ignore --> 部分的内容。我们定义的每个枚举变体的名称也成为了初始化函数。我们可以将这些初始化函数用作函数指针，从而实现闭包特性。这意味着我们可以将初始化函数作为接受闭包的方法的参数，如清单20-31所示。

<Listing number="20-31" caption="Using an enum initializer with the `map` method to create a `Status` instance from numbers">

```rust
    enum Status {
        Value(u32),
        Stop,
    }

    let list_of_statuses: Vec<Status> = (0u32..20).map(Status::Value).collect();

```

</Listing>

在这里，我们使用范围内的每个 `u32` 值来创建 `Status::Value` 实例。这些 `map` 对象是通过使用 `Status::Value` 的初始化器函数来调用的。有些人更喜欢这种风格，而有些人则更喜欢使用闭包。实际上，这两种方式编译出来的代码是相同的，因此你可以选择对你来说更清晰的方式。

### 返回闭包

闭包是通过特质来表示的，这意味着你不能直接返回闭包。在大多数情况下，如果你想返回一个特质，你可以将实现该特质的具体类型作为函数的返回值。然而，对于闭包来说，通常不能这样做，因为闭包没有可以返回的具体类型；例如，如果闭包捕获了其作用域中的任何值，那么你就不能将函数指针 `fn` 作为返回类型。

相反，你通常会使用我们在第10章中学到的 `impl Trait` 语法。你可以使用 `Fn`、 `FnOnce` 和 `FnMut` 来返回任何函数类型。例如，清单20-32中的代码将会正常编译。

<Listing number="20-32" caption="Returning a closure from a function using the `impl Trait` syntax">

```rust
fn returns_closure() -> impl Fn(i32) -> i32 {
    |x| x + 1
}

```

</Listing>

然而，正如我们在第13章的 [“Inferring and Annotating Closure
Types”][closure-types]<!-- ignore --> 部分所指出的，每个闭包本身也是其独特的类型。如果你需要处理多个具有相同签名但实现不同的函数，那么你需要使用特质对象来管理它们。想象一下，如果你编写了如清单20-33所示的代码，会发生什么情况。

<Listing file-name="src/main.rs" number="20-33" caption="Creating a `Vec<T>` of closures defined by functions that return `impl Fn` types">

```rust,ignore,does_not_compile
fn main() {
    let handlers = vec![returns_closure(), returns_initialized_closure(123)];
    for handler in handlers {
        let output = handler(5);
        println!("{output}");
    }
}

fn returns_closure() -> impl Fn(i32) -> i32 {
    |x| x + 1
}

fn returns_initialized_closure(init: i32) -> impl Fn(i32) -> i32 {
    move |x| x + init
}

```

</Listing>

这里有两个函数，分别是 `returns_closure` 和 `returns_initialized_closure`，这两个函数都返回 `impl Fn(i32) -> i32`。请注意，尽管它们实现了相同的类型，但返回的闭包是不同的。如果我们尝试编译这些代码，Rust 会告诉我们这是不可行的。

```text
$ cargo build
   Compiling functions-example v0.1.0 (file:///projects/functions-example)
error[E0308]: mismatched types
  --> src/main.rs:2:44
   |
 2 |     let handlers = vec![returns_closure(), returns_initialized_closure(123)];
   |                                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ expected opaque type, found a different opaque type
...
 9 | fn returns_closure() -> impl Fn(i32) -> i32 {
   |                         ------------------- the expected opaque type
...
13 | fn returns_initialized_closure(init: i32) -> impl Fn(i32) -> i32 {
   |                                              ------------------- the found opaque type
   |
   = note: expected opaque type `impl Fn(i32) -> i32`
              found opaque type `impl Fn(i32) -> i32`
   = note: distinct uses of `impl Trait` result in different opaque types

For more information about this error, try `rustc --explain E0308`.
error: could not compile `functions-example` (bin "functions-example") due to 1 previous error

```

错误信息告诉我们，每当我们返回 `impl Trait` 时，Rust 会创建一个独特的 _opaque 类型_。在这种类型中，我们无法了解 Rust 为我们构建的具体实现细节，也无法猜测 Rust 会生成什么样的类型以便我们自己进行编写。因此，尽管这些函数返回的闭包实现了相同的 trait `Fn(i32) -> i32`，但 Rust 为每种情况生成的 opaque 类型是不同的。（这与 Rust 为不同的异步块生成不同的具体类型的方式类似，就像我们在第 17 章中的 [“The `Pin` Type and the `Unpin` Trait”][future-types]<!-- ignore --> 中看到的那样。）我们已经多次看到解决这个问题的办法：我们可以使用 trait 对象，如 Listing 20-34 所示。

<Listing number="20-34" caption="Creating a `Vec<T>` of closures defined by functions that return `Box<dyn Fn>` so that they have the same type">

```rust
fn returns_closure() -> Box<dyn Fn(i32) -> i32> {
    Box::new(|x| x + 1)
}

fn returns_initialized_closure(init: i32) -> Box<dyn Fn(i32) -> i32> {
    Box::new(move |x| x + init)
}

```

</Listing>

这段代码可以正常编译。关于 trait 对象，更多内容请参阅第18章中的 [“Using Trait Objects To Abstract over Shared
Behavior”][trait-objects]<!-- ignore --> 部分。

接下来，让我们来看看宏！

[advanced-traits]: ch20-02-advanced-traits.html#advanced-traits
[enum-values]: ch06-01-defining-an-enum.html#enum-values
[closure-types]: ch13-01-closures.html#closure-type-inference-and-annotation
[future-types]: ch17-03-more-futures.html
[trait-objects]: ch18-02-trait-objects.html
