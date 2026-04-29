## 定义和实例化结构体

结构体与元组类似，在[“元组类型”][tuples]章节中有过讨论。两者都用于存储多个相关的数值。与元组一样，结构体的各个元素可以是不同的类型。但与元组不同的是，在结构中，你可以为每个数据元素命名，从而明确其含义。这种命名方式使得结构体比元组更加灵活：你不必依赖数据的顺序来指定或访问实例中的值。

要定义一个结构体，我们需要输入关键字 ``struct``，然后为整个结构体命名。结构体的名称应该能够描述将这些数据组合在一起的意义。接下来，在花括号内，我们可以定义这些数据的名称和类型，这些数据被称为`_fields_`。例如，列表5-1展示了一个用于存储用户账户信息的结构体。

<listing number="5-1" file-name="src/main.rs" caption="一个 `User` 结构定义">

```rust
{{#rustdoc_include ../listings/ch05-using-structs-to-structure-related-data/listing-05-01/src/main.rs:here}}
```

</ Listing>

在定义了一个结构体之后，要使用该结构体，我们需要为该结构体的每个字段指定具体的值，从而创建该结构体的实例。创建实例的方法很简单：先说出结构体的名称，然后加上包含`键:值`对的花括号，其中键是字段的名称，值则是我们想要存储在这些字段中的数据。不必按照在结构体中声明的顺序来指定字段。换句话说，结构体的定义就像是一个通用的模板，而实例则通过填充这个模板来创建该类型的对象。例如，我们可以像清单5-2所示，定义一个特定的用户。

<listing number="5-2" file-name="src/main.rs" caption="创建 `User` 结构的实例">

```rust
{{#rustdoc_include ../listings/ch05-using-structs-to-structure-related-data/listing-05-02/src/main.rs:here}}
```

</ Listing>

要从一个结构体中获取特定的值，我们可以使用点符号表示法。例如，要访问这个用户的电子邮件地址，我们使用`user1.email`。如果该实例是可变的，我们可以通过使用点符号并将值赋给特定的字段来修改它。清单5-3展示了如何修改可变的`User`实例中的`email`字段的值。

<listing number="5-3" file-name="src/main.rs" caption="更改 `User` 实例中 `email` 字段的值">

```rust
{{#rustdoc_include ../listings/ch05-using-structs-to-structure-related-data/listing-05-03/src/main.rs:here}}
```

</ Listing>

请注意，整个实例必须是可变的；Rust不允许我们只将某些字段标记为可变。与任何表达式一样，我们可以构造一个新的结构体实例，并将其作为函数体内的最后一个表达式来隐式返回该新实例。

清单5-4展示了一个`build_user`函数，该函数返回一个包含给定电子邮件和用户名信息的`User`实例。`active`字段获取的值就是`true`，而`sign_in_count`则获取了`1`的值。

<listing number="5-4" file-name="src/main.rs" caption="一个`build_user`函数，该函数接收电子邮件和用户名作为参数，并返回一个`User`实例">

```rust
{{#rustdoc_include ../listings/ch05-using-structs-to-structure-related-data/listing-05-04/src/main.rs:here}}
```

</ Listing>

将函数的参数命名为与结构体字段相同的名称是合理的，但是需要重复使用`email`和`username`这些字段名称和变量确实有点麻烦。如果结构体的字段更多，重复每个名称会更加令人烦恼。幸运的是，有一个方便的简写方式！

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="在变量和字段名称相同时使用字段初始化的简写形式"></a>

### 使用字段初始化简写

由于清单5-4中的参数名称和结构体字段名称完全相同，我们可以使用`_field init`简写语法来重写`build_user`，使其具有相同的行为，同时避免了`username`和`email`中的重复代码，如清单5-5所示。

<listing number="5-5" file-name="src/main.rs" caption="一个`build_user`函数，该函数使用字段初始化简写，因为`username`和`email`参数与结构体字段的名称相同">

```rust
{{#rustdoc_include ../listings/ch05-using-structs-to-structure-related-data/listing-05-05/src/main.rs:here}}
```

</ Listing>

在这里，我们创建了一个新的 ``User`` 结构的实例，该结构有一个名为 ``email`` 的字段。我们希望将 ``email`` 字段的值设置为 ``email`` 参数中的值。由于 ``email`` 字段和 ``email`` 参数具有相同的名称，因此我们只需要编写 ``email``，而无需使用 ``email: email``。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="通过结构体更新语法创建实例"></a>

### 使用结构体更新语法创建实例

通常，创建一个包含另一个相同类型实例中的大部分值，但修改其中一些值的结构体实例是非常有用的。你可以使用结构体更新语法来实现这一点。

首先，在清单5-6中，我们展示了如何以常规方式在`user2`中创建新的`User`实例，而不使用更新语法。我们为`email`设置了一个新的值，其余部分则继续使用在清单5-2中创建的`user1`中的相同值。

<列表编号="5-6" 文件名称="src/main.rs" 标题="使用`user1`中的除一个值之外的所有值来创建新的`User`实例">

```rust
{{#rustdoc_include ../listings/ch05-using-structs-to-structure-related-data/listing-05-06/src/main.rs:here}}
```

</ Listing>

通过使用结构更新语法，我们可以用更少的代码实现相同的效果，如清单5-7所示。语法`..`表示那些未明确设置的字段应该具有与给定实例中字段相同的值。

<列表编号="5-7" 文件名称="src/main.rs" 标题="使用结构更新语法为`User`实例设置新的`email`值，同时保留来自`user1`的其他值">

```rust
{{#rustdoc_include ../listings/ch05-using-structs-to-structure-related-data/listing-05-07/src/main.rs:here}}
```

</ Listing>

清单5-7中的代码还在`user2`中创建了一个实例，该实例的`email`具有不同的值，但`username`、`active`和`sign_in_count`字段的值与`user1`中的值相同。`..user1`必须放在最后，以指定其余字段的值应从`user1`中对应的字段获取。不过，我们可以按照任意顺序为任意数量的字段指定值，而无需考虑结构体定义中字段的顺序。

请注意，结构体的更新语法使用了 ``=`` 作为赋值方式；这是因为它移动了数据，就像我们在[“变量与数据交互”][move]这个章节中看到的那样。在这个例子中，在创建 ``user2`` 之后，我们无法再使用 ``user1``，因为 ``user1`` 中的 ``username`` 字段里的 ``String`` 已经被移到了 ``user2`` 中。如果我们为 ``user2`` 分别赋予了新的 ``String`` 值给 ``email`` 和 ``username`$，并且只使用了来自 ``user1`` 的 ``active`` 和 ``sign_in_count`` 值，那么即使在创建 ``user2`` 之后，``user1`` 仍然有效。``active`` 和 ``sign_in_count`` 都是实现了 ``Copy`` 特性的类型，因此我们在[“仅栈式数据：复制”][copy]这个章节中讨论的行为仍然适用。在这个例子中，我们仍然可以使用 ``user1.email`$，因为它的数值并没有被移出 ``user1``。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="使用无命名字段的元组结构体来创建不同类型"></a>

### 使用元组结构体创建不同类型的对象

Rust还支持类似于元组的结构体，称为“元组结构体”。  
元组结构体具有结构体名称所赋予的含义，但它们没有与字段相关联的名称；它们只是包含字段的类型而已。当你希望给整个元组一个名称，并且使该元组与其他元组区分开来时，使用元组结构体非常有用。此外，当为每个字段命名时，在常规结构体中这样做可能会显得冗长或多余。

要定义一个元组结构体，首先使用 ``struct`` 关键字，然后是该结构体的名称，最后加上元组中的类型。例如，这里我们定义了两个名为 ``Color`` 和 ``Point`` 的元组结构体：

<code listing file-name="src/main.rs">

```rust
{{#rustdoc_include ../listings/ch05-using-structs-to-structure-related-data/no-listing-01-tuple-structs/src/main.rs}}
```

</ Listing>

请注意，``black``和``origin``的值是不同类型的，因为它们是不同元组结构体的实例。每个结构体都是独立的类型，即使结构体内部的字段可能具有相同的类型。例如，一个接受类型为``Color``参数的函数不能接受``Point``作为参数，尽管这两种类型都由三个``i32``值组成。否则，元组结构体实例类似于元组，你可以将它们拆分成各个部分，并且可以使用``.``后跟索引来访问单个值。与元组不同的是，元组结构体在拆分时需要为结构体指定类型。例如，我们会使用``let Point(x, y, z) = origin;``来将``origin``中的值拆分成名为``x``、``y``和``z``的变量。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="单元式结构体无需任何字段"></a>

### 定义类似单位的结构体

您还可以定义没有任何字段的结构体！这些被称为“类似单位的结构体”，因为它们的行为类似于我们在[“元组类型”][tuples]章节中提到的`()`类型。当您需要在某种类型上实现某个特性，但又不希望在该类型本身中存储任何数据时，这类结构体非常有用。我们将在第十章中讨论特性。以下是声明并实例化一个名为`AlwaysEqual`的单位结构体的示例：

<code listing file-name="src/main.rs">

```rust
{{#rustdoc_include ../listings/ch05-using-structs-to-structure-related-data/no-listing-04-unit-like-structs/src/main.rs}}
```

</ Listing>

要定义 ``AlwaysEqual``，我们使用 ``struct`` 这个关键词，也就是我们想要的名称，然后加上一个分号。不需要使用花括号或圆括号！接下来，我们可以以类似的方式在 ``subject`` 变量中获取 ``AlwaysEqual`` 的一个实例，同样使用我们定义的名称，而不需要任何花括号或圆括号。想象一下，之后我们会为这种类型实现一些行为，使得每个 ``AlwaysEqual`` 的实例始终等于任何其他类型的实例，这样就能为测试目的获得已知的结果了。为了实现这种行为，我们不需要任何数据！在第10章中，你将了解到如何定义特质，并在任何类型上实现它们，包括类似单元的结构体。

> ### 结构体的所有权  
在清单5-1中的`User`结构体定义中，我们使用了被拥有的`String`类型，而不是`&str`字符串切片类型。这是一个有意为之的选择，因为我们希望每个结构体实例都能拥有其所有数据，并且这些数据在整个结构体有效期间都是有效的。  

结构体也可以存储对其他对象所拥有的数据的引用，但这样做需要使用“生命周期”这一Rust特性，我们将在第十章中详细讨论。生命周期确保结构体引用的数据在整个结构体有效期间都是有效的。例如，如果你尝试在没有指定生命周期的情况下在结构体中使用引用，就像在*src/main.rs*中的以下代码那样，这是不会生效的：  

<清单文件名称="src/main.rs">  
<!-- 无法提取链接：https://github.com/rust-lang/mdBook/issues/1127 -->  
```rust,ignore,does_not_compile
> struct User {
>     active: bool,
>     username: &str,
>     email: &str,
>     sign_in_count: u64,
> }
>
> fn main() {
>     let user1 = User {
>         active: true,
>         username: "someusername123",
>         email: "someone@example.com",
>         sign_in_count: 1,
>     };
> }
> ```  
</清单>  
编译器会提示需要指定生命周期说明符：  
```console
> $ cargo run
>    Compiling structs v0.1.0 (file:///projects/structs)
> error[E0106]: missing lifetime specifier
>  --> src/main.rs:3:15
>   |
> 3 |     username: &str,
>   |               ^ expected named lifetime parameter
>   |
> help: consider introducing a named lifetime parameter
>   |
> 1 ~ struct User<'a> {
> 2 |     active: bool,
> 3 ~     username: &'a str,
>   |
>
> error[E0106]: missing lifetime specifier
>  --> src/main.rs:4:12
>   |
> 4 |     email: &str,
>   |            ^ expected named lifetime parameter
>   |
> help: consider introducing a named lifetime parameter
>   |
> 1 ~ struct User<'a> {
> 2 |     active: bool,
> 3 |     username: &str,
> 4 ~     email: &'a str,
>   |
>
> For more information about this error, try `rustc --explain E0106`.
> error: could not compile `structs` (bin "structs") due to 2 previous errors
> ```  
在第十章中，我们将介绍如何修复这些错误，以便可以在结构体中使用引用。但现在，我们只需使用像`String`这样的拥有型别来替代像`&str`这样的引用型别即可。

<!-- 手动重新生成
针对上述错误
在运行 update-rustc.sh 之后：
使用 pbcopy 复制以下文件：
lists/ch05-using-structs-to-structure-related-data/no-listing-02-reference-in-struct/output.txt
将上述内容粘贴到上面提供的位置
在每行之前添加 `> ` -->

[tuples]: ch03-02-data-types.html#the-tuple-type  
[move]: ch04-01-what-is-ownership.html#variables-and-data-interacting-with-move  
[copy]: ch04-01-what-is-ownership.html#stack-only-data-copy