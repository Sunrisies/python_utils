## 定义和实例化结构体

结构体与元组类似，在[“元组类型”][tuples]<!--
ignore -->这一节中有过讨论。两者都用于存储多个相关的数值。与元组一样，结构体的各个元素可以是不同的类型。但与元组不同的是，在结构体中，你需要为每个数据元素命名，这样就能明确其含义。这种命名方式使得结构体比元组更加灵活：你不必依赖数据的顺序来指定或访问实例中的值。

要定义一个结构体，我们需要输入关键字 `struct`，然后为整个结构体命名。结构体的名称应该能够描述被组合在一起的数据片段的重要性。接下来，在花括号内，我们需要定义这些数据的名称和类型，这些名称被称为 `_fields_`。例如，列表5-1展示了一个用于存储用户账户信息的结构体。

<Listing number="5-1" file-name="src/main.rs" caption="A `User` struct definition">

```rust
struct User {
    active: bool,
    username: String,
    email: String,
    sign_in_count: u64,
}

```

</Listing>

在定义了一个结构体之后，要使用该结构体，我们需要为该结构体的每个字段指定具体的值，从而创建一个该结构体的实例。创建实例的方法很简单：先说出该结构体的名称，然后加上包含键值对的花括号，其中键是字段的名称，值则是我们想要存储在这些字段中的数据。不必按照在结构体中声明的顺序来指定字段。换句话说，结构体的定义就像是一个通用的模板，而实例则是用具体的数据填充这个模板，从而创建出该类型的对象。例如，我们可以像清单5-2中所示，定义一个特定的用户。

<Listing number="5-2" file-name="src/main.rs" caption="Creating an instance of the `User` struct">

```rust
fn main() {
    let user1 = User {
        active: true,
        username: String::from("someusername123"),
        email: String::from("someone@example.com"),
        sign_in_count: 1,
    };
}

```

</Listing>

要从一个结构体中获取特定的值，我们可以使用点符号。例如，要访问这个用户的电子邮件地址，我们可以使用 `user1.email`。如果该实例是可变的，我们可以通过使用点符号并将值赋给特定的字段来修改它。列表5-3展示了如何修改可变 `User` 实例中的 `email` 字段的值。

<Listing number="5-3" file-name="src/main.rs" caption="Changing the value in the `email` field of a `User` instance">

```rust
fn main() {
    let mut user1 = User {
        active: true,
        username: String::from("someusername123"),
        email: String::from("someone@example.com"),
        sign_in_count: 1,
    };

    user1.email = String::from("anotheremail@example.com");
}

```

</Listing>

请注意，整个实例必须是可变的；Rust不允许我们只将某些字段标记为可变。与任何表达式一样，我们可以构造一个新的结构体实例，并将其作为函数体内的最后一个表达式来隐式返回该新实例。

列表5-4展示了一个 `build_user` 函数，该函数返回一个 `User` 实例，该实例具有给定的电子邮件和用户名。`active` 字段获取值 `true`，而 `sign_in_count` 则获取值 `1`。

<Listing number="5-4" file-name="src/main.rs" caption="A `build_user` function that takes an email and username and returns a `User` instance">

```rust
fn build_user(email: String, username: String) -> User {
    User {
        active: true,
        username: username,
        email: email,
        sign_in_count: 1,
    }
}

```

</Listing>

将函数的参数命名为与结构体字段相同的名称是合理的，但是需要重复使用 `email` 和 `username` 这些字段名和变量确实有点麻烦。如果结构体有更多的字段，重复这些名称会更加令人烦恼。幸运的是，有一个方便的简写方式！

<!-- Old headings. Do not remove or links may break. -->

<a id="using-the-field-init-shorthand-when-variables-and-fields-have-the-same-name"></a>

### 使用 Field Init 简写方式

由于清单5-4中的参数名称和结构体字段名称完全相同，我们可以使用`_field init`简写语法来重写`build_user`，使其具有相同的行为，同时避免了`username`和`email`的重复代码，如清单5-5所示。

<Listing number="5-5" file-name="src/main.rs" caption="A `build_user` function that uses field init shorthand because the `username` and `email` parameters have the same name as struct fields">

```rust
fn build_user(email: String, username: String) -> User {
    User {
        active: true,
        username,
        email,
        sign_in_count: 1,
    }
}

```

</Listing>

在这里，我们创建了一个新的 `User` 结构实例，该实例有一个名为 `email` 的字段。我们希望将 `email` 字段的值设置为 `build_user` 函数中 `email` 参数中的值。由于 `email` 字段和 `email` 参数具有相同的名称，因此我们只需要写 `email` 而不是 `email: email`。

<!-- Old headings. Do not remove or links may break. -->

<a id="creating-instances-from-other-instances-with-struct-update-syntax"></a>

### 使用结构体更新语法创建实例

通常，创建一个包含另一个相同类型实例中的大部分值，但修改其中一些值的结构体实例是非常有用的。你可以使用结构体更新语法来实现这一点。

首先，在列表5-6中，我们展示了如何以常规方式在 `user2` 中创建一个新的 `User` 实例，而不使用更新语法。我们为 `email` 设置了一个新的值，但在其他方面仍然使用在列表5-2中创建的 `user1` 中的相同值。

<Listing number="5-6" file-name="src/main.rs" caption="Creating a new `User` instance using all but one of the values from `user1`">

```rust
fn main() {
    // --snip--

    let user2 = User {
        active: user1.active,
        username: user1.username,
        email: String::from("another@example.com"),
        sign_in_count: user1.sign_in_count,
    };
}

```

</Listing>

通过使用结构更新语法，我们可以用更少的代码实现相同的效果，如清单5-7所示。该语法 `..` 表示那些未被明确设置的字段应该具有与给定实例中字段相同的值。

<Listing number="5-7" file-name="src/main.rs" caption="Using struct update syntax to set a new `email` value for a `User` instance but to use the rest of the values from `user1`">

```rust
fn main() {
    // --snip--

    let user2 = User {
        email: String::from("another@example.com"),
        ..user1
    };
}

```

</Listing>

清单5-7中的代码还创建了一个在 `user2` 中的实例，该实例在 `email` 中有不同的值，但在 `username`、`active` 和 `sign_in_count` 字段中拥有与 `user1` 相同的数值。`..user1` 必须放在最后，以指定其余字段的值应从 `user1` 中对应的字段获取。不过，我们可以按照任意顺序为任意数量的字段指定值，而无需考虑结构体定义中字段的顺序。

请注意，结构更新语法使用 `=` 作为赋值操作；这是因为它移动了数据，正如我们在[“变量与数据交互”][move]<!-- ignore -->部分所看到的那样。在这个例子中，我们在创建 `user2` 之后不能再使用 `user1`，因为 `username` 字段中的 `String` 已经被移到了 `user2` 中。如果我们为 `email` 和 `username` 分别赋予了新的 `user2` 值，并且只使用了来自 `user1` 的 `active` 和 `sign_in_count` 值，那么即使在创建 `user2` 之后， `user1` 仍然有效。 `active` 和 `sign_in_count` 都是实现了 `Copy` 特性的类型，因此我们在[“仅栈式数据：复制”][copy]<!-- ignore -->部分讨论的行为仍然适用。在这个例子中，我们仍然可以使用 `user1.email`，因为它的数值并没有从 `user1` 中移出。

<!-- Old headings. Do not remove or links may break. -->

<a id="using-tuple-structs-without-named-fields-to-create-different-types"></a>

### 使用元组结构体创建不同类型的对象

Rust还支持类似于元组的结构体，称为“元组结构体”。  
元组结构体具有结构体名称所赋予的额外含义，但它们没有与字段相关联的名称；它们只是包含字段的类型。当您希望为整个元组指定一个名称，并且希望该元组与其他元组区分开来时，元组结构体非常有用。此外，当为每个字段命名时，如在普通结构体中那样做会显得冗长或多余。

要定义一个元组结构体，首先使用`struct`关键字，然后指定结构体名称，接着列出元组中的各个类型。例如，这里我们定义并使用了两个名为`Color`和`Point`的元组结构体。

<Listing file-name="src/main.rs">

```rust
struct Color(i32, i32, i32);
struct Point(i32, i32, i32);

fn main() {
    let black = Color(0, 0, 0);
    let origin = Point(0, 0, 0);
}

```

</Listing>

请注意，`black`和`origin`的值是不同类型的，因为它们是不同元组结构体的实例。您定义的每个结构体都是独立的类型，即使结构体内部的字段可能具有相同的类型。例如，一个接受类型为`Color`参数的函数不能接受`Point`作为参数，尽管这两种类型都由三个`i32`值组成。否则，元组结构体实例与元组类似，您可以将其拆解为各个独立的元素，并且可以使用`.`后跟索引来访问单个值。与元组不同的是，元组结构体在拆分时需要为结构体类型命名。例如，我们会使用`let Point(x, y, z) = origin;`来将`origin`中的值拆解为名为`x`、`y`和`z`的变量。

<!-- Old headings. Do not remove or links may break. -->

<a id="unit-like-structs-without-any-fields"></a>

### 定义类似单位的结构体

您还可以定义没有任何字段的结构体！这些结构体被称为“类似单位的结构体”，因为它们的行为类似于我们在[“元组类型”][tuples]<!-- ignore -->章节中提到的单位类型 `()`。当您需要在某个类型上实现某个特性，但该类型本身没有任何数据需要存储时，类似单位的结构体就非常有用。我们将在第十章中讨论特性。以下是一个声明并实例化名为 `AlwaysEqual` 的单位结构体的示例：

<Listing file-name="src/main.rs">

```rust
struct AlwaysEqual;

fn main() {
    let subject = AlwaysEqual;
}

```

</Listing>

要定义 `AlwaysEqual`，我们使用 `struct` 这个关键字，也就是我们想要的名称，然后加上分号。不需要使用花括号或圆括号！然后，我们可以以类似的方式在 `subject` 变量中得到一个 `AlwaysEqual` 的实例，同样使用我们定义的名称，而不需要任何花括号或圆括号。想象一下，之后我们为这种类型实现了一些行为，使得每个 `AlwaysEqual` 的实例始终等于任何其他类型的实例，这样在测试时就能得到已知的结果。为了实现这种行为，我们不需要任何数据！在第十章中，你将看到如何定义特质，并如何在任何类型上实现它们，包括类似单元的结构体。

> ### 结构数据的所有权  
在清单5-1中的结构定义中，我们使用了“owned `String`”类型，而不是“ `&str`”字符串切片类型。这是一个有意为之的选择，因为我们希望每个结构实例都能拥有其所有数据，并且这些数据在整个结构有效期间都是有效的。  

结构也可以存储对其他对象所拥有的数据的引用，但这样做需要使用“_lifetimes_”这一Rust特性，我们将在第十章中详细讨论。Lifetimes确保结构所引用的数据在整个结构有效期间都是有效的。假设你在没有指定生命周期的情况下尝试在结构中存储引用，比如在*src/main.rs*中这样做，这是不会生效的：  

```rust
 <Listing file-name="src/main.rs">
 <!-- CAN'T EXTRACT SEE https://github.com/rust-lang/mdBook/issues/1127 -->
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
 </Listing>
```  

编译器会提示需要指定生命周期：  

```rust
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
```  

在第十章中，我们将讨论如何修复这些错误，以便可以在结构中存储引用。但现在，我们将使用“owned `String`”类型来修复这类错误，而不是使用“ `&str`”类型的引用。

<!-- manual-regeneration
for the error above
after running update-rustc.sh:
pbcopy < listings/ch05-using-structs-to-structure-related-data/no-listing-02-reference-in-struct/output.txt
paste above
add `> ` before every line -->

[tuples]: ch03-02-data-types.html#the-tuple-type
[move]: ch04-01-what-is-ownership.html#variables-and-data-interacting-with-move
[copy]: ch04-01-what-is-ownership.html#stack-only-data-copy
