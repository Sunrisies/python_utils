# 编程实现一个猜谜游戏

让我们通过一起完成一个实践项目来开始学习Rust吧！这一章将通过展示如何在实际程序中使用一些常见的Rust概念，来让你了解这些概念。你将学习到`let`、`match`、方法、相关函数、外部库等等！在接下来的章节中，我们将更详细地探讨这些概念。在这一章中，你只需要练习基础知识。

我们将实现一个经典的编程入门问题：猜数游戏。其运作方式如下：程序会生成一个1到100之间的随机整数。然后，程序会提示玩家输入一个猜测数字。当玩家输入一个猜测数字后，程序会提示这个猜测数字是太低还是太高。如果猜测数字正确，游戏会打印一条祝贺消息并结束游戏。

## 创建新项目

要创建一个新的项目，请进入在第一章中创建的`_projects_`目录，然后使用Cargo创建一个新的项目，具体步骤如下：

```console
$ cargo new guessing_game
$ cd guessing_game
```

第一个命令 `cargo new`，将项目的名称（`guessing_game`）作为第一个参数。第二个命令则会将当前目录切换到新项目的目录。

请查看生成的_Cargo.toml_文件：

<!-- manual-regeneration
cd listings/ch02-guessing-game-tutorial
rm -rf no-listing-01-cargo-new
cargo new no-listing-01-cargo-new --name guessing_game
cd no-listing-01-cargo-new
cargo run > output.txt 2>&1
cd ../../..
-->

<span class="filename">文件名: Cargo.toml</span>

```toml
[package]
name = "guessing_game"
version = "0.1.0"
edition = "2024"

[dependencies]

```

如第1章所述，`cargo new`会为你生成一个“Hello, world!”程序。请查看`_src/main.rs_`文件。

<span class="filename"> 文件名: src/main.rs</span>

```rust
fn main() {
    println!("Hello, world!");
}

```

现在让我们编译这个“Hello, world!”程序，并使用 `cargo run` 命令来运行它。

```console
$ cargo run
   Compiling guessing_game v0.1.0 (file:///projects/guessing_game)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.08s
     Running `target/debug/guessing_game`
Hello, world!

```

当您需要快速迭代一个项目时，`run`命令就非常实用了。就像我们在游戏中所做的那样，可以在进行下一次迭代之前，快速测试每一次迭代的结果。

重新打开 _src/main.rs_ 文件。你需要在这个文件中编写所有的代码。

## 处理猜测结果

猜谜游戏程序的第一部分将要求用户输入，处理该输入，并验证输入是否符合预期格式。首先，我们将允许玩家输入一个猜测值。请将代码写入 Listing 2-1 文件中，文件位置为 src/main.rs_。

<Listing number="2-1" file-name="src/main.rs" caption="Code that gets a guess from the user and prints it">

```rust,ignore
// ANCHOR: io
use std::io;
// ANCHOR_END: io

// ANCHOR: main
fn main() {
    // ANCHOR_END: main
    // ANCHOR: print
    println!("Guess the number!");

    println!("Please input your guess.");
    // ANCHOR_END: print

    // ANCHOR: string
    let mut guess = String::new();
    // ANCHOR_END: string

    // ANCHOR: read
    io::stdin()
        .read_line(&mut guess)
        // ANCHOR_END: read
        // ANCHOR: expect
        .expect("Failed to read line");
    // ANCHOR_END: expect

    // ANCHOR: print_guess
    println!("You guessed: {guess}");
    // ANCHOR_END: print_guess
}

```

</Listing>

这段代码包含了大量的信息，因此让我们逐行仔细分析。为了获取用户输入并将结果输出，我们需要引入`io`输入/输出库。而`io`库则来自标准库，其名称为`std`。

```rust,ignore
use std::io;

```

默认情况下，Rust标准库中定义了一组元素，这些元素被应用到每个程序中。这组元素被称为“prelude”，你可以在标准库文档中查看相关内容[详见标准库文档][prelude]。

如果你想要使用的类型不在预定义中，那么你必须通过 `use` 语句来显式地将其引入作用域。使用 `std::io` 库可以为你提供许多有用的功能，包括接受用户输入的能力。

如第1章所述，`main`函数是程序的入口点：

```rust,ignore
fn main() {

```

`fn` 这种语法用于声明一个新的函数；括号 `()` 表示该函数没有参数；而大括号 `{` 则标志着函数的主体部分。

正如你在第一章中学习的那样，`println!`是一个宏，它会将字符串打印到屏幕上：

```rust,ignore
    println!("Guess the number!");

    println!("Please input your guess.");
    println!("You guessed: {guess}");

```

这段代码会打印出一个提示框，告诉用户这是哪个游戏，并请求用户输入。

### 使用变量存储值

接下来，我们将创建一个变量来存储用户输入，如下所示：

```rust,ignore
    let mut guess = String::new();

```

现在这个程序变得有趣了！在这小段代码中发生了很多事情。我们使用 `let` 语句来创建变量。这里还有一个例子：

```rust,ignore
let apples = 5;
```

这行代码创建了一个名为 `apples` 的新变量，并将其绑定到 `5` 的值。在Rust中，变量默认是不可变的，这意味着一旦我们为变量赋予一个值，该值就不会再改变。我们将在第三章的[“变量与可变性”][variables-and-mutability]<!-- ignore -->章节中详细讨论这个概念。要使变量变为可变，我们需要在变量名前加上 `mut`：

```rust,ignore
let apples = 5; // immutable
let mut bananas = 5; // mutable
```

注意：`//`这种语法用于开始一个注释，该注释会一直持续到行尾。Rust会忽略注释中的任何内容。我们将在[第3章][comments]<!-- ignore -->中更详细地讨论注释。

回到“猜测游戏”程序，现在你知道 `let mut guess` 会引入一个名为 `guess` 的可变变量。等号 (`=`) 告诉 Rust 我们现在想要为这个变量绑定某个值。等号右边的值是 `guess` 所绑定的内容，这个值是调用 `String::new` 函数后的结果。`String::new` 是一个函数，它返回一个新实例的 `String`。[`String`][string]<!-- ignore --> 是由标准库提供的字符串类型，它是一种可增长的、采用 UTF-8 编码的文本片段。

在 `::new` 行中，`::` 语法表示 `new` 是 `String` 类型的关联函数。所谓“关联函数”，指的是在某种类型上实现的函数，在本例中为 `String`。这个 `new` 函数会创建一个新的空字符串。你可以在许多类型中找到 `new` 函数，因为它是一种用于创建某种新值的函数的常见名称。

完整来说，`let mut guess = String::new();`这一行代码创建了一个可变变量，该变量当前绑定到一个新的、空的`String`实例上。真棒！

### 接收用户输入

请记住，我们在程序的第一行使用了标准库中的输入/输出功能，代码为 `use std::io;`。现在，我们将调用 `io` 模块中的 `stdin` 函数，这个函数可以帮助我们处理用户输入。

```rust,ignore
    io::stdin()
        .read_line(&mut guess)

```

如果我们没有在程序开头导入 `io` 模块，并且没有使用 `use std::io;`，那么我们仍然可以通过编写这样的函数调用来使用该函数：`std::io::stdin`。`stdin` 函数返回一个 [`std::io::Stdin`][iostdin]<!-- ignore --> 类型的实例，这个类型代表了一个对终端标准输入的句柄。

接下来，行``.read_line(&mut guess)``调用了标准输入句柄上的[`read_line`][read_line]<!--
ignore -->方法，以从用户那里获取输入。我们还将`&mut guess`作为参数传递给`read_line`，以指定存储用户输入的字符串。`read_line`的整个功能是将用户在标准输入中输入的内容追加到一个字符串中（而不会覆盖原有内容），因此我们将该字符串作为参数传递。这个字符串参数必须是可变的，这样该方法才能修改字符串的内容。

`&`表示这个参数是一个_引用_，它允许你的代码中的多个部分访问同一份数据，而无需多次将数据复制到内存中。引用是一个复杂的特性，而Rust的一个主要优势就是使用引用非常安全且简单。完成这个程序时，你不需要了解太多关于引用的细节。目前，你只需要知道，就像变量一样，引用默认是不可变的。因此，你需要使用`&mut guess`而不是`&guess`来使其变为可变的。（第4章会详细解释引用。）

<!-- Old headings. Do not remove or links may break. -->

<a id="handling-potential-failure-with-the-result-type"></a>

### 处理潜在的故障情况，使用 `Result`

我们仍在处理这一行代码。我们现在正在讨论第三行文本，但请注意，它仍然属于同一逻辑行代码的一部分。接下来的部分是这个方法：

```rust,ignore
        .expect("Failed to read line");

```

我们可以将这段代码写成如下形式：

```rust,ignore
io::stdin().read_line(&mut guess).expect("Failed to read line");
```

不过，一长行文字很难阅读，因此最好将其分成多行。在调用带有 `.method_name()` 语法的方法时，通常建议引入一个新行以及其他空白字符，以帮助分割长行。现在我们来讨论这一行代码的作用。

如前所述，`read_line`会将用户输入的内容放入我们传递给它的字符串中，但它还会返回一个`Result`值。[`Result`][result]<!--
ignore -->是一种[_enumeration_][enums]<!-- ignore -->类型，通常被称为_enum_，它是一种可以处于多种可能状态的类型。我们将每种可能状态称为一个_variant_。

[第6章][枚举类型]<!-- ignore --> 将更详细地介绍枚举类型。这些 `Result` 类型的目的是用来编码错误处理信息。

`Result`的变体分别是 `Ok` 和 `Err`。`Ok` 变体表示操作成功，并且包含了成功生成的值。而 `Err` 变体则表示操作失败，并且包含了关于操作失败的原因或方式的详细信息。

`Result`类型的数值，就像任何其他类型的数值一样，都有定义在其上的方法。`Result`的一个实例拥有一个[`expect`方法][expect]<!-- ignore -->，你可以调用这个方法来操作该实例。如果`Result`的这个实例是一个`Err`值，那么`expect`会导致程序崩溃，并显示你作为参数传递给`expect`的消息。如果`read_line`方法返回一个`Err`值，那很可能是由于底层操作系统出现了错误。如果`Result`的这个实例是一个`Ok`值，那么`expect`会获取`Ok`所持有的返回值，并将其返回给你，以便你可以使用它。在这种情况下，该值就是用户输入内容的字节数。

如果你不调用 `expect`，程序可以编译出来，但你会收到一个警告：

```console
$ cargo build
   Compiling guessing_game v0.1.0 (file:///projects/guessing_game)
warning: unused `Result` that must be used
  --> src/main.rs:10:5
   |
10 |     io::stdin().read_line(&mut guess);
   |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   |
   = note: this `Result` may be an `Err` variant, which should be handled
   = note: `#[warn(unused_must_use)]` on by default
help: use `let _ = ...` to ignore the resulting value
   |
10 |     let _ = io::stdin().read_line(&mut guess);
   |     +++++++

warning: `guessing_game` (bin "guessing_game") generated 1 warning
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.59s

```

Rust 提示您尚未使用从 `read_line` 返回的值 `Result`，这表明程序尚未处理可能的错误。

抑制警告的正确方法是实际编写错误处理代码，但在我们的案例中，我们只希望在出现问题时让程序崩溃，因此我们可以使用 `expect`。关于如何从错误中恢复，您可以在[第9章][recover]<!-- ignore -->中了解。

### 使用 `println!` 占位符打印值

除了最后一个闭合的花括号之外，到目前为止代码中还有一行需要讨论：

```rust,ignore
    println!("You guessed: {guess}");

```

这一行会打印出当前包含用户输入的字符串。`{}`这个花括号集合只是一个占位符：可以把`{}`想象成用来固定某个值的“小蟹钳”。在打印变量的值时，可以将变量名放在花括号内。而在打印表达式的结果时，需要在格式字符串中放入空花括号，然后在同一空花括号占位符中，按照相同的顺序列出要打印的表达式，并用逗号分隔。在一个调用`println!`的过程中，同时打印一个变量和一个表达式的结果的样子如下：

```rust
let x = 5;
let y = 10;

println!("x = {x} and y + 2 = {}", y + 2);
```

这段代码会输出 `x = 5 and y + 2 = 12`。

### 测试第一部分

让我们来测试这个猜谜游戏的第一部分。使用 `cargo run` 来运行它。

<!-- manual-regeneration
cd listings/ch02-guessing-game-tutorial/listing-02-01/
cargo clean
cargo run
input 6 -->

```console
$ cargo run
   Compiling guessing_game v0.1.0 (file:///projects/guessing_game)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 6.44s
     Running `target/debug/guessing_game`
Guess the number!
Please input your guess.
6
You guessed: 6
```

目前，游戏的第一部分已经完成：我们正在从键盘接收输入，然后将其打印出来。

## 生成秘密数字

接下来，我们需要生成一个用户需要尝试猜测的秘密数字。这个秘密数字每次都应该不同，这样游戏就可以多次玩，增加游戏的趣味性。我们将使用1到100之间的随机数字，这样游戏就不会太难。Rust的标准库目前还没有包含随机数生成功能。不过，Rust团队提供了一个名为[randcrate]的包，其中包含了这个功能。

<!-- Old headings. Do not remove or links may break. -->
<a id="using-a-crate-to-get-more-functionality"></a>

### 通过使用Crate提升功能

请记住，一个crate是由Rust源代码文件组成的集合。我们一直在构建的项目是一个二进制crate，即一个可执行文件。而 `rand` crate 则是一个库crate，它包含的代码旨在用于其他程序中，不能单独执行。

Cargo在协调外部crates方面表现得非常出色。在编写使用 `rand` 的代码之前，我们需要修改 _Cargo.toml_ 文件，将 `rand` crate 作为依赖项添加到文件中。现在打开该文件，在 `[dependencies]` 部分标题下方添加以下行。请确保严格按照这里的格式指定 `rand`，并附带版本号，否则本教程中的代码示例可能无法正常运行。

<!-- When updating the version of `rand` used, also update the version of
`rand` used in these files so they all match:
* ch07-04-bringing-paths-into-scope-with-the-use-keyword.md
* ch14-03-cargo-workspaces.md
-->

<span class="filename">文件名: Cargo.toml</span>

```toml

```

在_Cargo.toml_文件中，所有紧跟在标题之后的内容都属于同一部分，这部分会一直持续直到另一个部分开始。在 `[dependencies]` 中，你告诉Cargo你的项目依赖哪些外部crates，以及你需要这些crates的哪个版本。在这个例子中，我们使用语义版本规范 `0.8.5` 来指定 `rand` crate。Cargo理解[语义版本控制][semver]<!-- ignore -->，这是一种编写版本号的标准。符号 `0.8.5` 实际上是 `^0.8.5` 的缩写，指的是任何至少达到0.8.5但低于0.9.0的版本。

Cargo认为这些版本的公共API与0.8.5版本兼容，此规范确保您能够获取最新的补丁版本，同时该版本仍然可以与本章中的代码进行编译。任何0.9.0或更高版本的API并不保证与以下示例使用的API相同。

现在，在不更改任何代码的情况下，让我们按照清单2-2所示的步骤来构建这个项目。

<!-- manual-regeneration
cd listings/ch02-guessing-game-tutorial/listing-02-02/
rm Cargo.lock
cargo clean
cargo build -->

<Listing number="2-2" caption="The output from running `cargo build` after adding the `rand` crate as a dependency">

```console
$ cargo build
  Updating crates.io index
   Locking 15 packages to latest Rust 1.85.0 compatible versions
    Adding rand v0.8.5 (available: v0.9.0)
 Compiling proc-macro2 v1.0.93
 Compiling unicode-ident v1.0.17
 Compiling libc v0.2.170
 Compiling cfg-if v1.0.0
 Compiling byteorder v1.5.0
 Compiling getrandom v0.2.15
 Compiling rand_core v0.6.4
 Compiling quote v1.0.38
 Compiling syn v2.0.98
 Compiling zerocopy-derive v0.7.35
 Compiling zerocopy v0.7.35
 Compiling ppv-lite86 v0.2.20
 Compiling rand_chacha v0.3.1
 Compiling rand v0.8.5
 Compiling guessing_game v0.1.0 (file:///projects/guessing_game)
  Finished `dev` profile [unoptimized + debuginfo] target(s) in 2.48s
```

</Listing>

您可能会看到不同的版本号（但由于 SemVer 的缘故，这些版本号都可与代码兼容！），以及不同的行号（这取决于操作系统），而且这些行号的顺序也可能不同。

当我们引入一个外部依赖项时，Cargo会从_注册中心_获取该依赖项所需的所有最新版本。这个注册中心实际上是从[Crates.io]获取的数据副本。Crates.io是Rust生态系统中的平台，人们可以在这里发布他们的开源Rust项目，供其他人使用。

在更新注册表之后，Cargo会检查 `[dependencies]` 这一部分，并下载所有列出的、尚未下载的软件包。在这种情况下，尽管我们只列出了 `rand` 作为依赖项，但Cargo还会下载 `rand` 所依赖的其他软件包，以便项目能够正常运行。下载完这些软件包后，Rust会对其进行编译，然后项目也会在可用的依赖项下完成编译。

如果你不做出任何修改就立即再次运行 `cargo build`，那么除了 `Finished` 这一行之外，你将不会得到任何输出。Cargo 知道它已经下载并编译了所有依赖项，而且你在 _Cargo.toml_ 文件中也没有对它们进行任何修改。Cargo 还知道你的代码也没有任何变化，因此也不会重新编译代码。由于无事可做，它 simply 会退出。

如果你打开 _src/main.rs_ 文件，进行一个简单的修改，然后保存并重新构建，你只会看到两行输出：

<!-- manual-regeneration
cd listings/ch02-guessing-game-tutorial/listing-02-02/
touch src/main.rs
cargo build -->

```console
$ cargo build
   Compiling guessing_game v0.1.0 (file:///projects/guessing_game)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.13s
```

这些行表明，Cargo只会根据你对`src/main.rs`文件的微小修改来更新构建文件。你的依赖项没有发生变化，因此Cargo知道它可以重用已经下载并编译过的代码。

<!-- Old headings. Do not remove or links may break. -->
<a id="ensuring-reproducible-builds-with-the-cargo-lock-file"></a>

#### 确保可复现的构建过程

Cargo提供了一种机制，确保每次你或其他人编译代码时，都能构建相同的产物。Cargo只会使用你指定的依赖项的版本，直到你明确指示 otherwise。例如，假设下周 `rand` 这个 crate 的 0.8.6 版本发布，该版本包含重要的错误修复，但同时也包含可能会破坏你代码的回归问题。为了处理这种情况，Rust 会在你第一次运行 `cargo build` 时生成 _Cargo.lock_ 文件。因此，我们现在在 _guessing_game_ 目录下有了这个文件。

当你首次构建项目时，Cargo会找出所有符合要求的依赖库的版本，并将这些版本写入_Cargo.lock_文件。之后，当你再次构建项目时，Cargo会检查_Cargo.lock_文件是否存在，并直接使用其中指定的版本，而无需再次进行版本查找。这样，你就可以实现可复现的构建过程。换句话说，由于_Cargo.lock_文件的存在，你的项目将始终保持为0.8.5版本，直到你明确进行升级为止。因为_Cargo.lock_文件对于实现可复现的构建过程非常重要，所以它通常会与项目中的其他代码一起被提交到版本控制系统中。

#### 更新 crate 以获取新版本

当你确实想要更新某个 crate 时，Cargo 提供了 `update` 命令。该命令会忽略 _Cargo.lock_ 文件，并自动在 _Cargo.toml_ 中找到符合你要求的最新版本。之后，Cargo 会将这些版本写入 _Cargo.lock_ 文件。否则，默认情况下，Cargo 只会寻找大于 0.8.5 且小于 0.9.0 的版本。如果 `rand` crate 发布了两个新版本 0.8.6 和 0.999.0，那么当你运行 `cargo update` 命令时，你会看到以下结果：

<!-- manual-regeneration
cd listings/ch02-guessing-game-tutorial/listing-02-02/
cargo update
assuming there is a new 0.8.x version of rand; otherwise use another update
as a guide to creating the hypothetical output shown here -->

```console
$ cargo update
    Updating crates.io index
     Locking 1 package to latest Rust 1.85.0 compatible version
    Updating rand v0.8.5 -> v0.8.6 (available: v0.999.0)
```

Cargo忽略了0.999.0版本的发布。此时，你还会注意到_Cargo.lock_文件中的信息有所变化，现在使用的 `rand` 包的版本变成了0.8.6。如果你想使用 `rand` 的0.999.0版本，或者0.999._x_系列中的任何版本，那么你需要更新_Cargo.toml_文件，使其看起来像这样（但实际上不要进行这种修改，因为下面的示例假设你使用的是 `rand` 的0.8版本）。

```toml
[dependencies]
rand = "0.999.0"
```

下次当你运行 `cargo build` 时，Cargo 将会更新可用 crate 的注册表，并根据你指定的新版本重新评估你的 `rand` 需求。

关于[Cargo][doccargo]<!-- ignore -->以及[其生态系统][doccratesio]<!-- ignore -->，还有很多内容需要讨论，我们将在第十四章中详细探讨。不过目前，这些就是你需要了解的全部内容。Cargo使得库的重复使用变得非常容易，因此Rust开发者能够编写出由多个包组合而成的较小项目。

### 生成随机数

让我们开始使用 `rand` 来生成一个需要猜测的数字。下一步是更新 _src/main.rs_ 文件，如清单 2-3 所示。

<Listing number="2-3" file-name="src/main.rs" caption="Adding code to generate a random number">

```rust,ignore
use std::io;

// ANCHOR: ch07-04
use rand::Rng;

fn main() {
    // ANCHOR_END: ch07-04
    println!("Guess the number!");

    // ANCHOR: ch07-04
    let secret_number = rand::thread_rng().gen_range(1..=100);
    // ANCHOR_END: ch07-04

    println!("The secret number is: {secret_number}");

    println!("Please input your guess.");

    let mut guess = String::new();

    io::stdin()
        .read_line(&mut guess)
        .expect("Failed to read line");

    println!("You guessed: {guess}");
    // ANCHOR: ch07-04
}
// ANCHOR_END: ch07-04

```

</Listing>

首先，我们添加一行代码 `use rand::Rng;`。 `Rng` 这个特质定义了随机数生成器实现的方法，而我们需要在这个特质的作用域内才能使用这些方法。第10章会详细介绍特质的相关内容。

接下来，我们在中间添加两行代码。在第一行中，我们调用了`rand::thread_rng`函数，这个函数能够生成我们即将使用的特定随机数生成器。该生成器是本地化的，仅适用于当前执行线程，并且其种子值由操作系统提供。然后，我们调用了`gen_range`方法，该方法是由`Rng`特质定义的，而`Rng`特质是通过`use rand::Rng;`语句引入作用域中的。`gen_range`方法接受一个范围表达式作为参数，并在该范围内生成随机数。这里使用的范围表达式形式为`start..=end`，它包含下限和上限，因此我们需要指定`1..=100`来请求一个介于1到100之间的数字。

注意：你不会只知道应该使用哪些特性，以及从某个包中调用哪些方法或函数。因此，每个包都有关于如何使用该包的文档说明。Cargo的另一个优点在于，运行 `cargo doc
> --open` 命令可以本地生成所有依赖项提供的文档，并可以在浏览器中打开。如果你对 `rand` 包的其他功能感兴趣，可以运行 `cargo doc --open`，然后在左侧的侧边栏中点击 `rand`。

第二行新内容会打印出秘密数字。在开发程序时，这样做有助于测试程序，但在最终版本中我们会将其删除。如果程序在启动时就直接打印出答案，那就不算什么有趣的游戏了！

请尝试多次运行该程序：

<!-- manual-regeneration
cd listings/ch02-guessing-game-tutorial/listing-02-03/
cargo run
4
cargo run
5
-->

```console
$ cargo run
   Compiling guessing_game v0.1.0 (file:///projects/guessing_game)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.02s
     Running `target/debug/guessing_game`
Guess the number!
The secret number is: 7
Please input your guess.
4
You guessed: 4

$ cargo run
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.02s
     Running `target/debug/guessing_game`
Guess the number!
The secret number is: 83
Please input your guess.
5
You guessed: 5
```

你应该会得到不同的随机数字，而且这些数字都应该在1到100之间。干得真棒！

## 将猜测的数字与秘密数字进行比较

现在我们已经获得了用户的输入和一个随机数字，我们可以将它们进行比较。这一步骤在 Listing 2-4 中有所展示。请注意，目前这段代码还无法编译，我们会在后面解释原因。

<Listing number="2-4" file-name="src/main.rs" caption="Handling the possible return values of comparing two numbers">

```rust,ignore,does_not_compile
use std::cmp::Ordering;
use std::io;

use rand::Rng;

fn main() {
    // --snip--

    println!("You guessed: {guess}");

    match guess.cmp(&secret_number) {
        Ordering::Less => println!("Too small!"),
        Ordering::Greater => println!("Too big!"),
        Ordering::Equal => println!("You win!"),
    }
}

```

</Listing>

首先，我们添加了另一个 `use` 语句，从而将一种名为 `std::cmp::Ordering` 的类型引入到标准库中。 `Ordering` 类型是一种枚举类型，并且包含 `Less`、 `Greater` 和 `Equal` 这三种变体。这些就是比较两个值时可能出现的三种结果。

然后，我们在底部添加五行新的代码，这些代码使用了 `Ordering` 类型。`cmp` 方法用于比较两个值，并且可以应用于任何可以进行比较的对象。该方法需要一个引用，用来指定要比较的对象。在这里，它是在比较 `guess` 和 `secret_number`。之后，它返回一个由 `Ordering` 枚举定义的变量，该变量是通过 `use` 语句创建的。我们使用 [`match`][match]<!-- ignore --> 表达式来决定根据 `Ordering` 的哪个版本从 `cmp` 的调用中返回，以及 `guess` 和 `secret_number` 中的值，来决定接下来应该执行什么操作。

表达式 A `match` 由多个_分支_组成。每个分支包含一个_模式_，用于匹配给定值；如果给定值符合该分支的模式，则会执行相应的代码。Rust会依次检查 `match` 所给定的值，并匹配每个分支的模式。模式以及 `match` 构造是 Rust 中非常强大的功能：它们允许你表达代码可能遇到的各种情况，并确保你能正确处理这些情况。这些功能将在第6章和第19章中详细讨论。

让我们通过一个例子来演示这里使用的 `match` 表达式。假设用户猜中了 50，而这次随机生成的秘密数字是 38。

当代码比较 50 和 38 时，`cmp` 方法将返回`Ordering::Greater`，因为 50 大于 38。`match` 表达式会获取`Ordering::Greater`的值，并继续检查每个分支的模式。它首先查看第一个分支的模式`Ordering::Less`，发现该值与`Ordering::Greater`不匹配，因此忽略该分支中的代码，继续检查下一个分支。下一个分支的模式是`Ordering::Greater`，这个模式确实与`Ordering::Greater`匹配！因此，该分支中的相关代码将会执行，并将`Too big!`打印到屏幕上。由于`match`表达式在第一次成功匹配后就会结束，所以在这种情况下，它不会继续检查最后一个分支。

不过，Listing 2-4中的代码目前还无法编译。让我们试着运行一下吧：

<!--
The error numbers in this output should be that of the code **WITHOUT** the
anchor or snip comments
-->

```console
$ cargo build
   Compiling libc v0.2.86
   Compiling getrandom v0.2.2
   Compiling cfg-if v1.0.0
   Compiling ppv-lite86 v0.2.10
   Compiling rand_core v0.6.2
   Compiling rand_chacha v0.3.0
   Compiling rand v0.8.5
   Compiling guessing_game v0.1.0 (file:///projects/guessing_game)
error[E0308]: mismatched types
  --> src/main.rs:23:21
   |
23 |     match guess.cmp(&secret_number) {
   |                 --- ^^^^^^^^^^^^^^ expected `&String`, found `&{integer}`
   |                 |
   |                 arguments to this method are incorrect
   |
   = note: expected reference `&String`
              found reference `&{integer}`
note: method defined here
  --> /rustc/1159e78c4747b02ef996e55082b704c09b970588/library/core/src/cmp.rs:979:8

For more information about this error, try `rustc --explain E0308`.
error: could not compile `guessing_game` (bin "guessing_game") due to 1 previous error

```

错误提示指出存在_类型不匹配_的问题。Rust拥有强大且静态的类型系统，但同时也支持类型推断。当我们编写`let mut guess = String::new()`时，Rust能够推断出`guess`应该是一个`String`，因此我们不需要手动指定类型。而`secret_number`则属于数字类型。Rust中的一些数字类型可以表示1到100之间的数值：`i32`表示32位数字；`u32`表示无符号32位数字；`i64`表示64位数字。除非另有说明，Rust默认使用`i32`作为类型，除非你在其他地方添加了类型信息，导致Rust推断出不同的数字类型。出现错误的原因在于Rust无法将字符串和数字类型进行比较。

最终，我们希望将 `String` 程序中作为输入的数值类型化，以便我们可以对其进行数值上的比较，以验证它是否与秘密数字相等。我们通过在 `main` 函数的主体中添加以下代码来实现这一点：

<span class="filename"> 文件名: src/main.rs</span>

```rust,ignore
    // --snip--

    let mut guess = String::new();

    io::stdin()
        .read_line(&mut guess)
        .expect("Failed to read line");

    let guess: u32 = guess.trim().parse().expect("Please type a number!");

    println!("You guessed: {guess}");

    match guess.cmp(&secret_number) {
        Ordering::Less => println!("Too small!"),
        Ordering::Greater => println!("Too big!"),
        Ordering::Equal => println!("You win!"),
    }

```

这一行是：

```rust,ignore
let guess: u32 = guess.trim().parse().expect("Please type a number!");
```

我们创建了一个名为 `guess` 的变量。但是，程序里不已经有名为 `guess` 的变量了吗？确实如此，不过Rust允许我们重用 `guess` 的变量名，从而不影响 `guess` 的值。这种“影子化”功能让我们能够重复使用 `guess` 这个变量名，而不需要创建两个独立的变量，比如 `guess_str` 和 `guess`。我们将在[第3章][shadowing]<!-- ignore -->中详细讨论这一点，但现在只需知道，当需要将一个值从一种类型转换为另一种类型时，通常会使用这个功能。

我们将这个新变量绑定到表达式 `guess.trim().parse()` 上。表达式中的 `guess` 指的是原始的 `guess` 变量，该变量包含以字符串形式存储的输入数据。 `String` 实例上的 `trim` 方法会删除字符串开头和结尾的空白字符，这是在进行字符串转换之前必须完成的步骤，因为后续转换后，字符串只能包含数值数据。用户需要按下 <kbd>enter</kbd> 来满足 `read_line` 的条件，并输入他们的猜测值，这样就会在字符串末尾添加一个换行符。例如，如果用户输入 <kbd>5</kbd>，并按下 <kbd>enter</kbd>，那么 `guess` 就会变成 `5\n`。 `\n` 表示“换行符”。在 Windows 系统中，按下 <kbd>enter</kbd> 会同时产生回车符和换行符。 `trim` 方法会删除 `\n` 或 `\r\n`，最终只保留 `5`。

[`parse`方法用于字符串][parse]<!-- ignore -->可以将字符串转换为另一种类型。在这里，我们使用它来将字符串转换为数字。我们需要通过 `let guess: u32` 告诉Rust我们想要的具体数字类型。`guess` 后面的冒号 (`:`) 告诉Rust我们将为变量标注类型。Rust有一些内置的数字类型；这里看到的 `u32` 是一个无符号的32位整数。对于较小的正数来说，这是一个很好的默认选择。您将在[第3章][integers]<!-- ignore -->中了解其他数字类型。

此外，在这个示例程序中，注释 `u32` 以及与之相关的比较 `secret_number` 意味着 Rust 会推断 `secret_number` 也应该是 `u32`。因此，现在比较的将是两个相同类型的数值！

`parse` 方法仅适用于那些可以逻辑上转换为数字的角色，因此很容易导致错误。例如，如果字符串中包含 `A👍%`，那么就无法将其转换为数字。由于可能会失败，`parse` 方法会返回一个 `Result` 类型的数值，就像 `read_line` 方法所做的那样（之前在[“处理潜在错误与 `Result`”](#handling-potential-failure-with-result)<!-- ignore -->中讨论过）。我们将再次使用 `expect` 方法来处理这种情况。如果 `parse` 因为无法从字符串中创建出数字而返回 `Err` `Result` 类型的数值，那么 `expect` 调用将会导致游戏崩溃，并打印出我们给出的消息。如果 `parse` 能够成功地将字符串转换为数字，它将返回 `Ok` `Result` 类型的数值，而 `expect` 则会从 `Ok` 值中返回我们想要的数字。

现在让我们运行这个程序吧：

<!-- manual-regeneration
cd listings/ch02-guessing-game-tutorial/no-listing-03-convert-string-to-number/
touch src/main.rs
cargo run
  76
-->

```console
$ cargo run
   Compiling guessing_game v0.1.0 (file:///projects/guessing_game)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.26s
     Running `target/debug/guessing_game`
Guess the number!
The secret number is: 58
Please input your guess.
  76
You guessed: 76
Too big!
```

很好！尽管在猜测之前添加了空格，程序仍然能够识别出用户猜测的数字是76。请多次运行该程序，以验证不同输入情况下的行为：正确猜测数字、猜测过高的数字，以及猜测过低的数字。

目前，游戏的大部分功能已经可以正常运行了，但是用户只能进行一次猜测。让我们通过添加循环来解决这个问题吧！

## 通过循环实现允许多次猜测

关键词 `loop` 会导致无限循环。我们将添加一个循环，让用户有更多的机会猜测数字：

<span class="filename"> 文件名: src/main.rs</span>

```rust,ignore
    // --snip--

    println!("The secret number is: {secret_number}");

    loop {
        println!("Please input your guess.");

        // --snip--

        match guess.cmp(&secret_number) {
            Ordering::Less => println!("Too small!"),
            Ordering::Greater => println!("Too big!"),
            Ordering::Equal => println!("You win!"),
        }
    }
}

```

如您所见，我们已经将所有内容从猜测输入提示处转移到了循环结构中。请务必将循环内的每一行缩进四个空格，然后再次运行程序。现在，程序会不断要求用户输入新的猜测值，这实际上引入了一个新的问题。看起来用户无法退出程序！

用户始终可以通过使用键盘快捷键来中断程序运行。但是，还有另一种方法可以摆脱这个“永不满足的怪物”，正如在[“比较猜测与秘密数字”](#comparing-the-guess-to-the-secret-number)中的`parse`讨论中提到的那样：如果用户输入的非数字答案，程序将会崩溃。我们可以利用这一点让用户能够退出程序，如下所示：

<!-- manual-regeneration
cd listings/ch02-guessing-game-tutorial/no-listing-04-looping/
touch src/main.rs
cargo run
(too small guess)
(too big guess)
(correct guess)
quit
-->

```console
$ cargo run
   Compiling guessing_game v0.1.0 (file:///projects/guessing_game)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.23s
     Running `target/debug/guessing_game`
Guess the number!
The secret number is: 59
Please input your guess.
45
You guessed: 45
Too small!
Please input your guess.
60
You guessed: 60
Too big!
Please input your guess.
59
You guessed: 59
You win!
Please input your guess.
quit

thread 'main' panicked at src/main.rs:28:47:
Please type a number!: ParseIntError { kind: InvalidDigit }
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace
```

输入「`quit`」将会退出游戏，但正如你会注意到的，输入任何其他非数字字符同样也会使游戏停止。这至少可以说是次优的解决方案；我们希望在正确数字被猜中时，游戏也能自动停止。

### 正确猜测后退出

让我们在程序中添加 `break` 语句，当用户获胜时让游戏退出：

<span class="filename"> 文件名: src/main.rs</span>

```rust,ignore
        // --snip--

        match guess.cmp(&secret_number) {
            Ordering::Less => println!("Too small!"),
            Ordering::Greater => println!("Too big!"),
            Ordering::Equal => {
                println!("You win!");
                break;
            }
        }
    }
}

```

在 `You win!` 之后添加 `break` 这一行，可以使得程序在用户正确猜出秘密数字时退出循环。退出循环意味着程序也会终止，因为 `main` 是程序的最后一部分。

### 处理无效输入

为了进一步优化游戏的行为，当用户输入非数字字符时，不要让程序崩溃，而是让游戏忽略这些输入，这样用户就可以继续猜测。我们可以通过修改将`guess`转换为`String`的语句来实现这一点，如清单2-5所示。

<Listing number="2-5" file-name="src/main.rs" caption="Ignoring a non-number guess and asking for another guess instead of crashing the program">

```rust,ignore
        // --snip--

        io::stdin()
            .read_line(&mut guess)
            .expect("Failed to read line");

        // ANCHOR: ch19
        let guess: u32 = match guess.trim().parse() {
            Ok(num) => num,
            Err(_) => continue,
        };
        // ANCHOR_END: ch19

        println!("You guessed: {guess}");

        // --snip--

```

</Listing>

我们将从一个 `expect` 调用切换到一个 `match` 表达式，从而从因错误而崩溃的状态转变为能够处理错误。需要注意的是， `parse` 返回一个 `Result` 类型的返回值，而 `Result` 是一个枚举，包含 `Ok` 和 `Err` 两种变体。在这里，我们使用了一个 `match` 表达式，就像我们在 `cmp` 方法的 `Ordering` 结果中所做的那样。

如果 `parse` 能够成功地将字符串转换为一个数字，它将返回一个 `Ok` 值，该值包含最终得到的数字。这个 `Ok` 值将符合第一个分支的模式，而 `match` 表达式则只会返回 `num` 产生的数值，并将其放入 `Ok` 值中。这个数字最终会出现在我们新创建的 `guess` 变量中，正好位于我们想要的位置。

如果 `parse` 无法将字符串转换为数字，它将返回一个`Err`值，该值包含更多关于错误的信息。`Err`值并不符合第一个`match`中的`Ok(num)`模式，但它确实符合第二个`match`中的`Err(_)`模式。下划线`_`是一个通用的值；在这个例子中，我们表示希望匹配所有`Err`值，无论它们内部包含什么信息。因此，程序将执行第二个`continue`中的代码，该代码指示程序进行下一次迭代，并再次尝试猜测。实际上，程序会忽略所有`parse`可能遇到的错误！

现在，程序中的所有内容都应该按照预期正常工作了。让我们试试看：

<!-- manual-regeneration
cd listings/ch02-guessing-game-tutorial/listing-02-05/
cargo run
(too small guess)
(too big guess)
foo
(correct guess)
-->

```console
$ cargo run
   Compiling guessing_game v0.1.0 (file:///projects/guessing_game)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.13s
     Running `target/debug/guessing_game`
Guess the number!
The secret number is: 61
Please input your guess.
10
You guessed: 10
Too small!
Please input your guess.
99
You guessed: 99
Too big!
Please input your guess.
foo
Please input your guess.
61
You guessed: 61
You win!
```

太棒了！只需再做一个小小的调整，我们就能完成这个“猜谜游戏”了。还记得，程序仍然在打印出秘密数字。虽然这在测试时效果不错，但会破坏游戏的乐趣。让我们删除那个输出秘密数字的 `println!` 代码吧。列表 2-6 展示了最终的代码。

<Listing number="2-6" file-name="src/main.rs" caption="Complete guessing game code">

```rust,ignore
use std::cmp::Ordering;
use std::io;

use rand::Rng;

fn main() {
    println!("Guess the number!");

    let secret_number = rand::thread_rng().gen_range(1..=100);

    loop {
        println!("Please input your guess.");

        let mut guess = String::new();

        io::stdin()
            .read_line(&mut guess)
            .expect("Failed to read line");

        let guess: u32 = match guess.trim().parse() {
            Ok(num) => num,
            Err(_) => continue,
        };

        println!("You guessed: {guess}");

        match guess.cmp(&secret_number) {
            Ordering::Less => println!("Too small!"),
            Ordering::Greater => println!("Too big!"),
            Ordering::Equal => {
                println!("You win!");
                break;
            }
        }
    }
}

```

</Listing>

此时，你已经成功构建了一个猜谜游戏。恭喜！

## 摘要

这个项目通过实践的方式向您介绍了许多新的 Rust 概念：`let`、`match`、函数、外部库的使用等等。在接下来的几章中，您将更详细地了解这些概念。第3章介绍了大多数编程语言都有的概念，如变量、数据类型和函数，并展示了如何在 Rust 中使用它们。第4章探讨了所有权这一特性，它使得 Rust 与其他语言有所不同。第5章讨论了结构体和方法语法，而第6章则解释了枚举的工作原理。

[prelude]: ../std/prelude/index.html
[variables-and-mutability]: ch03-01-variables-and-mutability.html#variables-and-mutability
[comments]: ch03-04-comments.html
[string]: ../std/string/struct.String.html
[iostdin]: ../std/io/struct.Stdin.html
[read_line]: ../std/io/struct.Stdin.html#method.read_line
[result]: ../std/result/enum.Result.html
[enums]: ch06-00-enums.html
[expect]: ../std/result/enum.Result.html#method.expect
[recover]: ch09-02-recoverable-errors-with-result.html
[randcrate]: https://crates.io/crates/rand
[semver]: http://semver.org
[cratesio]: https://crates.io/
[doccargo]: https://doc.rust-lang.org/cargo/
[doccratesio]: https://doc.rust-lang.org/cargo/reference/publishing.html
[match]: ch06-02-match.html
[shadowing]: ch03-01-variables-and-mutability.html#shadowing
[parse]: ../std/primitive.str.html#method.parse
[integers]: ch03-02-data-types.html#integer-types
