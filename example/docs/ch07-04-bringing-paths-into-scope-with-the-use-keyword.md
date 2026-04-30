## 使用 `use` 关键字将路径引入作用域

需要手动输入函数调用的路径可能会让人感到不便且重复。在清单7-7中，无论我们选择使用绝对路径还是相对路径来调用 `add_to_waitlist` 函数，每次想要调用 `add_to_waitlist` 时，都必须同时指定 `front_of_house` 和 `hosting`。幸运的是，有一种方法可以简化这个过程：我们可以使用 `use` 关键字为某个路径创建一个快捷方式，然后在整个代码范围内使用这个更简短的名称。

在 Listing 7-11 中，我们将 `crate::front_of_house::hosting` 模块引入 `eat_at_restaurant` 函数的作用域中，这样我们就只需要指定 `hosting::add_to_waitlist` 来调用 `add_to_waitlist` 函数在 `eat_at_restaurant` 中。

<Listing number="7-11" file-name="src/lib.rs" caption="Bringing a module into scope with `use`">

```rust,noplayground,test_harness
mod front_of_house {
    pub mod hosting {
        pub fn add_to_waitlist() {}
    }
}

use crate::front_of_house::hosting;

pub fn eat_at_restaurant() {
    hosting::add_to_waitlist();
}

```

</Listing>

在某个作用域中添加 `use` 并指定一个路径，相当于在文件系统中创建符号链接。通过在 crate 的根目录下添加 `use crate::front_of_house::hosting`，那么 `hosting` 就成为了该作用域中的有效名称，就好像 `hosting` 模块已经在 crate 的根目录下被定义了一样。使用 `use` 引入的作用域中的路径，同样需要检查其隐私属性，就像其他任何路径一样。

请注意，`use`仅为出现`use`的特定作用域创建快捷方式。列表7-12将`eat_at_restaurant`函数移入一个名为`customer`的新子模块中，而该子模块与`use`语句所处的作用域不同，因此函数体将无法编译。

<Listing number="7-12" file-name="src/lib.rs" caption="A `use` statement only applies in the scope it’s in.">

```rust,noplayground,test_harness,does_not_compile,ignore
mod front_of_house {
    pub mod hosting {
        pub fn add_to_waitlist() {}
    }
}

use crate::front_of_house::hosting;

mod customer {
    pub fn eat_at_restaurant() {
        hosting::add_to_waitlist();
    }
}

```

</Listing>

编译器错误表明，在`customer`模块内，该快捷方式不再适用。

```console
$ cargo build
   Compiling restaurant v0.1.0 (file:///projects/restaurant)
error[E0433]: failed to resolve: use of unresolved module or unlinked crate `hosting`
  --> src/lib.rs:11:9
   |
11 |         hosting::add_to_waitlist();
   |         ^^^^^^^ use of unresolved module or unlinked crate `hosting`
   |
   = help: if you wanted to use a crate named `hosting`, use `cargo add hosting` to add it to your `Cargo.toml`
help: consider importing this module through its public re-export
   |
10 +     use crate::hosting;
   |

warning: unused import: `crate::front_of_house::hosting`
 --> src/lib.rs:7:5
  |
7 | use crate::front_of_house::hosting;
  |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  |
  = note: `#[warn(unused_imports)]` on by default

For more information about this error, try `rustc --explain E0433`.
warning: `restaurant` (lib) generated 1 warning
error: could not compile `restaurant` (lib) due to 1 previous error; 1 warning emitted

```

请注意，还有一则警告，表明 `use` 在其作用域内已不再被使用！为了解决这个问题，需要将 `use` 也移动到 `customer` 模块中，或者在父模块中使用 `super::hosting` 作为快捷方式，然后在子模块中使用 `customer`。

### 创建符合惯用的 `use` 路径

在 Listing 7-11 中，你可能会疑惑为什么我们指定了 `use
crate::front_of_house::hosting`，然后又在 `eat_at_restaurant` 中调用 `hosting::add_to_waitlist`，而不是一直使用 `use` 路径直到 `add_to_waitlist` 函数来实现同样的效果，就像 Listing 7-13 中所做的那样。

<Listing number="7-13" file-name="src/lib.rs" caption="Bringing the `add_to_waitlist` function into scope with `use`, which is unidiomatic">

```rust,noplayground,test_harness
mod front_of_house {
    pub mod hosting {
        pub fn add_to_waitlist() {}
    }
}

use crate::front_of_house::hosting::add_to_waitlist;

pub fn eat_at_restaurant() {
    add_to_waitlist();
}

```

</Listing>

虽然列表7-11和列表7-13都实现了相同的功能，但列表7-11是使用`use`来将函数引入作用域的更惯用的方式。而使用`use`来将函数的父模块引入作用域时，我们需要在调用函数时明确指定父模块。在调用函数时明确指定父模块，可以清楚地表明该函数并非局部定义，同时还能最大限度地减少完整路径的重复。而列表7-13中的代码则不清楚`add_to_waitlist`的定义位置。

另一方面，在引入结构体、枚举以及其他具有 `use` 特性的对象时，按照惯例需要指定完整的路径。列表 7-14 展示了将标准库中的 `HashMap` 结构体引入二进制 crate 范围的惯用方式。

<Listing number="7-14" file-name="src/main.rs" caption="Bringing `HashMap` into scope in an idiomatic way">

```rust
use std::collections::HashMap;

fn main() {
    let mut map = HashMap::new();
    map.insert(1, 2);
}

```

</Listing>

这个惯用的表达方式并没有什么深层次的原因：它只是逐渐形成的惯例，人们也习惯了以这种方式阅读和编写Rust代码。

这个惯用的例外情况是，当我们使用 `use` 语句将两个同名项带入作用域时，因为 Rust 不允许这种情况。列表 7-15 展示了如何将两个具有相同名称但属于不同父模块的 `Result` 类型带入作用域，以及如何引用它们。

<Listing number="7-15" file-name="src/lib.rs" caption="Bringing two types with the same name into the same scope requires using their parent modules.">

```rust,noplayground
use std::fmt;
use std::io;

fn function1() -> fmt::Result {
    // --snip--
}

fn function2() -> io::Result<()> {
    // --snip--
}

```

</Listing>

如您所见，使用父模块可以区分两个 `Result` 类型。  
如果我们改为指定 `use std::fmt::Result` 和 `use std::io::Result`，那么在同一作用域中就会存在两个 `Result` 类型。此时，当我们使用 `Result` 时，Rust 将无法区分我们指的是哪一个类型。

### 使用 `as` 关键词为项目提供新名称

还有一种解决将两种同名类型放入同一作用域的方法，即使用 `use`。在路径之后，我们可以指定 `as`，并为该类型创建一个新的本地名称，或者称为 _别名_。列表 7-16 展示了另一种编写代码的方式，通过使用 `as` 来重命名两个 `Result` 类型中的其中一个。

<Listing number="7-16" file-name="src/lib.rs" caption="Renaming a type when it’s brought into scope with the `as` keyword">

```rust,noplayground
use std::fmt::Result;
use std::io::Result as IoResult;

fn function1() -> Result {
    // --snip--
}

fn function2() -> IoResult<()> {
    // --snip--
}

```

</Listing>

在第二个 `use` 语句中，我们为 `std::io::Result` 类型选择了新的名称 `IoResult`，这个名称不会与 `std::fmt` 中的 `Result` 产生冲突，因为我们同样将 `std::fmt` 纳入了作用域。列表 7-15 和列表 7-16 被视为惯用用法，因此这个选择完全取决于你！

### 使用 `pub use` 重新导出名称

当我们使用 `use` 关键字将一个名称引入某个作用域时，该名称对该作用域内的代码是私有的。为了让该作用域外的代码能够像该名称在该作用域内一样使用它，我们可以结合使用 `pub` 和 `use`。这种技术被称为“重新导出”，因为我们不仅将某个名称引入作用域，还使其可供其他作用域内的代码使用。

列表7-17展示了列表7-11中的代码，其中根模块中的 `use` 被更改为 `pub use`。

<Listing number="7-17" file-name="src/lib.rs" caption="Making a name available for any code to use from a new scope with `pub use`">

```rust,noplayground,test_harness
mod front_of_house {
    pub mod hosting {
        pub fn add_to_waitlist() {}
    }
}

pub use crate::front_of_house::hosting;

pub fn eat_at_restaurant() {
    hosting::add_to_waitlist();
}

```

</Listing>

在之前的版本中，外部代码需要使用路径`restaurant::front_of_house::hosting::add_to_waitlist()`来调用 `add_to_waitlist` 函数，同时还需要将 `front_of_house` 模块标记为 `pub`。但现在，由于 `pub
use` 重新导出了从根模块中得到的 `hosting` 模块，外部代码可以使用路径 `restaurant::hosting::add_to_waitlist()` 来调用该函数。

当你的代码内部结构与调用你的程序的程序员所理解的领域结构不同时，重新导出是非常有用的。例如，在这个餐厅的隐喻中，经营餐厅的人会考虑“前台”和“后台”部分。但是，访问餐厅的顾客可能不会用这些术语来思考餐厅的各个部分。通过使用 `pub
use`，我们可以以一种结构编写代码，但实际上展示的是另一种结构。这样做可以使我们的库对于使用该库的程序员以及调用该库的程序员来说更加易于管理。我们将在第十四章的“导出便捷的公共API”部分，进一步探讨 `pub use` 这一机制如何影响你的库文档，以及如何在 [“Exporting a Convenient Public API”][ch14-pub-use]<!-- ignore --> 中实现这一点。

### 使用外部包

在第二章中，我们编写了一个猜谜游戏项目，该项目使用了名为 `rand` 的外部包来获取随机数。为了在项目中使用 `rand`，我们在 _Cargo.toml_ 文件中添加了如下一行代码：

<!-- When updating the version of `rand` used, also update the version of
`rand` used in these files so they all match:
* ch02-00-guessing-game-tutorial.md
* ch14-03-cargo-workspaces.md
-->

<Listing file-name="Cargo.toml">

```toml

```

</Listing>

在_Cargo.toml_文件中添加`rand`作为依赖项，这样Cargo就会下载`rand`这个包以及来自[crates.io](https://crates.io/)的所有依赖项，并使`rand`对我们的项目可用。

然后，为了将 `rand` 定义纳入我们的包的范围，我们添加了一行代码：`use`，该代码以 crate 的名称 `rand` 开头，并列出了我们希望纳入范围的各项内容。回想一下，在第二章的 [“生成随机数”][rand]<!-- ignore --> 中，我们将 `Rng` 特质纳入了范围，并调用了 `rand::thread_rng` 函数。

```rust,ignore
use rand::Rng;

fn main() {
    let secret_number = rand::thread_rng().gen_range(1..=100);
}

```

Rust社区的成员已经在[crates.io](https://crates.io/)上发布了许多软件包。将其中任何一个软件包添加到你的项目中，也需要遵循相同的步骤：在你的`Cargo.toml`文件中列出这些软件包，并使用`use`来将相关组件引入你的项目中。

请注意，标准的 `std` 库也是一个位于我们包之外的 crate。由于标准库是随 Rust 语言一起提供的，我们不需要修改 _Cargo.toml_ 来包含 `std`。但是，我们需要使用 `use` 来引用它，以便将 `std` 中的内容引入我们的包中。例如，使用 `HashMap`，我们会这样使用：

```rust
use std::collections::HashMap;
```

这是一个绝对路径，以 `std` 开头，这是标准库的名称，即 crate。

<!-- Old headings. Do not remove or links may break. -->

<a id="using-nested-paths-to-clean-up-large-use-lists"></a>

### 使用嵌套路径来清理 `use` 列表

如果我们使用了同一个 crate 或同一个模块中定义的多个项，那么将每个项单独列在单独的行上可能会占用大量的垂直空间。例如，在 Listing 2-4 中的这两个 `use` 语句，实际上将 `std` 中的项引入了作用域。

<Listing file-name="src/main.rs">

```rust,ignore
// --snip--
use std::cmp::Ordering;
use std::io;
// --snip--

```

</Listing>

相反，我们可以使用嵌套路径来在同一行中引入相同的元素。具体做法是先指定路径的共同部分，然后加上两个冒号，最后用大括号括起来，列出那些不同的路径部分，如清单7-18所示。

<Listing number="7-18" file-name="src/main.rs" caption="Specifying a nested path to bring multiple items with the same prefix into scope">

```rust,ignore
// --snip--
use std::{cmp::Ordering, io};
// --snip--

```

</Listing>

在更大的程序中，通过嵌套路径将多个项目从同一个 crate 或模块引入作用域，可以大大减少所需的多个 `use` 语句的数量！

我们可以在路径中的任何层级使用嵌套路径，这在组合两个共享子路径的`use`语句时非常有用。例如，列表7-19展示了两个`use`语句：其中一个将`std::io`带入作用域，另一个则将`std::io::Write`带入作用域。

<Listing number="7-19" file-name="src/lib.rs" caption="Two `use` statements where one is a subpath of the other">

```rust,noplayground
use std::io;
use std::io::Write;

```

</Listing>

这两条路径的共同部分是 `std::io`，这就是完整的第一条路径。为了将这两条路径合并成一条 `use` 语句，我们可以在嵌套路径中使用 `self`，如清单 7-20 所示。

<Listing number="7-20" file-name="src/lib.rs" caption="Combining the paths in Listing 7-19 into one `use` statement">

```rust,noplayground
use std::io::{self, Write};

```

</Listing>

这一行将 `std::io` 和 `std::io::Write` 引入到作用域中。

<!-- Old headings. Do not remove or links may break. -->

<a id="the-glob-operator"></a>

### 使用全局操作符导入项目

如果我们想要将路径中定义的所有公共项引入作用域，我们可以在该路径后面加上 `*` 全局操作符来表示。

```rust
use std::collections::*;
```

这个 `use` 语句会将 `std::collections` 中定义的所有公共项带入当前作用域。使用 glob 操作符时要小心！Glob 可能会使得难以判断哪些名称处于作用域内，以及程序中使用的名称是在哪里定义的。此外，如果依赖项的定义发生变化，你所导入的内容也会随之改变，这可能会导致在升级依赖项时出现编译错误。例如，如果依赖项在相同的作用域中添加了与你的定义同名的定义，就会出现这种情况。

glob运算符在测试时经常被使用，用于将所有需要测试的内容放入`tests`模块中；我们将在第十一章的[“如何编写测试”][writing-tests]<!-- ignore -->章节中讨论这一点。glob运算符有时也被用作prelude模式的一部分：有关该模式的更多信息，请参见[标准库文档](../std/prelude/index.html#other-preludes)<!-- ignore -->。

[ch14-pub-use]: ch14-02-publishing-to-crates-io.html#exporting-a-convenient-public-api
[rand]: ch02-00-guessing-game-tutorial.html#generating-a-random-number
[writing-tests]: ch11-01-writing-tests.html#how-to-write-tests
