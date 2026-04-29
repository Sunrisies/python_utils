## 定义与实例化结构体

结构体与元组类似，在“元组类型”一节中有过讨论。两者都包含多个相关的数值。与元组一样，结构体的各个元素可以是不同的类型。但与元组不同的是，在结构中，你可以为每个数据元素命名，从而明确其含义。这种命名方式使得结构体比元组更加灵活：你不必依赖数据的顺序来指定或访问实例中的值。

要定义一个结构体，我们需要输入关键字 ``struct``，然后为整个结构体命名。结构体的名称应该能够描述将其中的数据组合在一起的意义。接下来，在花括号内，我们可以定义这些数据的名称和类型，这些数据被称为`_fields_`。例如，清单5-1展示了一个用于存储用户账户信息的结构体。

<列表编号="5-1" 文件名称="src/main.rs" 标题="一个`User`结构体定义">

```rust
{{#rustdoc_include ../listings/ch05-using-structs-to-structure-related-data/listing-05-01/src/main.rs:here}}
```

</清单>

要在定义结构体之后使用它，我们需要为该结构中的每个字段指定具体的值，从而创建一个该结构的实例。创建实例时，先声明该结构的名称，然后加上包含`key:value`对的花括号，其中键是字段的名称，值则是我们想要存储在这些字段中的数据。我们不需要按照在结构中声明的顺序来指定字段。换句话说，结构体定义就像是一个通用的类型模板，而实例则是通过填充这个模板来具体数据，从而创建该类型的对象。例如，我们可以像清单5-2中所示，声明一个特定的用户。

<列表编号="5-2" 文件名称="src/main.rs" 标题="创建`User`结构的实例">

```rust
{{#rustdoc_include ../listings/ch05-using-structs-to-structure-related-data/listing-05-02/src/main.rs:here}}
```

</清单>

要从结构体中获取特定的值，我们使用点符号表示法。例如，要访问该用户的电子邮件地址，我们使用`user1.email`。如果实例是可变的，我们可以通过使用点符号表示法并将值赋给特定的字段来修改它。清单5-3展示了如何修改可变的`User`实例中的`email`字段的值。

<列表编号="5-3" 文件名称="src/main.rs" 标题="更改 `User` 实例中 `email` 字段的值">

```rust
{{#rustdoc_include ../listings/ch05-using-structs-to-structure-related-data/listing-05-03/src/main.rs:here}}
```

</清单>

请注意，整个实例必须是可变的；Rust不允许我们只将某些字段标记为可变。与任何表达式一样，我们可以在函数体的最后一步构造一个新的结构实例，并将其隐式返回。

清单5-4展示了一个`build_user`函数，该函数返回一个包含给定电子邮件和用户名在内的`User`实例。`active`字段获取的值就是`true`，而`sign_in_count`则获取的值为`1`。

<listing number="5-4" file-name="src/main.rs" caption="一个`build_user`函数，该函数接收电子邮件和用户名作为参数，并返回一个`User`实例">

```rust
{{#rustdoc_include ../listings/ch05-using-structs-to-structure-related-data/listing-05-04/src/main.rs:here}}
```

</清单>

将函数的参数命名为与结构体字段相同的名称是合理的，但不得不重复``email``和``username``这些字段名称和变量确实有点麻烦。如果结构体的字段更多，重复每个名称会更加令人烦恼。幸运的是，有一个方便的简写方式！

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="在变量和字段名称相同时使用field-init缩写方式"></a>

### 使用Field Init缩写方式

由于清单5-4中的参数名称和结构字段名称完全相同，我们可以使用`_field init`简写语法来重写`build_user`，使其具有相同的功能，但不再包含`username`和`email`中的重复代码，如清单5-5所示。

<列表编号="5-5" 文件名称="src/main.rs" 标题="一个`build_user`函数，该函数使用字段初始化简写，因为`username`和`email`参数与结构体字段的名称相同>

```rust
{{#rustdoc_include ../listings/ch05-using-structs-to-structure-related-data/listing-05-05/src/main.rs:here}}
```

</清单>

在这里，我们创建了一个新的`User`结构体的实例，该结构体有一个名为`email`的字段。我们希望将`email`字段的值设置为`build_user`函数中`email`参数所包含的值。由于`email`字段和`email`参数具有相同的名称，因此我们只需要编写`email`而不是`email: email`。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="通过结构更新语法从其他实例创建实例"></a>

### 使用结构更新语法创建实例

通常，创建一个新的结构体实例是非常有用的，该实例包含了同一类型另一个实例中的大部分值，但其中一些值进行了修改。你可以使用结构体更新语法来实现这一点。

首先，在清单5-6中，我们展示了如何以常规方式在`user2`中创建新的`User`实例，而不使用更新语法。我们为`email`设置了一个新的值，但在其他方面仍然使用在清单5-2中创建的`user1`中的相同值。

<列表编号="5-6" 文件名称="src/main.rs" 标题="使用`user1`中的除一个值之外的所有值来创建新的`User`实例">

```rust
{{#rustdoc_include ../listings/ch05-using-structs-to-structure-related-data/listing-05-06/src/main.rs:here}}
```

</清单>

通过使用结构更新语法，我们可以用更少的代码实现相同的效果，如清单5-7所示。语法`..`表示那些未明确设置的字段应该具有与给定实例中字段相同的值。

<列表编号="5-7" 文件名称="src/main.rs" 标题="使用struct update语法为`User`实例设置新的`email`值，同时保留来自`user1`的其他值">

```rust
{{#rustdoc_include ../listings/ch05-using-structs-to-structure-related-data/listing-05-07/src/main.rs:here}}
```

</清单>

清单5-7中的代码还在`user2`中创建了一个实例，该实例的`email`具有不同的值，但`username`、`active`和`sign_in_count`字段的值与`user1`中的值相同。`..user1`必须放在最后，以指定其余字段的值应从`user1`中的相应字段获取，但我们也可以选择直接指定这些值。我们希望以任意顺序访问多个字段，而不受结构体定义中字段顺序的影响。

请注意，结构更新语法使用``=``作为赋值操作；这是因为它移动了数据，就像我们在[“变量与数据交互”][move]章节中看到的那样。在这个例子中，在创建``user2``之后，我们无法再使用``user1``，因为``user1``中的``username``字段里的``String``已经被移到了``user2``中。如果我们给``user2``分配了新的``String``值的话……无论是`email`还是`username`，因此只使用了来自`user1`的`active`和`sign_in_count`的值。那么在创建`user2`之后，`user1`仍然有效。`active`和`sign_in_count`都是实现了`Copy`特性的类型，因此我们在[“仅堆栈数据：复制”][copy]<!-- ignore -->部分中讨论的行为仍然适用。在这个例子中，我们仍然可以使用`user1.email`。因为其值并未移出`user1`。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="使用无命名字段的元组结构来创建不同类型"></a>

### 使用元组结构体创建不同类型的对象

Rust还支持类似于元组的结构体，称为“元组结构体”。  
元组结构体具有结构体名称所赋予的额外含义，但其字段并不具有名称；它们只是包含字段的类型而已。当您希望给整个元组一个名称，并且使该元组与其他元组区分开来时，使用元组结构体非常有用。此外，当为每个字段命名时，在常规结构体中这样做可能会显得冗长或多余。

要定义一个元组结构体，首先使用 ``struct`` 关键字，然后是该结构体的名称，最后加上元组中的类型。例如，这里我们定义了两个名为 ``Color`` 和 ``Point`` 的元组结构体：

<listing file-name="src/main.rs">

```rust
{{#rustdoc_include ../listings/ch05-using-structs-to-structure-related-data/no-listing-01-tuple-structs/src/main.rs}}
```

</清单>

请注意，``black``和``origin``的值是不同类型的，因为它们是不同元组结构实例。您定义的每个结构都是独立的类型，即使结构内的字段可能具有相同的类型。例如，一个接受类型为``Color``参数的函数不能接受``Point``作为参数，尽管这两种类型都由三个``i32``组成。值。否则，元组结构实例与元组类似，你可以将它们分解成各个部分，并且可以使用 ``.`` 加上索引来访问单个值。与元组不同的是，元组结构在分解时需要为结构类型命名。例如，我们会使用 ``let Point(x, y, z) = origin;`` 来分解它们。在`origin`中的值指向名为`x`、`y`和`z`的变量。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="没有字段的单元级结构"></a>

### 定义类似单元的结构

您还可以定义没有任何字段的结构体！这些被称为“类结构体”，因为它们的行为类似于我们在[“元组类型”][tuples]章节中提到的`()`类型。当您需要在某种类型上实现某个特性，但该类本身没有任何需要存储的数据时，类结构体就非常有用。我们将在第十章中讨论特性。以下是一个声明和实例化名为`AlwaysEqual`的类结构体的示例：

<listing file-name="src/main.rs">

```rust
{{#rustdoc_include ../listings/ch05-using-structs-to-structure-related-data/no-listing-04-unit-like-structs/src/main.rs}}
```

</清单>

要定义 `AlwaysEqual`，我们使用 `struct` 这个关键字，也就是我们想要的名称，然后加上一个分号。不需要使用花括号或圆括号！然后，我们可以以类似的方式在 `subject` 变量中获取 `AlwaysEqual` 的实例，同样使用我们定义的名称，而不需要任何花括号或圆括号。想象一下，之后我们会为这种类型实现一些行为，使得每个 `AlwaysEqual` 的实例始终等于任何其他类型的实例。为了测试目的，我们拥有已知的结果。我们不需要任何数据来实施这种行为！在第10章中，你将了解到如何定义特性，并将其应用于任何类型，包括类似单元的结构体。

> ### 结构数据的所有权>> 在清单5-1中的`User`结构定义中，我们使用了属于自身的`String`类型，而不是`&str`字符串切片类型。这是一个有意为之的选择，因为我们希望每个结构实例都能拥有其所有数据，并且这些数据在整个结构仍然有效的情况下仍然有效。此外，结构也可以存储对由其他对象拥有的数据的引用。否则，但要做到这一点需要使用Rust中的一个特性——**生命周期**。我们将在第十章中讨论这一特性。生命周期确保结构体中引用的数据在整个结构体存在期间都是有效的。假设您尝试在不指定生命周期的情况下将引用存储在一个结构中，比如在*src/main.rs*中的以下代码；这是无法工作的：

```
<!-- 无法提取内容，请参阅 https://github.com/rust-lang/mdBook/issues/1127 --> 
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
</listing>
```编译器会提示需要生命周期说明符：>> ```console
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
> ```>> 在第十章中，我们将讨论如何修复这些错误，以便可以在结构体中使用引用来存储数据。不过目前，我们可以使用像`String`这样的拥有类型来修复这类错误，而不是使用像`&str`这样的引用。

<!-- 手动重新生成
针对上述错误
在运行update-rustc.sh之后：
使用pbcopy命令复制文件 listings/ch05-using-structs-to-structure-related-data/no-listing-02-reference-in-struct/output.txt
将上述内容粘贴到编辑器中
在每行之前添加`> ` -->

[tuples]: ch03-02-data-types.html#the-tuple-type  
[move]: ch04-01-what-is-ownership.html#variables-and-data-interacting-with-move  
[copy]: ch04-01-what-is-ownership.html#stack-only-data-copy