## 接受命令行参数

让我们创建一个新的项目，继续使用`cargo new`作为项目名称。我们将这个项目命名为`minigrep`，以便与您系统中可能已经存在的`grep`工具区分开来。

```console
$ cargo new minigrep
     Created binary (application) `minigrep` project
$ cd minigrep
```

第一个任务就是让 `minigrep` 能够接受它的两个命令行参数：文件路径和用于搜索的字符串。也就是说，我们希望能够使用 `cargo run` 来运行我们的程序，其中两个连字符表示接下来的参数是用于我们的程序，而不是用于 `cargo`；此外，还需要一个用于搜索的字符串，以及一个要搜索的文件的路径，格式如下：

```console
$ cargo run -- searchstring example-filename.txt
```

目前，由`cargo new`生成的程序无法处理我们提供的参数。在[crates.io](https://crates.io/)上有一些现有的库可以帮助编写能够接受命令行参数的程序，但由于您刚刚开始学习这个概念，让我们自己来实现这个功能吧。

### 读取参数值

为了使得`minigrep`能够读取我们传递给它的命令行参数的值，我们需要使用Rust标准库中的`std::env::args`函数。该函数返回一个迭代器，其中包含了传递给`minigrep`的命令行参数。我们将在[第13章][ch13]中详细讨论迭代器。目前，你只需要了解关于迭代器的两个要点：迭代器会生成一系列值，并且我们可以在一个迭代器上调用`collect`方法。将其转换为一个集合，例如一个向量，其中包含迭代器产生的所有元素。

清单12-1中的代码使你的`minigrep`程序能够读取传递给它的任何命令行参数，并将这些值收集到一个向量中。

<列表编号="12-1" 文件名称="src/main.rs" 标题="将命令行参数收集到向量中并打印出来">

```rust
{{#rustdoc_include ../listings/ch12-an-io-project/listing-12-01/src/main.rs}}
```

</清单>

首先，我们通过使用 `use` 语句将 `std::env` 模块引入作用域，这样我们就可以使用它的 `args` 函数。请注意，`std::env::args` 函数嵌套在两层模块中。正如我们在[Chapter7][ch7-idiomatic-use]<!-- ignore -->中所讨论的，当所需的函数嵌套在多个模块中时，我们选择将父模块引入作用域，而不是直接引入该函数。这样做可以让我们更轻松地使用其他函数。从`std::env`开始。与添加`use std::env::args`然后仅使用`args`调用该函数相比，这种方式也更为清晰明了。因为`args`很容易被误认为是当前模块中定义的函数。

> ### `args`函数与无效的Unicode  
请注意，如果任何参数包含无效的Unicode字符，`std::env::args`将会引发异常。如果你的程序需要接受包含无效Unicode参数的情况，建议使用`std::env::args_os`函数。该函数返回一个迭代器，能够生成`OsString`对应的值，而不是`String`对应的值。出于简单性的考虑，我们在这里选择了使用`std::env::args`；因为`OsString`对应的值会有所不同。> 这些平台比`String`值更复杂，也更难以处理。

在`main`的第一行中，我们调用了`env::args`，并且立即使用`collect`将迭代器转换为一个包含所有生成值的向量。我们可以使用`collect`函数来创建多种类型的集合，因此我们会明确标注`args`的类型，以指定我们希望得到一个字符串的向量。虽然你很少需要标注类型……在Rust中，`collect`这个函数通常需要被标注，因为Rust无法推断出你想要使用的集合类型。

最后，我们使用调试宏来打印这个向量。我们先尝试在没有参数的情况下运行代码，然后再尝试使用两个参数来运行。

```console
{{#include ../listings/ch12-an-io-project/listing-12-01/output.txt}}
```

```console
{{#include ../listings/ch12-an-io-project/output-only-01-with-args/output.txt}}
```

请注意，向量中的第一个值是`"target/debug/minigrep"`，这是我们二进制文件的名称。这与c语言中的参数列表的行为一致，允许程序在运行过程中使用其被调用的名称。通常，能够访问程序的名称是非常方便的，因为这样可以将其打印在消息中，或者根据用于调用程序的命令行别名来改变程序的行为。但就目前的目的而言……在章节中，我们忽略它，只保存我们需要的两个参数。

### 将参数值保存在变量中

该程序目前能够访问作为命令行参数指定的值。现在我们需要将这两个参数的值保存到变量中，这样我们就可以在整个程序中使用这些值了。我们在清单12-2中实现了这一点。

<列表编号="12-2" 文件名称="src/main.rs" 标题="创建用于存储查询参数和文件路径参数的变量">

```rust,should_panic,noplayground
{{#rustdoc_include ../listings/ch12-an-io-project/listing-12-02/src/main.rs}}
```

</清单>

正如我们在打印向量时所看到的，程序的名称占据了向量中`args[0]`位置的值，因此我们从索引1开始传递参数。第一个参数`minigrep`是我们正在搜索的字符串，因此我们将对这个字符串的引用存储在变量`query`中。第二个参数则是文件路径，因此我们将对这个路径的引用存储在变量`file_path`中。

我们暂时打印出这些变量的值，以证明代码按我们的意图正常运行。让我们再次运行这个程序，这次使用参数`test`和`sample.txt`。

```console
{{#include ../listings/ch12-an-io-project/listing-12-02/output.txt}}
```

太好了，程序运行正常！我们需要的参数值已经被正确保存到相应的变量中。之后我们会添加一些错误处理机制，以应对某些可能出现的问题，比如用户没有提供任何参数的情况。目前，我们暂时忽略这种情况，而是专注于增加文件读取功能。

[第13章]: ch13-00-functional-features.html  
[第7章——惯用用法]: ch07-04-bringing-paths-into-scope-with-the-use-keyword.html#creating-idiomatic-use-paths