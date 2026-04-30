<!-- Old headings. Do not remove or links may break. -->

<a id="closures-anonymous-functions-that-can-capture-their-environment"></a>
<a id="closures-anonymous-functions-that-capture-their-environment"></a>

## 闭包

Rust中的闭包是匿名函数，可以保存在变量中，或者作为参数传递给其他函数。你可以在一个地方创建闭包，然后在其他地方调用该闭包，以在不同的上下文中执行它。与函数不同，闭包可以捕获其定义范围内的变量值。我们将演示这些闭包特性如何允许代码的重用和行为的定制。

<!-- Old headings. Do not remove or links may break. -->

<a id="creating-an-abstraction-of-behavior-with-closures"></a>
<a id="refactoring-using-functions"></a>
<a id="refactoring-with-closures-to-store-code"></a>
<a id="capturing-the-environment-with-closures"></a>

### 捕捉环境

首先，我们将探讨如何使用闭包来捕获它们所定义的环境中的值，以便后续使用。具体情况如下：我们的T恤公司会定期向邮件列表中的用户赠送一件独家限量版T恤作为促销活动。邮件列表中的用户可以选择将自己的喜爱颜色添加到个人资料中。如果被选中的用户已经设置了自己喜爱的颜色，那么他们就会获得该颜色的T恤；如果用户没有指定喜爱的颜色，那么他们就会获得公司目前最受欢迎的颜色T恤。

实现这一功能的方法有很多。在这个示例中，我们将使用一个名为 `ShirtColor` 的枚举，该枚举包含 `Red` 和 `Blue` 两种变体（为了简化起见，只使用这两种变体来限制可用颜色的数量）。我们用一个 `Inventory` 结构体来表示公司的库存情况，该结构体有一个名为 `shirts` 的字段，该字段包含一个 `Vec<ShirtColor>`，代表当前有库存的衬衫颜色。在 `Inventory` 上定义的方法 `giveaway` 用于获取免费领取衬衫的用户的可选衬衫颜色偏好，并返回该用户将获得的衬衫颜色。这个实现方式如清单 13-1 所示。

<Listing number="13-1" file-name="src/main.rs" caption="Shirt company giveaway situation">

```rust,noplayground
#[derive(Debug, PartialEq, Copy, Clone)]
enum ShirtColor {
    Red,
    Blue,
}

struct Inventory {
    shirts: Vec<ShirtColor>,
}

impl Inventory {
    fn giveaway(&self, user_preference: Option<ShirtColor>) -> ShirtColor {
        user_preference.unwrap_or_else(|| self.most_stocked())
    }

    fn most_stocked(&self) -> ShirtColor {
        let mut num_red = 0;
        let mut num_blue = 0;

        for color in &self.shirts {
            match color {
                ShirtColor::Red => num_red += 1,
                ShirtColor::Blue => num_blue += 1,
            }
        }
        if num_red > num_blue {
            ShirtColor::Red
        } else {
            ShirtColor::Blue
        }
    }
}

fn main() {
    let store = Inventory {
        shirts: vec![ShirtColor::Blue, ShirtColor::Red, ShirtColor::Blue],
    };

    let user_pref1 = Some(ShirtColor::Red);
    let giveaway1 = store.giveaway(user_pref1);
    println!(
        "The user with preference {:?} gets {:?}",
        user_pref1, giveaway1
    );

    let user_pref2 = None;
    let giveaway2 = store.giveaway(user_pref2);
    println!(
        "The user with preference {:?} gets {:?}",
        user_pref2, giveaway2
    );
}

```

</Listing>

在 `main` 中定义的 `store` 有两件蓝色衬衫和一件红色衬衫剩余，这些衬衫将用于这次限量促销活动。我们将 `giveaway` 方法称为“偏好红色衬衫的用户”，而另一个方法则指“没有任何偏好需求的用户”。

再次强调，这段代码可以通过多种方式实现。在这里，为了专注于闭包的概念，我们仅讨论你已经学过的概念，除了 `giveaway` 方法的主体部分，该方法使用了闭包。在 `giveaway` 方法中，我们将用户偏好作为参数，该参数的类型为 `Option<ShirtColor>`，然后调用 `unwrap_or_else` 方法，该方法使用 `user_preference`。而 [`unwrap_or_else` 方法在 `Option<T>` 中，通过 [unwrap-or-else]<!-- ignore --> 实现，这个方法由标准库提供。它接受一个参数：一个没有任何参数的闭包，该闭包返回一个类型为 `T` 的值（与 `Some` 变体中的 `Option<T>` 存储的类型相同，在本例中为 `ShirtColor`）。如果 `Option<T>` 是 `Some` 的变体，则 `unwrap_or_else` 会从 `Some` 内部获取该值。如果 `Option<T>` 是 `None` 的变体，则 `unwrap_or_else` 会调用闭包，并返回闭包返回的值。

我们将闭包表达式 `|| self.most_stocked()` 作为 `unwrap_or_else` 的参数。这个闭包本身不接收任何参数（如果闭包有参数，这些参数会出现在两个竖线之间）。闭包的体部分调用了 `self.most_stocked()`。我们在这里定义这个闭包，而 `unwrap_or_else` 的实现将在之后执行，如果需要结果的话。

运行这段代码会输出以下内容：

```console
$ cargo run
   Compiling shirt-company v0.1.0 (file:///projects/shirt-company)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.27s
     Running `target/debug/shirt-company`
The user with preference Some(Red) gets Red
The user with preference None gets Blue

```

这里有一个有趣的点，那就是我们传递了一个闭包，该闭包在当前的 `Inventory` 实例上调用`self.most_stocked()`。标准库不需要了解我们定义的 `Inventory` 或 `ShirtColor` 类型，也不需要知道我们在这种情况下想要使用的逻辑。这个闭包捕获了对 `self` `Inventory` 实例的不可变引用，并将其与我们指定的代码一起传递给 `unwrap_or_else` 方法。而函数则无法以这种方式捕获它们的环境。

<!-- Old headings. Do not remove or links may break. -->

<a id="closure-type-inference-and-annotation"></a>

### 推断和注释闭包类型

函数和闭包之间存在更多差异。与函数不同，闭包通常不需要像函数那样对参数类型或返回值进行注解。函数需要类型注解，因为类型是属于用户所暴露的显式接口的一部分。严格定义这一接口对于确保每个人都对函数使用及返回的值的类型达成一致非常重要。而闭包则不会以这种方式被暴露到接口中：它们被存储在变量中，并且在不命名的情况下被使用，从而不会暴露给库的使用者。

闭包通常都很简短，且只适用于特定的上下文，而不是任意的场景。在这些有限的上下文中，编译器可以推断出参数的类型和返回类型的类型，这与编译器推断大多数变量类型的方式类似（不过也有极少数情况下，编译器需要为闭包指定类型）。

与变量类似，如果我们希望提高明确性和可读性，就可以添加类型注解。不过这样做会使得代码更加冗长，除非绝对有必要。对闭包进行类型注解的方式就像清单13-2中所示。在这个例子中，我们定义了一个闭包，并将其存储在一个变量中，而不是像清单13-1中那样在传递闭包作为参数的地方直接定义它。

<Listing number="13-2" file-name="src/main.rs" caption="Adding optional type annotations of the parameter and return value types in the closure">

```rust
    let expensive_closure = |num: u32| -> u32 {
        println!("calculating slowly...");
        thread::sleep(Duration::from_secs(2));
        num
    };

```

</Listing>

在添加了类型注解之后，闭包的语法看起来与函数的语法更为相似。这里，我们定义了一个将1加到其参数上的函数，以及一个具有相同行为的闭包，以便进行比较。我们添加了一些空格来使相关部分对齐。这说明了闭包的语法与函数的语法相似，除了使用了管道符号，以及部分语法是可选的。

```rust,ignore
fn  add_one_v1   (x: u32) -> u32 { x + 1 }
let add_one_v2 = |x: u32| -> u32 { x + 1 };
let add_one_v3 = |x|             { x + 1 };
let add_one_v4 = |x|               x + 1  ;
```

第一行显示了一个函数定义，第二行显示了一个带有完整注释的闭包定义。第三行中，我们删除了闭包定义中的类型注释。第四行中，我们删除了括号，因为闭包体只包含一个表达式，所以括号是可选的。这些都是有效的定义，在调用时会产生相同的行为。而`add_one_v3`和`add_one_v4`这两行则需要先评估闭包才能编译，因为类型是根据它们的使用来推断的。这与`let v = Vec::new();`的情况类似，后者需要要么加上类型注释，要么将某种类型的值插入到`Vec`中，才能让Rust能够推断出类型。

在闭包的定义中，编译器会为每个参数及其返回值推断出一个具体的类型。例如，列表13-3展示了这样一个简短闭包的定义：该闭包仅返回其接收的参数值。除了用于这个示例之外，这个闭包并没有什么实际用途。请注意，我们在定义中并没有添加任何类型注释。由于没有类型注释，我们可以使用任何类型来调用这个闭包，我们在这里第一次就尝试了 `String` 类型。如果我们尝试使用整数类型来调用 `example_closure`，则会引发错误。

<Listing number="13-3" file-name="src/main.rs" caption="Attempting to call a closure whose types are inferred with two different types">

```rust,ignore,does_not_compile
    let example_closure = |x| x;

    let s = example_closure(String::from("hello"));
    let n = example_closure(5);

```

</Listing>

编译器给出了这个错误：

```console
$ cargo run
   Compiling closure-example v0.1.0 (file:///projects/closure-example)
error[E0308]: mismatched types
 --> src/main.rs:5:29
  |
5 |     let n = example_closure(5);
  |             --------------- ^ expected `String`, found integer
  |             |
  |             arguments to this function are incorrect
  |
note: expected because the closure was earlier called with an argument of type `String`
 --> src/main.rs:4:29
  |
4 |     let s = example_closure(String::from("hello"));
  |             --------------- ^^^^^^^^^^^^^^^^^^^^^ expected because this argument is of type `String`
  |             |
  |             in this closure call
note: closure parameter defined here
 --> src/main.rs:2:28
  |
2 |     let example_closure = |x| x;
  |                            ^
help: try using a conversion method
  |
5 |     let n = example_closure(5.to_string());
  |                              ++++++++++++

For more information about this error, try `rustc --explain E0308`.
error: could not compile `closure-example` (bin "closure-example") due to 1 previous error

```

当我们第一次使用 `example_closure` 时，编译器会推断出 `x` 的类型，并且会确定闭包的返回类型为 `String`。这些类型随后会被锁定在 `example_closure` 中，因此当我们下次尝试使用相同闭包但不同类型的变量时，就会遇到类型错误。

### 捕获引用或转移所有权

闭包可以通过三种方式从其环境中捕获值，这三种方式直接对应于函数可以接受参数的三种方式：不可变地借用、可变地借用以及获取所有权。闭包会根据函数体对捕获值的处理方式来决定使用哪种方式。

在 Listing 13-4 中，我们定义了一个闭包，该闭包捕获了对名为 `list` 的向量的不可变引用，因为只需要一个不可变引用来打印该值即可。

<Listing number="13-4" file-name="src/main.rs" caption="Defining and calling a closure that captures an immutable reference">

```rust
fn main() {
    let list = vec![1, 2, 3];
    println!("Before defining closure: {list:?}");

    let only_borrows = || println!("From closure: {list:?}");

    println!("Before calling closure: {list:?}");
    only_borrows();
    println!("After calling closure: {list:?}");
}

```

</Listing>

这个例子还说明了，一个变量可以绑定到一个闭包的定义上，之后我们可以通过使用这个变量的名称以及括号来调用这个闭包，就像这个变量的名称本身是一个函数名称一样。

因为我们可以同时拥有多个对 `list` 的不可变引用，所以无论是在闭包定义之前、定义之后但在闭包被调用之前，还是在闭包被调用之后，都可以访问到`list`。这段代码可以编译、运行，并且会输出相应的结果。

```console
$ cargo run
   Compiling closure-example v0.1.0 (file:///projects/closure-example)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.43s
     Running `target/debug/closure-example`
Before defining closure: [1, 2, 3]
Before calling closure: [1, 2, 3]
From closure: [1, 2, 3]
After calling closure: [1, 2, 3]

```

接下来，在 Listing 13-5 中，我们修改了闭包的主体，使其能够在 `list` 向量中添加一个元素。现在，该闭包可以捕获一个可变引用。

<Listing number="13-5" file-name="src/main.rs" caption="Defining and calling a closure that captures a mutable reference">

```rust
fn main() {
    let mut list = vec![1, 2, 3];
    println!("Before defining closure: {list:?}");

    let mut borrows_mutably = || list.push(7);

    borrows_mutably();
    println!("After calling closure: {list:?}");
}

```

</Listing>

这段代码可以编译、运行，并且会输出以下内容：

```console
$ cargo run
   Compiling closure-example v0.1.0 (file:///projects/closure-example)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.43s
     Running `target/debug/closure-example`
Before defining closure: [1, 2, 3]
After calling closure: [1, 2, 3, 7]

```

请注意，在定义和调用 `borrows_mutably` 闭包之间，已经不再有 `println!` 了。当 `borrows_mutably` 被定义时，它实际上是对 `list` 的可变引用。在调用 `borrows_mutably` 闭包之后，我们不会再使用这个闭包，因此可变借用也随之结束。在闭包的定义和调用之间，不允许使用不可变的借用来进行打印操作，因为存在可变借用时，其他借用都是不允许的。试着在那里添加 `println!`，看看会收到什么错误信息！

如果您希望强制闭包在环境中拥有其所使用的数值的所有权，即使闭包的主体并不严格需要这种所有权，您可以在参数列表之前使用 `move` 这个关键字。

这种技术在将闭包传递给新线程以移动数据、使数据由新线程拥有时非常有用。我们将在第16章详细讨论线程以及为什么需要使用它们来处理并发问题。不过目前，让我们简要了解一下如何使用需要 `move` 关键字的闭包来创建新线程。列表13-6展示了经过修改的列表13-4，该代码在新建线程中而不是在主线程中打印向量。

<Listing number="13-6" file-name="src/main.rs" caption="Using `move` to force the closure for the thread to take ownership of `list`">

```rust
use std::thread;

fn main() {
    let list = vec![1, 2, 3];
    println!("Before defining closure: {list:?}");

    thread::spawn(move || println!("From thread: {list:?}"))
        .join()
        .unwrap();
}

```

</Listing>

我们创建一个新的线程，并将一个闭包作为参数传递给该线程。闭包体内会打印出列表。在 Listing 13-4 中，闭包仅使用不可变引用来捕获 `list`，因为这样对 `list` 的访问次数最少，从而能够正确地打印出列表。在这个例子中，尽管闭包体内仍然只需要不可变引用，但我们需要通过在闭包定义的开头加上 `move` 关键字来指定 `list` 应该被移入闭包中。如果主线程在调用 `join` 之前执行了更多的操作，那么新线程可能会在主线程完成之前完成，或者主线程可能会先完成。如果主线程仍然拥有 `list` 的所有权，但在新线程之前结束并丢弃 `list`，那么线程中的不可变引用就会变得无效。因此，编译器要求必须将 `list` 移入传递给新线程的闭包中，以确保引用仍然有效。尝试删除 `move` 关键字，或者在闭包定义之后在主线程中使用 `list`，看看会遇到哪些编译器错误！

<!-- Old headings. Do not remove or links may break. -->

<a id="storing-closures-using-generic-parameters-and-the-fn-traits"></a>
<a id="limitations-of-the-cacher-implementation"></a>
<a id="moving-captured-values-out-of-the-closure-and-the-fn-traits"></a>
<a id="moving-captured-values-out-of-closures-and-the-fn-traits"></a>

### 将捕获的值移出闭包

一旦一个闭包从定义它的环境中捕获了某个值的引用或所有权（从而影响了该值在闭包内部是否会被移动），那么闭包体内的代码就会决定当闭包被评估时，这些引用或值会发生什么变化（从而影响了这些值在闭包外部是否会被移动）。

闭包体可以执行以下操作之一：将捕获的值移出闭包，修改捕获的值，既不移出也不修改该值，或者根本不从环境中捕获任何值。

闭包如何捕获和处理来自环境的值，会影响闭包所实现的特性。而这些特性决定了函数和结构体可以使用何种类型的闭包。根据闭包体如何处理这些值，闭包会自动实现其中一个、两个或所有这三个特性，这种实现方式是累加式的。

* `FnOnce` 适用于可以调用一次的闭包。所有闭包至少实现了这一特性，因为所有闭包都可以被调用。如果一个闭包将捕获的值移出其作用域，那么它只实现 `FnOnce` 这一特性，而不实现其他 `Fn` 特性，因为它只能被调用一次。
* `FnMut` 适用于不会将捕获的值移出其作用域，但可能会改变捕获值的闭包。这样的闭包可以被多次调用。
* `Fn` 适用于既不会将捕获的值移出其作用域，也不会改变捕获值的闭包，以及那些从环境中捕获了零个值的闭包。这样的闭包可以在不被改变其环境的情况下被多次调用，这一点在需要同时多次调用闭包的情况下非常重要。

让我们看一下在清单13-1中使用的 `Option<T>` 上的 `unwrap_or_else` 方法的定义：

```rust,ignore
impl<T> Option<T> {
    pub fn unwrap_or_else<F>(self, f: F) -> T
    where
        F: FnOnce() -> T
    {
        match self {
            Some(x) => x,
            None => f(),
        }
    }
}
```

请记住，`T`是表示在`Some`变体中的值的通用类型。而类型`T`也是`unwrap_or_else`函数的返回类型。例如，在`Option<String>`上调用`unwrap_or_else`的函数，将会得到`String`的结果。

接下来，请注意`unwrap_or_else`函数还有一个额外的通用类型参数`F`。`F`类型是名为`f`的参数的类型，而`f`正是我们在调用`unwrap_or_else`时所提供的闭包。

在泛型类型 `F` 上指定的特征绑定是 `FnOnce() -> T`，这意味着 `F` 必须能够被调用一次，不接收任何参数，并且返回 `T`。在特征绑定中使用 `FnOnce` 是为了约束 `unwrap_or_else` 不会多次调用 `f`。在 `unwrap_or_else` 的主体中，我们可以看到如果 `Option` 是 `Some`，那么 `f` 就不会被调用。如果 `Option` 是 `None`，那么 `f` 将会被调用一次。因为所有的闭包都实现了 `FnOnce`，所以 `unwrap_or_else` 能够接受这三种类型的闭包，并且具有最大的灵活性。

注意：如果我们想要做的事情不需要从环境中获取某个值，我们可以使用函数的名称来代替闭包，这样我们就可以使用那些实现了 `Fn` 特征的函数。例如，对于一个 `Option<Vec<T>>` 类型的值，如果该值是 `None`，我们可以调用 `unwrap_or_else(Vec::new)` 来获取一个新的空向量。编译器会自动选择适用的 `Fn` 特征来定义函数。

现在让我们来看看标准库中的 `sort_by_key` 方法，该方法定义在切片上。我们来看看它与 `unwrap_or_else` 的区别，以及为什么 `sort_by_key` 使用 `FnMut` 而不是 `FnOnce` 作为特征绑定。这个闭包接收一个参数，该参数是对当前切片中元素的引用；它返回一个类型为 `K` 的值，这个值可以进行排序。当需要根据每个元素的特定属性对切片进行排序时，这个函数非常有用。在 Listing 13-7 中，我们有一个 `Rectangle` 实例的列表，我们使用 `sort_by_key` 来按照它们的 `width` 属性从低到高对它们进行排序。

<Listing number="13-7" file-name="src/main.rs" caption="Using `sort_by_key` to order rectangles by width">

```rust
#[derive(Debug)]
struct Rectangle {
    width: u32,
    height: u32,
}

fn main() {
    let mut list = [
        Rectangle { width: 10, height: 1 },
        Rectangle { width: 3, height: 5 },
        Rectangle { width: 7, height: 12 },
    ];

    list.sort_by_key(|r| r.width);
    println!("{list:#?}");
}

```

</Listing>

这段代码会输出：

```console
$ cargo run
   Compiling rectangles v0.1.0 (file:///projects/rectangles)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.41s
     Running `target/debug/rectangles`
[
    Rectangle {
        width: 3,
        height: 5,
    },
    Rectangle {
        width: 7,
        height: 12,
    },
    Rectangle {
        width: 10,
        height: 1,
    },
]

```

之所以将 `sort_by_key` 定义为需要 `FnMut` 的闭包，是因为它多次调用了该闭包——每次针对切片中的每个元素。而 `|r|
r.width` 闭包并不捕获、修改或移出其外部环境中的任何内容，因此它符合该特质的要求。

相比之下，列表13-8展示了一个仅实现了 `FnOnce` 特性的闭包示例，因为它会将值从环境中移出。编译器不允许我们将这个闭包与 `sort_by_key` 一起使用。

<Listing number="13-8" file-name="src/main.rs" caption="Attempting to use an `FnOnce` closure with `sort_by_key`">

```rust,ignore,does_not_compile
#[derive(Debug)]
struct Rectangle {
    width: u32,
    height: u32,
}

fn main() {
    let mut list = [
        Rectangle { width: 10, height: 1 },
        Rectangle { width: 3, height: 5 },
        Rectangle { width: 7, height: 12 },
    ];

    let mut sort_operations = vec![];
    let value = String::from("closure called");

    list.sort_by_key(|r| {
        sort_operations.push(value);
        r.width
    });
    println!("{list:#?}");
}

```

</Listing>

这是一种人为设计的、复杂的做法（实际上并不起作用），目的是统计在排序 `list` 时，`sort_by_key` 调用该闭包的次数。这段代码试图通过将 `value`——一个来自闭包环境的 `String`——放入 `sort_operations` 向量中来实现这一统计。闭包会捕获 `value`，然后通过将 `value` 的所有权转移给 `sort_operations` 向量，将 `value` 从闭包中移除。这个闭包只能被调用一次；如果尝试再次调用它，是行不通的，因为 `value` 将不再存在于环境中，无法再次被放入 `sort_operations` 中！因此，这个闭包只实现了 `FnOnce`。当我们尝试编译这段代码时，会遇到这样的错误：`value` 无法从闭包中移出，因为闭包必须实现 `FnMut`。

```console
$ cargo run
   Compiling rectangles v0.1.0 (file:///projects/rectangles)
error[E0507]: cannot move out of `value`, a captured variable in an `FnMut` closure
  --> src/main.rs:18:30
   |
15 |     let value = String::from("closure called");
   |         -----   ------------------------------ move occurs because `value` has type `String`, which does not implement the `Copy` trait
   |         |
   |         captured outer variable
16 |
17 |     list.sort_by_key(|r| {
   |                      --- captured by this `FnMut` closure
18 |         sort_operations.push(value);
   |                              ^^^^^ `value` is moved here
   |
help: consider cloning the value if the performance cost is acceptable
   |
18 |         sort_operations.push(value.clone());
   |                                   ++++++++

For more information about this error, try `rustc --explain E0507`.
error: could not compile `rectangles` (bin "rectangles") due to 1 previous error

```

该错误指向了闭包体内那个将 `value` 移出环境的位置。为了解决这个问题，我们需要修改闭包体内的代码，使其不会将值移出环境。在环境中保留一个计数器，并在闭包体内递增其值，是一种更直接的计数方法，可以统计闭包被调用的次数。列表 13-9 中的闭包能够正常工作，因为它只捕获对 `num_sort_operations` 计数器的可变引用，因此可以被调用多次。

<Listing number="13-9" file-name="src/main.rs" caption="Using an `FnMut` closure with `sort_by_key` is allowed.">

```rust
#[derive(Debug)]
struct Rectangle {
    width: u32,
    height: u32,
}

fn main() {
    let mut list = [
        Rectangle { width: 10, height: 1 },
        Rectangle { width: 3, height: 5 },
        Rectangle { width: 7, height: 12 },
    ];

    let mut num_sort_operations = 0;
    list.sort_by_key(|r| {
        num_sort_operations += 1;
        r.width
    });
    println!("{list:#?}, sorted in {num_sort_operations} operations");
}

```

</Listing>

在定义或使用需要闭包的函数或类型时，`Fn`特性非常重要。在下一节中，我们将讨论迭代器。许多迭代器方法会接受闭包参数，因此在后续的内容中请记住这些闭包相关的细节！

[unwrap-or-else]: ../std/option/enum.Option.html#method.unwrap_or_else
