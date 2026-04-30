## 可证伪性：某种模式是否可能无法匹配

模式有两种形式：可反驳的和不可反驳的。对于那些在传递任何可能的值时都能匹配的模式，被称为“不可反驳的”。例如，在语句 `let x = 5;` 中，模式 `x` 可以匹配任何值，因此必然能够匹配。而那些在某些可能的值下可能无法匹配的模式，则被称为“可反驳的”。例如，在表达式 `if let Some(x) =
a_value` 中，如果变量 `a_value` 中的值不是 `Some`，而是 `None`，那么模式 `Some(x)` 就不会匹配。

函数参数、`let`语句和`for`循环只能接受不可辩驳的模式，因为当值不匹配时，程序无法执行任何有意义的操作。`if let`和`while let`表达式以及`let...else`语句可以接受不可辩驳和不可辩驳的模式，但编译器会警告不要使用不可辩驳的模式，因为根据定义，这些模式是为了处理可能的失败情况：条件语句的功能在于能够根据成功或失败的情况而采取不同的行为。

一般来说，你不必担心可反驳模式与不可反驳模式之间的区别。不过，你需要熟悉可反驳性的概念，这样当你在错误信息中看到这个概念时，就能做出相应的回应。在这种情况下，你需要根据代码的预期行为，选择修改模式本身或与之结合使用的构造方式。

让我们来看一个例子，当尝试使用可反驳的模式时会发生什么。在Rust中，需要不可反驳的模式，反之亦然。列表19-8展示了一个`let`语句，但作为模式，我们指定了 `Some(x)`，这是一个可反驳的模式。正如你所预期的，这段代码将无法编译。

<Listing number="19-8" caption="Attempting to use a refutable pattern with `let`">

```rust,ignore,does_not_compile
    let Some(x) = some_option_value;

```

</Listing>

如果 `some_option_value` 是一个 `None` 值，那么它将无法匹配模式 `Some(x)`，这意味着该模式是可反驳的。然而， `let` 语句只能接受不可反驳的模式，因为代码无法对 `None` 值进行任何有效的操作。在编译时，Rust 会报错，提示我们试图使用一个需要不可反驳模式的模式，但实际上却使用了可反驳的模式。

```console
$ cargo run
   Compiling patterns v0.1.0 (file:///projects/patterns)
error[E0005]: refutable pattern in local binding
 --> src/main.rs:3:9
  |
3 |     let Some(x) = some_option_value;
  |         ^^^^^^^ pattern `None` not covered
  |
  = note: `let` bindings require an "irrefutable pattern", like a `struct` or an `enum` with only one variant
  = note: for more information, visit https://doc.rust-lang.org/book/ch19-02-refutability.html
  = note: the matched value is of type `Option<i32>`
help: you might want to use `let else` to handle the variant that isn't matched
  |
3 |     let Some(x) = some_option_value else { todo!() };
  |                                     ++++++++++++++++

For more information about this error, try `rustc --explain E0005`.
error: could not compile `patterns` (bin "patterns") due to 1 previous error

```

因为我们无法涵盖所有有效的 `pattern `Some(x)`` 值，所以 Rust 自然会产生编译错误。

如果我们有一个可反驳的模式，而我们需要一个不可反驳的模式，我们可以通过修改使用该模式的代码来解决这个问题：与其使用 `let`，我们可以使用 `let...else`。这样，如果模式不匹配，花括号中的代码就会处理该值。列表19-9展示了如何修改列表19-8中的代码。

<Listing number="19-9" caption="Using `let...else` and a block with refutable patterns instead of `let`">

```rust
    let Some(x) = some_option_value else {
        return;
    };

```

</Listing>

我们为这段代码提供了出路！这段代码是完全有效的，不过这意味着我们不能使用一种无可辩驳的模式，而不收到警告。如果我们为`let...else`提供一个总是会匹配的模式，比如 `x`，如清单19-10所示，编译器将会发出警告。

<Listing number="19-10" caption="Attempting to use an irrefutable pattern with `let...else`">

```rust
    let x = 5 else {
        return;
    };

```

</Listing>

Rust 会指出，使用 `let...else` 与不可辩驳的模式是毫无意义的：

```console
$ cargo run
   Compiling patterns v0.1.0 (file:///projects/patterns)
warning: irrefutable `let...else` pattern
 --> src/main.rs:2:5
  |
2 |     let x = 5 else {
  |     ^^^^^^^^^
  |
  = note: this pattern will always match, so the `else` clause is useless
  = help: consider removing the `else` clause
  = note: `#[warn(irrefutable_let_patterns)]` on by default

warning: `patterns` (bin "patterns") generated 1 warning
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.39s
     Running `target/debug/patterns`

```

因此，匹配臂必须使用可证伪的模式，除了最后一个臂，它应该使用不可证伪的模式来匹配任何剩余的值。Rust允许我们在只有一个臂的 `match` 中使用不可证伪的模式，但这种语法并不是特别有用，可以用更简单的 `let` 语句来替代。

现在你已经知道在何处使用模式，以及可反驳模式和不可反驳模式之间的区别，那么让我们来了解一下可以用来创建模式的所有语法。