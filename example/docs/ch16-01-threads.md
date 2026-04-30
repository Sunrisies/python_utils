## 使用线程同时运行代码

在大多数当前的操作系统中，执行程序的代码会在一个进程中运行，而操作系统会同时管理多个进程。在一个程序中，也可以有同时运行的独立部分。这些独立部分所运行的功能被称为“线程”。例如，一个Web服务器可以拥有多个线程，从而同时响应多个请求。

在程序中将计算任务拆分成多个线程来同时运行多个任务，可以提高性能，但这也会增加复杂性。由于线程可以同时运行，因此无法保证不同线程上的代码部分会以特定的顺序执行。这可能会导致一些问题，例如：

- 竞争条件，即多个线程以不一致的顺序访问数据或资源
- 死锁，即两个线程相互等待，导致两个线程都无法继续执行
- 仅在某些特定情况下发生的错误，这些错误很难重现，也难以可靠地修复

Rust试图减轻使用线程带来的负面影响，但在多线程环境下编程仍然需要仔细考虑，并且需要一种与单线程程序不同的代码结构。

编程语言以几种不同的方式实现线程，许多操作系统还提供了API，让编程语言可以调用这些API来创建新的线程。Rust标准库采用了一种_1:1_的线程实现模型，即每个语言线程对应一个操作系统线程。还有一些库采用了其他线程实现模型，这些模型在权衡方面与1:1模型有所不同。（Rust的异步系统，我们将在下一章中介绍，也提供了一种实现并发的方法。）

### 使用 `spawn` 创建新线程

要创建一个新的线程，我们调用 `thread::spawn` 函数，并传递一个闭包（我们在第13章中讨论过闭包），该闭包包含我们希望在新线程中运行的代码。清单16-1中的示例从主线程打印一些文本，同时从新线程打印其他文本。

**清单 16-1:** *src/main.rs* — 创建一个新线程来打印内容，同时主线程继续打印其他内容

```rust
use std::thread;
use std::time::Duration;

fn main() {
    thread::spawn(|| {
        for i in 1..10 {
            println!("hi number {i} from the spawned thread!");
            thread::sleep(Duration::from_millis(1));
        }
    });

    for i in 1..5 {
        println!("hi number {i} from the main thread!");
        thread::sleep(Duration::from_millis(1));
    }
}

```

请注意，当Rust程序的主线程完成时，所有被派生的线程都会被关闭，无论它们是否已经运行完毕。这个程序的输出可能会每次都有所不同，但看起来会与以下示例类似：

<!-- Not extracting output because changes to this output aren't significant;
the changes are likely to be due to the threads running differently rather than
changes in the compiler -->

```text
hi number 1 from the main thread!
hi number 1 from the spawned thread!
hi number 2 from the main thread!
hi number 2 from the spawned thread!
hi number 3 from the main thread!
hi number 3 from the spawned thread!
hi number 4 from the main thread!
hi number 4 from the spawned thread!
hi number 5 from the spawned thread!
```

调用 `thread::sleep` 会迫使一个线程在短时间内停止执行，从而让另一个线程有机会运行。这些线程通常会轮流执行，但这并不保证一定会如此——这取决于你的操作系统如何调度线程。在这次运行中，主线程首先打印出了内容，尽管从子线程中执行的打印语句在代码中出现得更早。即使我们告诉子线程一直执行到 `i` 条件满足时再继续执行，但实际上它只执行到了 `5` 条件满足时，之后主线程就停止了执行。

如果您运行这段代码时，只看到主线程的输出，或者看不到任何重叠现象，那么请尝试增加各个范围中的数值，从而为操作系统提供更多机会来在线程之间切换。

<!-- Old headings. Do not remove or links may break. -->

<a id="waiting-for-all-threads-to-finish-using-join-handles"></a>

### 等待所有线程完成

在 Listing 16-1 中的代码，由于主线程的终止，大多数情况下都会提前终止子线程的运行。此外，由于无法保证线程运行的顺序，我们也无法保证子线程一定会有机会运行！

我们可以通过将 `thread::spawn` 的返回值存储在一个变量中来解决子线程无法运行或提前终止的问题。 `thread::spawn` 的返回类型是 `JoinHandle<T>`。 `JoinHandle<T>` 是一个被拥有的值，当我们调用 `join` 方法时，会等待其子线程完成执行。清单 16-2 展示了如何使用清单 16-1 中创建的线程的 `JoinHandle<T>`，以及如何调用 `join` 来确保子线程在 `main` 退出之前完成执行。

**清单 16-2:** *src/main.rs* — 将 `thread::spawn` 中的内容保存到 `JoinHandle<T>` 中，以确保线程能够完整执行。

```rust
use std::thread;
use std::time::Duration;

fn main() {
    let handle = thread::spawn(|| {
        for i in 1..10 {
            println!("hi number {i} from the spawned thread!");
            thread::sleep(Duration::from_millis(1));
        }
    });

    for i in 1..5 {
        println!("hi number {i} from the main thread!");
        thread::sleep(Duration::from_millis(1));
    }

    handle.join().unwrap();
}

```

在句柄上调用 `join` 会阻塞当前正在运行的线程，直到该句柄所代表的线程终止。阻塞一个线程意味着该线程无法执行任务或退出。由于我们将 `join` 的调用放在了主线程的 `for` 循环之后，因此运行 Listing 16-2 应该会产生类似以下的输出：

<!-- Not extracting output because changes to this output aren't significant;
the changes are likely to be due to the threads running differently rather than
changes in the compiler -->

```text
hi number 1 from the main thread!
hi number 2 from the main thread!
hi number 1 from the spawned thread!
hi number 3 from the main thread!
hi number 2 from the spawned thread!
hi number 4 from the main thread!
hi number 3 from the spawned thread!
hi number 4 from the spawned thread!
hi number 5 from the spawned thread!
hi number 6 from the spawned thread!
hi number 7 from the spawned thread!
hi number 8 from the spawned thread!
hi number 9 from the spawned thread!
```

这两个线程继续交替运行，但由于调用了 `handle.join()`，主线程会等待，直到子线程完成工作之后才会结束。

但是，让我们看看当我们将 `handle.join()` 放在 `for` 循环之前的 `main` 中时会发生什么，就像这样：

<Listing file-name="src/main.rs">

```rust
use std::thread;
use std::time::Duration;

fn main() {
    let handle = thread::spawn(|| {
        for i in 1..10 {
            println!("hi number {i} from the spawned thread!");
            thread::sleep(Duration::from_millis(1));
        }
    });

    handle.join().unwrap();

    for i in 1..5 {
        println!("hi number {i} from the main thread!");
        thread::sleep(Duration::from_millis(1));
    }
}

```

</Listing>

主线程会等待被创建的线程完成，然后执行其`for`循环，因此输出将不再交错，如下所示：

<!-- Not extracting output because changes to this output aren't significant;
the changes are likely to be due to the threads running differently rather than
changes in the compiler -->

```text
hi number 1 from the spawned thread!
hi number 2 from the spawned thread!
hi number 3 from the spawned thread!
hi number 4 from the spawned thread!
hi number 5 from the spawned thread!
hi number 6 from the spawned thread!
hi number 7 from the spawned thread!
hi number 8 from the spawned thread!
hi number 9 from the spawned thread!
hi number 1 from the main thread!
hi number 2 from the main thread!
hi number 3 from the main thread!
hi number 4 from the main thread!
```

一些细节，比如 `join` 被称为什么，会影响你的线程是否能够同时运行。

### 在多线程中使用 `move` 闭包

我们通常会使用 `move` 这个关键字来指代传递给 `thread::spawn` 的闭包。因为这样，闭包就会拥有从环境中获取的值的所有权，从而将这些值的所有权从一个线程转移到另一个线程。在第十三章的 [“Capturing References or Moving Ownership”][capture]<!-- ignore
--> 中，我们讨论了 `move` 在闭包上下文中的使用。现在，我们将更专注于 `move` 和 `thread::spawn` 之间的交互关系。

请注意，在 Listing 16-1 中，我们传递给 `thread::spawn` 的闭包没有任何参数：我们在子线程的代码中并没有使用主线程的任何数据。为了在子线程中使用主线程的数据，子线程中的闭包必须捕获所需的数值。Listing 16-3 展示了在主线程中创建一个向量并在子线程中使用的尝试。然而，这种方法目前是行不通的，您很快就会看到原因。

**清单 16-3:** *src/main.rs* — 尝试在另一个线程中使用由主线程创建的向量

```rust,ignore,does_not_compile
use std::thread;

fn main() {
    let v = vec![1, 2, 3];

    let handle = thread::spawn(|| {
        println!("Here's a vector: {v:?}");
    });

    handle.join().unwrap();
}

```

这个闭包使用了 `v`，因此它会捕获 `v` 并将其作为闭包的环境的一部分。由于 `thread::spawn` 在新的线程中执行这个闭包，我们应该能够在那个新线程中访问 `v`。但是，当我们编译这个例子时，会出现以下错误：

```console
$ cargo run
   Compiling threads v0.1.0 (file:///projects/threads)
error[E0373]: closure may outlive the current function, but it borrows `v`, which is owned by the current function
 --> src/main.rs:6:32
  |
6 |     let handle = thread::spawn(|| {
  |                                ^^ may outlive borrowed value `v`
7 |         println!("Here's a vector: {v:?}");
  |                                     - `v` is borrowed here
  |
note: function requires argument type to outlive `'static`
 --> src/main.rs:6:18
  |
6 |       let handle = thread::spawn(|| {
  |  __________________^
7 | |         println!("Here's a vector: {v:?}");
8 | |     });
  | |______^
help: to force the closure to take ownership of `v` (and any other referenced variables), use the `move` keyword
  |
6 |     let handle = thread::spawn(move || {
  |                                ++++

For more information about this error, try `rustc --explain E0373`.
error: could not compile `threads` (bin "threads") due to 1 previous error

```

Rust会推断出如何捕获 `v`，而因为 `println!` 只需要一个引用就能指向 `v`，所以闭包会尝试借用 `v`。然而，存在一个问题：Rust无法知道新创建的线程会运行多久，因此它无法确定对 `v` 的引用是否始终有效。

列表16-4提供了一个更有可能包含 `v` 的情境，但该引用将不会生效。

**清单 16-4:** *src/main.rs* — 一个线程，其中包含了一个闭包，该闭包试图从主线程捕获对 `v` 的引用，而主线程则释放了 `v`。

```rust,ignore,does_not_compile
use std::thread;

fn main() {
    let v = vec![1, 2, 3];

    let handle = thread::spawn(|| {
        println!("Here's a vector: {v:?}");
    });

    drop(v); // oh no!

    handle.join().unwrap();
}

```

如果Rust允许我们运行这段代码，那么生成的线程很可能会立即被放到后台，根本不会执行。生成的线程内部有一个对 `v` 的引用，但是主线程立即丢弃了 `v`，并使用了我们在第15章中讨论过的 `drop` 函数。因此，当生成的线程开始执行时， `v` 就不再有效了，所以对其的引用也就无效了。糟糕！

为了修复清单 16-3 中的编译器错误，我们可以使用错误信息的提示来解决问题。

<!-- manual-regeneration
after automatic regeneration, look at listings/ch16-fearless-concurrency/listing-16-03/output.txt and copy the relevant part
-->

```text
help: to force the closure to take ownership of `v` (and any other referenced variables), use the `move` keyword
  |
6 |     let handle = thread::spawn(move || {
  |                                ++++
```

通过在闭包前添加 `move` 关键字，我们可以强制闭包自行负责其所使用的值，而不是让 Rust 自行推断应该借用这些值。如清单 16-5 所示，对清单 16-3 所做的修改将会按照我们的预期进行编译和运行。

**清单 16-5:** *src/main.rs* — 使用 `move` 关键字强制闭包拥有其所使用的值的所有权

```rust
use std::thread;

fn main() {
    let v = vec![1, 2, 3];

    let handle = thread::spawn(move || {
        println!("Here's a vector: {v:?}");
    });

    handle.join().unwrap();
}

```

我们可能会想要尝试同样的方法来修复清单 16-4 中的代码，其中主线程通过 `move` 闭包来调用 `drop`。然而，这种修复方法是不可行的，因为清单 16-4 的尝试存在另一个不允许的原因。如果我们向闭包中添加 `move`，那么 `v` 就会进入闭包的环境，而我们在主线程中就无法再调用 `drop` 了。相反，我们会遇到编译错误。

```console
$ cargo run
   Compiling threads v0.1.0 (file:///projects/threads)
error[E0382]: use of moved value: `v`
  --> src/main.rs:10:10
   |
 4 |     let v = vec![1, 2, 3];
   |         - move occurs because `v` has type `Vec<i32>`, which does not implement the `Copy` trait
 5 |
 6 |     let handle = thread::spawn(move || {
   |                                ------- value moved into closure here
 7 |         println!("Here's a vector: {v:?}");
   |                                     - variable moved due to use in closure
...
10 |     drop(v); // oh no!
   |          ^ value used here after move
   |
help: consider cloning the value before moving it into the closure
   |
 6 ~     let value = v.clone();
 7 ~     let handle = thread::spawn(move || {
 8 ~         println!("Here's a vector: {value:?}");
   |

For more information about this error, try `rustc --explain E0382`.
error: could not compile `threads` (bin "threads") due to 1 previous error

```

Rust的所有权规则再次帮了我们大忙！由于Listing 16-3中的代码出现了错误，因为Rust采用了保守的策略，只为线程借用 `v`，这意味着主线程理论上可以使得子线程的引用失效。通过告诉Rust将 `v` 的所有权移交给子线程，我们向Rust保证主线程将不再使用 `v`。如果我们以同样的方式修改Listing 16-4，那么在主线程中尝试使用 `v` 时，就会违反所有权规则。而 `move` 关键字则覆盖了Rust默认的保守借用策略，它不允许我们违反所有权规则。

既然我们已经了解了线程是什么以及线程API提供了哪些方法，接下来让我们看看在哪些情况下可以使用线程。

[capture]: ch13-01-closures.html#capturing-references-or-moving-ownership
