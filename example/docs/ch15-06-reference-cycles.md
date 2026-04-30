## 引用循环可能会导致内存泄漏

Rust的内存安全特性虽然能有效防止内存泄漏，但这种情况仍然可能发生。完全防止内存泄漏并非Rust的保证之一，因此Rust中的内存泄漏仍然是可避免的。通过使用 `Rc<T>` 和 `RefCell<T>`，Rust确实允许内存泄漏的发生：可以创建引用，使得对象之间形成循环引用。这种情况下，循环中的对象引用计数永远不会降为零，因此它们的值也永远不会被释放，从而导致内存泄漏。

### 创建引用循环

让我们来看看引用循环可能如何发生，以及如何防止这种情况，从 Listing 15-25 中的 `List` 枚举和 `tail` 方法的定义开始。

**清单 15-25:** *src/main.rs* — 一个cons列表定义，其中包含一个 `RefCell<T>`，这样我们就可以修改 `Cons` 变体所指向的内容。

```rust
use crate::List::{Cons, Nil};
use std::cell::RefCell;
use std::rc::Rc;

#[derive(Debug)]
enum List {
    Cons(i32, RefCell<Rc<List>>),
    Nil,
}

impl List {
    fn tail(&self) -> Option<&RefCell<Rc<List>>> {
        match self {
            Cons(_, item) => Some(item),
            Nil => None,
        }
    }
}

```

我们正在使用 Listing 15-5 中给出的 `List` 定义的另一种变体。在 `Cons` 变体中，第二个元素现在变成了 `RefCell<Rc<List>>`。这意味着，与 Listing 15-24 中那样能够修改 `i32` 值不同，我们现在想要修改的是 `List` 值，而 `List` 的值指向的是 `Cons` 的一个变体。我们还添加了一个 `tail` 方法，以便在我们拥有 `Cons` 变体时，能够方便地访问第二个项。

在 Listing 15-26 中，我们添加了一个 `main` 函数，该函数使用了 Listing 15-25 中的定义。这段代码在 `a` 和 `b` 中分别创建了一个列表，这两个列表都指向 `a` 中的列表。然后，它修改了 `a` 中的列表，使其指向 `b`，从而创建了一个引用循环。在过程中，还有 `println!` 语句用于显示各个阶段的引用计数情况。

**清单 15-26:** *src/main.rs* — 创建一个由两个 `List` 值相互指向的引用循环

```rust
fn main() {
    let a = Rc::new(Cons(5, RefCell::new(Rc::new(Nil))));

    println!("a initial rc count = {}", Rc::strong_count(&a));
    println!("a next item = {:?}", a.tail());

    let b = Rc::new(Cons(10, RefCell::new(Rc::clone(&a))));

    println!("a rc count after b creation = {}", Rc::strong_count(&a));
    println!("b initial rc count = {}", Rc::strong_count(&b));
    println!("b next item = {:?}", b.tail());

    if let Some(link) = a.tail() {
        *link.borrow_mut() = Rc::clone(&b);
    }

    println!("b rc count after changing a = {}", Rc::strong_count(&b));
    println!("a rc count after changing a = {}", Rc::strong_count(&a));

    // Uncomment the next line to see that we have a cycle;
    // it will overflow the stack.
    // println!("a next item = {:?}", a.tail());
}

```

我们创建了一个 `Rc<List>` 实例，该实例在变量 `a` 中存储一个 `List` 值，并且初始列表为 `5, Nil`。接着，我们创建了一个 `Rc<List>` 实例，该实例在变量 `b` 中存储另一个 `List` 值，同时 `b` 还包含值 `10`，并且指向 `a` 中的列表。

我们修改 `a`，使其指向 `b` 而不是 `Nil`，从而创建了一个循环。我们通过使用 `tail` 方法来获取 `a` 中 `RefCell<Rc<List>>` 的引用，并将该引用存储在变量 `link` 中。然后，我们使用 `borrow_mut` 方法来修改 `RefCell<Rc<List>>` 中的值，将其中持有的 `Nil` 值替换为 `Rc<List>`。

当我们运行这段代码时，暂时将最后一个 `println!` 注释掉，我们会得到这样的输出：

```console
$ cargo run
   Compiling cons-list v0.1.0 (file:///projects/cons-list)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.53s
     Running `target/debug/cons-list`
a initial rc count = 1
a next item = Some(RefCell { value: Nil })
a rc count after b creation = 2
b initial rc count = 1
b next item = Some(RefCell { value: Cons(5, RefCell { value: Nil }) })
b rc count after changing a = 2
a rc count after changing a = 2

```

在我们将 `a` 中的列表修改为指向 `b` 之后， `Rc<List>` 实例在 `a` 和 `b` 中的引用计数都变为 2。在 `main` 的末尾，Rust 会释放变量 `b`，这使得 `b` `Rc<List>` 实例的引用计数从 2 降为 1。此时， `Rc<List>` 在堆上占用的内存不会被释放，因为其引用计数仍为 1，而非 0。接着，Rust 会释放 `a`，这使得 `a` `Rc<List>` 实例的引用计数从 2 降为 1。不过，这个实例的内存也不会被释放，因为另一个 `Rc<List>` 实例仍然引用着它。而分配给列表的内存则永远无法被回收。为了形象地展示这个引用循环，我们在图 15-4 中绘制了相应的图表。

<img alt="A rectangle labeled 'a' that points to a rectangle containing the integer 5. A rectangle labeled 'b' that points to a rectangle containing the integer 10. The rectangle containing 5 points to the rectangle containing 10, and the rectangle containing 10 points back to the rectangle containing 5, creating a cycle." src="img/trpl15-04.svg" class="center" />

图15-4：列表`a`和`b`之间的引用循环，它们相互指向</span>

如果你取消注释最后的 `println!` 并运行程序，Rust 会尝试使用 `a` 来指向 `b`，再指向 `a`，以此类推，直到堆栈溢出。

与真实世界的应用程序相比，在这个示例中创建引用循环的后果并不严重：我们创建引用循环后，程序会立即终止。然而，如果一个更复杂的程序在循环中分配了大量内存，并且长时间持有这些内存，那么程序就会使用超出其需求的内存，从而可能使系统不堪重负，导致可用内存不足。

创建引用循环并不容易，但也不是不可能。如果你有包含其他值的类型，或者存在类似嵌套的类型组合，并且这些类型具有可变性以及引用计数机制，那么你必须确保不会创建引用循环；你不能依赖Rust来自动检测这些循环。在程序中创建引用循环相当于逻辑错误，你应该通过自动化测试、代码审查以及其他软件开发实践来减少这种错误的发生。

另一种避免引用循环的方法是重新组织数据结构，使得某些引用表示所有权，而另一些引用则不表示所有权。这样，循环就可以由一些所有权关系和一些非所有权关系组成，只有所有权关系才会影响某个值是否可以被删除。在清单15-25中，我们总是希望 `Cons` 这种变体能够拥有自己的列表，因此无法重新组织数据结构。让我们来看一个例子，使用由父节点和子节点组成的图，来了解何时使用非所有权关系是一种有效的防止引用循环的方法。

<!-- Old headings. Do not remove or links may break. -->

<a id="preventing-reference-cycles-turning-an-rct-into-a-weakt"></a>

### 使用 `Weak<T>` 防止引用循环

到目前为止，我们已经证明了调用 `Rc::clone` 会增加 `Rc<T>` 实例的 `strong_count` 值，而 `Rc<T>` 实例只有在其 `strong_count` 为 0 时才会被清理。你还可以通过调用 `Rc::downgrade` 并传递对 `Rc<T>` 的引用，来在 `Rc<T>` 实例中创建对该值的弱引用。*强引用*则是用来共享 `Rc<T>` 实例所有权的方式。*弱引用*则不会表达任何所有权关系，其数量也不会影响 `Rc<T>` 实例的清理时机。由于任何涉及弱引用的循环都会在相关值的强引用数量变为 0 时被打破，因此弱引用不会导致引用循环。

当你调用 `Rc::downgrade` 时，你会得到一个类型为 `Weak<T>` 的智能指针。与 `Rc<T>` 实例中的 `strong_count` 增加 1 不同，调用 `Rc::downgrade` 会使 `weak_count` 增加 1。 `Rc<T>` 类型使用 `weak_count` 来记录有多少个 `Weak<T>` 引用，这与 `strong_count` 类似。不同之处在于， `weak_count` 不需要为 0， `Rc<T>` 实例才能被清理。

因为 `Weak<T>` 所引用的对象可能已经被删除，所以要对 `Weak<T>` 指向的对象进行操作，必须确保该对象仍然存在。可以通过调用 `upgrade` 方法来实现这一点，该方法会返回一个 `Option<Rc<T>>`。如果 `Rc<T>` 所引用的对象尚未被删除，那么结果将是 `Some`；如果 `Rc<T>` 所引用的对象已经被删除，那么结果将是 `None`。由于 `upgrade` 返回一个 `Option<Rc<T>>`，Rust 会确保 `Some` 和 `None` 这两种情况都能得到处理，从而不会出现无效的指针。

例如，我们不会使用一种列表结构，其中每个元素只知道下一个元素的信息，而是会创建一个树形结构，其中每个元素不仅知道自己的子元素，还知道自己的父元素。

<!-- Old headings. Do not remove or links may break. -->

<a id="creating-a-tree-data-structure-a-node-with-child-nodes"></a>

#### 创建树数据结构

首先，我们将构建一个树结构，其中的节点能够了解它们的子节点。我们将创建一个名为 `Node` 的结构，该结构包含自己的 `i32` 值，同时还包含对其子节点 `Node` 的引用。

<span class="filename">文件名: src/main.rs</span>

```rust
use std::cell::RefCell;
use std::rc::Rc;

#[derive(Debug)]
struct Node {
    value: i32,
    children: RefCell<Vec<Rc<Node>>>,
}

```

我们希望一个 `Node` 能够拥有其下属元素，并且我们希望将这些所有权与变量共享，这样我们就可以直接访问树中的每个 `Node`。为了实现这一点，我们将 `Vec<T>` 项定义为 `Rc<Node>` 类型的值。我们还希望修改哪些节点是另一个节点的下属节点，因此我们在 `Vec<Rc<Node>>` 周围定义了一个 `RefCell<T>` 结构。

接下来，我们将使用我们的结构体定义，创建一个名为`leaf`的实例，其值为`3`，并且没有子节点。另外，还会创建一个名为`branch`的实例，其值为`5`，并且`leaf`是其子节点之一，如清单15-27所示。

**清单 15-27:** *src/main.rs* — 创建一个 `leaf` 节点，该节点没有子节点；同时创建一个 `branch` 节点，该节点的子节点中有一个 `leaf`。

```rust
fn main() {
    let leaf = Rc::new(Node {
        value: 3,
        children: RefCell::new(vec![]),
    });

    let branch = Rc::new(Node {
        value: 5,
        children: RefCell::new(vec![Rc::clone(&leaf)]),
    });
}

```

我们将 `leaf` 中的 `Rc<Node>` 克隆并存储在 `branch` 中，这意味着 `leaf` 中的 `Node` 现在有两个所有者： `leaf` 和 `branch`。我们可以通过 `branch.children` 从 `branch` 到达 `leaf`，但是无法从 `leaf` 到达 `branch`。原因是 `leaf` 没有对 `branch` 的引用，也不知道它们之间存在关联。我们希望 `leaf` 能够知道 `branch` 是它的父节点。接下来我们将实现这一功能。

#### 从子节点添加引用到父节点

为了让子节点能够感知其父节点，我们需要在 `Node` 结构定义中添加 `parent` 字段。问题在于如何确定 `parent` 的类型。我们知道 `parent` 不能包含 `Rc<T>`，因为那样会形成一个引用循环：其中 `leaf.parent` 指向 `branch`，而 `branch.children` 指向 `leaf`，这会导致它们的 `strong_count` 值永远不为 0。

从另一个角度来看，父节点应该拥有其子节点：如果父节点被删除，其子节点也应该被删除。然而，子节点不应该拥有其父节点：如果我们删除一个子节点，其父节点仍然应该存在。这种情况适合使用弱引用！

因此，我们不再使用 `Rc<T>`，而是让 `parent` 的类型使用 `Weak<T>`，具体来说就是 `RefCell<Weak<Node>>`。现在，我们的 `Node` 结构体定义看起来就像这样：

<span class="filename"> 文件名: src/main.rs</span>

```rust
use std::cell::RefCell;
use std::rc::{Rc, Weak};

#[derive(Debug)]
struct Node {
    value: i32,
    parent: RefCell<Weak<Node>>,
    children: RefCell<Vec<Rc<Node>>>,
}

```

一个节点可以引用其父节点，但并不拥有其父节点。在清单15-28中，我们将 `main` 更新为使用这个新定义，这样 `leaf` 节点就可以引用其父节点 `branch` 了。

**列表 15-28:** *src/main.rs* — 一个 `leaf` 节点，它对其父节点有弱引用， `branch`

```rust
fn main() {
    let leaf = Rc::new(Node {
        value: 3,
        parent: RefCell::new(Weak::new()),
        children: RefCell::new(vec![]),
    });

    println!("leaf parent = {:?}", leaf.parent.borrow().upgrade());

    let branch = Rc::new(Node {
        value: 5,
        parent: RefCell::new(Weak::new()),
        children: RefCell::new(vec![Rc::clone(&leaf)]),
    });

    *leaf.parent.borrow_mut() = Rc::downgrade(&branch);

    println!("leaf parent = {:?}", leaf.parent.borrow().upgrade());
}

```

创建 `leaf` 节点的过程与 Listing 15-27 类似，唯一的区别在于 `parent` 字段： `leaf` 开始时没有父节点，因此我们需要创建一个新的、空的 `Weak<Node>` 引用实例。

此时，当我们尝试使用 `upgrade` 方法获取 `leaf` 的引用时，我们得到的是一个 `None` 的值。我们在第一个 `println!` 语句的输出中看到了这一点：

```text
leaf parent = None
```

当我们创建 `branch` 节点时，它也会在 `parent` 字段中有一个新的 `Weak<Node>` 引用，因为 `branch` 没有父节点。我们仍然有 `leaf` 作为 `branch` 的子节点之一。一旦我们在 `branch` 中有了 `Node` 实例，我们就可以修改 `leaf`，使其对父节点有 `Weak<Node>` 的引用。我们在 `leaf` 的 `parent` 字段中对 `RefCell<Weak<Node>>` 使用 `borrow_mut` 方法，然后使用 `Rc::downgrade` 函数从 `branch` 中的 `Rc<Node>` 创建对 `branch` 的 `Weak<Node>` 引用。

当我们再次打印 `leaf` 的父节点时，这次会得到包含 `branch` 的 `Some` 版本。现在， `leaf` 可以访问它的父节点了！当我们打印 `leaf` 时，我们避免了像在 Listing 15-26 中那样出现的循环，最终导致堆栈溢出的情况；而 `Weak<Node>` 的引用则被打印为 `(Weak)`。

```text
leaf parent = Some(Node { value: 5, parent: RefCell { value: (Weak) },
children: RefCell { value: [Node { value: 3, parent: RefCell { value: (Weak) },
children: RefCell { value: [] } }] } })
```

缺乏无限输出表明这段代码没有产生引用循环。我们可以通过调用`Rc::strong_count`和`Rc::weak_count`得到的返回值来判断这一点。

#### 可视化 `strong_count` 和 `weak_count` 的变化

让我们看看，通过创建一个新的内部作用域，并将`branch`的创建移入该作用域，`Rc<Node>`实例的`branch`值会如何变化。通过这样做，我们可以观察到当`branch`被创建出来后，当它离开作用域时会发生什么。这些修改在 Listing 15-29 中有所展示。

**列表 15-29:** *src/main.rs* — 在内部作用域中创建 `branch`，并检查强引用和弱引用计数

```rust
fn main() {
    let leaf = Rc::new(Node {
        value: 3,
        parent: RefCell::new(Weak::new()),
        children: RefCell::new(vec![]),
    });

    println!(
        "leaf strong = {}, weak = {}",
        Rc::strong_count(&leaf),
        Rc::weak_count(&leaf),
    );

    {
        let branch = Rc::new(Node {
            value: 5,
            parent: RefCell::new(Weak::new()),
            children: RefCell::new(vec![Rc::clone(&leaf)]),
        });

        *leaf.parent.borrow_mut() = Rc::downgrade(&branch);

        println!(
            "branch strong = {}, weak = {}",
            Rc::strong_count(&branch),
            Rc::weak_count(&branch),
        );

        println!(
            "leaf strong = {}, weak = {}",
            Rc::strong_count(&leaf),
            Rc::weak_count(&leaf),
        );
    }

    println!("leaf parent = {:?}", leaf.parent.borrow().upgrade());
    println!(
        "leaf strong = {}, weak = {}",
        Rc::strong_count(&leaf),
        Rc::weak_count(&leaf),
    );
}

```

在创建 `leaf` 之后，其子对象 `Rc<Node>` 的强计数值为 1，弱计数值为 0。在内部范围内，我们创建了 `branch` 并将其与 `leaf` 关联起来。此时，当我们打印这些计数时， `Rc<Node>` 在 `branch` 中的强计数值为 1，弱计数值也为 1（因为 `leaf.parent` 指向了 `branch`，而 `Weak<Node>` 则指向了 `branch`）。当我们在 `leaf` 中打印这些计数时，会发现其强计数值为 2，因为 `branch` 现在在 `branch.children` 中保存了 `Rc<Node>` 的克隆副本，但弱计数值仍为 0。

当内部作用域结束时，`branch`就会脱离作用域，而`Rc<Node>`的强引用计数会减少到0，因此`Node`也会被移除。`leaf.parent`的弱引用计数为1，但这并不影响`Node`是否被移除，因此我们不会遇到任何内存泄漏的问题！

如果我们尝试在范围结束后访问 `leaf` 的父级，我们将再次得到 `None`。在程序的最后， `leaf` 中的 `Rc<Node>` 的强计数值为 1，弱计数值为 0，因为变量 `leaf` 现在成为了唯一对 `Rc<Node>` 的引用。

所有用于管理计数和值丢失的逻辑都内置在`Rc<T>`和`Weak<T>`中，以及它们对`Drop` trait的实现中。通过定义`Node` trait时，明确指出子节点与其父节点之间的关系应该是`Weak<T>`引用关系，这样父节点就可以指向子节点，反之亦然，而无需造成引用循环或内存泄漏。

## 总结

本章介绍了如何使用智能指针来实现与Rust默认使用普通引用时不同的保证和权衡。`Box<T>`类型具有已知的大小，并且指向堆上分配的数据。`Rc<T>`类型会跟踪对堆上数据的引用数量，这样数据就可以有多个所有者。而`RefCell<T>`类型具有内部可变性，它提供了一种类型，当我们需要不可变类型但需要修改该类型的内部值时可以使用这种类型；此外，它还在运行时而不是编译时强制执行借用规则。

此外，还讨论了 `Deref` 和 `Drop` 特性，这些特性实现了智能指针的许多功能。我们探讨了可能导致内存泄漏的引用循环，以及如何使用 `Weak<T>` 来防止这种情况的发生。

如果这一章引起了你的兴趣，并且你想自己实现智能指针，请查看 [“The Rustonomicon”][nomicon] 以获取更多有用的信息。

接下来，我们将讨论Rust中的并发机制。你还将学习一些新的智能指针。

[nomicon]: ../nomicon/index.html
