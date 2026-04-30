## 通用数据类型

我们使用泛型来为函数签名或结构体等元素定义规范，然后可以将这些定义应用于多种具体数据类型。首先，让我们看看如何使用泛型来定义函数、结构体、枚举和方法。接着，我们将讨论泛型对代码性能的影响。

### 在函数定义中

在定义使用泛型的函数时，我们将泛型放在函数的签名中，而通常我们会在这里指定参数和返回值的数据类型。这样做可以使我们的代码更加灵活，为函数的调用者提供更多的功能，同时还能避免代码重复。

继续我们的 `largest` 函数，列表 10-4 展示了两个都能找到切片中最大值的函数。之后，我们将这两个函数合并成一个使用泛型的函数。

<Listing number="10-4" file-name="src/main.rs" caption="Two functions that differ only in their names and in the types in their signatures">

```rust
fn largest_i32(list: &[i32]) -> &i32 {
    let mut largest = &list[0];

    for item in list {
        if item > largest {
            largest = item;
        }
    }

    largest
}

fn largest_char(list: &[char]) -> &char {
    let mut largest = &list[0];

    for item in list {
        if item > largest {
            largest = item;
        }
    }

    largest
}

fn main() {
    let number_list = vec![34, 50, 25, 100, 65];

    let result = largest_i32(&number_list);
    println!("The largest number is {result}");

    let char_list = vec!['y', 'm', 'a', 'q'];

    let result = largest_char(&char_list);
    println!("The largest char is {result}");
}

```

</Listing>

`largest_i32`函数是我们从清单10-3中提取出来的函数，它用于找出切片中最大的`i32`。`largest_char`函数则用于找出切片中最大的`char`。这两个函数的功能本质上是相同的，因此我们可以通过在单个函数中引入一个通用类型参数来消除重复代码。

为了在一个新的单一函数中参数化类型，我们需要为类型参数命名，就像为函数的值参数命名一样。你可以使用任何标识符作为类型参数名。不过，我们会使用 `T`，因为按照惯例，Rust 中的类型参数名通常很短，通常只有一个字母，而且 Rust 的类型命名惯例是 UpperCamelCase。 `T` 是大多数 Rust 程序员默认的命名方式。

当我们在函数体内使用参数时，必须在函数签名中声明该参数的名称，这样编译器才能明白这个名称的含义。同样地，当我们在函数签名中使用类型参数名称时，也必须在使用之前先声明该类型参数名称。为了定义泛型函数`largest`，我们需要在尖括号`<>`内声明类型名称，并将其放在函数名称和参数列表之间，如下所示：

```rust,ignore
fn largest<T>(list: &[T]) -> &T {
```

我们将这个定义理解为：“函数 `largest` 是某种类型的泛化，即 `largest` 是某种类型下的通用函数。” 这个函数有一个名为 `list` 的参数，该参数是一个类型为 `T` 的值的切片。而 `largest` 函数将返回一个指向相同类型 `T` 的值的引用。

列表10-5展示了使用泛型数据类型时，`largest`函数的完整定义。该列表还展示了如何通过使用`i32`或`char`的值来调用这个函数。请注意，这段代码目前还无法编译。

<Listing number="10-5" file-name="src/main.rs" caption="The `largest` function using generic type parameters; this doesn’t compile yet">

```rust,ignore,does_not_compile
fn largest<T>(list: &[T]) -> &T {
    let mut largest = &list[0];

    for item in list {
        if item > largest {
            largest = item;
        }
    }

    largest
}

fn main() {
    let number_list = vec![34, 50, 25, 100, 65];

    let result = largest(&number_list);
    println!("The largest number is {result}");

    let char_list = vec!['y', 'm', 'a', 'q'];

    let result = largest(&char_list);
    println!("The largest char is {result}");
}

```

</Listing>

如果我们现在编译这段代码，将会出现以下错误：

```console
$ cargo run
   Compiling chapter10 v0.1.0 (file:///projects/chapter10)
error[E0369]: binary operation `>` cannot be applied to type `&T`
 --> src/main.rs:5:17
  |
5 |         if item > largest {
  |            ---- ^ ------- &T
  |            |
  |            &T
  |
help: consider restricting type parameter `T` with trait `PartialOrd`
  |
1 | fn largest<T: std::cmp::PartialOrd>(list: &[T]) -> &T {
  |             ++++++++++++++++++++++

For more information about this error, try `rustc --explain E0369`.
error: could not compile `chapter10` (bin "chapter10") due to 1 previous error

```

帮助文本中提到了`std::cmp::PartialOrd`，这是一种特质。我们将在下一节中讨论特质。目前，请注意这个错误表明`largest`的主体无法适用于`T`可能存在的所有类型。因为我们需要在主体中比较类型为`T`的值，所以我们只能使用那些值可以排序的类型。为了启用比较功能，标准库提供了`std::cmp::PartialOrd`特质，你可以将其应用于类型上（有关此特质的更多信息，请参见附录C）。为了修复清单10-5，我们可以按照帮助文本的建议，将适用于`T`的类型限制为那些实现了`PartialOrd`的类型。这样，清单就能成功编译了，因为标准库同时实现了`PartialOrd`在`i32`和`char`上。

### 在结构体定义中

我们还可以定义结构体，以便在其中一个或多个字段中使用泛型类型参数，使用 `<>` 语法。列表 10-6 定义了一个 `Point<T>` 结构体，用于存储任何类型的 `x` 和 `y` 坐标值。

<Listing number="10-6" file-name="src/main.rs" caption="A `Point<T>` struct that holds `x` and `y` values of type `T`">

```rust
struct Point<T> {
    x: T,
    y: T,
}

fn main() {
    let integer = Point { x: 5, y: 10 };
    let float = Point { x: 1.0, y: 4.0 };
}

```

</Listing>

The syntax for using generics in struct definitions is similar to that used in
function definitions. First, we declare the name of the type parameter inside
angle brackets just after the name of the struct. Then, we use the generic type
in the struct definition where we would otherwise specify concrete data types.

Note that because we’ve used only one generic type to define `Point<T>`, this
definition says that the `Point<T>` struct is generic over some type `T`, and
the fields `x` and `y` are _both_ that same type, whatever that type may be. If
we create an instance of a `Point<T>` that has values of different types, as in
Listing 10-7, our code won’t compile.

<Listing number="10-7" file-name="src/main.rs" caption="The fields `x` and `y` must be the same type because both have the same generic data type `T`.">

```rust,ignore,does_not_compile
struct Point<T> {
    x: T,
    y: T,
}

fn main() {
    let wont_work = Point { x: 5, y: 4.0 };
}

```

</Listing>

In this example, when we assign the integer value `5` to `x`, we let the
compiler know that the generic type `T` will be an integer for this instance of
`Point<T>`. Then, when we specify `4.0` for `y`, which we’ve defined to have
the same type as `x`, we’ll get a type mismatch error like this:

```console
$ cargo run
   Compiling chapter10 v0.1.0 (file:///projects/chapter10)
error[E0308]: mismatched types
 --> src/main.rs:7:38
  |
7 |     let wont_work = Point { x: 5, y: 4.0 };
  |                                      ^^^ expected integer, found floating-point number

For more information about this error, try `rustc --explain E0308`.
error: could not compile `chapter10` (bin "chapter10") due to 1 previous error

```

To define a `Point` struct where `x` and `y` are both generics but could have
different types, we can use multiple generic type parameters. For example, in
Listing 10-8, we change the definition of `Point` to be generic over types `T`
and `U` where `x` is of type `T` and `y` is of type `U`.

<Listing number="10-8" file-name="src/main.rs" caption="A `Point<T, U>`对两种类型进行泛型处理，使得`x`和`y`可以成为不同类型的值">

```rust
struct Point<T, U> {
    x: T,
    y: U,
}

fn main() {
    let both_integer = Point { x: 5, y: 10 };
    let both_float = Point { x: 1.0, y: 4.0 };
    let integer_and_float = Point { x: 5, y: 4.0 };
}

```

</Listing>

现在，所有形如 `Point` 的实例都是被允许的！你可以在一个定义中使用任意多的通用类型参数，但使用太多会导致代码难以阅读。如果你发现自己的代码中使用了大量的通用类型，那么可能需要对代码进行重构，将其拆分成更小的部分。

### 在枚举定义中

就像我们对结构体所做的那样，我们也可以定义枚举来保存各种通用数据类型。让我们再看一下标准库提供的 `Option<T>` 枚举，我们在第6章中就已经使用过它了。

```rust
enum Option<T> {
    Some(T),
    None,
}
```

这个定义现在应该对你来说更有意义了。如你所见，``Option<T>`` 这个枚举类型是对 ``T`` 的泛化，它有两个变体：``Some``，它只包含一个类型为 ``T`` 的值，以及另一个 ``None`` 变体，它不包含任何值。通过使用 ``Option<T>`` 这个枚举类型，我们可以表达一个可选值的抽象概念。由于 ``Option<T>`` 是泛化的，无论可选值的类型是什么，我们都可以使用这种抽象方式。

枚举类型也可以使用多种泛型类型。我们在第9章中使用的 `Result` 枚举就是一个例子：

```rust
enum Result<T, E> {
    Ok(T),
    Err(E),
}
```

`Result` 枚举类型适用于两种类型：`T` 和 `E`，并且有两个变体：`Ok`，它存储类型为 `T` 的值；以及 `Err`，它存储类型为 `E` 的值。这个定义使得我们可以在任何可能成功执行操作（返回某种类型为 `T` 的值）或可能失败（返回某种类型为 `E` 的错误）的情况下使用 `Result` 枚举类型。实际上，在 Listing 9-3 中，我们正是使用这种方式来打开文件的。当文件成功打开时，`T` 会被填充为类型为 `std::fs::File` 的值；而当文件打开出现问题时，`E` 会被填充为类型为 `std::io::Error` 的值。

当你在代码中发现多个结构体或枚举定义，它们只是持有的值类型不同时，可以通过使用泛型类型来避免重复。

### 方法定义

我们可以像在第五章中那样，对结构体枚举实现方法，并且也可以在它们的定义中使用泛型类型。列表10-9展示了我们在列表10-6中定义的一个结构体 `Point<T>`，并在该结构体上实现了一个名为 `x` 的方法。

<Listing number="10-9" file-name="src/main.rs" caption="Implementing a method named `x` on the `Point<T>` struct that will return a reference to the `x` field of type `T`">

```rust
struct Point<T> {
    x: T,
    y: T,
}

impl<T> Point<T> {
    fn x(&self) -> &T {
        &self.x
    }
}

fn main() {
    let p = Point { x: 5, y: 10 };

    println!("p.x = {}", p.x());
}

```

</Listing>

Here, we’ve defined a method named `x` on `Point<T>` that returns a reference
to the data in the field `x`.

Note that we have to declare `T` just after `impl` so that we can use `T` to
specify that we’re implementing methods on the type `Point<T>`. By declaring
`T` as a generic type after `impl`, Rust can identify that the type in the
angle brackets in `Point` is a generic type rather than a concrete type. We
could have chosen a different name for this generic parameter than the generic
parameter declared in the struct definition, but using the same name is
conventional. If you write a method within an `impl` that declares a generic
type, that method will be defined on any instance of the type, no matter what
concrete type ends up substituting for the generic type.

We can also specify constraints on generic types when defining methods on the
type. We could, for example, implement methods only on `Point<f32>` instances
rather than on `Point<T>` instances with any generic type. In Listing 10-10, we
use the concrete type `f32`, meaning we don’t declare any types after `impl`.

<Listing number="10-10" file-name="src/main.rs" caption="An `impl` block that only applies to a struct with a particular concrete type for the generic type parameter `T`">

```rust
impl Point<f32> {
    fn distance_from_origin(&self) -> f32 {
        (self.x.powi(2) + self.y.powi(2)).sqrt()
    }
}

```

</Listing>

This code means the type `Point<f32>` will have a `distance_from_origin`
method; other instances of `Point<T>` where `T` is not of type `f32` will not
have this method defined. The method measures how far our point is from the
point at coordinates (0.0, 0.0) and uses mathematical operations that are
available only for floating-point types.

Generic type parameters in a struct definition aren’t always the same as those
you use in that same struct’s method signatures. Listing 10-11 uses the generic
types `X1` and `Y1` for the `Point` struct and `X2` and `Y2` for the `mixup`
method signature to make the example clearer. The method creates a new `Point`
instance with the `x` value from the `self` `Point` (of type `X1`) and the `y`
value from the passed-in `Point` (of type `Y2`).

<Listing number="10-11" file-name="src/main.rs" caption="A method that uses generic types that are different from its struct’s definition">

```rust
struct Point<X1, Y1> {
    x: X1,
    y: Y1,
}

impl<X1, Y1> Point<X1, Y1> {
    fn mixup<X2, Y2>(self, other: Point<X2, Y2>) -> Point<X1, Y2> {
        Point {
            x: self.x,
            y: other.y,
        }
    }
}

fn main() {
    let p1 = Point { x: 5, y: 10.4 };
    let p2 = Point { x: "Hello", y: 'c' };

    let p3 = p1.mixup(p2);

    println!("p3.x = {}, p3.y = {}", p3.x, p3.y);
}

```

</Listing>

In `main`, we’ve defined a `Point` that has an `i32` for `x` (with value `5`)
and an `f64` for `y` (with value `10.4`). The `p2` variable is a `Point` struct
that has a string slice for `x` (with value `"Hello"`) and a `char` for `y`
(with value `c`). Calling `mixup` on `p1` with the argument `p2` gives us `p3`,
which will have an `i32` for `x` because `x` came from `p1`. The `p3` variable
will have a `char` for `y` because `y` came from `p2`. The `println!` macro
call will print `p3.x = 5, p3.y = c`.

The purpose of this example is to demonstrate a situation in which some generic
parameters are declared with `impl` and some are declared with the method
definition. Here, the generic parameters `X1` and `Y1` are declared after
`impl` because they go with the struct definition. The generic parameters `X2`
and `Y2` are declared after `fn mixup` because they’re only relevant to the
method.

### Performance of Code Using Generics

You might be wondering whether there is a runtime cost when using generic type
parameters. The good news is that using generic types won’t make your program
run any slower than it would with concrete types.

Rust accomplishes this by performing monomorphization of the code using
generics at compile time. _Monomorphization_ is the process of turning generic
code into specific code by filling in the concrete types that are used when
compiled. In this process, the compiler does the opposite of the steps we used
to create the generic function in Listing 10-5: The compiler looks at all the
places where generic code is called and generates code for the concrete types
the generic code is called with.

Let’s look at how this works by using the standard library’s generic
`Option<T>` enum:

```rust
let integer = Some(5);
let float = Some(5.0);
```

When Rust compiles this code, it performs monomorphization. During that
process, the compiler reads the values that have been used in `Option<T>`
instances and identifies two kinds of `Option⊂PH85⊂`: One is `i32` and the other
is `f64`. As such, it expands the generic definition of `Option⊂PH89⊂⊂PH90` and `f64`, thereby replacing the generic
definition with the specific ones.

The monomorphized version of the code looks similar to the following (the
compiler uses different names than what we’re using here for illustration):

<Listing file-name="src/main.rs">

```rust
enum Option_i32 {
    Some(i32),
    None,
}

enum Option_f64 {
    Some(f64),
    None,
}

fn main() {
    let integer = Option_i32::Some(5);
    let float = Option_f64::Some(5.0);
}
```

</Listing>

The generic `Option<T>`将被编译器创建的具体定义所替代。因为Rust将泛型代码编译成每个实例都指定了类型的代码，所以我们使用泛型时不会产生运行时的成本。当代码运行时，它的执行方式与我们手动复制每个定义时完全相同。这种单态化过程使得Rust的泛型在运行时非常高效。