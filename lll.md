<!-- Old headings. Do not remove or links may break. -->

<a id="treating-smart-pointers-like-regular-references-with-the-deref-trait"></a>
<a id="treating-smart-pointers-like-regular-references-with-deref"></a>

## 将智能指针视为普通引用

实现 `Deref` 特性可以让你自定义 _dereference 运算符_ `*` 的行为（不要与乘法或全局运算符混淆）。通过实现 `Deref`，使得智能指针可以像普通引用一样被处理，你就可以编写能够操作引用的代码，并且这些代码也可以与智能指针一起使用。

首先，让我们看看解引用运算符是如何与普通引用协同工作的。接着，我们将尝试定义一个自定义类型，该类型的行为类似于 `Box<T>`，并了解为什么解引用运算符在我们新定义的类型上并不像引用那样工作。我们将探讨如何实现 `Deref` 特性，从而让智能指针能够以类似于引用的方式工作。最后，我们将了解 Rust 中的解引用强制转换功能，以及它如何让我们能够使用引用或智能指针。

<!-- Old headings. Do not remove or links may break. -->

<a id="following-the-pointer-to-the-value-with-the-dereference-operator"></a>
<a id="following-the-pointer-to-the-value"></a>

### 跟随值的引用

常规引用是一种指针类型，可以将指针视为指向其他地方存储的值的箭头。在 Listing 15-6 中，我们创建了一个指向 `i32` 值的引用，然后使用解引用运算符来追踪该引用所指向的值。

**列表 15-6:** *src/main.rs* — 使用去引用运算符来访问一个 `i32` 值的引用

```rust
fn main() {
    let x = 5;
    let y = &x;

    assert_eq!(5, x);
    assert_eq!(5, *y);
}

```

变量 `x` 包含一个 `i32` 的值，该值又指向 `5`。我们将 `y` 设置为对 `x` 的引用。因此，我们可以断言 `x` 等于 `5`。然而，如果我们想获取 `y` 中的具体值，就必须使用 `*y` 来获取它指向的值（即进行解引用操作），这样编译器才能比较实际的值。一旦我们完成了解引用操作，我们就能访问 `y` 所指向的整数值，并将其与 `5` 进行比较。

如果我们尝试使用 `assert_eq!(5, y);` 来编写代码，将会出现以下编译错误：

```console
$ cargo run
   Compiling deref-example v0.1.0 (file:///projects/deref-example)
error[E0277]: can't compare `{integer}` with `&{integer}`
 --> src/main.rs:6:5
  |
6 |     assert_eq!(5, y);
  |     ^^^^^^^^^^^^^^^^ no implementation for `{integer} == &{integer}`
  |
  = help: the trait `PartialEq<&{integer}>` is not implemented for `{integer}`
  = note: this error originates in the macro `assert_eq` (in Nightly builds, run with -Z macro-backtrace for more info)

For more information about this error, try `rustc --explain E0277`.
error: could not compile `deref-example` (bin "deref-example") due to 1 previous error

```

比较一个数字和一个对数字的引用是不允许的，因为它们属于不同的类型。我们必须使用解引用运算符来跟随那个引用，以获取它所指的值。

### 如何将 `Box<T>` 作为参考使用

我们可以将列表15-6中的代码重新编写，使用 `Box<T>` 代替引用操作；在列表15-7中用于对 `Box<T>` 进行解引用操作的运算符，其工作方式与在列表15-6中对引用进行解引用操作时的运算符相同。

**列表 15-7:** *src/main.rs* — 在 `Box<i32>` 上使用去引用运算符

```rust
fn main() {
    let x = 5;
    let y = Box::new(x);

    assert_eq!(5, x);
    assert_eq!(5, *y);
}

```

Listing 15-7与Listing 15-6的主要区别在于，在这里我们将`y`设置为指向`x`的复制值的盒子实例，而不是指向`x`值的引用。在最后一个断言中，我们可以使用解引用操作符来跟随盒子的指针，就像我们在`y`是引用时所做的那样。接下来，我们将探讨`Box<T>`的特殊之处，这种特殊之处使得我们可以通过定义自己的盒子类型来使用解引用操作符。

### 定义我们自己的智能指针

让我们构建一个类似于标准库提供的 `Box<T>` 类型的包装类型，以此来了解智能指针类型与默认引用方式之间的区别。接下来，我们将探讨如何添加使用解引用操作符的功能。

>注意：我们即将构建的 `MyBox<T>` 类型与真正的 `Box<T>` 之间存在一个重要区别：我们的版本不会将数据存储在堆上。我们重点讨论的是 `Deref`，因此数据的实际存储位置不如指针式的行为重要。

`Box<T>`类型最终被定义为一个只有一个元素的元组结构，因此
清单15-8以相同的方式定义了一个`MyBox<T>`类型。我们还将定义一个`new`函数，用于匹配在`Box<T>`上定义的`new`函数。

**清单 15-8:** *src/main.rs* — 定义一个 `MyBox<T>` 类型

```rust
struct MyBox<T>(T);

impl<T> MyBox<T> {
    fn new(x: T) -> MyBox<T> {
        MyBox(x)
    }
}

```

我们定义了一个名为 `MyBox` 的结构体，并声明了一个泛型参数 `T`，因为我们希望我们的类型能够容纳任何类型的值。 `MyBox` 类型是一个元组结构体，其中包含一个类型为 `T` 的元素。 `MyBox::new` 函数接受一个类型为 `T` 的参数，并返回一个 `MyBox` 实例，该实例包含传入的值。

让我们尝试在清单15-7中添加 `main` 函数到清单15-8中，并将其改为使用我们定义的 `MyBox<T>` 类型，而不是 `Box<T>`。由于Rust无法引用 `MyBox`，因此清单15-9中的代码将无法编译。

**清单 15-9:** *src/main.rs* — 尝试以与引用和 `Box<T>` 相同的方式使用 `MyBox<T>`

```rust,ignore,does_not_compile
fn main() {
    let x = 5;
    let y = MyBox::new(x);

    assert_eq!(5, x);
    assert_eq!(5, *y);
}

```

以下是编译产生的错误：

```console
$ cargo run
   Compiling deref-example v0.1.0 (file:///projects/deref-example)
error[E0614]: type `MyBox<{integer}>` cannot be dereferenced
  --> src/main.rs:14:19
   |
14 |     assert_eq!(5, *y);
   |                   ^^ can't be dereferenced

For more information about this error, try `rustc --explain E0614`.
error: could not compile `deref-example` (bin "deref-example") due to 1 previous error

```

我们的 `MyBox<T>` 类型无法被解引用，因为我们还没有在該类型上实现這種功能。為了讓 `*` 運算符能夠實現解引用功能，我們需要實現 `Deref` 屬性。

<!-- Old headings. Do not remove or links may break. -->

<a id="treating-a-type-like-a-reference-by-implementing-the-deref-trait"></a>

### 实现 `Deref` 特质

如 [“Implementing a Trait on a Type”][impl-trait]<!-- ignore --> 中所讨论的，在第十章中，要实现一个特质，我们需要为该特质所需的方法提供实现。标准库提供的 `Deref` 特质要求我们实现一个名为 `deref` 的方法，该方法会借用 `self` 并返回对内部数据的引用。列表 15-10 中包含了 `Deref` 的实现，以便添加到 `MyBox<T>` 的定义中。

**清单 15-10:** *src/main.rs* — 在 `MyBox<T>` 上实现 `Deref`

```rust
use std::ops::Deref;

impl<T> Deref for MyBox<T> {
    type Target = T;

    fn deref(&self) -> &Self::Target {
        &self.0
    }
}

```

这种 `type Target = T;` 语法为 `Deref` 特质定义了一个关联类型，以便使用。关联类型是一种稍微不同的声明泛型参数的方式，但目前不必担心它们；我们将在第20章中更详细地介绍它们。

我们将 `deref` 方法的主体替换为 `&self.0`，这样 `deref` 就能返回对我们使用 `*` 操作符要访问的值的引用；回想一下第5章中 [“Creating Different Types with Tuple Structs”][tuple-structs]<!--
ignore --> 的内容，其中 `.0` 可以访问元组结构中的第一个值。现在，列表15-9中的 `main` 函数可以调用 `*` 对 `MyBox<T>` 值进行操作，并且代码可以成功编译，所有的断言也都通过了！

如果没有 `Deref` 特性，编译器只能解引用 `&` 类型的引用。而 `deref` 方法则使编译器能够获取任何实现了 `Deref` 类型的数值，并调用 `deref` 方法来获取可以解引用的引用。

当我们在 Listing 15-9 中输入 `*y` 时，Rust 在后台实际上运行了以下代码：

```rust,ignore
*(y.deref())
```

Rust 通过将 `*` 运算符替换为对 `deref` 方法的调用，然后再进行简单的解引用操作，这样我们就无需考虑是否需要调用 `deref` 方法了。这一特性使得我们可以编写出无论使用普通引用还是实现了 `Deref` 类型的引用时都能正常工作的代码。

之所以 `deref` 方法返回的是对值的引用，而 `*(y.deref())` 方法中的直接去引用操作仍然是必要的，这与所有权系统有关。如果 `deref` 方法直接返回值而不是引用，那么该值就会从 `self` 中移出。在这种情况下，或者在我们使用去引用操作符的大多数情况下，我们都不希望拥有 `MyBox<T>` 内部的值。

请注意，`*`运算符被替换为对`deref`方法的调用，然后仅对`*`运算符进行一次调用，每次在代码中都使用`*`。由于`*`运算符的替换不会无限递归，最终我们得到的数据类型为`i32`，这与`assert_eq!`中的`5`相匹配，如清单15-9所示。

<!-- Old headings. Do not remove or links may break. -->

<a id="implicit-deref-coercions-with-functions-and-methods"></a>
<a id="using-deref-coercions-in-functions-and-methods"></a>

### 在函数和方法中使用去引用强制类型转换

_解引用强制转换_将指向实现了 `Deref` 特性的类型的引用转换为指向另一个类型的引用。例如，解引用强制转换可以将 `&String` 转换为 `&str`，因为 `String` 实现了 `Deref` 特性，从而返回 `&str`。解引用强制转换是 Rust 对函数和方法参数进行的便捷操作，且仅适用于实现了 `Deref` 特性的类型。当我们将指向特定类型的引用作为参数传递给一个与函数或方法定义中的参数类型不匹配的函数或方法时，解引用强制转换会自动发生。对 `deref` 方法的连续调用会将我们提供的类型转换为参数所需的类型。

Rust中增加了解引用强制操作，这样编写函数和方法调用的程序员就不必频繁地使用 `&` 和 `*` 来进行显式的引用和解引用操作。解引用强制功能还使我们能够编写更多适用于引用或智能指针的代码。

为了看到去引用强制转换的实际应用，我们可以使用在清单15-8中定义的 `MyBox<T>` 类型，以及我们在清单15-10中添加的 `Deref` 实现。清单15-11展示了一个具有字符串切片参数的函数的定义。

**清单 15-11:** *src/main.rs* — 一个函数，其参数类型为 `&str`，函数本身的类型为 `name`

```rust
fn hello(name: &str) {
    println!("Hello, {name}!");
}

```

我们可以将字符串切片作为参数来调用 `hello` 函数，例如 `hello("Rust");`。通过引用类型为 `MyBox<String>` 的值，也可以调用 `hello` 函数，如清单 15-12 所示。

**清单 15-12:** *src/main.rs* — 使用 `hello` 调用一个 `MyBox<String>` 值的函数，这种调用方式之所以有效，是因为存在去引用强制转换机制。

```rust
fn main() {
    let m = MyBox::new(String::from("Rust"));
    hello(&m);
}

```

在这里，我们调用了一个带有参数 `&m` 的函数，该函数是对 `MyBox<String>` 值的引用。由于我们在 Listing 15-10 中实现了 `MyBox<T>` 上的 `Deref` 特质，因此 Rust 可以通过调用 `deref` 将 `&MyBox<String>` 转换为 `&String`。标准库提供了 `String` 上的 `Deref` 实现，该实现返回一个字符串切片，这一信息可以在 `Deref` 的 API 文档中找到。Rust 再次调用 `deref` 来将 `&String` 转换为 `&str`，这与 `hello` 函数的定义相匹配。

如果Rust不实现去引用强制转换功能，我们就不得不像在清单15-12中那样编写代码，而不是在清单15-13中编写代码，来调用 `hello`，并且需要提供一个类型为 `&MyBox<String>` 的值。

**清单 15-13:** *src/main.rs* — 如果Rust没有去引用强制转换功能，我们必须要写的代码

```rust
fn main() {
    let m = MyBox::new(String::from("Rust"));
    hello(&(*m)[..]);
}

```

该代码将 `MyBox<String>` 解引用为 `String`。然后， `&` 和 `[..]` 会获取 `String` 中的一个字符串切片，这个切片等于整个字符串，以便与 `hello` 的签名相匹配。如果没有解引用强制操作，这样的代码会难以阅读、编写和理解，因为需要处理所有这些符号。解引用强制操作使得 Rust 能够自动处理这些转换。

当涉及的类型定义了 `Deref` trait 时，Rust 会分析这些类型，并根据需要多次使用 `Deref::deref` 来获取与参数类型匹配的引用。而 `Deref::deref` 需要被插入的次数则是在编译时确定的，因此利用去引用强制转换并不会造成运行时的性能损失！

<!-- Old headings. Do not remove or links may break. -->

<a id="how-deref-coercion-interacts-with-mutability"></a>

### 使用可变引用处理隐式强制类型转换

类似于使用 `Deref` 特性来覆盖不可变引用上的 `*` 运算符，你也可以使用 `DerefMut` 特性来覆盖可变引用上的 `*` 运算符。

当 Rust 在三种情况下发现类型及 trait 实现时，会执行去引用强制转换操作：

1. 从 `&T` 到 `&U`，当 `T: Deref<Target=U>`  
2. 从 `&mut T` 到 `&mut U`，当 `T: DerefMut<Target=U>`  
3. 从 `&mut T` 到 `&U`，当 `T: Deref<Target=U>`

前两种情况是相同的，只是第二种情况实现了可变性。  
第一种情况指出，如果你有一个 `&T`，并且 `T` 实现了 `Deref` 到某种类型 `U`，那么你可以透明地获得 `&U`。第二种情况则指出，对于可变引用，同样会发生去引用转换。

第三种情况更为复杂：Rust还会将可变引用强制转换为不可变引用。但是反过来是不可能的：不可变引用永远无法被强制转换为可变引用。由于借用规则的存在，如果你有一个可变引用，那么这个可变引用必须是对该数据的唯一引用（否则程序将无法编译）。将一个可变引用转换为不可变引用不会违反借用规则。然而，将不可变引用转换为可变引用则需要初始的不可变引用必须是对该数据的唯一不可变引用，但借用规则并不保证这一点。因此，Rust无法假设将不可变引用转换为可变引用是可能的。

[impl-trait]: ch10-02-traits.html#implementing-a-trait-on-a-type
[tuple-structs]: ch05-01-defining-structs.html#creating-different-types-with-tuple-structs
