## 使用向量存储值列表

我们首先要探讨的收集类型是 `Vec<T>`，也被称为向量。向量允许你在单一数据结构中存储多个值，这些值在内存中会相邻排列。向量只能存储相同类型的值。当你有一个项目列表时，比如文件中的文本行或购物篮中的商品价格，使用向量会非常方便。

### 创建新的向量

要创建一个新的、空的向量，我们可以调用 `Vec::new` 函数，如清单 8-1 所示。

<Listing number="8-1" caption="Creating a new, empty vector to hold values of type `i32`">

```rust
    let v: Vec<i32> = Vec::new();

```

</Listing>

请注意，我们在这里添加了一个类型注解。由于我们没有向这个向量中插入任何值，Rust并不知道我们打算存储的是哪种类型的元素。这是一个重要的点。向量是使用泛型实现的；我们将在第十章中介绍如何将自己的类型与泛型一起使用。目前，只需知道标准库提供的 `Vec<T>` 类型可以存储任何类型的元素。当我们创建一个向量来保存特定类型的元素时，可以在尖括号内指定该类型。在 Listing 8-1 中，我们告诉 Rust， `v` 中的 `Vec<T>` 将存储 `i32` 类型的元素。

通常情况下，你会创建一个带有初始值的 `Vec<T>`，Rust 会自动推断出你想要存储的值的类型，因此很少需要手动指定这种类型注释。Rust 提供了方便的 `vec!` 宏，它可以创建一个新向量，用来存储你提供的数值。列表 8-2 创建了一个新的 `Vec<i32>`，它存储了 `1`、 `2` 和 `3` 这些数值。整数类型被设置为 `i32`，因为这是默认的整数类型，正如我们在第 3 章的 [“数据类型”][data-types]<!-- ignore --> 部分所讨论的那样。

<Listing number="8-2" caption="Creating a new vector containing values">

```rust
    let v = vec![1, 2, 3];

```

</Listing>

因为我们已经赋予了 `i32` 的初始值，所以 Rust 可以推断出 `v` 的类型就是 `Vec<i32>`，因此类型注释并不是必需的。接下来，我们将探讨如何修改向量。

### 更新向量

要创建一个向量，然后向其中添加元素，我们可以使用 `push` 方法，如清单 8-3 所示。

<Listing number="8-3" caption="Using the `push` method to add values to a vector">

```rust
    let mut v = Vec::new();

    v.push(5);
    v.push(6);
    v.push(7);
    v.push(8);

```

</Listing>

与任何变量一样，如果我们想要改变其值，就需要使用 `mut` 关键字来使其变为可变的，这一点在第三章中有详细讨论。我们放在其中的数字都是 `i32` 类型的，而 Rust 会根据数据自动推断出这一点，因此我们不需要 `Vec<i32>` 注释。

### 向量的读取元素

引用存储在向量中的值有两种方式：通过索引或使用 `get` 方法。在以下示例中，我们为这些函数返回的值的类型添加了注释，以便更清晰地理解。

列表8-4展示了两种访问向量中值的方法，包括索引语法以及 `get` 方法。

<Listing number="8-4" caption="Using indexing syntax and using the `get` method to access an item in a vector">

```rust
    let v = vec![1, 2, 3, 4, 5];

    let third: &i32 = &v[2];
    println!("The third element is {third}");

    let third: Option<&i32> = v.get(2);
    match third {
        Some(third) => println!("The third element is {third}"),
        None => println!("There is no third element."),
    }

```

</Listing>

请注意这里的几个细节。我们使用 `2` 的索引值来获取第三个元素，因为向量的索引是从零开始的。使用 `&` 和 `[]` 可以让我们引用索引值对应的元素。当我们使用 `get` 方法，并将索引作为参数传递时，我们得到一个 `Option<&T>`，然后我们可以用它来调用 `match`。

Rust提供了这两种方式来引用元素，这样你就可以选择当尝试使用超出现有元素范围的索引值时程序的行为。例如，让我们看看当有一个包含五个元素的向量时，分别使用这两种技术来访问索引为100的元素会发生什么，如清单8-5所示。

<Listing number="8-5" caption="Attempting to access the element at index 100 in a vector containing five elements">

```rust,should_panic,panics
    let v = vec![1, 2, 3, 4, 5];

    let does_not_exist = &v[100];
    let does_not_exist = v.get(100);

```

</Listing>

当我们运行这段代码时，第一个 `[]` 方法会导致程序崩溃，因为它引用了一个不存在的元素。这种方法最适合在希望程序在尝试访问向量末尾之外的元素时崩溃的情况下使用。

当`get`方法接收到超出向量范围的索引时，它会返回`None`，而不会引发恐慌。如果你在正常情况下偶尔需要访问超出向量范围的元素，就可以使用这种方法。此时，你的代码需要包含逻辑来处理这两种情况，如第6章所述。例如，这个索引可能是由用户输入的数字。如果他们不小心输入了一个过大的数字，导致程序得到`None`的值，你可以告诉用户当前向量中有多少个元素，并给他们另一个机会输入一个有效的数值。这样比因为输入错误而导致程序崩溃要更用户友好！

当程序拥有有效的引用时，借用检查器会执行所有权和借用规则（详见第4章），以确保该引用以及对该向量内容的任何其他引用都保持有效。请记住，同一作用域中不能同时存在可变引用和不可变引用这一规则。这一规则在清单8-6中得到了体现：我们持有一个对向量中第一个元素的不可变引用，并试图向向量的末尾添加元素。如果我们之后在函数中再次引用该元素，那么这个程序将无法正常运行。

<Listing number="8-6" caption="Attempting to add an element to a vector while holding a reference to an item">

```rust,ignore,does_not_compile
    let mut v = vec![1, 2, 3, 4, 5];

    let first = &v[0];

    v.push(6);

    println!("The first element is: {first}");

```

</Listing>

编译这段代码会导致以下错误：

```console
$ cargo run
   Compiling collections v0.1.0 (file:///projects/collections)
error[E0502]: cannot borrow `v` as mutable because it is also borrowed as immutable
 --> src/main.rs:6:5
  |
4 |     let first = &v[0];
  |                  - immutable borrow occurs here
5 |
6 |     v.push(6);
  |     ^^^^^^^^^ mutable borrow occurs here
7 |
8 |     println!("The first element is: {first}");
  |                                      ----- immutable borrow later used here

For more information about this error, try `rustc --explain E0502`.
error: could not compile `collections` (bin "collections") due to 1 previous error

```

清单8-6中的代码看起来应该可以正常运行：为什么对向量中第一个元素的引用需要关心向量末尾的变化呢？这个错误是由于向量的工作原理导致的：因为向量在内存中是将元素并排存放的，所以向向量末尾添加新元素时，可能需要分配新的内存，并将旧元素复制到新的内存空间中。如果当前存储向量的内存不足以容纳所有元素，那么对第一个元素的引用就会指向已释放的内存。而借用规则可以防止程序陷入这种状况。

注意：有关 `Vec<T>` 类型的实现细节，请参阅[《Rustonomicon》][nomicon]。

### 遍历向量中的值

要依次访问向量中的每个元素，我们需要遍历所有元素，而不是使用索引来逐一访问。清单8-7展示了如何使用`for`循环来获取向量中每个元素的不可变引用，并对其进行打印。

<Listing number="8-7" caption="Printing each element in a vector by iterating over the elements using a `for` loop">

```rust
    let v = vec![100, 32, 57];
    for i in &v {
        println!("{i}");
    }

```

</Listing>

我们还可以遍历可变向量中的每个元素的可变引用，以便对所有元素进行更改。清单8-8中的循环会将 `50` 添加到每个元素上。

<Listing number="8-8" caption="Iterating over mutable references to elements in a vector">

```rust
    let mut v = vec![100, 32, 57];
    for i in &mut v {
        *i += 50;
    }

```

</Listing>

要更改可变引用所指向的值，我们必须使用`*`去解除引用操作，才能访问`i`中的值，然后再使用`+=`操作符。我们将在第十五章的[“解除对值的引用”][deref]<!-- ignore -->部分详细讨论解除引用操作。

在向量上进行迭代时，无论是不可变还是可变的向量，都是安全的，因为存在借用检查器的规则。如果我们尝试在 Listing 8-7 和 Listing 8-8 中的循环体插入或删除元素，将会出现类似于 Listing 8-6 中代码所出现的编译器错误。循环体所引用的向量可以防止对整个向量同时进行修改。

### 使用枚举类型存储多种类型的数据

向量只能存储相同类型的值。这可能会带来不便；当然也有需要存储不同类型元素的列表的情况。幸运的是，枚举的变体是在相同的枚举类型下定义的，因此当我们需要一种类型来表示不同类型的数据时，我们可以定义并使用枚举！

例如，假设我们想要从电子表格中的某一行获取数据，该行中的某些列包含整数、浮点数以及字符串。我们可以定义一个枚举类型，其各个变体分别存储不同的数据类型，而所有枚举变体都被视为同一种类型。然后，我们可以创建一个向量来保存这个枚举类型，从而最终能够存储多种不同类型的数据。我们在清单8-9中展示了这一做法。

<Listing number="8-9" caption="Defining an enum to store values of different types in one vector">

```rust
    enum SpreadsheetCell {
        Int(i32),
        Float(f64),
        Text(String),
    }

    let row = vec![
        SpreadsheetCell::Int(3),
        SpreadsheetCell::Text(String::from("blue")),
        SpreadsheetCell::Float(10.12),
    ];

```

</Listing>

Rust需要在编译时知道向量中将会包含哪些类型，这样它就能准确知道存储每个元素所需的堆内存大小。我们还必须明确说明这个向量允许包含哪些类型。如果Rust允许向量存储任何类型，那么其中一种或多种类型可能会导致对向量元素进行操作时出现错误。使用枚举加上`match`表达式意味着Rust会在编译时确保处理每一种可能的情况，正如第6章所讨论的那样。

如果你不知道程序在运行时会获得哪些类型来存储在向量中，那么枚举技术将无法使用。相反，你可以使用一个特质对象，我们将在第18章中介绍这一点。

既然我们已经讨论了一些使用向量的最常见方法，请务必查阅[API文档][vec-api]<!-- ignore -->，了解标准库中定义的所有有用方法。例如，除了 `push` 之外，还有一个 `pop` 方法可以移除并返回最后一个元素。

### 删除一个向量会同时删除其所有元素

像其他 `struct` 一样，当向量离开其作用域时，它也会被释放，如清单 8-10 所示。

<Listing number="8-10" caption="Showing where the vector and its elements are dropped">

```rust
    {
        let v = vec![1, 2, 3, 4];

        // do stuff with v
    } // <- v goes out of scope and is freed here

```

</Listing>

当向量被丢弃时，其所有内容也会一同被清除，这意味着它所持有的整数数据也会被释放。借用检查器会确保，对向量内容的任何引用仅在向量本身仍然有效的情况下才被使用。

接下来，让我们来看看下一个集合类型： `String`!

[data-types]: ch03-02-data-types.html#data-types
[nomicon]: ../nomicon/vec/vec.html
[vec-api]: ../std/vec/struct.Vec.html
[deref]: ch15-02-deref.html#following-the-pointer-to-the-value-with-the-dereference-operator
