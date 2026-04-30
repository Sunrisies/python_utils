## 接受命令行参数

让我们像往常一样，使用 `cargo new` 创建一个新的项目。我们将这个项目命名为 `minigrep`，以便与您系统中可能已经存在的 `grep` 工具区分开来。

```console
$ cargo new minigrep
     Created binary (application) `minigrep` project
$ cd minigrep
```

第一个任务就是让 `minigrep` 能够接受两个命令行参数：文件路径和用于搜索的字符串。也就是说，我们希望能够这样运行我们的程序：使用 `cargo run`，两个连字符来表示后续参数属于程序本身，而不是 `cargo`，即用于搜索的字符串，以及要搜索的文件的路径。

```console
$ cargo run -- searchstring example-filename.txt
```

目前，由 `cargo new` 生成的程序无法处理我们传递给它的参数。在 [crates.io](https://crates.io/) 上有一些现有的库可以帮助编写能够接受命令行参数的程序，但由于你刚刚开始学习这个概念，让我们自己来实现这个功能吧。

### 读取参数值

为了使得 `minigrep` 能够读取我们传递给它的命令行参数的值，我们需要使用 Rust 标准库中的 `std::env::args` 函数。该函数返回一个迭代器，其中包含了传递给 `minigrep` 的命令行参数。我们将在[第13章][ch13]<!-- ignore
-->中详细讨论迭代器。目前，你只需要了解关于迭代器的两个要点：迭代器会生成一系列值，并且我们可以调用 `collect` 方法来将迭代器转换为一个集合，比如向量，从而包含所有由迭代器生成的元素。

清单 12-1 中的代码使你的 `minigrep` 程序能够读取传递给它的任何命令行参数，并将这些值收集到一个向量中。

<Listing number="12-1" file-name="src/main.rs" caption="Collecting the command line arguments into a vector and printing them">

```rust
use std::env;

fn main() {
    let args: Vec<String> = env::args().collect();
    dbg!(args);
}

```

</Listing>

首先，我们通过使用 `use` 语句将 `std::env` 模块引入作用域，这样我们就可以使用它的 `args` 函数。请注意， `std::env::args` 函数嵌套在两个级别的模块中。正如我们在 [第7章][ch7-idiomatic-use]<!-- ignore --> 中讨论的那样，当所需函数嵌套在多个模块中时，我们选择将父模块引入作用域，而不是直接调用该函数。这样做可以让我们更方便地使用 `std::env` 中的其他函数。此外，这种方式比添加 `use std::env::args` 后再使用 `args` 来调用该函数更为清晰，因为 `args` 很容易被误认为是当前模块中定义的函数。

> ### `args`函数与无效的Unicode字符
>
> 请注意，如果任何参数包含无效的Unicode字符， `std::env::args`函数将会引发panic。如果您的程序需要接受包含无效Unicode字符的参数，请使用 `std::env::args_os`函数。该函数返回一个迭代器，该迭代器返回的是 `OsString`类型的值，而不是 `String`类型的值。为了简单起见，我们在这里选择使用 `std::env::args`函数，因为 `OsString`类型的值因平台而异，且比 `String`类型的值更难以处理。

在 `main` 的第一行中，我们调用 `env::args`，并立即使用 `collect` 将迭代器转换为一个包含所有生成值的向量。我们可以使用 `collect` 函数来创建多种类型的集合，因此我们会明确标注 `args` 的类型，以指定我们希望得到一个字符串的向量。虽然在 Rust 中很少需要标注类型，但 `collect` 是一个经常需要标注的函数，因为 Rust 无法推断出你想要的集合类型。

最后，我们使用调试宏来打印这个向量。我们先尝试在没有参数的情况下运行代码，然后再尝试在有两个参数的情况下运行。

```console
$ cargo run
   Compiling minigrep v0.1.0 (file:///projects/minigrep)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.61s
     Running `target/debug/minigrep`
[src/main.rs:5:5] args = [
    "target/debug/minigrep",
]

```

```console
$ cargo run -- needle haystack
   Compiling minigrep v0.1.0 (file:///projects/minigrep)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 1.57s
     Running `target/debug/minigrep needle haystack`
[src/main.rs:5:5] args = [
    "target/debug/minigrep",
    "needle",
    "haystack",
]

```

请注意，向量中的第一个值是 `"target/debug/minigrep"`，这是我们二进制文件的名称。这与C语言中参数列表的行为相匹配，允许程序在执行过程中使用其被调用的名称。通常，能够访问程序名称是非常方便的，因为这样可以将其打印在消息中，或者根据用于调用程序的命令行别名来改变程序的行为。不过，对于本章的目的而言，我们暂时忽略这一点，只关注我们需要的两个参数。

### 将参数值保存在变量中

该程序目前能够访问作为命令行参数指定的值。现在我们需要将这两个参数的值保存到变量中，这样我们就可以在整个程序中使用这些值了。我们在清单 12-2 中实现了这一功能。

<Listing number="12-2" file-name="src/main.rs" caption="Creating variables to hold the query argument and file path argument">

```rust,should_panic,noplayground
use std::env;

fn main() {
    let args: Vec<String> = env::args().collect();

    let query = &args[1];
    let file_path = &args[2];

    println!("Searching for {query}");
    println!("In file {file_path}");
}

```

</Listing>

当我们打印这个向量时，可以看到程序的名称占据了向量中 `args[0]` 位置的值，因此我们从索引1开始传递参数。第一个参数 `minigrep` 是我们正在搜索的字符串，因此我们将对这个字符串的引用存储在变量 `query` 中。第二个参数则是文件路径，因此我们将对这个路径的引用存储在变量 `file_path` 中。

我们暂时打印这些变量的值，以证明代码按我们的意图正常运行。让我们再次运行这个程序，这次使用参数 `test` 和 `sample.txt`。

```console
$ cargo run -- test sample.txt
   Compiling minigrep v0.1.0 (file:///projects/minigrep)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.0s
     Running `target/debug/minigrep test sample.txt`
Searching for test
In file sample.txt

```

太好了，程序运行正常！我们需要的参数的值已经被保存到正确的变量中。之后我们会添加一些错误处理功能，以应对某些可能出现的问题，比如用户没有提供任何参数的情况。目前，我们暂时忽略这种情况，而是继续开发文件读取功能。

[ch13]: ch13-00-functional-features.html
[ch7-idiomatic-use]: ch07-04-bringing-paths-into-scope-with-the-use-keyword.html#creating-idiomatic-use-paths
