<!-- Old headings. Do not remove or links may break. -->

<a id="the-match-control-flow-operator"></a>

## `match` 控制流构造

Rust 拥有一个非常强大的控制流结构，称为 `match`。它允许你将一个值与一系列模式进行比较，然后根据匹配到的模式来执行相应的代码。这些模式可以包含字面值、变量名、通配符等多种元素；[第19章][ch19-00-patterns]<!-- ignore --> 详细介绍了各种模式及其功能。 `match` 的强大之处在于其模式的表达能力，以及编译器能够确保所有可能的情况都被处理。

可以将 `match` 表达式想象成一个硬币分类机：硬币沿着一条带有不同大小孔洞的轨道下滑，每枚硬币会掉入第一个符合其尺寸的孔洞中。同样地，值也会通过 `match` 中的每个模式，当值符合某个模式时，它就会落入相应的代码块中，并在执行时被使用。

说到硬币，我们就以 `match`! 为例来演示一下。我们可以编写一个函数，该函数接收一个未知的美国硬币，然后像计数机一样，确定硬币的种类，并返回其价值，以美分为单位，如清单 6-3 所示。

<Listing number="6-3" caption="An enum and a `match` expression that has the variants of the enum as its patterns">

```rust
enum Coin {
    Penny,
    Nickel,
    Dime,
    Quarter,
}

fn value_in_cents(coin: Coin) -> u8 {
    match coin {
        Coin::Penny => 1,
        Coin::Nickel => 5,
        Coin::Dime => 10,
        Coin::Quarter => 25,
    }
}

```

</Listing>

让我们来分析一下 `value_in_cents` 函数中的 `match` 部分。首先，我们看到的是 `match` 这个关键字，后面跟着一个表达式，在这个例子中，这个表达式就是值 `coin`。这看起来很类似于与 `if` 一起使用的条件表达式，但实际上有很大的区别：在 `if` 中，条件需要被评估为一个布尔值，而在这里，条件可以是任何类型。在这个例子中， `coin` 的类型就是我们在第一行定义的 `Coin` 枚举类型。

接下来是 `match` 这个分支。一个分支包含两部分：一个模式和一些代码。这里的第一个分支有一个模式，即值 `Coin::Penny`，然后是一个 `=>` 运算符，用于分隔模式和要执行的代码。在这种情况下，代码就是值 `1`。每个分支通过逗号与下一个分支分隔开来。

当 `match` 表达式执行时，它会依次将结果值与每个分支的模式进行比较。如果某个模式与值匹配，那么与该模式相关的代码就会被执行。如果某个模式与值不匹配，那么执行将继续到下一个分支，就像在硬币分类机中一样。我们可以根据需要设置任意多个分支：在 Listing 6-3 中，我们的 `match` 有四个分支。

与每个分支相关的代码都是一个表达式，而在匹配分支中该表达式的结果值，就是整个 `match` 表达式所返回的值。

如果匹配分支的代码较短，我们通常不会使用花括号。正如清单6-3所示，每个分支仅返回一个值。如果你想在匹配分支中运行多行代码，就必须使用花括号，而分支后面的逗号则不是必需的。例如，以下代码在每次方法被调用时都会打印“Lucky penny!”，但它仍然会返回该代码块中的最后一个值：⊃。

```rust
fn value_in_cents(coin: Coin) -> u8 {
    match coin {
        Coin::Penny => {
            println!("Lucky penny!");
            1
        }
        Coin::Nickel => 5,
        Coin::Dime => 10,
        Coin::Quarter => 25,
    }
}

```

### 与值相关联的模式

Match Arms的另一个有用特性是，它们可以绑定到与模式匹配的值部分。通过这种方式，我们可以从枚举变体中提取出相应的值。

例如，让我们修改其中一个枚举变体，以在其内部存储数据。从1999年到2008年，美国为50个州各自铸造了不同设计的25美分硬币。没有其他硬币具有州特定的设计，因此只有25美分硬币具有这种额外价值。我们可以通过修改 `Quarter` 变体来添加这些信息，使其内部存储一个 `UsState` 值，正如我们在清单6-4中所做的那样。

<Listing number="6-4" caption="A `Coin` enum in which the `Quarter` variant also holds a `UsState` value">

```rust
#[derive(Debug)] // so we can inspect the state in a minute
enum UsState {
    Alabama,
    Alaska,
    // --snip--
}

enum Coin {
    Penny,
    Nickel,
    Dime,
    Quarter(UsState),
}

```

</Listing>

让我们想象一个朋友正在尝试收集全部50个州造币券。当我们按照硬币类型整理零钱时，我们还会说出每个硬币所代表的州名，这样如果朋友没有这种硬币，他们就可以把它添加到他们的收藏中。

在这段代码的匹配表达式中，我们在匹配 variant `Coin::Quarter` 值的模式中添加了一个名为 `state` 的变量。当匹配到 `Coin::Quarter` 时， `state` 变量将绑定到该季度的状态值。然后，我们可以在相应分支的代码中使用 `state`，如下所示：

```rust
fn value_in_cents(coin: Coin) -> u8 {
    match coin {
        Coin::Penny => 1,
        Coin::Nickel => 5,
        Coin::Dime => 10,
        Coin::Quarter(state) => {
            println!("State quarter from {state:?}!");
            25
        }
    }
}

```

如果我们称 `value_in_cents(Coin::Quarter(UsState::Alaska))` 为 `coin`，那么 `coin` 就相当于 `Coin::Quarter(UsState::Alaska)`。当我们比较这个值与各个匹配项时，直到遇到 `Coin::Quarter(state)` 之前，都没有匹配项能够匹配上。在到达 `Coin::Quarter(state)` 时， `state` 的绑定值就会变成 `UsState::Alaska`。然后我们可以在 `println!` 表达式中利用这个绑定值，从而获取 `Quarter` 中 `Coin` 枚举变体所对应的内部状态值。

<!-- Old headings. Do not remove or links may break. -->

<a id="matching-with-optiont"></a>

### `Option<T>` `match` 模式

在上一节中，我们试图从使用 `Option<T>` 的 `Some` 情况中提取出 `T` 的值。同样地，我们也可以使用 `match` 来处理 `Option<T>`，就像我们对 `Coin` 枚举所做的那样！与其比较硬币，我们不如比较 `Option<T>` 的各种变体，不过 `match` 表达式的运作方式保持不变。

假设我们想要编写一个函数，该函数接受一个 `Option<i32>` 参数。如果参数内部有值，则将该值加1。如果参数内部没有值，那么该函数应该返回 `None` 的值，并且不尝试执行任何操作。

这个函数非常容易编写，多亏了 `match`，它的样子就像清单6-5所示。

<Listing number="6-5" caption="A function that uses a `match` expression on an `Option<i32>`">

```rust
    fn plus_one(x: Option<i32>) -> Option<i32> {
        match x {
            // ANCHOR: first_arm
            None => None,
            // ANCHOR_END: first_arm
            // ANCHOR: second_arm
            Some(i) => Some(i + 1),
            // ANCHOR_END: second_arm
        }
    }

    let five = Some(5);
    let six = plus_one(five);
    let none = plus_one(None);

```

</Listing>

Let’s examine the first execution of `加一` in more detail. When we call
`加一(五)`, the variable `x` in the body of `加一` will have the
value `Some(5)`. We then compare that against each match arm:

```rust,ignore
            None => None,

```

The `Some(5)` value doesn’t match the pattern `无`, so we continue to the
next arm:

```rust,ignore
            Some(i) => Some(i + 1),

```

Does `Some(5)` match `Some(i)`? It does! We have the same variant. The `i`
binds to the value contained in `Some`, so `i` takes the value `5`. The code in
the match arm is then executed, so we add 1 to the value of `i` and create a
new `Some` value with our total `6` inside.

Now let’s consider the second call of `加一` in Listing 6-5, where `x` is
`无`. We enter the `匹配` and compare to the first arm:

```rust,ignore
            None => None,

```

It matches! There’s no value to add to, so the program stops and returns the
`无` value on the right side of `=>`. Because the first arm matched, no other
arms are compared.

Combining `匹配` and enums is useful in many situations. You’ll see this
pattern a lot in Rust code: `匹配` against an enum, bind a variable to the
data inside, and then execute code based on it. It’s a bit tricky at first, but
once you get used to it, you’ll wish you had it in all languages. It’s
consistently a user favorite.

### Matches Are Exhaustive

There’s one other aspect of `匹配` we need to discuss: The arms’ patterns must
cover all possibilities. Consider this version of our `加一` function,
which has a bug and won’t compile:

```rust,ignore,does_not_compile
    fn plus_one(x: Option<i32>) -> Option<i32> {
        match x {
            Some(i) => Some(i + 1),
        }
    }

```

We didn’t handle the `无` case, so this code will cause a bug. Luckily, it’s
a bug Rust knows how to catch. If we try to compile this code, we’ll get this
error:

```console
$ cargo run
   Compiling enums v0.1.0 (file:///projects/enums)
error[E0004]: non-exhaustive patterns: `None` not covered
 --> src/main.rs:3:15
  |
3 |         match x {
  |               ^ pattern `None` not covered
  |
note: `Option<i32>` defined here
 --> /rustc/1159e78c4747b02ef996e55082b704c09b970588/library/core/src/option.rs:593:1
 ::: /rustc/1159e78c4747b02ef996e55082b704c09b970588/library/core/src/option.rs:597:5
  |
  = note: not covered
  = note: the matched value is of type `Option<i32>`
help: ensure that all possible cases are being handled by adding a match arm with a wildcard pattern or an explicit pattern as shown
  |
4 ~             Some(i) => Some(i + 1),
5 ~             None => todo!(),
  |

For more information about this error, try `rustc --explain E0004`.
error: could not compile `enums` (bin "enums") due to 1 previous error

```

Rust knows that we didn’t cover every possible case and even knows which
pattern we forgot! Matches in Rust are _exhaustive_: We must exhaust every last
possibility in order for the code to be valid. Especially in the case of
`选项⊂PH29⊂`, when Rust prevents us from forgetting to explicitly handle the
`无` case, it protects us from assuming that we have a value when we might
have null, thus making the billion-dollar mistake discussed earlier impossible.

### Catch-All Patterns and the `_` Placeholder

Using enums, we can also take special actions for a few particular values, but
for all other values take one default action. Imagine we’re implementing a game
where, if you roll a 3 on a dice roll, your player doesn’t move but instead
gets a fancy new hat. If you roll a 7, your player loses a fancy hat. For all
other values, your player moves that number of spaces on the game board. Here’s
a `匹配` that implements that logic, with the result of the dice roll
hardcoded rather than a random value, and all other logic represented by
functions without bodies because actually implementing them is out of scope for
this example:

```rust
    let dice_roll = 9;
    match dice_roll {
        3 => add_fancy_hat(),
        7 => remove_fancy_hat(),
        other => move_player(other),
    }

    fn add_fancy_hat() {}
    fn remove_fancy_hat() {}
    fn move_player(num_spaces: u8) {}

```

For the first two arms, the patterns are the literal values `3` and `7`. For
the last arm that covers every other possible value, the pattern is the
variable we’ve chosen to name `其他`. The code that runs for the `其他` arm
uses the variable by passing it to the `移动玩家` function.

This code compiles, even though we haven’t listed all the possible values a
`u8` can have, because the last pattern will match all values not specifically
listed. This catch-all pattern meets the requirement that `匹配` must be
exhaustive. Note that we have to put the catch-all arm last because the
patterns are evaluated in order. If we had put the catch-all arm earlier, the
other arms would never run, so Rust will warn us if we add arms after a
catch-all!

Rust also has a pattern we can use when we want a catch-all but don’t want to
_use_ the value in the catch-all pattern: `_` is a special pattern that matches
any value and does not bind to that value. This tells Rust we aren’t going to
use the value, so Rust won’t warn us about an unused variable.

Let’s change the rules of the game: Now, if you roll anything other than a 3 or
a 7, you must roll again. We no longer need to use the catch-all value, so we
can change our code to use `_` instead of the variable named `其他`:

```rust
    let dice_roll = 9;
    match dice_roll {
        3 => add_fancy_hat(),
        7 => remove_fancy_hat(),
        _ => reroll(),
    }

    fn add_fancy_hat() {}
    fn remove_fancy_hat() {}
    fn reroll() {}

```

This example also meets the exhaustiveness requirement because we’re explicitly
ignoring all other values in the last arm; we haven’t forgotten anything.

Finally, we’ll change the rules of the game one more time so that nothing else
happens on your turn if you roll anything other than a 3 or a 7. We can express
that by using the unit value (the empty tuple type we mentioned in [“The Tuple
Type”][tuples]<!-- ignore --> section) as the code that goes with the `_` arm:

```rust
    let dice_roll = 9;
    match dice_roll {
        3 => add_fancy_hat(),
        7 => remove_fancy_hat(),
        _ => (),
    }

    fn add_fancy_hat() {}
    fn remove_fancy_hat() {}

```

Here, we’re telling Rust explicitly that we aren’t going to use any other value
that doesn’t match a pattern in an earlier arm, and we don’t want to run any
code in this case.

There’s more about patterns and matching that we’ll cover in [Chapter
19][ch19-00-patterns]<!-- ignore -->. For now, we’re going to move on to the
`如果让` syntax, which can be useful in situations where the `匹配`表达式有点冗长。

[tuples]: ch03-02-data-types.html#the-tuple-type
[ch19-00-patterns]: ch19-00-patterns.html
