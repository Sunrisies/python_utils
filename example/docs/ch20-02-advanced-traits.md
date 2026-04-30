## 高级特性

我们在第10章的 [“Defining Shared Behavior with
Traits”][traits]<!-- ignore --> 部分先介绍了特性，但并没有讨论更详细的细节。现在，既然你对Rust有了更多的了解，我们可以深入讨论这些细节了。

<!-- Old headings. Do not remove or links may break. -->

<a id="specifying-placeholder-types-in-trait-definitions-with-associated-types"></a>
<a id="associated-types"></a>

### 使用关联类型定义特性

“关联类型”将一个类型占位符与某个特质连接起来，使得该特质的接口定义可以在其签名中使用这些类型占位符。某个特质的实现者会指定要使用的具体类型，而不是该特质的类型占位符。这样，我们可以定义一个使用某些类型的特质，而无需在特质实现之前就确切知道这些类型是什么。

在本章中，我们描述的大部分高级功能都是很少需要的。而相关类型则处于中间位置：它们的使用频率虽然低于书中其他功能，但比本章讨论的许多其他功能更为常见。

一个具有相关类型的 trait 的例子是标准库提供的 `Iterator` trait。该相关类型的名称是 `Item`，它代表了实现 `Iterator` trait 的类型所遍历的值的类型。 `Iterator` trait 的定义如清单 20-13 所示。

<Listing number="20-13" caption="The definition of the `Iterator` trait that has an associated type `Item`">

```rust,noplayground
pub trait Iterator {
    type Item;

    fn next(&mut self) -> Option<Self::Item>;
}

```

</Listing>

类型 `Item` 是一个占位符，而 `next` 方法的定义表明，它将返回 `Option<Self::Item>` 类型的值。实现 `Iterator` 特性的开发者将指定 `Item` 的具体类型，而 `next` 方法将返回一个包含该具体类型的 `Option` 值。

关联类型可能看起来与泛型概念类似，因为泛型允许我们定义函数，而不需要指定该函数能够处理哪些类型。为了探讨这两种概念之间的区别，我们将观察一个名为 `Counter` 的类型上的 `Iterator`  trait 的实现，该实现指定了 `Item` 类型是 `u32`。

<Listing file-name="src/lib.rs">

```rust,ignore
impl Iterator for Counter {
    type Item = u32;

    fn next(&mut self) -> Option<Self::Item> {
        // --snip--

```

</Listing>

这种语法似乎与泛型语法相当。那么，为什么不直接像 Listing 20-14 中那样使用泛型来定义`Iterator` trait呢？

<Listing number="20-14" caption="A hypothetical definition of the `Iterator` trait using generics">

```rust,noplayground
pub trait Iterator<T> {
    fn next(&mut self) -> Option<T>;
}

```

</Listing>

区别在于，在使用泛型时，如清单20-14所示，我们必须为每个实现进行类型注释；因为我们也可以实现`Iterator<String> for Counter`或任何其他类型，所以我们可以为`Counter`实现多个`Iterator`。换句话说，当一个特质具有泛型参数时，可以为该类型实现多次，每次都会改变泛型类型参数的具体类型。当我们对`Counter`使用`next`方法时，我们必须提供类型注释来指明我们想要使用哪个`Iterator`的实现。

在关联类型的情况下，我们不需要对类型进行注释，因为我们无法多次实现某个 trait 于一个类型上。在 Listing 20-13 中，使用关联类型的定义时，我们只能一次指定 `Item` 的类型，因为只能存在一个 `impl Iterator for Counter`。在调用 `next` 于 `Counter` 时，我们不必指定需要的是一个 `u32` 值的迭代器。

关联类型也是 trait 契约的一部分：实现该 trait 的模块必须提供一个类型来替代关联类型的占位符。关联类型通常有一个名称，用于描述该类型的用途，因此在 API 文档中记录关联类型是一个良好的实践。

<!-- Old headings. Do not remove or links may break. -->

<a id="default-generic-type-parameters-and-operator-overloading"></a>

### 使用默认通用参数和运算符重载

当我们使用泛型类型参数时，可以为泛型类型指定一个默认的具体类型。这样，如果默认类型能够正常工作，那么实现该特性的代码就不需要再指定具体类型。使用 `<PlaceholderType=ConcreteType>` 语法声明泛型类型时，就可以指定默认类型。

一个使用这种技术的绝佳例子是_运算符重载_，通过这种方法，你可以在特定情况下自定义某个运算符的行为（例如 `+`）。

Rust不允许你创建自己的运算符或重载任意运算符。但是，你可以通过实现与运算符相关的特征来重载 `std::ops` 中列出的操作及其对应的特征。例如，在 Listing 20-15 中，我们通过在一个 `Point` 结构体上实现 `Add` 特征，从而重载 `+` 运算符，以将两个 `Point` 实例相加。

**清单 20-15:** *src/main.rs* — 实现 `Add` 特性，以针对 `Point` 实例重载 `+` 运算符

```rust
use std::ops::Add;

#[derive(Debug, Copy, Clone, PartialEq)]
struct Point {
    x: i32,
    y: i32,
}

impl Add for Point {
    type Output = Point;

    fn add(self, other: Point) -> Point {
        Point {
            x: self.x + other.x,
            y: self.y + other.y,
        }
    }
}

fn main() {
    assert_eq!(
        Point { x: 1, y: 0 } + Point { x: 2, y: 3 },
        Point { x: 3, y: 3 }
    );
}

```

方法 `add` 会将两个 `Point` 实例的 `x` 值和两个 `Point` 实例的 `y` 值相加，从而创建一个新的 `Point`。 `Add` 特质有一个名为 `Output` 的关联类型，该类型决定了该方法返回的类型。

这段代码的默认泛型类型属于 `Add` 特质。以下是它的定义：

```rust
trait Add<Rhs=Self> {
    type Output;

    fn add(self, rhs: Rhs) -> Self::Output;
}
```

这段代码的架构应该很熟悉：一个带有一种方法和一个关联类型的特性。新的部分就是 `Rhs=Self`：这种语法被称为_默认类型参数_。 `Rhs` 泛型类型参数（简称“右侧”）定义了 `rhs` 参数在 `add` 方法中的类型。如果我们在实现 `Add` 特性时没有为 `Rhs` 指定具体的类型，那么 `Rhs` 的类型将默认使用 `Self`，而这正是我们在实现 `Add` 时所依赖的类型。

在为 `Point` 实现 `Rhs` 时，我们使用了默认值，因为我们需要添加两个 `Point` 实例。让我们来看一个实现 `Add`  trait 的例子，在这个例子中，我们想要自定义 `Rhs` 类型，而不是使用默认值。

我们有两个结构体，分别命名为 `Millimeters` 和 `Meters`，它们分别存储不同单位的值。这种在一个结构体中对现有类型进行封装的做法被称为“新类型模式”，我们将在 [“Implementing
External Traits with the Newtype Pattern”][newtype]<!-- ignore --> 部分对此进行更详细的说明。我们希望将毫米单位的值转换为米单位，并且希望 `Add` 的实现能够正确地进行转换操作。我们可以像 Listing 20-16 中所示，用 `Meters` 作为 `Rhs`，为 `Millimeters` 实现 `Add` 的功能。

**清单 20-16:** *src/lib.rs* — 在 `Millimeters`  trait 上实现 `Add` trait，以添加 `Millimeters` 和 `Meters`

```rust,noplayground
use std::ops::Add;

struct Millimeters(u32);
struct Meters(u32);

impl Add<Meters> for Millimeters {
    type Output = Millimeters;

    fn add(self, other: Meters) -> Millimeters {
        Millimeters(self.0 + (other.0 * 1000))
    }
}

```

为了添加 `Millimeters` 和 `Meters`，我们指定 `impl Add<Meters>` 来设置 `Rhs` 类型参数的值，而不是使用默认的 `Self`。

你将以两种主要方式使用默认类型参数：

1. 在不破坏现有代码的情况下扩展类型  
2. 允许在特定情况下进行自定义，这些情况大多数用户并不需要

标准库中的 `Add` trait 就是第二个用途的一个例子：通常，你会添加两个类似的类型，但 `Add` trait 提供了进一步自定义的能力。在 `Add` trait 的定义中使用默认类型参数意味着你不必在大多数情况下指定额外的参数。换句话说，不需要一些额外的实现代码，这使得使用该 trait 更加简单。

第一个目的与第二个类似，但方向相反：如果你想为现有的特质添加类型参数，可以为其指定一个默认值，从而在不破坏现有实现代码的情况下扩展该特质的功能。

<!-- Old headings. Do not remove or links may break. -->

<a id="fully-qualified-syntax-for-disambiguation-calling-methods-with-the-same-name"></a>
<a id="disambiguating-between-methods-with-the-same-name"></a>

### 在同名方法之间进行消歧

在Rust中，没有任何规定阻止一个特质拥有与另一个特质的方法同名的方法。Rust也不会阻止你在某个类型上同时实现这两个特质。此外，你也可以直接在具有与特质方法相同名称的类型上实现方法。

在调用同名方法时，你需要告诉 Rust 你想要使用哪一个方法。请参考清单20-17中的代码，其中我们定义了两个名为`Pilot`和`Wizard`的特质，这两个特质都有一个名为`fly`的方法。然后我们在类型`Human`上实现了这两个特质，而`Human`类型本身已经实现了一个名为`fly`的方法。每个`fly`方法都执行不同的操作。

**列表 20-17:** *src/main.rs* — 定义了两个带有 `fly` 方法的特质，这些方法是在 `Human` 类型上实现的；同时，还有一个 `fly` 方法直接定义在 `Human` 上。

```rust
trait Pilot {
    fn fly(&self);
}

trait Wizard {
    fn fly(&self);
}

struct Human;

impl Pilot for Human {
    fn fly(&self) {
        println!("This is your captain speaking.");
    }
}

impl Wizard for Human {
    fn fly(&self) {
        println!("Up!");
    }
}

impl Human {
    fn fly(&self) {
        println!("*waving arms furiously*");
    }
}

```

当我们对 `Human` 的实例调用 `fly` 时，编译器会默认调用该类型上直接实现的方法，如 Listing 20-18 所示。

**清单 20-18:** *src/main.rs* — 在 `Human` 的实例上调用 `fly`

```rust
fn main() {
    let person = Human;
    person.fly();
}

```

运行这段代码会输出 `*waving arms furiously*`，这表明 Rust 直接调用了在 `Human` 上实现的 `fly` 方法。

为了从 `Pilot` trait 或 `Wizard` trait 中调用 `fly` 方法，我们需要使用更明确的语法来指定我们指的是哪个 `fly` 方法。清单 20-19 展示了这种语法。

**清单 20-19:** *src/main.rs* — 指定我们想要调用哪个 trait 的 `fly` 方法

```rust
fn main() {
    let person = Human;
    Pilot::fly(&person);
    Wizard::fly(&person);
    person.fly();
}

```

在方法名称之前指定 trait 名称，可以明确告诉 Rust 我们希望调用的是 `fly` 的哪个实现。我们也可以写成 `Human::fly(&person)`，这与我们在 Listing 20-19 中使用的 `person.fly()` 是等效的。不过，如果我们不需要消除歧义的话，这种写法会稍微长一些。

运行这段代码会输出以下内容：

```console
$ cargo run
   Compiling traits-example v0.1.0 (file:///projects/traits-example)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.46s
     Running `target/debug/traits-example`
This is your captain speaking.
Up!
*waving arms furiously*

```

因为 `fly` 方法需要一个 `self` 参数，如果我们有两个 _类型_，这两个类型都实现了某个 _特性_，那么 Rust 可以根据 `self` 的类型来决定使用哪个特性的实现。

然而，那些不是方法的关联函数并没有 `self` 参数。当存在多个类型或特质定义了具有相同函数名称的非方法函数时，除非使用完全限定的语法，否则 Rust 并不总能知道你指的是哪种类型。例如，在 Listing 20-20 中，我们为动物收容所创建了一个特质，希望将所有幼犬命名为 Spot。我们创建了一个 `Animal` 特质，并为其关联了一个非方法函数 `baby_name`。这个 `Animal` 特质被实现在 `Dog` 结构上，我们还直接为 `Dog` 结构提供了一个关联的非方法函数 `baby_name`。

**列表 20-20:** *src/main.rs* — 一个带有相关函数的特质，以及一个具有相同名称的类型，该类型也实现了该特质的相关函数。

```rust
trait Animal {
    fn baby_name() -> String;
}

struct Dog;

impl Dog {
    fn baby_name() -> String {
        String::from("Spot")
    }
}

impl Animal for Dog {
    fn baby_name() -> String {
        String::from("puppy")
    }
}

fn main() {
    println!("A baby dog is called a {}", Dog::baby_name());
}

```

我们实现了用于在 `Dog` 上定义的函数中命名所有名为 Spot 的小狗的代码。 `Dog` 类型还实现了 trait `Animal`，该 trait 描述了所有动物的共同特征。小狗被称为 puppies，这一点在 `baby_name` 函数中与 `Animal` trait 相关的 `Animal` trait 的实现中得到了体现。

在 `main` 中，我们调用 `Dog::baby_name` 函数，该函数直接调用在 `Dog` 上定义的相关函数。这段代码会输出以下内容：

```console
$ cargo run
   Compiling traits-example v0.1.0 (file:///projects/traits-example)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.54s
     Running `target/debug/traits-example`
A baby dog is called a Spot

```

这个输出并不是我们想要的。我们希望为 `Dog` 上实现过的 `Animal` 特质中的 `baby_name` 函数命名，这样代码就能输出 `A baby dog is called a puppy`。我们在 Listing 20-19 中使用的指定特质名称的方法在这里并不起作用；如果我们把 `main` 改为 Listing 20-21 中的代码，就会遇到编译错误。

**列表 20-21:** *src/main.rs* — 尝试调用来自 `Animal` trait 的 `baby_name` 函数，但 Rust 不知道应该使用哪个实现。

```rust,ignore,does_not_compile
fn main() {
    println!("A baby dog is called a {}", Animal::baby_name());
}

```

因为 `Animal::baby_name` 没有 `self` 参数，而且可能还有其他实现了 `Animal` 特性的类型，Rust 无法判断我们想要的是哪种 `Animal::baby_name` 的实现。因此，我们会遇到这个编译器错误：

```console
$ cargo run
   Compiling traits-example v0.1.0 (file:///projects/traits-example)
error[E0790]: cannot call associated function on trait without specifying the corresponding `impl` type
  --> src/main.rs:20:43
   |
 2 |     fn baby_name() -> String;
   |     ------------------------- `Animal::baby_name` defined here
...
20 |     println!("A baby dog is called a {}", Animal::baby_name());
   |                                           ^^^^^^^^^^^^^^^^^^^ cannot call associated function of trait
   |
help: use the fully-qualified path to the only available implementation
   |
20 |     println!("A baby dog is called a {}", <Dog as Animal>::baby_name());
   |                                           +++++++       +

For more information about this error, try `rustc --explain E0790`.
error: could not compile `traits-example` (bin "traits-example") due to 1 previous error

```

为了消除歧义，并告诉 Rust 我们希望使用 `Dog` 的 `Animal` 实现，而不是对某些其他类型使用的 `Animal` 实现，我们需要使用完全限定语法。列表 20-22 展示了如何使用完全限定语法。

**清单 20-22:** *src/main.rs* — 使用完全限定语法来指定我们希望调用来自 `Animal` 特质在 `Dog` 上实现的 `baby_name` 函数

```rust
fn main() {
    println!("A baby dog is called a {}", <Dog as Animal>::baby_name());
}

```

我们为 Rust 提供了一种类型注释，这种注释位于尖括号中，用来表示我们希望调用 `Animal` 特质中的 `Dog` 方法的实现，具体来说，就是希望将 `Dog` 类型视为 `Animal` 类型，以便进行函数调用。这段代码现在能够输出我们想要的结果了。

```console
$ cargo run
   Compiling traits-example v0.1.0 (file:///projects/traits-example)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.48s
     Running `target/debug/traits-example`
A baby dog is called a puppy

```

一般来说，完全限定语法定义如下：

```rust,ignore
<Type as Trait>::function(receiver_if_method, next_arg, ...);
```

对于那些不是方法的关联函数来说，就不会有 `receiver` 这种语法了：  
只会有一个其他参数的列表。你可以在任何调用函数或方法的地方使用完全限定的语法。不过，你可以省略 Rust 能够从程序中的其他信息中推断出来的这部分语法。只有在存在多个使用相同名称的实现，并且 Rust 需要帮助来识别你想要调用哪个实现的情况下，才需要使用这种更冗长的语法。

<!-- Old headings. Do not remove or links may break. -->

<a id="using-supertraits-to-require-one-traits-functionality-within-another-trait"></a>

### 使用超级特性

有时候，你可能会编写一个依赖于另一个 trait 的 trait 定义：为了让一个类型实现第一个 trait，你需要要求该类型同时也实现第二个 trait。你这样做是为了让你的 trait 定义能够利用第二个 trait 中的相关项。你所依赖的那个 trait 被称为你的 trait 的 _supertrait_。

例如，假设我们想要创建一个具有`outline_print`方法的`OutlinePrint` trait，该方法能够打印出一个格式化的给定值，并且该值会被用星号包围。也就是说，给定一个实现了标准库`Display` trait的`Point` struct，当我们对具有`1`作为`x`和`3`作为`y`的`Point`实例调用`outline_print`时，它应该打印出如下内容：

```text
**********
*        *
* (1, 3) *
*        *
**********
```

在实现 `outline_print` 方法时，我们希望使用 `Display` 特质的功能。因此，我们需要指定 `OutlinePrint` 特质仅适用于那些同时实现了 `Display` 并且提供了 `OutlinePrint` 所需功能的类型。我们可以通过在特质定义中指定 `OutlinePrint: Display` 来实现这一点。这种技术类似于为特质添加特质绑定。列表 20-23 展示了 `OutlinePrint` 特质的实现。

**列表 20-23:** *src/main.rs* — 实现需要 `Display` 功能的 `OutlinePrint` 特性

```rust
use std::fmt;

trait OutlinePrint: fmt::Display {
    fn outline_print(&self) {
        let output = self.to_string();
        let len = output.len();
        println!("{}", "*".repeat(len + 4));
        println!("*{}*", " ".repeat(len + 2));
        println!("* {output} *");
        println!("*{}*", " ".repeat(len + 2));
        println!("{}", "*".repeat(len + 4));
    }
}

```

因为我们已经指定了 `OutlinePrint` 需要 `Display` 特性，所以我们可以使用 `to_string` 函数，该函数会自动为实现了 `Display` 的任何类型实现。如果我们尝试在不添加冒号的情况下使用 `to_string`，并且在特性名称之后不指定 `Display` 特性，我们将会得到一个错误，提示在当前范围内没有名为 `to_string` 的方法适用于类型 `&Self`。

让我们看看，当我们尝试在一个没有实现 `Display` 的类型上实现 `OutlinePrint` 时，比如 `Point` 结构体，会发生什么情况。

<Listing file-name="src/main.rs">

```rust,ignore,does_not_compile
struct Point {
    x: i32,
    y: i32,
}

impl OutlinePrint for Point {}

```

</Listing>

我们收到了一个错误，提示需要 `Display`，但它并未实现。

```console
$ cargo run
   Compiling traits-example v0.1.0 (file:///projects/traits-example)
error[E0277]: `Point` doesn't implement `std::fmt::Display`
  --> src/main.rs:20:23
   |
20 | impl OutlinePrint for Point {}
   |                       ^^^^^ the trait `std::fmt::Display` is not implemented for `Point`
   |
note: required by a bound in `OutlinePrint`
  --> src/main.rs:3:21
   |
 3 | trait OutlinePrint: fmt::Display {
   |                     ^^^^^^^^^^^^ required by this bound in `OutlinePrint`

error[E0277]: `Point` doesn't implement `std::fmt::Display`
  --> src/main.rs:24:7
   |
24 |     p.outline_print();
   |       ^^^^^^^^^^^^^ the trait `std::fmt::Display` is not implemented for `Point`
   |
note: required by a bound in `OutlinePrint::outline_print`
  --> src/main.rs:3:21
   |
 3 | trait OutlinePrint: fmt::Display {
   |                     ^^^^^^^^^^^^ required by this bound in `OutlinePrint::outline_print`
 4 |     fn outline_print(&self) {
   |        ------------- required by a bound in this associated function

For more information about this error, try `rustc --explain E0277`.
error: could not compile `traits-example` (bin "traits-example") due to 2 previous errors

```

为了解决这个问题，我们在 `Point` 上实现了 `Display`，并满足了以下约束条件：
`OutlinePrint` 的要求，如下所示：

<Listing file-name="src/main.rs">

```rust
use std::fmt;

impl fmt::Display for Point {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "({}, {})", self.x, self.y)
    }
}

```

</Listing>

那么，在 `Point` 上实现 `OutlinePrint` trait 将会成功编译，我们可以在一个 `Point` 实例上调用 `outline_print` 来将其显示在星号组成的标题中。

<!-- Old headings. Do not remove or links may break. -->

<a id="using-the-newtype-pattern-to-implement-external-traits-on-external-types"></a>
<a id="using-the-newtype-pattern-to-implement-external-traits"></a>

### 使用 Newtype 模式实现外部特征

在第十章的 [“Implementing a Trait on a Type”][implementing-a-trait-on-a-type]<!--
ignore --> 部分中，我们提到了“孤儿规则”，该规则规定：
我们只能在类型上实现某个 trait，前提是 trait 或类型本身，或者两者都位于我们的 crate 内部。通过使用 newtype 模式，可以绕过这一限制。这种模式涉及在 tuple struct 中创建一个新的类型。（我们在第五章的 [“Creating Different Types with
Tuple Structs”][tuple-structs]<!-- ignore --> 部分已经介绍过 tuple struct。）这个 tuple struct 将包含一个字段，并作为我们想要实现 trait 的类型的一个薄包装层。这样一来，包装层类型就位于我们的 crate 内部，我们可以在该包装层上实现 trait。_Newtype_ 这个术语源自 Haskell 编程语言。使用这种模式并不会对运行时性能产生任何影响，而且包装层类型在编译时会被省略。

例如，假设我们想要在 `Vec<T>` 上实现 `Display`，但由于孤儿规则的限制，我们无法直接这样做，因为 `Display` 特质和 `Vec<T>` 类型是在我们的 crate 之外定义的。我们可以创建一个 `Wrapper` 结构体，该结构体包含一个 `Vec<T>` 的实例；然后，我们可以在 `Wrapper` 上实现 `Display`，并使用 `Vec<T>` 的值，如清单 20-24 所示。

**清单 20-24:** *src/main.rs* — 围绕 `Vec<String>` 创建 `Wrapper` 类型以实现 `Display`

```rust
use std::fmt;

struct Wrapper(Vec<String>);

impl fmt::Display for Wrapper {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "[{}]", self.0.join(", "))
    }
}

fn main() {
    let w = Wrapper(vec![String::from("hello"), String::from("world")]);
    println!("w = {w}");
}

```

该实现中，使用 `self.0` 来访问内部的 `Vec<T>`，因为 `Wrapper` 是一个元组结构，而 `Vec<T>` 是元组中索引为 0 的元素。然后，我们可以利用 `Display` 特质的功能来操作 `Wrapper`。

使用这种技术的缺点是，`Wrapper`是一种新类型，因此它没有它所持有的值的任何方法。我们必须直接在`Wrapper`上实现`Vec<T>`的所有方法，这样这些方法就可以委托给`self.0`，从而让我们可以像对待`Vec<T>`一样对待`Wrapper`。如果我们希望新类型拥有内部类型的所有方法，那么可以在`Wrapper`上实现`Deref`特性，以返回内部类型，这确实是一个解决方案（我们在第15章的`Deref`特性实现部分进行了讨论）。如果我们不希望`Wrapper`类型拥有内部类型的所有方法——例如，为了限制`Wrapper`类型的特性——那么我们就必须手动实现我们真正需要的方法。

这种新类型模式在不涉及特质的情况下也同样有用。让我们转移一下注意力，看看一些与 Rust 类型系统交互的高级方法。

[newtype]: ch20-02-advanced-traits.html#implementing-external-traits-with-the-newtype-pattern
[implementing-a-trait-on-a-type]: ch10-02-traits.html#implementing-a-trait-on-a-type
[traits]: ch10-02-traits.html
[smart-pointer-deref]: ch15-02-deref.html#treating-smart-pointers-like-regular-references
[tuple-structs]: ch05-01-defining-structs.html#creating-different-types-with-tuple-structs
