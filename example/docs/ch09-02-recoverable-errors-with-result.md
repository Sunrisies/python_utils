## 可恢复的与 `Result` 相关的错误

大多数错误并不严重到需要让程序完全停止运行。有时候，当一个函数出现错误时，其背后的原因通常是可以轻易理解的，并且可以做出相应的处理。例如，如果你尝试打开一个文件，但操作失败了，因为文件不存在，那么你可以选择创建这个文件，而不是终止程序。

请回想一下在第二章中关于[“使用 `Result` 处理潜在故障”][handle_failure]<!--
ignore -->的内容。其中， `Result` 枚举被定义为有两种变体： `Ok` 和 `Err`，具体如下所示：

```rust
enum Result<T, E> {
    Ok(T),
    Err(E),
}
```

`T`和`E`是通用类型参数：我们将在第十章中更详细地讨论泛型。目前你需要知道的是，`T`代表了在`Ok`变体中成功情况下返回的值的类型，而`E`则代表了在`Err`变体失败情况下返回的错误值的类型。由于`Result`具有这些通用类型参数，因此我们可以在许多不同的情况下使用`Result`类型及其上定义的函数，这些情况下我们想要返回的成功值和错误值可能会有所不同。

我们称一个返回 `Result` 值的函数为“可能失败的函数”。在 Listing 9-3 中，我们尝试打开一个文件。

<Listing number="9-3" file-name="src/main.rs" caption="Opening a file">

```rust
use std::fs::File;

fn main() {
    let greeting_file_result = File::open("hello.txt");
}

```

</Listing>

`File::open` 的返回类型是一个 `Result<T, E>`。泛型参数 `T` 通过 `File::open` 的实现来填充，该实现使用了成功值的类型 `std::fs::File`，而 `std::fs::File` 是一个文件句柄。错误值中使用的 `E` 的类型是 `std::io::Error`。这种返回类型意味着对 `File::open` 的调用可能会成功，并返回一个我们可以读取或写入的文件句柄。不过，函数调用也可能失败：例如，文件可能不存在，或者我们没有权限访问该文件。`File::open` 函数需要有一种方式来告诉我们它是成功还是失败，并且同时提供文件句柄或错误信息。这些信息正是 `Result` 枚举所传达的内容。

在 `File::open` 成功的情况下，变量 `greeting_file_result` 中的值将是一个包含文件句柄的 `Ok` 的实例。在 `File::open` 失败的情况下，变量 `greeting_file_result` 中的值将是一个包含有关发生错误类型更详细信息的 `Err` 的实例。

我们需要在 Listing 9-3 中的代码中添加一些逻辑，以便根据 `File::open` 返回的值来执行不同的操作。Listing 9-4 展示了一种使用基本工具来处理 `Result` 的方法，这个工具就是我们在第 6 章中讨论过的 `match` 表达式。

<Listing number="9-4" file-name="src/main.rs" caption="Using a `match` expression to handle the `Result` variants that might be returned">

```rust,should_panic
use std::fs::File;

fn main() {
    let greeting_file_result = File::open("hello.txt");

    let greeting_file = match greeting_file_result {
        Ok(file) => file,
        Err(error) => panic!("Problem opening the file: {error:?}"),
    };
}

```

</Listing>

请注意，与 `Option` 枚举类似， `Result` 枚举及其变体也已经被引入到范围内，因此我们在 `match` 分支中不需要在 `Ok` 和 `Err` 变体之前指定 `Result::`。

当结果为 `Ok` 时，这段代码会从 `Ok` 变体中返回内部的 `file` 值，然后将该文件句柄值赋给变量 `greeting_file`。在 `match` 之后，我们就可以使用这个文件句柄来进行读取或写入操作了。

`match`的另一个分支处理从`File::open`获取`Err`值的情况。在这个例子中，我们选择调用`panic!`宏。如果当前目录中没有名为_hello.txt_的文件，而我们运行这段代码，那么我们会看到`panic!`宏的输出如下：

```console
$ cargo run
   Compiling error-handling v0.1.0 (file:///projects/error-handling)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.73s
     Running `target/debug/error-handling`

thread 'main' panicked at src/main.rs:8:23:
Problem opening the file: Os { code: 2, kind: NotFound, message: "No such file or directory" }
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace

```

像往常一样，这个输出准确地告诉我们出了什么问题。

### 针对不同类型的错误进行匹配

在清单9-4中的代码，无论`File::open`为何失败，都会继续执行`panic!`。然而，我们希望针对不同的失败原因采取不同的处理措施。如果`File::open`因为文件不存在而失败，我们希望创建该文件，并返回对新文件的句柄。如果`File::open`因为其他原因失败——例如，因为我们没有权限打开该文件——我们仍然希望代码以与清单9-4中相同的方式继续执行`panic!`。为此，我们在清单9-5中添加了一个内部`match`表达式。

<Listing number="9-5" file-name="src/main.rs" caption="Handling different kinds of errors in different ways">

<!-- ignore this test because otherwise it creates hello.txt which causes other
tests to fail lol -->

```rust,ignore
use std::fs::File;
use std::io::ErrorKind;

fn main() {
    let greeting_file_result = File::open("hello.txt");

    let greeting_file = match greeting_file_result {
        Ok(file) => file,
        Err(error) => match error.kind() {
            ErrorKind::NotFound => match File::create("hello.txt") {
                Ok(fc) => fc,
                Err(e) => panic!("Problem creating the file: {e:?}"),
            },
            _ => {
                panic!("Problem opening the file: {error:?}");
            }
        },
    };
}

```

</Listing>

`File::open` 返回的值的类型是 `Err` 变体中的 `io::Error`，这是一个由标准库提供的结构体。该结构体包含一个方法 `kind`，我们可以通过调用这个方法来获取 `io::ErrorKind` 类型的值。枚举 `io::ErrorKind` 也是由标准库提供的，它包含了多种变体，用于表示 `io` 操作可能产生的不同类型的错误。我们想要使用的变体是 `ErrorKind::NotFound`，它表示我们试图打开的文件尚不存在。因此，我们会使用 `greeting_file_result` 来进行匹配，同时还会使用 `error.kind()` 来进行内部匹配。

我们想要在内部匹配中检查的条件，是 `error.kind()` 返回的值是否是 `NotFound` 枚举中的 `ErrorKind` 变体。如果是的话，我们会尝试使用 `File::create` 来创建文件。然而，由于 `File::create` 也可能失败，因此我们需要在内部 `match` 表达式中添加第二个分支。当文件无法创建时，会打印出不同的错误信息。外部 `match` 的第二个分支保持不变，因此程序在除文件缺失错误之外的任何错误情况下都会崩溃。

> #### 使用 `Result<T, E>` 的替代方法
>
> 竟然有这么多 `match`！ `match` 表达式非常有用，但也很基础。在第13章中，你将学习闭包的概念，这些闭包可以与定义在 `Result<T, E>` 上的许多方法一起使用。在处理 `Result<T, E>` 值的代码中，使用闭包比使用 `match` 更简洁。
>
> 例如，以下是与清单9-5中相同的逻辑，这次使用了闭包和 `unwrap_or_else` 方法：
>
> <!-- CAN'T EXTRACT SEE https://github.com/rust-lang/mdBook/issues/1127 -->
>
> ```rust,ignore
> use std::fs::File;
> use std::io::ErrorKind;
>
> fn main() {
>     let greeting_file = File::open("hello.txt").unwrap_or_else(|error| {
>         if error.kind() == ErrorKind::NotFound {
>             File::create("hello.txt").unwrap_or_else(|error| {
>                 panic!("Problem creating the file: {error:?}");
>             })
>         } else {
>             panic!("Problem opening the file: {error:?}");
>         }
>     });
> }
> ```
>
> 虽然这段代码的行为与清单9-5相同，但它不包含任何 `match` 表达式，且阅读起来更清晰。在阅读完第13章后，请再回顾这个例子，并查阅标准库文档中关于 `unwrap_or_else` 方法的说明。在处理错误时，许多这类方法可以帮助你简化复杂的、嵌套的 `match` 表达式。

<!-- Old headings. Do not remove or links may break. -->

<a id="shortcuts-for-panic-on-error-unwrap-and-expect"></a>

#### 错误处理时的快速退出选项

使用 `match` 的效果还算不错，但它可能会显得有些冗长，而且并不总是能够很好地传达意图。 `Result<T, E>` 类型上有许多辅助方法，用于执行各种更具体的任务。 `unwrap` 方法是一个快捷方法，其实现方式与我们在清单 9-4 中编写的 `match` 表达式相同。如果 `Result` 的值是 `Ok` 的变体，那么 `unwrap` 将返回 `Ok` 内部的值。如果 `Result` 是 `Err` 的变体，那么 `unwrap` 会调用 `panic!` 宏。以下是 `unwrap` 的一个使用示例：

<Listing file-name="src/main.rs">

```rust,should_panic
use std::fs::File;

fn main() {
    let greeting_file = File::open("hello.txt").unwrap();
}

```

</Listing>

如果我们在不提供 _hello.txt_ 文件的情况下运行这段代码，将会看到 `panic!` 方法调用时出现的错误信息：

<!-- manual-regeneration
cd listings/ch09-error-handling/no-listing-04-unwrap
cargo run
copy and paste relevant text
-->

```text
thread 'main' panicked at src/main.rs:4:49:
called `Result::unwrap()` on an `Err` value: Os { code: 2, kind: NotFound, message: "No such file or directory" }
```

同样，`expect`方法还让我们能够选择`panic!`错误信息。使用`expect`而不是`unwrap`，并提供清晰的错误信息，可以传达你的意图，并使得追踪panic的来源变得更加容易。`expect`的语法如下所示：

<Listing file-name="src/main.rs">

```rust,should_panic
use std::fs::File;

fn main() {
    let greeting_file = File::open("hello.txt")
        .expect("hello.txt should be included in this project");
}

```

</Listing>

我们使用 `expect` 的方式与 `unwrap` 相同：用于返回文件句柄或调用 `panic!` 宏。 `expect` 在调用 `panic!` 时使用的错误消息，将是我们传递给 `expect` 的参数，而不是 `unwrap` 使用的默认 `panic!` 消息。具体格式如下：

<!-- manual-regeneration
cd listings/ch09-error-handling/no-listing-05-expect
cargo run
copy and paste relevant text
-->

```text
thread 'main' panicked at src/main.rs:5:10:
hello.txt should be included in this project: Os { code: 2, kind: NotFound, message: "No such file or directory" }
```

在高质量的生产代码中，大多数 Rust 开发者更倾向于使用 `expect` 而不是`unwrap`，并且会提供更多关于为什么这种操作总是会成功的上下文信息。这样，如果您的假设被证明是错误的，您就有更多的信息可用于调试。

### 错误传播

当函数的实现调用某个可能失败的操作时，与其在函数内部处理错误，不如将错误返回给调用代码，这样调用代码就可以自行决定如何处理该错误。这被称为“传播错误”，它赋予了调用代码更多的控制权，因为调用代码可能拥有更多关于如何处理错误的信息或逻辑，而这些信息或逻辑在函数的上下文中是无法获取的。

例如，清单 9-6 展示了一个从文件中读取用户名的函数。如果文件不存在或无法读取，该函数会将这些错误返回给调用该函数的代码。

<Listing number="9-6" file-name="src/main.rs" caption="A function that returns errors to the calling code using `match`">

<!-- Deliberately not using rustdoc_include here; the `main` function in the
file panics. We do want to include it for reader experimentation purposes, but
don't want to include it for rustdoc testing purposes. -->

```rust
use std::fs::File;
use std::io::{self, Read};

fn read_username_from_file() -> Result<String, io::Error> {
    let username_file_result = File::open("hello.txt");

    let mut username_file = match username_file_result {
        Ok(file) => file,
        Err(e) => return Err(e),
    };

    let mut username = String::new();

    match username_file.read_to_string(&mut username) {
        Ok(_) => Ok(username),
        Err(e) => Err(e),
    }
}

```

</Listing>

这个函数可以用更简洁的方式编写，但我们首先会手动完成大部分代码，以便探索错误处理的方式；最后，我们会展示更简洁的实现方法。首先，让我们看看这个函数的返回类型：`Result<String, io::Error>`。这意味着该函数返回的是一个类型为`Result<T, E>`的值，其中泛型参数`T`已经被具体类型`String`替代，而泛型类型`E`则被具体类型`io::Error`替代。

如果这个函数能够顺利执行，那么调用这个函数的代码将收到一个 `Ok` 类型的值，该值包含 `String` 信息——也就是这个函数从文件中读取到的 `username` 信息。如果这个函数遇到任何问题，调用代码的接收值将是一个 `Err` 类型的值，该值包含 `io::Error` 的实例，而 `io::Error` 会提供更多关于问题的详细信息。我们选择 `io::Error` 作为这个函数的返回类型，因为恰好这个类型就是我们在函数体内调用的两个可能失败的操作所返回的误差值的类型：即 `File::open` 函数和 `read_to_string` 方法。

该函数的主体首先调用 `File::open` 函数。然后，我们处理 `Result` 的值，采用与 Listing 9-4 中的 `match` 类似的处理方式。如果 `File::open` 成功执行，那么模式变量 `file` 中的文件句柄就会成为可变变量 `username_file` 的值，函数将继续执行。在 `Err` 的情况下，我们不会调用 `panic!`，而是使用 `return` 关键字来提前结束函数的执行，并将 `File::open` 中的错误值（现在存储在模式变量 `e` 中）作为该函数的错误值返回给调用代码。

因此，如果我们有一个在 `username_file` 中的文件句柄，那么该函数会创建一个新的变量 `username`，并在 `username_file` 中的文件句柄上调用 `read_to_string` 方法来读取文件的内容到 `username` 中。`read_to_string` 方法也会返回一个 `Result`，因为即使 `File::open` 成功执行，它也可能失败。所以，我们需要另一个 `match` 来处理这种情况：如果 `read_to_string` 成功执行，那么我们的函数就成功了，我们会从现在位于 `username` 中的文件中获取用户名，并将其封装在 `Ok` 中。如果 `read_to_string` 失败，我们会以与处理 `match` 时返回错误值相同的方式返回错误值。不过，我们不需要明确写出 `return`，因为这是函数的最后一个表达式。

调用此代码的代码将会处理两种情况：一种是包含用户名的 `Ok` 值，另一种是包含 `io::Error` 值的 `Err` 值。具体如何处理这些值由调用该代码的代码来决定。如果调用代码得到了 `Err` 值，它可能会调用 `panic!` 从而导致程序崩溃，或者使用默认的用户名，或者从文件以外的其他来源获取用户名。由于我们对调用代码的实际意图了解不足，因此将所有成功或错误信息向上传递，以便其能够妥善处理。

在Rust中，这种错误传播的模式非常常见，因此Rust提供了问号运算符 `?` 来简化这一情况。

<!-- Old headings. Do not remove or links may break. -->

<a id="a-shortcut-for-propagating-errors-the--operator"></a>

#### `?` 运算符的快捷方式

清单9-7展示了一个 `read_username_from_file` 的实现，其功能与清单9-6相同，但此实现使用了 `?` 运算符。

<Listing number="9-7" file-name="src/main.rs" caption="A function that returns errors to the calling code using the `?` operator">

<!-- Deliberately not using rustdoc_include here; the `main` function in the
file panics. We do want to include it for reader experimentation purposes, but
don't want to include it for rustdoc testing purposes. -->

```rust
use std::fs::File;
use std::io::{self, Read};

fn read_username_from_file() -> Result<String, io::Error> {
    let mut username_file = File::open("hello.txt")?;
    let mut username = String::new();
    username_file.read_to_string(&mut username)?;
    Ok(username)
}

```

</Listing>

在 `Result` 值之后放置 `?`，其工作方式几乎与我们为处理 `Result` 值而定义的 `match` 表达式相同。  
清单 9-6：如果 `Result` 的值为 `Ok`，则 `Ok` 内的值会被返回，程序将继续运行。如果值为 `Err`，则整个函数会返回 `Err`，就像我们使用了 `return` 关键字一样，这样错误值就会传播到调用代码的代码中。

Listing 9-6 中的 `match` 表达式所做的事情，与 `?` 运算符所做的事情之间存在差异：那些被 `?` 运算符调用的错误值，会经过标准库中的 `From` 特质中定义的 `from` 函数进行处理。这个函数的作用是将一种类型的值转换为另一种类型的值。当 `?` 运算符调用 `from` 函数时，接收到的错误类型会被转换为当前函数返回类型中定义的错误类型。这一点在函数返回一种错误类型来表示函数可能出现的所有错误情况时非常有用，即使某些部分可能因为多种不同的原因而失败。

例如，我们可以将清单9-7中的`read_username_from_file`函数修改为返回我们自定义的error类型`OurError`。如果我们还定义`impl From<io::Error> for OurError`来从`io::Error`构造`OurError`的实例，那么`?`运算符在`read_username_from_file`的主体中将会调用`from`，从而将错误类型进行转换，而无需在函数中添加更多的代码。

在 Listing 9-7 的上下文中， `File::open` 调用末尾的 `Ok` 会将 `Ok` 内部的值返回给 `username_file` 变量。如果发生错误， `?` 运算符会在整个函数执行过程中提前终止，并将任何 `Err` 值返回给调用代码。同样的规则也适用于 `read_to_string` 调用末尾的 `?`。

`?`运算符消除了大量的样板代码，使得这个函数的实现更加简洁。我们甚至可以通过在`?`之后立即链接方法调用来进一步缩短代码，如清单9-8所示。

<Listing number="9-8" file-name="src/main.rs" caption="Chaining method calls after the `?` operator">

<!-- Deliberately not using rustdoc_include here; the `main` function in the
file panics. We do want to include it for reader experimentation purposes, but
don't want to include it for rustdoc testing purposes. -->

```rust
use std::fs::File;
use std::io::{self, Read};

fn read_username_from_file() -> Result<String, io::Error> {
    let mut username = String::new();

    File::open("hello.txt")?.read_to_string(&mut username)?;

    Ok(username)
}

```

</Listing>

我们将新变量 `String` 的创建操作移到了函数的最开始部分；这部分并没有发生变化。我们没有创建变量 `username_file`，而是将 `read_to_string` 的调用直接链接到 `File::open("hello.txt")?` 的结果上。在 `read_to_string` 的调用末尾仍然有一个 `?`，并且当两个 `File::open` 和 `read_to_string` 都成功时，我们仍然会返回一个包含 `username` 的 `Ok` 值，而不是返回错误。其功能与 Listing 9-6 和 Listing 9-7 中的功能相同；这只是另一种更易于使用的编写方式而已。

列表9-9展示了一种使用 `fs::read_to_string` 来使代码更简洁的方法。

<Listing number="9-9" file-name="src/main.rs" caption="Using `fs::read_to_string` instead of opening and then reading the file">

<!-- Deliberately not using rustdoc_include here; the `main` function in the
file panics. We do want to include it for reader experimentation purposes, but
don't want to include it for rustdoc testing purposes. -->

```rust
use std::fs;
use std::io;

fn read_username_from_file() -> Result<String, io::Error> {
    fs::read_to_string("hello.txt")
}

```

</Listing>

将文件读取到字符串中是一个相当常见的操作，因此标准库提供了方便的 `fs::read_to_string` 函数，该函数可以打开文件、创建一个新的 `String`、读取文件的内容、将内容放入该 `String` 中，并返回结果。当然，使用 `fs::read_to_string` 并不能让我们详细解释所有的错误处理，所以我们先采用较长的方式来实现这个功能。

<!-- Old headings. Do not remove or links may break. -->

<a id="where-the--operator-can-be-used"></a>

#### `?` 运算符的使用场景

`?`运算符只能用于返回类型与`?`所作用的数值兼容的函数中。这是因为`?`运算符被定义为在函数外部提前返回数值，其方式与我们在第9-6节中定义的`match`表达式相同。在第9-6节中，`match`使用了`Result`数值，而提前返回的部分则返回了`Err(e)`数值。因此，函数的返回类型必须是`Result`类型，这样才能与`return`兼容。

在 Listing 9-10 中，我们将看到如果我们在一个返回类型与我们使用 `?` 操作数的类型不兼容的 `main` 函数中使用 `?` 运算符时，会遇到的错误。

<Listing number="9-10" file-name="src/main.rs" caption="Attempting to use the `?` in the `main` function that returns `()` won’t compile.">

```rust,ignore,does_not_compile
use std::fs::File;

fn main() {
    let greeting_file = File::open("hello.txt")?;
}

```

</Listing>

这段代码试图打开一个文件，但可能会失败。`?`运算符遵循由`File::open`返回的值，但是`main`函数的返回类型是`()`，而不是`Result`。当我们编译这段代码时，会收到以下错误信息：

```console
$ cargo run
   Compiling error-handling v0.1.0 (file:///projects/error-handling)
error[E0277]: the `?` operator can only be used in a function that returns `Result` or `Option` (or another type that implements `FromResidual`)
 --> src/main.rs:4:48
  |
3 | fn main() {
  | --------- this function should return `Result` or `Option` to accept `?`
4 |     let greeting_file = File::open("hello.txt")?;
  |                                                ^ cannot use the `?` operator in a function that returns `()`
  |
help: consider adding return type
  |
3 ~ fn main() -> Result<(), Box<dyn std::error::Error>> {
4 |     let greeting_file = File::open("hello.txt")?;
5 +     Ok(())
  |

For more information about this error, try `rustc --explain E0277`.
error: could not compile `error-handling` (bin "error-handling") due to 1 previous error

```

这个错误表明，我们只能在一个返回 `Result`、 `Option` 或实现了 `FromResidual` 的其他类型的函数中使用 `?` 运算符。

要修复这个错误，你有两个选择。第一个选择是更改函数的返回类型，使其与你在 `?` 运算符上使用的数值兼容，只要没有限制阻止这一点。第二个选择是使用 `match` 或 `Result<T, E>` 中的某一种方法来以适当的方式处理 `Result<T, E>`。

错误信息还提到，`?`也可以与`Option<T>`的值一起使用。就像在`Result`上使用`?`一样，你只能在返回`Option`的函数中使用`?`和`Option`。当`?`运算符在`Option<T>`上被调用时，其行为类似于在`Result<T, E>`上被调用时的行为：如果值是`None`，那么`None`会在函数执行到那个点时提前返回。如果值是`Some`，那么`Some`内的数值就是表达式的结果，函数会继续执行。列表9-11中有一个示例，展示了如何找到给定文本中第一行的最后一个字符。

<Listing number="9-11" caption="Using the `?` operator on an `Option<T>` value">

```rust
fn last_char_of_first_line(text: &str) -> Option<char> {
    text.lines().next()?.chars().last()
}

```

</Listing>

This function returns `选项<char>` because it’s possible that there is a
character there, but it’s also possible that there isn’t. This code takes the
`文本` string slice argument and calls the `行` method on it, which returns
an iterator over the lines in the string. Because this function wants to
examine the first line, it calls `下一个` on the iterator to get the first value
from the iterator. If `文本` is the empty string, this call to `下一个` will
return `无`, in which case we use `？` to stop and return `无` from
`第一行最后一个字符`. If `文本` is not the empty string, `下一个` will
return a `一些` value containing a string slice of the first line in `文本`.

The `？` extracts the string slice, and we can call `字符` on that string slice
to get an iterator of its characters. We’re interested in the last character in
this first line, so we call `最后一个` to return the last item in the iterator.
This is an `选项` because it’s possible that the first line is the empty
string; for example, if `文本` starts with a blank line but has characters on
other lines, as in `“\nhi”`. However, if there is a last character on the first
line, it will be returned in the `一些` variant. The `？` operator in the middle
gives us a concise way to express this logic, allowing us to implement the
function in one line. If we couldn’t use the `？` operator on `选项`, we’d
have to implement this logic using more method calls or a `匹配` expression.

Note that you can use the `？` operator on a `结果` in a function that returns
`结果`, and you can use the `？` operator on an `选项` in a function that
returns `选项`, but you can’t mix and match. The `？` operator won’t
automatically convert a `结果` to an `选项` or vice versa; in those cases,
you can use methods like the `成功` method on `结果` or the `成功或` method on
`选项` to do the conversion explicitly.

So far, all the `主程序` functions we’ve used return `()`. The `主程序⊂PH43⊂PH44<(), E>⊂PH46⊂PH47<(), Box<dyn Error>>` and added a return value `可以(())` to the end. This
code will now compile.

<Listing number="9-12" file-name="src/main.rs" caption="Changing `main` to return `Result<(), E>`允许在`Result`值上使用`?`运算符。>

```rust,ignore
use std::error::Error;
use std::fs::File;

fn main() -> Result<(), Box<dyn Error>> {
    let greeting_file = File::open("hello.txt")?;

    Ok(())
}

```

</Listing>

`Box<dyn Error>`类型是一个特质对象，我们将在第18章的“使用特质对象来抽象共享行为”部分中详细讨论<!-- ignore -->。目前，你可以将`Box<dyn Error>`理解为“任何类型的错误”。在`main`函数中对`Result`值使用`?`并指定错误类型为`Box<dyn Error>`是允许的，因为这允许任何`Err`值的提前返回。尽管这个`main`函数的主体只会返回类型为`std::io::Error`的错误，但通过指定`Box<dyn Error>`，即使有更多返回其他错误的代码被添加到`main`函数的主体中，这个签名仍然是正确的。

当 `main` 函数返回 `Result<(), E>` 时，如果 `main` 返回 `Ok(())`，则执行程序将以 `0` 的值退出；如果 `main` 返回 `Err` 的值，则执行程序将以非零值退出。用 C 语言编写的执行程序在退出时返回整数：成功退出的程序返回整数 `0`，而发生错误的程序则返回除 `0` 之外的其他整数。Rust 也允许执行程序返回整数，以与这一惯例保持一致。

`main` 函数可以返回任何实现了 [`std::process::Termination` 特质][termination]<!-- ignore --> 的类型，该特质包含一个返回 `ExitCode` 的 `report` 函数。有关如何为您的类型实现 `Termination` 特质的更多信息，请参阅标准库文档。

既然我们已经讨论了调用 `panic!` 或返回 `Result` 的细节，现在让我们回到如何决定在哪些情况下使用哪种方法的主题。

[handle_failure]: ch02-00-guessing-game-tutorial.html#handling-potential-failure-with-result
[trait-objects]: ch18-02-trait-objects.html#using-trait-objects-to-abstract-over-shared-behavior
[termination]: ../std/process/trait.Termination.html
