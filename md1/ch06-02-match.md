<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="匹配控制流运算符"></a>

## `match` 控制流结构

Rust 拥有一个非常强大的控制流结构，称为 ``match``。它允许你将某个值与一系列模式进行比较，然后根据匹配到的模式来执行相应的代码。这些模式可以包含字面值、变量名、通配符等多种元素；[第19章][ch19-00-patterns]<!-- 忽略 --> 详细介绍了各种模式的类型及其作用。`match` 的强大之处在于其模式的表达能力，以及编译器能够确保所有可能的情况都被处理。

可以将 `match` 表达式想象成一台硬币分类机：硬币沿着一条带有不同大小孔洞的轨道下滑，每枚硬币会掉入第一个符合其尺寸的孔洞中。同样地，值也会通过 `match` 中的每个模式，当值符合某个模式的规则时，它就会落入相应的代码块中，并在执行时被使用。

说到硬币，我们就用`match`来举个例子吧！我们可以编写一个函数，该函数接收一个未知的美国硬币，然后像计数机一样确定这是哪一种硬币，并返回其价值以分为单位，如清单6-3所示。

<列表编号="6-3" 标题="一个枚举以及一个`match`表达式，该表达式中包含枚举的各种变体作为模式">

```rust
{{#rustdoc_include ../listings/ch06-enums-and-pattern-matching/listing-06-03/src/main.rs:here}}
```

</ Listing>

让我们来分析一下 `value_in_cents` 函数中 `match` 的部分。首先，我们看到 `match` 这个关键词，后面跟着一个表达式，在这个例子中，这个表达式的值就是 `coin`。这看起来与用于 `if` 的条件表达式非常相似，但实际上有很大的区别：在 `if` 中，条件需要被评估为一个布尔值，而在这里，条件可以是任何类型。在这个例子中，`coin` 的类型就是我们在第一行定义的 `Coin` 枚举类型。

接下来是`match`这个分支。一个分支由两部分组成：一个模式和一些代码。这里的第一个分支包含一个模式，即值`Coin::Penny`，然后是一个`=>`运算符，用于分隔模式和要执行的代码。在这种情况下，代码实际上就是值`1`。每个分支通过逗号与下一个分支分开。

当 `match` 表达式执行时，它会依次将结果值与每个分支的模式进行比较。如果某个模式与值匹配，那么与该模式相关联的代码就会被执行。如果某个模式与值不匹配，则执行将继续进行到下一个分支，就像在硬币分类机中一样。我们可以根据需要设置任意多个分支：在清单6-3中，我们的 `match` 有四个分支。

与每个分支相关的代码都是一个表达式，而匹配分支中该表达式的结果值，就是整个`match`表达式所返回的值。

如果我们发现匹配分支的代码很短，通常不需要使用花括号。正如清单6-3所示，每个分支只是返回一个值而已。如果你想在匹配分支中运行多行代码，就必须使用花括号，而紧随其后的逗号则不是必需的。例如，下面的代码在每次方法被调用时都会打印“Lucky penny!”，同时还会返回该代码块中的最后一个值，即`1`。

```rust
{{#rustdoc_include ../listings/ch06-enums-and-pattern-matching/no-listing-08-match-arm-multiple-lines/src/main.rs:here}}
```

### 与值相关联的模式

Match Arms的另一个有用特性是，它们可以绑定到与模式匹配的值部分。通过这种方式，我们可以从枚举变体中提取出相应的值。

例如，让我们修改其中一个枚举变体，以在其内部存储数据。  
从1999年到2008年，美国为50个州各自铸造了不同设计的25美分硬币。没有其他硬币具有各州的特定设计，因此只有25美分硬币具有这种额外价值。我们可以通过修改`Quarter`变体来将这一信息添加到我们的`enum`中，从而在其中存储`UsState`的值。我们在清单6-4中实现了这一点。

<列表编号="6-4" 标题="一个`Coin`枚举，其中`Quarter`变体还包含一个`UsState`值">

```rust
{{#rustdoc_include ../listings/ch06-enums-and-pattern-matching/listing-06-04/src/main.rs:here}}
```

</ Listing>

让我们想象一个朋友正在尝试收集全部50枚州造币币。在我们将零钱按硬币类型分类的同时，我们还会说出每枚硬币所代表的州的名称，这样如果朋友没有这种硬币，他们就可以把它添加到他们的收藏中。

在这段代码的匹配表达式中，我们添加了一个名为`state`的变量，用于匹配变量`Coin::Quarter`的值。当`Coin::Quarter`被匹配时，`state`变量将绑定到该季度的状态值。然后，我们可以在相应分支的代码中使用`state`，如下所示：

```rust
{{#rustdoc_include ../listings/ch06-enums-and-pattern-matching/no-listing-09-variable-in-pattern/src/main.rs:here}}
```

如果我们调用`value_in_cents(Coin::Quarter(UsState::Alaska))`和`coin`，那么结果将会是`Coin::Quarter(UsState::Alaska)`。当我们比较这个值与各个匹配项时，直到到达`Coin::Quarter(state)`之前，都没有匹配到任何值。在那一刻，`state`的绑定将会是`UsState::Alaska`的值。然后我们可以在`println!`表达式中使用这个绑定，从而获取`Quarter`对应的`Coin`枚举变体中的内部状态值。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="匹配与选项">与选项匹配</a>

### `Option<T>` `match` 模式

在上一节中，我们试图从``Some``中获取``T``的值，同时利用``Option<T>``来实现条件判断。我们还可以使用``match``来处理``Option<T>``，就像我们对``Coin``枚举所做的那样。与其比较硬币，我们不如比较``Option<T>``的各种变体，不过``match``表达式的工作方式保持不变。

假设我们想要编写一个函数，该函数接收一个`Option<i32>`参数。如果其中包含某个值，则将该值加1。如果没有包含任何值，那么该函数应该返回`None`的值，而不尝试执行任何操作。

这个函数非常容易编写，多亏了`match`，它的样子就像 Listing 6-5 所示。

<列表编号="6-5" 标题="一个在 `Option<i32>` 上使用 `match` 表达式的函数">

```rust
{{#rustdoc_include ../listings/ch06-enums-and-pattern-matching/listing-06-05/src/main.rs:here}}
```

</ Listing>

让我们更详细地看看`plus_one`的第一次执行。当我们调用`plus_one(five)`时，位于`plus_one`主体中的变量`x`将拥有值`Some(5)`。然后，我们会将这个值与每个匹配分支进行比较。

```rust,ignore
{{#rustdoc_include ../listings/ch06-enums-and-pattern-matching/listing-06-05/src/main.rs:first_arm}}
```

`Some(5)`的值与模式`None`不匹配，因此我们继续进入下一个分支：

```rust,ignore
{{#rustdoc_include ../listings/ch06-enums-and-pattern-matching/listing-06-05/src/main.rs:second_arm}}
```

`Some(5)`与`Some(i)`是否匹配？确实匹配！我们拥有相同的变量。`i`绑定到`Some`中包含的值，因此`i`会获取`5`中的值。然后，匹配分支中的代码会被执行，所以我们会在`i`的值上加上1，并创建一个新的`Some`对象，其中包含了我们累加后的`6`值。

现在让我们考虑清单6-5中`plus_one`的第二次调用，其中`x`就是`None`。我们进入`match`，然后与第一个分支进行比较：

```rust,ignore
{{#rustdoc_include ../listings/ch06-enums-and-pattern-matching/listing-06-05/src/main.rs:first_arm}}
```

匹配成功！没有需要添加的值，因此程序会停止，并返回`=>`右侧的`None`值。由于第一个分支已经匹配，因此不会再比较其他分支。

在许多情况下，将 ``match``与枚举结合使用是非常有用的。在Rust代码中，你会经常看到这种模式：将变量绑定到枚举内部的数据上，然后根据该数据执行相应的代码。一开始可能会有点复杂，但一旦习惯了这种用法，你就会希望所有编程语言都支持这种机制。这确实一直都是用户最喜爱的编程技巧之一。

### 匹配是穷尽的

还有另一个关于`match`的问题需要讨论：手臂的模式必须涵盖所有可能性。考虑一下我们`plus_one`函数的这个版本，它存在错误，无法编译：

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch06-enums-and-pattern-matching/no-listing-10-non-exhaustive-match/src/main.rs:here}}
```

我们没有处理`None`这种情况，因此这段代码会导致错误。幸运的是，这是Rust能够捕获的错误类型。如果我们尝试编译这段代码，将会出现以下错误：

```console
{{#include ../listings/ch06-enums-and-pattern-matching/no-listing-10-non-exhaustive-match/output.txt}}
```

Rust知道我们并没有涵盖所有可能的情况，甚至知道我们遗漏了哪些情况！在Rust中，匹配是“穷举”式的：我们必须穷尽每一种可能性，才能让代码保持有效性。特别是在`Option<T>`的情况下，Rust会阻止我们忘记显式处理`None`的情况，从而防止我们假设存在某个值，而实际上该值是null。这样就能避免前面提到的那个代价高昂的错误。

### 万能模式与`_`占位符

通过使用枚举类型，我们还可以对某些特定值采取特殊操作，但对于其他所有值则采用默认操作。想象一下，我们正在开发一个游戏，如果在掷骰子时得到3点，玩家不会移动，而是会获得一顶新帽子。如果掷到7点，玩家则会失去一顶新帽子。对于其他所有值，玩家会在游戏板上移动相应数量的格子。下面是一个实现该逻辑的`match`代码，其中骰子掷出的结果被硬编码，而不是随机值。所有其他逻辑都通过没有函数的主体来表示，因为实际上实现这些逻辑超出了这个示例的范围。

```rust
{{#rustdoc_include ../listings/ch06-enums-and-pattern-matching/no-listing-15-binding-catchall/src/main.rs:here}}
```

在前两个分支中，对应的模式就是字面值 `3` 和 `7`。而对于最后一个分支，它涵盖了所有其他可能的值，该模式的变量就是我们选择命名为 `other`。在 `other` 分支中运行的代码，是通过将变量传递给 `move_player` 函数来使用这个变量的。

这段代码可以编译成功，尽管我们没有列出 ``u8`` 所有可能的取值。因为最后一个模式会匹配所有未被特别列出的取值。这个“兜底”模式满足了 ``match`` 必须全面覆盖所有取值的要求。需要注意的是，我们必须将“兜底”模式放在最后，因为模式是按顺序进行评估的。如果我们把“兜底”模式放在前面，那么其他模式就永远不会被执行了，因此当我们在一个“兜底”模式之后添加其他模式时，Rust 会发出警告！

Rust还提供了一种模式，当我们想要一个“捕获所有情况”的模式，但不想实际使用该值的时候可以使用这种模式。这里的`_`是一个特殊的模式，它可以匹配任何值，并且不会将该值绑定到某个变量上。这样告诉Rust我们不会使用该值，因此Rust不会因为我们使用了未使用的变量而发出警告。

让我们改变游戏规则：现在，如果你掷出的点数不是3或7，就必须重新掷一次。我们不再需要使用那个通用的数值，因此我们可以修改代码，使用`_`来代替名为`other`的变量。

```rust
{{#rustdoc_include ../listings/ch06-enums-and-pattern-matching/no-listing-16-underscore-catchall/src/main.rs:here}}
```

这个例子也满足了全面性的要求，因为我们明确忽略了最后一个分支中的所有其他值；我们没有遗漏任何内容。

最后，我们还会再次修改游戏规则，这样当你掷出除了3或7之外的任何数字时，就不会再发生其他事情了。我们可以通过使用单位值（我们在[“元组类型”][tuples]<!-- ignore -->部分提到的空元组类型）作为与`_`符号一起出现的代码来表达这一点。

```rust
{{#rustdoc_include ../listings/ch06-enums-and-pattern-matching/no-listing-17-underscore-unit/src/main.rs:here}}
```

在这里，我们明确告诉Rust，我们不会使用任何不符合之前模式的其他值，并且在这种情况下，我们不希望执行任何代码。

关于模式和匹配的内容还有很多，我们将在[第19章][ch19-00-patterns]中详细讨论。目前，我们接下来将介绍`if let`语法，这种语法在`match`表达式比较冗长的情况下非常有用。

[tuples]: ch03-02-data-types.html#the-tuple-type  
[ch19-00-patterns]: ch19-00-patterns.html