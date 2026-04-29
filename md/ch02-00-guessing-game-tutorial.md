# 编程实现一个猜谜游戏

让我们通过一起完成一个实践项目来开始学习Rust吧！这一章将通过展示如何在实际程序中使用一些常见的Rust概念，来引导您了解Rust的基础知识。您将学习到`let`、`match`、方法、关联函数、外部库等等。在接下来的章节中，我们将更详细地探讨这些概念。在这一章里，您只需练习基础内容即可。

我们将实现一个经典的编程入门问题：猜数游戏。其运作方式如下：程序会生成一个1到100之间的随机整数。然后，程序会提示玩家输入一个猜测的数字。当玩家输入了一个猜测数字后，程序会指出这个猜测是太低还是太高。如果猜测正确，游戏会打印一条祝贺的消息并结束游戏。

## 创建新项目

要创建一个新的项目，请进入在第一章中创建的`_projects_`目录，然后使用Cargo创建一个新的项目，具体步骤如下：

```console
$ cargo new guessing_game
$ cd guessing_game
```

第一个命令 ``cargo new``，将项目的名称（``guessing_game``）作为第一个参数。第二个命令则切换到新项目的目录。

请查看生成的_Cargo.toml_文件：

<!-- 手动重新生成
cd listings/ch02-guessing-game-tutorial
rm -rf no-listing-01-cargo-new
cargo new no-listing-01-cargo-new --name guessing_game
cd no-listing-01-cargo-new
cargo run > output.txt 2>&1
cd ./../..
-->

<span class="filename">文件名：Cargo.toml</span>

```toml
{{#include ../listings/ch02-guessing-game-tutorial/no-listing-01-cargo-new/Cargo.toml}}
```

如第1章所述，`cargo new`为你生成了一个“Hello, world!”程序。请查看`_src/main.rs_`文件。

<span class="filename">文件名：src/main.rs</span>

```rust
{{#rustdoc_include ../listings/ch02-guessing-game-tutorial/no-listing-01-cargo-new/src/main.rs}}
```

现在让我们编译这个“Hello, world!”程序，并使用`cargo run`命令在同一步骤中运行它。

```console
{{#include ../listings/ch02-guessing-game-tutorial/no-listing-01-cargo-new/output.txt}}
```

当您需要快速迭代一个项目时，``run``命令就非常实用了。就像我们在这个游戏中所做的那样，我们可以快速测试每次迭代的结果，然后再进行下一次迭代。

重新打开 _src/main.rs_ 文件。你需要在这个文件中编写所有的代码。

## 处理猜测结果

猜谜游戏程序的第一部分将要求用户输入，处理该输入，并检查输入是否符合预期格式。首先，我们将允许玩家输入一个猜测值。请将代码写入清单2-1中，并将其放在src/main.rs_文件中。

<列表编号="2-1" 文件名称="src/main.rs" 标题="从用户那里获取猜测并打印出来的代码">

```rust,ignore
{{#rustdoc_include ../listings/ch02-guessing-game-tutorial/listing-02-01/src/main.rs:all}}
```

</清单>

这段代码包含了大量的信息，因此让我们逐行进行解析。为了获取用户输入并将结果打印出来，我们需要将`io`这个输入/输出库引入到代码范围内。`io`这个库来自标准库，其来源为`std`。

```rust,ignore
{{#rustdoc_include ../listings/ch02-guessing-game-tutorial/listing-02-01/src/main.rs:io}}
```

默认情况下，Rust标准库中定义了一组元素，这些元素被应用到每个程序的范围内。这组元素被称为“预处理器”，你可以在标准库文档中查看其中的所有内容。[参见标准库文档][预处理器]

如果您想要使用的类型不在预定义中，那么您必须通过使用 ``use`` 语句来明确将其引入作用域。使用 ``std::io`` 库可以为您提供许多有用的功能，包括接受用户输入的能力。

如第1章所述，`main`函数是程序的入口点：

```rust,ignore
{{#rustdoc_include ../listings/ch02-guessing-game-tutorial/listing-02-01/src/main.rs:main}}
```

`fn`语法用于声明一个新的函数；括号`()`表示该函数没有参数；而大括号`{`则标志着函数的主体部分。

正如你在第一章中学习的那样，`println!`是一个宏，它可以将字符串打印到屏幕上：

```rust,ignore
{{#rustdoc_include ../listings/ch02-guessing-game-tutorial/listing-02-01/src/main.rs:print}}
```

这段代码会打印出一个提示框，告知用户正在玩什么游戏，并请求用户输入相关信息。

### 使用变量存储值

接下来，我们将创建一个变量来保存用户输入的内容，如下所示：

```rust,ignore
{{#rustdoc_include ../listings/ch02-guessing-game-tutorial/listing-02-01/src/main.rs:string}}
```

现在这个程序变得有趣了！在这行代码中发生了很多事情。我们使用`let`语句来创建变量。这里还有一个例子：

```rust,ignore
let apples = 5;
```

这行代码创建了一个名为 `apples` 的新变量，并将其绑定到值 `5` 上。在Rust中，默认情况下变量是不可变的，这意味着一旦我们给变量赋予了一个值，这个值就不会再改变。我们将在第三章的[“变量与可变性”][variables-and-mutability]<!-- ignore -->部分详细讨论这个概念。要使一个变量变得可变，我们需要在变量名称之前加上 `mut`：

```rust,ignore
let apples = 5; // immutable
let mut bananas = 5; // mutable
```

注意：`//`语法用于开始一个注释，该注释会一直持续到行尾。Rust会忽略注释中的所有内容。我们将在[第3章][comments]中更详细地讨论注释。

回到“猜测游戏”程序，现在你知道`let mut guess`将会引入一个名为`guess`的可变变量。等号(`=`)告诉Rust我们现在想要将某个值绑定到这个变量上。等号的右边是`guess`所绑定的值，这个值是通过调用`String::new`这个函数得到的，而`String::new`函数返回的是`String`的一个新实例。[`String`][string]<!-- 忽略 --> 是由标准库提供的一种字符串类型，它是一种可增长的、采用UTF-8编码的文本片段。

在`::new`行中的`::`语法表明`new`是`String`类型的关联函数。所谓“关联函数”，指的是在某个类型上实现的函数，在本例中就是`String`。这个`new`函数创建一个新的空字符串。在许多类型中都可以找到`new`函数，因为它是一个常见的函数名称，用于创建某种类型的新值。

完整来说，`let mut guess = String::new();`这一行创建了一个可变的变量，该变量目前绑定到一个新的、空的`String`实例上。真棒！

### 接收用户输入

请记住，我们在程序的第一行使用了来自标准库的输入/输出功能，其中``use std::io;``被包含在代码中。现在，我们将调用来自``io``模块的``stdin``函数，这将使我们能够处理用户的输入。

```rust,ignore
{{#rustdoc_include ../listings/ch02-guessing-game-tutorial/listing-02-01/src/main.rs:read}}
```

如果我们没有在程序的开头导入`io`模块，并且没有使用`use std::io;`，那么我们仍然可以通过编写如下函数调用来使用该函数：`std::io::stdin`。`stdin`函数返回一个[`std::io::Stdin`][iostdin]<!-- ignore -->类型的实例，这个类型代表了一个用于访问终端标准输入的句柄。

接下来，行`.read_line(&mut guess)`调用了标准输入处理器的[`read_line`][read_line]<!--ignore-->方法，以从用户那里获取输入。我们还将`&mut guess`作为参数传递给`read_line`，以指定存储用户输入的字符串。`read_line`的整个功能是将用户在标准输入中输入的内容提取出来，并将其附加到一个字符串中（而不会覆盖原有的内容），因此我们将这个字符串作为...参数。该字符串参数必须是可变的，这样该方法才能更改字符串的内容。

`&`表示这个参数是一种“引用”，它允许你的代码中的多个部分访问同一份数据，而无需多次将这份数据复制到内存中。引用是一个复杂的特性，而Rust的一个主要优势就是使用引用非常安全且方便。完成这个程序时，你不需要了解太多相关的细节。目前，你只需要知道，就像变量一样，引用也是可以被使用的。默认情况下是不可变的。因此，要使它可变，你需要使用`&mut guess`而不是`&guess`。（第4章将更详细地解释引用。）

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="处理潜在故障与结果类型"></a>

### 处理潜在的故障与`Result`

我们仍在处理这一行代码。我们现在正在讨论第三行文本，但请注意，它仍然属于同一逻辑代码行的一部分。接下来的部分是这个方法：

```rust,ignore
{{#rustdoc_include ../listings/ch02-guessing-game-tutorial/listing-02-01/src/main.rs:expect}}
```

我们可以将这段代码写成如下形式：

```rust,ignore
io::stdin().read_line(&mut guess).expect("Failed to read line");
```

不过，一长行文字很难阅读，因此最好将其分成多行。在调用带有 ``.method_name()`` 语法的方法时，通常建议引入一个新行以及其他空白字符，以帮助分割长行。现在让我们来讨论这一行代码的作用。

如前所述，`read_line`会将用户输入的内容放入我们传递给它的字符串中，但它还会返回一个`Result`值。[`Result`][result]<!--忽略-->是一个[_enumeration_][enums]<!--忽略-->类型，通常被称为_enum_，这是一种可以处于多种可能状态的类型。我们将每种可能的状态称为_variant_。

[第6章][枚举类型]<!-- 忽略 -->将更详细地介绍枚举类型。这些`Result`类型的目的是用于编码错误处理信息。

`Result`的变体包括`Ok`和`Err`。`Ok`变体表示操作成功，并且包含了成功生成的值。而`Err`变体则表示操作失败，并且包含了关于操作失败的原因或方式的详细信息。

`Result`类型的数值，就像任何其他类型的数值一样，都有定义在其上的方法。`Result`的实例拥有一个[`expect`方法][expect]<!-- 忽略 -->，你可以调用这个方法来执行特定的操作。如果`Result`的实例是一个`Err`类型的值，那么`expect`会导致程序崩溃，并显示你作为参数传递给`expect`的消息。如果`read_line`方法返回一个`Err`类型的值，那么……这很可能是由底层操作系统出现的错误所导致的。如果`Result`这个实例是一个`Ok`的值，那么`expect`就会获取`Ok`所持有的返回值，并将其返回给你，以便你可以使用它。在这种情况下，该值就是用户输入内容的字节数。

如果你不调用`expect`，程序将会编译成功，但你会收到一个警告：

```console
{{#include ../listings/ch02-guessing-game-tutorial/no-listing-02-without-expect/output.txt}}
```

Rust警告指出，您尚未使用从`read_line`返回的`Result`值，这表明程序尚未处理可能出现的错误。

抑制警告的正确方法是实际编写错误处理代码，但在我们的案例中，我们只希望在出现问题时让程序崩溃，因此我们可以使用`expect`。关于如何从错误中恢复，您可以在[第9章][recover]<!-- ignore -->中学习。

### 使用 `println!` 占位符打印值

除了最后一个闭合的花括号之外，到目前为止代码中还有一行需要讨论：

```rust,ignore
{{#rustdoc_include ../listings/ch02-guessing-game-tutorial/listing-02-01/src/main.rs:print_guess}}
```

这一行会打印出当前包含用户输入的字符串。`{}`中的花括号是一个占位符：可以将`{}`想象成用来固定值的“小蟹钳”。当打印变量的值时，变量名可以放在花括号内。而当打印表达式的结果时，需要在格式字符串中放入空的花括号，然后再用逗号分隔的列表形式列出要打印的表达式。以相同的顺序使用圆括号占位符。在一个调用`println!`时，同时打印一个变量和一个表达式的结果，看起来会像这样：

```rust
let x = 5;
let y = 10;

println!("x = {x} and y + 2 = {}", y + 2);
```

这段代码会打印出`x = 5 and y + 2 = 12`。

### 测试第一部分

让我们来测试猜谜游戏的第一部分。使用 `cargo run` 来运行它。

<!-- 手动重新生成
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

接下来，我们需要生成一个用户需要尝试猜测的秘密数字。这个秘密数字每次都应该不同，这样游戏就可以多次玩，而且每次都很有趣。我们将使用1到100之间的随机数字，这样游戏就不会太难。Rust的标准库目前还没有包含随机数生成功能。不过，Rust团队提供了一个名为[`rand`crate][randcrate]的库，其中包含了这个功能。

<a id="使用框架板来增加功能">使用框架板来增加功能</a>

### 通过Crate提升功能性

请记住，一个“crate”是一组Rust源代码文件的总和。我们正在构建的项目是一个二进制crate，即一个可执行的程序。而`rand`这个crate则是一个库crate，它包含的是那些旨在用于其他程序的代码，不能单独执行。

Cargo在协调外部依赖库方面表现得非常出色。在我们能够编写使用`rand`的代码之前，我们需要修改_Cargo.toml_文件，将`rand`依赖项添加到文件中。现在打开该文件，在_Cargo为你创建的`[dependencies]`部分标题下方添加以下行。请确保严格按照这里的格式指定`rand`版本号，否则本教程中的代码示例可能无法正常运行。

<!-- 在更新使用`rand`的版本时，同时需要更新这些文件中使用的`rand`的版本，以确保两者一致：
* ch07-04-bringing-paths-into-scope-with-the-use-keyword.md
* ch14-03-cargo-workspaces.md
-->

<span class="filename">文件名：Cargo.toml</span>

```toml
{{#include ../listings/ch02-guessing-game-tutorial/listing-02-02/Cargo.toml:8:}}
```

在_Cargo.toml_文件中，所有紧跟在头部之后的内容都属于同一部分，这部分会一直持续下去，直到出现另一个部分为止。在`[dependencies]`中，你可以告诉Cargo你的项目依赖哪些外部库，以及你需要这些库的哪个版本。在这个例子中，我们使用`0.8.5`这样的语义版本规范来指定`rand`这个库。Cargo支持[SemanticVersioning][semver]（有时被称为_SemVer_），这是一种……这是编写版本号的标准。标识符`0.8.5`实际上是`^0.8.5`的缩写，这意味着任何版本都必须是至少0.8.5但低于0.9.0的版本。

Cargo认为这些版本的公共API与0.8.5版本兼容，并且该规范确保您将获得最新的补丁版本，同时该版本仍然可以与本章中的代码进行编译。任何0.9.0或更高版本的API并不保证与以下示例中使用的API相同。

现在，在不更改任何代码的情况下，让我们按照清单2-2所示的步骤来构建该项目。

<!-- 手动重新生成项目文件
cd listings/ch02-guessing-game-tutorial/listing-02-02/
删除 Cargo.lock 文件
执行 cargo clean 命令
执行 cargo build 命令 -->

<列表编号="2-2" 标题="在将`rand`作为依赖项后运行`cargo build`的输出">

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

</清单>

您可能会看到不同的版本号（但由于SemVer的存在，所有这些版本号都与代码兼容！），以及不同的行号（这取决于操作系统），而且这些行号的顺序也可能不同。

当我们引入一个外部依赖时，Cargo会从_注册中心_获取该依赖所需的所有最新版本。这个注册中心实际上是从[Crates.io][cratesio]中获取的数据副本。Crates.io是Rust生态系统中的平台，人们可以在这里发布他们的开源Rust项目，供其他人使用。

在更新注册表之后，Cargo会检查`[dependencies]`这一部分，并下载那些尚未下载的依赖库。在这种情况下，虽然我们只列出了`rand`作为依赖项，但Cargo还会下载其他由`rand`所依赖的库，以确保项目的正常运行。在下载完这些依赖库之后，Rust会对其进行编译，然后结合已下载的依赖库来编译整个项目。

如果你不做出任何修改就立即再次运行`cargo build`，那么除了`Finished`这一行之外，你将不会得到任何输出。Cargo知道它已经下载并编译了所有依赖项，而且你在`_Cargo.toml_`文件中也没有对它们进行任何修改。Cargo还知道你对代码本身也没有进行任何修改，因此也不会重新编译代码。由于无事可做，它只会直接退出。

如果你打开`_src/main.rs_`文件，进行一个简单的修改，然后保存并重新构建，你只会看到两行输出：

<!-- 手动重新生成
cd listings/ch02-guessing-game-tutorial/listing-02-02/
touch src/main.rs
cargo build -->

```console
$ cargo build
   Compiling guessing_game v0.1.0 (file:///projects/guessing_game)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.13s
```

这几行代码表明，Cargo只会根据你对`src/main.rs`文件的微小修改来更新构建文件。你的依赖项没有发生变化，因此Cargo知道它可以重用已经下载并编译好的内容。

<a id="确保使用Cargo Lock文件实现可重复构建"></a>

#### 确保可复现的构建过程

Cargo提供了一种机制，确保无论您还是其他人何时构建代码时，都能使用相同的依赖版本。Cargo只会使用您指定的依赖版本，直到您明确指示 otherwise。例如，假设下周 `rand` 这个包的 0.8.6 版本发布，该版本包含重要的漏洞修复，但同时也存在可能导致代码失效的回归问题。为了处理这种情况，Rust 会生成 _Cargo.lock_ 文件。运行`cargo build`的时间，现在这个文件已经存在于_guessing_game_directory_中。

当你首次构建项目时，Cargo会找出所有符合要求的依赖库的版本，并将它们写入_Cargo.lock_文件中。之后，当你再次构建项目时，Cargo会检测到_Cargo.lock_文件的存在，并会使用其中指定的版本，而无需再次去查找合适的版本。这样，你就可以实现可重复的构建过程。换句话说，你的项目将能够始终使用相同的版本进行构建。请保持在0.8.5版本，直到您明确进行升级为止，这要归功于_Cargo.lock_文件。由于_Cargo.lock_文件对于可复现的构建非常重要，因此它通常会与项目中的其他代码一起被提交到源代码控制中。

#### 更新箱子以获得新版本

当你确实想要更新某个包时，Cargo提供了`update`命令，该命令会忽略_Cargo.lock_文件，并在_Cargo.toml_中查找符合你要求的所有最新版本。然后，Cargo会将这些版本写入_Cargo.lock_文件。否则，默认情况下，Cargo只会寻找大于0.8.5且小于0.9.0的版本。如果`rand`包发布了两个新版本0.8.6和0.999.0，你会看到如下情况：您运行了`cargo update`：

<!-- 手动重新生成
cd listings/ch02-guessing-game-tutorial/listing-02-02/
cargo update
假设存在新的0.8.x版本的rand；否则请使用其他更新工具
作为生成此处所示假设输出的指南 -->

```console
$ cargo update
    Updating crates.io index
     Locking 1 package to latest Rust 1.85.0 compatible version
    Updating rand v0.8.5 -> v0.8.6 (available: v0.999.0)
```

Cargo忽略了0.999.0版本的发布。此时，您还会注意到_Cargo.lock_文件中的变化，显示当前使用的`rand`包的版本已变为0.8.6。若想使用`rand`的0.999.0版本或0.999._x_系列中的任何版本，则需要更新_Cargo.toml_文件，使其看起来像这样（但实际上不必进行此更改，因为以下示例假设您使用的是`rand` 0.8版本）。

```toml
[dependencies]
rand = "0.999.0"
```

下次当你运行`cargo build`时，Cargo将会更新可用插件的注册表，并根据你指定的新版本重新评估你的`rand`需求。

关于[Cargo][doccargo]<!-- 忽略 -->以及其[生态系统][doccratesio]<!-- 忽略 -->，还有很多内容需要讨论，我们将在第十四章中详细探讨。不过目前，这些就是你需要了解的全部内容。Cargo使得重用库变得非常容易，因此Rust开发者能够编写出由多个包组合而成的较小项目。

### 生成随机数字

让我们开始使用 ``rand`` 来生成需要猜测的数字。下一步是更新 `_src/main.rs` 文件，如清单 2-3 所示。

<列表编号="2-3" 文件名称="src/main.rs" 标题="添加用于生成随机数的代码">

```rust,ignore
{{#rustdoc_include ../listings/ch02-guessing-game-tutorial/listing-02-03/src/main.rs:all}}
```

</清单>

首先，我们添加了 ``use rand::Rng;`` 这一行。``Rng`` 这个特性定义了随机数生成器实现的方法，而要使用这些方法，就必须处于该特性的作用域内。第10章将详细介绍特性相关的内容。

接下来，我们在中间添加两行代码。在第一行中，我们调用了`rand::thread_rng`函数，该函数为我们提供了要使用的特定随机数生成器：这个生成器是局限于当前执行线程的，并且其种子是由操作系统设定的。然后，我们对随机数生成器调用了`gen_range`方法。这个方法是由`Rng`特性定义的，我们通过`use rand::Rng;`语句将其引入作用域中。`gen_range`方法接受一个范围表达式作为参数，并在该范围内生成一个随机数。我们在这里使用的范围表达式形式为`start..=end`，它包含下限和上限的值。因此，我们需要使用`1..=100`来请求一个介于1到100之间的随机数。

注意：您将不仅仅知道应该使用哪些特性，以及从某个包中调用哪些方法或函数。因此，每个包都有关于如何使用该包的文档说明。Cargo的另一个优点在于，运行`cargo doc --open`命令可以本地生成所有依赖项的文档，并可以在浏览器中打开这些文档。如果您对`rand`这个包的其他功能感兴趣，可以运行`cargo doc --open`。> 在左侧的侧边栏中点击`rand`。

第二行新内容会打印出秘密数字。在开发程序时，这样做有助于测试程序，但在最终版本中我们会将其删除。如果程序在启动时就直接打印出答案的话，那就不算真正的游戏了！

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

现在我们已经获得了用户的输入和一个随机数字，我们可以将它们进行比较。这一步骤在清单2-4中有所展示。请注意，目前这段代码可能无法编译，我们将在后面解释原因。

<列表编号="2-4" 文件名称="src/main.rs" 标题="处理比较两个数字时可能出现的返回值">

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch02-guessing-game-tutorial/listing-02-04/src/main.rs:here}}
```

</清单>

首先，我们添加了另一个``use``语句，将一种名为``std::cmp::Ordering``的类型引入到标准库的作用域中。``Ordering``是一种枚举类型，包含三种变体：``Less``、``Greater``和``Equal``。当比较两个值时，这三种变体分别表示三种可能的结果。

然后，我们在底部添加了五行新的代码，这些代码使用了`Ordering`类型。`cmp`方法可以比较两个值，并且可以在任何可以进行比较的对象上调用它。该方法需要一个引用，用来指定要比较的对象：在这里，就是比较`guess`和`secret_number`。最后，该方法返回`Ordering`枚举的一个变体，这个变体是通过`use`语句引入的。我们使用这个变体来实现我们的功能。[`match`][匹配]<!-- 忽略 --> 根据从`cmp`调用中返回的不同变体，结合`guess`和`secret_number`中的值，来决定接下来要执行的操作。

一个`match`表达式由多个“分支”组成。每个分支包含一个用于匹配的“模式”，以及当`match`传递的值符合该分支的模式时应该执行的代码。Rust会依次检查`match`所传递的值，并与每个分支的模式进行匹配。模式和`match`构造是Rust中非常强大的功能：它们使你能够表达各种情况。可能会遇到各种情况，而这些情况都会得到妥善处理。这些功能将在第6章和第19章中详细讨论。

让我们通过一个例子来演示这里使用的`match`表达式。假设用户猜对了50，而这次随机生成的秘密数字是38。

当代码比较50与38时，`cmp`方法将返回`Ordering::Greater`，因为50大于38。`match`表达式获取`Ordering::Greater`的值，并开始检查每个分支的模式。它首先查看第一个分支的模式，即`Ordering::Less`，发现值`Ordering::Greater`与`Ordering::Less`不匹配，因此忽略该分支中的代码，并继续检查下一个分支。下一个分支的模式是……`Ordering::Greater`确实与`Ordering::Greater`相匹配！该分支中的相关代码将会执行，并将`Too big!`打印到屏幕上。`match`表达式在第一次成功匹配之后就会结束，因此在这种情况下，它不会考虑最后一个分支的情况。

然而，Listing 2-4中的代码目前无法编译。让我们尝试一下：

<!--
此输出中的错误编号应为**没有**锚点或截剪评论的代码的错误编号
-->

```console
{{#include ../listings/ch02-guessing-game-tutorial/listing-02-04/output.txt}}
```

错误核心指出存在“类型不匹配”的问题。Rust具有强大且静态的类型系统，但同时也支持类型推断功能。当我们编写`let mut guess = String::new()`时，Rust能够自动推断出`guess`应该是一个`String`类型，因此我们不需要手动指定类型。而`secret_number`则属于数字类型。Rust中的一些数字类型可以表示1到100之间的数值：`i32`是一个32位数的数字；`u32`则是一个无符号的32位数。`i64`是一个64位数字，以及其他类型的数据。除非另有说明，Rust默认使用`i32`作为`secret_number`的类型，除非在其他地方添加了类型信息，导致Rust推断出不同的数值类型。出现错误的原因是Rust无法比较字符串和数值类型。

最终，我们希望将程序读取的`String`作为输入转换为数字类型，以便我们可以将其与秘密数字进行数值比较。我们通过在`main`函数的主体中添加以下代码来实现这一点：

<span class="filename">文件名：src/main.rs</span>

```rust,ignore
{{#rustdoc_include ../listings/ch02-guessing-game-tutorial/no-listing-03-convert-string-to-number/src/main.rs:here}}
```

这句话是：

```rust,ignore
let guess: u32 = guess.trim().parse().expect("Please type a number!");
```

我们创建了一个名为`guess`的变量。但是，程序难道不已经有了一个名为`guess`的变量吗？确实如此，但Rust允许我们通过创建一个新的变量来遮蔽`guess`的先前值。这种“遮蔽”功能让我们能够重复使用`guess`这个变量名，而不需要创建两个唯一的变量，比如`guess_str`和`guess`。我们将在后续内容中更详细地介绍这一点。[第3章][阴影处理]<!-- 忽略 -->，不过目前可以知道，这个功能通常在需要将一个类型的值转换为另一个类型时使用。

我们将这个新变量绑定到表达式`guess.trim().parse()`上。表达式中的`guess`指的是原始的`guess`变量，该变量以字符串形式存储了输入数据。对`String`实例的`trim`方法会删除其开头和结尾处的空白字符，这是在进行字符串转换之前必须完成的步骤，因为之后字符串只能包含数值数据。用户需要按照指示进行操作。按下<kbd>enter</kbd>键以满足`read_line`的要求，并输入他们的猜测值，这样会在字符串中新增一个换行符。例如，如果用户输入<kbd>5</kbd>，然后按下<kbd>enter</kbd>，则`guess`会显示为`5\n`。`\n`表示“换行符”。在Windows系统中，按下<kbd>enter</kbd>会同时产生回车符和换行符，即`\r\n`。`trim`方法可以消除`\n`或`\r\n`。在`5`内完成。

[`parse`方法用于字符串][parse]<!-- 忽略 -->可以将字符串转换为另一种类型。在这里，我们使用它来将字符串转换为数字。我们需要通过`let guess: u32`告诉Rust我们想要的具体数字类型。在`guess`之后的冒号(`:`)告诉Rust我们将对变量的类型进行注解。Rust提供了一些内置的数字类型；这里看到的`u32`是一个无符号的32位整数。对于较小的正数来说，这是一个很好的默认选择。您可以在[第3章][整数]中了解其他类型的数字。

此外，在这个示例程序中，``u32``这个注释以及它与``secret_number``的比较意味着Rust会推断``secret_number``也应该是``u32``类型。因此，现在比较的将是两个相同类型的数值！

`parse`方法仅适用于那些可以逻辑上转换为数字的角色，因此很容易导致错误。例如，如果字符串中包含`A👍%`，那么就无法将其转换为数字。由于可能会出现错误，`parse`方法会返回一个`Result`类型的值，这与`read_line`方法的返回值相同（之前在“处理潜在错误”部分已经讨论过）。“`Result`”](#处理潜在故障及结果)。我们将以同样的方式处理这个`Result`，再次使用`expect`方法。如果`parse`无法将字符串转换为数字，并且返回了`Err`的变体，那么`expect`的调用将会导致游戏崩溃，并打印出我们给出的消息。如果`parse`能够成功地将字符串转换为数字，它将返回……`Ok`是`Result`的变体，而`expect`则会从`Ok`值中返回我们想要的数值。

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

目前大部分游戏功能已经可以正常运行了，但是用户只能进行一次猜测。让我们通过添加一个循环来解决这个问题吧！

## 通过循环实现允许多次猜测

``loop``这个关键字会导致无限循环。我们将添加一个循环，让用户有更多的机会来猜测数字：

<span class="filename">文件名：src/main.rs</span>

```rust,ignore
{{#rustdoc_include ../listings/ch02-guessing-game-tutorial/no-listing-04-looping/src/main.rs:here}}
```

如您所见，我们已经将所有内容从猜测输入提示处开始，转移到了一个循环中。请注意，循环内的每一行都要再缩进四个空格，然后再次运行程序。现在，程序会不断要求用户输入新的猜测值，这实际上引入了一个新的问题。看起来用户无法退出该程序！

用户始终可以通过使用键盘快捷键`<kbd>ctrl</kbd>-<kbd>C</kbd>`来中断程序运行。不过，还有另一种方法可以摆脱这个“贪食者”，正如在[“比较猜测数字与真实数字”](#comparing-the-guess-to-the-secret-number)中的`parse`讨论中提到的那样：如果用户输入了非数字答案，程序就会崩溃。我们可以利用这一点让用户能够退出程序。

<!-- 手动重新生成
cd listings/ch02-guessing-game-tutorial/no-listing-04-looping/
touch src/main.rs
cargo run
(猜测太小)
(猜测太大)
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

输入 `quit` 将会退出游戏，但正如您会注意到的，输入任何其他非数字内容同样会导致游戏退出。这至少可以说是不理想的；我们希望在猜中正确的数字时，游戏也能停止。

### 正确猜测后退出

让我们在代码中加入一个 ``break`` 语句，这样当用户获胜时，游戏就会自动退出。

<span class="filename">文件名：src/main.rs</span>

```rust,ignore
{{#rustdoc_include ../listings/ch02-guessing-game-tutorial/no-listing-05-quitting/src/main.rs:here}}
```

在 `You win!` 之后添加 `break` 这一行代码，可以使程序在用户正确猜出秘密数字时退出循环。退出循环意味着程序也会终止运行，因为循环是 `main` 的最后一部分。

### 处理无效输入

为了进一步优化游戏的行为，当用户输入非数字字符时，不要让程序崩溃，而是让游戏忽略这些输入，这样用户就可以继续猜测。我们可以通过修改将`guess`从`String`转换为`u32`的那一行代码来实现这一点，如清单2-5所示。

<列表编号="2-5" 文件名称="src/main.rs" 标题="忽略非数字猜测，要求再次尝试，而不是导致程序崩溃">

```rust,ignore
{{#rustdoc_include ../listings/ch02-guessing-game-tutorial/listing-02-05/src/main.rs:here}}
```

</清单>

我们从一个`expect`调用切换到一个`match`表达式，从而从因错误而崩溃转变为处理错误。需要注意的是，`parse`返回一个`Result`类型的对象，而`Result`是一个枚举类型，包含`Ok`和`Err`两种变体。在这里，我们使用了一个`match`表达式，就像我们在`cmp`方法的`Ordering`结果中所做的那样。

如果 `parse` 能够成功地将字符串转换为数字，它将返回一个 `Ok` 值，该值包含转换后的数字。这个 `Ok` 值会匹配第一个臂的模式，而 `match` 表达式则只会返回由 `parse` 生成的 `num` 值，并将其放入 `Ok` 值中。这个数字最终会被放在我们新创建的 `guess` 变量中我们想要的位置上。

如果`parse`无法将字符串转换为数字，它将返回一个`Err`值，该值包含有关错误的更多信息。`Err`的值与第一个`match`分支中的`Ok(num)`模式不匹配，但它与第二个分支中的`Err(_)`模式匹配。下划线`_`是一个通用匹配值；在这个例子中，我们表示希望匹配所有`Err`。无论其中包含什么信息，程序都会执行第二个分支的代码，即`continue`。这段代码会指示程序进入`loop`的下一个迭代步骤，并再次尝试进行猜测。因此，实际上，程序会忽略`parse`可能遇到的所有错误！

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

太棒了！只需再做一个小小的调整，我们就能完成这个“猜谜游戏”了。还记得，程序仍然在打印秘密数字。虽然这在测试时效果不错，但会破坏游戏的乐趣。让我们删除那个用于输出秘密数字的 `println!` 代码吧。清单 2-6 展示了最终的代码。

<列表编号="2-6" 文件名称="src/main.rs" 标题="完整的猜谜游戏代码">

```rust,ignore
{{#rustdoc_include ../listings/ch02-guessing-game-tutorial/listing-02-06/src/main.rs}}
```

</清单>

此时，你已经成功构建了一个猜谜游戏。恭喜！

## 摘要

这个项目是一种实践性的方式，旨在让您了解许多新的Rust概念：`let`、`match`、函数、外部库的使用等等。在接下来的几章中，您将更详细地学习这些概念。第3章介绍了大多数编程语言都有的概念，如变量、数据类型和函数，并展示了如何在Rust中使用它们。第4章探讨了所有权这一特性，它使得Rust与其他语言有所不同。第5章……本文讨论了结构体和方法语法，第6章则解释了枚举类型的工作原理。

[prelude]:../std/prelude/index.html  
[variables-and-mutability]: ch03-01-variables-and-mutability.html#variables-and-mutability  
[comments]: ch03-04-comments.html  
[string]:../std/string/struct.String.html  
[iostdin]:../std/io/struct.Stdin.html  
[read_line]:../std/io/struct.Stdin.html#method.read_line  
[result]:../std/result/enum.Result.html  
[enums]: ch06-00-enums.html  
[expect]:../std/result/enum.Result.html#method.expect  
[recover]: ch09-02-recoverable-errors-with-result.html[randcrate]: https://crates.io/crates/rand  
[semver]: http://semver.org  
[cratesio]: https://crates.io/  
[doccargo]: https://doc.rust-lang.org/cargo/  
[doccratesio]: https://doc.rust-lang.org/cargo/reference/publishing.html  
[match]: ch06-02-match.html  
[shadowing]: ch03-01-variables-and-mutability.html#shadowing  
[parse]:../std/primitive.str.html#method.parse  
[integers]: ch03-02-data-types.html#integer-types