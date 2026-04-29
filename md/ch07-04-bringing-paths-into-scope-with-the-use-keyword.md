## 使用`use`关键字将路径引入作用域

需要手动输入函数调用的路径可能会让人感到不便且重复。在清单7-7中，无论我们选择的是绝对路径还是相对路径来调用`add_to_waitlist`函数，每次想要调用`add_to_waitlist`时，都必须同时指定`front_of_house`和`hosting`。幸运的是，有办法简化这个过程：我们可以使用`use`关键字一次性创建一个路径的快捷方式，然后在整个代码范围内使用这个更简短的名称。

在清单7-11中，我们将`crate::front_of_house::hosting`模块引入到`eat_at_restaurant`函数的作用域内，这样我们就只需要指定`hosting::add_to_waitlist`来调用位于`eat_at_restaurant`中的`add_to_waitlist`函数。

<列表编号="7-11" 文件名称="src/lib.rs" 标题="使用 `use` 将模块引入作用域">

```rust,noplayground,test_harness
{{#rustdoc_include ../listings/ch07-managing-growing-projects/listing-07-11/src/lib.rs}}
```

</清单>

在作用域内添加 ``use`` 以及路径，相当于在文件系统中创建符号链接。通过在库根目录下添加 ``use crate::front_of_house::hosting``，``hosting`` 现在在该作用域中成为一个有效的名称，就好像 ``hosting`` 模块已经在库根目录下定义了一样。通过 ``use`` 引入的作用域中的路径，也会像其他路径一样进行隐私检查。

请注意，`use`仅为该特定作用域中出现的`use`创建快捷方式。清单7-12将`eat_at_restaurant`函数移入一个名为`customer`的新子模块中，而该子模块与`use`语句属于不同的作用域，因此该函数体将无法编译。

<List numbering="7-12" file-name="src/lib.rs" caption="`use` 语句仅在其作用域内生效。">

```rust,noplayground,test_harness,does_not_compile,ignore
{{#rustdoc_include ../listings/ch07-managing-growing-projects/listing-07-12/src/lib.rs}}
```

</清单>

编译错误表明，该快捷方式在`customer`模块内不再适用。

```console
{{#include ../listings/ch07-managing-growing-projects/listing-07-12/output.txt}}
```

请注意，还有一个警告提示：`use`在其作用域内已不再被使用！为了解决这个问题，需要将`use`移动到`customer`模块中，或者在子模块`customer`中使用`super::hosting`来引用父模块中的快捷方式。

### 创建惯用的`use`路径

在清单7-11中，您可能会疑惑为什么我们在`eat_at_restaurant`中指定了`use crate::front_of_house::hosting` and then called `hosting::add_to_waitlist`，而不是通过`use`路径一直到`add_to_waitlist`函数来达到同样的效果，就像在清单7-13中所做的那样。

<列表编号="7-13" 文件名称="src/lib.rs" 标题="通过`use`将`add_to_waitlist`函数引入作用域，这种方法并不符合惯用法>

```rust,noplayground,test_harness
{{#rustdoc_include ../listings/ch07-managing-growing-projects/listing-07-13/src/lib.rs}}
```

</清单>

虽然清单7-11和清单7-13都实现了相同的功能，但清单7-11是使用惯用方式将函数引入作用域的方法，使用的是`use`。而使用`use`则意味着在调用函数时需要指定父模块。在调用函数时指定父模块可以明确表明该函数并非局部定义的，同时还能最大限度地减少完整路径的重复。清单7-13中的代码就是这种方法的体现。不清楚``add_to_waitlist``的定义位置。

另一方面，在引入结构体、枚举以及其他包含`use`的元素时，按照惯例需要指定完整的路径。清单7-14展示了将标准库的`HashMap`结构体引入二进制包的作用域的惯用方式。

<列表编号="7-14" 文件名称="src/main.rs" 标题="以惯用方式将`HashMap`引入作用域">

```rust
{{#rustdoc_include ../listings/ch07-managing-growing-projects/listing-07-14/src/main.rs}}
```

</清单>

这种惯用法的背后并没有什么充分的理由：它只是逐渐形成的惯例，人们也习惯了以这种方式阅读和编写Rust代码。

这个惯用的例外情况是，当我们使用`use`语句将两个同名项带入作用域时，因为Rust不允许这种情况。清单7-15展示了如何将两个具有相同名称但属于不同父模块的`Result`类型带入作用域，以及如何引用它们。

<List numbering="7-15" file-name="src/lib.rs" caption="将同名的两个类型放在同一个作用域中，需要使用它们的父模块。">

```rust,noplayground
{{#rustdoc_include ../listings/ch07-managing-growing-projects/listing-07-15/src/lib.rs:here}}
```

</清单>

如您所见，使用父模块可以区分两种类型的`Result`。如果我们指定了`use std::fmt::Result`和`use std::io::Result`，那么在同一作用域中就会存在两种类型的`Result`。这样一来，当我们使用`Result`时，Rust就无法判断我们指的是哪一种类型。

### 使用`as`关键字为新名称提供信息

解决将两种同名类型放入同一个作用域中的问题的另一种方法是：在路径之后，我们可以指定`as`以及一个新的局部名称，或者称为“别名”。清单7-16展示了通过重新命名其中一个`Result`类型来编写清单7-15中代码的另一种方式，使用的是`as`。

<列表编号="7-16" 文件名称="src/lib.rs" 标题="当类型通过 `as` 关键字被引入作用域时，对其进行重命名">

```rust,noplayground
{{#rustdoc_include ../listings/ch07-managing-growing-projects/listing-07-16/src/lib.rs:here}}
```

</清单>

在第二个``use``语句中，我们为``std::io::Result``类型选择了新的名称``IoResult``。这个名称不会与``std::fmt``中的``Result``产生冲突，因为我们也已经将``std::fmt``包含到了作用域中。列表7-15和列表7-16被认为是惯用的做法，所以选择哪个名称完全取决于你！

### 使用`pub use`重新导出名称

当我们使用 ``use`` 关键字将一个名称引入作用域时，该名称仅限于我们将其导入的那个作用域内部。为了让该作用域之外的代码能够像在作用域内部定义的一样引用该名称，我们可以结合使用 ``pub`` 和 ``use``。这种技术被称为“重新导出”，因为我们不仅将某个名称引入作用域，还使其可供其他作用域使用。

清单7-17展示了清单7-11中的代码，其中根模块中的``use``已更改为``pub use``。

<列表编号="7-17" 文件名称="src/lib.rs" 标题="通过`pub use`使名称可供任何代码在新作用域中使用">

```rust,noplayground,test_harness
{{#rustdoc_include ../listings/ch07-managing-growing-projects/listing-07-17/src/lib.rs}}
```

</清单>

在做出这个改变之前，外部代码需要使用路径`restaurant::front_of_house::hosting::add_to_waitlist()`来调用`add_to_waitlist`函数，同时还需要将`front_of_house`模块标记为`pub`。现在，由于这个`pub_use` has re-exported the `hosting`模块是从根模块中直接获取的，因此外部代码可以使用路径`restaurant::hosting::add_to_waitlist()`来进行调用。

当代码的内部结构与调用该代码的程序员对领域的理解不同的时候，重新导出是非常有用的。例如，在这个餐厅的隐喻中，经营餐厅的人会考虑“前台”和“后台”两个部分。但是，访问餐厅的顾客可能不会用这样的术语来思考餐厅的各个部分。通过使用`pubuse`，我们可以以一种结构来编写代码，但同时展示出不同的结构。这样做可以使我们的库对使用该库的程序员以及调用该库的程序员来说更加井然有序。我们将在第十四章的“导出便捷的公共API”部分，进一步探讨另一个关于`pub use`的例子，以及它如何影响你的项目的文档说明。

### 使用外部包

在第二章中，我们编写了一个猜谜游戏项目，该项目使用了一个名为`rand`的外部包来获取随机数。为了在项目中使用`rand`，我们在_Cargo.toml_文件中添加了如下行：

<!-- 在更新`rand`的版本时，同时需要更新这些文件中使用的`rand`的版本，以确保两者一致：
* ch02-00-guessing-game-tutorial.md
* ch14-03-cargo-workspaces.md
-->

<listing file-name="Cargo.toml">

```toml
{{#include ../listings/ch02-guessing-game-tutorial/listing-02-02/Cargo.toml:9:}}
```

</清单>

在_Cargo.toml_文件中添加`rand`作为依赖项，可以告诉Cargo下载`rand`包以及来自[crates.io](https://crates.io/)的所有依赖项，从而使`rand`对我们的项目可用。

然后，为了将`rand`定义纳入我们的包的作用域，我们添加了一行代码，该代码以crate的名称`rand`开头，并列出了我们希望纳入作用域的項目。請記住，在第二章的“生成随机數字”部分中，我們將`Rng`特性纳入了作用域，並调用了`rand::thread_rng`函數。

```rust,ignore
{{#rustdoc_include ../listings/ch02-guessing-game-tutorial/listing-02-03/src/main.rs:ch07-04}}
```

Rust社区的成员在[crates.io](https://crates.io/)上提供了许多软件包。将其中任何一个软件包添加到你的项目中，也需要遵循相同的步骤：在你的项目的_Cargo.toml_文件中列出这些软件包，并使用`use`来将相关代码引入你的项目中。

请注意，标准的 ``std`` 库也是一个位于我们包之外的外部依赖项。由于标准库是随Rust语言一起提供的，因此我们不需要修改 `_Cargo.toml`文件来包含 ``std``。但是，我们需要使用 ``use`` 来引用它，以便将其中的内容引入我们的包中。例如，在 ``HashMap`` 的情况下，我们会使用这样的代码：

```rust
use std::collections::HashMap;
```

这是一个绝对路径，以`std`开头，这是标准库crate的名称。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="使用嵌套路径来清理大型使用列表"></a>

### 使用嵌套路径来清理 `use` 列表

如果我们使用了同一 crate 或同一模块中定义的多个项，那么将每个项单独列在单行上可能会占用大量的垂直空间。例如，在 Listing 2-4 中的 guessing game 代码中，这两个 `use` 语句将 `std` 中的内容引入到作用域中。

<listing file-name="src/main.rs">

```rust,ignore
{{#rustdoc_include ../listings/ch07-managing-growing-projects/no-listing-01-use-std-unnested/src/main.rs:here}}
```

</清单>

相反，我们可以使用嵌套路径来在同一行中引入相同的元素。具体做法是先指定路径的共同部分，然后加上两个冒号，最后用大括号括起来，列出那些不同的路径部分，如清单7-18所示。

<列表编号="7-18" 文件名称="src/main.rs" 标题="指定嵌套路径以将具有相同前缀的多个项目纳入作用域">

```rust,ignore
{{#rustdoc_include ../listings/ch07-managing-growing-projects/listing-07-18/src/main.rs:here}}
```

</清单>

在更大的程序中，通过嵌套路径将多个项目从同一个 crate 或模块中引入，可以大大减少所需的 `use` 语句的数量！

我们可以在路径中使用嵌套路径，这在需要组合两个共享子路径的``use``语句时非常有用。例如，清单7-19展示了两个``use``语句：一个将``std::io``带入作用域，另一个则将``std::io::Write``带入作用域。

<列表编号="7-19" 文件名称="src/lib.rs" 标题="两个`use`语句，其中一个是另一个的子路径">

```rust,noplayground
{{#rustdoc_include ../listings/ch07-managing-growing-projects/listing-07-19/src/lib.rs}}
```

</清单>

这两条路径的共同部分是`std::io`，这就是完整的第一条路径。为了将这两条路径合并成一条`use`语句，我们可以在嵌套路径中使用`self`，如清单7-20所示。

<列表编号="7-20" 文件名称="src/lib.rs" 标题="将清单7-19中的路径合并为一个__INLINE_CODE__语句">

```rust,noplayground
{{#rustdoc_include ../listings/ch07-managing-growing-projects/listing-07-20/src/lib.rs}}
```

</清单>

这行代码将`std::io`和`std::io::Write`引入到作用域中。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="全局运算符"></a>

### 使用Glob运算符导入项目

如果我们想要将路径中定义的所有公共项目纳入范围，我们可以在该路径后面加上`*`全局操作符来表示。

```rust
use std::collections::*;
```

这条语句 ``use`` 会将所有在 ``std::collections`` 中定义的公共项带入当前作用域。使用glob操作符时要小心！glob使得很难判断哪些名称属于当前作用域，以及程序中使用的名称是在哪里定义的。此外，如果依赖项的定义发生变化，你所导入的内容也会随之改变，这可能会导致在升级依赖项时出现编译错误，因为新的依赖项可能会引入具有相同名称的定义。例如，作为你在同一范围内所定义的内容。

glob运算符在测试时经常被使用，用于将所有被测试的内容放入`tests`模块中；我们将在第11章的“如何编写测试”部分讨论这一点。此外，glob运算符有时也被用作prelude模式的一部分：有关该模式的更多信息，请参阅标准库文档（](../std/prelude/index.html#other-preludes）<!-- ignore -->。

[ch14-pub-use]: ch14-02-publishing-to-crates-io.html#exporting-a-convenient-public-api  
[rand]: ch02-00-guessing-game-tutorial.html#generating-a-random-number  
[writing-tests]: ch11-01-writing-tests.html#how-to-write-tests