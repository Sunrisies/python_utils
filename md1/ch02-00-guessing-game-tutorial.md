# 编程实现一个猜谜游戏

让我们通过一起完成一个实践项目来开始学习Rust吧！这一章将通过实际程序演示，向您介绍一些常见的Rust概念。您将学习到`let`、`match`、方法、关联函数、外部库等等！在接下来的章节中，我们将更详细地探讨这些概念。在这一章中，您只需练习基础知识即可。

我们将实现一个经典的编程入门问题：猜数游戏。其运作方式如下：程序会生成一个1到100之间的随机整数。然后，程序会提示玩家输入一个猜测数字。当玩家输入一个猜测数字后，程序会指出这个猜测是太低还是太高。如果猜测正确，游戏会打印一条祝贺消息并结束游戏。

## 创建新项目

要创建一个新的项目，请进入在第一章中创建的`_projects_`目录，然后使用Cargo创建一个新的项目，具体步骤如下：

```console
$ cargo new guessing_game
$ cd guessing_game
```

第一个命令 ``cargo new``，将项目的名称（``guessing_game``）作为第一个参数。第二个命令则切换到新项目的目录。

请查看生成的`_Cargo.toml_`文件：

<!-- 手动重新生成项目目录
cd listings/ch02-guessing-game-tutorial
删除 no-listing-01-cargo-new 目录及其内容
cargo new no-listing-01-cargo-new --name guessing_game
cd no-listing-01-cargo-new
运行项目 cargo run，并将输出结果保存到 output.txt 文件中
cd../../..
-->

<span class="filename">文件名：Cargo.toml</span>

```toml
{{#include ../listings/ch02-guessing-game-tutorial/no-listing-01-cargo-new/Cargo.toml}}
```

如第1章所述，`cargo new`为你生成了一个“Hello, world!”程序。请查看`_src/main.rs_`文件：

<span class="filename">文件名：src/main.rs</span>

```rust
{{#rustdoc_include ../listings/ch02-guessing-game-tutorial/no-listing-01-cargo-new/src/main.rs}}
```

现在让我们编译这个“Hello, world!”程序，并使用`cargo run`命令来运行它。

```console
{{#include ../listings/ch02-guessing-game-tutorial/no-listing-01-cargo-new/output.txt}}
```

在需要快速迭代项目时，``run``命令非常实用，就像我们在游戏中所做的那样，可以在进行下一次迭代之前，快速测试每次迭代的结果。

重新打开 `_src/main.rs_`文件。你需要在这个文件中编写所有的代码。

## 处理猜测结果

猜谜游戏程序的第一部分将要求用户输入，处理该输入，并检查输入是否符合预期格式。首先，我们将允许玩家输入一个猜测值。请将代码写入清单2-1中，并将其放在src/main.rs_文件中。

<列表编号="2-1" 文件名称="src/main.rs" 标题="从用户那里获取猜测并打印出来的代码">

```rust,ignore
{{#rustdoc_include ../listings/ch02-guessing-game-tutorial/listing-02-01/src/main.rs:all}}
```

</ Listing>

这段代码包含了大量的信息，因此让我们逐行进行解析。为了获取用户输入并将结果打印出来，我们需要将`io`这个输入/输出库引入作用域中。`io`这个库来自标准库，其来源为`std`。

```rust,ignore
{{#rustdoc_include ../listings/ch02-guessing-game-tutorial/listing-02-01/src/main.rs:io}}
```

默认情况下，Rust标准库中定义了一组元素，这些元素被应用到每个程序的范围内。这组元素被称为“预处理器”，你可以在标准库文档中查看相关内容[详见标准库文档][预处理器]。

如果你想要使用的类型不在预定义中，就必须使用 ``use`` 语句来显式地将其引入作用域。使用 ``std::io`` 库可以让你获得许多有用的功能，包括接受用户输入的能力。

如第1章所述，`main`函数是程序的入口点：

```rust,ignore
{{#rustdoc_include ../listings/ch02-guessing-game-tutorial/listing-02-01/src/main.rs:main}}
```

`fn`语法用于声明一个新的函数；括号`()`表示该函数没有参数；而大括号`{`则标志着函数的主体部分。

正如你在第一章中学习的那样，`println!`是一个宏，它可以将字符串打印到屏幕上：

```rust,ignore
{{#rustdoc_include ../listings/ch02-guessing-game-tutorial/listing-02-01/src/main.rs:print}}
```

这段代码会打印出一个提示框，告诉用户这是哪个游戏，并请求用户输入。

### 使用变量存储值

接下来，我们将创建一个变量来存储用户输入，如下所示：

```rust,ignore
{{#rustdoc_include ../listings/ch02-guessing-game-tutorial/listing-02-01/src/main.rs:string}}
```

现在这个程序变得有趣了！在这行代码中发生了很多事情。我们使用 ``let`` 语句来创建变量。这里还有一个例子：

```rust,ignore
let apples = 5;
```

这行代码创建了一个名为 `apples`的新变量，并将其绑定到 `5`的值上。在Rust中，默认情况下变量是不可变的，这意味着一旦我们给变量赋予了一个值，这个值就不会再改变。我们将在第三章的[“变量与可变性”][variables-and-mutability]<!-- ignore -->部分详细讨论这个概念。要使一个变量变为可变，我们需要在变量名称之前加上 `mut`：

```rust,ignore
let apples = 5; // immutable
let mut bananas = 5; // mutable
```

注意：`//`语法用于开始一个注释，该注释会一直持续到行尾。Rust会忽略注释中的所有内容。我们将在[第3章][comments]中更详细地讨论注释的相关内容。

回到“猜测游戏”程序，现在你知道`let mut guess`将会引入一个名为`guess`的可变变量。等号(`=`)告诉Rust我们现在想要将某个值绑定到这个变量上。等号的右边是`guess`所绑定的值，这个值是通过调用`String::new`得到的，而`String::new`是一个返回`String`新实例的函数。[`String`][string]<!-- 忽略 -->是由标准库提供的一种字符串类型，它是一种可增长的、UTF-8编码的文本片段。

在`::new`行中的`::`语法表明`new`是`String`类型的关联函数。关联函数是一种在类型上实现的函数，在本例中为`String`。这个`new`函数创建一个新的空字符串。在许多类型中都可以找到`new`函数，因为它是一个用于创建某种新值的函数的常见名称。

完整来说，`let mut guess = String::new();`这一行创建了一个可变变量，该变量当前绑定到一个新的、空的`String`实例。哇！

### 接收用户输入

请记住，我们在程序的第一行使用了标准库中的输入/输出功能，这部分代码被标记为`use std::io;`。现在，我们将从`io`模块中调用`stdin`函数，这个函数可以帮助我们处理用户输入。

```rust,ignore
{{#rustdoc_include ../listings/ch02-guessing-game-tutorial/listing-02-01/src/main.rs:read}}
```

如果我们没有在程序的开头导入 `io` 模块以及 `use std::io;`，我们仍然可以通过编写如下函数调用来使用 `std::io::stdin` 函数。`stdin` 函数返回一个 [`std::io::Stdin`][iostdin]<!-- ignore --> 类型的实例，这个类型代表了一个用于访问终端标准输入的句柄。

接下来，行 ``.read_line(&mut guess)`` 调用了标准输入句柄上的 `[`read_line`][read_line]<!--ignore-->` 方法，以从用户那里获取输入。我们还将 ``&mut guess`` 作为参数传递给 ``read_line``，以便告诉它要将用户输入存储到哪个字符串中。__`INLINE_CODE_86__` 的主要任务是将用户在标准输入中输入的内容追加到一个字符串中（而不会覆盖原有的内容），因此我们将该字符串作为参数传递。这个字符串参数必须是可变的，这样该方法才能修改字符串的内容。

`&`表示这个参数是一种引用，它允许你的代码中的多个部分能够访问同一份数据，而无需多次将这份数据复制到内存中。引用是一个复杂的特性，而Rust的一个主要优势就是使用引用非常安全且简单。完成这个程序时，你不需要了解太多关于引用的细节。目前，你需要知道的是，就像变量一样，引用默认是不可变的。因此，你需要使用`&mut guess`而不是`&guess`来使其变为可变的。（第4章会详细解释引用。）

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="如何处理潜在的失败情况与结果类型"></a>

### 处理潜在的错误与`Result`

我们仍在处理这一行代码。我们现在正在讨论第三行文本，但请注意，它仍然属于同一逻辑行代码的一部分。接下来的部分是这个方法：

```rust,ignore
{{#rustdoc_include ../listings/ch02-guessing-game-tutorial/listing-02-01/src/main.rs:expect}}
```

我们可以将这段代码写成如下形式：

```rust,ignore
io::stdin().read_line(&mut guess).expect("Failed to read line");
```

不过，一长行代码很难阅读，因此最好将其分成多行。在调用带有 ``.method_name()`` 语法的方法时，通常建议引入一个新行以及其他空白字符，以帮助分割长行。现在我们来讨论这一行代码的作用。

如前所述，`read_line`会将用户输入的内容放入我们传递给它的字符串中，但它还会返回一个`Result`值。[`Result`][result]<!--
忽略 -->是一个[_enumeration_][enums]<!-- 忽略 -->，通常被称为_enum_，它是一种可以处于多种可能状态的类型。我们将每种可能的状态称为_variant_。

[第6章][枚举]<!-- 忽略 -->将更详细地介绍枚举类型。这些`Result`类型的目的是用来编码错误处理信息。

`Result`的变体是`Ok`和`Err`。`Ok`变体表示操作成功，并且包含了成功生成的值。而`Err`变体则表示操作失败，并且包含了关于操作失败的原因或方式的详细信息。

`Result`类型的数值，就像任何其他类型的数值一样，都拥有定义在其上的方法。`Result`的一个实例拥有一个[`expect`方法][期望]<!-- 忽略 -->，你可以调用这个方法来执行相应的操作。如果这个`Result`的实例是一个`Err`类型的数值，那么`expect`会导致程序崩溃，并显示你作为参数传递给`expect`的消息。如果`read_line`方法返回一个`Err`类型的数值，那很可能是由于底层操作系统出现了错误所导致的。如果`Result`的这个实例是一个`Ok`类型的数值，那么`expect`将会获取`Ok`所持有的返回值，并将其返回给你，以便你可以使用它。在这种情况下，该数值就是用户输入内容的字节数。

如果你不调用 ``expect``，程序将会编译成功，但你会收到一个警告：

```console
{{#include ../listings/ch02-guessing-game-tutorial/no-listing-02-without-expect/output.txt}}
```

Rust提示您尚未使用从`read_line`返回的`Result`值，这表明程序尚未处理可能的错误。

抑制警告的正确方法是实际编写错误处理代码，但在我们的案例中，我们只希望在出现问题时让程序崩溃，因此我们可以使用 ``expect``。关于如何从错误中恢复，您可以在[第9章][recover]<!-- ignore -->中学习。

### 使用 `println!` 占位符打印值

除了最后一个闭合大括号之外，到目前为止代码中还有一行需要讨论：

```rust,ignore
{{#rustdoc_include ../listings/ch02-guessing-game-tutorial/listing-02-01/src/main.rs:print_guess}}
```

这一行会打印出当前包含用户输入的字符串。`{}`中的那些花括号是一个占位符：可以将`{}`想象成用来固定某个值的“小蟹钳”。在打印变量的值时，可以将变量名放在花括号内。而在打印表达式的结果时，需要在格式字符串中放入空的花括号，然后在同一顺序下，用逗号分隔列出要打印的每个表达式。在一次调用`println!`的过程中，同时打印一个变量的值和一个表达式的结果，看起来就像这样：

```rust
let x = 5;
let y = 10;

println!("x = {x} and y + 2 = {}", y + 2);
```

这段代码会打印出`x = 5 and y + 2 = 12`。

### 测试第一部分

让我们来测试这个猜谜游戏的第一部分。使用 `cargo run` 来运行它：

<!-- 手动重新生成
cd listings/ch02-guessing-game-tutorial/listing-02-01/
cargo clean
cargo run
输入 6 -->

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

接下来，我们需要生成一个用户需要尝试猜测的秘密数字。这个秘密数字每次都应该不同，这样游戏就可以多次玩，而且很有趣。我们将使用1到100之间的随机数字，这样游戏就不会太难了。Rust的标准库目前还没有包含随机数生成功能。不过，Rust团队提供了一个名为[`rand`crate][randcrate]的库，其中包含了这个功能。

<!-- 旧的标题。不要删除，否则链接可能会失效。 -->
<a id="使用 crate 获得更多功能"></a>

### 通过使用Crate提升功能

请记住，一个“crate”是一组Rust源代码文件的集合。我们一直在构建的项目是一个二进制crate，即一个可执行文件。而`rand`这个crate则是一个库crate，它包含的是那些旨在供其他程序使用的代码，不能单独执行。

Cargo在协调外部依赖库方面表现得非常出色。在我们能够编写使用`rand`的代码之前，我们需要修改_Cargo.toml_文件，将`rand`依赖项添加到文件中。现在打开该文件，在由Cargo为你创建的`[dependencies]`部分标题下方，添加以下行。请确保严格按照这里的格式指定`rand`及其版本号，否则本教程中的代码示例可能无法正常运行。

<!-- 在更新用于 `rand` 的版本时，也需要更新这些文件中用于 `rand` 的版本，以确保两者一致：
* ch07-04-bringing-paths-into-scope-with-the-use-keyword.md
* ch14-03-cargo-workspaces.md
-->

<span class="filename">文件名：Cargo.toml</span>

```toml
{{#include ../listings/ch02-guessing-game-tutorial/listing-02-02/Cargo.toml:8:}}
```

在_Cargo.toml_文件中，所有紧跟在标题之后的内容都属于同一部分，这部分会一直持续直到另一个部分开始。在`[dependencies]`中，你可以告诉Cargo你的项目依赖哪些外部库，以及你需要这些库的哪个版本。在这个例子中，我们使用语义版本规范`0.8.5`来指定`rand`这个库。Cargo支持[Semantic Versioning][semver]（有时称为_SemVer_），这是一种编写版本号的标准规范。符号`0.8.5`实际上是`^0.8.5`的缩写，这意味着任何至少达到0.8.5但低于0.9.0的版本都符合要求。

Cargo认为这些版本具有与0.8.5版本兼容的公共API。此规范确保您将获得最新的补丁版本，该版本仍然可以与本章中的代码一起编译。任何0.9.0或更高版本的API并不保证与以下示例使用的API相同。

现在，在不更改任何代码的情况下，让我们按照清单2-2所示的步骤来构建这个项目。

<!-- 手动重新生成项目文件
cd listings/ch02-guessing-game-tutorial/listing-02-02/
删除 Cargo.lock 文件
cargo clean
cargo build -->

<列表编号="2-2" 标题="在将 `rand` 作为依赖项后运行 `cargo build` 的输出">

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

</ Listing>

您可能会看到不同的版本号（但由于SemVer的原因，所有这些版本号都与代码兼容！），以及不同的行号（这取决于操作系统）。而且，这些行号的顺序也可能不同。

当我们引入一个外部依赖时，Cargo会从`_registry_`中下载该依赖所需的所有最新版本。这个_registry_实际上是从[Crates.io]获取的数据副本。Crates.io是Rust生态系统中的平台，人们可以在这里发布他们的开源Rust项目，供其他人使用。

在更新注册表之后，Cargo会检查`[dependencies]`这一部分，并下载那些未被下载过的依赖库。在这种情况下，虽然我们只列出了`rand`作为一个依赖项，但Cargo还会下载其他由`rand`所依赖的库，以确保项目的正常运行。在下载完这些依赖库之后，Rust会对其进行编译，然后项目就能在可用的依赖库环境下进行编译了。

如果你再次运行 `cargo build`，而不做任何更改，那么除了 `Finished` 这一行之外，你将不会得到任何输出。Cargo 知道它已经下载并编译了所有依赖项，而且你在 _Cargo.toml_ 文件中也没有对它们进行任何修改。Cargo 还知道你对代码本身也没有进行任何修改，因此也不会重新编译代码。由于无事可做，它只是简单地退出而已。

如果你打开 `_src/main.rs_`文件，进行一个简单的修改，然后保存并重新构建，你只会看到两行输出：

<!-- 手动重新生成目录
cd listings/ch02-guessing-game-tutorial/listing-02-02/
touch src/main.rs
cargo build -->

```console
$ cargo build
   Compiling guessing_game v0.1.0 (file:///projects/guessing_game)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.13s
```

这几行代码表明，Cargo只会根据你对`src/main.rs`文件的微小修改来更新构建文件。你的依赖项没有发生变化，因此Cargo知道它可以重用已经下载并编译好的内容。

<a id="确保使用Cargo锁定文件实现可重复构建"></a>

#### 确保可复现的构建过程

Cargo提供了一种机制，确保每次您或其他人编译代码时，都能构建相同的产物。Cargo只会使用您指定的依赖项的版本，直到您明确指示 otherwise。例如，假设下周 `rand` 这个包的版本为 0.8.6，该版本包含重要的错误修复，但同时也存在可能导致代码崩溃的回归问题。为了应对这种情况，Rust会在您第一次运行 `cargo build` 时生成 _Cargo.lock_ 文件。因此，我们现在在 _guessing_game_ 目录下有了这个文件。

当你第一次构建项目时，Cargo会找出所有符合要求的依赖库的版本，并将它们写入_Cargo.lock_文件。之后，当你再次构建项目时，Cargo会检查_Cargo.lock_文件是否存在，并直接使用其中指定的版本，而无需重新进行版本查找。这样就能实现可重复的构建过程。换句话说，由于_Cargo.lock_文件的存在，你的项目将始终保持为0.8.5版本，直到你明确进行升级为止。因为_Cargo.lock_文件对于实现可重复构建非常重要，所以它通常会与项目中的其他代码一起被提交到源代码控制中。

#### 更新 crate 以获取新版本

当你确实想要更新某个 crate 时，Cargo 提供了 `update` 这个命令。该命令会忽略 _Cargo.lock_ 文件，然后从 _Cargo.toml_ 文件中找出符合你要求的所有最新版本。之后，Cargo 会将这些版本写入 _Cargo.lock_ 文件。否则，默认情况下，Cargo 只会寻找大于 0.8.5 且小于 0.9.0 的版本。如果 `rand` 这个 crate 发布了两个新版本 0.8.6 和 0.999.0，那么如果你运行 `cargo update` 命令，你会看到如下结果：

<!-- 手动重新生成
cd listings/ch02-guessing-game-tutorial/listing-02-02/
cargo update
假设存在新的0.8.x版本的rand；否则使用其他更新工具
作为创建此处所示假设输出的指南 -->

```console
$ cargo update
    Updating crates.io index
     Locking 1 package to latest Rust 1.85.0 compatible version
    Updating rand v0.8.5 -> v0.8.6 (available: v0.999.0)
```

Cargo忽略了0.999.0版本的发布。此时，您还会注意到`_Cargo.lock_`文件中的变化，显示当前使用的`rand`包的版本已变为0.8.6。若想使用`rand`的0.999.0版本或0.999._x_系列中的任何版本，则需要更新`_Cargo.toml`文件，使其看起来像这样（但实际上不必进行此更改，因为以下示例假设您使用的是`rand`的0.8版本）。

```toml
[dependencies]
rand = "0.999.0"
```

下次当你运行`cargo build`时，Cargo将会更新可用套件的注册表，并根据你指定的新版本重新评估你的`rand`需求。

关于[Cargo][doccargo]<!-- 忽略 -->及其生态系统[dkratesio]<!-- 忽略 -->，还有很多内容需要讨论，我们将在第十四章中详细探讨。不过目前，你们只需要了解这些就够了。Cargo使得库的重复使用变得非常容易，因此Rust开发者能够编写出由多个包组合而成的更小规模的项目。

### 生成随机数

让我们开始使用 ``rand`` 来生成一个需要猜测的数字。下一步是更新 `_src/main.rs` 文件，如清单 2-3 所示。

<listing number="2-3" file-name="src/main.rs" caption="添加代码以生成随机数">

```rust,ignore
{{#rustdoc_include ../listings/ch02-guessing-game-tutorial/listing-02-03/src/main.rs:all}}
```

</ Listing>

首先，我们添加了 ``use rand::Rng;`` 这一行。``Rng`` 这个特质定义了随机数生成器所实现的方法，而要使用这些方法，我们必须处于该特质的范围内。第10章会详细介绍特质的相关内容。

接下来，我们在中间添加两行代码。在第一行中，我们调用了`rand::thread_rng`函数，该函数提供了我们将要使用的特定随机数生成器：这个生成器是局限于当前执行线程内的，并且由操作系统来初始化种子值。然后，我们调用了`gen_range`方法。这个方法是由`Rng`特质定义的，我们通过`use rand::Rng;`语句将其引入作用域。`gen_range`方法接受一个范围表达式作为参数，并在该范围内生成一个随机数。这里我们使用的是`start..=end`形式的范围表达式，它包含下限和上限，因此我们需要使用`1..=100`来指定一个介于1到100之间的数字。

注意：您不会仅仅知道应该使用哪些特性，以及从某个包中调用哪些方法或函数。因此，每个包都有关于如何使用该包的文档说明。Cargo的另一个优点在于，运行`cargo doc --open`命令可以本地生成所有依赖项的文档，并可以在浏览器中打开这些文档。如果您对`rand`包的其他功能感兴趣，例如，可以运行`cargo doc --open`，然后点击左侧侧边栏中的`rand`。

第二行新内容会打印出秘密数字。在开发程序时，这样做有助于测试程序，但在最终版本中我们会将其删除。如果程序一启动就直接显示答案的话，那就不算真正的游戏了！

请尝试多次运行该程序：

<!-- 手动重新生成
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

你应该会得到不同的随机数字，而且这些数字都应该介于1到100之间。干得真棒！

## 将猜测的数字与秘密数字进行比较

现在我们已经获得了用户输入和一个随机数字，我们可以将它们进行比较。这一步骤在清单2-4中有所展示。请注意，目前这段代码还无法编译，我们会在后面解释原因。

<列表编号="2-4" 文件名称="src/main.rs" 标题="处理比较两个数字时可能出现的返回值">

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch02-guessing-game-tutorial/listing-02-04/src/main.rs:here}}
```

</ Listing>

首先，我们添加另一个 ``use`` 语句，将一种名为 ``std::cmp::Ordering`` 的类型引入到标准库的作用域中。``Ordering`` 也是一种枚举类型，包含三个变体：``Less``、``Greater`` 和 ``Equal``。这些就是比较两个值时可能出现的三种结果。

然后，我们在底部添加了五行新的代码，这些代码使用了 ``Ordering`` 类型。``cmp`` 方法用于比较两个值，并且可以在任何可以进行比较的对象上调用。该方法接受一个引用，指向你想要比较的对象：在这里，它是在比较 ``guess`` 和 ``secret_number``。之后，该方法会返回一个与 ``Ordering`` 枚举相关的结果，这个枚举是通过 ``use`` 语句引入作用域中的。我们使用 `[`match`][match]<!-- ignore -->` 表达式来决定接下来应该执行什么操作，这取决于在调用 ``cmp`` 时返回了哪个 ``Ordering`` 的变体，以及 ``guess`` 和 ``secret_number`` 中提供的数值。

一个 `match` 表达式由多个_分支_组成。每个分支包含一个用于匹配的_模式_，以及当 `match` 传递的值符合该分支的模式时，需要执行的代码。Rust会依次检查传给 `match` 的值，并与每个分支的模式进行匹配。模式与 `match` 结构都是Rust的强大特性：它们允许你表达代码中可能遇到的各种情况，并确保你能正确处理这些情况。这些特性将在第6章和第19章中详细讨论。

让我们通过一个例子来演示这里使用的 ``match`` 表达式。假设用户猜对了50，而这次随机生成的秘密数字是38。

当代码比较50与38时，`cmp`方法将返回`Ordering::Greater`，因为50大于38。`match`表达式获取`Ordering::Greater`的值，并开始检查每个分支的模式。它首先查看第一个分支的模式，即`Ordering::Less`，发现值`Ordering::Greater`与`Ordering::Less`不匹配，因此忽略该分支中的代码，继续检查下一个分支。下一个分支的模式是`Ordering::Greater`，这个模式确实与`Ordering::Greater`匹配！与该模式相关的代码将会被执行，并将`Too big!`打印到屏幕上。`match`表达式在第一次成功匹配之后就会结束，因此在这种情况下，它不会继续检查最后一个分支。

然而，Listing 2-4中的代码目前无法编译。让我们尝试一下：

<!--
此输出中的错误编号应为**没有**锚点或截剪评论的代码的错误编号
-->

```console
{{#include ../listings/ch02-guessing-game-tutorial/listing-02-04/output.txt}}
```

错误提示显示存在“类型不匹配”的问题。Rust拥有强大且静态的类型系统，但同时也支持类型推断功能。当我们编写`let mut guess = String::new()`时，Rust能够自动推断出`guess`应该是一个`String`类型，因此我们不需要手动指定类型。而`secret_number`则属于数字类型。Rust中的一些数字类型可以表示1到100之间的数值：`i32`是一个32位数的数字；`u32`是一个无符号的32位数；`i64`则是一个64位数的数字。除非另有说明，否则Rust默认使用`i32`作为`secret_number`的类型，除非你在其他地方添加了类型信息，导致Rust推断出不同的数字类型。出现这个错误的原因是Rust无法将字符串和数字类型进行比较。

最终，我们希望将程序读取的`String`作为输入转换为数字类型，以便我们可以对其进行数值比较，以验证它是否与秘密数字相符。我们通过在`main`函数的主体中添加以下代码来实现这一点：

<span class="filename">文件名：src/main.rs</span>

```rust,ignore
{{#rustdoc_include ../listings/ch02-guessing-game-tutorial/no-listing-03-convert-string-to-number/src/main.rs:here}}
```

这一行是：

```rust,ignore
let guess: u32 = guess.trim().parse().expect("Please type a number!");
```

我们创建了一个名为 ``guess`` 的变量。但是，程序难道不是已经有一个名为 ``guess`` 的变量了吗？确实如此，不过Rust很贴心地允许我们使用一个新的变量来遮蔽 ``guess`` 的先前值。通过“遮蔽”功能，我们可以重复使用 ``guess`` 这个变量名，而不需要创建两个唯一的变量，比如 ``guess_str`` 和 ``guess``。我们将在[第3章][shadowing]中详细讨论这一点，但现在只需知道，这个功能通常在需要将一个类型的值转换为另一个类型时会被使用。

我们将这个新变量绑定到表达式 `guess.trim().parse()` 上。表达式中的 `guess` 指的是原始的 `guess` 变量，该变量包含了以字符串形式表示的输入数据。对 `String` 实例调用 `trim` 方法会删除其开头和结尾的空白字符，这是在进行字符串转换之前必须完成的步骤，因为之后字符串只能包含数值数据。用户需要按下 <kbd>enter</kbd> 键来提交他们的猜测值，这会在字符串末尾添加一个新行字符。例如，如果用户输入了 <kbd>5</kbd> 并按下了 <kbd>enter</kbd> 键，那么 `guess` 就会变成 `5\n`。`\n` 代表“新行”字符（在 Windows 系统中，按下 <kbd>enter</kbd> 键会同时产生回车符和新行字符，即 `\r\n`）。`trim` 方法会删除 `\n` 或 `\r\n` 中的空白字符，最终得到只有 `5` 的版本。

[`parse`方法对字符串进行解析][parse]<!-- 忽略 -->，可以将字符串转换为另一种类型。在这里，我们使用它来将字符串转换为数字。我们需要通过`let guess: u32`来告诉Rust我们想要的具体数字类型。在`guess`之后加上冒号(`:`)是为了让Rust知道我们将对变量的类型进行注解。Rust有一些内置的数字类型；这里使用的`u32`是一个无符号的32位整数。对于较小的正数来说，这是一个很好的默认选择。您将在[第3章][integers]<!-- 忽略 -->中了解其他数字类型。

此外，在这个示例程序中，``u32``这个注解以及它与``secret_number``的比较意味着Rust会推断``secret_number``也应该是``u32``类型。因此，现在比较的将是两个相同类型的数值！

`parse`方法仅适用于那些可以逻辑上转换为数字的角色，因此很容易导致错误。例如，如果字符串中包含`A👍%`，那么就无法将其转换为数字。由于可能会失败，`parse`方法会返回`Result`类型，就像`read_line`方法所做的那样（之前在[“处理`Result`可能导致的错误”](#handling-potential-failure-with-result)中讨论过）。我们将再次使用`expect`方法来处理这个`Result`。如果`parse`因为无法将字符串转换为数字而返回`Err` `Result`变体，那么`expect`调用将会使游戏崩溃，并打印我们给出的消息。如果`parse`能够成功地将字符串转换为数字，它将返回`Ok`的`Result`变体，而`expect`则将返回我们从`Ok`值中得到的所需数字。

现在让我们运行这个程序吧：

<!-- 手动重新生成
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

很好！尽管在猜测之前添加了空格，程序仍然能够识别出用户猜的是76。请多次运行该程序，以验证不同输入情况下的行为：正确猜测数字、猜测过高的数字，以及猜测过低的数字。

目前游戏的大部分功能已经可以正常运行了，但是用户只能进行一次猜测。让我们通过添加一个循环来解决这个问题吧！

## 通过循环实现允许多次猜测

``loop``这个关键字会导致无限循环。我们将添加一个循环，让用户有更多的机会来猜测数字：

<span class="filename">文件名：src/main.rs</span>

```rust,ignore
{{#rustdoc_include ../listings/ch02-guessing-game-tutorial/no-listing-04-looping/src/main.rs:here}}
```

如您所见，我们已经将所有代码从猜测输入提示处开始，转移到了一个循环结构中。请注意，循环内的每一行都需要再缩进四个空格，然后重新运行程序。现在，程序会不断要求用户输入新的猜测值，这实际上引入了一个新的问题。看起来用户无法退出该程序！

用户始终可以通过使用键盘快捷键来中断程序运行，即<kbd>ctrl</kbd>-<kbd>C</kbd>。不过，还有另一种方法可以摆脱这个“贪食怪”——正如在[“比较猜测数字与真实数字”](#comparing-the-guess-to-the-secret-number)中的`parse`讨论中提到的那样：如果用户输入了非数字答案，程序就会崩溃。我们可以利用这一点让用户能够退出程序。

<!-- 手动重新生成
cd listings/ch02-guessing-game-tutorial/no-listing-04-looping/
touch src/main.rs
cargo run
(太小了 猜测)
(太大了 猜测)
(正确的猜测)
退出
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

输入 `quit` 将会退出游戏，但正如您会注意到的，输入任何其他非数字内容同样会导致游戏退出。这至少可以说是一种次优的做法；我们希望在正确数字被猜中时，游戏也能停止。

### 正确猜测后退出

让我们在代码中加入一个 ``break`` 语句，当用户获胜时让游戏自动退出。

<span class="filename">文件名：src/main.rs</span>

```rust,ignore
{{#rustdoc_include ../listings/ch02-guessing-game-tutorial/no-listing-05-quitting/src/main.rs:here}}
```

在 `You win!` 之后添加 `break` 这一行代码，可以使程序在用户正确猜出秘密数字时退出循环。退出循环意味着程序也会终止运行，因为循环是 `main` 的最后一部分。

### 处理无效输入

为了进一步优化游戏的行为，当用户输入非数字字符时，不要让程序崩溃，而是让游戏忽略这些非数字字符，这样用户就可以继续猜测。我们可以通过修改将`guess`从`String`转换为`u32`的那一行代码来实现这一点，如清单2-5所示。

<Listing number="2-5" file-name="src/main.rs" caption="忽略非数字猜测，要求再次尝试，而不是导致程序崩溃">

```rust,ignore
{{#rustdoc_include ../listings/ch02-guessing-game-tutorial/listing-02-05/src/main.rs:here}}
```

</ Listing>

我们从一个 ``expect`` 调用切换到一个 ``match`` 表达式，从而从因错误而崩溃的状态转变为能够处理错误。需要注意的是，``parse`` 返回一个 ``Result`` 类型，而 ``Result`` 是一个枚举，包含 ``Ok`` 和 ``Err`` 两种变体。在这里，我们使用了一个 ``match`` 表达式，就像我们在 ``cmp`` 方法的 ``Ordering`` 结果中所做的那样。

如果 `parse` 能够成功地将字符串转换为数字，它将返回一个 `Ok` 值，该值包含转换后的数字。这个 `Ok` 值会与第一个分支的模式相匹配，而 `match` 表达式则只会返回由 `parse` 生成的 `num` 值，并将其放入 `Ok` 值中。最终，这个数字将被放置在我们要在新建的 `guess` 变量中的正确位置。

如果 `parse` 无法将字符串转换为数字，它将返回一个包含有关错误更多信息的 `Err` 值。`Err` 值与第一个 `match` 中的 `Ok(num)` 模式不匹配，但它与第二个 `Err(_)` 模式匹配。下划线 `_` 是一个通用的值；在这个例子中，我们表示希望匹配所有 `Err` 值，无论它们内部包含什么信息。因此，程序将执行第二个 `Err(_)` 中的代码 `continue`，该代码指示程序进入 `loop` 的下一个迭代，并再次尝试进行猜测。实际上，程序会忽略 `parse` 可能遇到的所有错误！

现在程序中的所有内容都应该按照预期正常工作了。让我们试试看：

<!-- 手动重新生成
cd listings/ch02-guessing-game-tutorial/listing-02-05/
cargo run
(太小猜测)
(太大猜测)
foo
(正确猜测)
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

太棒了！只需再做一些微小的调整，我们就能完成这个“猜谜游戏”了。还记得，程序仍然在打印秘密数字吧？这种方式适合测试，但会破坏游戏的乐趣。让我们删除那个用于输出秘密数字的 ``println!`` 代码。清单 2-6 展示了最终的代码。

<listing number="2-6" file-name="src/main.rs" caption="完整的猜谜游戏代码">

```rust,ignore
{{#rustdoc_include ../listings/ch02-guessing-game-tutorial/listing-02-06/src/main.rs}}
```

</ Listing>

此时，你已经成功构建了一个猜谜游戏。恭喜！

## 总结

这个项目通过实践的方式向您介绍了许多新的Rust概念：`let`、`match`、函数、外部库的使用等等。在接下来的几章中，您将更详细地了解这些概念。第3章介绍了大多数编程语言都有的概念，如变量、数据类型和函数，并展示了如何在Rust中使用它们。第4章探讨了所有权这一特性，它使得Rust与其他语言有所不同。第5章讨论了结构体和方法语法，而第6章则解释了枚举的工作原理。

[prelude]:../std/prelude/index.html  
[variables-and-mutability]: ch03-01-variables-and-mutability.html#variables-and-mutability  
[comments]: ch03-04-comments.html  
[string]:../std/string/struct.String.html  
[iostdin]:../std/io/struct.Stdin.html  
[read_line]:../std/io/struct.Stdin.html#method.read_line  
[result]:../std/result/enum.Result.html  
[enums]: ch06-00-enums.html  
[expect]:../std/result/enum.Result.html#method.expect  
[recover]: ch09-02-recoverable-errors-with-result.html  
[randcrate]: https://crates.io/crates/rand  
[semver]: http://semver.org  
[cratesio]: https://crates.io/  
[doccargo]: https://doc.rust-lang.org/cargo/  
[doccratesio]: https://doc.rust-lang.org/cargo/reference/publishing.html  
[match]: ch06-02-match.html  
[shadowing]: ch03-01-variables-and-mutability.html#shadowing  
[parse]:../std/primitive.str.html#method.parse  
[integers]: ch03-02-data-types.html#integer-types