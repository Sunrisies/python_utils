## 重构以提高模块化和错误处理能力

为了改进我们的程序，我们需要解决四个与程序结构以及处理潜在错误相关的问题。首先，我们的 `main` 函数现在执行两项任务：解析参数和读取文件。随着程序的不断发展， `main` 函数需要处理的独立任务数量将会增加。当一个函数承担更多的职责时，它就会变得更加难以理解、难以测试，而且在不破坏其某个部分的情况下进行修改也会变得更加困难。因此，最好将功能分离，让每个函数只负责一项任务。

这个问题也涉及到第二个问题：虽然 `query` 和 `file_path` 是我们的程序的配置变量，但像 `contents` 这样的变量则用于执行程序的逻辑。当 `main` 的长度增加时，我们需要引入更多的变量；而变量越多，就越难以明确每个变量的作用。因此，最好将配置变量归类到一个结构中，以便明确它们的用途。

第三个问题是，我们在读取文件失败时使用了 `expect` 来打印错误信息，但实际上打印出来的却是 `Should have been
able to read the file`。文件读取失败可能有多种原因：例如，文件可能缺失，或者我们没有权限打开该文件。目前，无论哪种情况，我们都会打印相同的错误信息，这并不能为用户提供任何有用的信息！

第四，我们使用 `expect` 来处理错误。如果用户在不指定足够参数的情况下运行我们的程序，他们将收到来自 Rust 的 `index out of bounds` 错误提示，而该错误提示并不能清楚地解释问题所在。最好将所有错误处理代码放在一个地方，这样未来的维护人员只需查阅一个地方，就能了解错误处理逻辑是否需要修改。将所有错误处理代码放在一个地方，还可以确保我们打印出的消息对最终用户来说具有意义。

让我们通过重构项目来解决这四个问题。

<!-- Old headings. Do not remove or links may break. -->

<a id="separation-of-concerns-for-binary-projects"></a>

### 在二进制项目中分离关注点

将多个任务的职责分配给 `main` 函数的组织问题，在许多二进制项目中都很常见。因此，当 `main` 函数变得庞大时，许多 Rust 程序员认为将二进制程序的各个部分分开处理是非常有用的。这个过程包括以下步骤：

- 将你的程序拆分为一个 _main.rs_ 文件和一个 _lib.rs_ 文件，并将程序的逻辑放在 _lib.rs_ 文件中。
- 只要命令行解析逻辑比较简单，就可以保留在 `main` 函数中。
- 当命令行解析逻辑变得复杂时，可以将其从 `main` 函数中分离出来，并创建其他函数或类型来处理这些逻辑。

经过这个过程之后，`main`函数中仍然存在的职责应该仅限于以下方面：

- 使用参数值调用命令行解析逻辑  
- 设置其他相关配置  
- 在 _lib.rs_ 中调用 `run` 函数  
- 如果 `run` 返回错误，则处理该错误

这种模式旨在将不同功能分离开来：_main.rs_ 负责程序的运行，而 _lib.rs_ 则负责处理当前任务的所有逻辑。由于无法直接测试 `main` 这个函数，这种结构允许你将整个程序的逻辑分离出来，从而进行测试。留在 `main` 函数中的代码规模足够小，可以通过阅读来验证其正确性。让我们按照这个流程来重新设计我们的程序。

#### 提取参数解析器

我们将把解析参数的功能提取到一个函数中，这个函数会被调用。列表12-5展示了新的 `main` 函数的开始部分，该函数会调用一个新的 `parse_config` 函数。我们将在 _src/main.rs_ 中定义 `parse_config` 函数。

<Listing number="12-5" file-name="src/main.rs" caption="Extracting a `parse_config` function from `main`">

```rust,ignore
fn main() {
    let args: Vec<String> = env::args().collect();

    let (query, file_path) = parse_config(&args);

    // --snip--
}

fn parse_config(args: &[String]) -> (&str, &str) {
    let query = &args[1];
    let file_path = &args<!-- ignore -->;

    (query, file_path)
}

```

</Listing>

我们仍在将命令行参数收集到一个向量中，但是，我们并没有在 `main` 函数中将索引为1的参数值赋值给变量 `query`，也没有将索引为2的参数值赋值给变量 `file_path`。相反，我们将整个向量传递给 `parse_config` 函数。然后，`parse_config` 函数负责确定哪些参数应该赋值给哪些变量，并将这些值传递回 `main`。我们仍然在 `main` 中创建了 `query` 和 `file_path` 变量，但是 `main` 不再有决定命令行参数和变量之间关系的责任。

这次重构对我们这个小型程序来说可能显得有些过度，但我们是在逐步、小步骤地进行重构。完成这个改动后，请再次运行程序，以确认参数解析功能仍然正常工作。经常检查进度是非常好的做法，这样可以在出现问题时及时找到问题的原因。

#### 分组配置值

我们可以再迈出一小步，以进一步改进 `parse_config` 这个函数。目前，我们返回的是一个元组，但随后又立即将这个元组拆分成多个独立的元素。这表明我们可能还没有达到正确的抽象层次。

另一个表明需要改进的指标是 `parse_config` 中的 `config` 部分。这部分表明我们返回的两个值是相关的，并且都属于同一个配置值的一部分。目前，除了将这两个值组合成一个元组之外，我们在数据结构中并没有明确表达这一含义。我们将这两个值放入一个结构体中，并为每个结构体字段赋予有意义的名称。这样做将有助于未来的维护者更容易理解这些不同值之间的关系以及它们的用途。

列表12-6展示了`parse_config`函数的改进之处。

<Listing number="12-6" file-name="src/main.rs" caption="Refactoring `parse_config` to return an instance of a `Config` struct">

```rust,should_panic,noplayground
fn main() {
    let args: Vec<String> = env::args().collect();

    let config = parse_config(&args);

    println!("Searching for {}", config.query);
    println!("In file {}", config.file_path);

    let contents = fs::read_to_string(config.file_path)
        .expect("Should have been able to read the file");

    // --snip--
}

struct Config {
    query: String,
    file_path: String,
}

fn parse_config(args: &[String]) -> Config {
    let query = args[1].clone();
    let file_path = args[2].clone();

    Config { query, file_path }
}

```

</Listing>

我们添加了一个名为 `Config` 的结构体，该结构体包含名为 `query` 和 `file_path` 的字段。 `parse_config` 的签名现在表明它返回一个 `Config` 类型的值。在 `parse_config` 的内部，我们过去返回的是引用 `String` 在 `args` 中的值的字符串切片，现在我们将 `Config` 定义为包含被 `String` 拥有的值。在 `main` 中的 `args` 变量是参数值的所有者，它只允许 `parse_config` 函数借用这些值。如果 `Config` 试图获取 `args` 中的这些值的所有权，那么就会违反 Rust 的借用规则。

我们有多种方法来处理 `String` 数据。最简单的方法是在值上调用 `clone` 方法。这样做会为 `Config` 实例创建一个完整的数据副本，但这需要比直接存储字符串数据更多的时间和内存。不过，克隆数据也使得我们的代码更加简洁，因为我们不必管理这些引用的生命周期。在这种情况下，为了简单起见而牺牲一点性能是值得的。

> ### 使用 `clone` 的权衡  
> 许多 Rust 开发者倾向于避免使用 `clone` 来解决所有权问题，因为其运行成本较高。在[第13章][ch13]<!-- ignore -->中，你将学习如何在这种情况下使用更高效的方法。不过，目前可以复制一些字符串以继续开发，因为这样的复制操作只会进行一次，而且文件路径和查询字符串都非常短。与其在初次开发时就过度优化代码，不如先实现一个功能正常的程序，虽然这样效率会稍低一些。随着你对 Rust 的熟悉程度提高，以后使用最高效的解决方案会变得更加容易，但现在使用 `clone` 也是完全可以接受的。

我们已经更新了 `main` 这个函数，使其将 `Config` 的实例存储在名为 `config` 的变量中。同时，我们更新了之前使用单独的 `query` 和 `file_path` 变量的代码，现在这些变量可以使用 `Config` 结构体中的字段来替代。

现在，我们的代码更清楚地表明了 `query` 和 `file_path` 是相关的，它们的目的是配置程序的运行方式。任何使用这些值的代码都应当知道在 `config` 实例中，在为其目的而指定的字段里找到它们。

#### 为 `Config` 创建构造函数

到目前为止，我们已经提取了负责解析命令行参数的逻辑，并将其放在 `parse_config` 函数中。这样做后，我们发现 `query` 和 `file_path` 的值之间存在关联，而这种关联应该被体现在我们的代码中。接着，我们创建了一个 `Config` 结构体，用来命名 `query` 和 `file_path` 的相关功能，并且能够从 `parse_config` 函数中返回这些值的名称作为结构体字段的名称。

因此，既然 `parse_config` 函数的目的是创建一个 `Config` 实例，那么我们可以将 `parse_config` 从普通函数改为一个与 `Config` 结构体相关联的命名函数 `new`。进行这样的修改后，代码会更加符合编程习惯。我们可以通过调用 `String::new` 来创建标准库中的类型实例，例如 `String`。同样地，通过将 `parse_config` 改为与 `Config` 相关联的 `new` 函数，我们就可以通过调用 `Config::new` 来创建 `Config` 的实例。列表 12-7 展示了我们需要进行的修改。

<Listing number="12-7" file-name="src/main.rs" caption="Changing `parse_config` into `Config::new`">

```rust,should_panic,noplayground
fn main() {
    let args: Vec<String> = env::args().collect();

    let config = Config::new(&args);

    // --snip--
}

// --snip--

impl Config {
    fn new(args: &[String]) -> Config {
        let query = args[1].clone();
        let file_path = args[2].clone();

        Config { query, file_path }
    }
}

```

</Listing>

我们已经更新了 `main` 这个函数的调用方式，原本使用的是 `parse_config`，现在改为使用 `Config::new`。同时，我们将 `parse_config` 的名称改为 `new`，并将其移入 `impl` 块中，这样就能将 `new` 函数与 `Config` 关联起来。请尝试再次编译这段代码，以确保其能够正常运行。

### 修复错误处理问题

现在我们将着手修复我们的错误处理问题。请记住，如果 `args` 向量中索引为1或2的值无法访问，程序将会崩溃，因为该向量中的项目数量少于三个。尝试不传递任何参数来运行程序，程序的样子应该像这样：

```console
$ cargo run
   Compiling minigrep v0.1.0 (file:///projects/minigrep)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.0s
     Running `target/debug/minigrep`

thread 'main' panicked at src/main.rs:27:21:
index out of bounds: the len is 1 but the index is 1
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace

```

行“`index out of bounds: the len is 1 but the index is 1`”是一个错误消息，是专门给程序员看的。它并不能帮助我们的最终用户了解他们应该做什么。我们现在就来修复这个问题吧。

#### 改进错误信息

在 Listing 12-8 中，我们在 `new` 函数中添加了一个检查，用于验证切片的长度是否足够，才能访问索引 1 和索引 2。如果切片的长度不足，程序会崩溃，并显示更详细的错误信息。

<Listing number="12-8" file-name="src/main.rs" caption="Adding a check for the number of arguments">

```rust,ignore
    // --snip--
    fn new(args: &[String]) -> Config {
        if args.len() < 3 {
            panic!("not enough arguments");
        }
        // --snip--

```

</Listing>

这段代码与我们在[Listing 9-13][ch9-custom-types]中编写的`Guess::new`函数类似。当`value`参数的值超出有效范围时，我们会调用`panic!`函数。在这里，我们不是检查一系列值，而是检查`args`的长度是否至少为`3`，并且函数的其余部分可以假设这个条件已经得到满足。如果`args`中的项目数量少于三个，那么就会触发`true`条件，此时我们会调用`panic!`宏来立即终止程序。

在 `new` 中添加这几行额外的代码后，让我们再次运行程序，而不使用任何参数，看看现在的错误是什么样子：

```console
$ cargo run
   Compiling minigrep v0.1.0 (file:///projects/minigrep)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.0s
     Running `target/debug/minigrep`

thread 'main' panicked at src/main.rs:26:13:
not enough arguments
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace

```

这个输出已经更好了：我们现在得到了一个合理的错误信息。不过，还有一些多余的信息是我们不想提供给用户的。也许我们在清单9-13中使用的技术并不适合这里：对于编程问题来说，调用`panic!`更为合适，而不是用于使用问题，[如第9章所讨论的那样][ch9-error-guidelines]<!-- ignore -->。相反，我们将使用你在第9章中学到的另一种技术——[返回一个`Result`][ch9-result]<!-- ignore -->，这个返回值可以表示成功或错误。

<!-- Old headings. Do not remove or links may break. -->

<a id="returning-a-result-from-new-instead-of-calling-panic"></a>

#### 返回 `Result` 而不是调用 `panic!`

我们可以返回一个 `Result` 值，该值在成功的情况下会包含一个 `Config` 实例，并在出错的情况下描述问题。我们还将函数名称从 `new` 改为 `build`，因为许多程序员期望 `new` 函数永远不会失败。当 `Config::build` 与 `main` 进行通信时，我们可以使用 `Result` 类型来表明存在问题。然后，我们可以修改 `main`，将 `Err` 变体转换为对用户来说更实用的错误信息，而不需要包含关于 `thread
'main'` 和 `RUST_BACKTRACE` 的额外文本，这些文本通常用来说明调用 `panic!` 所导致的错误。

列表12-9展示了我们需要对现在调用的函数 `Config::build` 的返回值进行的变化，以及为了使函数 body 能够返回 `Result` 而需要做的修改。请注意，这些更改只有在同时更新 `main` 之后才能编译成功，我们将在下一个列表中对此进行更新。

<Listing number="12-9" file-name="src/main.rs" caption="Returning a `Result` from `Config::build`">

```rust,ignore,does_not_compile
impl Config {
    fn build(args: &[String]) -> Result<Config, &'static str> {
        if args.len() < 3 {
            return Err("not enough arguments");
        }

        let query = args[1].clone();
        let file_path = args[2].clone();

        Ok(Config { query, file_path })
    }
}

```

</Listing>

我们的 `build` 函数会在成功情况下返回一个 `Result`，该 `Result` 包含一个 `Config` 实例；在错误情况下则返回一个字符串字面量。我们的错误值始终为具有 `'static` 生命周期的字符串字面量。

我们在函数的主体中进行了两项修改：当用户提供的参数不足时，不再调用 `panic!`，而是返回 `Err` 的值。此外，我们将 `Config` 的返回值包装在 `Ok` 中。这些修改使得函数符合新的类型签名。

从 `Config::build` 返回一个 `Err` 值，可以让 `main` 函数能够处理从 `build` 函数返回的值，并在出现错误时更干净地退出进程。

<!-- Old headings. Do not remove or links may break. -->

<a id="calling-confignew-and-handling-errors"></a>

#### 调用 `Config::build` 并处理错误

为了处理错误情况并输出用户友好的消息，我们需要更新`main`以处理`Result`由`Config::build`返回的情况，如清单12-10所示。我们还将把带有非零错误代码的命令行工具退出责任从`panic!`中分离出来，而是由我们自己来实现。非零退出状态是一种惯例，用于向调用我们程序的进程表明该程序以错误状态退出。

<Listing number="12-10" file-name="src/main.rs" caption="Exiting with an error code if building a `Config` fails">

```rust,ignore
use std::process;

fn main() {
    let args: Vec<String> = env::args().collect();

    let config = Config::build(&args).unwrap_or_else(|err| {
        println!("Problem parsing arguments: {err}");
        process::exit(1);
    });

    // --snip--

```

</Listing>

在本文档中，我们使用了一个尚未详细讨论的方法：`unwrap_or_else`。该方法由标准库定义，适用于 `Result<T, E>`。使用 `unwrap_or_else` 可以让我们定义一些自定义的、非 `panic!` 的错误处理机制。如果 `Result` 是一个 `Ok` 类型的值，那么这个方法的行为类似于 `unwrap`：它返回 `Ok` 所包裹的内部值。然而，如果该值是 `Err` 类型的值，那么这个方法会调用闭包中的代码，即我们定义并作为参数传递给 `unwrap_or_else` 的匿名函数。我们将在 [第13章][ch13]<!-- ignore --> 中更详细地介绍闭包。目前，你只需要知道 `unwrap_or_else` 会将 `Err` 的内部值传递给闭包，在这个案例中，这个内部值就是我们在 Listing 12-9 中添加的静态字符串 `"not enough arguments"`。然后，闭包中的代码可以在运行时使用 `err` 类型的值。

我们添加了一条新的 `use` 语句，将标准库中的 `process` 引入到当前代码范围内。在错误情况下会执行的闭包中的代码只有两行：首先打印 `err` 的值，然后调用 `process::exit`。`process::exit` 函数会立即终止程序，并返回作为退出状态代码的数值。这与我们在 Listing 12-8 中使用的基于 `panic!` 的处理方式类似，但我们不再获得所有额外的输出信息。让我们试试看：

```console
$ cargo run
   Compiling minigrep v0.1.0 (file:///projects/minigrep)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.48s
     Running `target/debug/minigrep`
Problem parsing arguments: not enough arguments

```

太好了！这样的输出对我们的用户来说更加友好。

<!-- Old headings. Do not remove or links may break. -->

<a id="extracting-logic-from-the-main-function"></a>

### 从 `main` 中提取逻辑

现在我们已经完成了配置解析的重构工作，接下来让我们来看看程序的逻辑部分。正如我们在[“在二进制项目中分离关注点”](#separation-of-concerns-for-binary-projects)中所述，我们会提取一个名为 `run` 的函数，该函数将包含目前位于 `main` 函数中的所有逻辑，但这些逻辑并不涉及配置设置或错误处理。完成后， `main` 函数将会更加简洁，并且可以通过检查来验证其正确性。同时，我们还可以为所有其他逻辑编写测试。

列表12-11展示了提取 `run` 函数时取得的微小改进。

<Listing number="12-11" file-name="src/main.rs" caption="Extracting a `run` function containing the rest of the program logic">

```rust,ignore
fn main() {
    // --snip--

    println!("Searching for {}", config.query);
    println!("In file {}", config.file_path);

    run(config);
}

fn run(config: Config) {
    let contents = fs::read_to_string(config.file_path)
        .expect("Should have been able to read the file");

    println!("With text:\n{contents}");
}

// --snip--

```

</Listing>

现在，`run`函数包含了从`main`开始的所有剩余逻辑，这些逻辑都是从读取文件开始的。`run`函数则接受一个`Config`实例作为参数。

<!-- Old headings. Do not remove or links may break. -->

<a id="returning-errors-from-the-run-function"></a>

#### 从 `run` 返回错误

通过将剩余的程序逻辑分离到 `run` 函数中，我们可以改进错误处理机制，就像我们在 Listing 12-9 中的 `Config::build` 所做的那样。与让程序通过调用 `expect` 而陷入恐慌不同，当出现问题时， `run` 函数会返回 `Result<T, E>`。这样，我们就可以以更用户友好的方式，将错误处理逻辑进一步整合到 `main` 中。Listing 12-12 展示了我们需要对 `run` 的函数签名和函数体所做的修改。

<Listing number="12-12" file-name="src/main.rs" caption="Changing the `run` function to return `Result`">

```rust,ignore
use std::error::Error;

// --snip--

fn run(config: Config) -> Result<(), Box<dyn Error>> {
    let contents = fs::read_to_string(config.file_path)?;

    println!("With text:\n{contents}");

    Ok(())
}

```

</Listing>

我们在这里做出了三个重要的修改。首先，我们将`run`函数的返回类型改为`Result<(), Box<dyn Error>>`。这个函数之前返回的是单位类型`()`，而我们在`Ok`情况下仍然使用这个类型作为返回值。

对于错误类型，我们使用了trait对象 `Box<dyn Error>`（并且我们通过位于顶部的 `use` 语句将 `std::error::Error` 引入到作用域中）。我们将在[第18章][ch18]<!-- ignore -->中详细讨论trait对象。目前，只需知道 `Box<dyn Error>` 表示该函数将返回一个实现了 `Error` trait 的类型，但我们不必指定返回值的具体类型。这使我们能够在不同的错误情况下返回不同类型的错误值。`dyn` 是 _dynamic_ 的缩写。

其次，我们替换了对 `expect` 的调用，转而使用 `?` 运算符，正如我们在[第9章][ch9-question-mark]<!-- ignore -->中讨论过的。与`panic!`那样直接返回错误信息不同，`?`会返回当前函数中的错误值，由调用者自行处理。

第三，`run`函数在成功情况下现在返回的是一个`Ok`值。  
我们在函数声明中将`run`函数的成功类型定义为`()`，这意味着我们需要将单位类型值包裹在`Ok`值中。这种`Ok(())`语法乍看之下可能有些奇怪。但是，像这样使用`()`是一种惯用的方式，用来表示我们只调用`run`函数以执行其副作用，而并不返回我们需要的值。

当你运行这段代码时，它会编译成功，但会显示一个警告：

```console
$ cargo run -- the poem.txt
   Compiling minigrep v0.1.0 (file:///projects/minigrep)
warning: unused `Result` that must be used
  --> src/main.rs:19:5
   |
19 |     run(config);
   |     ^^^^^^^^^^^
   |
   = note: this `Result` may be an `Err` variant, which should be handled
   = note: `#[warn(unused_must_use)]` on by default
help: use `let _ = ...` to ignore the resulting value
   |
19 |     let _ = run(config);
   |     +++++++

warning: `minigrep` (bin "minigrep") generated 1 warning
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.71s
     Running `target/debug/minigrep the poem.txt`
Searching for the
In file poem.txt
With text:
I'm nobody! Who are you?
Are you nobody, too?
Then there's a pair of us - don't tell!
They'd banish us, you know.

How dreary to be somebody!
How public, like a frog
To tell your name the livelong day
To an admiring bog!


```

Rust 告诉我们，我们的代码忽略了 `Result` 和 `Result` 这两个值，这可能会表明出现了错误。但是，我们没有检查是否真的发生了错误，编译器提醒我们，我们可能本应该在这里添加一些错误处理代码！现在让我们解决这个问题吧。

#### 处理从 `run` 到 `main` 过程中返回的错误

我们将检查错误，并使用一种类似于我们在 Listing 12-10 中用于 `Config::build` 的技术来处理这些错误，不过有一些细微的差别：

<span class="filename"> 文件名: src/main.rs</span>

```rust,ignore
fn main() {
    // --snip--

    println!("Searching for {}", config.query);
    println!("In file {}", config.file_path);

    if let Err(e) = run(config) {
        println!("Application error: {e}");
        process::exit(1);
    }
}

```

我们使用 `if let` 而不是 `unwrap_or_else` 来检查 `run` 是否返回了 `Err` 类型的值，并在返回该值时调用 `process::exit(1)`。`run` 函数并不返回我们想要的值，而且它的返回方式与 `Config::build` 返回 `Config` 实例的方式不同。由于 `run` 在成功情况下会返回 `()`，因此我们只需要检测错误，所以不需要让 `unwrap_or_else` 返回解包后的值，因为那样只会得到 `()`。

在两种情况下，`if let`和`unwrap_or_else`函数的行为是相同的：我们打印出错误信息并退出程序。

### 将代码拆分为一个库包

我们的 `minigrep` 项目目前进展得很顺利！现在我们将把 src/main.rs 文件拆分成两个文件，并将一些代码放入 src/lib.rs 文件中。这样，我们就可以对代码进行测试，同时让 src/main.rs 文件的职责变得更简单。

让我们在 _src/lib.rs_ 中定义负责搜索文本的代码，而不是在 _src/main.rs_ 中。这样，我们或任何使用我们的`minigrep`库的人都可以从更多的上下文中调用搜索函数，而不仅仅是我们的`minigrep`二进制文件。

首先，让我们在`_src/lib.rs_`中定义`search`函数的签名，如清单12-13所示，并且该函数的主体会调用`unimplemented!`宏。当我们完成实现时，会详细解释这个签名。

<Listing number="12-13" file-name="src/lib.rs" caption="Defining the `search` function in *src/lib.rs*">

```rust,ignore,does_not_compile
pub fn search<'a>(query: &str, contents: &'a str) -> Vec<&'a str> {
    unimplemented!();
}

```

</Listing>

我们在函数定义中使用了`pub`这个关键字，来表示`search`是我们库的公共API的一部分。现在，我们拥有一个可以从中使用的库，并且可以对其进行测试了！

现在我们需要将 _src/lib.rs_ 中定义的代码引入 _src/main.rs_ 中的二进制依赖库，并调用该代码，如清单 12-14 所示。

<Listing number="12-14" file-name="src/main.rs" caption="Using the `minigrep` library crate’s `search` function in *src/main.rs*">

```rust,ignore
// --snip--
use minigrep::search;

fn main() {
    // --snip--
}

// --snip--

fn run(config: Config) -> Result<(), Box<dyn Error>> {
    let contents = fs::read_to_string(config.file_path)?;

    for line in search(&config.query, &contents) {
        println!("{line}");
    }

    Ok(())
}

```

</Listing>

我们在`use minigrep::search`这一行代码中添加了相关代码，以便将来自库crate的`search`函数引入到二进制crate的 Scope 中。接着，在`run`函数中，我们不再直接打印文件的内容，而是调用`search`函数，并将`config.query`值和`contents`作为参数传递给该函数。之后，`run`将使用`for`循环来打印从`search`返回的、与查询匹配的所有行内容。这也是移除`main`函数中那些用于显示查询和文件路径的代码的好时机，这样我们的程序就只能打印搜索结果了（如果不存在错误的话）。

请注意，搜索功能会将所有结果收集到一个向量中，并在任何打印之前将其返回。当搜索大文件时，这种实现可能会显示结果的速度较慢，因为结果是在被发现时立即被返回的。我们将在第13章中讨论一种使用迭代器来解决这个问题的方法。

哇！这确实是一项艰巨的工作，但我们已经为未来的成功做好了准备。现在处理错误变得更加容易了，而且我们的代码也变得更加模块化了。从现在开始，我们几乎所有的工作都将在 `_src/lib.rs_`文件中完成。

让我们利用这种新发现的模块化特性，去做一些使用旧代码时很困难但在新代码下却很容易的事情：我们编写一些测试吧！

[ch13]: ch13-00-functional-features.html
[ch9-custom-types]: ch09-03-to-panic-or-not-to-panic.html#creating-custom-types-for-validation
[ch9-error-guidelines]: ch09-03-to-panic-or-not-to-panic.html#guidelines-for-error-handling
[ch9-result]: ch09-02-recoverable-errors-with-result.html
[ch18]: ch18-00-oop.html
[ch9-question-mark]: ch09-02-recoverable-errors-with-result.html#a-shortcut-for-propagating-errors-the--operator
