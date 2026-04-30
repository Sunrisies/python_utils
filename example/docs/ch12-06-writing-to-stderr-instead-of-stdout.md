<!-- Old headings. Do not remove or links may break. -->

<a id="writing-error-messages-to-standard-error-instead-of-standard-output"></a>

## 将错误重定向到标准错误输出

目前，我们所有的输出都是使用`println!`宏写入终端的。在大多数终端中，输出分为两种类型：_标准输出_（`stdout`），用于显示一般信息；_标准错误_（`stderr`），用于显示错误信息。这种区分使得用户可以选择将程序的成功输出保存到文件中，同时仍然可以将错误信息打印到屏幕上。

`println!`宏只能输出到标准输出，因此我们必须使用其他方式来将信息输出到标准错误流中。

### 检查错误所在的位置

首先，让我们观察 `minigrep` 输出的内容是如何被写入标准输出流的，同时记录下我们想写入标准错误流的任何错误信息。我们可以通过将标准输出流重定向到文件来实现这一点，同时故意引发一个错误。不过，我们不会将标准错误流重定向，因此任何发送到标准错误流的内容仍然会显示在屏幕上。

命令行程序应该将错误信息发送到标准错误流，这样即使我们将标准输出流重定向到文件，我们仍然可以在屏幕上看到错误信息。不过，我们的程序目前表现不佳：我们即将发现它实际上是将错误信息输出保存到文件中了！

为了演示这种行为，我们将运行程序，并使用 `>` 以及我们想要将标准输出流重定向到的文件路径 output.txt_。我们不会传递任何参数，这应该会导致一个错误：

```console
$ cargo run > output.txt
```

`>`语法告诉shell将标准输出内容写入到output.txt_文件中，而不是屏幕。我们没有看到预期的错误信息被显示到屏幕上，这意味着错误信息一定被存储在了文件中。下面就是output.txt_文件的内容：

```text
Problem parsing arguments: not enough arguments
```

是的，我们的错误信息被打印到标准输出上。对于这类错误信息来说，将其打印到标准错误输出会更实用，这样只有成功运行的数据才会被保存到文件中。我们会进行修改。

### 将打印错误输出到标准错误日志中

我们将使用清单12-24中的代码来修改错误信息的显示方式。由于本章前面进行的重构，所有用于显示错误信息的代码都集中在一个函数中，即 `main` 函数。标准库提供了 `eprintln!` 宏，用于将错误信息输出到标准错误流中。因此，我们将调用 `println!` 的两个地方改为使用 `eprintln!` 来显示错误信息。

<Listing number="12-24" file-name="src/main.rs" caption="Writing error messages to standard error instead of standard output using `eprintln!`">

```rust,ignore
fn main() {
    let args: Vec<String> = env::args().collect();

    let config = Config::build(&args).unwrap_or_else(|err| {
        eprintln!("Problem parsing arguments: {err}");
        process::exit(1);
    });

    if let Err(e) = run(config) {
        eprintln!("Application error: {e}");
        process::exit(1);
    }
}

```

</Listing>

现在，让我们以同样的方式再次运行该程序，不要提供任何参数，并通过 `>` 将标准输出重定向：

```console
$ cargo run > output.txt
Problem parsing arguments: not enough arguments
```

现在我们在屏幕上看到了错误，而`_output.txt_`文件中什么都没有，这正是我们对命令行程序所期望的行为。

让我们再次运行这个程序，这次使用不会导致错误的参数，同时仍然将标准输出重定向到文件中，如下所示：

```console
$ cargo run -- to poem.txt > output.txt
```

我们将不会在终端看到任何输出，而`_output.txt_`文件将包含我们的结果：

<span class="filename">文件名: output.txt</span>

```text
Are you nobody, too?
How dreary to be somebody!
```

这表明，我们现在使用标准输出来处理成功的结果，而适当使用标准错误来处理错误信息。

## 摘要

本章回顾了您迄今为止学习的一些重要概念，并介绍了如何在Rust中执行常见的I/O操作。通过使用命令行参数、文件、环境变量以及`eprintln!`宏来打印错误信息，您现在已经准备好编写命令行应用程序了。结合前几章中的概念，您的代码将能够很好地组织，数据将有效地存储在适当的数据结构中，错误处理也会更加完善，同时代码也会经过充分的测试。

接下来，我们将探讨一些受到函数式语言影响的Rust特性：闭包和迭代器。