<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="将我们的单线程服务器转换为多线程服务器"></a>
<a id="从单线程到多线程服务器"></a>

## 从单线程服务器转变为多线程服务器

目前，服务器会依次处理每个请求，这意味着直到第一个请求处理完毕之后，才会处理第二个请求。如果服务器收到的请求越来越多，这种串行处理方式就会变得不那么有效。如果某个请求需要很长时间来处理，那么后续的请求就不得不等待那个长请求的完成，即使新的请求可以很快被处理。我们需要解决这个问题。首先，让我们看看这个问题的实际表现。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="在当前的服务器实现中模拟慢速请求"></a>

### 模拟慢速请求

我们将探讨缓慢处理的请求如何影响对当前服务器实现的其他请求。清单21-10展示了如何处理对`_/sleep_`的请求，该请求会模拟一个缓慢的响应，使服务器在响应之前休眠五秒钟。

<列表编号="21-10" 文件名称="src/main.rs" 标题="通过休眠五秒来模拟慢速请求">

```rust,no_run
{{#rustdoc_include ../listings/ch21-web-server/listing-21-10/src/main.rs:here}}
```

</清单>

既然我们有了三种情况，我们就将代码从`if`切换到了`match`。我们需要显式地匹配`request_line`中的某个片段，以便与字符串字面值进行模式匹配；而`match`并不像相等性方法那样自动进行引用和解除引用操作。

第一个分支与清单21-9中的`if`块相同。第二个分支匹配对/_sleep_的请求。当接收到该请求时，服务器会休眠五秒钟，然后再渲染成功的HTML页面。第三个分支与清单21-9中的`else`块相同。

你可以看到我们的服务器是多么原始：真正的库会以更简洁的方式处理多个请求的识别问题！

使用`cargo run`启动服务器。然后，打开两个浏览器窗口：一个用于http://127.0.0.1:7878_，另一个用于http://127.0.0.1:7878/sleep_。如果你像之前一样多次输入/_/_ URI，你会看到它快速响应。但是，如果你先输入_/sleep_，然后再加载_/_，你会发现_/_会在`sleep`完全休眠五秒之后才继续加载。

我们有多种技术可以用来避免慢速请求导致其他请求被阻塞，包括使用异步处理，就像我们在第17章中所做的那样；而我们将要实现的是线程池技术。

### 通过线程池提高吞吐量

**线程池**是一组已经创建出来、处于就绪状态并等待处理任务的线程。当程序接收到新的任务时，它会将线程池中的一个线程分配给该任务，该线程将负责处理该任务。在任务处理过程中，线程池中的其他线程仍然可以处理其他到来的任务。当第一个线程完成其任务后，它会被返回到空闲线程池中，准备继续处理其他任务。一个新的任务。线程池允许您同时处理连接，从而提高服务器的吞吐量。

我们将池中的线程数量限制在一个较小的数值，以防止DoS攻击；如果我们让程序在接收到每个请求时都创建一个新的线程，那么向我们的服务器发送1000万次请求的人就可以耗尽所有的服务器资源，导致请求的处理过程完全停止。

因此，我们不会创建无限数量的线程，而是会有一个固定数量的线程在池中等待。进入系统的请求会被发送到池中进行处理。池会维护一个待处理的请求队列。池中的每个线程会从队列中取出一个请求进行处理，然后向队列中请求另一个请求。通过这种设计，我们可以同时处理最多`N`个请求，其中`N`就是线程的数量。如果每个线程都能独立处理请求，那么系统的处理能力就会得到极大的提升。线程正在响应一个长时间运行的请求，后续的请求仍然可以积压在队列中，但我们已经增加了我们能够处理的长时间运行请求的数量，以避免达到那个临界点。

这种技术只是提高网络服务器吞吐量的众多方法之一。您还可以尝试使用分叉/合并模型、单线程异步I/O模型以及多线程异步I/O模型。如果您对这个话题感兴趣，可以阅读更多关于其他解决方案的信息，并尝试将其付诸实践；使用像Rust这样的低级语言，所有这些选项都是可行的。

在开始实现线程池之前，我们先来讨论一下使用线程池应该是什么样的。在设计代码时，先编写客户端接口可以帮助指导你的设计思路。编写API时，要确保其结构符合你预期的调用方式；然后，在该结构内实现功能，而不是先实现功能后再设计公共API。

与我们在第12章的项目中使用的测试驱动开发类似，我们在这里也会使用编译器驱动的开发方法。我们将编写调用所需函数的代码，然后查看编译器的错误信息，以确定接下来需要修改哪些部分才能让代码正常工作。不过，在这样做之前，我们先来探讨一下那个我们不会使用的技术作为起点。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="代码结构如果我们能为每个请求创建一个线程"></a>

#### 为每个请求创建一个线程

首先，让我们看看如果我们的代码为每个连接创建一个新的线程，那么代码会是什么样子。如前所述，由于可能存在无限创建线程的问题，这并不是我们的最终方案，但它是一个开始点，可以让我们先实现一个可运行的多线程服务器。之后，我们将引入线程池作为改进措施，这样对比这两种解决方案就会更加容易了。

清单21-11展示了需要对`main`进行的修改，以便在该循环内为每个流创建一个新的线程来处理它们。

<列表编号="21-11" 文件名称="src/main.rs" 标题="为每个流创建一个新的线程">

```rust,no_run
{{#rustdoc_include ../listings/ch21-web-server/listing-21-11/src/main.rs:here}}
```

</清单>

正如你在第16章中学到的那样，`thread::spawn`会创建一个新的线程，然后在新的线程中运行闭包中的代码。如果你运行这段代码，并在浏览器中加载_/sleep_，那么在另外两个浏览器标签页中加载_/_，你会发现对_/_的请求不必等待_/sleep_完成。然而，正如我们提到的，这样做最终会使系统不堪重负，因为你会无限制地创建新线程。

您可能还记得在第17章中提到过，这正是异步和await发挥作用的地方！在构建线程池时，请记住这一点，思考一下如果使用异步，情况会如何有所不同，或者是否保持不变。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="为无限数量的线程创建类似的界面"></a>

#### 创建有限数量的线程

我们希望我们的线程池能够以类似且熟悉的方式运行，这样在从单个线程切换到线程池时，不需要对使用我们API的代码进行大规模的修改。清单21-12展示了我们希望使用的`ThreadPool`结构的假设接口，而不是`thread::spawn`。

<列表编号="21-12" 文件名称="src/main.rs" 标题="我们理想的 `ThreadPool` 接口">

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch21-web-server/listing-21-12/src/main.rs:here}}
```

</清单>

我们使用 ``ThreadPool::new`` 来创建一个新的线程池，该线程池可以配置线程数量，在这个例子中是四个线程。然后，在 ``for`` 循环中，``pool.execute`` 的接口与 ``thread::spawn`` 类似，它接受一个闭包，这个闭包将被线程池中的每个线程执行。我们需要实现 ``pool.execute``，以便它能够接收这个闭包并将其传递给线程池中的某个线程来执行。这段代码目前还无法编译，但我们会尝试编译，以便编译器能够指导我们如何修复它。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="通过编译器驱动的开发来构建线程池结构"></a>

#### 使用编译器驱动的开发方式构建`ThreadPool`

请对清单21-12中的代码进行修改，将其改为`_src/main.rs_`。然后，我们可以利用``cargo check``产生的编译错误来指导我们的开发工作。这是我们遇到的第一个错误：

```console
{{#include ../listings/ch21-web-server/listing-21-12/output.txt}}
```

太好了！这个错误告诉我们我们需要一个 `ThreadPool` 类型或模块，所以我们现在就创建一个。我们的 `ThreadPool` 实现将独立于我们的网络服务器正在执行的工作类型。因此，让我们把 `hello` 包从二进制包改为库包，以存放我们的 `ThreadPool` 实现。在改为库包之后，我们还可以使用单独的线程池库来处理任何需要使用线程池的工作，而不仅仅是为了处理网络请求。

创建一个`_src/lib.rs_`文件，其中包含以下代码，这是目前我们能够定义的最简单的``ThreadPool``结构体的定义：

<listing file-name="src/lib.rs">

```rust,noplayground
{{#rustdoc_include ../listings/ch21-web-server/no-listing-01-define-threadpool-struct/src/lib.rs}}
```

</清单>

然后，编辑`_main.rs_`文件，将``ThreadPool``从库目录中引入到作用域内，方法是在`_src/main.rs_`文件的顶部添加以下代码：

<listing file-name="src/main.rs">

```rust,ignore
{{#rustdoc_include ../listings/ch21-web-server/no-listing-01-define-threadpool-struct/src/main.rs:here}}
```

</清单>

这段代码仍然无法运行，但让我们再次检查一下，以找出需要解决的下一个错误。

```console
{{#include ../listings/ch21-web-server/no-listing-01-define-threadpool-struct/output.txt}}
```

这个错误表明，接下来我们需要为`ThreadPool`创建一个名为`new`的关联函数。我们还知道，`new`需要有一个参数，该参数可以接受`4`作为参数，并且应该返回一个`ThreadPool`实例。让我们实现最简单的`new`函数，该函数具备这些特性：

<listing file-name="src/lib.rs">

```rust,noplayground
{{#rustdoc_include ../listings/ch21-web-server/no-listing-02-impl-threadpool-new/src/lib.rs}}
```

</清单>

我们选择 ``usize``作为``size``参数的类型，因为我们知道，线程数量为零是没有意义的。我们还知道，我们将使用这个``4``来表示线程集合中的元素数量，正如第3章的[“整数类型”][integer-types]章节中所讨论的那样，``usize``类型正是用于此目的的。

让我们再次检查这段代码：

```console
{{#include ../listings/ch21-web-server/no-listing-02-impl-threadpool-new/output.txt}}
```

现在出现错误的原因是，在 `ThreadPool` 上并没有 `execute` 这个方法。回想一下在[“创建有限数量的线程”](#creating-a-finite-number-of-threads)部分的内容，我们决定我们的线程池应该有一个类似于 `thread::spawn` 的接口。此外，我们还将实现 `execute` 函数，该函数接收给定的闭包，并将其交给线程池中的空闲线程来运行。

我们将在 `ThreadPool` 上定义 `execute` 方法，该方法接受一个闭包作为参数。回顾第13章中的[“将捕获的值移出闭包”][moving-out-of-closures]<!-- 忽略 -->，我们知道可以将闭包作为参数使用，但存在三种不同的特性：`Fn`、`FnMut` 和 `FnOnce`。我们需要决定在这里使用哪种类型的闭包。我们知道最终会采用类似于标准库中的 `thread::spawn` 的方式进行处理。因此，我们可以查看`thread::spawn`的签名对其参数的限制。文档中提供了以下信息：

```rust,ignore
pub fn spawn<F, T>(f: F) -> JoinHandle<T>
    where
        F: FnOnce() -> T,
        F: Send + 'static,
        T: Send + 'static,
```

`F`类型参数是我们在这里关注的；`T`类型参数与返回值相关，我们并不关心这一点。我们可以看到`spawn`使用`FnOnce`作为`F`的特质绑定。这可能也是我们所期望的，因为最终我们会将`execute`中得到的参数传递给`spawn`。我们可以进一步确认`FnOnce`正是我们需要的特质。因为用于执行请求的线程只会执行该请求的闭包一次，这与`FnOnce`中的`Once`是一致的。

类型参数`F`还具有绑定到`Send`的特性，以及生命周期绑定到`'static`。这些特性在我们的情况下非常有用：我们需要`Send`来将闭包从一个线程传递到另一个线程，同时还需要`'static`，因为我们不知道线程执行所需的时间。让我们在`ThreadPool`上创建一个`execute`方法，该方法接受一个类型为`F`的通用参数，并且具有如下限制：

<listing file-name="src/lib.rs">

```rust,noplayground
{{#rustdoc_include ../listings/ch21-web-server/no-listing-03-define-execute/src/lib.rs:here}}
```

</清单>

我们在 ``FnOnce``之后仍然使用``()``，因为``FnOnce``代表一个不接收参数且返回单位类型``()``的闭包。就像函数定义一样，返回类型可以在签名中省略，但即使没有参数，我们仍然需要括号。

再次说明，这是`execute`方法的最简单实现：它实际上并不执行任何操作，但我们只是想让代码能够编译通过而已。让我们再检查一下吧：

```console
{{#include ../listings/ch21-web-server/no-listing-03-define-execute/output.txt}}
```

它已经编译成功了！不过请注意，如果您尝试调用`cargo run`并在浏览器中发起请求，您将会看到我们在章节开头看到的那些错误。实际上，我们的库还没有调用传递给`execute`的闭包！

注意：关于使用严格编译器的语言，比如Haskell和Rust，人们常会听到这样一句话：“如果代码能够编译出来，那就说明它是正确的。”不过，这句话并不适用于所有情况。我们的项目能够成功编译，但实际上它根本没有任何功能！如果我们正在构建一个真正完整的项目，现在正是开始编写单元测试的时候，以确保代码不仅能够编译出来，而且其行为符合我们的期望。

考虑一下：如果我们选择执行未来操作，而不是使用闭包，那么情况会有所不同吗？

#### 验证`new`中的线程数量

我们并没有对 `new` 和 `execute` 的参数做任何处理。让我们按照想要的行为来实现这些函数的主体部分。首先，我们来考虑一下 `new`。之前，我们为 `size` 参数选择了一个无符号类型，因为线程数为负数的池是没有意义的。然而，线程数为零的池也是没有意义的，不过零本身其实是一个完全有效的数值。有效的 `usize`。我们将添加代码来检查 `size` 是否大于零，然后再返回 `ThreadPool` 的实例。如果程序接收到零值，我们将使用 `assert!` 宏来引发程序异常，如清单 21-13 所示。

<列表编号="21-13" 文件名称="src/lib.rs" 标题="实现`ThreadPool::new`，当`size`为零时触发panic">

```rust,noplayground
{{#rustdoc_include ../listings/ch21-web-server/listing-21-13/src/lib.rs:here}}
```

</清单>

我们还为我们的 `ThreadPool` 添加了一些文档注释。请注意，我们遵循了良好的文档编写规范，添加了一个部分来说明我们的函数可能会陷入恐慌的情况，具体内容可以在第14章中了解到。尝试运行 `cargo doc --open`，并点击 `ThreadPool` 结构，看看生成的 `new` 的文档是什么样子！

与其像这里那样添加`assert!`宏，我们还可以将`new`改为`build`，然后返回`Result`，就像我们在Listing 12-9中的I/O项目里对`Config::build`所做的那样。但在这种情况下，我们决定：尝试创建一个没有任何线程的线程池将会导致不可恢复的错误。如果你觉得有雄心壮志的话，试着编写一个名为`build`的函数。与`new`函数进行对比的签名：

```rust,ignore
pub fn build(size: usize) -> Result<ThreadPool, PoolCreationError> {
```

#### 创建存储空间以存放线程

现在我们已经有了一个方法来确认我们拥有的线程数量是有效的，可以存储到池中。接下来，我们可以创建这些线程，并将它们存储在`ThreadPool`结构中，然后再返回该结构。但是，我们该如何“存储”一个线程呢？让我们再看一下`thread::spawn`的签名：

```rust,ignore
pub fn spawn<F, T>(f: F) -> JoinHandle<T>
    where
        F: FnOnce() -> T,
        F: Send + 'static,
        T: Send + 'static,
```

`spawn`函数返回一个`JoinHandle<T>`类型的值，其中`T`是闭包所返回的类型。让我们也尝试使用`JoinHandle`，看看会发生什么。在我们的例子中，我们传递给线程池的闭包会处理连接操作，并不会返回任何内容，因此`T`将会是单位类型`()`。

清单21-14中的代码可以编译，但目前它并没有创建任何线程。我们修改了`ThreadPool`的定义，使其包含一个`thread::JoinHandle<()>`实例的向量；该向量被初始化为`size`的容量；同时设置了一个`for`循环，用于运行一些代码来创建线程；最后返回一个包含这些线程的`ThreadPool`实例。

<列表编号="21-14" 文件名称="src/lib.rs" 标题="创建一个向量，用于存放`ThreadPool`中的线程">

```rust,ignore,not_desired_behavior
{{#rustdoc_include ../listings/ch21-web-server/listing-21-14/src/lib.rs:here}}
```

</清单>

我们将 `std::thread` 引入库包的作用域中，因为我们在 `ThreadPool` 中使用了 `thread::JoinHandle` 作为向量中元素的类型。

一旦接收到有效的尺寸信息，我们的`ThreadPool`就会创建一个新的向量，该向量可以容纳`size`个元素。`with_capacity`函数执行的任务与`Vec::new`相同，但有一个重要的区别：它会在向量中预先分配空间。由于我们知道需要在向量中存储`size`个元素，因此提前进行这种分配比在插入元素时动态调整大小使用`Vec::new`要更高效。

当你再次运行`cargo check`时，应该会成功。

<a id="a-worker-struct-responsible-for-sending-code-from-the-threadpool-to-a-thread"></a>

#### 将`ThreadPool`中的代码发送到另一个线程

我们在 Listing 21-14 中的 `for` 循环中留下了一条关于线程创建的评论。在这里，我们将探讨如何实际创建线程。标准库提供了 `thread::spawn` 来创建线程，而 `thread::spawn` 则期望在线程创建后能够执行某些代码。然而，在我们的案例中，我们希望先创建线程，然后再等待稍后发送的代码来执行后续操作。标准库的……线程的实现并不包含任何实现这一功能的手段；我们必须手动进行实现。

我们将通过在`ThreadPool`与负责管理此新行为的线程之间引入一个新的数据结构来实现这一行为。我们将这个数据结构称为_Worker_，这是池化实现中常用的术语。`Worker`会选取需要运行的代码，并在其对应的线程中执行这些代码。

想象一下在餐厅厨房工作的人员：他们需要等待顾客下单，然后负责处理这些订单并完成相应的烹饪工作。

与其在线程池中存储`JoinHandle<()>`实例的向量，不如存储`Worker`结构的实例。每个`Worker`将存储一个`JoinHandle<()>`实例。然后，我们将在`Worker`上实现一个方法，该方法接受一个要运行的代码闭包，并将其发送到已经运行的线程中进行执行。此外，我们还会为每个`Worker`提供一个`id`结构，以便我们能够区分不同的实例。在日志或调试过程中，``Worker``的不同实例之间的区别。

这是当我们创建`ThreadPool`时将会发生的新流程。我们将实现一段代码，在通过`Worker`进行设置之后，将闭包发送到线程中。

1. 定义一个 `Worker` 结构体，该结构体包含一个 `id` 和一个 `JoinHandle<()>`。  
2. 将 `ThreadPool` 修改为存储一个由 `Worker` 实例组成的向量。  
3. 定义一个 `Worker::new` 函数，该函数接受一个 `id` 数字，并返回一个 `Worker` 实例，该实例包含 `id` 以及一个使用空闭包创建的线程。  
4. 在 `ThreadPool::new` 中，使用 `for` 的循环计数器来生成 `id`，并进行创建操作。使用那个`id`创建一个新的`Worker`，并将`Worker`存储到向量中。

如果你愿意接受挑战，请在查看清单21-15中的代码之前，尝试自己实施这些更改。

准备好了吗？以下是Listing 21-15，其中介绍了一种进行上述修改的方法。

<列表编号="21-15" 文件名称="src/lib.rs" 标题="修改 `ThreadPool` 以存储 `Worker` 实例，而不是直接存储线程">

```rust,noplayground
{{#rustdoc_include ../listings/ch21-web-server/listing-21-15/src/lib.rs:here}}
```

</清单>

我们将 `ThreadPool` 中的字段名称从 `threads` 更改为 `workers`。因为现在它存储的是 `Worker` 实例，而不是 `JoinHandle<()>` 实例。我们在 `for` 循环中使用这个计数器作为 `Worker::new` 的参数，并将每个新的 `Worker` 存储在名为 `workers` 的向量中。

外部代码（比如我们的服务器中的`_src/main.rs_`文件）不需要了解在 ``ThreadPool``中使用``Worker``结构的实现细节，因此我们将``Worker``结构及其``new``函数设为私有成员。``Worker::new``函数使用我们提供的``id``，并存储一个通过创建新线程并使用空闭包而生成的``JoinHandle<()>``实例。

注意：如果操作系统由于系统资源不足而无法创建线程，那么`thread::spawn`将会引发异常。这将导致整个服务器崩溃，尽管某些线程的创建可能成功。为了简单起见，这种行为是可以接受的，但在实际的生产环境线程池实现中，你通常会使用[`std::thread::Builder`][builder]<!-- 忽略 -->。>[`spawn`][builder-spawn]<!-- 忽略 --> 该方法返回的是 `Result`。

这段代码将会被编译，并且会存储我们作为参数传递给`ThreadPool::new`的`Worker`实例的数量。不过，我们仍然没有处理在`execute`中得到的闭包。接下来，我们将看看如何解决这个问题。

#### 通过通道向线程发送请求

下一个需要解决的问题是，分配给`thread::spawn`的闭包根本没有任何作用。目前，我们能够得到那个想要在`execute`方法中执行的闭包。但是，当我们在创建`ThreadPool`的过程中创建每个`Worker`时，我们需要给`thread::spawn`一个闭包来使其能够运行。

我们希望刚刚创建的`Worker`结构体能够从存储在`ThreadPool`队列中获取要运行的代码，并将该代码发送到相应的线程中进行执行。

我们在第16章中了解的通道——一种在两个线程之间进行通信的简单方式——非常适合这种应用场景。我们将使用通道作为任务的队列，而`execute`会将任务从`ThreadPool`发送到`Worker`实例，后者再将任务发送到相应的线程中。以下是具体的实施方案：

1. ``ThreadPool``将创建一个通道并保存发送者信息。  
2. 每个 ``Worker``会保存接收者信息。  
3. 我们将创建一个新的 ``Job``结构，用来保存我们想通过通道传递的闭包。  
4. ``execute``方法会通过发送者来发送它想要执行的任务。  
5. 在其线程中，``Worker``会遍历其接收者，并执行它们接收到的任何任务的闭包。

让我们从在`ThreadPool::new`中创建一个频道开始，并将发送者存储在`ThreadPool`实例中，如清单21-16所示。目前，`Job`结构体并不包含任何内容，但将来它将是我们通过频道发送内容的类型。

<列表编号="21-16" 文件名称="src/lib.rs" 标题="修改 `ThreadPool` 以存储发送通道的发送者，该通道传输 `Job` 实例">

```rust,noplayground
{{#rustdoc_include ../listings/ch21-web-server/listing-21-16/src/lib.rs:here}}
```

</清单>

在`ThreadPool::new`中，我们创建了新频道，并让pool对象持有发送者。这样就能成功编译了。

让我们尝试将通道的接收者作为参数传递给每个`Worker`，因为线程池会创建这个通道。我们知道希望在这些`Worker`实例所创建的线程中使用接收者，因此我们在闭包中引用`receiver`参数。清单21-17中的代码目前还无法编译成功。

<列表编号="21-17" 文件名称="src/lib.rs" 标题="将接收者传递给每个`Worker`">

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch21-web-server/listing-21-17/src/lib.rs:here}}
```

</清单>

我们做了一些简单直接的修改：我们将接收者传递给`Worker::new`，然后在闭包内部使用它。

当我们尝试检查这段代码时，出现了这个错误：

```console
{{#include ../listings/ch21-web-server/listing-21-17/output.txt}}
```

这段代码试图将`receiver`传递给多个`Worker`实例。这是不可行的，正如我们在第16章中所提到的：Rust的通道实现是一个多个_生产者_、一个_消费者_的结构。这意味着我们无法简单地克隆通道的接收端来修复这段代码。此外，我们也不希望向多个消费者发送相同的消息多次；我们希望有一个消息列表，其中包含多个`Worker`实例，这样每条消息都能被处理一次。

此外，将某个任务从通道队列中移除会修改`receiver`，因此线程需要一种安全的方式来共享和修改`receiver`；否则，可能会出现竞态条件（如第16章所述）。

请回想一下第16章中讨论的线程安全智能指针：为了在多个线程之间共享所有权，并允许线程修改值，我们需要使用`Arc<Mutex<T>>`。`Arc`类型允许多个`Worker`实例拥有接收者，而`Mutex`则确保一次只有一个`Worker`可以从接收者那里获取操作。列表21-18展示了我们需要进行的修改。

<列表编号="21-18" 文件名称="src/lib.rs" 标题="使用 `Arc` 和 `Mutex` 在 `Worker` 实例之间共享接收器">

```rust,noplayground
{{#rustdoc_include ../listings/ch21-web-server/listing-21-18/src/lib.rs:here}}
```

</清单>

在`ThreadPool::new`中，我们将接收者放入`Arc`和`Mutex`中。对于每个新的`Worker`实例，我们都会克隆`Arc`，以增加引用计数，从而使`Worker`实例能够共享对接收者的所有权。

经过这些修改后，代码可以编译了！我们即将成功！

#### 实现`execute`方法

最后，让我们在`ThreadPool`上实现`execute`方法。同时，我们将`Job`从结构体改为类型别名，用于表示`execute`所接收的闭包的类型。正如第20章中的[“类型同义词与类型别名”][type-aliases]部分所讨论的，类型别名可以帮助我们简化复杂的类型名称，使其更易于使用。请查看清单21-19。

<listing number="21-19" file-name="src/lib.rs" caption="为包含每个闭包的`Box`创建一个`Job`类型的别名，然后将该任务通过通道发送">

```rust,noplayground
{{#rustdoc_include ../listings/ch21-web-server/listing-21-19/src/lib.rs:here}}
```

</清单>

在使用在`execute`中获得的闭包创建新的`Job`实例之后，我们将这项任务发送到通道的另一端。如果发送失败，我们会调用`unwrap`来处理这种情况。这种情况可能发生在我们所有的线程都停止执行时，也就是说，接收端已经停止接收新消息了。目前，我们无法停止线程的执行：只要池还存在，我们的线程就会继续执行。我们使用 ``unwrap`` 的原因在于，我们知道这种失败情况不会发生，但编译器并不确定这一点。

但是，我们还没有完成！在`Worker`中，我们的闭包被传递给`thread::spawn`时，它仍然只是_引用_通道的接收端。相反，我们需要让这个闭包无限循环，不断向通道的接收端请求任务，并在接收到任务时执行该任务。让我们把清单21-20中所展示的修改应用到`Worker::new`上。

<列表编号="21-20" 文件名称="src/lib.rs" 标题="在`Worker`实例的线程中接收并执行任务">

```rust,noplayground
{{#rustdoc_include ../listings/ch21-web-server/listing-21-20/src/lib.rs:here}}
```

</清单>

在这里，我们首先对`receiver`调用`lock`来获取互斥锁，然后在对`unwrap`的调用中，会在出现错误时引发恐慌。如果互斥锁处于“中毒”状态，获取锁可能会失败。这种情况可能发生在其他线程在持有锁时没有释放锁的情况下导致其他线程发生恐慌。在这种情况下，调用`unwrap`来使该线程引发恐慌是正确的操作。请随时提问。将这段代码``unwrap``替换为``expect``，并添加一条对你来说有意义的错误信息。

如果我们成功获得了互斥锁，就会调用`recv`来从通道中接收`Job`。最后的`unwrap`可以处理任何可能出现的错误，这些错误可能发生在持有发送者的线程关闭时。类似于`send`方法在接收者关闭时返回`Err`的情况。

对`recv`的调用会阻塞线程，因此如果没有任务可用，当前线程将等待直到有任务出现。`Mutex<T>`则确保一次只有一个`Worker`线程尝试请求任务。

我们的线程池现在已经处于正常工作状态了！请执行一个`cargo run`，然后发起一些请求：

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

成功！我们现在拥有一个可以异步执行连接的线程池。创建的线程数量永远不会超过四个，因此当服务器收到大量请求时，系统也不会出现过载的情况。如果我们向_/sleep_发起请求，服务器可以通过另一个线程来处理其他请求，从而继续服务其他客户。

注意：如果您同时在多个浏览器窗口中打开`_/sleep_`页面，它们可能会以每五秒一次的频率依次加载。某些网络浏览器出于缓存考虑，会顺序执行同一请求的多个实例。这种限制并非由我们的网络服务器引起。

现在是暂停并思考一下，如果使用未来函数而不是闭包来指定需要执行的任务，那么 Listing 21-18、21-19 和 21-20 中的代码将会有何不同的时候。哪些类型会发生变化？方法签名是否会有所不同，如果有变化的话，具体是怎样的？代码的哪些部分保持不变呢？

在了解了第17章和第19章中的`while let`循环之后，你可能会好奇为什么我们没有像清单21-21中那样编写`Worker`线程代码。

<列表编号="21-21" 文件名称="src/lib.rs" 标题="使用 `while let` 实现 `Worker::new` 的另一种方法">

```rust,ignore,not_desired_behavior
{{#rustdoc_include ../listings/ch21-web-server/listing-21-21/src/lib.rs:here}}
```

</清单>

这段代码可以编译并运行，但并没有达到预期的线程处理效果：一个较慢的请求仍然会导致其他请求等待处理。原因有些微妙：`Mutex`结构体没有公开的`unlock`方法，因为锁的所有权取决于`LockResult<MutexGuard<T>>`中`MutexGuard<T>`的生命周期，而`lock`方法则负责返回该生命周期。在编译时，借用检查器可以强制执行这一规则。也就是说，除非我们持有锁，否则无法访问由`Mutex`保护的资源。然而，如果我们不注意`MutexGuard<T>`的生命周期，这种实现方式可能会导致锁被持有的时间超过预期。

在清单21-20中的代码使用了`let job = receiver.lock().unwrap().recv().unwrap();` works because with `let`，等号右边表达式中使用过的所有临时值会在``let``语句结束后立即被丢弃。然而，`while let` (and ` if let` and ` match`)则不会在相关代码块结束之前丢弃临时值。在清单21-21中，锁会一直保持锁定状态直到代码执行完毕。调用`job()`，这意味着其他`Worker`实例无法接收任务。

[type-aliases]: ch20-03-advanced-types.html#type-synonyms-and-type-aliases
[整数类型]: ch03-02-data-types.html#integer-types
[移出闭包]: ch13-01-closures.html#moving-captured-values-out-of-closures
[构建器]:../std/thread/struct.Builder.html
[构建器启动]:../std/thread/struct.Builder.html#method.spawn