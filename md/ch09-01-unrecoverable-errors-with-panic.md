## 无法恢复的与`panic!`相关的错误

有时候，代码中会发生一些糟糕的事情，而我们无法对此做出任何改变。在这种情况下，Rust提供了`panic!`宏。实际上，有两种方式会导致程序出现恐慌：一种是执行某个可能导致程序崩溃的操作（例如访问数组的超出范围的元素），另一种则是显式调用`panic!`宏。在这两种情况下，我们都会让程序陷入恐慌状态。默认情况下，这些恐慌会打印出错误信息，然后重新初始化程序，清理堆栈，并最终退出程序。环境变量允许在出现panic时，Rust能够显示调用栈，从而更容易追踪panic的来源。

> ### 在出现恐慌时展开栈或立即终止程序>> 默认情况下，当发生恐慌时，程序会开始“展开栈”，也就是说，Rust会沿着栈的层次结构返回，并清理每个函数所占用的数据。然而，这种操作非常繁琐。因此，Rust允许您选择立即“终止”程序，从而无需进行清理操作。>> 此时，程序所使用的内存就需要由其他机制来清理了。操作系统。如果在您的项目中需要尽可能减小生成的二进制文件的大小，可以在您的_Cargo.toml_文件中，将`panic = 'abort'`添加到相应的`[profile]`部分，从而在出现恐慌时从展开状态切换到中止状态。例如，如果您希望在发布模式下在出现恐慌时中止程序，可以添加如下代码：>> ```toml
> [profile.release]
> panic = 'abort'
> ```

让我们尝试在简单的程序中调用`panic!`：

<listing file-name="src/main.rs">

```rust,should_panic,panics
{{#rustdoc_include ../listings/ch09-error-handling/no-listing-01-panic/src/main.rs}}
```

</清单>

当你运行这个程序时，你会看到类似这样的结果：

```console
{{#include ../listings/ch09-error-handling/no-listing-01-panic/output.txt}}
```

调用`panic!`会导致最后两行出现错误消息。第一行显示了我们的恐慌信息，以及恐慌在源代码中的位置：_src/main.rs:2:5_表示这是我们的_src/main.rs文件的第二行，第五个字符的位置。

在这种情况下，所指示的那一行是我们代码的一部分。如果我们进入那一行代码，就会看到`panic!`宏的调用。在其他情况下，`panic!`的调用可能出现在我们代码调用的其他代码中，而错误信息中报告的文件名和行号则指向另一个人的代码，在那里调用了`panic!`宏，而不是最终导致`panic!`调用的那一行代码。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="使用恐慌回溯路径"></a>

我们可以利用`panic!`所调用的函数的调用链，来找出导致问题的代码部分。为了了解如何使用`panic!`的调用链，让我们来看另一个例子，看看当`panic!`的调用来自库中的代码时，情况会如何——这种情况是由于我们的代码中存在错误，而不是因为代码直接调用了宏。清单9-1中有一段代码，它试图访问向量中超出有效索引范围的索引。

<列表编号="9-1" 文件名称="src/main.rs" 标题="尝试访问向量末尾之外的元素，这将导致调用`panic!`">

```rust,should_panic,panics
{{#rustdoc_include ../listings/ch09-error-handling/listing-09-01/src/main.rs}}
```

</清单>

在这里，我们试图访问向量中的第100个元素（因为索引是从0开始的，所以实际上是指向第99个位置），但向量实际上只有三个元素。在这种情况下，Rust会触发panic。使用`[]`应该是为了返回一个元素，但如果传递了一个无效的索引，那么Rust无法返回任何有效的元素。

在C语言中，试图读取超出数据结构末尾的数据会导致未定义的行为。你可能会得到存储在该位置的内存中的任何内容，即使该内存并不属于该数据结构。这种现象被称为“缓冲区溢出”，如果攻击者能够操纵索引，从而读取到不应该被允许的数据，那么就可能引发安全漏洞。

为了保护你的程序免受这种漏洞的影响，如果你尝试读取一个不存在的索引处的元素，Rust会停止执行并拒绝继续运行。让我们试试看：

```console
{{#include ../listings/ch09-error-handling/listing-09-01/output.txt}}
```

这个错误出现在我们的`_main.rs_`文件的第4行，我们试图在`v`中访问向量中的第99个索引。

`note:`这一行告诉我们，可以将`RUST_BACKTRACE`环境变量设置为获取导致错误的详细追踪信息。A_backtrace_是一个列表，其中包含了所有被调用以到达这一点的函数。在Rust中，回溯功能的实现与其他语言类似：读取回溯信息的关键是从顶部开始，一直读到你编写代码的地方为止。那里就是问题的起源点。上述提到的问题所在的那几行代码这些是你的代码所调用的代码；下面的行则是调用了你的代码的代码。这些前后对比的代码可能包括核心Rust代码、标准库代码，或者你正在使用的各种库。让我们尝试通过将`RUST_BACKTRACE`环境变量设置为除`0`之外的任何值来获取调用链信息。清单9-2展示了与你所看到的类似的输出。

<!-- 手动重新生成
cd listings/ch09-error-handling/listing-09-01
RUST_BACKTRACE=1 cargo run
复制下面的回溯信息
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

</清单>

这确实会产生大量的输出！您看到的输出可能会因您的操作系统和Rust版本而有所不同。为了获得包含这些信息的回溯信息，必须启用调试符号。当使用`cargo build`或`cargo run`且未使用`--release`标志时，调试符号默认是启用的，就像我们在这里所做的那样。

在清单9-2的输出中，回溯跟踪的第6行指向了ourproject项目中导致问题的那一行代码：即_src/main.rs文件的第4行。如果我们不希望程序出现恐慌情况，那么我们应该从第一行提到的、我们编写的文件所在的位置开始排查问题。在清单9-1中，我们故意编写了会导致程序恐慌的代码，解决这种恐慌的方法就是不要请求超出向量索引范围的某个元素。当你的代码在未来出现恐慌情况时，你需要弄清楚代码正在执行哪些操作，使用哪些值会导致恐慌，以及代码应该采取什么措施来应对这种情况。

我们将在后面讨论何时以及何不使用`panic!`来处理[“是否转向`panic!`还是`panic!`”][to-panic-or-not-to-panic]这一章节中的错误情况。接下来，我们将探讨如何利用`Result`来从错误中恢复。

[是否应该感到恐慌]: ch09-03_是否应该感到恐慌.html#是否应该感到恐慌