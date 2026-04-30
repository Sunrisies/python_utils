## 使用 `if let` 和 `let...else` 实现简洁的控制流

`if let` 语法允许你将 `if` 和 `let` 结合起来，以一种更简洁的方式处理那些符合某个模式的值，同时忽略其余的值。请参考清单 6-6 中的程序，该程序会在 `config_max` 变量中查找符合 `Option<u8>` 的值，但只有当该值是 `Some` 变体时才会执行代码。

<Listing number="6-6" caption="A `match` that only cares about executing code when the value is `Some`">

```rust
    let config_max = Some(3u8);
    match config_max {
        Some(max) => println!("The maximum is configured to be {max}"),
        _ => (),
    }

```

</Listing>

如果值为 `Some`，我们通过将值绑定到模式中的变量 `max`，从而输出 `Some` 变体中的值。我们不想对 `None` 值进行任何操作。为了满足 `match` 表达式，我们需要在处理其中一个变体后添加 `_ =>
()`，这会增加烦人的样板代码。

相反，我们可以使用 `if let` 来更简洁地表达这一内容。以下代码与 Listing 6-6 中的 `match` 行为相同：

```rust
    let config_max = Some(3u8);
    if let Some(max) = config_max {
        println!("The maximum is configured to be {max}");
    }

```

语法 `if let` 接受一个模式和一个由等号分隔的表达式。它的工作方式与 `match` 类似，其中表达式被传递给 `match`，而模式则是 `match` 的第一个分支。在这种情况下，模式是 `Some(max)`，而 `max` 则绑定到 `Some` 内部的值。然后，我们可以像在 `max` 中使用的那样，在 `if let` 块的主体中使用 `max`，就像在相应的 `match` 分支中使用的 `max` 一样。只有当值与模式匹配时， `if let` 块中的代码才会执行。

使用 `if let` 可以节省输入代码、减少缩进，并减少样板代码。不过，这种写法会失去详尽的检查功能，而 `match` 则能确保不会遗漏任何情况的处理。在 `match` 和 `if
let` 之间选择，取决于你在特定情况下的具体需求，以及是否认为简洁性提升是牺牲详尽检查功能的合理权衡。

换句话说，你可以将 `if let` 视为一个 `match` 的语法糖，它会在某个值符合某个模式时执行代码，而忽略所有其他值。

我们可以包含一个 `else`，并且还有一个 `if let`。与 `else` 一起出现的代码块，与 `_` 情况下的 `match` 表达式中的代码块是相同的，而 `match` 表达式则等同于 `if let` 和 `else`。请回想一下 Listing 6-4 中的 `Coin` 枚举定义，其中 `Quarter` 变体也持有一个 `UsState` 值。如果我们想要统计所有非 quarter 硬币的数量，同时告知 quarter 硬币的状态，我们可以使用 `match` 表达式来实现这一点。

```rust
    let mut count = 0;
    match coin {
        Coin::Quarter(state) => println!("State quarter from {state:?}!"),
        _ => count += 1,
    }

```

或者我们可以使用这样的`if let`和`else`表达式：

```rust
    let mut count = 0;
    if let Coin::Quarter(state) = coin {
        println!("State quarter from {state:?}!");
    } else {
        count += 1;
    }

```

## 保持“幸福之路”上的`let...else`

常见的模式是在某个值存在时执行某些计算，而在其他情况下返回默认值。以我们关于硬币的例子为例，如果某个硬币的`UsState`值为真，我们想根据硬币上的状态的年龄来输出一些有趣的信息，那么我们可以为`UsState`状态引入一个方法来检查该状态的年龄，如下所示：

```rust
impl UsState {
    fn existed_in(&self, year: u16) -> bool {
        match self {
            UsState::Alabama => year >= 1819,
            UsState::Alaska => year >= 1959,
            // -- snip --
        }
    }
}

```

然后，我们可以使用 `if let` 来匹配硬币的类型，并在条件的主体中引入一个 `state` 变量，如清单 6-7 所示。

<Listing number="6-7" caption="Checking whether a state existed in 1900 by using conditionals nested inside an `if let`">

```rust
fn describe_state_quarter(coin: Coin) -> Option<String> {
    if let Coin::Quarter(state) = coin {
        if state.existed_in(1900) {
            Some(format!("{state:?} is pretty old, for America!"))
        } else {
            Some(format!("{state:?} is relatively new."))
        }
    } else {
        None
    }
}

```

</Listing>

这种方法确实可以完成任务，但是它将代码块挤到了 `if
let` 语句的主体部分。如果需要完成的工作更为复杂，那么很难准确理解各个顶层分支之间的关系。我们还可以利用表达式能够生成值的特点，从而生成 `state`，或者像 Listing 6-8 中那样提前返回结果。（对于 `match` 也可以采用类似的方法。）

<Listing number="6-8" caption="Using `if let` to produce a value or return early">

```rust
fn describe_state_quarter(coin: Coin) -> Option<String> {
    let state = if let Coin::Quarter(state) = coin {
        state
    } else {
        return None;
    };

    if state.existed_in(1900) {
        Some(format!("{state:?} is pretty old, for America!"))
    } else {
        Some(format!("{state:?} is relatively new."))
    }
}

```

</Listing>

不过，这种处理方式确实有点麻烦！其中一个分支会返回一个值，而另一个分支则完全从函数中返回结果。

为了使得这种常见的模式更易于表达，Rust提供了 `let...else` 这种语法。`let...else` 这种语法左边是一个模式，右边是一个表达式，与 `if let` 非常相似，但是 `let...else` 没有 `if` 这个分支，只有 `else` 这个分支。如果模式匹配，那么模式中的值将会被绑定到外部作用域中。如果模式不匹配，程序将会进入 `else` 这个分支，而该分支必须从函数中返回。

在 Listing 6-9 中，你可以看到当使用 `let...else` 代替 `if let` 时，Listing 6-8 的显示效果。

<Listing number="6-9" caption="Using `let...else` to clarify the flow through the function">

```rust
fn describe_state_quarter(coin: Coin) -> Option<String> {
    let Coin::Quarter(state) = coin else {
        return None;
    };

    if state.existed_in(1900) {
        Some(format!("{state:?} is pretty old, for America!"))
    } else {
        Some(format!("{state:?} is relatively new."))
    }
}

```

</Listing>

请注意，通过这种方式，函数主体始终保持在“正常路径”上，两个分支的控制流程并没有发生显著的变化，这与 `if let` 的方式是一致的。

如果你遇到这样的情况：你的程序中的逻辑过于冗长，无法用 `match` 来表达，那么请记住， `if let` 和 `let...else` 也是你的 Rust 工具箱中的工具。

## 摘要

我们现在已经了解了如何使用枚举来创建自定义类型，这些类型可以表示从一组枚举值中选择的一个值。我们还展示了标准库中的 `Option<T>` 类型如何帮助你利用类型系统来避免错误。当枚举值包含数据时，你可以根据需要处理的情况，使用 `match` 或 `if let` 来提取并使用这些数据。

现在，你的Rust程序可以使用结构体和数据类型来表达你所在领域中的概念。在API中创建自定义类型可以确保类型安全：编译器会确保你的函数只能接收每个函数所期望的类型的值。

为了为用户提供一个组织良好的API，使其使用起来非常直观，并且只暴露用户真正需要的功能，现在让我们来了解一下Rust中的模块。