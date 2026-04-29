## 无法恢复的与`panic!`相关的错误

有时候，你的代码中会发生一些糟糕的事情，而对此你无能为力。在这种情况下，Rust提供了`panic!`宏。实际上，有两种方式会导致程序崩溃：一种是执行某个导致程序崩溃的操作（比如访问数组的末尾元素），另一种则是显式调用`panic!`宏。在这两种情况下，程序都会崩溃。默认情况下，这些崩溃会打印出错误信息，然后重新初始化程序，清理栈内存，并终止程序。你还可以通过环境变量让Rust在崩溃时显示调用栈，这样就能更容易地找到崩溃的根源。

> ### 在发生恐慌时展开栈或立即终止程序
>
> 默认情况下，当发生恐慌时，程序会开始“展开栈”，即Rust会沿着栈的回溯方向执行，并清理每个函数所占用的数据。然而，这种操作非常耗时。因此，Rust允许您选择立即“终止”程序，从而无需进行清理操作。
>
> 此时，程序所使用的内存将由操作系统负责清理。如果您希望生成的二进制文件尽可能小，可以在_Cargo.toml_文件中将`panic = 'abort'`添加到相应的`[profile]`部分，从而在发生恐慌时选择终止程序。例如，如果您希望在发布模式下发生恐慌时立即终止程序，可以添加如下代码：
>
> ```toml
> [profile.release]
> panic = 'abort'
> ```

让我们尝试在一个简单的程序中调用`panic!`：

<code listing file-name="src/main.rs">

```rust,should_panic,panics
{{#rustdoc_include ../listings/ch09-error-handling/no-listing-01-panic/src/main.rs}}
```

</ Listing>

当你运行这个程序时，你会看到类似这样的结果：

```console
{{#include ../listings/ch09-error-handling/no-listing-01-panic/output.txt}}
```

调用 `panic!` 会导致最后两行中出现错误信息。第一行显示了我们的恐慌信息，以及代码中发生恐慌的位置：_src/main.rs:2:5_ 表示这是 _src/main.rs_ 文件的第二行，第五个字符的位置。

在这种情况下，所指示的那一行是我们代码的一部分。如果我们进入那一行代码，就会看到`panic!`宏的调用。在其他情况下，`panic!`的调用可能出现在我们代码调用的代码中，而错误信息中报告的文件名和行号则指向其他人的代码，在那里调用了`panic!`宏，而不是最终导致`panic!`调用的那一行代码。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="使用恐慌回溯路径"></a>

我们可以利用 `panic!` 所调用的函数的调用链来找出导致问题的代码部分。为了了解如何使用 `panic!` 的调用链，让我们来看另一个例子，看看当 `panic!` 的调用来自库中的代码时会发生什么——这种情况是由于我们的代码存在错误，而不是因为代码直接调用了宏。清单 9-1 中有一段代码，它试图访问向量中超出有效索引范围的索引。

<列表编号="9-1" 文件名称="src/main.rs" 标题="尝试访问向量末尾之外的元素，这将导致调用`panic!`">

```rust,should_panic,panics
{{#rustdoc_include ../listings/ch09-error-handling/listing-09-01/src/main.rs}}
```

</ Listing>

在这里，我们试图访问向量中的第100个元素（因为索引是从0开始的，所以实际上是第99个位置），但向量实际上只有三个元素。在这种情况下，Rust会抛出panic异常。使用`[]`应该是用来返回一个元素的，但是如果你传递了一个无效的索引，那么Rust无法返回任何有效的元素。

在C语言中，试图读取超过数据结构末尾的数据属于未定义行为。你可能会读到内存中与该数据结构中的元素相对应的内容，尽管该内存并不属于该数据结构。这种现象被称为“缓冲区越读”，如果攻击者能够操纵索引，从而读取到不应该被允许的数据，那么可能会导致安全漏洞。

为了保护你的程序免受这种漏洞的影响，如果你尝试读取一个不存在的索引处的元素，Rust会停止执行并拒绝继续执行。让我们试试看：

```console
{{#include ../listings/ch09-error-handling/listing-09-01/output.txt}}
```

这个错误出现在我们的 `_main.rs_`文件的第4行，我们试图在`v`中访问向量中的第99个索引。

`note:`这一行告诉我们，我们可以设置`RUST_BACKTRACE`环境变量，以获取导致错误的确切原因的相关调用链信息。一个调用链是一个列表，其中包含了所有被调用以到达这一点的函数。在Rust中，调用链的工作原理与其他语言相同：读取调用链的关键在于从顶部开始，一直读到你编写过的代码。那些位于问题起始位置的行，就是你的代码调用的代码；而位于其下方的行则是调用了你的代码的代码。这些前后相关的行可能包含核心Rust代码、标准库代码，或者你正在使用的其他库。让我们尝试通过设置`RUST_BACKTRACE`环境变量为除`0`之外的任何值来获取调用链信息。清单9-2展示了与你所看到的类似的结果。

<!-- 手动重新生成
cd listings/ch09-error-handling/listing-09-01
RUST_BACKTRACE=1 cargo run
复制下面显示的回溯信息
检查列表下方文本中提到的回溯编号
-->

<列表编号="9-2" 标题="当环境变量 `RUST_BACKTRACE` 被设置时，调用 `panic!` 生成的回溯信息">

```console
$ RUST_BACKTRACE=1 cargo run
thread 'main' panicked at src/main.rs:4:6:
index out of bounds: the len is 3 but the index is 99
stack backtrace:
   0: rust_begin_unwind
             at /rustc/4d91de4e48198da2e33413efdcd9cd2cc0c46688/library/std/src/panicking.rs:692:5
   1: core::panicking::panic_fmt
             at /rustc/4d91de4e48198da2e33413efdcd9cd2cc0c46688/library/core/src/panicking.rs:75:14
   2: core::panicking::panic_bounds_check
             at /rustc/4d91de4e48198da2e33413efdcd9cd2cc0c46688/library/core/src/panicking.rs:273:5
   3: <usize as core::slice::index::SliceIndex<[T]>>::index
             at file:///home/.rustup/toolchains/1.85/lib/rustlib/src/rust/library/core/src/slice/index.rs:274:10
   4: core::slice::index::<impl core::ops::index::Index<I> for [T]>::index
             at file:///home/.rustup/toolchains/1.85/lib/rustlib/src/rust/library/core/src/slice/index.rs:16:9
   5: <alloc::vec::Vec<T,A> as core::ops::index::Index<I>>::index
             at file:///home/.rustup/toolchains/1.85/lib/rustlib/src/rust/library/alloc/src/vec/mod.rs:3361:9
   6: panic::main
             at ./src/main.rs:4:6
   7: core::ops::function::FnOnce::call_once
             at file:///home/.rustup/toolchains/1.85/lib/rustlib/src/rust/library/core/src/ops/function.rs:250:5
note: Some details are omitted, run with `RUST_BACKTRACE=full` for a verbose backtrace.
```

</ Listing>

这确实会产生大量的输出！您看到的输出可能会因您的操作系统和Rust版本而有所不同。为了获得包含这些信息的回溯信息，必须启用调试符号。当使用`cargo build`或`cargo run`且不包含`--release`标志时，调试符号默认是启用的，就像我们在这里所做的那样。

在 Listing 9-2 的输出中，回溯跟踪的第 6 行指向了我们项目中导致问题的那一行代码：即 _src/main.rs_ 的第 4 行。如果我们不想让程序出现 panic 情况，就应该从第一行所指向的位置开始调查，该位置所指向的文件就是我们故意编写导致 panic 的代码所在的位置。在 Listing 9-1 中，我们故意编写了会导致 panic 的代码，解决这个问题的办法就是不要请求向量索引范围之外的元素。将来，当你的代码出现 panic 时，你需要弄清楚是哪些操作以及使用哪些值导致了 panic，然后确定代码应该采取什么措施来避免这种情况的发生。

我们将在后面讨论何时以及何不使用`panic!`来处理[“是否转向`panic!`还是`panic!`”][to-panic-or-not-to-panic]这一章节中的错误情况。接下来，我们将探讨如何利用`Result`来从错误中恢复。

[是否应该恐慌：ch09-03_是否应该恐慌.html#是否应该恐慌]