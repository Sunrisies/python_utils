
<!-- Old headings. Do not remove or links may break. -->

<a id="yielding"></a>

### 将控制权交给运行时

回想一下在 [“Our First Async Program”][async-program]<!-- ignore --> 这一节中提到的内容：在每一个等待点，Rust会让运行时有机会暂停任务，并切换到另一个任务，如果等待的未来结果尚未准备好。反之亦然：Rust只会暂停异步块，并在等待点将控制权返回给运行时。等待点之间的所有操作都是同步的。

这意味着，如果你在异步块中执行大量工作，而该异步块中没有使用 `await` 关键字，那么那个异步任务将会阻塞其他异步任务的执行。有时，这种情况被称为一个异步任务“饿死”其他异步任务。在某些情况下，这可能不是什么大问题。然而，如果你正在执行一些耗时的设置操作或需要长时间运行的任务，或者如果你有一个需要持续执行特定任务的异步任务，那么你就需要考虑何时以及将控制权交还给运行时。

让我们模拟一个长时间运行的操作，以说明饥饿问题，然后探讨如何解决这个问题。列表17-14中介绍了一个 `slow` 函数。

<Listing number="17-14" caption="Using `thread::sleep` to simulate slow operations" file-name="src/main.rs">

```rust
fn slow(name: &str, ms: u64) {
    thread::sleep(Duration::from_millis(ms));
    println!("'{name}' ran for {ms}ms");
}

```

</Listing>

这段代码使用 `std::thread::sleep` 而不是 `trpl::sleep`，这样调用 `slow` 会阻塞当前线程若干毫秒。我们可以使用 `slow` 来代表那些既耗时又会阻塞的实际操作。

在 Listing 17-15 中，我们使用 `slow` 来模拟在一对未来任务中执行这种计算密集型工作。

<Listing number="17-15" caption="Calling the `slow` function to simulate slow operations" file-name="src/main.rs">

```rust
        let a = async {
            println!("'a' started.");
            slow("a", 30);
            slow("a", 10);
            slow("a", 20);
            trpl::sleep(Duration::from_millis(50)).await;
            println!("'a' finished.");
        };

        let b = async {
            println!("'b' started.");
            slow("b", 75);
            slow("b", 10);
            slow("b", 15);
            slow("b", 350);
            trpl::sleep(Duration::from_millis(50)).await;
            println!("'b' finished.");
        };

        trpl::select(a, b).await;

```

</Listing>

每个“未来”操作在执行一系列缓慢的操作之后，才会将控制权返回给运行时系统。如果你运行这段代码，将会看到这样的输出：

<!-- manual-regeneration
cd listings/ch17-async-await/listing-17-15/
cargo run
copy just the output
-->

```text
'a' started.
'a' ran for 30ms
'a' ran for 10ms
'a' ran for 20ms
'b' started.
'b' ran for 75ms
'b' ran for 10ms
'b' ran for 15ms
'b' ran for 350ms
'a' finished.
```

正如清单17-5所示，我们使用 `trpl::select` 来竞争获取两个URL的未来，而 `select` 在 `a` 完成后立即执行。不过，两个未来任务对 `slow` 的调用之间并没有进行任何交错。 `a` 未来任务会一直执行，直到等待 `trpl::sleep` 的调用；然后 `b` 未来任务会一直执行，直到等待自己的 `trpl::sleep` 调用；最后 `a` 未来任务才会完成。为了让这两个未来任务能够在它们缓慢的任务之间取得进展，我们需要等待点，这样我们就可以将控制权交还给运行时。这意味着我们需要某种可以等待的对象！

在 Listing 17-15 中，我们已经可以看到这种切换现象：如果我们移除 `a` 语句末尾的 `trpl::sleep`，那么 `a` 的后续操作将能够正常完成，而 `b` 则根本不会被执行。让我们尝试使用 `trpl::sleep` 函数作为起点，让操作在进展过程中自动停止，如 Listing 17-16 所示。

<Listing number="17-16" caption="Using `trpl::sleep` to let operations switch off making progress" file-name="src/main.rs">

```rust
        let one_ms = Duration::from_millis(1);

        let a = async {
            println!("'a' started.");
            slow("a", 30);
            trpl::sleep(one_ms).await;
            slow("a", 10);
            trpl::sleep(one_ms).await;
            slow("a", 20);
            trpl::sleep(one_ms).await;
            println!("'a' finished.");
        };

        let b = async {
            println!("'b' started.");
            slow("b", 75);
            trpl::sleep(one_ms).await;
            slow("b", 10);
            trpl::sleep(one_ms).await;
            slow("b", 15);
            trpl::sleep(one_ms).await;
            slow("b", 350);
            trpl::sleep(one_ms).await;
            println!("'b' finished.");
        };

```

</Listing>

我们添加了 `trpl::sleep` 调用，并在每次调用之间加入了带有 await 点的 `slow`。现在，这两个未来的执行结果被交错处理了。

<!-- manual-regeneration
cd listings/ch17-async-await/listing-17-16
cargo run
copy just the output
-->

```text
'a' started.
'a' ran for 30ms
'b' started.
'b' ran for 75ms
'a' ran for 10ms
'b' ran for 10ms
'a' ran for 20ms
'b' ran for 15ms
'a' finished.
```

在将控制权交给 `b` 之前， `a` 仍然会运行一段时间，因为它在调用 `trpl::sleep` 之前会先调用 `slow`。不过，一旦其中一个函数达到等待点，两个未来函数就会互相交换控制权。在这种情况下，我们在每次调用 `slow` 之后都会执行这一操作，但我们也可以以最合理的方式将工作分解开来。

不过，我们其实并不想在这里“睡觉”：我们希望尽可能快地取得进展。我们只需要将控制权交还给运行时。我们可以直接使用 `trpl::yield_now` 这个函数来实现这一点。在 Listing 17-17 中，我们将所有 `trpl::sleep` 的调用都替换成了 `trpl::yield_now`。

<Listing number="17-17" caption="Using `yield_now` to let operations switch off making progress" file-name="src/main.rs">

```rust
        let a = async {
            println!("'a' started.");
            slow("a", 30);
            trpl::yield_now().await;
            slow("a", 10);
            trpl::yield_now().await;
            slow("a", 20);
            trpl::yield_now().await;
            println!("'a' finished.");
        };

        let b = async {
            println!("'b' started.");
            slow("b", 75);
            trpl::yield_now().await;
            slow("b", 10);
            trpl::yield_now().await;
            slow("b", 15);
            trpl::yield_now().await;
            slow("b", 350);
            trpl::yield_now().await;
            println!("'b' finished.");
        };

```

</Listing>

这段代码在表达实际意图方面更加清晰，而且比使用 `sleep` 要快得多。因为像 `sleep` 所使用的计时器通常存在精度限制。例如，我们使用的 `sleep` 版本总是会至少休眠一毫秒，即使我们给它传递一个一纳秒的 `Duration`。再次强调，现代计算机非常快速：它们可以在一毫秒内完成大量操作！

这意味着，即使对于计算密集型任务来说，异步功能也是有用的，这取决于程序还在执行哪些其他任务。因为异步功能为构建程序不同部分之间的关系提供了一种有用的工具（但会带来异步状态机带来的额外开销）。这是一种协作式多任务处理机制，其中每个“未来”都有能力决定何时通过`await`点移交控制权。因此，每个“未来”也有责任避免长时间阻塞。在一些基于Rust的嵌入式操作系统中，这种多任务处理方式是**唯一**的方式！

在现实世界的代码中，通常不会在每一行代码中都交替使用函数调用和`await`指令。虽然以这种方式让程序暂停控制相对成本较低，但并非完全免费。在许多情况下，试图将计算密集型任务拆分成多个部分可能会显著降低其执行速度。因此，有时为了提升整体性能，让某个操作暂时阻塞也是可行的。务必测量一下，了解代码中的实际性能瓶颈是什么。不过，如果你发现大量操作实际上是串行进行的，而原本期望它们是并发执行的，那么理解底层动态机制就非常重要了！

### 构建我们自己的异步抽象层

我们还可以将不同的未来函数组合在一起，以创建新的模式。例如，我们可以使用已经拥有的异步构建模块来构建一个 `timeout` 函数。完成之后，结果将成为一个新的构建模块，我们可以用它来创建更多的异步抽象结构。

列表17-18展示了在较慢的未来情况下，我们预期这个 `timeout` 会如何运作。

<Listing number="17-18" caption="Using our imagined `timeout` to run a slow operation with a time limit" file-name="src/main.rs">

```rust,ignore,does_not_compile
        let slow = async {
            trpl::sleep(Duration::from_secs(5)).await;
            "Finally finished"
        };

        match timeout(slow, Duration::from_secs(2)).await {
            Ok(message) => println!("Succeeded with '{message}'"),
            Err(duration) => {
                println!("Failed after {} seconds", duration.as_secs())
            }
        }

```

</Listing>

让我们来实现这个功能吧！首先，我们来思考一下 `timeout` 的 API 设计：

- 它必须是一个异步函数，这样我们才能对其进行等待操作。
- 它的第一个参数应该是一个未来值，用于执行操作。我们可以使这个参数具有通用性，以便它能够处理任何未来值。
- 它的第二个参数将表示最大等待时间。如果我们使用 `Duration`，那么就可以很容易地将这个时间值传递给 `trpl::sleep`。
- 它应该返回一个 `Result`。如果未来值成功完成，那么 `Result` 将包含由未来值产生的数值。如果超时时间先到，那么 `Result` 将包含超时等待的时间长度。

列表17-19展示了这一声明。

<!-- This is not tested because it intentionally does not compile. -->

<Listing number="17-19" caption="Defining the signature of `timeout`" file-name="src/main.rs">

```rust,ignore,does_not_compile
async fn timeout<F: Future>(
    future_to_try: F,
    max_time: Duration,
) -> Result<F::Output, Duration> {
    // Here is where our implementation will go!
}

```

</Listing>

这满足了我们对这些类型的需求。现在让我们考虑一下我们需要的_行为_：我们希望将传入的未来值与持续时间进行比较。我们可以使用`trpl::sleep`来从持续时间中创建一个计时器未来，然后使用`trpl::select`来运行这个计时器，并将调用者传入的未来值作为参数传递给它。

在 Listing 17-20 中，我们通过匹配 await 的结果来实现 `timeout`。

<Listing number="17-20" caption="Defining `timeout` with `select` and `sleep`" file-name="src/main.rs">

```rust
use trpl::Either;

// --snip--

async fn timeout<F: Future>(
    future_to_try: F,
    max_time: Duration,
) -> Result<F::Output, Duration> {
    match trpl::select(future_to_try, trpl::sleep(max_time)).await {
        Either::Left(output) => Ok(output),
        Either::Right(_) => Err(max_time),
    }
}

```

</Listing>

`trpl::select` 的实现并不公平：它总是按照参数传递的顺序来轮询参数（而其他 `select` 的实现则会随机选择先轮询哪个参数）。因此，我们应该先向 `future_to_try` 传递 `select`，这样即使 `max_time` 的持续时间非常短，它也有机会完成任务。如果 `future_to_try` 先完成，那么 `select` 将会返回 `Left`，同时附带 `future_to_try` 的输出结果。如果 `timer` 先完成，那么 `select` 将会返回 `Right`，同时附带计时器的输出结果 `()`。

如果 `future_to_try` 成功执行，并且我们得到了 `Left(output)`，那么我们将返回 `Ok(output)`。如果 instead，睡眠计时器到期了，并且我们得到了 `Right(())`，那么我们将忽略 `()` 以及 `_`，而是返回 `Err(max_time)`。

就这样，我们实现了由两个异步辅助函数构成的 `timeout` 功能。如果我们运行这段代码，它会在超时后打印出失败模式：

```text
Failed after 2 seconds
```

因为未来操作可以与其他未来操作组合在一起，所以你可以使用一些更简单的异步组件来构建非常强大的工具。例如，你可以采用同样的方法将超时机制与重试机制结合起来，进而将这些机制应用于网络调用等操作中（如清单17-5所示）。

在实践中，你通常会直接使用 `async` 和 `await`，并借助 `select` 这样的函数以及 `join!` 这样的宏来控制最外层未来事件的执行方式。

我们已经看到了多种同时处理多个未来时态的方法。接下来，我们将探讨如何利用 _流_ 来按时间顺序处理多个未来时态。

[async-program]: ch17-01-futures-and-syntax.html#our-first-async-program
