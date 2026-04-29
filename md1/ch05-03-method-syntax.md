## 方法

方法类似于函数：我们使用 ``fn`` 关键字以及一个名称来声明它们。方法可以拥有参数和返回值，并且包含一些在从其他地方调用该方法时执行的代码。与函数不同的是，方法是在结构体（或者枚举或特质对象）的上下文中定义的，这些概念我们在[第6章][enums]<!-- 忽略 -->和[第18章][trait-objects]<!-- 忽略 -->中分别进行了介绍。方法的第一个参数总是 ``self``，它代表了被调用该方法的那个结构体的实例。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="定义方法"></a>

### 方法语法

让我们修改 `area` 这个函数，该函数有一个 `Rectangle` 类型的参数。相反，我们会在 `Rectangle` 结构体上定义一个 `area` 方法，如清单 5-13 所示。

<listing number="5-13" file-name="src/main.rs" caption="在 `Rectangle` 结构体中定义 `area` 方法">

```rust
{{#rustdoc_include ../listings/ch05-using-structs-to-structure-related-data/listing-05-13/src/main.rs}}
```

</ Listing>

为了在 `Rectangle` 的上下文中定义该函数，我们首先为 `Rectangle` 启动一个 `impl` (实现) 块。在这个 `impl` 块内的所有内容都将与 `Rectangle` 类型相关联。接着，我们将 `area` 函数移动到 `impl` 的花括号内，并在签名中以及函数的主体中将第一个参数改为 `self`。在 `main` 中，我们调用了 `area` 函数，并将 `rect1` 作为参数传递。此时，我们可以使用 _method 语法来调用 `area` 方法，从而实现对 `Rectangle` 实例的访问。方法语法格式为：在实例之后加上一个点，然后依次是方法名、括号以及任何参数。

在 `area` 的签名中，我们使用 `&self` 而不是 `rectangle: &Rectangle`。实际上，`&self` 是 `self: &Self` 的缩写。在 `impl` 块中，类型 `Self` 是 `impl` 块的类型的别名。方法必须有一个名为 `self` 的参数，该参数的类型为 `Self`。因此，Rust允许我们在第一个参数位置仅使用 `self` 这个缩写。需要注意的是，我们仍然需要在 `self` 前面使用 `&` 来表明该方法借用的是 `Self` 实例，就像我们在 `rectangle: &Rectangle` 中所做的那样。方法可以拥有 `self` 的所有权，也可以不可变地借用 `self`，就像我们在这里所做的那样，或者可以可变地借用 `self`，就像它们可以借用任何其他参数一样。

我们在这里选择 `&self` 的原因，与我们在函数中使用 `&Rectangle` 的原因相同。  
版本说明：我们不希望拥有该实例的所有权，只是想读取结构体中的数据，而不是对其进行修改。如果我们想要改变调用该方法的实例，我们会使用 `&mut self` 作为第一个参数。通常，只有当方法需要将 `self` 转换为其他形式，并且希望防止调用者在转换后继续使用原始实例时，才会使用仅以 `self` 作为第一个参数的方法。

使用方法而非函数的主要原因，除了提供方法语法以及不必在每个方法的签名中重复``self``的类型之外，还有组织上的考虑。我们将类型实例所能执行的所有操作集中在一个``impl``块中，而不是让未来的代码使用者需要在我们提供的库中的各个地方寻找``Rectangle``的功能。

请注意，我们可以选择让一个方法的名称与结构体中的一个字段的名称相同。例如，我们可以在`Rectangle`上定义一个方法，该方法的名称也是`width`：

<code listing file-name="src/main.rs">

```rust
{{#rustdoc_include ../listings/ch05-using-structs-to-structure-related-data/no-listing-06-method-field-interaction/src/main.rs:here}}
```

</ Listing>

在这里，我们选择让 `width` 方法在实例的 `width` 字段中的值大于 `0` 时返回 `true`；而当该值为 `0` 时则返回 `false`。我们可以在任何情况下使用同名字段。在 `main` 中，当我们用括号跟随 `rect1.width` 时，Rust 会知道我们指的是方法 `width`。而当我们不使用括号时，Rust 会知道我们指的是字段 `width`。

通常，但并非总是如此，当我们给一个方法命名与字段相同的时候，我们希望该方法只能返回字段中的值，而不执行其他操作。这类方法被称为_获取器_，而Rust并不像其他一些语言那样自动实现这些功能。获取器的使用非常有用，因为你可以将字段设为私有，而将方法设为公有，从而让该字段只能通过公共API进行只读访问。我们将在[第7章][public]<!-- ignore -->中讨论什么是公有和私有，以及如何将一个字段或方法指定为公有或私有。

> ### `->` 运算符在哪里？
>
> 在C和C++中，有两种不同的运算符用于调用方法：如果你直接对对象调用方法，则使用`.`；如果你是通过指向对象的指针来调用方法，并且需要先解引用该指针，则使用`->`。换句话说，如果`object`是一个指针，那么`object->something()`与`(*object).something()`类似。
>
> Rust中没有与之对应的`->`运算符；相反，Rust有一个名为“自动引用和解引用”的特性。调用方法是Rust中少数几个具有这种特性的地方之一。
>
> 其工作原理如下：当你使用`object.something()`调用方法时，Rust会自动添加`&`、`&mut`或`*`，使得`object`与方法的签名相匹配。换句话说，以下两种情况实际上是相同的：
>
> <!-- CAN'T EXTRACT SEE BUG https://github.com/rust-lang/mdBook/issues/1127 -->
>
> ```rust
> # #[derive(Debug,Copy,Clone)]
> # struct Point {
> #     x: f64,
> #     y: f64,
> # }
> #
> # impl Point {
> #    fn distance(&self, other: &Point) -> f64 {
> #        let x_squared = f64::powi(other.x - self.x, 2);
> #        let y_squared = f64::powi(other.y - self.y, 2);
> #
> #        f64::sqrt(x_squared + y_squared)
> #    }
> # }
> # let p1 = Point { x: 0.0, y: 0.0 };
> # let p2 = Point { x: 5.0, y: 6.5 };
> p1.distance(&p2);
> (&p1).distance(&p2);
> ```
>
> 第一种方式看起来更简洁。这种自动引用行为之所以有效，是因为方法有一个明确的接收者——即`self`的类型。根据方法的接收者和名称，Rust可以明确地判断该方法是在读取数据（`&self`）、修改数据（`&mut self`）还是消耗数据（`self`）。Rust让方法的接收者具有隐式的借用特性，这是使所有权机制在实际使用中更加便捷的一个重要因素。

### 具有更多参数的方法

让我们通过在一个名为 `Rectangle` 的结构体上实现第二个方法来练习使用方法的使用。这次，我们希望一个 `Rectangle` 的实例能够接收另一个 `Rectangle` 的实例，并且如果第二个 `Rectangle` 可以完全容纳在 `self` 中（即第一个 `Rectangle`），则它应该返回 `true`；否则，它应该返回 `false`。也就是说，一旦我们定义了 `can_hold` 方法之后，我们就可以像清单 5-14 中展示的那样编写程序了。

<列表编号="5-14" 文件名称="src/main.rs" 标题="使用尚未定义的 `can_hold` 方法">

```rust,ignore
{{#rustdoc_include ../listings/ch05-using-structs-to-structure-related-data/listing-05-14/src/main.rs}}
```

</ Listing>

预期的输出结果如下：因为`rect2`的两个维度都小于`rect1`的维度，但是`rect3`的宽度大于`rect1`的宽度。

```text
Can rect1 hold rect2? true
Can rect1 hold rect3? false
```

我们知道需要定义一个方法，因此它将会位于 ``impl Rectangle`` 块中。该方法的名称将是 ``can_hold``，并且它将接收一个不可变的引用作为参数，这个引用指向另一个 ``Rectangle`` 对象。我们可以通过查看调用该方法的代码来确定参数的类型：`rect1.can_hold(&rect2)` 将传递 `&rect2`，这是一个不可变的引用，而 `&rect2` 又指向 `rect2`，后者是 `Rectangle` 的一个实例。这样做是有道理的，因为我们只需要读取 `rect2`（而不是写入，那样就需要一个可变的引用），同时我们希望 `main` 能够保留对 `rect2` 的所有权，这样我们就可以在调用 `can_hold` 方法之后再次使用它。`can_hold` 的返回值将是一个布尔值，而实现部分会检查 `self` 的宽度和高度是否大于另一个 `Rectangle` 的宽度和高度。现在，让我们在 Listing 5-13 中的 `impl` 块中添加新的 `can_hold` 方法，如 Listing 5-15 所示。

<listing number="5-15" file-name="src/main.rs" caption="在`Rectangle`上实现`can_hold`方法，该方法接受一个`Rectangle`实例作为参数">

```rust
{{#rustdoc_include ../listings/ch05-using-structs-to-structure-related-data/listing-05-15/src/main.rs:here}}
```

</ Listing>

当我们使用清单5-14中的`main`函数运行这段代码时，我们将得到期望的输出。方法可以接受多个参数，这些参数可以在`self`参数之后添加到方法的签名中，这些参数的工作原理与函数中的参数相同。

### 相关函数

在 ``impl`` 块中定义的所有函数都是_关联函数_，因为它们与名为 ``impl`` 的类型相关联。我们可以定义一些没有 ``self`` 作为其第一个参数的关联函数（因此不是方法），因为这些函数不需要该类型的实例就能正常工作。我们已经使用过一个这样的函数：就是定义在 ``String`` 类型上的 ``String::from`` 函数。

那些不是方法的关联函数，通常被用于创建结构体的构造函数中。这些函数通常被称为`new`，但`new`并不是一个特殊的名称，也不是语言内置的。例如，我们可以选择提供一个名为`square`的关联函数，该函数有一个维度参数，并将其用作宽度和高度，这样就能更容易地创建一个正方形`Rectangle`，而不需要两次指定相同的数值。

<span class="filename">文件名：src/main.rs</span>

```rust
{{#rustdoc_include ../listings/ch05-using-structs-to-structure-related-data/no-listing-03-associated-functions/src/main.rs:here}}
```

在返回类型和函数的主体中，`Self`这个关键字实际上是`impl`关键字的别名，而`impl`这个关键字对应的类型就是`Rectangle`。

要调用这个关联函数，我们使用 ``::`` 语法，并带上结构体的名称；``let sq = Rectangle::square(3);`` 是一个示例。这个函数是由结构体来命名的：``::`` 语法既用于关联函数，也用于由模块创建的名称空间。我们将在[第7章][modules]中讨论模块。

### 多个`impl`块

每个结构体都可以包含多个`impl`块。例如，清单5-15与清单5-16中的代码是等效的，其中每个方法都位于自己的`impl`块中。

<Listing number="5-16" caption="重新编写清单5-15，使用多个`impl`块">

```rust
{{#rustdoc_include ../listings/ch05-using-structs-to-structure-related-data/listing-05-16/src/main.rs:here}}
```

</ Listing>

没有必要将这些方法分开到多个`impl`块中，但这种语法是有效的。我们将在第十章中看到使用多个`impl`块的例子，届时我们会讨论泛型类型和特质的相关内容。

## 总结

结构体允许你创建对特定领域有意义的自定义类型。通过使用结构体，你可以将相关的数据片段相互连接，并为每个部分命名，从而使代码更加清晰。在`impl`块中，你可以定义与你的类型相关联的函数，而方法则是一种关联函数，它允许你指定结构体实例的行为。

但是，结构体并不是创建自定义类型的唯一方式：让我们利用Rust中的枚举功能，为你的工具箱增添另一种工具吧。

[枚举类型]: ch06-00-enums.html  
[特质对象]: ch18-02-trait-objects.md  
[公共成员]: ch07-03-paths-for-referring-to-an-item-in-the-module-tree.html#exposing-paths-with-the-pub-keyword  
[模块]: ch07-02-defining-modules-to-control-scope-and-privacy.html