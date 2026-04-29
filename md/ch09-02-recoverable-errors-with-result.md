## 可通过`Result`恢复的错误

大多数错误并不严重到需要让程序完全停止运行。有时候，当一个函数出现故障时，其原因是可以轻易理解的，并且可以做出相应的处理。例如，如果你尝试打开一个文件，但操作失败是因为该文件不存在，那么你可以选择创建这个文件，而不是终止程序。

请回想一下在第二章中的[“使用`Result`处理潜在故障”][handle_failure]<!--
忽略 -->，其中`Result`枚举被定义为有两种变体，即`Ok`和`Err`，具体如下所示：

```rust
enum Result<T, E> {
    Ok(T),
    Err(E),
}
```

`T`和`E`是通用类型参数：我们将在第十章中详细讨论泛型。目前你需要了解的是，`T`表示在`Ok`变体中成功情况下返回的值的类型，而`E`则表示在`Err`变体失败情况下返回的错误类型的标识符。因为`Result`具有这些通用类型参数。在参数方面，我们可以使用`Result`类型，并在许多不同的情况下使用该类型所定义的函数。在这些情况下，我们想要返回的成败值可能会有所不同。

让我们定义一个函数，该函数返回一个`Result`值，因为该函数可能会失败。在清单9-3中，我们尝试打开一个文件。

<列表编号="9-3" 文件名称="src/main.rs" 标题="打开一个文件">

```rust
{{#rustdoc_include ../listings/ch09-error-handling/listing-09-03/src/main.rs}}
```

</清单>

`File::open`的返回类型是`Result<T, E>`。泛型参数`T`由`File::open`的实现填充，其中使用了success值的类型`std::fs::File`，这是一个文件句柄。在错误值中使用的`E`的类型是`std::io::Error`。这种返回类型意味着对`File::open`的调用可能会成功，并返回一个我们可以读取的文件句柄。调用该函数时也可能出现失败情况：例如，文件可能不存在，或者我们没有权限访问该文件。`File::open`函数需要有一种方式来告诉我们是否成功执行，同时还需要提供文件句柄或错误信息。这些信息正是`Result`枚举所传递的。

在`File::open`成功的情况下，变量`greeting_file_result`的值将是一个包含文件句柄的`Ok`实例。而在`File::open`失败的情况下，变量`greeting_file_result`的值将是一个包含有关发生错误类型信息的`Err`实例。

我们需要在清单9-3中的代码中添加一些逻辑，以便根据`File::open`返回的值来采取相应的操作。清单9-4展示了一种使用基本工具来处理`Result`的方法，以及我们在第6章中讨论过的`match`表达式。

<列表编号="9-4" 文件名称="src/main.rs" 标题="使用 `match` 表达式来处理可能返回的 `Result` 变体">

```rust,should_panic
{{#rustdoc_include ../listings/ch09-error-handling/listing-09-04/src/main.rs}}
```

</清单>

请注意，与`Option`枚举一样，`Result`枚举及其变体也是由prelude引入到作用域中的，因此我们不需要在`match`的`Ok`和`Err`变体中指定`Result::`。

当结果为`Ok`时，这段代码会从`Ok`变体中获取内部的`file`值，然后将该文件句柄值赋给变量`greeting_file`。在`match`之后，我们可以使用该文件句柄来进行读取或写入操作。

`match`的另一个分支处理从`File::open`获取`Err`值的情况。在这个例子中，我们选择调用`panic!`宏。如果我们当前目录中没有名为_hello.txt_的文件，并且运行这段代码，那么我们将看到`panic!`宏的输出如下：

```console
{{#include ../listings/ch09-error-handling/listing-09-04/output.txt}}
```

像往常一样，这个输出准确地告诉我们出了什么问题。

### 针对不同类型的错误进行匹配

在清单9-4中的代码无论为什么导致`File::open`失败，都会执行`panic!`。然而，我们希望针对不同的失败原因采取不同的措施。如果`File::open`因为文件不存在而失败，我们希望创建该文件，并将文件句柄返回给调用者。如果`File::open`因其他原因失败——例如，因为我们没有权限打开该文件——我们仍然希望代码以与清单9-4中相同的方式执行`panic!`。为此，我们需要……在内部添加了一个``match``表达式，如清单9-5所示。

<列表编号="9-5" 文件名称="src/main.rs" 标题="以不同方式处理不同类型的错误">

<!-- 忽略这个测试，因为否则会生成hello.txt文件，这会导致其他测试失败，哈哈 -->

```rust,ignore
{{#rustdoc_include ../listings/ch09-error-handling/listing-09-05/src/main.rs}}
```

</清单>

在`Err`变体中，`File::open`返回的值的类型是`io::Error`，这是一个由标准库提供的结构体。该结构体包含一个名为`kind`的方法，我们可以通过调用此方法来获取`io::ErrorKind`的值。枚举类型`io::ErrorKind`也是由标准库提供的，它包含多个变体，用于表示由`io`可能导致的不同类型的错误。我们正在尝试使用的变体是`ErrorKind::NotFound`，它表示我们试图打开的文件尚不存在。因此，我们会匹配`greeting_file_result`，同时还会有一个内部的匹配条件`error.kind()`。

我们想要在内部匹配中检查的条件是，``error.kind()``返回的值是否为``ErrorKind``枚举中的``NotFound``变体。如果是的话，我们会尝试使用``File::create``来创建文件。然而，由于``File::create``也可能失败，因此我们需要在内部``match``表达式中加入第二个分支。如果无法创建文件，则会打印不同的错误信息。外部代码部分``match``保持不变，因此当缺少文件时，程序会在出现任何错误的情况下崩溃。

> #### 使用`match`与`Result<T, E>`的替代方案>> 这真是大量的`match`！`match`表达式非常有用，但也很原始。在第13章中，你将学习到闭包的概念，这些概念被用于许多定义在`Result<T, E>`上的方法。当在代码中处理`Result<T, E>`值时，这些方法比使用`match`更为简洁。例如，这里还有另一种实现相同逻辑的方法，与 Listing 9-5 中的方法类似，但这次使用了闭包和 `unwrap_or_else` 方法：  
>> <!-- 无法提取代码内容，请参阅：https://github.com/rust-lang/mdBook/issues/1127 -->  
>> ```rust,ignore
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
虽然这段代码的运行结果与 Listing 9-5 相同，但它不包含任何 `match` 表达式，且可读性更强。在阅读完第13章后，可以再回到这个例子，并查阅 `unwrap_or_else` 方法的相关内容。标准库文档。在处理错误时，这些方法中有许多可以清理那些庞大且嵌套的``match``表达式。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="紧急处理错误时的快捷方式">紧急处理错误时的快捷方式</a>

#### 处理错误时的快捷方式

使用`match`效果还算不错，但这种方式可能会显得有些冗长，而且并不能很好地传达意图。`Result<T, E>`类型包含了许多辅助方法，用于执行各种更具体的任务。`unwrap`是一个简短的快捷方式，其实现方式与我们在清单9-4中编写的`match`表达式相同。如果`Result`的值与`Ok`相匹配，那么`unwrap`将会返回某个结果。在`Ok`中的值。如果`Result`是`Err`的变体，那么`unwrap`将会为我们调用`panic!`宏。以下是`unwrap`的一个使用示例：

<listing file-name="src/main.rs">

```rust,should_panic
{{#rustdoc_include ../listings/ch09-error-handling/no-listing-04-unwrap/src/main.rs}}
```

</清单>

如果我们在不提供`_hello.txt`文件的情况下运行这段代码，我们会看到来自``panic!``调用的错误信息，该错误是由``unwrap``方法引起的。

<!-- 手动重新生成
cd listings/ch09-error-handling/no-listing-04-unwrap
cargo run
复制并粘贴相关文本
-->

```text
thread 'main' panicked at src/main.rs:4:49:
called `Result::unwrap()` on an `Err` value: Os { code: 2, kind: NotFound, message: "No such file or directory" }
```

同样，`expect`方法也允许我们选择`panic!`错误信息。使用`expect`而不是`unwrap`，并提供清晰的错误信息，可以传达你的意图，并使追踪恐慌的来源变得更加容易。`expect`的语法如下所示：

<listing file-name="src/main.rs">

```rust,should_panic
{{#rustdoc_include ../listings/ch09-error-handling/no-listing-05-expect/src/main.rs}}
```

</清单>

我们使用`expect`的方式与`unwrap`相同：用于返回文件句柄或调用`panic!`宏。`expect`在调用`panic!`时使用的错误信息，将是我们传递给`expect`的参数，而不是`unwrap`所使用的默认`panic!`信息。具体如下所示：

<!-- 手动重新生成
cd listings/ch09-error-handling/no-listing-05-expect
cargo run
复制并粘贴相关文本
-->

```text
thread 'main' panicked at src/main.rs:5:10:
hello.txt should be included in this project: Os { code: 2, kind: NotFound, message: "No such file or directory" }
```

在生产级别的代码中，大多数Rust开发者更倾向于使用`expect`而不是`unwrap`。同时，他们还会提供更多的上下文信息，说明为什么这种操作被期望始终能够成功。这样一来，如果我们的假设最终被证明是错误的，我们就有更多的信息可以用来进行调试。

### 错误传播

当函数的实现调用某个可能失败的操作时，与其在函数内部处理错误，不如将错误返回给调用代码，让调用代码来决定如何处理该错误。这被称为“传播错误”，它赋予了调用代码更多的控制权，因为调用代码可能拥有更多关于如何处理错误的信息或逻辑，而这些信息或逻辑在您的代码中可能并不具备。

例如，清单9-6展示了一个从文件中读取用户名的函数。如果文件不存在或者无法读取，这个函数会将这些错误返回给调用该函数的代码。

<列表编号="9-6" 文件名称="src/main.rs" 标题="一个使用`match`将错误返回给调用代码的函数">

<!-- 故意没有使用 rustdoc_include；文件中的 `main` 函数会导致程序崩溃。我们确实希望将其包含进来以供读者实验使用，但不想将其包含在 rustdoc 的测试过程中。-->

```rust
{{#include ../listings/ch09-error-handling/listing-09-06/src/main.rs:here}}
```

</清单>

这个函数可以用更简洁的方式编写，但我们首先会手动执行很多操作来探索错误处理的过程；最后，我们会展示更简洁的方法。首先，让我们看看这个函数的返回类型：`Result<String, io::Error>`。这意味着该函数返回的是`Result<T, E>`类型的数值，其中通用参数`T`已经被具体类型`String`替代，而通用类型`E`则保持不变。填充了具体类型`io::Error`。

如果此函数能够顺利执行，那么调用此函数的代码将收到一个`Ok`的值，该值中包含`String`——也就是此函数从文件中读取到的`username`。如果此函数遇到任何问题，调用代码的将会收到一个`Err`的值，该值中包含`io::Error`的实例，而`io::Error`则包含了关于问题的更多详细信息。我们选择了这种方式。`io::Error`被用作此函数的返回类型，因为这正是我们在该函数体内调用的两个可能失败的操作所返回的错误值的类型：`File::open`函数和`read_to_string`方法。

该函数的主体首先调用了`File::open`函数。然后，我们使用`match`来处理`Result`的值，这与清单9-4中的`match`类似。如果`File::open`成功执行，那么模式变量`file`中的文件句柄就会成为可变变量`username_file`的值，之后函数将继续执行。在`Err`的情况下，我们不会调用`panic!`，而是使用`return`。需要返回一个关键词，使其完全从函数中返回，并将错误值从`File::open`传递到调用代码，此时该错误值存储在模式变量`e`中。

因此，如果我们有一个文件句柄在`username_file`中，那么该函数会在变量`username`中创建一个新的`String`，并在`username_file`中的文件句柄上调用`read_to_string`方法来读取文件的内容到`username`中。`read_to_string`方法也会返回一个`Result`值，因为即使`File::open`成功执行了，它仍有可能失败。所以，我们需要另一个`match`来……处理 `Result`：如果 `read_to_string` 成功执行，那么我们的函数就成功了，此时我们会从文件中提取用户名，该文件现在被包含在 `Ok` 中。如果 `read_to_string` 失败，我们会以与处理 `File::open` 中的错误值相同的方式返回错误值。不过，我们不需要明确说明这一点。`return`，因为这是该函数的最后一个表达式。

调用此代码的代码将负责获取一个包含用户名的值 ``Ok``，或者一个包含 ``io::Error`` 的值 ``Err`$。接下来由调用该代码的代码来决定如何处理这些值。如果调用代码获取到 ``Err`` 的值，它可能会调用 ``panic!``，从而导致程序崩溃；或者使用默认的用户名；或者从文件之外的其他地方查找用户名。例如，我们并没有足够的信息来了解调用代码实际上想要做什么，因此我们将所有的成功或错误信息向上传递，以便由上层代码进行适当的处理。

在Rust中，这种错误传播的模式非常常见，因此Rust提供了``?``这个问号运算符，以便更方便地处理这种情况。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="一种用于传播错误的快捷方式——操作员"></a>

#### `?` 运算符的快捷方式

清单9-7展示了`read_username_from_file`的实现，其功能与清单9-6相同，但此实现使用了`?`运算符。

<列表编号="9-7" 文件名称="src/main.rs" 标题="一个使用`?`操作符将错误返回给调用代码的函数">

<!-- 故意没有使用 rustdoc_include；文件中的 `main` 函数会导致程序崩溃。我们确实希望将其包含在内以供读者实验使用，但不想将其包含在 rustdoc 的测试过程中。-->

```rust
{{#include ../listings/ch09-error-handling/listing-09-07/src/main.rs:here}}
```

</清单>

在`Result`之后定义的`?`，其工作方式几乎与我们在Listing 9-6中定义的用于处理`Result`值的`match`表达式相同。如果`Result`的值是一个`Ok`，那么`Ok`内的内容将会被返回，程序将继续运行。`value`是一个``Err``，而``Err``会从整个函数中返回，就像我们使用了``return``关键字一样，这样错误值就会传播到调用代码中。

Listing 9-6中的`match`表达式与`?`运算符的作用是不同的：那些调用了`?`运算符的错误值会经过标准库中定义的`From`特征中的`from`函数进行处理，该函数用于将一种类型的值转换为另一种类型。当`?`运算符调用`from`函数时，接收到的错误类型就是……该错误类型被转换为当前函数返回类型中定义的错误类型。当一个函数返回一个错误类型时，这非常有用，因为它能够表示函数可能出现的所有故障情况，即使某些部分可能因为多种不同的原因而失败。

例如，我们可以修改清单9-7中的`read_username_from_file`函数，使其返回我们自定义的误差类型`OurError`。如果我们同时定义`impl From<io::Error> for OurError`，以便从`io::Error`构造出`OurError`的实例，那么位于`read_username_from_file`体内的`?`操作符调用将会调用`from`，从而将误差类型进行转换，而无需在函数中添加更多的代码。

在清单9-7的上下文中，位于`File::open`末尾的`?`会将`Ok`内部的值返回给变量`username_file`。如果发生错误，`?`运算符会在整个函数执行过程中提前终止，并将任何`Err`的值返回给调用代码。同样的情况也适用于位于`read_to_string`末尾的`?`。

`?`运算符消除了大量的样板代码，使得这个函数的实现更加简洁。我们甚至可以通过在`?`之后立即链接方法调用来进一步缩短代码，如清单9-8所示。

<列表编号="9-8" 文件名称="src/main.rs" 标题="在`?`运算符之后链接方法调用">

<!-- 故意没有使用 rustdoc_include；文件中的 `main` 函数会导致程序崩溃。我们确实希望将其包含进来以供读者实验使用，但不想将其包含在 rustdoc 的测试过程中。-->

```rust
{{#include ../listings/ch09-error-handling/listing-09-08/src/main.rs:here}}
```

</清单>

我们将在`username`中创建新的`String`的功能移到了函数的开头；这部分并没有改变。我们没有创建变量`username_file`，而是将`read_to_string`的调用直接链接到`File::open("hello.txt")?`的结果上。在`read_to_string`的调用末尾仍然有一个`?`，并且我们仍然返回一个包含`username`的`Ok`值。当`File::open`和`read_to_string`都成功执行时，不会返回错误。其功能与Listing 9-6和Listing 9-7中的相同；这只是另一种更易于使用的编写方式而已。

清单9-9展示了如何使用`fs::read_to_string`来使代码更加简洁。

<列表编号="9-9" 文件名称="src/main.rs" 标题="使用`fs::read_to_string`而不是直接打开然后读取文件">

<!-- 故意没有使用 rustdoc_include；文件中的 `main` 函数会导致程序崩溃。我们确实希望将其包含进来以供读者实验使用，但不想将其包含在 rustdoc 的测试过程中。-->

```rust
{{#include ../listings/ch09-error-handling/listing-09-09/src/main.rs:here}}
```

</清单>

将文件读取到字符串中是一个相当常见的操作，因此标准库提供了方便的`fs::read_to_string`函数。该函数可以打开文件，创建一个新的`String`对象，读取文件的内容，将这些内容放入`String`对象中，然后返回该对象。当然，使用`fs::read_to_string`并不能让我们详细解释所有的错误处理机制，所以我们还是选择采用更传统的处理方式。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="where-the--operator-can-be-used"></a>

#### 在何处使用 `?` 运算符

`?`运算符只能用于返回类型与`?`所操作的值兼容的函数中。这是因为`?`运算符被定义为在函数外部提前返回一个值，其方式与我们在第9-6节中定义的`match`表达式相同。在第9-6节中，`match`使用了`Result`的值，而提前返回的部分则返回一个值。`Err(e)`值。该函数的返回类型必须是`Result`类型，以便与这个`return`兼容。

在清单9-10中，我们将看看如果我们在一个返回类型与``?``所操作的值的类型不兼容的``main``函数中使用``?``运算符时，会遇到的错误。

<Listing number="9-10" file-name="src/main.rs" caption="尝试在返回 `()` 的 `main` 函数中使用 `?`，但会导致编译失败。">

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch09-error-handling/listing-09-10/src/main.rs}}
```

</清单>

这段代码试图打开一个文件，但可能会失败。`?`运算符会依赖于`Result`返回的值，而`File::open`则负责返回该值。不过，`main`函数的返回类型却是`()`，而不是`Result`。当我们编译这段代码时，会出现以下错误信息：

```console
{{#include ../listings/ch09-error-handling/listing-09-10/output.txt}}
```

这个错误表明，我们只能在返回 `Result`、`Option` 或实现了 `FromResidual` 的其他类型的函数中使用 `?` 运算符。

要修复这个错误，你有两种选择。一种选择是更改函数的返回类型，使其与您使用 ``?`` 操作符所处理的值兼容，前提是没有任何限制阻止这样做。另一种选择是使用 ``match`` 或 ``Result<T, E>`` 中的任何一种方法来以适当的方式处理 ``Result<T, E>``。

错误信息还提到，`?`也可以与`Option<T>`一起使用。就像在`Result`上使用`?`一样，你只能在返回`Option`的函数中，将`?`用于`Option`。当`?`运算符在`Option<T>`上被调用时，其行为类似于它在`Result<T, E>`上被调用时的行为。如果值为`None`，那么`None`将在该函数执行到那个点时提前被返回。如果值为`Some`，那么`Some`内的数值就是表达式的结果，函数将继续执行。清单9-11展示了一个用于获取给定文本首行最后一个字符的函数示例。

<列表编号="9-11" 标题="在 `Option<T>` 值上使用 `?` 运算符">

```rust
{{#rustdoc_include ../listings/ch09-error-handling/listing-09-11/src/main.rs:here}}
```

</清单>

该函数返回`Option<char>`，因为可能存在一个字符在该位置，但也可能不存在这样的字符。这段代码接收`text`字符串切片参数，并调用`lines`方法，该方法返回一个遍历字符串中各行数据的迭代器。由于该函数需要检查第一行，因此它会使用`next`对迭代器进行操作，以获取第一行数据。从迭代器中获取数据。如果`text`为空字符串，那么对`next`的调用将返回`None`；在这种情况下，我们使用`?`来停止迭代，并从`last_char_of_first_line`中返回`None`。如果`text`不为空字符串，那么`next`将返回一个包含`text`第一行字符串片段的`Some`值。

`?`负责提取字符串切片，而我们可以调用`chars`来处理该字符串切片，从而获取其字符的迭代器。我们感兴趣的是这一行中的最后一个字符，因此调用`last`来返回迭代器中的最后一个元素。这是一个`Option`，因为有可能这一行是空字符串；例如，如果`text`以空白行开始，但其中包含字符的话……其他行，如`"\nhi"`中的内容。不过，如果第一行有最后一个字符，那么它将以`Some`的形式返回。中间的`?`运算符为我们提供了一种简洁的方式来表达这种逻辑，使我们能够在一行代码中实现该函数。如果我们不能对`Option`使用`?`运算符，那么我们就需要使用更多的方法调用或者`match`表达式来实现这种逻辑。

请注意，您可以在返回`Result`的函数中的`Result`上使用`?`运算符，也可以在返回`Option`的函数中的`Option`上使用`?`运算符，但是这两种运算符不能混合使用。`?`运算符不会自动将`Result`转换为`Option`，反之亦然；在这种情况下，需要手动进行转换。您可以使用像`ok`方法对`Result`进行操作，或者使用`ok_or`方法对`Option`进行转换，从而实现显式的转换操作。

到目前为止，我们使用的所有`main`函数都返回`()`。而`main`函数则有些特殊，因为它是可执行程序的入口点和出口点，并且对其返回类型有特定的限制，以确保程序能够正常运行。

幸运的是，`main`也可以返回`Result<(), E>`。清单9-12中包含了与清单9-10相同的代码，但我们将`main`的返回类型改为`Result<(), Box<dyn Error>>`，并在末尾添加了返回值`Ok(())`。现在这段代码可以编译了。

<列表编号="9-12" 文件名称="src/main.rs" 标题="将`main`改为return `Result<(), E>`后，可以在`Result`值上使用`?`运算符。">

```rust,ignore
{{#rustdoc_include ../listings/ch09-error-handling/listing-09-12/src/main.rs}}
```

</清单>

`Box<dyn Error>`类型是一个特质对象，我们将在第十八章的“使用特质对象来抽象共享行为”部分进行讨论。目前，你可以将`Box<dyn Error>`理解为“任何类型的错误”。在`main`函数中对`Result`值使用`?`，并指定错误类型为`Box<dyn Error>`是允许的，因为这允许返回任何`Err`类型的值。虽然这个`main`函数的主体只会返回类型为`std::io::Error`的错误，但通过指定`Box<dyn Error>`，即使向`main`的体内添加了返回其他错误的代码，该签名仍然保持正确。

当`main`函数返回`Result<(), E>`时，如果`main`返回`Ok(())`，则可执行文件将以`0`的值退出；如果`main`返回`Err`的值，则可执行文件将以非零值退出。用C语言编写的可执行文件在退出时会返回整数：成功退出的程序会返回整数`0`。那个错误返回了一个与`0`不同的整数。Rust也会从可执行文件中返回整数，以符合这一惯例。

`main`函数可以返回任何实现了[`std::process::Termination`特征][终止条件]的类型。该特征包含一个函数`report`，该函数返回一个`ExitCode`类型的值。有关如何为自己的类型实现`Termination`特征的更多信息，请参阅标准库文档。

既然我们已经讨论了调用`panic!`或返回`Result`的细节，现在让我们回到如何决定在哪些情况下使用哪种方法的主题上。

[处理失败情况]: ch02-00-guessing-game-tutorial.html#handling-potential-failure-with-result
[特性对象]: ch18-02-trait-objects.html#using-trait-objects-to-abstract-over-shared-behavior
[终止处理]:../std/process/trait.Termination.html