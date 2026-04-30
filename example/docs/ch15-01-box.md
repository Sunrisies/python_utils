## 使用 `Box<T>` 来指向堆上的数据

最基础的智能指针就是“盒子”，其类型表示为`Box<T>`。这种“盒子”可以让你将数据存储在堆上，而不是栈上。存储在栈上的只是指向堆数据的指针。关于栈和堆之间的区别，可以参考第4章。

盒子除了将数据存储在堆上而不是栈上之外，并没有额外的性能开销。不过，它们也没有太多额外的功能。你最有可能在以下情况下使用它们：

- 当某个类型的尺寸在编译时无法确定时，你希望在需要精确尺寸的上下文中使用该类型的值。
- 当你有大量数据，并且希望转移数据的所有权，但同时又希望确保数据在转移过程中不会被复制时。
- 当你希望拥有某个值，并且你只关心该值是实现了某个特定 trait 的类型，而不是该值的具体类型时。

我们将在[“使用盒子实现递归类型”](#enabling-recursive-types-with-boxes)中演示第一种情况。在第二种情况下，由于数据在栈上被多次复制，因此转移大量数据的所有权可能需要很长时间。为了提高性能，我们可以将大量数据存储在堆中的盒子里。这样，只有少量的指针数据会在栈上被复制，而它引用的数据则保持在一个位置上的堆中。第三种情况被称为“特质对象”，第18章中的[“使用特质对象来抽象共享行为”][trait-objects]⊂PH1⊁专门讨论了这一主题。所以，你在这里学到的知识可以在那一部分中再次应用！

<!-- Old headings. Do not remove or links may break. -->

<a id="using-boxt-to-store-data-on-the-heap"></a>

### 在堆上存储数据

在讨论 `Box<T>` 的堆存储用例之前，我们将先介绍其语法以及如何与存储在 `Box<T>` 中的值进行交互。

列表15-1展示了如何使用一个盒子在堆上存储一个 `i32` 值。

<Listing number="15-1" file-name="src/main.rs" caption="Storing an `i32` value on the heap using a box">

```rust
fn main() {
    let b = Box::new(5);
    println!("b = {b}");
}

```

</Listing>

我们定义变量 `b` 的值为 `Box` 所指向的 `5` 的值，该值存储在堆上。这个程序会打印出 `b = 5`；在这种情况下，我们可以像访问存储在栈上的数据一样访问存储在堆上的数据。就像任何被占用的数据一样，当盒子超出作用域时，比如在 `main` 的末尾，该盒子及其所指向的数据都会被释放。释放操作既适用于存储在栈上的盒子，也适用于存储在堆上的数据。

在堆上放置单个值并没有太大用处，因此你通常不会以这种方式使用盒子本身。在大多数情况下，将像 `i32` 这样的值存储在栈上更为合适。让我们来看一个例子，在这个例子中，盒子可以帮助我们定义一些类型，而这些类型如果没有盒子是无法定义的。

### 使用装箱实现递归类型

递归类型的某个值可以包含另一个相同类型的值作为其一部分。递归类型存在一个问题，因为Rust需要在编译时知道一个类型所占用的空间大小。然而，递归类型的值的嵌套理论上可以无限进行下去，因此Rust无法知道该值究竟需要多大的空间。由于盒子具有已知的大小，我们可以通过在递归类型定义中插入一个盒子来启用递归类型。

作为递归类型的例子，让我们来探讨一下`cons`列表类型。这是一种在函数式编程语言中常见的数据类型。我们定义的`cons`列表类型在结构上非常简单，唯一的难点在于递归部分；因此，我们在示例中使用的概念，在应对更复杂的递归类型问题时会非常有用。

<!-- Old headings. Do not remove or links may break. -->

<a id="more-information-about-the-cons-list"></a>

#### 理解Cons列表

`cons列表`是一种源自Lisp编程语言及其变体的数据结构，由嵌套的对组成，实际上是Lisp版本的链表。其名称来源于Lisp中的``cons``函数（即`construct函数`），该函数用两个参数创建一个新的对。通过对由一个值和一个对组成的对调用``cons``函数，我们可以构建由递归对构成的`cons列表`。

例如，以下是一个包含该列表的合集列表的伪代码表示形式，其中每对括号内的内容如下：

```text
(1, (2, (3, Nil)))
```

cons列表中的每个元素包含两个元素：当前元素的值以及下一个元素的值。列表中的最后一个元素仅包含一个名为`Nil`的值，且不包含下一个元素。cons列表是通过递归调用`cons`函数生成的。表示递归基础情况的规范名称是`Nil`。需要注意的是，这与第6章中讨论的“null”或“nil”概念不同，因为“null”或“nil”指的是无效或缺失的值。

在Rust中，cons列表并不是一种常用的数据结构。大多数情况下，当你需要处理一个项目列表时，使用 `Vec<T>` 是一个更好的选择。其他更复杂的递归数据类型在各种情况下确实很有用，但通过在本章中先介绍cons列表，我们可以探讨如何在不引入太多干扰的情况下定义递归数据类型。

列表15-2中定义了一个用于cons列表的枚举类型。请注意，这段代码目前无法编译，因为`List`这种类型的大小是未知的，我们将在后续内容中展示如何解决这个问题。

<Listing number="15-2" file-name="src/main.rs" caption="The first attempt at defining an enum to represent a cons list data structure of `i32` values">

```rust,ignore,does_not_compile
enum List {
    Cons(i32, List),
    Nil,
}

```

</Listing>

注意：为了这个示例的目的，我们实现了一个cons列表，该列表仅包含`i32`类型的值。我们可以使用泛型来实现它，正如我们在第10章中讨论的那样，这样可以定义一个能够存储任何类型值的cons列表类型。

使用 `List` 类型来存储列表 `1, 2, 3` 的代码如下所示：
清单 15-3.

<Listing number="15-3" file-name="src/main.rs" caption="Using the `List` enum to store the list `1, 2, 3`">

```rust,ignore,does_not_compile
// --snip--

use crate::List::{Cons, Nil};

fn main() {
    let list = Cons(1, Cons(2, Cons(3, Nil)));
}

```

</Listing>

第一个值 `Cons` 对应 `1`，另一个值 `List` 对应 `List`。这个 `List` 值又是另一个 `Cons` 值，而 `Cons` 值又对应 `2`，再有一个 `List` 值。这个 `List` 值又是一个 `List` 值，而 `List` 值又对应 `Cons` 值， `Cons` 值又对应 `3` 和一个 `List` 值。最终，这个 `List` 值就是 `Nil`，即那个非递归的变体，它标志着列表的结束。

如果我们尝试编译清单15-3中的代码，将会出现清单15-4中所示的错误。

<Listing number="15-4" caption="The error we get when attempting to define a recursive enum">

```console
$ cargo run
   Compiling cons-list v0.1.0 (file:///projects/cons-list)
error[E0072]: recursive type `List` has infinite size
 --> src/main.rs:1:1
  |
1 | enum List {
  | ^^^^^^^^^
2 |     Cons(i32, List),
  |               ---- recursive without indirection
  |
help: insert some indirection (e.g., a `Box`, `Rc`, or `&`) to break the cycle
  |
2 |     Cons(i32, Box<List>),
  |               ++++    +

error[E0391]: cycle detected when computing when `List` needs drop
 --> src/main.rs:1:1
  |
1 | enum List {
  | ^^^^^^^^^
  |
  = note: ...which immediately requires computing when `List` needs drop again
  = note: cycle used when computing whether `List` needs drop
  = note: see https://rustc-dev-guide.rust-lang.org/overview.html#queries and https://rustc-dev-guide.rust-lang.org/query.html for more information

Some errors have detailed explanations: E0072, E0391.
For more information about an error, try `rustc --explain E0072`.
error: could not compile `cons-list` (bin "cons-list") due to 2 previous errors

```

</Listing>

这个错误提示“该类型具有无限大小”。原因是我们定义了一个递归的`List`类型，它直接存储了自身的值。因此，Rust无法确定存储一个`List`类型的值需要多少空间。让我们来分析一下为什么会遇到这个错误。首先，我们来看看Rust是如何决定存储非递归类型的值需要多少空间的。

#### 计算非递归类型的尺寸

请回想一下我们在第6章讨论枚举定义时，在清单6-2中定义的`Message`枚举。

```rust
enum Message {
    Quit,
    Move { x: i32, y: i32 },
    Write(String),
    ChangeColor(i32, i32, i32),
}

```

为了确定为 `Message` 值分配多少空间，Rust会逐一检查每种变体，以确定哪种变体需要最多的空间。Rust发现 `Message::Quit` 不需要任何空间，而 `Message::Move` 需要足够的空间来存储两个 `i32` 值，以此类推。由于只会使用一种变体，因此 `Message` 值所需的最大空间就是存储其最大变体所需的空间。

与Rust在尝试确定像清单15-2中的`List`枚举这样的递归类型需要多少空间时的情况相比，可以这样理解：编译器首先查看`Cons`变体，该变体包含一个类型为`i32`的值以及一个类型为`List`的值。因此，`Cons`需要的内存空间等于一个`i32`的大小加上一个`List`的大小。为了计算出`List`类型需要多少内存，编译器会依次检查各个变体，从`Cons`开始。`Cons`变体包含一个类型为`i32`的值以及一个类型为`List`的值，这个过程会无限进行下去，如图15-1所示。

<img alt="An infinite Cons list: a rectangle labeled 'Cons' split into two smaller rectangles. The first smaller rectangle holds the label 'i32', and the second smaller rectangle holds the label 'Cons' and a smaller version of the outer 'Cons' rectangle. The 'Cons' rectangles continue to hold smaller and smaller versions of themselves until the smallest comfortably sized rectangle holds an infinity symbol, indicating that this repetition goes on forever." src="img/trpl15-01.svg" class="center" style="width: 50%;" />

图15-1：一个由无限多个 `Cons` 变体组成的无限集合 `List`

<!-- Old headings. Do not remove or links may break. -->

<a id="using-boxt-to-get-a-recursive-type-with-a-known-size"></a>

#### 获取已知大小的递归类型

因为Rust无法确定如何为递归定义的类型分配空间，编译器会给出这个有用的建议，并引发错误：

<!-- manual-regeneration
after doing automatic regeneration, look at listings/ch15-smart-pointers/listing-15-03/output.txt and copy the relevant line
-->

```text
help: insert some indirection (e.g., a `Box`, `Rc`, or `&`) to break the cycle
  |
2 |     Cons(i32, Box<List>),
  |               ++++    +
```

在这个建议中，_间接访问_指的是不要直接存储一个值，而是改变数据结构，通过存储指向该值的指针来间接存储该值。

因为`Box<T>`是一个指针，所以Rust总是知道`Box<T>`需要多少空间：指针的大小不会随着它所指向的数据量而改变。这意味着我们可以将`Box<T>`放在`Cons`变体中，而不是直接放在另一个`List`值中。`Box<T>`将会指向堆中的下一个`List`值，而不是位于`Cons`变体内部。从概念上讲，我们仍然有一个列表，这个列表又包含其他列表，但这种实现方式更像是将元素并排放置，而不是将它们嵌套在一起。

我们可以修改 Listing 15-2 中 `List` enum 的定义，以及 Listing 15-3 中 `List` 的使用方式，使其与 Listing 15-5 中的代码一致。这样修改后的代码就可以正常编译了。

<Listing number="15-5" file-name="src/main.rs" caption="The definition of `List` that uses `Box<T>` in order to have a known size">

```rust
enum List {
    Cons(i32, Box<List>),
    Nil,
}

use crate::List::{Cons, Nil};

fn main() {
    let list = Cons(1, Box::new(Cons(2, Box::new(Cons(3, Box::new(Nil))))));
}

```

</Listing>

The `Cons` variant needs the size of an `i32` plus the space to store the box’s
pointer data. The `Nil` variant stores no values, so it needs less space on the
stack than the `Cons` variant. We now know that any `List` value will take up
the size of an `i32` plus the size of a box’s pointer data. By using a box,
we’ve broken the infinite, recursive chain, so the compiler can figure out the
size it needs to store a `List` value. Figure 15-2 shows what the `Cons`
variant looks like now.

<img alt="A rectangle labeled 'Cons' split into two smaller rectangles. The first smaller rectangle holds the label 'i32', and the second smaller rectangle holds the label 'Box' with one inner rectangle that contains the label 'usize', representing the finite size of the box's pointer." src="img/trpl15-02.svg" class="center" />

<span class="caption">Figure 15-2: A `List` that is not infinitely sized,
because `Cons` holds a `Box`</span>

Boxes provide only the indirection and heap allocation; they don’t have any
other special capabilities, like those we’ll see with the other smart pointer
types. They also don’t have the performance overhead that these special
capabilities incur, so they can be useful in cases like the cons list where the
indirection is the only feature we need. We’ll look at more use cases for boxes
in Chapter 18.

The `Box<T>` type is a smart pointer because it implements the `Deref` trait,
which allows `Box<T>` values to be treated like references. When a `Box<T>`
value goes out of scope, the heap data that the box is pointing to is cleaned
up as well because of the `Drop。这些特性在实现上非常重要，它们对于我们在本章后续部分将讨论的其他智能指针类型的功能实现起着关键作用。让我们更详细地探讨这两个特性。

[trait-objects]: ch18-02-trait-objects.html#using-trait-objects-to-abstract-over-shared-behavior
