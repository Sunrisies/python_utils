## 参考文献与借用

在 Listing 4-5 中的元组代码中存在的问题是，我们必须将 `String` 返回给调用函数，这样在调用 `calculate_length` 之后，我们仍然可以使用 `String`，因为 `String` 已经被移到了 `calculate_length` 中。相反，我们可以提供一个对 `String` 值的引用。引用就像指针一样，它是一个地址，我们可以通过这个地址来访问存储在该地址的数据；这些数据属于某个其他变量。与指针不同的是，引用在引用存在的时间内始终指向特定类型的有效值。

以下是如何定义和使用一个 `calculate_length` 函数的方法，该函数以对象引用作为参数，而不是直接拥有该值：

<Listing file-name="src/main.rs">

```rust
fn main() {
    // ANCHOR: here
    let s1 = String::from("hello");

    let len = calculate_length(&s1);
    // ANCHOR_END: here

    println!("The length of '{s1}' is {len}.");
}

fn calculate_length(s: &String) -> usize {
    s.len()
}

```

</Listing>

首先，请注意在变量声明和函数返回值中所有的元组代码都消失了。其次，请注意我们将 `&s1` 传递给 `calculate_length`，并且在 `calculate_length` 的定义中，我们使用的是 `&String` 而不是 `String`。这些冒号表示引用，它们允许你引用某个值而不需要拥有该值的所有权。图4-6展示了这个概念。

<img alt="Three tables: the table for s contains only a pointer to the table
for s1. The table for s1 contains the stack data for s1 and points to the
string data on the heap." src="img/trpl04-06.svg" class="center" />

图4-6：一个示意图，展示了 `&String` `s` 指向 `String` `s1` </span> 的布局。

注意：使用 `&` 进行引用的相反操作是 _反引用_，这可以通过反引用运算符 `*` 来实现。我们将在第八章看到一些反引用运算符的用法，并在第十五章中详细讨论反引用的细节。

让我们仔细看看这里的函数调用：

```rust
    let s1 = String::from("hello");

    let len = calculate_length(&s1);

```

`&s1`语法允许我们创建一个引用，该引用_指向`s1`的值，但并不拥有该值。由于引用并不拥有该值，因此当引用不再被使用时，它所指向的值也不会被丢弃。

同样，该函数的签名使用 `&` 来表示参数 `s` 的类型是一个引用。让我们添加一些解释性注释：

```rust
fn calculate_length(s: &String) -> usize { // s is a reference to a String
    s.len()
} // Here, s goes out of scope. But because s does not have ownership of what
  // it refers to, the String is not dropped.

```

变量 `s` 有效的范围与任何函数的参数范围相同，但是当 `s` 不再被使用时，引用所指的值并不会被丢弃，因为 `s` 并不拥有该值的所有权。当函数以引用而非实际值作为参数时，我们不需要返回这些值来归还所有权，因为我们本来就没有拥有该值的权力。

我们将创建引用的行为称为“借用”。就像在现实生活中一样，如果一个人拥有某物，那么你可以从他们那里借用它。借用结束后，你必须归还它。此时，你不再拥有它。

那么，如果我们试图修改我们正在借用的内容会怎么样呢？请尝试使用 Listing 4-6 中的代码。剧透一下：这样做是行不通的！

<Listing number="4-6" file-name="src/main.rs" caption="Attempting to modify a borrowed value">

```rust,ignore,does_not_compile
fn main() {
    let s = String::from("hello");

    change(&s);
}

fn change(some_string: &String) {
    some_string.push_str(", world");
}

```

</Listing>

以下是错误信息：

```console
$ cargo run
   Compiling ownership v0.1.0 (file:///projects/ownership)
error[E0596]: cannot borrow `*some_string` as mutable, as it is behind a `&` reference
 --> src/main.rs:8:5
  |
8 |     some_string.push_str(", world");
  |     ^^^^^^^^^^^ `some_string` is a `&` reference, so the data it refers to cannot be borrowed as mutable
  |
help: consider changing this to be a mutable reference
  |
7 | fn change(some_string: &mut String) {
  |                         +++

For more information about this error, try `rustc --explain E0596`.
error: could not compile `ownership` (bin "ownership") due to 1 previous error

```

正如变量默认是不可变的，引用也是不可变的。我们不允许修改那些被引用到的对象。

### 可变引用

我们可以通过对 Listing 4-6 中的代码进行少量修改，从而允许我们修改被借用的变量。这些修改使用的是 _可变的引用_。

<Listing file-name="src/main.rs">

```rust
fn main() {
    let mut s = String::from("hello");

    change(&mut s);
}

fn change(some_string: &mut String) {
    some_string.push_str(", world");
}

```

</Listing>

首先，我们将 `s` 改为 `mut`。然后，我们创建一个可变引用，该引用指向 `&mut s`，并在其中调用 `change` 函数，同时更新函数的签名，使其能够接受指向 `some_string: &mut String` 的可变引用。这样就能清楚地表明 `change` 函数会修改它所引用的数值。

可变的引用有一个很大的限制：如果你有一个对某个值的可变引用，那么你就不能再有其他对该值的引用。这段代码试图创建两个对 `s` 的可变引用，但会失败。

<Listing file-name="src/main.rs">

```rust,ignore,does_not_compile
    let mut s = String::from("hello");

    let r1 = &mut s;
    let r2 = &mut s;

    println!("{r1}, {r2}");

```

</Listing>

以下是错误信息：

```console
$ cargo run
   Compiling ownership v0.1.0 (file:///projects/ownership)
error[E0499]: cannot borrow `s` as mutable more than once at a time
 --> src/main.rs:5:14
  |
4 |     let r1 = &mut s;
  |              ------ first mutable borrow occurs here
5 |     let r2 = &mut s;
  |              ^^^^^^ second mutable borrow occurs here
6 |
7 |     println!("{r1}, {r2}");
  |                -- first borrow later used here

For more information about this error, try `rustc --explain E0499`.
error: could not compile `ownership` (bin "ownership") due to 1 previous error

```

这个错误提示指出，这段代码无效，因为我们无法在同一时刻多次借用 `s` 这个变量为可变变量。第一次可变变量的借用发生在 `r1` 中，并且必须持续到它在 `println!` 中被使用为止。但在创建那个可变引用之后，我们又尝试在 `r2` 中创建另一个可变引用，而该引用又从 `r1` 中借用相同的数据。

这种限制禁止同时有多个可变引用指向同一数据，这样可以实现修改，但必须以非常可控的方式来进行。这是新学习 Rust 的开发者们难以掌握的地方，因为大多数语言都允许你在任何时候进行修改。设置这种限制的好处是，Rust 可以在编译时防止数据竞争。所谓“数据竞争”，类似于竞态条件，当以下三种情况发生时，就会引发数据竞争：

- 两个或更多的指针同时访问相同的数据。
- 至少有一个指针用于写入数据。
- 没有机制用于同步对数据的访问。

数据竞争会导致未定义的行为，在运行时试图追踪它们时，诊断和修复这些问题可能会非常困难；Rust通过拒绝编译包含数据竞争的代码来避免这个问题！

一如既往，我们可以使用花括号来创建一个新的作用域，从而允许多个可变引用，但只能同时使用其中一个引用：

```rust
    let mut s = String::from("hello");

    {
        let r1 = &mut s;
    } // r1 goes out of scope here, so we can make a new reference with no problems.

    let r2 = &mut s;

```

Rust对组合可变引用和不可变引用也实施了类似的规则。  
这段代码会导致错误：

```rust,ignore,does_not_compile
    let mut s = String::from("hello");

    let r1 = &s; // no problem
    let r2 = &s; // no problem
    let r3 = &mut s; // BIG PROBLEM

    println!("{r1}, {r2}, and {r3}");

```

以下是错误信息：

```console
$ cargo run
   Compiling ownership v0.1.0 (file:///projects/ownership)
error[E0502]: cannot borrow `s` as mutable because it is also borrowed as immutable
 --> src/main.rs:6:14
  |
4 |     let r1 = &s; // no problem
  |              -- immutable borrow occurs here
5 |     let r2 = &s; // no problem
6 |     let r3 = &mut s; // BIG PROBLEM
  |              ^^^^^^ mutable borrow occurs here
7 |
8 |     println!("{r1}, {r2}, and {r3}");
  |                -- immutable borrow later used here

For more information about this error, try `rustc --explain E0502`.
error: could not compile `ownership` (bin "ownership") due to 1 previous error

```

哎呀！当我们对同一个值拥有不可变引用时，我们也无法使用可变的引用。

使用不可变引用的人不会期望数据会突然在他们控制范围之外发生变化！不过，允许多个不可变引用是有原因的，因为仅仅阅读数据的用户无法影响其他用户对数据的读取。

请注意，引用的范围从它被引入的地方开始，一直持续到最后一次使用该引用为止。例如，这段代码可以编译，因为不可变引用的最后一次使用是在 `println!` 中，而在可变引用被引入之前。

```rust
    let mut s = String::from("hello");

    let r1 = &s; // no problem
    let r2 = &s; // no problem
    println!("{r1} and {r2}");
    // Variables r1 and r2 will not be used after this point.

    let r3 = &mut s; // no problem
    println!("{r3}");

```

不可变引用`r1`和`r2`的作用域在`println!`之后结束。它们最后一次被使用的位置是在可变引用`r3`被创建之前。这些作用域是不重叠的，因此这段代码是允许的：编译器能够判断出该引用在作用域结束之前就已经不再被使用了。

尽管借用错误有时可能会让人感到沮丧，但请记住，是Rust编译器在编译时指出潜在的错误，并明确指出问题的具体位置。这样，你就无需去追踪为什么数据并不像你想象的那样了。

### 悬空引用

在支持指针的语言中，很容易因为释放某些内存而错误地创建“悬空指针”——即指向可能已经分配给其他人的内存位置的指针。相比之下，在Rust中，编译器保证引用永远不会成为悬空引用：如果你有对某数据的引用，编译器会确保在引用该数据之前，该数据不会超出作用域。

让我们尝试创建一个悬空引用，看看Rust是如何通过编译时错误来防止这种情况发生的：

<Listing file-name="src/main.rs">

```rust,ignore,does_not_compile
fn main() {
    let reference_to_nothing = dangle();
}

fn dangle() -> &String {
    let s = String::from("hello");

    &s
}

```

</Listing>

以下是错误信息：

```console
$ cargo run
   Compiling ownership v0.1.0 (file:///projects/ownership)
error[E0106]: missing lifetime specifier
 --> src/main.rs:5:16
  |
5 | fn dangle() -> &String {
  |                ^ expected named lifetime parameter
  |
  = help: this function's return type contains a borrowed value, but there is no value for it to be borrowed from
help: consider using the `'static` lifetime, but this is uncommon unless you're returning a borrowed value from a `const` or a `static`
  |
5 | fn dangle() -> &'static String {
  |                 +++++++
help: instead, you are more likely to want to return an owned value
  |
5 - fn dangle() -> &String {
5 + fn dangle() -> String {
  |

For more information about this error, try `rustc --explain E0106`.
error: could not compile `ownership` (bin "ownership") due to 1 previous error

```

这条错误消息涉及了一个我们尚未讨论的特性：生命周期。我们将在第十章中详细讨论生命周期。不过，如果你忽略关于生命周期的部分，这条消息仍然包含了为什么这段代码存在问题的关键所在。

```text
this function's return type contains a borrowed value, but there is no value
for it to be borrowed from
```

让我们更仔细地看看我们的`dangle`代码在每个阶段到底发生了什么。

<Listing file-name="src/main.rs">

```rust,ignore,does_not_compile
fn dangle() -> &String { // dangle returns a reference to a String

    let s = String::from("hello"); // s is a new String

    &s // we return a reference to the String, s
} // Here, s goes out of scope and is dropped, so its memory goes away.
  // Danger!

```

</Listing>

因为 `s` 是在 `dangle` 内部创建的，当 `dangle` 的代码完成之后，`s` 将会被释放内存。但是，我们试图返回一个对它的引用。这意味着这个引用会指向一个无效的 `String`。这可不行！Rust 不允许我们这样做。

这里的解决方案是直接返回 `String`。

```rust
fn no_dangle() -> String {
    let s = String::from("hello");

    s
}

```

这个操作没有任何问题。所有权已经转移出去，而且没有任何内存被释放。

### 引用规则

让我们回顾一下我们关于引用所讨论的内容：

- 在任何时候，你可以拥有一个可变引用，或者任意数量的不可变引用。
- 引用必须始终有效。

接下来，我们将介绍另一种引用方式：切片。