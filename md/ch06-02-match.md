<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="匹配控制流运算符"></a>

## `match` 控制流结构

Rust拥有一个非常强大的控制流结构，称为`match`。它允许你将某个值与一系列模式进行比较，然后根据匹配到的模式来执行相应的代码。这些模式可以由字面值、变量名、通配符等多种元素组成；[第19章][ch19-00-patterns]<!-- 忽略 -->详细介绍了各种模式的类型及其作用。`match`的强大之处在于其表达能力的丰富性。模式以及编译器能够确保所有可能的情况都被处理的事实。

可以将`match`表达式想象成一台硬币分类机：硬币沿着一条带有不同大小孔洞的轨道下滑，每枚硬币会掉入第一个符合其尺寸的孔洞中。同样地，数值也会通过`match`中的每个“模式”，当数值符合某个模式时，它就会落入相应的代码块中，以便在执行时被使用。

说到硬币，让我们用它们作为例子，使用`match`！我们可以编写一个函数，该函数接收一个未知的美国硬币，并以与计数机类似的方式确定硬币的类型，然后返回其价值以美分为单位，如清单6-3所示。

<列表编号="6-3" 标题="一个枚举类型以及一个`match`表达式，该表达式中包含枚举类型的各种变体作为模式">

```rust
{{#rustdoc_include ../listings/ch06-enums-and-pattern-matching/listing-06-03/src/main.rs:here}}
```

</清单>

让我们来分析一下`value_in_cents`函数中的`match`。首先，我们看到`match`这个关键字，后面跟着一个表达式，在这个例子中，这个表达式的值就是`coin`。这看起来与用于`if`的条件表达式非常相似，但两者之间有一个重要的区别：在`if`中，条件需要被评估为一个布尔值，而在这里，条件可以是任何类型。在这个例子中，`coin`的类型是……这是我们在第一行定义的 ``Coin`` 枚举类型。

接下来是`match`这个部分。一个部分由两部分组成：一个模式和一些代码。这里的第一个部分包含一个模式，即值`Coin::Penny`，然后是一个`=>`运算符，用于分隔模式和要执行的代码。在这种情况下，代码就是值`1`。每个部分通过逗号与下一个部分隔开。

当`match`表达式执行时，它会依次将结果值与每个分支的模式进行比较。如果某个模式与值匹配，那么与该模式相关的代码就会被执行。如果模式不匹配该值，则执行将继续到下一个分支，就像在硬币分类机中一样。我们可以根据需要设置任意多个分支：在清单6-3中，我们的`match`有四个分支。

与每个分支相关的代码是一个表达式，而该表达式中匹配分支的结果值，就是整个`match`表达式所返回的值。

通常情况下，如果匹配分支的代码很短，我们不会使用花括号。正如清单6-3所示，每个分支只是返回一个值而已。如果你想在匹配分支中运行多行代码，就必须使用花括号，而分支后面的逗号则不是必需的。例如，下面的代码在每次方法被调用时都会打印“Lucky penny!”，同时还会返回该代码块中的最后一个值，即`1`。

```rust
{{#rustdoc_include ../listings/ch06-enums-and-pattern-matching/no-listing-08-match-arm-multiple-lines/src/main.rs:here}}
```

### 与值相关联的模式

Match Arms的另一个有用特性是，它们可以绑定到与模式匹配的值的部分。通过这种方式，我们可以从枚举变体中提取出值。

例如，让我们修改其中一个枚举变体，使其内部存储数据。从1999年到2008年，美国为50个州各自铸造了不同设计的25美分硬币。没有其他硬币具有各州的特定设计，因此只有25美分硬币具有这种额外价值。我们可以通过更改`Quarter`变体来将这一信息添加到我们的`enum`中，从而在其中存储`UsState`的值。我们在清单6-4中实现了这一点。

<列表编号="6-4" 标题="一个`Coin`枚举，其中`Quarter`变体还包含一个`UsState`值>

```rust
{{#rustdoc_include ../listings/ch06-enums-and-pattern-matching/listing-06-04/src/main.rs:here}}
```

</清单>

让我们想象一个朋友正在尝试收集全部50枚州造币币。当我们按照硬币类型整理零钱时，我们还会说出每枚硬币所代表的州的名称，这样如果朋友没有这种硬币，他们就可以把它添加到自己的收藏中。

在这段代码的匹配表达式中，我们在模式中添加了一个名为`state`的变量，该变量用于匹配变量`Coin::Quarter`的值。当`Coin::Quarter`匹配时，`state`变量将绑定到该季度的状态值。然后，我们可以在相应分支的代码中使用`state`，如下所示：

```rust
{{#rustdoc_include ../listings/ch06-enums-and-pattern-matching/no-listing-09-variable-in-pattern/src/main.rs:here}}
```

如果我们称 `value_in_cents(Coin::Quarter(UsState::Alaska))` 和 `coin` 为 `Coin::Quarter(UsState::Alaska)`。当我们比较这个值与各个匹配值时，直到到达 `Coin::Quarter(state)` 之前，没有任何一个值相匹配。在那时，`state` 的绑定将会是 `UsState::Alaska` 的值。然后我们可以在 `println!` 表达式中使用该绑定，从而获取来自 `Coin` 枚举变体的内部状态值，用于 `Quarter`。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="匹配与选项"></a>

### `Option<T>` `match` 模式

在上一节中，我们希望从``Some``中获取``T``的值，并使用``Option<T>``来实现这一功能。我们还可以使用``match``来处理``Option<T>``，就像我们对``Coin``所做的那样！与其比较硬币，我们不如比较``Option<T>``的各种变体，不过``match``表达式的运作方式保持不变。

假设我们想要编写一个函数，该函数接收一个`Option<i32>`参数。如果其中包含某个值，则将该值加1。如果没有包含任何值，那么该函数应该返回`None`的值，而不尝试执行任何操作。

这个函数非常容易编写，多亏了`match`的功能，其代码如下：

清单 6-5.

<列表编号="6-5" 标题="一个在`Option<i32>`上使用`match`表达式的函数">

```rust
{{#rustdoc_include ../listings/ch06-enums-and-pattern-matching/listing-06-05/src/main.rs:here}}
```

</清单>

让我们更详细地看看`plus_one`的第一次执行。当我们调用`plus_one(five)`时，位于`plus_one`主体中的变量`x`将拥有值`Some(5)`。然后，我们会将这个值与每个匹配的条件进行比较。

```rust,ignore
{{#rustdoc_include ../listings/ch06-enums-and-pattern-matching/listing-06-05/src/main.rs:first_arm}}
```

`Some(5)`的值与模式`None`不匹配，因此我们继续进入下一个分支：

```rust,ignore
{{#rustdoc_include ../listings/ch06-enums-and-pattern-matching/listing-06-05/src/main.rs:second_arm}}
```

`Some(5)`与`Some(i)`是否匹配？确实匹配！我们拥有相同的变量值。`i`绑定到`Some`中的值，因此`i`会获取`5`的值。然后，匹配分支中的代码会被执行，所以我们会将1加到`i`的值上，并创建一个新的`Some`值，其中包含了我们累加后的`6`值。

现在让我们考虑清单6-5中第二次调用`plus_one`的情况，其中`x`就是`None`。我们进入`match`，并将其与第一个分支进行比较。

```rust,ignore
{{#rustdoc_include ../listings/ch06-enums-and-pattern-matching/listing-06-05/src/main.rs:first_arm}}
```

匹配成功！没有需要添加的值，因此程序会停止，并返回`=>`右侧的`None`值。由于第一个条件匹配成功，因此不会进行其他条件的比较。

在许多情况下，将`match`与枚举结合使用是非常有用的。在Rust代码中，你会经常看到这种模式：将`match`与枚举关联起来，将一个变量绑定到枚举内部的数据上，然后根据该数据进行相应的操作。一开始可能会有点复杂，但一旦习惯了这种用法，你就会希望所有语言都支持这种机制。这确实一直都是用户最喜爱的用法之一。

### 匹配是全面的

还有另一个关于`match`的方面需要讨论：武器的图案必须涵盖所有可能性。考虑一下我们`plus_one`函数的这个版本，它存在错误，无法编译：

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch06-enums-and-pattern-matching/no-listing-10-non-exhaustive-match/src/main.rs:here}}
```

我们没有处理`None`这种情况，因此这段代码会导致错误。幸运的是，这是Rust能够捕获的错误类型。如果我们尝试编译这段代码，将会出现以下错误：

```console
{{#include ../listings/ch06-enums-and-pattern-matching/no-listing-10-non-exhaustive-match/output.txt}}
```

Rust知道我们并没有涵盖所有可能的情况，甚至知道我们遗漏了哪些情况！在Rust中，匹配是“穷举”的：我们必须穷尽每一个可能性，才能让代码有效。特别是在`Option<T>`的情况下，Rust会防止我们忘记显式处理`None`的情况，从而保护我们不会假设存在某个值，而实际上可能是null。这样，之前提到的那个代价高昂的错误就不复发生了。

### 万能模式与`_`占位符

通过使用枚举类型，我们还可以针对某些特定值采取特殊操作，但对于其他所有值则采用默认操作。想象一下，我们正在开发一个游戏，如果在掷骰子时得到3点，玩家就不会移动，而是会获得一顶新帽子。如果掷到7点，玩家则会失去一顶新帽子。对于其他所有值，玩家会在游戏板上移动相应数量的格子。下面是一段实现该逻辑的`match`代码，以及掷骰子的结果。采用硬编码的方式，而不是使用随机值；所有其他逻辑都通过无体的函数来表示，因为实际实现这些功能超出了本例的范围。

```rust
{{#rustdoc_include ../listings/ch06-enums-and-pattern-matching/no-listing-15-binding-catchall/src/main.rs:here}}
```

在前两个分支中，对应的模式分别是字面值 `3` 和 `7`。而对于最后一个分支，它涵盖了所有其他可能的值，该模式的变量名为 `other`。在 `other` 分支中运行的代码，是通过将变量传递给 `move_player` 函数来使用的。

这段代码可以成功编译，尽管我们没有列出`u8`可能拥有的所有值。因为最后一个模式会匹配所有未被特别列出的值。这个“兜底”模式满足了`match`必须全面覆盖的要求。需要注意的是，我们必须将“兜底”模式放在最后，因为模式是按顺序进行评估的。如果我们把“兜底”模式放在前面，那么其他模式就不会被执行了，因此当我们在一个“兜底”模式之后添加其他模式时，Rust会发出警告！

在需要一种万能的捕获模式时，Rust还提供了一种特殊的模式，即`_`。这种模式可以匹配任何值，但不会将该值绑定到某个变量上。这样，我们可以告诉Rust不会使用这个值，因此Rust也不会因为我们未使用的变量而发出警告。

让我们改变游戏规则：现在，如果你掷出的点数不是3或7，就必须重新掷一次。我们不再需要使用那个通用的数值，因此我们可以修改代码，使用`_`来代替名为`other`的变量。

```rust
{{#rustdoc_include ../listings/ch06-enums-and-pattern-matching/no-listing-16-underscore-catchall/src/main.rs:here}}
```

这个例子也满足了全面性的要求，因为我们明确忽略了最后一个分支中的所有其他值；我们没有遗漏任何内容。

最后，我们还会再次修改游戏规则，这样如果你掷出的点数不是3或7，那么在你的回合就不会发生其他事情了。我们可以通过使用单位值（我们在[“元组类型”][tuples]<!-- ignore -->章节中提到的空元组类型）作为与`_`符号相关联的代码来表达这一点。

```rust
{{#rustdoc_include ../listings/ch06-enums-and-pattern-matching/no-listing-17-underscore-unit/src/main.rs:here}}
```

在这里，我们明确告诉Rust，我们不会使用任何不符合之前模式的其他值，并且在这种情况下，我们不希望执行任何代码。

关于模式和匹配的相关内容，我们将在[第19章][ch19-00-patterns]中详细讨论。目前，我们接下来将介绍`if let`语法，当`match`表达式有些冗长时，这种语法会非常有用。

[tuples]: ch03-02-data-types.html#the-tuple-type
[ch19-00-patterns]: ch19-00-patterns.html