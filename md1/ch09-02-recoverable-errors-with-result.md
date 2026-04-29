## 可恢复的与`Result`相关的错误

大多数错误并不严重到需要让程序完全停止运行。有时候，当一个函数失败时，其背后的原因是可以轻易理解的，并且可以做出相应的响应。例如，如果你尝试打开一个文件，但操作失败了，因为该文件不存在，那么你可以选择创建这个文件，而不是终止程序。

请回想一下在第二章中的[“使用`Result`处理潜在故障”][handle_failure]<!--
ignore -->，其中`Result`枚举被定义为有两种变体，分别是`Ok`和`Err`，具体定义如下：

```rust
enum Result<T, E> {
    Ok(T),
    Err(E),
}
```

`T`和`E`是泛型类型参数：我们将在第十章中详细讨论泛型。目前你需要知道的是，`T`代表了在`Ok`变体中成功情况下返回的值的类型，而`E`则代表了在`Err`变体中失败情况下返回的错误类型。由于`Result`具有这些泛型类型参数，因此我们可以在许多不同的情况下使用`Result`类型以及其上的函数，这些情况下我们想要返回的成功值和错误值可能会有所不同。

让我们称一个返回 `Result` 值的函数为“可能失败的函数”。在清单9-3中，我们尝试打开一个文件。

<列表编号="9-3" 文件名称="src/main.rs" 标题="打开文件">

```rust
{{#rustdoc_include ../listings/ch09-error-handling/listing-09-03/src/main.rs}}
```

</ Listing>

`File::open`的返回类型是`Result<T, E>`。泛型参数`T`是通过实现`File::open`来填充的，该实现使用了成功值的类型`std::fs::File`，而`std::fs::File`实际上是一个文件句柄。在错误值中使用的`E`的类型是`std::io::Error`。这种返回类型意味着对`File::open`的调用可能会成功，并返回一个我们可以读取或写入的文件句柄。不过，函数调用也可能失败：例如，文件可能不存在，或者我们没有权限访问该文件。`File::open`函数需要有一种方式来告诉我们它是成功了还是失败了，并且同时提供文件句柄或错误信息。这些信息正是`Result`枚举所传达的内容。

在`File::open`成功的情况下，变量`greeting_file_result`中的值将是一个包含文件句柄的`Ok`实例。而在`File::open`失败的情况下，变量`greeting_file_result`中的值将是一个包含有关发生错误类型信息的`Err`实例。

我们需要在 Listing 9-3 中的代码中添加一些逻辑，以便根据 `File::open` 返回的值来采取相应的操作。Listing 9-4 展示了一种使用基本工具来处理 `Result` 的方法，以及我们在第 6 章中讨论过的 `match` 表达式。

<列表编号="9-4" 文件名称="src/main.rs" 标题="使用 `match` 表达式来处理可能返回的 `Result` 变体">

```rust,should_panic
{{#rustdoc_include ../listings/ch09-error-handling/listing-09-04/src/main.rs}}
```

</ Listing>

请注意，与 ``Option`` 枚举一样，``Result`` 枚举及其变体也是由前奏引入作用域的，因此我们在 ``match`` 分支中不需要在 ``Ok`` 和 ``Err`` 变体之前指定 ``Result::``。

当结果为`Ok`时，这段代码会从`Ok`变体中获取内部的`file`值，然后将该文件句柄值赋给变量`greeting_file`。在`match`之后，我们可以使用这个文件句柄来进行读取或写入操作。

`match`的另一个分支负责处理从`File::open`获取`Err`值的情况。在这个例子中，我们选择调用`panic!`宏。如果我们当前目录中没有名为_hello.txt_的文件，并且运行这段代码，那么我们将看到`panic!`宏的输出如下：

```console
{{#include ../listings/ch09-error-handling/listing-09-04/output.txt}}
```

像往常一样，这个输出准确地告诉我们出了什么问题。

### 针对不同类型的错误进行匹配

在清单9-4中的代码，无论为什么导致`File::open`失败，都会执行`panic!`。  
然而，我们希望针对不同的失败原因采取不同的措施。如果`File::open`因为文件不存在而失败，我们希望创建该文件，并返回对新文件的句柄。如果`File::open`因其他原因失败——例如，因为我们没有权限打开该文件——我们仍然希望代码以与清单9-4中相同的方式执行`panic!`。为此，我们在内部添加了`match`表达式，如清单9-5所示。

<listing number="9-5" file-name="src/main.rs" caption="以不同方式处理不同类型的错误">

<!-- 忽略这个测试，因为否则会生成 hello.txt 文件，这会导致其他测试失败，哈哈 -->

```rust,ignore
{{#rustdoc_include ../listings/ch09-error-handling/listing-09-05/src/main.rs}}
```

</ Listing>

在 `Err` 变体中，`File::open` 返回的值的类型是 `io::Error`，这是一个由标准库提供的结构体。该结构体包含一个名为 `kind` 的方法，我们可以通过调用这个方法来获取 `io::ErrorKind` 类型的值。枚举类型 `io::ErrorKind` 也是由标准库提供的，它包含了多种变体，用于表示 `io` 操作可能产生的不同类型的错误。我们想要使用的变体是 `ErrorKind::NotFound`，它表示我们正在尝试打开的文件尚不存在。因此，我们会匹配 `greeting_file_result` 的值，但同时也会匹配 `error.kind()` 的值。

我们想要在内部匹配中检查的条件是指`error.kind()`返回的值是否为`ErrorKind`枚举中的`NotFound`变体。如果是这样，我们会尝试使用`File::create`来创建文件。然而，由于`File::create`也可能失败，因此我们需要在内部`match`表达式中加入第二个分支。当无法创建文件时，会打印出不同的错误信息。外部`match`的第二个分支保持不变，因此除了文件缺失错误之外，程序在其他错误情况下会崩溃。

> #### 使用 `match` 和 `Result<T, E>` 的替代方案  
>  
> 这真是大量的 `match`！`match` 表达式非常有用，但也很简单。在第13章中，你将学习到闭包的概念，它们被用于许多定义在 `Result<T, E>` 上的方法。在处理代码中的 `Result<T, E>` 值时，使用闭包比使用 `match` 更简洁。  
>  
> 例如，以下是与清单9-5相同逻辑的另一种写法，这次使用了闭包和 `unwrap_or_else` 方法：  
>  
> <!-- 无法提取示例链接：https://github.com/rust-lang/mdBook/issues/1127 -->  
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
> 虽然这段代码的行为与清单9-5相同，但它不包含任何 `match` 表达式，且阅读起来更清晰。在阅读完第13章之后，可以再回到这个例子，并查阅标准库中关于 `unwrap_or_else` 方法的文档。在处理错误时，许多这类方法可以帮助清理那些复杂的、嵌套的 `match` 表达式。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="快捷方式以处理错误时的解引用和预期"></a>

#### 在出错时触发Panic的快捷方式

使用 ``match`` 效果还算不错，但这种方式可能会显得有些冗长，而且并不能总是很好地传达意图。``Result<T, E>`` 类型包含了许多辅助方法，用于执行各种更具体的任务。``unwrap`` 是一个快捷方式，其实现方式与我们在清单 9-4 中编写的 ``match`` 表达式相同。如果 ``Result`` 的值是 ``Ok`` 的变体，那么 ``unwrap`` 将会返回 ``Ok`` 中的值。如果 ``Result`` 是 ``Err`` 的变体，那么 ``unwrap`` 将会调用 ``panic!`` 宏。以下是 ``unwrap`` 的一个使用示例：

<code listing file-name="src/main.rs">

```rust,should_panic
{{#rustdoc_include ../listings/ch09-error-handling/no-listing-04-unwrap/src/main.rs}}
```

</ Listing>

如果我们在不提供`_hello.txt_`文件的情况下运行这段代码，我们会看到来自``panic!``调用的错误信息，该错误是由``unwrap``方法引发的。

<!-- 手动重新生成
cd listings/ch09-error-handling/no-listing-04-unwrap
cargo run
复制并粘贴相关文本
-->

```text
thread 'main' panicked at src/main.rs:4:49:
called `Result::unwrap()` on an `Err` value: Os { code: 2, kind: NotFound, message: "No such file or directory" }
```

同样，`expect`方法还允许我们选择`panic!`错误信息。使用`expect`而不是`unwrap`，并提供清晰的错误信息，可以传达你的意图，并使追踪panic的来源变得更加容易。`expect`的语法如下所示：

<code listing file-name="src/main.rs">

```rust,should_panic
{{#rustdoc_include ../listings/ch09-error-handling/no-listing-05-expect/src/main.rs}}
```

</ Listing>

我们使用 ``expect`` 的方式与 ``unwrap`` 相同：用于返回文件句柄或调用 ``panic!`` 宏。在 ``expect`` 调用 ``panic!`` 时使用的错误信息，将是我们传递给 ``expect`` 的参数，而不是 ``unwrap`` 所使用的默认 ``panic!`` 信息。具体如下所示：

<!-- 手动重新生成
cd listings/ch09-error-handling/no-listing-05-expect
cargo run
复制并粘贴相关文本
-->

```text
thread 'main' panicked at src/main.rs:5:10:
hello.txt should be included in this project: Os { code: 2, kind: NotFound, message: "No such file or directory" }
```

在生产级代码中，大多数Rust开发者更倾向于使用`expect`而不是`unwrap`。同时，他们会提供更多关于为何该操作总是能成功的具体说明。这样一来，如果我们的假设最终被证明是错误的，我们就有更多的信息可用于调试。

### 传播错误

当函数的实现调用某个可能失败的操作时，与其在函数内部处理错误，不如将错误返回给调用代码，让调用代码来决定如何处理该错误。这被称为“传播错误”，它赋予了调用代码更多的控制权，因为调用代码可能拥有更多关于如何处理错误的信息或逻辑，而这些信息或逻辑在你自己的代码中是无法获取的。

例如，清单9-6展示了一个从文件中读取用户名的函数。如果文件不存在或无法读取，该函数会将错误返回给调用该函数的代码。

<listing number="9-6" file-name="src/main.rs" caption="一个使用 `match` 将错误返回给调用代码的函数">

<!-- 故意没有使用 rustdoc_include；文件中的 `main` 函数会导致程序崩溃。我们确实希望将其包含进来以供读者实验使用，但不想将其包含在 rustdoc 的测试过程中。-->

```rust
{{#include ../listings/ch09-error-handling/listing-09-06/src/main.rs:here}}
```

</ Listing>

这个函数可以用更简洁的方式编写，但我们首先会手动完成大部分代码，以便探索错误处理的过程；最后，我们会展示更简洁的实现方式。首先，让我们看看这个函数的返回类型：`Result<String, io::Error>`。这意味着该函数返回的类型是`Result<T, E>`，其中泛型参数`T`已经被具体类型`String`替代，而泛型类型`E`则被具体类型`io::Error`替代。

如果这个函数能够顺利执行且没有遇到任何问题，那么调用这个函数的代码将会收到一个`Ok`的值，该值中包含`String`——也就是这个函数从文件中读取到的`username`。如果这个函数遇到了任何问题，那么调用代码的将会收到一个`Err`的值，该值中包含`io::Error`的实例，而`io::Error`则包含了关于问题的更多详细信息。我们选择`io::Error`作为这个函数的返回类型，因为恰好这是我们函数中可能失败的两个操作的错误值的类型：`File::open`函数和`read_to_string`方法。

该函数的主体首先调用了`File::open`函数。然后，我们处理`Result`的值，并使用与清单9-4中的`match`类似的`match`方法进行处理。如果`File::open`成功执行，那么模式变量`file`中的文件句柄就会成为可变变量`username_file`的值，之后函数将继续执行。在`Err`的情况下，我们不会调用`panic!`，而是使用`return`关键字来提前结束函数执行，并将来自`File::open`的错误值——现在存储在模式变量`e`中——作为此函数的错误值返回给调用代码。

因此，如果我们有一个文件句柄在 ``username_file`` 中，那么该函数会在变量 ``username`` 中创建一个新的 ``String``，并在 ``username_file`` 中的文件句柄上调用 ``read_to_string`` 方法来读取文件内容到 ``username`` 中。``read_to_string`` 方法也会返回一个 ``Result``，因为即使 ``File::open`` 成功了，它也可能失败。所以，我们需要另一个 ``match`` 来处理这个 ``Result``：如果 ``read_to_string`` 成功了，那么我们的函数就成功了，我们会从文件中获取用户名，该文件现在位于 ``username`` 中，并以 ``Ok`` 的形式进行封装。如果 ``read_to_string`` 失败了，我们就会以与处理 ``File::open`` 返回值时的相同方式返回错误值。不过，我们不需要明确说明 ``return`$，因为这是函数的最后一个表达式。

调用此代码的代码将会处理获取一个包含用户名的值 ``Ok``，或者一个包含 ``io::Error`` 的值 ``Err`$。具体如何处理这些值由调用该代码的代码来决定。如果调用代码获取到 ``Err`` 的值，它可能会调用 ``panic!``，从而导致程序崩溃；或者使用默认的用户名；又或者从文件以外的其他来源查找用户名。由于我们缺乏关于调用代码实际意图的信息，因此我们将所有的成功或错误信息向上传递，以便其能够妥善处理。

在Rust中，这种错误传播的模式非常常见，因此Rust提供了``?``这个问号运算符，以便更方便地处理这种情况。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="a-shortcut-for-propagating-errors-the--operator"></a>

#### `?` 运算符的快捷方式

清单9-7展示了`read_username_from_file`的实现，该实现具有与清单9-6中相同的功能，但此实现使用了`?`运算符。

<listing number="9-7" file-name="src/main.rs" caption="一个使用 `?` 操作符将错误返回给调用代码的函数">

<!-- 故意没有使用 rustdoc_include；文件中的 `main` 函数会导致程序崩溃。我们确实希望将其包含进来以供读者实验使用，但不想将其包含在 rustdoc 的测试过程中。-->

```rust
{{#include ../listings/ch09-error-handling/listing-09-07/src/main.rs:here}}
```

</ Listing>

在 `Result` 定义的值之后放置的 `?`，其工作方式几乎与我们在 Listing 9-6 中定义的用于处理 `Result` 值的 `match` 表达式相同。如果 `Result` 的值是一个 `Ok`，那么 `Ok` 内的内容将被返回，程序将继续运行。如果值是 `Err`，那么整个函数的 `Err` 将被返回，就像我们使用了 `return` 关键字一样，这样错误值就会传播到调用代码。

在清单9-6中的__`INLINE_CODE_199__`表达式所做的事情与__`INLINE_CODE_200__`操作符所做的事情之间存在差异：那些调用了__`INLINE_CODE_201__`操作符的错误值会经过标准库中的__`INLINE_CODE_203__`特质中定义的__`INLINE_CODE_202__`函数进行处理。该函数在将一种类型的值转换为另一种类型时非常有用。

当__`INLINE_CODE_204__`操作符调用__`INLINE_CODE_205__`函数时，接收到的错误类型会被转换为当前函数返回类型中定义的错误类型。这一点在当一个函数返回一个错误类型来代表函数可能出现的所有失败情况时非常有用，即使某些部分可能因为多种不同的原因而失败。

例如，我们可以修改清单9-7中的`read_username_from_file`函数，使其返回我们自定义的error类型`OurError`。如果我们同时定义`impl From<io::Error> for OurError`，以便从`io::Error`构造出`OurError`的实例，那么位于`read_username_from_file`体内的`?`操作符调用将会调用`from`，从而将错误类型进行转换，而无需在函数中添加更多代码。

在 Listing 9-7 的上下文中，位于 `File::open` 末尾的 `?` 会将 `Ok` 内的数值返回给变量 `username_file`。如果发生错误，`?` 运算符会提前退出整个函数，并将任何 `Err` 的值返回给调用代码。同样的情况也适用于位于 `read_to_string` 末尾的 `?`。

`?`运算符消除了大量的样板代码，使得这个函数的实现更加简洁。我们甚至可以通过在`?`之后立即链接方法调用来进一步缩短这段代码，如清单9-8所示。

<listing number="9-8" file-name="src/main.rs" caption="在 `?` 运算符之后链式调用方法">

<!-- 故意没有使用 rustdoc_include；文件中的 `main` 函数会导致程序崩溃。我们确实希望将其包含进来以供读者实验使用，但不想将其包含在 rustdoc 的测试过程中。-->

```rust
{{#include ../listings/ch09-error-handling/listing-09-08/src/main.rs:here}}
```

</ Listing>

我们将在`username`中创建新的`String`的功能移到了函数的开头；这部分并没有发生变化。我们没有再创建一个变量`username_file`，而是直接将`read_to_string`的调用链接到`File::open("hello.txt")?`的结果上。在`read_to_string`调用的末尾，我们仍然有一个`?`；当`File::open`和`read_to_string`都成功时，我们仍然会返回一个包含`username`的`Ok`值，而不是返回错误。这个功能与Listing 9-6和Listing 9-7中的功能相同；这只是一种更易于使用的编写方式而已。

清单9-9展示了一种使用`fs::read_to_string`来使代码更简洁的方法。

<列表编号="9-9" 文件名称="src/main.rs" 标题="使用 `fs::read_to_string` 而不是直接打开后再读取文件">

<!-- 故意没有使用 rustdoc_include；文件中的 `main` 函数会导致程序崩溃。我们确实希望将其包含进来以供读者实验使用，但不想将其包含在 rustdoc 的测试过程中。-->

```rust
{{#include ../listings/ch09-error-handling/listing-09-09/src/main.rs:here}}
```

</ Listing>

将文件读取到字符串中是一个相当常见的操作，因此标准库提供了方便的`fs::read_to_string`函数。该函数可以打开文件，创建一个新的`String`对象，读取文件内容，并将内容放入`String`对象中，最后返回该对象的内容。当然，使用`fs::read_to_string`并不能让我们详细讲解所有的错误处理方式，所以我们先采用更传统的做法来处理这个问题。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="where-the--operator-can-be-used"></a>

#### `?`运算符的使用场景

`?`运算符只能用于返回类型与`?`所操作的值兼容的函数中。这是因为`?`运算符被定义为以一种类似于我们在Listing 9-6中定义的`match`表达式的方式，在函数外部提前返回值。在Listing 9-6中，`match`使用了`Result`的值，而提前返回的操作符则返回了`Err(e)`的值。因此，函数的返回类型必须是`Result`，以便与`return`兼容。

在清单9-10中，我们将看到如果我们在一个返回类型与``?``所操作的值的类型不兼容的``main``函数中使用``?``运算符时，会遇到的错误。

<Listing number="9-10" file-name="src/main.rs" caption="尝试在返回 `()` 的 `main` 函数中使用 `?`，但会导致编译失败。">

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch09-error-handling/listing-09-10/src/main.rs}}
```

</ Listing>

这段代码会打开一个文件，但可能会失败。`?`运算符会依赖于`Result`返回的值，而`File::open`会返回`()`类型的返回值，而不是`Result`类型。当我们编译这段代码时，会出现以下错误信息：

```console
{{#include ../listings/ch09-error-handling/listing-09-10/output.txt}}
```

这个错误表明，我们只能在返回 `Result`、`Option` 或实现了 `FromResidual` 的其他类型的函数中使用 `?` 运算符。

要修复这个错误，你有两种选择。一种选择是更改函数的返回类型，使其与您使用 ``?`` 操作符所得到的值兼容，只要没有限制阻止这一点。另一种选择是使用 ``match`` 或 ``Result<T, E>`` 中的某一种方法来以适当的方式处理 ``Result<T, E>``。

错误信息还提到，`?`也可以与`Option<T>`的值一起使用。就像在`Result`上使用`?`一样，你只能在返回`Option`的函数中，将`?`用于`Option`。当`?`运算符被调用到`Option<T>`上时，其行为类似于它被调用到`Result<T, E>`时的情况：如果值是`None`，那么`None`会在该函数执行到那个点时被提前返回。如果值是`Some`，那么`Some`内的数值就是表达式的结果，函数会继续执行。清单9-11是一个示例函数，它用于查找给定文本中第一行的最后一个字符。

<列表编号="9-11" 标题="在 `Option<T>` 值上使用 `?` 运算符">

```rust
{{#rustdoc_include ../listings/ch09-error-handling/listing-09-11/src/main.rs:here}}
```

</ Listing>

该函数返回 `Option<char>`，因为可能存在这样的字符，但也可能不存在。这段代码接收 `text` 类型的字符串切片参数，并调用 `lines` 方法，该方法会返回一个遍历字符串中各行的结果。由于该函数需要检查第一行，因此它会调用 `next` 来获取迭代器中的第一个值。如果 `text` 是空字符串，那么对 `next` 的调用将返回 `None`；在这种情况下，我们使用 `?` 来停止执行，并从 `last_char_of_first_line` 返回 `None`。如果 `text` 不是空字符串，那么 `next` 将返回一个包含 `text` 中第一行的字符串切片的 `Some` 值。

``?``负责提取字符串切片，然后我们可以调用``chars``来处理该字符串切片，从而获取其字符的迭代器。我们感兴趣的是这一行中的最后一个字符，因此调用``last``来返回迭代器中的最后一个元素。这里使用了``Option``，因为第一行可能是空字符串；例如，如果``text``以空白行开始，但在其他行上有字符，就像在``"\nhi"``中那样。不过，如果第一行确实有最后一个字符，那么它将通过``Some``得到。``?``操作符为我们提供了一种简洁的方式来表达这种逻辑，使我们能够用一行代码实现该函数。如果我们不能对``Option``使用``?``操作符，我们就不得不通过更多的方法调用或使用``match``表达式来实现这种逻辑。

请注意，您可以在返回`Result`的函数中使用`?`运算符，同时也可以在返回`Option`的函数中使用`?`运算符。但是，这两种运算符不能混合使用。`?`运算符不会自动将`Result`转换为`Option`，反之亦然。在这种情况下，您可以使用如`ok`方法对`Result`进行操作，或者使用`ok_or`方法对`Option`进行转换。

到目前为止，我们使用的所有`main`函数都返回`()`。而`main`函数则特别一些，因为它是可执行程序的入口点和出口点，并且对其返回类型有特定的限制，以确保程序能够正常运行。

幸运的是，`main`也可以返回`Result<(), E>`。清单9-12中的代码来自清单9-10，但我们将`main`的返回类型改为`Result<(), Box<dyn Error>>`，并在末尾添加了返回值`Ok(())`。现在这段代码可以编译了。

<listing number="9-12" file-name="src/main.rs" caption="将`main`改为return`Result<(), E>`后，就可以在`Result`值上使用`?`运算符了。">

```rust,ignore
{{#rustdoc_include ../listings/ch09-error-handling/listing-09-12/src/main.rs}}
```

</ Listing>

`Box<dyn Error>`类型是一个特质对象，我们将在第十八章的[“使用特质对象来抽象共享行为”][trait-objects]中详细讨论。目前，你可以将`Box<dyn Error>`理解为“任何类型的错误”。在`main`函数中对`Result`值使用`?`并指定错误类型为`Box<dyn Error>`是允许的，因为这允许任何`Err`类型的值被提前返回。尽管这个`main`函数的主体只会返回`std::io::Error`类型的错误，但通过指定`Box<dyn Error>`，即使有更多返回其他错误的代码被添加到`main`函数的主体中，这个签名仍然是正确的。

当`main`函数返回`Result<(), E>`时，如果`main`返回`Ok(())`，则可执行程序将以`0`的值退出；如果`main`返回`Err`值，则可执行程序将返回一个非零值。用C语言编写的可执行程序在退出时会返回整数：成功退出的程序会返回整数`0`，而发生错误的程序则会返回除`0`之外的其他整数。Rust同样允许从可执行程序返回整数，以与这一惯例保持一致。

`main`函数可以返回任何实现了[`std::process::Termination`特质][termination]的函数类型。该特质包含一个函数`report`，该函数返回一个`ExitCode`类型的值。有关如何为自己的类型实现`Termination`特质的更多信息，请参阅标准库文档。

既然我们已经讨论了调用 ``panic!`` 或返回 ``Result`` 的细节，现在让我们回到如何决定在哪些情况下使用哪种方法的主题上。

[处理失败情况]: ch02-00-guessing-game-tutorial.html#handling-potential-failure-with-result  
[特性对象]: ch18-02-trait-objects.html#using-trait-objects-to-abstract-over-shared-behavior  
[终止处理]:../std/process/trait.Termination.html