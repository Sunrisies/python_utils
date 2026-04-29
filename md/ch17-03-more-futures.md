<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="yielding"></a>

### 将控制权交给运行时

请回想一下在[“我们的第一个异步程序”][async-program]<!-- 忽略 -->这一节的内容。在那里提到，在每个等待的时刻，Rust会让运行时有机会暂停任务，并在等待的未来结果未准备好时切换到其他任务。反之亦然：Rust只会暂停异步代码块，并在等待时刻将控制权返回给运行时。等待时刻之间的所有操作都是同步的。

这意味着，如果你在异步块中执行大量操作，而没有任何等待点，那么那个未来的任务将会阻塞其他任务的执行。有时，这种情况被称为一个未来“饿死”了其他未来任务。在某些情况下，这可能不是什么大问题。然而，如果你正在执行一些昂贵的设置操作或需要长时间运行的任务，或者如果你有一个需要无限期地执行特定任务的未来任务，那么你就需要考虑何时以及在哪里将控制权交还给运行时系统。

让我们模拟一个长时间运行的操作，以说明饥饿问题，然后探讨如何解决这个问题。列表17-14中介绍了一个名为`slow`的函数。

<List numbering="17-14" caption="使用 `thread::sleep` 来模拟慢速操作" file-name="src/main.rs">

```rust
{{#rustdoc_include ../listings/ch17-async-await/listing-17-14/src/main.rs:slow}}
```

</清单>

这段代码使用`std::thread::sleep`代替`trpl::sleep`，这样调用`slow`就会在当前线程上阻塞一段时间。我们可以使用`slow`来替代那些既耗时又会导致阻塞的实际操作。

在清单17-15中，我们使用`slow`来模拟使用一对未来操作来执行这种计算密集型任务。

<List numbering="17-15" caption="调用`slow`函数以模拟慢速操作" file-name="src/main.rs">

```rust
{{#rustdoc_include ../listings/ch17-async-await/listing-17-15/src/main.rs:slow-futures}}
```

</清单>

每个“未来”操作在执行一系列缓慢的操作之后，才会将控制权返回给运行时系统。如果你运行这段代码，将会看到这样的输出：

<!-- 手动重新生成
cd listings/ch17-async-await/listing-17-15/
cargo run
仅复制输出内容
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

与清单17-5中的情况类似，我们使用`trpl::select`来竞争获取两个URL的future操作。在这种情况下，一旦`a`完成，`select`也会立即完成其任务。不过，在两个future中调用`slow`之间并没有进行任何交错处理。`a`的future会一直执行其所有操作，直到等待`trpl::sleep`的调用；然后`b`的future会继续执行其所有操作，直到等待自己的`trpl::sleep`调用。`a` 未来任务已经完成。为了让这两个未来任务能够在它们的慢任务之间继续推进，我们需要“等待点”，这样我们才能将控制权交还给运行时系统。这意味着我们需要某种可以等待的对象！

我们已经可以在清单17-15中看到这种切换现象：如果我们移除`a`后面的`trpl::sleep`，那么`a`的后续操作将能够在不运行`b`的情况下完成。让我们尝试使用`trpl::sleep`函数来作为让操作停止并继续前进的起点，如清单17-16所示。

<List numbering="17-16" caption="使用 `trpl::sleep` 让操作在进展过程中可以暂停" file-name="src/main.rs">

```rust
{{#rustdoc_include ../listings/ch17-async-await/listing-17-16/src/main.rs:here}}
```

</清单>

我们添加了`trpl::sleep`的调用，并在每个调用之间都包含了await操作，这些调用与`slow`相关联。现在，这两个未来协程的工作是相互交织的。

<!-- 手动重新生成
cd listings/ch17-async-await/listing-17-16
cargo run
仅复制输出内容
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

`a`这个future在将控制权交给`b`之前还会继续运行一段时间，因为它在调用`trpl::sleep`之前会先调用`slow`。不过在那之后，每当其中一个future遇到await点时，它们就会互相交换控制权。在这种情况下，我们在每次调用`slow`之后都会执行这一操作，但我们也可以以最合理的方式将任务拆分成更小的部分来处理。

不过，我们其实并不想在这里“睡觉”：我们希望尽可能快地取得进展。我们只需要将控制权交还给运行时系统。我们可以直接使用`trpl::yield_now`函数来实现这一点。在清单17-17中，我们将所有`trpl::sleep`的调用都替换成了`trpl::yield_now`。

<List numbering="17-17" caption="使用 `yield_now` 让操作在进展过程中可以暂停" file-name="src/main.rs">

```rust
{{#rustdoc_include ../listings/ch17-async-await/listing-17-17/src/main.rs:yields}}
```

</清单>

这段代码在表达实际意图方面更加清晰，而且比使用`sleep`要快得多。因为像`sleep`所使用的计时器通常存在精度限制。例如，我们使用的`sleep`版本总是会至少休眠一毫秒，即使我们传递一个持续一纳秒的`Duration`也是如此。再次强调，现代计算机非常快速：它们可以在一毫秒内完成许多操作！

这意味着，即使对于计算密集型任务来说，异步技术也是有用的，这取决于程序还在执行哪些其他操作。因为异步技术为构建程序不同部分之间的关系提供了一个有用的工具（但代价是异步状态机所带来的额外开销）。这是一种协作式多任务处理的方式，每个“未来”都有能力决定何时通过`await`点来移交控制权。因此，每个“未来”也拥有……有责任避免长时间阻塞。在一些基于Rust的嵌入式操作系统中，这确实是唯一的一种多任务处理方式！

在现实世界的代码中，通常不会在每一行代码中都交替使用函数调用和`await`点。虽然以这种方式传递控制相对成本较低，但并非毫无代价。在许多情况下，试图将计算密集型任务拆分成多个部分可能会显著降低其执行速度，因此有时为了整体性能考虑，让某个操作暂时阻塞也是可行的。务必测量你的代码的实际性能瓶颈是什么。不过，需要注意的是，如果确实有很多工作以串行方式发生，而它们本应同时发生的话，那么这种串行模式就很重要了！

### 构建我们自己的异步抽象层

我们还可以将不同的未来时态组合在一起，以创建新的模式。例如，我们可以使用已有的异步构建模块来构建一个`timeout`函数。完成之后，这个结果将成为另一个可以使用的构建模块，进而创造出更多的异步抽象结构。

清单17-18展示了我们如何期望这个`timeout`在性能较慢的未来版本中能够正常运行。

<List numbering="17-18" caption="使用我们模拟的`timeout`来执行一个有时间限制的慢操作" file-name="src/main.rs">

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch17-async-await/listing-17-18/src/main.rs:here}}
```

</清单>

让我们来实现这个吧！首先，我们来思考一下用于`timeout`的API。

- 它必须是一个异步函数，这样我们才能对其进行等待操作。  
- 它的第一个参数应该是一个未来对象，用于执行任务。我们可以使这个参数具有通用性，以便它能够与任何未来对象一起使用。  
- 它的第二个参数表示最大等待时间。如果我们使用 ``Duration``，那么就可以很容易地将这个参数传递给 ``trpl::sleep``。  
- 它应该返回一个 ``Result``。如果未来对象成功完成，那么……`Result`将会变成`Ok`，其值由未来的值产生。如果超时时间先到，那么`Result`将会变成`Err`，并且表示超时等待的时间长度。

清单17-19展示了这一声明。

<!-- 这部分内容因为没有经过测试而未被编译。-->

<List numbering="17-19" caption="定义 `timeout` 的签名" file-name="src/main.rs">

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch17-async-await/listing-17-19/src/main.rs:declaration}}
```

</清单>

这满足了我们对这些类型的需求。现在让我们考虑一下我们需要的_行为_：我们希望将传入的未来值与持续时间进行比较。我们可以使用`trpl::sleep`来从持续时间中创建一个计时器，然后使用`trpl::select`来运行这个计时器，并将调用者传入的未来值作为参数传递给它。

在清单17-20中，我们通过匹配`trpl::select`的结果来实现`timeout`。

<List numbering="17-20" caption="使用 `select` 和 `sleep` 定义 `timeout`" file-name="src/main.rs">

```rust
{{#rustdoc_include ../listings/ch17-async-await/listing-17-20/src/main.rs:implementation}}
```

</清单>

实现`trpl::select`的方式并不公平：它总是按照参数被传递的顺序来轮询它们（而其他实现则会随机选择先处理哪个参数）。因此，我们应该先将`future_to_try`传递给`select`，这样即使`max_time`的持续时间非常短，`select`也有机会完成任务。如果`future_to_try`先完成，那么`select`将返回`Left`。根据`future_to_try`的输出结果。如果`timer`先完成，那么`select`将会返回`Right`，同时还会返回计时器输出的`()`的结果。

如果`future_to_try`成功执行，并且我们得到了`Left(output)`的结果，那么我们就返回`Ok(output)`。相反，如果睡眠计时器已经到期，而我们得到了`Right(())`的结果，那么我们就忽略带有下划线的`()`，而是返回`Err(max_time)`。

就这样，我们创建了一个由另外两个异步辅助函数构成的可用`timeout`。如果我们运行这段代码，它会在超时后打印出失败模式：

```text
Failed after 2 seconds
```

因为期货可以与其他期货组合使用，所以你可以使用一些较小的异步组件来构建非常强大的工具。例如，你可以采用同样的方法将超时机制与重试机制结合起来，进而将这些机制应用于网络调用等操作中（如清单17-5所示）。

在实践中，你通常会直接处理`async`和`await`，同时也会使用如`select`这样的函数以及`join!`这样的宏来控制最外层的未来操作的执行方式。

我们已经看到了多种同时处理多个未来的方法。接下来，我们将探讨如何利用_流_来按顺序处理多个未来。

[异步程序]: ch17-01-futures-and-syntax.html#我们的第一个异步程序