<!-- Old headings. Do not remove or links may break. -->

<a id="treating-smart-pointers-like-regular-references-with-the-deref-trait"></a>
<a id="treating-smart-pointers-like-regular-references-with-deref"></a>

## 将智能指针视为普通引用

实现 `Deref` 特性可以让你自定义 _dereference 运算符_ `*` 的行为（不要与乘法或全局运算符混淆）。通过实现 `Deref`，使得智能指针可以像普通引用一样被处理，你就可以编写能够操作引用的代码，并且这些代码也可以与智能指针一起使用。

首先，让我们看看解引用运算符是如何与普通引用协同工作的。接着，我们将尝试定义一个自定义类型，该类型的行为类似于 `Box<T>`，并了解为什么解引用运算符在我们新定义的类型上并不像引用那样工作。我们将探讨如何实现 `Deref` 特性，从而让智能指针能够以类似于引用的方式工作。最后，我们将了解 Rust 中的解引用强制转换功能，以及它如何让我们能够使用引用或智能指针。

<!-- Old headings. Do not remove or links may break. -->

<a id="following-the-pointer-to-the-value-with-the-dereference-operator"></a>
<a id="following-the-pointer-to-the-value"></a>

### 跟随对值的引用

常规引用是一种指针类型，可以将指针视为指向其他地方存储的值的箭头。在 Listing 15-6 中，我们创建了一个指向 `i32` 值的引用，然后使用解引用运算符来追踪该引用所指向的值。

<Listing number="15-6" file-name="src/main.rs" caption="Using the dereference operator to follow a reference to an `i32` value">

```rust
fn main() {
    let x = 5;
    let y = &x;

    assert_eq!(5, x);
    assert_eq!(5, *y);
}

```

</Listing>

变量 `x` 包含一个 `i32` 的值，该值又指向 `5`。我们将 `y` 设置为对 `x` 的引用。因此，我们可以断言 `x` 等于 `5`。然而，如果我们想对 `y` 中的值进行断言，我们必须使用 `*y` 来访问它指向的值（即进行解引用），这样编译器才能比较实际的值。一旦我们解引用了 `y`，我们就能访问 `y` 所指向的整数值，并将其与 `5` 进行比较。

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

我们可以将清单15-6中的代码重新编写，使用 `Box<T>` 代替引用；在清单15-7中用于 `Box<T>` 的解引用操作，其工作方式与在清单15-6中用于引用对象的解引用操作相同。

<Listing number="15-7" file-name="src/main.rs" caption="Using the dereference operator on a `Box<i32>`">

```rust
fn main() {
    let x = 5;
    let y = Box::new(x);

    assert_eq!(5, x);
    assert_eq!(5, *y);
}

```

</Listing>

The main difference between Listing 15-7 and Listing 15-6 is that here we set
`y` to be an instance of a box pointing to a copied value of `x` rather than a
reference pointing to the value of `x`. In the last assertion, we can use the
dereference operator to follow the box’s pointer in the same way that we did
when `y` was a reference. Next, we’ll explore what is special about `Box<T>`
that enables us to use the dereference operator by defining our own box type.

### Defining Our Own Smart Pointer

Let’s build a wrapper type similar to the `Box<T>` type provided by the
standard library to experience how smart pointer types behave differently from
references by default. Then, we’ll look at how to add the ability to use the
dereference operator.

> Note: There’s one big difference between the `MyBox<T>` type we’re about to
> build and the real `Box<T>`: Our version will not store its data on the heap.
> We are focusing this example on `Deref`, so where the data is actually stored
> is less important than the pointer-like behavior.

The `Box<T>` type is ultimately defined as a tuple struct with one element, so
Listing 15-8 defines a `MyBox<T>` type in the same way. We’ll also define a
`new` function to match the `new` function defined on `Box<T>`.

<Listing number="15-8" file-name="src/main.rs" caption="Defining a `MyBox<T>` type">

```rust
struct MyBox<T>(T);

impl<T> MyBox<T> {
    fn new(x: T) -> MyBox<T> {
        MyBox(x)
    }
}

```

</Listing>

我们定义了一个名为 `MyBox` 的结构体，并声明了一个泛型参数 `T`，因为我们希望我们的类型能够容纳任何类型的值。 `MyBox` 是一个元组结构体，其中包含一个类型为 `T` 的元素。 `MyBox::new` 函数接受一个类型为 `T` 的参数，并返回一个包含传入值的 `MyBox` 实例。

让我们尝试在清单15-7中添加 `main` 函数到清单15-8中，并将其改为使用我们定义的 `MyBox<T>` 类型，而不是 `Box<T>` 类型。由于Rust无法引用 `MyBox`，因此清单15-9中的代码将无法编译。

<Listing number="15-9" file-name="src/main.rs" caption="Attempting to use `MyBox<T>` in the same way we used references and `Box<T>`">

```rust,ignore,does_not_compile
fn main() {
    let x = 5;
    let y = MyBox::new(x);

    assert_eq!(5, x);
    assert_eq!(5, *y);
}

```

</Listing>

Here’s the resultant compilation error:

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

Our `MyBox<T>` type can’t be dereferenced because we haven’t implemented that
ability on our type. To enable dereferencing with the `*` operator, we
implement the `Deref` trait.

<!-- Old headings. Do not remove or links may break. -->

<a id="treating-a-type-like-a-reference-by-implementing-the-deref-trait"></a>

### Implementing the `Deref` Trait

As discussed in [“Implementing a Trait on a Type”][impl-trait]<!-- ignore --> in
Chapter 10, to implement a trait we need to provide implementations for the
trait’s required methods. The `Deref` trait, provided by the standard library,
requires us to implement one method named `deref` that borrows `self` and
returns a reference to the inner data. Listing 15-10 contains an implementation
of `Deref` to add to the definition of `MyBox<T>`.

<Listing number="15-10" file-name="src/main.rs" caption="Implementing `Deref` on `MyBox<T>`">

```rust
use std::ops::Deref;

impl<T> Deref for MyBox<T> {
    type Target = T;

    fn deref(&self) -> &Self::Target {
        &self.0
    }
}

```

</Listing>

`type Target = T;`语法为`Deref`特质定义了一个关联类型，以便使用。关联类型是一种稍微不同的声明泛型参数的方式，但目前不必担心它们；我们将在第20章中更详细地介绍它们。

我们将 `deref` 方法的主体替换为 `&self.0`，这样 `deref` 就能返回对我们使用 `*` 操作符要访问的值的引用；回想一下第5章中关于“使用元组结构体创建不同类型”的内容[tuple-structs]<!--
ignore -->，其中 `.0` 用于访问元组结构体中的第一个值。现在，列表15-9中的 `main` 函数能够调用 `*` 对 `MyBox<T>` 值进行操作，并且代码可以成功编译，所有的断言也都通过了！

如果没有 `Deref` 特性，编译器只能解引用 `&` 类型的引用。而 `deref` 方法则使编译器能够获取任何实现了 `Deref` 类型的数值，并调用 `deref` 方法来获取一个可以解引用的引用。

当我们在 Listing 15-9 中输入 `*y` 时，Rust 实际上在后台运行了以下代码：

```rust,ignore
*(y.deref())
```

Rust 通过将 `*` 运算符替换为对 `deref` 方法的调用，然后再进行简单的解引用操作，这样我们就无需考虑是否需要调用 `deref` 方法了。这一特性使得我们可以编写出无论使用普通引用还是实现了 `Deref` 接口的类型，代码都能同样正常运行的程序。

之所以 `deref` 方法返回的是对某个值的引用，而 `*(y.deref())` 方法外部的普通解引用操作仍然是必要的，这与所有权系统有关。如果 `deref` 方法直接返回该值，而不是返回对该值的引用，那么该值就会从 `self` 中移出。在这种情况下，或者在我们使用解引用操作符的大多数情况下，我们都不希望拥有 `MyBox<T>` 内部的值的所有权。

请注意，`*`运算符被替换为对`deref`方法的调用，然后仅对`*`运算符进行一次调用，每次在代码中都使用`*`。由于`*`运算符的替换不会无限递归，最终我们得到的数据类型为`i32`，这与`assert_eq!`中的`5`相匹配。详见列表15-9。

<!-- Old headings. Do not remove or links may break. -->

<a id="implicit-deref-coercions-with-functions-and-methods"></a>
<a id="using-deref-coercions-in-functions-and-methods"></a>

### 在函数和方法中使用去引用强制类型转换

_解引用强制转换_将指向实现了 `Deref` 特征的类型的引用转换为指向另一个类型的引用。例如，解引用强制转换可以将 `&String` 转换为 `&str`，因为 `String` 实现了 `Deref` 特征，从而返回 `&str`。解引用强制转换是 Rust 对函数和方法参数进行的便捷操作，且仅适用于实现了 `Deref` 特征的类型。当我们将指向特定类型的引用作为参数传递给一个与函数或方法定义中的参数类型不匹配的函数或方法时，解引用强制转换会自动发生。对 `deref` 方法的连续调用会将我们提供的类型转换为参数所需的类型。

Rust 增加了解引用强制功能，这样编写函数和方法的程序员就不需要使用 `&` 和 `*` 来添加如此多的显式引用和解引用操作。解引用强制功能还使我们能够编写更多适用于引用或智能指针的代码。

为了看到去引用强制转换的实际应用，我们可以使用在清单15-8中定义的`MyBox<T>`类型，以及我们在清单15-10中添加的`Deref`的实现。清单15-11展示了一个具有字符串切片参数的函数的定义。

<Listing number="15-11" file-name="src/main.rs" caption="A `hello` function that has the parameter `name` of type `&str`">

```rust
fn hello(name: &str) {
    println!("Hello, {name}!");
}

```

</Listing>

我们可以将`hello`函数以字符串切片作为参数进行调用，例如`hello("Rust");`。通过解引用强制操作，我们可以以`MyBox<String>`类型的引用来调用`hello`，如清单15-12所示。

<Listing number="15-12" file-name="src/main.rs" caption="Calling `hello` with a reference to a `MyBox<String>` value, which works because of deref coercion">

```rust
fn main() {
    let m = MyBox::new(String::from("Rust"));
    hello(&m);
}

```

</Listing>

Here we’re calling the `hello` function with the argument `&m`, which is a
reference to a `MyBox<String>` value. Because we implemented the `Deref` trait
on `MyBox<T>` in Listing 15-10, Rust can turn `&MyBox<String>` into `&String`
by calling `deref`. The standard library provides an implementation of `Deref`
on `String` that returns a string slice, and this is in the API documentation
for `Deref`. Rust calls `deref` again to turn the `&String` into `&str`, which
matches the `hello` function’s definition.

If Rust didn’t implement deref coercion, we would have to write the code in
Listing 15-13 instead of the code in Listing 15-12 to call `hello` with a value
of type `&MyBox<String>`.

<Listing number="15-13" file-name="src/main.rs" caption="The code we would have to write if Rust didn’t have deref coercion">

```rust
fn main() {
    let m = MyBox::new(String::from("Rust"));
    hello(&(*m)[..]);
}

```

</Listing>

The `(*m)` dereferences the `MyBox<String>` into a `String`. Then, the `&` and
`[..]` take a string slice of the `String` that is equal to the whole string to
match the signature of `hello`. This code without deref coercions is harder to
read, write, and understand with all of these symbols involved. Deref coercion
allows Rust to handle these conversions for us automatically.

When the `Deref` trait is defined for the types involved, Rust will analyze the
types and use `Deref::deref` as many times as necessary to get a reference to
match the parameter’s type. The number of times that `Deref::deref` needs to be
inserted is resolved at compile time, so there is no runtime penalty for taking
advantage of deref coercion!

<!-- Old headings. Do not remove or links may break. -->

<a id="how-deref-coercion-interacts-with-mutability"></a>

### Handling Deref Coercion with Mutable References

Similar to how you use the `Deref` trait to override the `*` operator on
immutable references, you can use the `DerefMut` trait to override the `*`
operator on mutable references.

Rust does deref coercion when it finds types and trait implementations in three
cases:

1. From `&T` to `&U` when `T: Deref<Target=U>`
2. From `&mut T` to `&mut U` when `T: DerefMut<Target=U>`
3. From `&mut T` to `&U` when `T: Deref⊂PH48`

The first two cases are the same except that the second implements mutability.
The first case states that if you have a `&T⊂PH50⊂T` implements `Deref⊂PH52⊂U⊂PH53⊂&U。第二种情况表明，对于可变的引用，也会发生相同的deref操作。

第三种情况更为复杂：Rust还会将可变引用强制转换为不可变引用。但是反过来是不可能的：不可变引用永远无法被强制转换为可变引用。由于借用规则的存在，如果你有一个可变引用，那么这个可变引用必须是对该数据的唯一引用（否则程序将无法编译）。将一个可变引用转换为不可变引用不会违反借用规则。然而，将不可变引用转换为可变引用则需要初始的不可变引用必须是对该数据的唯一不可变引用，但借用规则并不保证这一点。因此，Rust无法假设将不可变引用转换为可变引用是可能的。

[impl-trait]: ch10-02-traits.html#implementing-a-trait-on-a-type
[tuple-structs]: ch05-01-defining-structs.html#creating-different-types-with-tuple-structs
