<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="将我们的单线程服务器转换为多线程服务器"></a>  
<a id="从单线程到多线程服务器"></a>

## 从单线程服务器转变为多线程服务器

目前，服务器会依次处理每个请求，这意味着直到第一个请求的处理完成之后，服务器才会处理第二个连接。如果服务器收到的请求越来越多，这种串行处理方式就会变得越来越不理想。如果服务器收到一个需要很长时间才能处理的请求，那么后续的请求将不得不等待该请求完成，即使新的请求可以很快被处理。我们需要解决这个问题，但在此之前，我们先来看看这个问题在实际中的表现。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="在当前的服务器实现中模拟慢速请求"></a>

### 模拟慢速请求

我们将探讨一个处理速度较慢的请求如何影响对当前服务器实现的其他请求。清单21-10展示了如何处理对`_/sleep_`的请求，该请求会模拟一个缓慢的响应，导致服务器在响应之前休眠五秒钟。

<listing number="21-10" file-name="src/main.rs" caption="通过休眠五秒来模拟慢速请求">

```rust,no_run
{{#rustdoc_include ../listings/ch21-web-server/listing-21-10/src/main.rs:here}}
```

</ Listing>

既然我们有了三种情况，我们就将代码从`if`切换到了`match`。我们需要显式地匹配`request_line`中的某个片段，以便与字符串字面量进行模式匹配；而`match`并不像相等性方法那样进行自动引用和解引用操作。

第一个分支与清单21-9中的__`INLINE_CODE_29__`块相同。第二个分支匹配对`_/sleep_`的请求。当接收到该请求时，服务器会休眠五秒钟，然后再渲染成功的HTML页面。第三个分支与清单21-9中的__`INLINE_CODE_30__`块相同。

你可以看到我们的服务器是多么原始：真正的库会以更简洁的方式来处理多个请求的识别问题！

使用 `cargo run` 启动服务器。然后，打开两个浏览器窗口：一个用于 http://127.0.0.1:7878_，另一个用于 http://127.0.0.1:7878/sleep_。如果你像之前一样多次输入 _/_ URI，你会看到它快速响应。但是，如果你先输入 _/sleep_，然后再加载 _/_，你会发现 _/_ 会等待 `sleep` 完全睡五秒之后才会继续加载。

我们有多种方法可以避免慢速请求导致其他请求被阻塞，包括使用异步处理，就像我们在第17章中做的那样；我们将要实现的方法是使用线程池。

### 通过线程池提高吞吐量

**线程池**是一组已经创建出来、处于就绪状态并等待处理任务的线程。当程序接收到新的任务时，它会将线程池中的一个线程分配给该任务，该线程将负责处理该任务。在第一个线程处理任务的过程中，线程池中的其余线程仍然可以处理其他到来的任务。当第一个线程完成其任务后，它会被返回到空闲线程池中，准备处理新的任务。线程池允许您同时处理多个连接，从而提高服务器的吞吐量。

我们将池中的线程数量限制在一个较小的数值，以此来防止DoS攻击。如果我们让程序在接收到每个请求时都创建一个新的线程，那么那些向我们的服务器发送1000万次请求的用户就有可能耗尽所有的服务器资源，导致请求的处理过程完全停止。

因此，我们不会创建无限数量的线程，而是会有一个固定数量的线程在池中等待。进入系统的请求会被发送到池中进行处理。池会维护一个待处理的请求队列。池中的每个线程会从队列中取出一个请求进行处理，然后向队列中请求另一个请求。通过这种设计，我们可以同时处理多达`N`个请求，其中`N`是线程的数量。如果每个线程都在处理一个耗时较长的请求，那么后续的请求仍然可以排队等待，但我们能够处理的耗时较长请求的数量已经增加了。

这种技术只是提高网络服务器吞吐量的众多方法之一。您还可以尝试使用分叉/合并模型、单线程异步I/O模型以及多线程异步I/O模型。如果您对这个话题感兴趣，可以阅读更多关于其他解决方案的信息，并尝试实现它们；使用像Rust这样的低级语言，所有这些选项都是可行的。

在开始实现线程池之前，我们先来了解一下使用线程池应该是什么样的。在设计代码时，先编写客户端接口可以帮助指导你的设计思路。先编写代码的API，使其按照你想要调用它的方式进行结构化；然后在这个结构内实现功能，而不是先实现功能后再设计公共API。

与我们在第12章项目中使用的测试驱动开发类似，我们在这里也会使用编译器驱动的开发方法。我们将编写调用我们想要调用的函数的代码，然后查看编译器的错误信息，以确定接下来需要修改哪些部分才能让代码正常工作。不过，在这样做之前，我们先来探讨一下那个我们不会使用的技术作为起点。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="代码结构：如果我们能为每个请求创建一个线程"></a>

#### 为每个请求创建一个线程

首先，让我们看看如果我们的代码为每个连接都创建一个新的线程，那么代码会是什么样子。如前所述，由于可能存在无限创建线程的问题，这并不是我们的最终方案。不过，这确实是一个开始，可以让我们先实现一个功能正常的多线程服务器。之后，我们可以加入线程池作为改进措施，这样两种解决方案之间的对比就会更加容易了。

清单21-11展示了需要对`main`所做的修改，以便在该循环内为每个流创建一个新的线程来处理它们。

<列表编号="21-11" 文件名称="src/main.rs" 标题="为每个流创建一个新的线程">

```rust,no_run
{{#rustdoc_include ../listings/ch21-web-server/listing-21-11/src/main.rs:here}}
```

</ Listing>

正如你在第16章中学到的那样，`thread::spawn`会创建一个新的线程，然后在新线程中执行闭包中的代码。如果你运行这段代码，并在浏览器中加载_/sleep_，那么在另外两个浏览器标签页中加载_/_，你会发现对_/_的请求不必等待_/sleep_完成。然而，正如我们之前提到的，这样做最终会导致系统负担过重，因为你会无限制地创建新的线程。

你可能还记得在第17章中提到过，这正是异步和await发挥作用的地方！在构建线程池时，请记住这一点，思考一下如果使用异步技术，情况会如何变化，或者是否保持不变。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="如何为大量线程创建类似的接口"></a>

#### 创建有限数量的线程

我们希望我们的线程池能够以类似且熟悉的方式运行，这样在从单个线程切换到线程池时，不需要对使用我们API的代码进行大规模的修改。清单21-12展示了我们希望使用的`ThreadPool`结构的假设接口，以替代`thread::spawn`。

<列表编号="21-12" 文件名称="src/main.rs" 标题="我们理想的 `ThreadPool` 接口">

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch21-web-server/listing-21-12/src/main.rs:here}}
```

</ Listing>

我们使用 ``ThreadPool::new`` 来创建一个新的线程池，该线程池可以配置线程数量，在这个例子中是四个线程。然后，在 ``for`` 循环中，``pool.execute`` 与 ``thread::spawn`` 具有类似的接口，它接受一个闭包，这个闭包将被线程池中的每个线程执行。我们需要实现 ``pool.execute``，以便它能够接收这个闭包并将其传递给线程池中的某个线程来执行。这段代码目前还无法编译，但我们会尝试进行编译，以便编译器能够指导我们如何修复这个问题。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="通过编译器驱动的开发来构建线程池结构"></a>

#### 使用编译器驱动的开发方式构建 `ThreadPool`

请对清单21-12中的代码进行修改，将其保存到`_src/main.rs_`文件中。之后，我们可以利用`cargo check`产生的编译错误来指导我们的开发工作。这是我们遇到的第一个错误：

```console
{{#include ../listings/ch21-web-server/listing-21-12/output.txt}}
```

太好了！这个错误提示我们需要一个 `ThreadPool` 类型或模块，所以我们现在就创建一个。我们的 `ThreadPool` 实现将独立于我们的网络服务器正在执行的工作类型。因此，我们将 `hello`  crate 从二进制 crate 更改为库 crate，以便存储我们的 `ThreadPool` 实现。在改为库 crate 之后，我们还可以使用单独的线程池库来处理任何需要使用线程池的工作，而不仅仅是为了处理网络请求。

创建一个 `_src/lib.rs_`文件，其中包含以下代码，这是目前我们能够定义的最简单的`__INLINE_CODE__50__`结构体的定义：

<listing file-name="src/lib.rs">

```rust,noplayground
{{#rustdoc_include ../listings/ch21-web-server/no-listing-01-define-threadpool-struct/src/lib.rs}}
```

</ Listing>

然后，编辑 _main.rs_ 文件，将 `ThreadPool` 从库 crate 中引入作用域，方法是在 _src/main.rs_ 文件的顶部添加以下代码：

<code listing file-name="src/main.rs">

```rust,ignore
{{#rustdoc_include ../listings/ch21-web-server/no-listing-01-define-threadpool-struct/src/main.rs:here}}
```

</ Listing>

这段代码仍然无法运行，但让我们再次检查一下，以找出需要解决的下一个错误。

```console
{{#include ../listings/ch21-web-server/no-listing-01-define-threadpool-struct/output.txt}}
```

这个错误表明，接下来我们需要为 `ThreadPool` 创建一个名为 `new` 的相关函数。我们还知道，`new` 需要一个参数，该参数可以接受 `4` 作为参数，并且应该返回一个 `ThreadPool` 类型的实例。让我们实现最简单的 `new` 函数，该函数具备这些特性：

<listing file-name="src/lib.rs">

```rust,noplayground
{{#rustdoc_include ../listings/ch21-web-server/no-listing-02-impl-threadpool-new/src/lib.rs}}
```

</ Listing>

我们选择 ``usize`` 作为 ``size`` 参数的类型，因为我们知道，线程数量为零是没有意义的。我们还知道，我们将使用这个 ``4`` 来表示线程集合中的元素数量，正如第3章的[“整数类型”][integer-types]章节中所讨论的那样，``usize`` 类型正是用于此目的的。

让我们再次检查一下代码：

```console
{{#include ../listings/ch21-web-server/no-listing-02-impl-threadpool-new/output.txt}}
```

现在出现错误是因为我们在 `ThreadPool` 上没有 `execute` 方法。回想一下在[“创建有限数量的线程”](#creating-a-finite-number-of-threads)部分，我们决定我们的线程池应该有一个类似于 `thread::spawn` 的接口。此外，我们还将实现 `execute` 函数，该函数接收给定的闭包，并将其传递给线程池中的空闲线程来运行。

我们将在 `ThreadPool` 上定义 `execute` 方法，该方法接受一个闭包作为参数。回顾第13章中的[“将捕获的值移出闭包”][moving-out-of-closures]<!-- ignore -->，我们知道可以用三种不同的特征来接受闭包作为参数：`Fn`、`FnMut` 和 `FnOnce`。我们需要决定在这里使用哪种类型的闭包。我们知道最终会采用类似于标准库中的 `thread::spawn` 实现的方式，因此我们可以查看 `thread::spawn` 的签名对参数的限制。文档中提供了以下信息：

```rust,ignore
pub fn spawn<F, T>(f: F) -> JoinHandle<T>
    where
        F: FnOnce() -> T,
        F: Send + 'static,
        T: Send + 'static,
```

这里的`F`类型参数是我们关注的；而`T`类型参数则与返回值相关，我们并不关心这一点。我们可以看到，`spawn`在`F`中使用了`FnOnce`作为特征绑定。这可能正是我们所需要的，因为最终我们会将`execute`中的参数传递给`spawn`。我们可以进一步确认`FnOnce`就是我们需要使用的特征，因为执行请求的那个线程只会执行一次该请求的闭包，这与`FnOnce`中的`Once`是一致的。

类型参数`F`还具有`Send`这一特性绑定，以及`'static`的生命周期绑定。这些在我们的场景中非常有用：我们需要`Send`来将闭包从一个线程传输到另一个线程，同时还需要`'static`，因为我们不知道线程执行所需的时间。让我们在`ThreadPool`上创建一个`execute`方法，该方法接受一个类型为`F`的通用参数，并且具有这些边界限制。

<listing file-name="src/lib.rs">

```rust,noplayground
{{#rustdoc_include ../listings/ch21-web-server/no-listing-03-define-execute/src/lib.rs:here}}
```

</ Listing>

我们在 ``FnOnce``之后仍然使用 ``()``，因为此__`INLINE_CODE_93__`代表一个不接收参数且返回单位类型__`INLINE_CODE_94__`的闭包。就像函数定义一样，返回类型可以在签名中省略，但即使没有参数，我们仍然需要括号。

再次说明，这是 ``execute`` 方法的最简单实现：它实际上并不执行任何操作，但我们只是想让代码能够编译通过而已。让我们再检查一下吧：

```console
{{#include ../listings/ch21-web-server/no-listing-03-define-execute/output.txt}}
```

它已经可以编译了！不过请注意，如果您尝试调用 `cargo run` 并在浏览器中发起请求，您将会看到与章节开头相同的错误。实际上，我们的库还没有调用传递给 `execute` 的闭包！

注意：关于那些使用严格编译器的语言，比如Haskell和Rust，人们常说“如果代码能够编译出来，那就说明它是正确的”。不过，这句话并不适用于所有情况。我们的项目能够成功编译，但实际上它根本没有任何功能！如果我们正在开发一个真正完整的项目，现在正是时候开始编写单元测试，以确保代码不仅能够编译，而且其行为符合我们的期望。

思考一下：如果我们打算执行一个未来操作，而不是使用闭包，那么情况会有什么不同呢？

#### 验证 `new` 中线程的数量

我们对 `new` 和 `execute` 的参数没有任何操作。让我们按照期望的行为来编写这些函数的主体代码。首先，我们来考虑一下 `new`。之前，我们为 `size` 参数选择了一个无符号类型，因为具有负数线程数的池是没有意义的。然而，零线程数的池也是没有意义的，不过零仍然是一个完全有效的 `usize`。我们将添加代码来检查 `size` 是否大于零，然后再返回 `ThreadPool` 的实例。如果使用 `assert!` 宏，并且接收到零值，程序将会发生panic，如清单 21-13 所示。

<listing number="21-13" file-name="src/lib.rs" caption="实现`ThreadPool::new`，如果`size`为零则引发panic">

```rust,noplayground
{{#rustdoc_include ../listings/ch21-web-server/listing-21-13/src/lib.rs:here}}
```

</ Listing>

我们还为我们的 `ThreadPool` 添加了一些带有文档注释的说明。  
请注意，我们遵循了良好的文档编写规范，添加了一个部分来指出我们的函数可能会陷入恐慌的情况，具体内容可以在第14章中了解到。请尝试运行 `cargo doc --open`，并点击 `ThreadPool` 结构，以查看 `new` 生成的文档效果！

与其像在这里那样添加 `assert!` 宏，我们完全可以将 `new` 改为 `build`，然后返回 `Result`，就像我们在 Listing 12-9 中的 I/O 项目中对 `Config::build` 所做的那样。不过，在这种情况下，我们决定：尝试创建一个没有任何线程的线程池应该会引发无法恢复的错误。如果你有雄心壮志，可以尝试编写一个名为 `build` 的函数，其签名如下，以便与 `new` 函数进行比较：

```rust,ignore
pub fn build(size: usize) -> Result<ThreadPool, PoolCreationError> {
```

#### 创建存储线程的空间

现在我们已经有了一个方法来确认可以安全地使用一定数量的线程进行存储，那么我们就可以创建这些线程，并将它们存储在`ThreadPool`结构中，然后再返回该结构。但是，我们该如何“存储”一个线程呢？让我们再看一下`thread::spawn`的签名：

```rust,ignore
pub fn spawn<F, T>(f: F) -> JoinHandle<T>
    where
        F: FnOnce() -> T,
        F: Send + 'static,
        T: Send + 'static,
```

`spawn`函数返回一个`JoinHandle<T>`类型的值，其中`T`是闭包所返回的类型。让我们也尝试使用`JoinHandle`，看看会发生什么。在我们的例子中，我们传递给线程池的闭包会负责处理连接操作，并不会返回任何内容，因此`T`将是一个单位类型，即`()`。

清单 21-14 中的代码可以编译，但目前它并不会创建任何线程。  
我们修改了 ``ThreadPool`` 的定义，使其能够存储一个由 ``thread::JoinHandle<()>`` 实例组成的向量；同时为该向量分配了 ``size`` 的容量；还设置了一个 ``for`` 循环，该循环会执行一些代码来创建线程；最后返回了一个包含这些线程的 ``ThreadPool`` 实例。

<列表编号="21-14" 文件名称="src/lib.rs" 标题="创建一个向量，用于存放 `ThreadPool` 中的线程">

```rust,ignore,not_desired_behavior
{{#rustdoc_include ../listings/ch21-web-server/listing-21-14/src/lib.rs:here}}
```

</ Listing>

我们在库 crate中引入了 `std::thread`，因为我们在 `ThreadPool` 中使用了 `thread::JoinHandle` 作为向量中元素的类型。

一旦接收到有效的尺寸信息，我们的`ThreadPool`就会创建一个新的向量，该向量能够存储`size`个元素。`with_capacity`函数执行的任务与`Vec::new`相同，但有一个重要的区别：它会在向量中预先分配空间。因为我们知道需要在向量中存储`size`个元素，所以这种预先分配空间的方式比在插入元素时动态调整大小的做法更为高效。

当你再次运行`cargo check`时，应该会成功。

<a id="a-worker-struct-responsible-for-sending-code-from-the-threadpool-to-a-thread"></a>

#### 将代码从 `ThreadPool` 发送到线程中

我们在 Listing 21-14 中的 `for` 循环中留下了一条关于线程创建的评论。接下来，我们将探讨如何实际创建线程。标准库提供了 `thread::spawn` 作为创建线程的方法，而 `thread::spawn` 则期望在线程创建后立即执行某些代码。然而，在我们的案例中，我们希望创建线程，并让它们等待稍后发送的代码。标准库对线程的实现并没有提供这样的功能；我们必须手动实现它。

我们将通过在`ThreadPool`与负责管理此新行为的线程之间引入一个新的数据结构来实现这一行为。我们将这个数据结构称为_Worker_，这是池化实现中常用的术语。`Worker`会选取需要运行的代码，并在其对应的线程上执行这些代码。

想象一下餐厅厨房里的工作人员：他们需要等待顾客下单，然后负责处理这些订单并完成相应的烹饪工作。

与其在线程池中存储`JoinHandle<()>`实例的向量，我们将存储`Worker`结构的实例。每个`Worker`将存储一个`JoinHandle<()>`实例。然后，我们将在`Worker`上实现一个方法，该方法接受一个要运行的代码闭包，并将其发送到已经运行的线程中进行执行。此外，我们还会为每个`Worker`提供一个`id`结构，这样在日志记录或调试时，我们可以区分线程池中的不同`Worker`实例。

这是当我们创建 ``ThreadPool`` 时将会发生的新流程。我们将实现将闭包发送到线程的代码，而这一切都是在 ``Worker`` 设置之后进行的。

1. 定义一个 ``Worker`` 结构体，该结构体包含一个 ``id`` 和一个 ``JoinHandle<()>``。

2. 将 ``ThreadPool`` 修改为能够存储多个 ``Worker`` 实例的向量。

3. 定义一个 ``Worker::new`` 函数，该函数接受一个 ``id`` 类型的数字，并返回一个 ``Worker`` 实例，该实例包含 ``id`` 以及一个带有空闭包的线程。

4. 在 ``ThreadPool::new`` 中，使用 ``for`` 的循环计数器来生成 ``id``；利用该值创建一个新的 ``Worker`` 实例，并将 ``Worker`` 存储到该向量中。

如果你愿意接受挑战，请在查看清单21-15中的代码之前，尝试自己实现这些更改。

准备好了吗？以下是 Listing 21-15，它展示了一种实现上述修改的方法。

<列表编号="21-15" 文件名称="src/lib.rs" 标题="修改 `ThreadPool` 以存储 `Worker` 实例，而不是直接存储线程">

```rust,noplayground
{{#rustdoc_include ../listings/ch21-web-server/listing-21-15/src/lib.rs:here}}
```

</ Listing>

我们将 `ThreadPool` 中的字段名称从 `threads` 更改为 `workers`，因为现在它存储的是 `Worker` 实例，而不是 `JoinHandle<()>` 实例。我们在 `for` 循环中使用的计数器作为参数传递给 `Worker::new`，并且每个新的 `Worker` 实例都会被存储在名为 `workers` 的向量中。

外部代码（比如我们的服务器在`_src/main.rs_`中）不需要知道在`ThreadPool``中使用`Worker``结构的实现细节，因此我们将`Worker``结构及其`new``函数设为私有。`Worker::new``函数使用我们提供的`id`，并存储一个由空闭包触发的新线程创建的`JoinHandle<()>``实例。

注意：如果操作系统由于系统资源不足而无法创建线程，那么`thread::spawn`将会引发恐慌。这将导致整个服务器陷入恐慌状态，尽管某些线程的创建可能成功。为了简单起见，这种行为是可以接受的，但在实际的生产环境线程池实现中，你更建议使用[`std::thread::Builder`][builder]<!-- 忽略 -->以及其[`spawn`][builder-spawn]<!-- 忽略 -->方法，后者会返回`Result`。

这段代码将会被编译，并且会存储我们作为参数传递给`ThreadPool::new`的`Worker`实例的数量。不过，我们仍然没有处理在`execute`中得到的闭包。接下来，让我们看看该如何处理这个问题。

#### 通过通道向线程发送请求

接下来我们要解决的问题是，分配给`thread::spawn`的闭包根本没有任何作用。目前，我们获得了想要在`execute`方法中执行的闭包。但是，在创建每个`Worker`时，我们需要给`thread::spawn`一个闭包来运行。

我们希望刚刚创建的`Worker`结构体能够从存储在`ThreadPool`队列中获取要运行的代码，并将该代码发送到相应的线程中进行执行。

我们在第16章中学到的通道——一种在两个线程之间进行通信的简单方式——非常适合这种使用场景。我们将使用通道来充当任务队列，而`execute`将会将任务从`ThreadPool`发送到`Worker`实例，后者再将任务发送到相应的线程中。以下是具体的实施方案：

1. ``ThreadPool`` 将创建一个通道，并持有发送者。
2. 每个 ``Worker`` 将持有接收者。
3. 我们将创建一个新的 ``Job`` 结构体，用来保存我们想要通过通道发送的闭包。
4. ``execute`` 方法将通过发送者发送它想要执行的任务。
5. 在其线程中，``Worker`` 会遍历其接收者，并执行接收到的任何任务的闭包。

让我们首先在`ThreadPool::new`中创建一个通道，并将发送者存储在`ThreadPool`实例中，如清单21-16所示。目前，`Job`结构体并不存储任何内容，但将来它将是我们通过通道发送内容的类型。

<列表编号="21-16" 文件名称="src/lib.rs" 标题="修改 `ThreadPool` 以存储发送通道的发送者，该通道传输 `Job` 实例">

```rust,noplayground
{{#rustdoc_include ../listings/ch21-web-server/listing-21-16/src/lib.rs:here}}
```

</ Listing>

在`ThreadPool::new`中，我们创建了新通道，并让pool负责持有发送者。这样就能成功编译了。

让我们尝试将通道的接收者作为参数传递给每个`Worker`，因为线程池会创建这个通道。我们知道，我们希望在`Worker`实例所创建的线程中使用这个接收者，因此我们在闭包中引用`receiver`参数。清单21-17中的代码目前还无法编译成功。

<列表编号="21-17" 文件名称="src/lib.rs" 标题="将接收者传递给每个__INLINE_CODE__224__">

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch21-web-server/listing-21-17/src/lib.rs:here}}
```

</ Listing>

我们进行了一些简单直接的修改：我们将接收者传递给`Worker::new`，然后在闭包内部使用它。

当我们尝试检查这段代码时，出现了这个错误：

```console
{{#include ../listings/ch21-web-server/listing-21-17/output.txt}}
```

这段代码试图将 ``receiver`` 传递给多个 ``Worker`` 实例。这是不可行的，正如你在第16章《通道实现》中所了解到的那样，Rust提供的通道是一个多个生产者、一个消费者的模型。这意味着我们不能简单地克隆通道的接收端来修复这个问题。此外，我们也不希望多次向多个消费者发送消息；我们希望有一个消息列表，其中包含多个 ``Worker`` 实例，这样每条消息都能被处理一次。

此外，将任务从通道队列中移除会涉及到对`receiver`进行修改，因此线程需要一种安全的方式来共享和修改`receiver`；否则，我们可能会遇到竞态条件（如第16章所述）。

请回想一下第16章中讨论的线程安全智能指针：为了在多个线程之间共享所有权，并允许线程修改该值，我们需要使用`Arc<Mutex<T>>`。`Arc`类型可以让多个`Worker`实例拥有接收者，而`Mutex`则确保一次只有一个`Worker`从接收者那里获取数据。列表21-18展示了我们需要进行的修改。

<列表编号="21-18" 文件名称="src/lib.rs" 标题="使用 `Arc` 和 `Mutex` 在 `Worker` 实例之间共享接收器">

```rust,noplayground
{{#rustdoc_include ../listings/ch21-web-server/listing-21-18/src/lib.rs:here}}
```

</ Listing>

在 `ThreadPool::new` 中，我们将接收者放入 `Arc` 和 `Mutex` 中。对于每个新的 `Worker` 实例，我们都会克隆 `Arc` 以增加引用计数，这样 `Worker` 的实例就可以共享对接收者的所有权。

经过这些修改之后，代码可以编译了！我们即将成功！

#### 实现 `execute` 方法

让我们最终在 `ThreadPool` 上实现 `execute` 方法。同时，我们将 `Job` 从结构体改为类型别名，用于表示 `execute` 所接收的闭包的类型。正如第20章的[“类型别名与类型同义表达”][type-aliases]章节中所讨论的，类型别名可以帮助我们简化复杂的类型名称，使其更易于使用。请查看清单21-19。

<listing number="21-19" file-name="src/lib.rs" caption="为包含多个闭包的`Box`创建一个`Job`类型别名，然后将任务通过通道传递">

```rust,noplayground
{{#rustdoc_include ../listings/ch21-web-server/listing-21-19/src/lib.rs:here}}
```

</ Listing>

在使用在 `execute` 中得到的闭包来创建新的 `Job` 实例之后，我们将该任务发送到通道的发送端。如果发送失败，我们会调用 `unwrap` 来处理这种情况。这种情况可能发生在我们停止所有线程执行的时候，这意味着接收端不再接收到新的消息。目前，我们无法停止线程的执行：只要线程池存在，我们的线程就会继续运行。我们使用 `unwrap` 的原因是我们知道这种失败情况不会发生，但编译器并不了解这一点。

但是，我们还没有完成！在`Worker`中，我们的闭包被传递给`thread::spawn`时，它仍然只是对通道的接收端进行引用。相反，我们需要让这个闭包无限循环，不断向通道的接收端请求任务，并在接收到任务时执行该任务。让我们把清单21-20中所展示的修改应用到`Worker::new`上。

<列表编号="21-20" 文件名称="src/lib.rs" 标题="在`Worker`实例的线程中接收并执行任务">

```rust,noplayground
{{#rustdoc_include ../listings/ch21-web-server/listing-21-20/src/lib.rs:here}}
```

</ Listing>

在这里，我们首先调用 `lock` 来获取 `receiver` 中的互斥锁，然后调用 `unwrap` 来在发生错误时引发恐慌。如果互斥锁处于“中毒”状态，获取锁可能会失败。这种情况可能发生在其他线程在持有锁时没有释放锁的情况下导致其他线程发生恐慌。在这种情况下，调用 `unwrap` 来让该线程引发恐慌是正确的操作。你可以自由地将 `unwrap` 替换为 `expect`，并在其中添加对你来说有意义的错误信息。

如果我们成功获得了互斥锁，就会调用`recv`来从通道中接收`Job`。最后的`unwrap`则可以处理任何可能出现的错误，比如当持有发送者的线程关闭时。这与`send`方法类似，如果接收者关闭，该方法也会返回`Err`。

对`recv`的调用会阻塞线程，因此如果没有任务可用，当前线程将等待直到有任务可用为止。`Mutex<T>`则确保一次只有一个`Worker`线程尝试请求任务。

我们的线程池现在已经可以正常运行了！请执行一个`cargo run`，然后发起一些请求：

<!-- 手动重新生成
cd listings/ch21-web-server/listing-21-20
cargo run
向 127.0.0.1:7878 发起一些请求
由于输出结果取决于请求的发送方式，因此无法实现自动化操作
-->

```console
$ cargo run
   Compiling hello v0.1.0 (file:///projects/hello)
warning: field `workers` is never read
 --> src/lib.rs:7:5
  |
6 | pub struct ThreadPool {
  |            ---------- field in this struct
7 |     workers: Vec<Worker>,
  |     ^^^^^^^
  |
  = note: `#[warn(dead_code)]` on by default

warning: fields `id` and `thread` are never read
  --> src/lib.rs:48:5
   |
47 | struct Worker {
   |        ------ fields in this struct
48 |     id: usize,
   |     ^^
49 |     thread: thread::JoinHandle<()>,
   |     ^^^^^^

warning: `hello` (lib) generated 2 warnings
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 4.91s
     Running `target/debug/hello`
Worker 0 got a job; executing.
Worker 2 got a job; executing.
Worker 1 got a job; executing.
Worker 3 got a job; executing.
Worker 0 got a job; executing.
Worker 2 got a job; executing.
Worker 1 got a job; executing.
Worker 3 got a job; executing.
Worker 0 got a job; executing.
Worker 2 got a job; executing.
```

成功！我们现在拥有一个可以异步执行连接的线程池。创建的线程数量永远不会超过四个，因此当服务器收到大量请求时，系统也不会出现负载过重的情况。如果我们向_/sleep_发起请求，服务器可以通过另一个线程来处理其他请求。

注意：如果您同时在多个浏览器窗口中打开 _/sleep_ 这个页面，它们可能会以每五秒一次的频率依次加载。某些网络浏览器出于缓存考虑，会顺序执行同一请求的多个实例。这种限制并非由我们的网络服务器引起。

现在是暂停并思考一下：如果使用未来函数而不是闭包来代表需要执行的操作，那么 Listing 21-18、21-19 和 21-20 中的代码将会有何不同。哪些类型会发生变化？方法签名是否会有所不同，如果有变化的话？代码的哪些部分保持不变呢？

在了解了第17章和第19章中的`while let`循环之后，你可能会好奇为什么我们没有像清单21-21中那样编写`Worker`线程代码。

<listing number="21-21" file-name="src/lib.rs" caption="使用 `while let` 实现的 `Worker::new` 的另一种方法">

```rust,ignore,not_desired_behavior
{{#rustdoc_include ../listings/ch21-web-server/listing-21-21/src/lib.rs:here}}
```

</ Listing>

这段代码可以编译并运行，但并不能实现预期的线程行为：一个较慢的请求仍然会导致其他请求等待处理。原因有些微妙：`Mutex`结构体没有公开的`unlock`方法，因为锁的所有权取决于`LockResult<MutexGuard<T>>`中`lock`方法所返回的对象的生命周期。在编译时，借用检查器会强制规定，除非持有锁，否则无法访问由`Mutex`保护的资源。然而，如果我们不注意`MutexGuard<T>`的生命周期，这种实现可能会导致锁被持有的时间超过预期。

在 Listing 21-20 中的代码使用了 `let job = receiver.lock().unwrap().recv().unwrap();` works because with `let`，等号右侧表达式中所使用的所有临时值会在 ``let`` 语句结束后立即被丢弃。然而，`while let` (and `if let` and `match`) 中的临时值则不会在相关块结束之前被丢弃。在 Listing 21-21 中，锁会一直保持到调用 ``job()`` 为止，这意味着其他 ``Worker`` 实例无法接收任务。

[type-aliases]: ch20-03-advanced-types.html#type-synonyms-and-type-aliases
[integer-types]: ch03-02-data-types.html#integer-types
[moving-out-of-closures]: ch13-01-closures.html#moving-captured-values-out-of-closures
[builder]:../std/thread/struct.Builder.html
[builder-spawn]:../std/thread/struct.Builder.html#method.spawn