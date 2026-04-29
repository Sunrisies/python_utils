## 方法

方法类似于函数：我们使用``fn``关键字来声明它们，并且需要指定名称。方法可以拥有参数和返回值，同时包含一些代码，当从其他地方调用该方法时，这些代码会被执行。与函数不同的是，方法是在结构体（或枚举、特质对象）的上下文中定义的，相关内容我们将在《第6章》中关于枚举部分以及《第18章》中关于特质对象部分进行介绍。方法的第一个参数也是类似的。始终使用`self`，它代表了该方法被调用的那个结构体的实例。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="定义方法"></a>

### 方法语法

让我们修改 `area` 这个函数，该函数有一个 `Rectangle` 的实例作为参数。相反，我们会在 `Rectangle` 结构体上定义一个 `area` 方法，如清单 5-13 所示。

<列表编号="5-13" 文件名称="src/main.rs" 标题="在 `Rectangle` 结构体上定义 `area` 方法">

```rust
{{#rustdoc_include ../listings/ch05-using-structs-to-structure-related-data/listing-05-13/src/main.rs}}
```

</清单>

为了在`Rectangle`的上下文中定义该函数，我们首先为`Rectangle`启动一个`impl`(实现)块。该`impl`块内的所有内容都将与`Rectangle`类型相关联。接着，我们将`area`函数移动到`impl`的方括号中，并在签名以及函数的主体中，将第一个参数改为`self`。`main`中，我们调用了`area`函数，并将`rect1`作为参数传递。不过，我们可以使用_method语法来调用`area`方法，作用于我们的`Rectangle`实例。该方法语法是在实例之后使用的：先加上一个点，然后跟上方法名，再接上括号以及任何参数。

在 `area` 的签名中，我们使用 `&self` 而不是 `rectangle: &Rectangle`。`&self`实际上是 `self: &Self`的缩写。在 `impl` 块内，类型 `Self`是 `impl` 块的类型的别名。方法必须有一个名为 `self`的参数，该参数的类型为 `Self`；因此，Rustlet建议在第一个参数位置仅使用 `self`作为缩写。请注意，我们仍然需要在`self`前面使用`&`这个缩写，以表明该方法借用`Self`实例，就像我们在`rectangle: &Rectangle`中所做的那样。方法可以拥有`self`的所有权，也可以不可变地借用`self`，就像我们在这里所做的那样；或者可以可变地借用`self`，就像它们可以借用任何其他参数一样。

我们在这里选择`&self`的原因与在functionversion中使用`&Rectangle`的原因相同：我们不希望拥有该实例的所有权，只是想读取结构体中的数据，而不是对其进行修改。如果我们想要改变调用该方法的实例，作为该方法的一部分，我们会使用`&mut self`作为第一个参数。通常，一个方法仅通过`self`作为第一个参数来拥有该实例的所有权的情况很少见。当该方法将`self`转换为其他形式时，可以使用此选项，以防止调用者在转换后继续使用原始实例。

使用方法而不是函数的主要原因，除了提供方法语法以及不必在每个方法的签名中重复`self`这种类型之外，还有组织上的考虑。我们将能够使用某个类型实例的所有功能都放在一个`impl`块中，而不是让未来的代码使用者需要在我们提供的库中的各个地方寻找`Rectangle`的功能。

请注意，我们可以选择让一个方法的名称与结构体中的某个字段相同。例如，我们可以在`Rectangle`上定义一个方法，该方法的名称也是`width`：

<listing file-name="src/main.rs">

```rust
{{#rustdoc_include ../listings/ch05-using-structs-to-structure-related-data/no-listing-06-method-field-interaction/src/main.rs:here}}
```

</清单>

在这里，我们选择让`width`方法在实例的`width`字段的值大于`0`时返回`true`；而当该值为`0`时则返回`false`。我们可以在同一个名称的字段中使用该方法，用于任何目的。在`main`中，当我们用括号跟随`rect1.width`时，Rust会知道我们指的是方法`width`。而当我们不使用括号时，Rust会知道我们指的是那个字段。`width`。

通常，但并非总是如此，当我们给一个方法命名与我们希望该字段相同的名称时，这个方法只会返回字段中的值，而不会执行其他操作。这类方法被称为_获取器_，而Rust并不像其他一些语言那样自动为结构体字段实现这些获取器。获取器的优点在于，你可以将字段设为私有，而将方法设为公有，从而允许通过公共API以只读方式访问该字段。我们将在后面讨论什么是公有和私有属性。在[第7章][public]中，如何将一个字段或方法指定为公共或私有。

> ### `->` 运算符在哪里？>> 在C和C++中，有两种不同的运算符用于调用方法：如果你直接对对象调用方法，则使用> `.`；如果你是通过指向对象的指针来调用方法，并且需要先解引用该指针，则使用`->`。换句话说，如果`object`是一个指针，那么`object->something()`与`(*object).something()`类似。>> Rust中没有等同于`->`运算符的运算符。相反，Rust有一个名为“自动引用和解除引用”的特性。在Rust中，调用方法是实现这一特性的少数几个地方之一。其工作原理如下：当你使用`object.something()`调用一个方法时，Rust会自动插入`&`、`&mut`或`*`，使得`object`与方法的签名相匹配。换句话说，以下这些内容实际上是相同的：> <!-- 无法提取SEE BUG的详细信息：https://github.com/rust-lang/mdBook/issues/1127 -->>> ```rust
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
> ```>> 第一个看起来更清晰。这种自动引用行为之所以有效，是因为方法有一个明确的接收者——即`self`的类型。根据方法的接收者和名称，Rust可以明确地判断该方法是在读取(`&self`)、修改(`&mut self`)还是消费(`self`)。事实上Rust将方法接收器的借用变为隐式的做法，是使所有权管理更加便捷的一个重要因素。

### 具有更多参数的方法

让我们通过在一个`Rectangle`结构上实现第二个方法来练习使用这些方法。这次，我们希望一个`Rectangle`的实例能够与另一个`Rectangle`进行 instanceof 比较，如果第二个`Rectangle`可以完全容纳在`self`中（即第一个`Rectangle`），则它应该返回`true`；否则，它应该返回`false`。也就是说，一旦我们定义了`can_hold`方法之后，我们就可以编写清单5-14中所示的程序了。

<列表编号="5-14" 文件名称="src/main.rs" 标题="使用尚未定义的 `can_hold` 方法">

```rust,ignore
{{#rustdoc_include ../listings/ch05-using-structs-to-structure-related-data/listing-05-14/src/main.rs}}
```

</清单>

预期的输出结果如下：因为`rect2`的两个维度都小于`rect1`的维度，但是`rect3`的宽度大于`rect1`的宽度。

```text
Can rect1 hold rect2? true
Can rect1 hold rect3? false
```

我们知道我们需要定义一个方法，因此它将会位于`impl Rectangle`块内。该方法名为`can_hold`，它将接收一个不可变的参数，该参数来自另一个`Rectangle`实例。我们可以通过查看调用该方法的代码来确定参数的类型：`rect1.can_hold(&rect2)`将传递`&rect2`作为参数，而`&rect2`又是一个不可变的参数，这个参数指向`rect2`，后者是`Rectangle`的实例。这样做是有道理的，因为我们只需要使用这些参数来构建我们的方法逻辑即可。需要读取`rect2`（而不是进行写入操作，因为那样就需要一个可变借用对象），并且我们希望`main`能够保留对`rect2`的所有权，这样在调用`can_hold`方法之后，我们可以再次使用`rect2`。`can_hold`的返回值将是一个布尔值，实现中会检查`self`的宽度和高度是否大于另一个`Rectangle`的宽度和高度。分别。让我们在Listing 5-15中，将新的`can_hold`方法添加到Listing 5-13中的`impl`块中。

<list numbering="5-15" file-name="src/main.rs" caption="在`Rectangle`上实现`can_hold`方法，该方法接受一个`Rectangle`实例作为参数">

```rust
{{#rustdoc_include ../listings/ch05-using-structs-to-structure-related-data/listing-05-15/src/main.rs:here}}
```

</清单>

当我们使用清单5-14中的`main`函数运行这段代码时，我们将得到期望的输出。方法可以接受多个参数，这些参数可以在`self`参数之后添加，并且这些参数的工作方式与函数中的参数相同。

### 相关函数

在 ``impl`` 块中定义的所有函数都被称为“关联函数”，因为它们与名为 ``impl`` 的类型相关联。我们可以定义一些没有 ``self`` 作为其第一个参数的关联函数（因此不是方法），因为这些函数不需要类型的实例就能正常工作。我们已经使用过一个这样的函数：即定义在 ``String`` 类型上的 ``String::from`` 函数。

那些不是方法的关联函数，通常被用于创建新实例的构造函数中。这些函数通常被称为`new`，不过`new`并不是一个特殊的名称，而且也没有被内置到语言中。例如，我们可以选择提供一个名为`square`的关联函数，该函数会接受一个维度参数，并将其作为宽度和高度来使用，从而使其功能更加灵活。创建正方形`Rectangle`比两次指定同一个值要容易得多。

<span class="filename">文件名：src/main.rs</span>

```rust
{{#rustdoc_include ../listings/ch05-using-structs-to-structure-related-data/no-listing-03-associated-functions/src/main.rs:here}}
```

在返回类型和函数的主体中，``Self``这个关键字是``impl``这个关键字的别名，而``impl``在这个案例中就是``Rectangle``。

要调用这个关联函数，我们使用``::``语法，并带上结构名称；``let sq = Rectangle::square(3);``是一个示例。这个函数是由结构来命名的：``::``语法既用于关联函数，也用于由模块创建的名称空间。我们将在[第7章][modules]中讨论模块。

### 多个`impl`块

每个结构体都可以包含多个`impl`块。例如，清单5-15与清单5-16中显示的代码是等效的，其中每个方法都位于自己的`impl`块中。

<列表编号="5-16" 标题="使用多个`impl`块重新编写列表5-15">

```rust
{{#rustdoc_include ../listings/ch05-using-structs-to-structure-related-data/listing-05-16/src/main.rs:here}}
```

</清单>

没有必要将这些方法分开到多个`impl`块中，但这种语法是有效的。我们将在第十章中看到使用多个`impl`块的例子，在那里我们会讨论泛型类型和特质。

## 摘要

结构体允许你创建对特定领域有意义的自定义类型。通过使用结构体，你可以将相关的数据片段相互连接，并为每个部分命名，从而使代码更加清晰。在`impl`块中，你可以定义与你的类型相关联的函数，而方法是一种关联函数，它允许你指定结构体实例的行为。

但是结构体并不是创建自定义类型的唯一方式：让我们利用Rust的枚举功能，为你的工具箱增添另一种工具吧。

[枚举类型]: ch06-00-enums.html  
[特性对象]: ch18-02-trait-objects.md  
[公共部分]: ch07-03-paths-for-referring-to-an-item-in-the-module-tree.html#exposing-paths-with-the-pub-keyword  
[模块]: ch07-02-defining-modules-to-control-scope-and-privacy.html