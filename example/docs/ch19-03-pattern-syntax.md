## 模式语法

在本节中，我们将收集所有在模式中有效的语法，并讨论为什么以及何时需要使用每一种语法。

### 匹配字面量

如第6章所述，你可以直接对字面量进行模式匹配。以下代码提供了一些示例：

```rust
    let x = 1;

    match x {
        1 => println!("one"),
        2 => println!("two"),
        3 => println!("three"),
        _ => println!("anything"),
    }

```

这段代码会输出 `one`，因为 `x` 的值为 `1`。这种语法在您希望代码在接收到特定具体值时执行某种操作时非常有用。

### 匹配命名变量

命名变量是一种不可辩驳的模式，可以匹配任何值。我们在本书中多次使用了它们。然而，在 `match`、 `if let` 或 `while let` 表达式中使用命名变量时存在一个问题。因为每种这样的表达式都会创建一个新的作用域，所以在这些表达式内部作为模式声明的变量会与构造外部具有相同名称的变量产生冲突。正如所有变量的情况一样。在 Listing 19-11 中，我们声明了一个名为 `x` 的变量，其值为 `Some(5)`，同时还声明了一个名为 `y` 的变量，其值为 `10`。然后，我们在值 `x` 的基础上创建了一个 `match` 表达式。请观察匹配臂中的模式以及最后的 `println!`，试着在运行这段代码或继续阅读之前预测出这段代码会输出什么。

**清单 19-11:** *src/main.rs* — 一个 `match` 表达式，其中包含一个引入新变量的分支，该新变量会遮蔽现有的变量 `y`

```rust
    let x = Some(5);
    let y = 10;

    match x {
        Some(50) => println!("Got 50"),
        Some(y) => println!("Matched, y = {y}"),
        _ => println!("Default case, x = {x:?}"),
    }

    println!("at the end: x = {x:?}, y = {y}");

```

让我们来看看当 `match` 表达式运行时会发生什么。第一个匹配分支的模式与定义的 `x` 不匹配，因此代码会继续执行。

在第二个匹配表达式中，引入了一个新的变量 `y`，该变量可以匹配 `Some` 内部的值。由于我们处于 `match` 表达式内的新作用域中，因此这是一个新的 `y` 变量，而不是我们在开头用 `10` 声明的 `y` 变量。这个新的 `y` 绑定可以匹配 `Some` 内部的所有值，而 `x` 中正好有这样的值。因此，这个新的 `y` 绑定到 `Some` 在 `x` 中的内部值。那个值就是 `5`，所以该表达式会执行并输出 `Matched, y = 5`。

如果 `Some(5)` 的值实际上是 `None`，那么前两个实施例中的模式就不会匹配，因此该值会匹配到下划线。我们在下划线表达式中没有引入 `x` 变量，所以表达式中的 `x` 仍然是未被影子化的外部 `x`。在这种假设的情况下， `match` 将会打印出 `Default case,
x = None`。

当 `match` 表达式执行完毕后，它的作用域就结束了，同样地，内部 `y` 的作用域也结束了。最后一个 `println!` 会生成 `at the end: x = Some(5), y = 10`。

为了创建一个 `match` 表达式，用于比较 outer `x` 和 `y` 的值，而不是引入一个新的变量来遮蔽现有的 `y` 变量，我们需要使用条件性的 match guard。我们将在 [“使用 match guards 添加条件语句”](#adding-conditionals-with-match-guards)<!-- ignore --> 部分中讨论 match guards。

<!-- Old headings. Do not remove or links may break. -->
<a id="multiple-patterns"></a>

### 匹配多个模式

在 `match` 表达式中，你可以使用 `|` 语法来匹配多个模式，这就是 _或_ 运算符。例如，在以下代码中，我们将 `x` 的值与匹配条件进行比较，其中第一个匹配条件有一个 _或_ 选项，这意味着如果 `x` 的值与该条件中的任何一个值匹配，那么该条件的代码就会被执行。

```rust
    let x = 1;

    match x {
        1 | 2 => println!("one or two"),
        3 => println!("three"),
        _ => println!("anything"),
    }

```

这段代码会输出 `one or two`。

### 使用 `..=` 匹配数值范围

`..=`语法允许我们匹配一个包含多个值的范围。在以下代码中，当模式匹配到给定范围内的任何一个值时，相应的分支将会被执行：

```rust
    let x = 5;

    match x {
        1..=5 => println!("one through five"),
        _ => println!("something else"),
    }

```

如果 `x` 等于 `1`、 `2`、 `3`、 `4` 或 `5`，那么第一个分支将会匹配。这种语法比使用 `|` 运算符来表达相同的概念更为方便；如果我们使用 `|`，则必须指定 `1 | 2 |
3 | 4 | 5`。指定一个范围会大大简化代码，尤其是当我们想要匹配比如说在 1 到 1,000 之间的任何数字时！

编译器在编译时会检查该范围是否为空。由于Rust能够判断范围是否为空的类型只有 `char` 和数值类型，因此范围仅允许使用数值类型或 `char` 类型来定义。

以下是一个使用 `char` 值的示例：

```rust
    let x = 'c';

    match x {
        'a'..='j' => println!("early ASCII letter"),
        'k'..='z' => println!("late ASCII letter"),
        _ => println!("something else"),
    }

```

Rust能够识别 `'c'` 属于第一个模式的范围，并输出 `early
ASCII letter`。

### 解构赋值以拆分值

我们还可以使用模式来重构结构体、枚举类型和元组，以便使用这些值的不同部分。让我们逐一了解每种类型。

<!-- Old headings. Do not remove or links may break. -->

<a id="destructuring-structs"></a>

#### 结构体

清单19-12展示了一个 `Point` 结构体，它包含两个字段： `x` 和 `y`。我们可以使用带有 `let` 语句的模式来将这些字段分开。

**清单 19-12:** *src/main.rs* — 将结构的字段分解为独立的变量

```rust
struct Point {
    x: i32,
    y: i32,
}

fn main() {
    let p = Point { x: 0, y: 7 };

    let Point { x: a, y: b } = p;
    assert_eq!(0, a);
    assert_eq!(7, b);
}

```

这段代码创建了变量 `a` 和 `b`，它们分别匹配结构体 `p` 的 `x` 和 `y` 字段的值。这个例子表明，模式中变量的名称不必与结构体的字段名称完全匹配。不过，通常的做法是将变量名称与字段名称保持一致，这样更容易记住每个变量来自哪个字段。由于这种常见的用法，以及编写 `let Point { x: x, y: y } = p;` 时存在大量重复内容，Rust 为匹配结构体字段的模式提供了简写方式：只需列出结构体字段的名称，那么由该模式生成的变量就会具有相同的名称。列表 19-13 中的代码与列表 19-12 中的代码行为相同，但是 `let` 模式中生成的变量分别是 `x` 和 `y`，而不是 `a` 和 `b`。

**清单 19-13:** *src/main.rs* — 使用结构体字段简写法对结构体字段进行解构

```rust
struct Point {
    x: i32,
    y: i32,
}

fn main() {
    let p = Point { x: 0, y: 7 };

    let Point { x, y } = p;
    assert_eq!(0, x);
    assert_eq!(7, y);
}

```

这段代码创建了变量 `x` 和 `y`，它们分别与 `x` 和 `y` 字段相对应。最终，变量 `x` 和 `y` 会包含来自 `p` 结构体的值。

我们还可以使用字面值来重构结构体，而不是为所有字段创建单独的变量。这样做可以让我们在创建变量以重构其他字段的同时，对某些字段进行特定值的测试。

在 Listing 19-14 中，我们有一个 `match` 表达式，它将 `Point` 值分为三种情况：直接位于 `x` 轴上的点（当 `y = 0` 成立时）、位于 `y` 轴上的点（当 `x = 0` 成立时），以及既不位于任一轴上的点。

**列表 19-14:** *src/main.rs* — 使用同一模式进行字面值的解构和匹配

```rust
fn main() {
    let p = Point { x: 0, y: 7 };

    match p {
        Point { x, y: 0 } => println!("On the x axis at {x}"),
        Point { x: 0, y } => println!("On the y axis at {y}"),
        Point { x, y } => {
            println!("On neither axis: ({x}, {y})");
        }
    }
}

```

第一个分支会匹配任何位于 `x` 轴上的点，其实现方式是规定 `y` 域的值必须匹配字面值 `0`。这种模式仍然会创建一个 `x` 变量，我们可以在代码中使用这个变量来实现这个分支的功能。

同样，第二个分支通过指定以下条件来匹配 `y` 轴上的任意点：如果 `x` 字段的值满足 `0` 的条件，那么两个字段就匹配；同时，该分支还会为 `y` 字段的值创建一个变量 `y`。第三个分支没有指定任何具体的值，因此它可以匹配任何其他 `Point`，并为 `x` 和 `y` 字段分别创建变量。

在这个示例中，值 `p` 通过包含 `0` 而匹配到第二个分支，因此这段代码将输出 `On the y axis at 7`。

请注意，一个 `match` 表达式在找到第一个匹配的模式后就会停止检查其他模式。因此，即使 `Point { x: 0, y: 0 }` 位于 `x` 轴上，而 `y` 轴上，这段代码也只会输出 `On the x axis at 0`。

<!-- Old headings. Do not remove or links may break. -->

<a id="destructuring-enums"></a>

#### 枚举类型

在本书中，我们已经对枚举进行了解构处理（例如，第6章中的Listing 6-5），但还没有明确讨论解构枚举的模式与枚举中存储的数据定义方式之间的关系。例如，在Listing 19-15中，我们使用了来自Listing 6-2的 `Message` 枚举，并编写了 `match` 模式，以解构每个内部值。

**清单 19-15:** *src/main.rs* — 用于解构包含不同类型值的枚举变体

```rust
enum Message {
    Quit,
    Move { x: i32, y: i32 },
    Write(String),
    ChangeColor(i32, i32, i32),
}

fn main() {
    let msg = Message::ChangeColor(0, 160, 255);

    match msg {
        Message::Quit => {
            println!("The Quit variant has no data to destructure.");
        }
        Message::Move { x, y } => {
            println!("Move in the x direction {x} and in the y direction {y}");
        }
        Message::Write(text) => {
            println!("Text message: {text}");
        }
        Message::ChangeColor(r, g, b) => {
            println!("Change color to red {r}, green {g}, and blue {b}");
        }
    }
}

```

这段代码会打印出 `Change color to red 0, green 160, and blue 255`。尝试将 `msg` 的值进行更改，以观察其他分支的代码运行情况。

对于没有任何数据的枚举变体，比如 `Message::Quit`，我们无法进一步解构该值。我们只能匹配字面意义上的 `Message::Quit` 值，而且该模式中没有任何变量。

对于类似结构的枚举变体，例如 `Message::Move`，我们可以使用与指定用于匹配结构体的模式类似的模式。在变体名称之后，我们放置花括号，然后列出带有变量的字段，这样就能将各个部分分离出来，以便在代码中使用。这里我们使用与 Listing 19-13 中相同的简写形式。

对于类似元组的枚举变体，比如 `Message::Write` 表示包含一个元素的元组，而 `Message::ChangeColor` 表示包含一个元素的元组，其模式与我们用来匹配元组的模式类似。模式中的变量数量必须与我们正在匹配的变体中的元素数量相匹配。

<!-- Old headings. Do not remove or links may break. -->

<a id="destructuring-nested-structs-and-enums"></a>

#### 嵌套结构体与枚举类型

到目前为止，我们的示例都只匹配了一层深度的结构体或枚举类型，但实际上，匹配功能也可以应用于嵌套项！例如，我们可以将 Listing 19-15 中的代码重构，以支持 `ChangeColor` 消息中的 RGB 和 HSV 颜色，如 Listing 19-16 所示。

<Listing number="19-16" caption="Matching on nested enums">

```rust
enum Color {
    Rgb(i32, i32, i32),
    Hsv(i32, i32, i32),
}

enum Message {
    Quit,
    Move { x: i32, y: i32 },
    Write(String),
    ChangeColor(Color),
}

fn main() {
    let msg = Message::ChangeColor(Color::Hsv(0, 160, 255));

    match msg {
        Message::ChangeColor(Color::Rgb(r, g, b)) => {
            println!("Change color to red {r}, green {g}, and blue {b}");
        }
        Message::ChangeColor(Color::Hsv(h, s, v)) => {
            println!("Change color to hue {h}, saturation {s}, value {v}");
        }
        _ => (),
    }
}

```

</Listing>

在 `match` 表达式中，第一个分支的模式匹配了一个包含 `Color::Rgb` 变体的 `Message::ChangeColor` 枚举变体；然后，该模式绑定到三个内部的 `i32` 值上。第二个分支的模式也匹配了一个 `Message::ChangeColor` 枚举变体，但内部的枚举变体匹配的是 `Color::Hsv`。我们可以在一个 `match` 表达式中指定这些复杂的条件，尽管这里涉及到了两个枚举类型。

<!-- Old headings. Do not remove or links may break. -->

<a id="destructuring-structs-and-tuples"></a>

#### 结构体与元组

我们可以以更复杂的方式混合、匹配和嵌套解构模式。
下面的例子展示了一个复杂的解构过程，其中我们在一个元组内部嵌套结构体，并从该元组中解构所有基本值。

```rust
    let ((feet, inches), Point { x, y }) = ((3, 10), Point { x: 3, y: -10 });

```

这段代码可以将复杂类型分解为其组成部分，这样我们就可以分别使用我们感兴趣的值。

使用模式进行解构是一种方便的方式，可以将结构体中的各个字段的值分别使用。

### 忽略模式中的值

您已经注意到，有时候忽略模式中的某些值是有用的。例如，在 `match` 的最后一个分支中，使用这种方法来得到一个“通用”的值，这个值实际上并不执行任何操作，但能够涵盖所有剩余的可能值。有几种方法可以忽略模式中的整个值或部分值：使用 `_` 模式（您已经见过这种方式）；在另一个模式中使用 `_` 模式；使用以下划线开头的名称；或者使用 `..` 来忽略值的剩余部分。让我们来探讨一下如何以及为什么使用这些模式。

<!-- Old headings. Do not remove or links may break. -->

<a id="ignoring-an-entire-value-with-_"></a>

#### 一个完整的数值，带有 `_`

我们使用了下划线作为通配符模式，它可以匹配任何值，但不会绑定到该值。这在 `match` 表达式的最后一个分支中特别有用，但我们也可以在任何模式中使用它，包括函数参数，如清单19-17所示。

**清单 19-17:** *src/main.rs* — 在函数签名中使用 `_`

```rust
fn foo(_: i32, y: i32) {
    println!("This code only uses the y parameter: {y}");
}

fn main() {
    foo(3, 4);
}

```

这段代码将完全忽略作为第一个参数的 `3` 的值，而会打印出 `This code only uses the y parameter: 4`。

在大多数情况下，当你不再需要某个特定的函数参数时，你应该修改函数的签名，使其不包含未使用的参数。在以下情况下，忽略函数参数尤其有用：例如，当你在实现某个特质时，需要特定的类型签名，但实现中的函数体并不需要其中一个参数。这样，你就可以避免编译器发出关于未使用函数参数的警告，因为使用名称的话，就会遇到这样的警告。

<!-- Old headings. Do not remove or links may break. -->

<a id="ignoring-parts-of-a-value-with-a-nested-_"></a>

#### 具有嵌套结构的 Value 的各个部分 `_`

我们还可以使用 `_` 在另一个模式中忽略某个值的一部分。例如，当我们只想测试某个值的一部分，而在相应的代码中不需要使用其他部分时，就可以使用这种方式。清单19-18展示了负责管理某个设置值的代码。业务需求是，用户不应该能够覆盖某个设置的现有自定义值，但如果设置当前是未设置的，用户可以取消设置并为其指定一个值。

<Listing number="19-18" caption="Using an underscore within patterns that match `Some` variants when we don’t need to use the value inside the `Some`">

```rust
    let mut setting_value = Some(5);
    let new_setting_value = Some(10);

    match (setting_value, new_setting_value) {
        (Some(_), Some(_)) => {
            println!("Can't overwrite an existing customized value");
        }
        _ => {
            setting_value = new_setting_value;
        }
    }

    println!("setting is {setting_value:?}");

```

</Listing>

这段代码会先打印出 `Can't overwrite an existing customized value`，然后打印出 `setting is Some(5)`。在第一个匹配分支中，我们不需要匹配或使用 `Some` 变体中的值，但是我们需要测试当 `setting_value` 和 `new_setting_value` 都是 `Some` 变体的情况。在这种情况下，我们会打印出不更改 `setting_value` 的原因，而 `setting_value` 实际上不会被更改。

在所有其他情况下（如果 `setting_value` 或 `new_setting_value` 是 `None`），
由第二个分支中的 `_` 模式所表达的，我们希望允许 `new_setting_value` 变成 `setting_value`。

我们还可以在一个模式中多次使用下划线来忽略特定的值。清单19-19展示了一个例子，展示了如何在一个包含五个元素的元组中忽略第二个和第四个元素。

<Listing number="19-19" caption="Ignoring multiple parts of a tuple">

```rust
    let numbers = (2, 4, 8, 16, 32);

    match numbers {
        (first, _, third, _, fifth) => {
            println!("Some numbers: {first}, {third}, {fifth}");
        }
    }

```

</Listing>

这段代码将输出 `Some numbers: 2, 8, 32`，而 `4` 和 `16` 的值将被忽略。

<!-- Old headings. Do not remove or links may break. -->

<a id="ignoring-an-unused-variable-by-starting-its-name-with-_"></a>

#### 一个未使用的变量，其名称以 `_` 开头

如果你创建了一个变量，但并没有在任何地方使用它，Rust通常会发出警告，因为未使用的变量可能会成为错误。然而，在某些情况下，能够创建一些暂时不会使用的变量是有用的，比如在进行原型设计或刚开始项目的时候。在这种情况下，你可以通过在变量名前加上下划线来告诉Rust不要对未使用的变量发出警告。在 Listing 19-20 中，我们创建了两个未使用的变量，但在编译代码时，我们只会对其中一个变量收到警告。

**清单 19-20:** *src/main.rs* — 使用下划线开头来命名变量，以避免产生未使用的变量警告

```rust
fn main() {
    let _x = 5;
    let y = 10;
}

```

在这里，我们收到了一个关于未使用变量 `y` 的警告，但是并没有收到关于未使用变量 `_x` 的警告。

请注意，使用仅 `_` 与使用以下划线开头的名称之间存在细微差别。语法 `_x` 仍然会将值绑定到变量上，而 `_` 则根本不会进行绑定操作。为了说明这种区别的重要性，清单 19-21 将展示一个错误示例。

<Listing number="19-21" caption="An unused variable starting with an underscore still binds the value, which might take ownership of the value.">

```rust,ignore,does_not_compile
    let s = Some(String::from("Hello!"));

    if let Some(_s) = s {
        println!("found a string");
    }

    println!("{s:?}");

```

</Listing>

我们会收到一个错误，因为 `s` 的值仍然会被移动到 `_s` 中，这导致我们无法再次使用 `s`。然而，仅仅使用下划线本身并不会与值绑定。列表 19-22 将会正常编译，因为 `s` 不会被移动到 `_` 中。

<Listing number="19-22" caption="Using an underscore does not bind the value.">

```rust
    let s = Some(String::from("Hello!"));

    if let Some(_) = s {
        println!("found a string");
    }

    println!("{s:?}");

```

</Listing>

这段代码的运行效果很好，因为我们根本没有将 `s` 绑定到任何东西上；它并没有被移动。

<a id="ignoring-remaining-parts-of-a-value-with-"></a>

#### 使用 `..` 表示值的剩余部分

在处理包含多个部分的数值时，我们可以使用 `..` 语法来指定特定的部分，而忽略其余部分。这样就不必为每个被忽略的值列出下划线。 `..` 模式会忽略那些我们没有在模式的其他部分中明确匹配到的数值部分。在 Listing 19-23 中，我们有一个 `Point` 结构体，它存储了三维空间中的坐标。在 `match` 表达式中，我们只想对 `x` 坐标进行操作，而忽略 `y` 和 `z` 字段中的数值。

<Listing number="19-23" caption="Ignoring all fields of a `Point` except for `x` by using `..`">

```rust
    struct Point {
        x: i32,
        y: i32,
        z: i32,
    }

    let origin = Point { x: 0, y: 0, z: 0 };

    match origin {
        Point { x, .. } => println!("x is {x}"),
    }

```

</Listing>

我们先列出 `x` 的值，然后再包含 `..` 的模式。这样比需要列出 `y: _` 和 `z: _` 要快得多，尤其是在处理具有许多字段的结构体时，此时只有一两个字段是相关的。

语法 `..` 会根据需要生成尽可能多的值。清单 19-24 展示了如何使用带有元组的 `..`。

**列表 19-24:** *src/main.rs* — 仅匹配元组中的第一个和最后一个值，忽略所有其他值

```rust
fn main() {
    let numbers = (2, 4, 8, 16, 32);

    match numbers {
        (first, .., last) => {
            println!("Some numbers: {first}, {last}");
        }
    }
}

```

在这段代码中，第一个值和最后一个值分别被匹配为 `first` 和 `last`。而 `..` 则会匹配并忽略中间的所有内容。

然而，使用 `..` 时必须明确无误。如果不清楚哪些值应该用于匹配，哪些值应该被忽略，Rust 会报错。清单 19-25 展示了一个使用 `..` 造成歧义的例子，因此该代码将无法编译。

**清单 19-25:** *src/main.rs* — 试图以模糊的方式使用 `..`

```rust,ignore,does_not_compile
fn main() {
    let numbers = (2, 4, 8, 16, 32);

    match numbers {
        (.., second, ..) => {
            println!("Some numbers: {second}")
        },
    }
}

```

当我们编译这个示例时，出现了以下错误：

```console
$ cargo run
   Compiling patterns v0.1.0 (file:///projects/patterns)
error: `..` can only be used once per tuple pattern
 --> src/main.rs:5:22
  |
5 |         (.., second, ..) => {
  |          --          ^^ can only be used once per tuple pattern
  |          |
  |          previously used here

error: could not compile `patterns` (bin "patterns") due to 1 previous error

```

Rust无法确定在匹配到 `second` 之前应该忽略元组中的多少个值，以及之后还应该忽略多少个值。这段代码可能意味着我们想要忽略 `2`，将 `second` 绑定到 `4`，然后忽略 `8`、 `16` 和 `32`；或者我们想要忽略 `2` 和 `4`，将 `second` 绑定到 `8`，然后忽略 `16` 和 `32`；以此类推。在Rust中，变量名 `second` 并没有特殊含义，因此我们会遇到编译错误，因为像这样在两个地方使用 `..` 会导致歧义。

<!-- Old headings. Do not remove or links may break. -->

<a id="extra-conditionals-with-match-guards"></a>

### 使用 Match Guards 添加条件语句

匹配守卫是一种额外的 `if` 条件，它位于模式之后的 `match` 分支中，该条件必须得到满足，才能选择该分支。匹配守卫适用于表达比单纯模式所能实现的更复杂的逻辑。不过需要注意的是，它们仅适用于 `match` 表达式，不适用于 `if let` 或 `while let` 表达式。

该条件可以使用在模式中创建的变量。列表19-26展示了一个`match`，其中第一个分支使用了模式 `Some(x)`，并且还有一个匹配守卫 `if x % 2 == 0`（如果数字是偶数，这个守卫将会变成 `true`）。

<Listing number="19-26" caption="Adding a match guard to a pattern">

```rust
    let num = Some(4);

    match num {
        Some(x) if x % 2 == 0 => println!("The number {x} is even"),
        Some(x) => println!("The number {x} is odd"),
        None => (),
    }

```

</Listing>

这个示例将输出 `The number 4 is even`。当 `num` 与第一个分支中的模式进行比较时，它匹配了，因为 `Some(4)` 与 `Some(x)` 匹配。然后，匹配守卫会检查 `x` 除以 2 的余数是否等于 0，由于余数等于 0，因此第一个分支会被选中。

如果原本应该是 `Some(5)` 而不是 `num`，那么第一个分支中的匹配保护就会变成 `false`，因为 5 除以 2 的余数是 1，而 1 并不等于 0。在这种情况下，Rust 会执行第二个分支，因为第二个分支没有匹配保护，因此会匹配任何 `Some` 类型的变量。

在模式内无法表达 `if x % 2 == 0` 这个条件，因此，匹配保护机制为我们提供了表达这种逻辑的能力。这种额外表达能力的缺点是，当涉及到匹配保护表达式时，编译器不会尝试检查其穷尽性。

在讨论清单19-11时，我们提到可以使用匹配守卫来解决模式遮蔽问题。回想一下，我们在 `match` 表达式中的模式内部创建了一个新变量，而不是使用 `match` 外部的变量。这个新变量意味着我们无法测试外部变量的值。清单19-27展示了如何使用匹配守卫来解决这个问题。

**清单 19-27:** *src/main.rs* — 使用 match guard 来测试与外部变量的相等性

```rust
fn main() {
    let x = Some(5);
    let y = 10;

    match x {
        Some(50) => println!("Got 50"),
        Some(n) if n == y => println!("Matched, n = {n}"),
        _ => println!("Default case, x = {x:?}"),
    }

    println!("at the end: x = {x:?}, y = {y}");
}

```

这段代码现在会打印出 `Default case, x = Some(5)`。在第二个 match 分支中的模式并没有引入一个新的变量 `y`，这样就不会遮蔽外部变量 `y`，因此我们可以在 match guard 中使用外部变量 `y`。我们没有使用 `Some(y)` 来指定模式，因为那样会遮蔽外部变量 `y`，而是选择了 `Some(n)`。这样就会创建一个新的变量 `n`，这个变量不会遮蔽任何东西，因为在外层 `match` 之外并没有 `n` 变量。

匹配守卫 `if n == y` 并不是一个模式，因此不会引入新的变量。这个 `y` _实际上是_ 外部 `y` 的一部分，而不是一个新的 `y` 来遮蔽它。我们可以通过比较 `n` 和 `y`，来寻找一个与外部 `y` 具有相同值的变量。

你也可以在匹配守卫中使用 _or_ 运算符 `|` 来指定多个模式；此时，匹配守卫的条件将适用于所有模式。列表 19-28 展示了在组合使用 `|` 模式的匹配守卫时的优先级。这个例子的重要之处在于，尽管看起来 `if y` 匹配守卫只适用于 `4`，但实际上它适用于 `5`、_以及 `6`，而 `if y` 则只适用于 `6`。

<Listing number="19-28" caption="Combining multiple patterns with a match guard">

```rust
    let x = 4;
    let y = false;

    match x {
        4 | 5 | 6 if y => println!("yes"),
        _ => println!("no"),
    }

```

</Listing>

匹配条件规定，只有当 `x` 的值等于 `4`、`5` 或 `6` 时，才匹配到 `y`。当这段代码运行时，第一个臂的模式匹配成功，因为 `x` 等于 `4`，但匹配保护 `if y` 的值为 `false`，因此第一个臂没有被选中。代码接着进入第二个臂，这个臂确实匹配成功，于是程序会输出 `no`。原因是 `if` 条件适用于整个模式 `4 | 5 | 6`，而不仅仅是最后一个值 `6`。换句话说，匹配保护相对于模式的优先级就是这样决定的。

```text
(4 | 5 | 6) if y => ...
```

而不是这样：

```text
4 | 5 | (6 if y) => ...
```

运行代码后，优先级的行为非常明显：如果匹配守卫仅应用于使用`|`运算符指定的值列表中的最后一个值，那么匹配条件就会成立，程序就会输出`yes`。

<!-- Old headings. Do not remove or links may break. -->

<a id="-bindings"></a>

### 使用 `@` 绑定

`_at_ 运算符 `@` 允许我们创建一个变量，在测试该值的模式匹配时，该变量同时持有该值。在 Listing 19-29 中，我们想要测试一个 `Message::Hello` `id` 字段是否在 `3..=7` 的范围内。我们还想将该值绑定到变量 `id` 上，这样我们就可以在与该分支相关的代码中使用该值。

<Listing number="19-29" caption="Using `@` to bind to a value in a pattern while also testing it">

```rust
    enum Message {
        Hello { id: i32 },
    }

    let msg = Message::Hello { id: 5 };

    match msg {
        Message::Hello { id: id @ 3..=7 } => {
            println!("Found an id in range: {id}")
        }
        Message::Hello { id: 10..=12 } => {
            println!("Found an id in another range")
        }
        Message::Hello { id } => println!("Found some other id: {id}"),
    }

```

</Listing>

这个示例将打印出 `Found an id in range: 5`。通过在范围 `3..=7` 之前指定 `id @`，我们可以捕获与范围匹配的任何值，并将其存储在名为 `id` 的变量中，同时还会检查该值是否符合范围模式。

在第二个分支中，模式中只指定了一个范围，与这个分支相关联的代码并没有包含 `id` 字段的实际值的变量。`id` 字段的值可能是 10、11 或 12，但与该模式相关联的代码并不知道具体是哪一个值。模式代码无法使用 `id` 字段的值，因为我们并没有将 `id` 的值存储在一个变量中。

在最后一个分支中，我们定义了一个没有范围的变量，实际上，这个变量中存储了可以在该分支代码中使用的值，这个变量名为 `id`。之所以如此，是因为我们使用了结构字段的简写语法。不过，与前两个分支不同的是，我们没有对这个 `id` 字段中的值进行任何测试——任何值都能符合这种模式。

使用 `@` 可以让我们测试一个值，并将其保存在一个变量中，整个过程只需一个模式即可完成。

## 摘要

Rust中的模式在区分不同类型的数据方面非常有用。在 `match` 表达式中使用时，Rust确保你的模式能够覆盖所有可能的值，否则程序将无法编译。在 `let` 语句和函数参数中使用模式可以使这些构造更加有用，能够将值分解为更小的部分，并将这些部分分配给变量。我们可以创建简单或复杂的模式来满足我们的需求。

接下来，在本书的倒数第二章中，我们将探讨Rust各种特性的一些高级方面。