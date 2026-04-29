## 使用 `if let` 和 `let...else`实现简洁的控制流

`if let`语法允许你将`if`和`let`结合起来，以一种更简洁的方式来处理符合某种模式的值，同时忽略其他值。请参考清单6-6中的程序，该程序会在`config_max`变量中查找符合`Option<u8>`值的匹配项，但只有当该值为`Some`变体时才会执行相应的代码。

<列表编号="6-6" 标题="一个`match`，仅在值为`Some`时执行代码">

```rust
{{#rustdoc_include ../listings/ch06-enums-and-pattern-matching/listing-06-06/src/main.rs:here}}
```

</ Listing>

如果值为`Some`，我们可以通过将值绑定到模式中的变量`max`来输出`Some`变体中的值。我们不想对`None`的值进行任何操作。为了满足`match`表达式的要求，我们必须在处理其中一个变体之后加上`_ =>()`，这会增加一些繁琐的样板代码。

相反，我们可以使用 `if let` 以更简洁的方式编写这段代码。以下代码与清单 6-6 中的 `match` 行为相同：

```rust
{{#rustdoc_include ../listings/ch06-enums-and-pattern-matching/no-listing-12-if-let/src/main.rs:here}}
```

语法 ``if let`` 接受一个模式和一个由等号分隔的表达式。它的工作方式与 ``match`` 类似，其中表达式被传递给 ``match``，而模式则是其第一个参数。在这种情况下，模式是 ``Some(max)``，而 ``max`` 会绑定到 ``Some`` 中的值。然后，我们可以像使用 ``max`` 在相应的 ``match`` 中一样，在 ``if let`` 块的主体中使用 ``max``。只有当值与模式匹配时，`if let` 块中的代码才会执行。

使用 ``if let`` 可以减少输入量、缩进次数以及样板代码的数量。不过，这样做会失去 `match` 所提供的详尽检查功能，后者能够确保你不会遗漏任何情况的处理。在 ``match`` 和 `if let` 之间做出选择，取决于你在特定情况下的具体需求，以及是否认为简洁性提升与失去详尽检查功能是可接受的权衡。

换句话说，你可以将`if let`视为一种语法糖，它对应着`match`，后者在值符合某个模式时执行代码，而忽略所有其他值。

我们可以包含一个 `else` 和一个 `if let`。与 `else` 一起出现的代码块，与 `match` 表达式中 `_` 情况对应的代码块是相同的，而 `match` 表达式则等同于 `if let` 和 `else`。请参考清单 6-4 中的 `Coin` 枚举定义，其中 `Quarter` 变体也包含了一个 `UsState` 值。如果我们想要统计所有非 quarter 硬币的数量，同时告知 quarter 硬币的状态，我们可以使用 `match` 表达式来实现这一点。

```rust
{{#rustdoc_include ../listings/ch06-enums-and-pattern-matching/no-listing-13-count-and-announce-match/src/main.rs:here}}
```

或者我们可以使用__`INLINE_CODE_51__`和__`INLINE_CODE_52__`这样的表达式，如下所示：

```rust
{{#rustdoc_include ../listings/ch06-enums-and-pattern-matching/no-listing-14-count-and-announce-if-let-else/src/main.rs:here}}
```

## 与`let...else`一起保持在“幸福之路”上

常见的做法是在某个值存在时执行某些计算操作，而在其他情况下返回默认值。以我们关于硬币的例子为例，如果我们要根据硬币上的状态的年龄来展示一些有趣的内容，我们可以在`UsState`上添加一个方法，用于检查状态的年龄。

```rust
{{#rustdoc_include ../listings/ch06-enums-and-pattern-matching/listing-06-07/src/main.rs:state}}
```

然后，我们可以使用 ``if let``来匹配硬币的类型，并在条件的主体中引入一个 ``state``变量，如清单6-7所示。

<列表编号="6-7" 标题="使用嵌套在`if let`中的条件语句来检查1900年时是否存在某个状态">

```rust
{{#rustdoc_include ../listings/ch06-enums-and-pattern-matching/listing-06-07/src/main.rs:describe}}
```

</ Listing>

这种方法确实可以完成任务，但是它将代码移到了 `if let` 语句的主体中。如果需要执行的操作比较复杂，那么很难准确理解各个顶层分支之间的关系。我们还可以利用表达式能够产生值这一特性，从而从 ``if let`` 中生成 `state`，或者像清单 6-8 中所做的那样提前返回结果。（你也可以对 `match` 采用类似的方法。）

<列表编号="6-8" 标题="使用 `if let` 生成值或提前返回">

```rust
{{#rustdoc_include ../listings/ch06-enums-and-pattern-matching/listing-06-08/src/main.rs:describe}}
```

</ Listing>

不过，这种处理方式确实有点麻烦！`if let`的一个分支会返回一个值，而另一个分支则完全从函数中返回。

为了使这种常见模式更易于表达，Rust提供了`let...else`。`let...else`语法在左侧接受一个模式，在右侧接受一个表达式，这与`if let`非常相似，但它没有`if`分支，只有`else`分支。如果模式匹配成功，它将把模式中的值绑定到外部作用域中。如果模式不匹配，程序将进入`else`分支，该分支必须从函数中返回。

在清单6-9中，你可以看到当使用`let...else`代替`if let`时，清单6-8的显示效果。

<listing number="6-9" caption="使用 `let...else` 来阐明函数的执行流程">

```rust
{{#rustdoc_include ../listings/ch06-enums-and-pattern-matching/listing-06-09/src/main.rs:describe}}
```

</ Listing>

请注意，通过这种方式，函数主体中的控制流程始终保持在“正常路径”上，而`if let`的处理方式则没有对两个分支进行显著不同的控制流程。

如果您遇到这样的情况：程序中的逻辑过于冗长，无法用 ``match`` 来表示，那么请记住，``if let`` 和 ``let...else`` 也是您 Rust 工具箱中的工具。

## 总结

我们现在已经了解了如何使用枚举来创建自定义类型，这些类型可以表示从一组枚举值中选择的一个值。我们还展示了标准库中的`Option<T>`类型如何帮助你利用类型系统来避免错误。当枚举值包含数据时，你可以根据需要处理的情况，使用`match`或`if let`来提取并使用这些值。

现在，你的Rust程序可以使用结构体和数据类型来表达你所在领域中的概念。在API中创建自定义类型可以确保类型安全：编译器会确保你的函数只能接收每个函数所期望的类型的值。

为了为用户提供一个组织良好的API，使其使用起来非常直观，并且只暴露用户真正需要的功能，现在让我们来了解一下Rust中的模块。