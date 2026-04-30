## `RefCell<T>` 与内部可变性模式

_内部可变性_是Rust中的一种设计模式，它允许你在存在不可变引用的情况下修改数据；通常情况下，这种操作是被借用规则所禁止的。为了实现数据修改，该模式会在数据结构内部使用`unsafe`代码来打破Rust通常关于变异和借用的规则。使用unsafe代码可以向编译器表明，我们是手动检查这些规则，而不是依赖编译器来为我们检查；我们将在第20章中更详细地讨论unsafe代码。

我们只能在能够确保借用规则在运行时得到遵守的情况下，使用具有内部可变性模式的类型。尽管编译器无法保证这一点，但涉及的 `unsafe` 代码会被包装在一个安全的 API 中，而外部类型仍然保持不可变性。

让我们通过查看遵循内部可变性模式的 `RefCell<T>` 类型来探讨这个概念。

<!-- Old headings. Do not remove or links may break. -->

<a id="enforcing-borrowing-rules-at-runtime-with-refcellt"></a>

### 在运行时强制执行借用规则

与 `Rc<T>` 不同， `RefCell<T>` 类型表示对数据的单一所有权。那么，究竟是什么让 `RefCell<T>` 与 `Box<T>` 这样的类型有所不同呢？请回想一下你在第4章中学到的借用规则。

- 在任何时候，你可以拥有一个可变引用，或者任意数量的不可变引用（但不能同时拥有两者）。
- 引用必须始终有效。

在引用和 `Box<T>` 的情况下，借用规则的不变量在编译时会被强制执行。而在 `RefCell<T>` 的情况下，这些不变量在运行时才会被强制执行。在引用的情况下，如果你违反了这些规则，将会出现编译错误。而在 `RefCell<T>` 的情况下，如果你违反了这些规则，程序将会出现 panic 并退出。

在编译时检查借用规则的优势在于，错误可以在开发过程中更早地被发现，而且由于所有分析都在编译之前完成，因此不会影响到运行时的性能。基于这些原因，在大多数情况下，编译时检查借用规则是最佳选择，这也是Rust的默认行为。

在运行时检查借用规则的优势在于，某些内存安全的场景可以被允许，而这些场景在编译时检查是无法被禁止的。静态分析，比如Rust编译器，本质上是一种保守的方法。有些代码特性是无法通过分析代码来检测的：最著名的例子就是停机问题，这个问题超出了本书的讨论范围，但确实是一个值得研究的话题。

因为有些分析是不可能的，如果Rust编译器无法确定代码是否遵循所有权规则，它可能会拒绝一个正确的程序。这样一来，Rust采取了保守的做法。如果Rust接受了错误的程序，用户就无法信任Rust所做出的保证。然而，如果Rust拒绝了正确的程序，程序员会感到不便，但不会发生任何灾难性后果。当您确信自己的代码遵循了借用规则，但编译器无法理解和保证这一点时，使用 `RefCell<T>` 类型就非常有用。

与 `Rc<T>` 类似， `RefCell<T>` 仅适用于单线程场景。如果你在多线程环境中尝试使用它，将会引发编译时错误。我们将在第16章中讨论如何在多线程程序中实现 `RefCell<T>` 的功能。

以下是选择 `Box<T>`、 `Rc<T>` 或 `RefCell<T>` 的理由的总结：

- `Rc<T>` 允许同一数据拥有多个所有者； `Box<T>` 和 `RefCell<T>` 则只有单个所有者。
- `Box<T>` 允许在编译时检查可变或不可变的借用； `Rc<T>` 仅允许在编译时检查不可变的借用； `RefCell<T>` 允许在运行时检查可变或不可变的借用。
- 由于 `RefCell<T>` 允许在运行时检查可变借用，因此即使在 `RefCell<T>` 是不可变的情况下，也可以修改 `RefCell<T>` 中的值。

在不可变值内部修改其值是内部可变性模式。让我们来看一个内部可变性有用的场景，并探讨如何实现这种特性。

<!-- Old headings. Do not remove or links may break. -->

<a id="interior-mutability-a-mutable-borrow-to-an-immutable-value"></a>

### 使用内部可变性

借用规则的一个结果是，当你拥有一个不可变的值时，你不能对其进行可变的借用。例如，以下代码将无法编译：

```rust,ignore,does_not_compile
fn main() {
    let x = 5;
    let y = &mut x;
}

```

如果你尝试编译这段代码，将会出现以下错误：

```console
$ cargo run
   Compiling borrowing v0.1.0 (file:///projects/borrowing)
error[E0596]: cannot borrow `x` as mutable, as it is not declared as mutable
 --> src/main.rs:3:13
  |
3 |     let y = &mut x;
  |             ^^^^^^ cannot borrow as mutable
  |
help: consider changing this to be mutable
  |
2 |     let mut x = 5;
  |         +++

For more information about this error, try `rustc --explain E0596`.
error: could not compile `borrowing` (bin "borrowing") due to 1 previous error

```

不过，在某些情况下，让一个值在自身的方法中发生变异，但对其他代码来说却表现为不可变，这是很有用的。位于该值方法之外的代码将无法对该值进行变异。使用 `RefCell<T>` 是一种实现内部可变异性的方法，但 `RefCell<T>` 并不能完全规避借用规则：编译器的借用检查器允许这种内部可变性，而借用规则则是在运行时进行检查的。如果你违反了这些规则，系统会显示 `panic!` 的错误信息，而不是编译错误。

让我们通过一个实际例子来演示如何使用 `RefCell<T>` 来修改不可变的值，并了解为什么这样做是有用的。

<!-- Old headings. Do not remove or links may break. -->

<a id="a-use-case-for-interior-mutability-mock-objects"></a>

#### 使用模拟对象进行测试

在测试过程中，程序员有时会使用一种类型来代替另一种类型，以便观察特定的行为，并确认该类型是否被正确实现。这种占位类型被称为“测试用替身”。可以将其想象成电影中的替身演员，他们代替真实的演员来表演一些特别复杂的场景。在测试运行时，测试用替身可以替代其他类型。而“模拟对象”则是特定类型的测试用替身，它们会记录测试过程中的各种情况，从而确保正确的操作确实发生了。

Rust中的对象与其他语言中的对象有所不同，而且Rust的标准库中没有内置类似mock对象的功能。不过，你完全可以创建一个结构体，使其具备与mock对象相同的功能。

我们将测试以下场景：我们将创建一个库，该库会跟踪一个数值，并根据该数值与最大值之间的差距来发送消息。例如，这个库可以用来记录用户允许的API调用次数配额。

我们的库仅提供以下功能：跟踪某个值距离最大值还有多远，以及这些消息应该在什么时间显示。使用我们库的应用程序需要自行实现发送消息的机制：应用程序可以直接向用户显示消息，发送电子邮件，发送短信，或者采取其他方式。库不需要了解这些细节。它只需要一个实现了我们提供的 `Messenger` 特性的对象即可。列表15-20展示了该库的代码。

<Listing number="15-20" file-name="src/lib.rs" caption="A library to keep track of how close a value is to a maximum value and warn when the value is at certain levels">

```rust,noplayground
pub trait Messenger {
    fn send(&self, msg: &str);
}

pub struct LimitTracker<'a, T: Messenger> {
    messenger: &'a T,
    value: usize,
    max: usize,
}

impl<'a, T> LimitTracker<'a, T>
where
    T: Messenger,
{
    pub fn new(messenger: &'a T, max: usize) -> LimitTracker<'a, T> {
        LimitTracker {
            messenger,
            value: 0,
            max,
        }
    }

    pub fn set_value(&mut self, value: usize) {
        self.value = value;

        let percentage_of_max = self.value as f64 / self.max as f64;

        if percentage_of_max >= 1.0 {
            self.messenger.send("Error: You are over your quota!");
        } else if percentage_of_max >= 0.9 {
            self.messenger
                .send("Urgent warning: You've used up over 90% of your quota!");
        } else if percentage_of_max >= 0.75 {
            self.messenger
                .send("Warning: You've used up over 75% of your quota!");
        }
    }
}

```

</Listing>

这段代码中的一个重要部分是，`Messenger` trait有一个名为`send`的方法，该方法接受一个不可变的对`self`的引用，以及消息的文本。这个trait是我们模拟对象需要实现的接口，这样模拟对象就可以像真实对象一样被使用。另一个重要部分是，我们希望测试`set_value`方法在`LimitTracker`上的行为。我们可以改变传递给`value`参数的内容，但是`set_value`并不返回任何内容以供我们进行断言。我们希望能够判断，如果我们创建一个实现了`Messenger` trait的`LimitTracker`对象，并且为`max`指定了特定的值，那么当我们在`value`中传递不同的数值时，模拟对象会发送相应的消息。

我们需要一个模拟对象，当调用 `send` 时，它不会发送电子邮件或短信，而只是记录被指示要发送的消息。我们可以创建一个新的模拟对象实例，创建一个使用该模拟对象的 `LimitTracker`，然后调用 `LimitTracker` 中的 `set_value` 方法，最后检查模拟对象是否包含我们期望的消息。列表15-21展示了实现这样一个模拟对象的尝试，但借用检查器不允许这样做。

<Listing number="15-21" file-name="src/lib.rs" caption="An attempt to implement a `MockMessenger` that isn’t allowed by the borrow checker">

```rust,ignore,does_not_compile
#[cfg(test)]
mod tests {
    use super::*;

    struct MockMessenger {
        sent_messages: Vec<String>,
    }

    impl MockMessenger {
        fn new() -> MockMessenger {
            MockMessenger {
                sent_messages: vec![],
            }
        }
    }

    impl Messenger for MockMessenger {
        fn send(&self, message: &str) {
            self.sent_messages.push(String::from(message));
        }
    }

    #[test]
    fn it_sends_an_over_75_percent_warning_message() {
        let mock_messenger = MockMessenger::new();
        let mut limit_tracker = LimitTracker::new(&mock_messenger, 100);

        limit_tracker.set_value(80);

        assert_eq!(mock_messenger.sent_messages.len(), 1);
    }
}

```

</Listing>

这段测试代码定义了一个 `MockMessenger` 结构体，该结构体包含一个 `sent_messages` 字段，该字段具有 `Vec` 和 `String` 值，用于记录需要发送的消息。我们还定义了一个相关的函数 `new`，以便能够方便地创建以空消息列表开头的新 `MockMessenger` 值。接着，我们为 `MockMessenger` 实现了 `Messenger` 特性，这样我们就可以向 `LimitTracker` 传递 `MockMessenger`。在定义 `send` 方法时，我们将作为参数传递的消息存储在 `MockMessenger` 的 `sent_messages` 列表中。

在测试中，我们旨在观察当`LimitTracker`被设置为`value`时会发生什么情况，而`value`的值应超过`max`值的75%。首先，我们创建一个新的`MockMessenger`，它最初是一个空的消息列表。接着，我们创建一个新的`LimitTracker`，并为其分配对新的`MockMessenger`的引用，同时赋予`max`一个`100`的值。然后，我们在`LimitTracker`上调用`set_value`方法，并传入一个`80`的值，该值确实超过了100的75%。最后，我们断言，由`MockMessenger`所跟踪的消息列表中现在应该有一个消息。

不过，这个测试存在一个问题，如下所示：

```console
$ cargo test
   Compiling limit-tracker v0.1.0 (file:///projects/limit-tracker)
error[E0596]: cannot borrow `self.sent_messages` as mutable, as it is behind a `&` reference
  --> src/lib.rs:58:13
   |
58 |             self.sent_messages.push(String::from(message));
   |             ^^^^^^^^^^^^^^^^^^ `self` is a `&` reference, so the data it refers to cannot be borrowed as mutable
   |
help: consider changing this to be a mutable reference in the `impl` method and the `trait` definition
   |
 2 ~     fn send(&mut self, msg: &str);
 3 | }
...
56 |     impl Messenger for MockMessenger {
57 ~         fn send(&mut self, message: &str) {
   |

For more information about this error, try `rustc --explain E0596`.
error: could not compile `limit-tracker` (lib test) due to 1 previous error

```

我们无法修改 `MockMessenger` 来跟踪消息，因为 `send` 方法需要的是对 `self` 的不可变引用。我们也无法将错误文本中的建议采纳，即在 `impl` 方法和 trait 定义中同时使用 `&mut self`。我们并不想仅仅为了测试而修改 `Messenger` trait。相反，我们需要找到一种方法，让我们的测试代码能够与我们现有的设计兼容并正确运行。

这种情况中，内部可变性可以发挥重要作用！我们将`sent_messages`存储在一个`RefCell<T>`中，然后`send`方法就能够修改`sent_messages`来保存我们看到的消息。列表15-22展示了这一过程的实现方式。

<Listing number="15-22" file-name="src/lib.rs" caption="Using `RefCell<T>` to mutate an inner value while the outer value is considered immutable">

```rust,noplayground
#[cfg(test)]
mod tests {
    use super::*;
    use std::cell::RefCell;

    struct MockMessenger {
        sent_messages: RefCell<Vec<String>>,
    }

    impl MockMessenger {
        fn new() -> MockMessenger {
            MockMessenger {
                sent_messages: RefCell::new(vec![]),
            }
        }
    }

    impl Messenger for MockMessenger {
        fn send(&self, message: &str) {
            self.sent_messages.borrow_mut().push(String::from(message));
        }
    }

    #[test]
    fn it_sends_an_over_75_percent_warning_message() {
        // --snip--

        assert_eq!(mock_messenger.sent_messages.borrow().len(), 1);
    }
}

```

</Listing>

The `发送消息` field is now of type `RefCell<Vec<String>>` instead of
`向量<String>`. In the `新建` function, we create a new `RefCell<Vec<String>>`
instance around the empty vector.

For the implementation of the `发送` method, the first parameter is still an
immutable borrow of `自身`, which matches the trait definition. We call
`借用可变` on the `RefCell<Vec<String>>` in `自身已发送的消息` to get a
mutable reference to the value inside the `RefCell<Vec<String>>`, which is the
vector. Then, we can call `推送` on the mutable reference to the vector to keep
track of the messages sent during the test.

The last change we have to make is in the assertion: To see how many items are
in the inner vector, we call `借用` on the `RefCell<Vec<String>>` to get an
immutable reference to the vector.

Now that you’ve seen how to use `RefCell<T>`, let’s dig into how it works!

<!-- Old headings. Do not remove or links may break. -->

<a id="keeping-track-of-borrows-at-runtime-with-refcellt"></a>

#### Tracking Borrows at Runtime

When creating immutable and mutable references, we use the `&` and `&mut`
syntax, respectively. With `RefCell<T>`, we use the `借用` and `借用可变`
methods, which are part of the safe API that belongs to `RefCell<T>`. The
`借用` method returns the smart pointer type `引用<T>`, and `借用可变`
returns the smart pointer type `RefMut<T>`. Both types implement `解引用`, so we
can treat them like regular references.

The `RefCell<T>` keeps track of how many `引用<T>` and `RefMut<T>` smart
pointers are currently active. Every time we call `借用`, the `RefCell<T>`
increases its count of how many immutable borrows are active. When a `引用⊂PH48`
value goes out of scope, the count of immutable borrows goes down by 1. Just
like the compile-time borrowing rules, `RefCell⊂PH50` lets us have many immutable
borrows or one mutable borrow at any point in time.

If we try to violate these rules, rather than getting a compiler error as we
would with references, the implementation of `RefCell⊂PH52` will panic at
runtime. Listing 15-23 shows a modification of the implementation of `发送` in
Listing 15-22. We’re deliberately trying to create two mutable borrows active
for the same scope to illustrate that `RefCell<T>` prevents us from doing this
at runtime.

<Listing number="15-23" file-name="src/lib.rs" caption="Creating two mutable references in the same scope to see that `RefCell<T>`将引发恐慌

```rust,ignore,panics
    impl Messenger for MockMessenger {
        fn send(&self, message: &str) {
            let mut one_borrow = self.sent_messages.borrow_mut();
            let mut two_borrow = self.sent_messages.borrow_mut();

            one_borrow.push(String::from(message));
            two_borrow.push(String::from(message));
        }
    }

```

</Listing>

我们为从 `borrow_mut` 返回的 `RefMut<T>` 智能指针创建了一个变量 `one_borrow`。然后，我们以相同的方式在 `two_borrow` 变量中创建了另一个可变借用对象。这样，在同一个作用域中就有两个可变引用，这是不允许的。当我们运行库中的测试时，Listing 15-23 中的代码可以编译而不会出错，但是测试将会失败。

```console
$ cargo test
   Compiling limit-tracker v0.1.0 (file:///projects/limit-tracker)
    Finished `test` profile [unoptimized + debuginfo] target(s) in 0.91s
     Running unittests src/lib.rs (target/debug/deps/limit_tracker-e599811fa246dbde)

running 1 test
test tests::it_sends_an_over_75_percent_warning_message ... FAILED

failures:

---- tests::it_sends_an_over_75_percent_warning_message stdout ----

thread 'tests::it_sends_an_over_75_percent_warning_message' panicked at src/lib.rs:60:53:
RefCell already borrowed
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace


failures:
    tests::it_sends_an_over_75_percent_warning_message

test result: FAILED. 0 passed; 1 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

error: test failed, to rerun pass `--lib`

```

请注意，代码因消息 `already borrowed:
BorrowMutError` 而陷入恐慌。这就是 `RefCell<T>` 在运行时处理借用规则违规的方式。

选择在运行时而不是编译时捕获借用错误，就像我们在这里所做的那样，意味着你在开发过程的后期可能会发现代码中的错误——可能要等到代码被部署到生产环境之后才会发现。此外，由于需要在运行时而不是编译时跟踪借用情况，代码的运行性能会略有下降。不过，使用 `RefCell<T>` 可以创建一个模拟对象，该对象可以在被允许使用不可变值的上下文中自行修改，以记录它所看到的信息。尽管有这些权衡，你仍然可以使用 `RefCell<T>` 来获得比普通引用更多的功能。

<!-- Old headings. Do not remove or links may break. -->

<a id="having-multiple-owners-of-mutable-data-by-combining-rc-t-and-ref-cell-t"></a>
<a id="allowing-multiple-owners-of-mutable-data-with-rct-and-refcellt"></a>

### 允许多个可变数据的所有者

使用 `RefCell<T>` 的常见方式是与 `Rc<T>` 结合使用。需要注意的是，`Rc<T>` 允许某些数据拥有多个所有者，但它仅提供对该数据的不可变访问权限。而如果使用 `Rc<T>` 来持有 `RefCell<T>`，那么就可以获取一个可以拥有多个所有者的值，并且还可以对其进行修改！

例如，回想一下清单15-18中的cons列表示例，我们使用`Rc<T>`来允许多个列表共享另一个列表的所有权。由于`Rc<T>`仅持有不可变的值，因此一旦我们创建了这些值，就无法再修改它们。接下来，我们添加`RefCell<T>`，以便能够修改这些列表中的值。清单15-24表明，通过在`Cons`的定义中使用`RefCell<T>`，我们可以修改所有列表中存储的值。

<Listing number="15-24" file-name="src/main.rs" caption="Using `Rc<RefCell<i32>>` to create a `列表` that we can mutate">

```rust
#[derive(Debug)]
enum List {
    Cons(Rc<RefCell<i32>>, Rc<List>),
    Nil,
}

use crate::List::{Cons, Nil};
use std::cell::RefCell;
use std::rc::Rc;

fn main() {
    let value = Rc::new(RefCell::new(5));

    let a = Rc::new(Cons(Rc::clone(&value), Rc::new(Nil)));

    let b = Cons(Rc::new(RefCell::new(3)), Rc::clone(&a));
    let c = Cons(Rc::new(RefCell::new(4)), Rc::clone(&a));

    *value.borrow_mut() += 10;

    println!("a after = {a:?}");
    println!("b after = {b:?}");
    println!("c after = {c:?}");
}

```

</Listing>

We create a value that is an instance of `引用<RefCell<i32>>` and store it in a
variable named `值` so that we can access it directly later. Then, we create
a `列表` in `a` with a `常量` variant that holds `值`. We need to clone
`值` so that both `a` and `值` have ownership of the inner `5` value
rather than transferring ownership from `值` to `a` or having `a` borrow
from `值`.

We wrap the list `a` in an `引用<T>` so that when we create lists `b` and `c`,
they can both refer to `a`, which is what we did in Listing 15-18.

After we’ve created the lists in `a`, `b`, and `c`, we want to add 10 to the
value in `值`. We do this by calling `借用·可变性` on `值`, which uses the
automatic dereferencing feature we discussed in [“Where’s the `->`
Operator?”][wheres-the---operator]<!-- ignore --> in Chapter 5 to dereference
the `引用<T>` to the inner `引用可传递<T>` value. The `借用·可变性` method returns a
`引用·可变性<T>` smart pointer, and we use the dereference operator on it and change
the inner value.

When we print `a`, `b`, and `c`, we can see that they all have the modified
value of `15` rather than `5`:

```console
$ cargo run
   Compiling cons-list v0.1.0 (file:///projects/cons-list)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.63s
     Running `target/debug/cons-list`
a after = Cons(RefCell { value: 15 }, Nil)
b after = Cons(RefCell { value: 3 }, Cons(RefCell { value: 15 }, Nil))
c after = Cons(RefCell { value: 4 }, Cons(RefCell { value: 15 }, Nil))

```

This technique is pretty neat! By using `引用可传递<T>`, we have an outwardly
immutable `列表` value. But we can use the methods on `引用可传递<T>` that provide
access to its interior mutability so that we can modify our data when we need
to. The runtime checks of the borrowing rules protect us from data races, and
it’s sometimes worth trading a bit of speed for this flexibility in our data
structures. Note that `引用可传递<T>` does not work for multithreaded code!
`互斥锁<T>` is the thread-safe version of `引用可传递<T>`, and we’ll discuss
`互斥锁<T>` 在第十六章中

[wheres-the---operator]: ch05-03-method-syntax.html#wheres-the---operator
