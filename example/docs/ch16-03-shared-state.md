## 共享状态并发

消息传递是一种处理并发的良方法，但它并非唯一的方式。另一种方法是让多个线程访问相同的共享数据。再次参考 Go 语言文档中的口号：“不要通过共享内存来进行通信。”

通过共享内存来进行通信会是什么样子呢？此外，为什么消息传递的爱好者们会提醒不要使用内存共享呢？

从某种程度上说，任何编程语言中的通道都类似于单一所有权。因为一旦你将值通过通道传递出去，就不应该再使用这个值了。共享内存并发则类似于多重所有权：多个线程可以同时访问同一个内存位置。正如我们在第15章中所看到的，智能指针使得多重所有权成为可能，而多重所有权也会带来复杂性，因为需要管理这些不同的所有者。Rust的类型系统和所有权规则在正确管理这些关系方面提供了很大的帮助。例如，让我们来看看互斥锁，这是用于共享内存的常用并发原语之一。

<!-- Old headings. Do not remove or links may break. -->

<a id="using-mutexes-to-allow-access-to-data-from-one-thread-at-a-time"></a>

### 使用互斥锁控制访问

_Mutex_是_互斥_的缩写，意味着在任何给定时间，只有一个线程可以访问某些数据。要访问mutex中的数据，线程必须先通过请求获取mutex的锁来表明它希望访问这些数据。_锁_是一种数据结构，它是mutex的一部分，用于记录当前谁拥有对数据的独占访问权。因此，mutex通过锁定系统来“保护”其所持有的数据。

互斥锁因其使用难度而名声不佳，因为你需要记住两条规则：

1. 在使用数据之前，必须尝试获取锁。
2. 当使用由互斥锁保护的数据完毕后，必须解锁该数据，以便其他线程能够获取锁。

为了更好地理解互斥锁的工作原理，我们可以想象一个会议上的小组讨论场景。在这个场景中，只有一个麦克风可供使用。在一位小组成员发言之前，他们必须先请求或示意其他小组成员可以使用麦克风。当他们拿到麦克风后，就可以随心所欲地发言，然后将其交给下一位想要发言的小组成员。如果某位小组成员在发言结束后忘记将麦克风交还，那么其他成员就无法发言了。如果共享麦克风的管理不当，整个讨论就会无法按计划进行！

互斥体的管理非常难以掌握，这就是为什么很多人对通道感到兴奋。不过，得益于Rust的类型系统和所有权规则，锁定与解锁的操作根本不会出错。

#### `Mutex<T>` 的 API

作为使用互斥锁的一个示例，我们先来看一下在单线程环境中如何使用互斥锁，如清单 16-12 所示。

**列表 16-12:** *src/main.rs* — 为了简单起见，在单线程环境下探索 `Mutex<T>` 的 API

```rust
use std::sync::Mutex;

fn main() {
    let m = Mutex::new(5);

    {
        let mut num = m.lock().unwrap();
        *num = 6;
    }

    println!("m = {m:?}");
}

```

与许多类型一样，我们使用相关的函数 `new` 来创建 `Mutex<T>`。为了访问互斥锁内的数据，我们使用 `lock` 方法来获取锁。这个调用会阻塞当前线程，直到轮到我们获得锁为止，此时线程将无法执行任何任务。

如果另一个持有锁的线程发生恐慌，那么对 `lock` 的调用将会失败。在这种情况下，将没有人能够获取锁，因此我们选择让 `unwrap` 在这种情况下发生恐慌。

在我们获得锁之后，我们可以将名为 `num` 的返回值视为对内部数据的可变引用。类型系统确保我们在在 `m` 中使用该值之前先获得锁。 `m` 的类型是 `Mutex<i32>`，而不是 `i32`，因此我们必须调用 `lock` 才能使用 `i32` 这个值。我们不能忘记这一点；否则，类型系统将不允许我们访问内部的 `i32`。

调用 `lock` 会返回一个名为 `MutexGuard` 的类型，该类型被封装在一个 `LockResult` 结构中。我们对 `LockResult` 的处理是通过调用 `unwrap` 来实现的。 `MutexGuard` 类型实现了 `Deref`，用于指向我们的内部数据；该类型还包含 `Drop` 的实现，当 `MutexGuard` 超出作用域时，该实现会自动释放锁。因此，我们不必担心忘记释放锁，从而防止互斥锁被其他线程占用。因为锁的释放是自动进行的。

在释放锁之后，我们可以打印出互斥量的值，从而看到我们成功地将内部的 `i32` 改为了 `6`。

<!-- Old headings. Do not remove or links may break. -->

<a id="sharing-a-mutext-between-multiple-threads"></a>

#### 对 `Mutex<T>` 的共享访问

现在，让我们尝试使用 `Mutex<T>` 在多个线程之间共享一个值。我们将启动 10 个线程，让每个线程将计数器的值增加 1，这样计数器的值就会从 0 增加到 10。清单 16-13 中的示例将会产生编译错误，我们可以利用这个错误来了解如何使用 `Mutex<T>`，以及 Rust 如何帮助我们正确地使用它。

**清单 16-13:** *src/main.rs* — 十个线程，每个线程都会递增一个由 `Mutex<T>` 保护的计数器

```rust,ignore,does_not_compile
use std::sync::Mutex;
use std::thread;

fn main() {
    let counter = Mutex::new(0);
    let mut handles = vec![];

    for _ in 0..10 {
        let handle = thread::spawn(move || {
            let mut num = counter.lock().unwrap();

            *num += 1;
        });
        handles.push(handle);
    }

    for handle in handles {
        handle.join().unwrap();
    }

    println!("Result: {}", *counter.lock().unwrap());
}

```

我们创建了一个 `counter` 变量来存放 `i32` 的值，就像在 Listing 16-12 中做的那样。接下来，我们通过遍历一系列数字来创建 10 个线程。我们使用 `thread::spawn`，并给所有线程相同的闭包：一个将计数器移动到线程内的闭包，通过调用 `lock` 方法来获取 `Mutex<T>` 的锁，然后向互斥量中的值加 1。当一个线程完成其闭包的运行时， `num` 就会超出作用域并释放锁，以便另一个线程可以获取该锁。

在主线程中，我们收集所有的join句柄。然后，就像在 Listing 16-2 中做的那样，我们对每个句柄调用 `join`，以确保所有线程都完成执行。此时，主线程将获取锁，并打印出这个程序的结果。

我们之前暗示过，这个例子无法编译。现在让我们来了解一下原因吧！

```console
$ cargo run
   Compiling shared-state v0.1.0 (file:///projects/shared-state)
error[E0382]: borrow of moved value: `counter`
  --> src/main.rs:21:29
   |
 5 |     let counter = Mutex::new(0);
   |         ------- move occurs because `counter` has type `std::sync::Mutex<i32>`, which does not implement the `Copy` trait
...
 8 |     for _ in 0..10 {
   |     -------------- inside of this loop
 9 |         let handle = thread::spawn(move || {
   |                                    ------- value moved into closure here, in previous iteration of loop
...
21 |     println!("Result: {}", *counter.lock().unwrap());
   |                             ^^^^^^^ value borrowed here after move
   |
help: consider moving the expression out of the loop so it is only moved once
   |
 8 ~     let mut value = counter.lock();
 9 ~     for _ in 0..10 {
10 |         let handle = thread::spawn(move || {
11 ~             let mut num = value.unwrap();
   |

For more information about this error, try `rustc --explain E0382`.
error: could not compile `shared-state` (bin "shared-state") due to 1 previous error

```

错误信息表明，`counter`这个值在循环的上一轮迭代中被移动了。Rust告诉我们，不能将lock `counter`的所有权分配给多个线程。让我们使用在第15章中讨论的多重所有权方法来修复编译器的错误。

#### 多线程下的多重所有权

在第十五章中，我们通过使用智能指针`Rc<T>`为多个所有者分配了一个值，从而创建了一个引用计数型值。在这里我们也这样做，看看会发生什么。在 Listing 16-14 中，我们将 `Mutex<T>` 包裹在 `Rc<T>` 中，并在将所有权移交给线程之前，先克隆一下 `Rc<T>`。

**列表 16-14:** *src/main.rs* — 尝试使用 `Rc<T>` 来允许多个线程拥有 `Mutex<T>`

```rust,ignore,does_not_compile
use std::rc::Rc;
use std::sync::Mutex;
use std::thread;

fn main() {
    let counter = Rc::new(Mutex::new(0));
    let mut handles = vec![];

    for _ in 0..10 {
        let counter = Rc::clone(&counter);
        let handle = thread::spawn(move || {
            let mut num = counter.lock().unwrap();

            *num += 1;
        });
        handles.push(handle);
    }

    for handle in handles {
        handle.join().unwrap();
    }

    println!("Result: {}", *counter.lock().unwrap());
}

```

再次进行编译后，我们得到了不同的错误！编译器教会了我们很多东西：

```console
$ cargo run
   Compiling shared-state v0.1.0 (file:///projects/shared-state)
error[E0277]: `Rc<std::sync::Mutex<i32>>` cannot be sent between threads safely
  --> src/main.rs:11:36
   |
11 |           let handle = thread::spawn(move || {
   |                        ------------- ^------
   |                        |             |
   |  ______________________|_____________within this `{closure@src/main.rs:11:36: 11:43}`
   | |                      |
   | |                      required by a bound introduced by this call
12 | |             let mut num = counter.lock().unwrap();
13 | |
14 | |             *num += 1;
15 | |         });
   | |_________^ `Rc<std::sync::Mutex<i32>>` cannot be sent between threads safely
   |
   = help: within `{closure@src/main.rs:11:36: 11:43}`, the trait `Send` is not implemented for `Rc<std::sync::Mutex<i32>>`
note: required because it's used within this closure
  --> src/main.rs:11:36
   |
11 |         let handle = thread::spawn(move || {
   |                                    ^^^^^^^
note: required by a bound in `spawn`
  --> /rustc/1159e78c4747b02ef996e55082b704c09b970588/library/std/src/thread/mod.rs:723:1

For more information about this error, try `rustc --explain E0277`.
error: could not compile `shared-state` (bin "shared-state") due to 1 previous error

```

哇，那个错误信息真长！下面是最重要的部分：
`` `Rc<Mutex<i32>>` cannot be sent between threads safely ``. The compiler is
also telling us the reason why: `` the trait `Send` is not implemented for
`Rc<Mutex<i32>>` ``. We’ll talk about `Send` in the next section: It’s one of
the traits that ensures that the types we use with threads are meant for use in
concurrent situations.

Unfortunately, `Rc<T>` is not safe to share across threads. When `Rc<T>`
manages the reference count, it adds to the count for each call to `clone` and
subtracts from the count when each clone is dropped. But it doesn’t use any
concurrency primitives to make sure that changes to the count can’t be
interrupted by another thread. This could lead to wrong counts—subtle bugs that
could in turn lead to memory leaks or a value being dropped before we’re done
with it. What we need is a type that is exactly like `Rc<T>`, but that makes
changes to the reference count in a thread-safe way.

#### Atomic Reference Counting with `Arc<T>`

Fortunately, `Arc<T>` _is_ a type like `Rc<T>` that is safe to use in
concurrent situations. The _a_ stands for _atomic_, meaning it’s an _atomically
reference-counted_ type. Atomics are an additional kind of concurrency
primitive that we won’t cover in detail here: See the standard library
documentation for [`std::sync::atomic`][atomic]<!-- ignore --> for more
details. At this point, you just need to know that atomics work like primitive
types but are safe to share across threads.

You might then wonder why all primitive types aren’t atomic and why standard
library types aren’t implemented to use `Arc<T>` by default. The reason is that
thread safety comes with a performance penalty that you only want to pay when
you really need to. If you’re just performing operations on values within a
single thread, your code can run faster if it doesn’t have to enforce the
guarantees atomics provide.

Let’s return to our example: `Arc<T>` and `Rc<T>` have the same API, so we fix
our program by changing the `use` line, the call to `new`, and the call to
`clone`. The code in Listing 16-15 will finally compile and run.

**Listing 16-15:** *src/main.rs* — Using an `Arc<T>` to wrap the `Mutex<T>` to be able to share ownership across multiple threads

```rust
use std::sync::{Arc, Mutex};
use std::thread;

fn main() {
    let counter = Arc::new(Mutex::new(0));
    let mut handles = vec![];

    for _ in 0..10 {
        let counter = Arc::clone(&counter);
        let handle = thread::spawn(move || {
            let mut num = counter.lock().unwrap();

            *num += 1;
        });
        handles.push(handle);
    }

    for handle in handles {
        handle.join().unwrap();
    }

    println!("Result: {}", *counter.lock().unwrap());
}

```

This code will print the following:

<!-- Not extracting output because changes to this output aren't significant;
the changes are likely to be due to the threads running differently rather than
changes in the compiler -->

```text
Result: 10
```

We did it! We counted from 0 to 10, which may not seem very impressive, but it
did teach us a lot about `Mutex<T>` and thread safety. You could also use this
program’s structure to do more complicated operations than just incrementing a
counter. Using this strategy, you can divide a calculation into independent
parts, split those parts across threads, and then use a `Mutex<T>` to have each
thread update the final result with its part.

Note that if you are doing simple numerical operations, there are types simpler
than `Mutex<T>` types provided by the [`std::sync::atomic` module of the
standard library][atomic]<!-- ignore -->. These types provide safe, concurrent,
atomic access to primitive types. We chose to use `Mutex<T>` with a primitive
type for this example so that we could concentrate on how `Mutex<T>` works.

<!-- Old headings. Do not remove or links may break. -->

<a id="similarities-between-refcelltrct-and-mutextarct"></a>

### Comparing `RefCell<T>`/`Rc<T>` and `Mutex<T>`/`Arc<T>`

You might have noticed that `counter` is immutable but that we could get a
mutable reference to the value inside it; this means `Mutex<T>` provides
interior mutability, as the `Cell` family does. In the same way we used
`RefCell<T>` in Chapter 15 to allow us to mutate contents inside an `Rc<T>`, we
use `Mutex<T>` to mutate contents inside an `Arc<T>`.

Another detail to note is that Rust can’t protect you from all kinds of logic
errors when you use `Mutex<T>`. Recall from Chapter 15 that using `Rc<T>` came
with the risk of creating reference cycles, where two `Rc<T>` values refer to
each other, causing memory leaks. Similarly, `Mutex<T>` comes with the risk of
creating _deadlocks_. These occur when an operation needs to lock two resources
and two threads have each acquired one of the locks, causing them to wait for
each other forever. If you’re interested in deadlocks, try creating a Rust
program that has a deadlock; then, research deadlock mitigation strategies for
mutexes in any language and have a go at implementing them in Rust. The
standard library API documentation for `Mutex<T>` and `MutexGuard` offers
useful information.

We’ll round out this chapter by talking about the `Send` and `Sync` 这些特性，以及我们如何将它们与自定义类型一起使用。

[atomic]: ../std/sync/atomic/index.html
