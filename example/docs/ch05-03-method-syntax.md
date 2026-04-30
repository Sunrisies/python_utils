## 方法

方法类似于函数：我们使用 `fn` 关键字和一个名称来声明它们，它们可以拥有参数和返回值，并且包含一些在从其他地方调用该方法时执行的代码。与函数不同的是，方法是在结构体（或枚举或特质对象中定义的，我们将在[第6章][enums]<!-- ignore -->和[第18章][trait-objects]<!-- ignore -->中分别介绍）、以及特质对象的上下文中定义的。方法的第一个参数总是 `self`，这个参数代表了被调用方法的那个结构体的实例。

<!-- Old headings. Do not remove or links may break. -->

<a id="defining-methods"></a>

### 方法语法

让我们修改那个包含 `Rectangle` 作为参数的 `area` 函数，而是在一个 `Rectangle` 结构上定义 `area` 方法，如清单 5-13 所示。

<Listing number="5-13" file-name="src/main.rs" caption="Defining an `area` method on the `Rectangle` struct">

```rust
#[derive(Debug)]
struct Rectangle {
    width: u32,
    height: u32,
}

impl Rectangle {
    fn area(&self) -> u32 {
        self.width * self.height
    }
}

fn main() {
    let rect1 = Rectangle {
        width: 30,
        height: 50,
    };

    println!(
        "The area of the rectangle is {} square pixels.",
        rect1.area()
    );
}

```

</Listing>

为了在 `Rectangle` 的上下文中定义该函数，我们首先为 `Rectangle` 创建一个 `impl`（实现）块。这个 `impl` 块中的所有内容都将与 `Rectangle` 类型相关联。接着，我们将 `area` 函数放在 `impl` 的花括号中，并更改其第一个参数，使其变为 `self`，同时在整个函数体内也使用 `self` 作为参数。在 `main` 中，当我们调用 `area` 函数并将 `rect1` 作为参数传递时，我们可以使用 _方法语法_ 来调用 `area` 方法，从而实现对 `Rectangle` 实例的访问。方法语法格式为：在实例后面加上一个点，然后依次是方法名、括号以及任何参数。

在 `area` 的签名中，我们使用 `&self` 而不是 `rectangle: &Rectangle`。  
`&self` 实际上是 `self: &Self` 的缩写。在 `impl` 块中，类型 `Self` 是 `impl` 块所代表的类型的别名。方法必须在其第一个参数中有一个名为 `self` 的参数，该参数的类型为 `Self`。因此，Rust 允许你在第一个参数位置仅使用 `self` 作为缩写。  
请注意，我们仍然需要在 `self` 简写之前使用 `&` 来表明该方法借用 `Self` 实例，就像我们在 `rectangle: &Rectangle` 中所做的那样。方法可以拥有 `self`，不可变地借用 `self`，就像我们在这里所做的那样，或者可变地借用 `self`，就像它们可以处理任何其他参数一样。

我们选择使用 `&self` 的原因，与我们在函数版本中使用的 `&Rectangle` 相同。  
我们的目的不是要拥有该实例的所有权，只是想读取结构体中的数据，而不是对其进行修改。如果我们希望改变调用该方法的实例，以便该方法能够执行特定的操作，那么我们会使用 `&mut self` 作为第一个参数。不过，通常只有在某些方法中，才会使用 `self` 作为第一个参数，以便该方法能够拥有该实例的所有权。这种技术通常用于将 `self` 转换为其他形式，同时希望防止调用者在转换后继续使用原始实例。

使用方法而非函数的主要原因，除了提供方法语法，并且不必在每个方法的签名中重复 `self` 类型之外，还有组织上的考虑。我们将能够使用某个类型实例的所有功能都放在一个 `impl` 块中，而不是让未来的代码使用者需要在我们提供的库的各个地方去寻找 `Rectangle` 的功能。

请注意，我们可以选择让一个方法的名称与结构体中的一个字段相同。例如，我们可以在 `Rectangle` 上定义一个方法，该方法的名称也是`width`。

<Listing file-name="src/main.rs">

```rust
impl Rectangle {
    fn width(&self) -> bool {
        self.width > 0
    }
}

fn main() {
    let rect1 = Rectangle {
        width: 30,
        height: 50,
    };

    if rect1.width() {
        println!("The rectangle has a nonzero width; it is {}", rect1.width);
    }
}

```

</Listing>

在这里，我们选择让 `width` 方法在实例的 `width` 字段中的值大于 `0` 时返回 `true`，而在值等于 `0` 时返回 `false`。我们可以在同一个名称的方法中使用同一个字段，用于任何目的。在 `main` 中，当我们用括号跟随 `rect1.width` 时，Rust 会知道我们指的是方法 `width`。而不使用括号时，Rust 会知道我们指的是字段 `width`。

通常，但并非总是如此，当我们给一个方法命名与字段相同的名称时，我们希望该方法仅返回字段中的值，而不执行其他操作。这类方法被称为_获取器_。与某些其他语言不同，Rust并不会自动为结构体字段实现获取器功能。获取器非常有用，因为你可以将字段设为私有，而将方法设为公有，从而让该字段只能通过公共API进行只读访问。我们将在[第7章][public]<!-- ignore -->中讨论什么是公有和私有，以及如何将字段或方法指定为公有或私有。

> ### `->` 运算符在哪里？
>
> 在 C 和 C++ 中，有两种不同的运算符用于调用方法：如果你直接调用对象上的方法，则使用 `.`；如果你是通过指向对象的指针来调用方法，并且需要先解引用该指针，则使用 `->`。换句话说，如果 `object` 是一个指针，那么 `object->something()` 与 `(*object).something()` 类似。
>
> Rust 没有与 `->` 运算符相对应的功能；相反，Rust 有一个名为“自动引用和解引用”的特性。调用方法是 Rust 中少数几个具有这种特性的地方。
>
> 其工作原理如下：当你使用 `object.something()` 调用方法时，Rust 会自动添加 `&`、 `&mut` 或 `*`，使得 `object` 与方法的签名相匹配。换句话说，以下两种方式是相同的：
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
> 第一种方式看起来更简洁。这种自动引用行为之所以有效，是因为方法有一个明确的接收者——即 `self` 的类型。根据方法的接收者和名称，Rust 可以明确地判断该方法是进行读取操作（`&self`）、修改操作（`&mut self`）还是消费操作（`self`）。Rust 让方法的接收者具有隐式借用特性，这是使所有权机制在实际使用中更加便捷的一个重要因素。

### 具有更多参数的方法

让我们通过为 `Rectangle` 结构实现第二个方法来练习使用方法。这次，我们希望 `Rectangle` 结构的一个实例能够接受另一个 `Rectangle` 结构实例，并且如果第二个 `Rectangle` 结构能够完全容纳在 `self` 结构中（第一个 `Rectangle` 结构允许这种情况），则应该返回 `true`；否则，应该返回 `false`。也就是说，一旦我们定义了 `can_hold` 方法，我们就可以编写如清单 5-14 所示的程序。

<Listing number="5-14" file-name="src/main.rs" caption="Using the as-yet-unwritten `can_hold` method">

```rust,ignore
fn main() {
    let rect1 = Rectangle {
        width: 30,
        height: 50,
    };
    let rect2 = Rectangle {
        width: 10,
        height: 40,
    };
    let rect3 = Rectangle {
        width: 60,
        height: 45,
    };

    println!("Can rect1 hold rect2? {}", rect1.can_hold(&rect2));
    println!("Can rect1 hold rect3? {}", rect1.can_hold(&rect3));
}

```

</Listing>

预期的输出结果如下：因为`rect2`的两个维度都小于`rect1`的维度，但是`rect3`的宽度大于`rect1`的宽度。

```text
Can rect1 hold rect2? true
Can rect1 hold rect3? false
```

我们知道需要定义一个方法，因此它将会位于 `impl Rectangle` 块内。该方法的名称将是 `can_hold`，并且它将接收一个不可变的借用对象作为参数，这个参数来自另一个 `Rectangle`。我们可以通过查看调用该方法的代码来确定参数的类型：`rect1.can_hold(&rect2)` 将传入 `&rect2`，而 `&rect2` 则是一个不可变的借用对象，这个借用对象被传递给 `rect2`，而 `rect2` 又是 `Rectangle` 的一个实例。这样做是有意义的，因为我们只需要读取 `rect2`（而不是写入，那样就需要一个可变的借用对象），同时我们希望 `main` 能够保留对 `rect2` 的所有权，这样在调用 `can_hold` 方法之后，我们仍然可以使用 `rect2`。`can_hold` 的返回值将是一个布尔值，而实现部分会检查 `self` 的宽度和高度是否大于另一个 `Rectangle` 的宽度和高度。让我们在 Listing 5-13 中的 `impl` 块中添加新的 `can_hold` 方法，如 Listing 5-15 所示。

<Listing number="5-15" file-name="src/main.rs" caption="Implementing the `can_hold` method on `Rectangle` that takes another `Rectangle` instance as a parameter">

```rust
impl Rectangle {
    fn area(&self) -> u32 {
        self.width * self.height
    }

    fn can_hold(&self, other: &Rectangle) -> bool {
        self.width > other.width && self.height > other.height
    }
}

```

</Listing>

当我们使用清单5-14中的`main`函数运行这段代码时，我们将得到期望的输出。方法可以接受多个参数，这些参数可以添加到`self`参数之后，并且这些参数的作用方式与函数中的参数相同。

### 相关函数

在 `impl` 块中定义的所有函数都被称为_关联函数_，因为它们与以 `impl` 命名的类型相关联。我们可以定义那些没有 `self` 作为其第一个参数的关联函数（因此也不是方法），因为这些函数不需要该类型的实例来运作。我们已经使用过一个这样的函数：就是在 `String` 类型上定义的 `String::from` 函数。

那些不是方法的关联函数，通常被用于创建结构体实例的构造函数中。这些函数通常被称为 `new`，不过 `new` 并不是一个特殊的名称，而且也没有被内置到语言中。例如，我们可以选择一个名为 `square` 的关联函数，该函数有一个维度参数，并将其用作宽度和高度，这样就能更容易地创建一个正方形 `Rectangle`，而不需要两次指定相同的数值。

<span class="filename"> 文件名: src/main.rs</span>

```rust
impl Rectangle {
    fn square(size: u32) -> Self {
        Self {
            width: size,
            height: size,
        }
    }
}

```

在函数返回类型和函数体内出现的 `Self` 关键字，实际上是 `impl` 关键字后所出现的类型的别名，在这种情况下，该类型就是 `Rectangle`。

要调用这个关联函数，我们使用带有结构体名称的 `::` 语法；`let sq = Rectangle::square(3);` 就是一个例子。这个函数是由结构体来命名的：`::` 语法既用于关联函数，也用于由模块创建的名称空间。我们将在[第7章][modules]<!-- ignore -->中讨论模块。

### 多个 `impl` 块

每个结构体可以包含多个 `impl` 块。例如，列表 5-15 与列表 5-16 中的代码是等效的，其中每个方法都位于自己的 `impl` 块中。

<Listing number="5-16" caption="Rewriting Listing 5-15 using multiple `impl` blocks">

```rust
impl Rectangle {
    fn area(&self) -> u32 {
        self.width * self.height
    }
}

impl Rectangle {
    fn can_hold(&self, other: &Rectangle) -> bool {
        self.width > other.width && self.height > other.height
    }
}

```

</Listing>

在这里，没有必要将这些方法分开到多个 `impl` 块中，但这种语法是有效的。我们将在第十章中看到多个 `impl` 块的使用场景，届时我们会讨论泛型类型和特质。

## 摘要

结构体允许你创建对特定领域有意义的自定义类型。通过使用结构体，你可以将相关的数据片段相互连接，并为每个数据片段命名，从而使代码更加清晰。在 `impl` 块中，你可以定义与类型相关的函数，而方法则是一种关联函数，它允许你指定结构体实例的行为。

但是，结构体并不是创建自定义类型的唯一方式：让我们利用Rust的枚举功能，为你的工具箱增添另一种工具。

[enums]: ch06-00-enums.html
[trait-objects]: ch18-02-trait-objects.md
[public]: ch07-03-paths-for-referring-to-an-item-in-the-module-tree.html#exposing-paths-with-the-pub-keyword
[modules]: ch07-02-defining-modules-to-control-scope-and-privacy.html
