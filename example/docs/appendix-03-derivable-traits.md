## 附录C：可推导出的特性

在书的各个部分中，我们讨论过 `derive` 属性，你可以将其应用于结构体或枚举类型的定义。而 `derive` 属性则会产生代码，这些代码会为你所标注的类型实现一个带有默认实现的特质。

在这个附录中，我们列出了标准库中所有可以与 `derive` 一起使用的特性。每个部分都包含以下内容：

- 哪些运算符和方法可以继承这个特性
- `derive` 提供的这个特性的实现具体是什么
- 继承这个特性对类型有什么意义
- 在哪些情况下可以或不能继承这个特性
- 需要这个特性的操作示例

如果您希望获得与 `derive` 属性所提供的行为不同的结果，请查阅[标准库文档](../std/index.html)<!-- ignore -->，了解如何手动实现每个 trait 的详细信息。

这里列出的特性是标准库中唯一可以通过 `derive` 在你的类型上实现的特性。标准库中定义的其他特性并没有合理的默认行为，因此你需要根据自己的需求来实现它们。

一个无法被派生的 trait 的例子是 `Display`，它负责处理最终用户的格式设置问题。在决定如何向最终用户展示一个类型时，你应该始终考虑合适的展示方式。最终用户应该能够看到类型的哪些部分？他们觉得哪些部分很重要？哪种数据格式对他们来说最相关？Rust 编译器没有这种洞察力，因此无法为你提供合适的默认行为。

本附录中提供的可派生特性的列表并不全面：  
库可以为自己的特性实现 `derive` 功能，这使得可以与 `derive` 一起使用的特性数量变得非常广泛。而实现 `derive` 则需要使用过程式宏，相关内容将在第20章的[“自定义 `derive` 宏”][custom-derive-macros]<!-- ignore -->部分进行介绍。

### 程序员输出使用 `Debug`

`Debug` trait 使得在格式字符串中可以进行调试格式化操作，您可以通过在 `{}` 占位符内添加 `:?` 来实现这一点。

`Debug` trait 允许你打印该类型的实例，以便于调试。这样，你和其他使用该类型的程序员可以在程序执行的特定阶段检查该实例。

例如，在使用 `assert_eq!` 宏时，需要包含 `Debug` trait。这个宏会在等式断言失败的情况下，打印作为参数传递的实例的值，这样程序员就能明白为什么这两个实例并不相等。

### 用于相等性比较的 `PartialEq` 和 `Eq`

`PartialEq` trait 允许你比较同一类型的实例，以检查它们是否相等，并且使得可以使用 `==` 和 `!=` 运算符。

通过派生 `PartialEq` 可以实现 `eq` 方法。当在结构体上派生 `PartialEq` 时，只有当所有字段都相等时，两个实例才相等；如果有任何字段不相等，则这两个实例就不相等。当在枚举类型上派生 `PartialEq` 时，每个变体都等于自身，而不等于其他变体。

需要使用 `PartialEq` trait，例如，通过使用`assert_eq!`宏，该宏需要能够比较两个类型的实例是否相等。

`Eq` trait 没有方法。它的作用是指示对于该标注类型的每一个值，该值都等于自身。`Eq` trait 只能应用于同时实现了 `PartialEq` 的类型，不过并非所有实现了 `PartialEq` 的类型都能实现 `Eq`。一个例子就是浮点数值类型：浮点数的实现规定，两个不是数字（`NaN`）的实例并不相等。

一个需要使用 `Eq` 的例子是对于 `HashMap<K, V>` 中的键，这样 `HashMap<K, V>` 就可以判断两个键是否相同。

### 用于排序比较的 `PartialOrd` 和 `Ord`

`PartialOrd` trait 允许你为了排序的目的而比较同一类型的实例。实现了 `PartialOrd` 的类型可以与 `<`, `>`、`<=`, and `>=` 运算符一起使用。你只能将 `PartialOrd` trait 应用于同时实现了 `PartialEq` 的类型。

Deriving `PartialOrd` 实现了 `partial_cmp` 方法，该方法返回一个`Option<Ordering>`，当给定的值无法产生排序时，该值将变为`None`。一个无法产生排序的例子是`NaN` 浮点数值。无论使用哪个浮点数值调用 `partial_cmp`，并且使用`NaN` 浮点数值，最终都会返回`None`。

在结构体上派生时，`PartialOrd`通过按照结构体定义中字段出现的顺序来比较两个实例的各个字段的值。在枚举上派生时，枚举定义中较早声明的枚举变体会被视为比后面列出的变体更“低”。

例如，对于来自 `rand`  crate 中的 `gen_range` 方法来说，需要用到 `PartialOrd` trait。这个 `rand` crate 能够生成一个在指定范围内随机值的数值。

`Ord` 特性允许你知道，对于任何两个被标注的类型的值，都存在一个有效的排序关系。`Ord` 特性实现了 `cmp` 方法，该方法返回的是 `Ordering` 而不是 `Option<Ordering>`，因为总是存在有效的排序关系。你只能将 `Ord` 特性应用于那些同时实现了 `PartialOrd` 和 `Eq` 的类型（而 `Eq` 则需要 `PartialEq`）。在结构体和处理器派生时，`cmp` 的行为与 `partial_cmp` 在 `PartialOrd` 上的派生实现相同。

当需要在 `BTreeSet<T>` 中存储值时，就需要使用 `Ord`。 `BTreeSet<T>` 是一种基于值的排序顺序来存储数据的数据结构。

### 对于复制值，使用 `Clone` 和 `Copy`

`Clone` trait 允许你显式地创建一个值的深度复制，而复制过程可能涉及运行任意代码以及复制堆数据。有关 `Clone` 的更多信息，请参阅第4章中的[“变量与数据在克隆中的交互”][variables-and-data-interacting-with-clone]<!-- ignore -->部分。

通过派生 `Clone` 来实现 `clone` 方法。当该方法应用于整个类型时，它会对类型的每个部分调用 `clone`。这意味着类型中的所有字段或值也必须实现 `Clone`，才能派生出 `Clone`。

一个需要使用 `Clone` 的例子是当在切片上调用 `to_vec` 方法时。切片并不拥有其所包含的类型实例，但是由 `to_vec` 返回的向量需要拥有这些实例。因此， `to_vec` 需要对每个项调用 `clone`。这样一来，存储在切片中的类型就必须实现 `Clone` 接口。

`Copy` trait 允许你仅通过复制存储在栈上的数据来复制一个值，无需执行任何自定义代码。有关 `Copy` 的更多信息，请参阅第4章中的[“仅限栈的数据复制”][stack-only-data-copy]<!-- ignore -->部分。

`Copy` trait 并没有定义任何方法来防止程序员重载这些方法，从而避免违反“不会运行任意代码”的假设。这样一来，所有程序员都可以认为复制一个值的过程会非常快速。

你可以将 `Copy` 推导出来，适用于所有其各个部分都实现了 `Copy` 的类型。一个实现了 `Copy` 的类型也必须实现 `Clone`，因为实现了 `Copy` 的类型有一个简单的实现，该实现执行与 `Copy` 相同的任务。

`Copy` trait 很少被需要；实现了 `Copy` 的类型可以享受到优化，这意味着你不必调用 `clone`，这样会使代码更加简洁。

使用 `Copy` 可以完成所有可能的事情，你也可以使用 `Clone` 来实现同样的功能，不过代码可能会更慢，或者在某些地方需要使用 `clone`。

### 使用 `Hash` 将值映射到固定大小的值

`Hash` trait 允许你取一个任意大小的类型实例，并使用哈希函数将该实例映射到一个固定大小的值。`Hash` 的派生实现了 `hash` 方法。`hash` 方法的派生实现会将对类型各个部分调用 `hash` 的结果结合起来，这意味着所有字段或值也必须实现 `Hash` 才能派生出 `Hash`。

在存储数据时，需要使用 `Hash` 的情况之一就是在 `HashMap<K, V>` 中存储键，以实现高效的数据存储。

### 默认值为 `Default`

`Default` trait 允许你为某个类型创建一个默认值。派生类`Default`实现了`default`函数。`default`函数的派生实现会调用`default`函数，该函数在类型的每个部分上都会执行此操作，这意味着类型中的所有字段或值也必须实现`Default`，才能派生出`Default`。

`Default::default`函数通常与第5章中讨论的[“使用结构更新语法从其他实例创建实例”][creating-instances-from-other-instances-with-struct-update-syntax]<!--
ignore -->部分中的结构更新语法一起使用。你可以自定义结构中的几个字段，然后为其余字段设置并使用默认值，使用的是`..Default::default()`。

例如，当您在`Option<T>`实例上使用`unwrap_or_default`方法时，需要包含`Default` trait。如果`Option<T>`是`None`，那么`unwrap_or_default`方法将返回存储在`Option<T>`中的`T`类型的`Default::default`的结果。

[creating-instances-from-other-instances-with-struct-update-syntax]: ch05-01-defining-structs.html#creating-instances-from-other-instances-with-struct-update-syntax
[stack-only-data-copy]: ch04-01-what-is-ownership.html#stack-only-data-copy
[variables-and-data-interacting-with-clone]: ch04-01-what-is-ownership.html#variables-and-data-interacting-with-clone
[custom-derive-macros]: ch20-05-macros.html#custom-derive-macros
