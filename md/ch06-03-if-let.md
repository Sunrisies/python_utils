## 使用`if let`和`let...else`实现简洁的控制流程

`if let`语法允许你将`if`和`let`结合起来，以一种更简洁的方式来处理符合某种模式的值，同时忽略其他值。请参考清单6-6中的程序，该程序会在`config_max`变量中查找与`Option<u8>`匹配的值，但只有当该值为`Some`的变体时才会执行相应的代码。

<列表编号="6-6" 标题="一个`match`，仅在值为`Some`时执行代码">

```rust
{{#rustdoc_include ../listings/ch06-enums-and-pattern-matching/listing-06-06/src/main.rs:here}}
```

</清单>

如果值为`Some`，我们可以通过将值绑定到模式中的变量`max`来输出`Some`变体中的值。我们不想对`None`的值进行任何操作。为了满足`match`的表达式要求，我们需要在处理其中一个变体后添加`_ =>()`，这会增加一些繁琐的样板代码。

相反，我们可以使用`if let`来更简洁地编写这段代码。以下代码与清单6-6中的`match`行为相同：

```rust
{{#rustdoc_include ../listings/ch06-enums-and-pattern-matching/no-listing-12-if-let/src/main.rs:here}}
```

语法`if let`接受一个模式和一个由等号分隔的表达式。它的工作方式与`match`类似，其中表达式被传递给`match`，而模式则是其第一个参数。在这种情况下，模式是`Some(max)`，而`max`则绑定到`Some`内部的值上。然后，我们可以在同一`if let`块的体内使用`max`，就像我们在`max`中使用的那样。对应的`match`部分。只有当value符合模式时，`if let`块中的代码才会执行。

使用 ``if let`` 可以减少输入量、缩进次数以及样板代码的数量。不过，这样做会失去详尽的检查功能。``match`` 则能确保不会出现遗漏任何情况的处理方式。在 ``match`` 和 `if let` 之间做出选择，取决于你在特定情况下的具体需求，以及是否认为简洁性提升与详尽检查功能的丧失是值得的权衡。

换句话说，你可以将`if let`视为一种语法糖，用于`match`，该代码会在值符合某个模式时执行代码，而忽略所有其他值。

我们可以包含一个`else`和一个`if let`。与`else`一起出现的代码块，与`match`表达式中以`_`开头的代码块相同，而`match`相当于`if let`和`else`。请参考清单6-4中的`Coin`枚举定义，其中`Quarter`变体也包含了一个`UsState`值。如果我们想要统计所有非四分之一硬币的数量，那么……在宣布季度状态时，我们可以使用一个`match`表达式来实现这一点，如下所示：

```rust
{{#rustdoc_include ../listings/ch06-enums-and-pattern-matching/no-listing-13-count-and-announce-match/src/main.rs:here}}
```

或者我们可以使用``if let``和``else``表达式，如下所示：

```rust
{{#rustdoc_include ../listings/ch06-enums-and-pattern-matching/no-listing-14-count-and-announce-if-let-else/src/main.rs:here}}
```

## 与`let...else`一起保持在“幸福之路”上

常见的做法是在某个值存在时执行某些计算操作，而在其他情况下返回默认值。以我们关于硬币的例子为例，如果我们要根据硬币上的状态保存时间来判断一些有趣的事情，我们可以在`UsState`上添加一个方法来检查状态的保存时间。

```rust
{{#rustdoc_include ../listings/ch06-enums-and-pattern-matching/listing-06-07/src/main.rs:state}}
```

然后，我们可以使用 ``if let``来匹配硬币的类型，并在条件的主体中引入一个 ``state``变量，如清单6-7所示。

<列表编号="6-7" 标题="通过嵌套在`if let`中的条件语句来检查1900年时是否存在某个状态">

```rust
{{#rustdoc_include ../listings/ch06-enums-and-pattern-matching/listing-06-07/src/main.rs:describe}}
```

</清单>

这样的实现方式是可以完成任务的，但是它将代码移到了`if let`语句的主体中。如果需要执行的操作比较复杂，那么很难准确理解各个顶层分支之间的关系。我们还可以利用这样一个事实：表达式可以生成值，要么从``if let``中生成``state``，要么提前返回结果，就像在清单6-8中所做的那样。（你也可以对``match``采取类似的做法。）

<列表编号="6-8" 标题="使用 `if let` 生成值或提前返回">

```rust
{{#rustdoc_include ../listings/ch06-enums-and-pattern-matching/listing-06-08/src/main.rs:describe}}
```

</清单>

不过，按照这种方式来跟踪确实有点麻烦！其中一个分支会生成一个值，而另一个分支则完全从函数中返回。

为了使这种常见的模式更易于表达，Rust提供了`let...else`。`let...else`语法在左侧接受一个模式，在右侧接受一个表达式，这与`if let`非常相似，但它没有`if`分支，只有`else`分支。如果模式匹配成功，它将把模式中的值绑定到外部作用域中。如果模式不匹配，程序将进入`else`分支，该分支必须从函数中返回。

在清单6-9中，你可以看到当使用`let...else`代替`if let`时，清单6-8的显示效果。

<列表编号="6-9" 标题="使用 `let...else` 来阐明函数的执行流程">

```rust
{{#rustdoc_include ../listings/ch06-enums-and-pattern-matching/listing-06-09/src/main.rs:describe}}
```

</清单>

请注意，通过这种方式，函数主体始终保持在“正常路径”上，两个分支的控制流程并没有发生显著的变化，这与`if let`的方式不同。

如果你遇到这样的情况：你的程序中的逻辑过于冗长，无法用`match`来表述，那么请记住，`if let`和`let...else`也是你的Rust工具箱中的利器。

## 摘要

我们已经介绍了如何使用枚举来创建自定义类型，这些类型可以是枚举值中的一个。我们还展示了标准库中的`Option<T>`类型如何帮助你利用类型系统来避免错误。当枚举值包含数据时，你可以根据需要处理的情况，使用`match`或`if let`来提取并使用这些数据。

您的Rust程序现在可以使用结构体和数据类型来表示您所在领域中的概念。在API中创建自定义类型可以确保类型安全：编译器会确保函数接收到的数值都是它们所期望的类型。

为了为用户提供一个组织良好的API，使其易于使用，并且只暴露用户真正需要的功能，我们现在来了解一下Rust中的模块。