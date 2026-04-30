## 将模块分离到不同的文件中

到目前为止，本章中的所有示例都在一个文件中定义了多个模块。当模块变得较大时，你可能希望将其定义移到一个单独的文件中，这样代码就更容易浏览了。

例如，让我们从清单7-17中的代码开始，该代码包含多个餐厅模块。我们将这些模块提取到单独的文件中，而不是将所有模块都定义在库根文件中。在这种情况下，库根文件是`src/lib.rs_`，但这一做法也适用于库根文件为`_src/main.rs__`的二进制库。

首先，我们将 `front_of_house` 模块提取到单独的文件中。删除 `front_of_house` 模块内的代码，只保留 `mod front_of_house;` 的声明，这样 _src/lib.rs_ 就只包含列表 7-21 中显示的代码。请注意，除非我们创建列表 7-22 中的 src/front_of_house.rs 文件，否则这段代码将无法编译。

<Listing number="7-21" file-name="src/lib.rs" caption="Declaring the `front_of_house` module whose body will be in *src/front_of_house.rs*">

```rust,ignore,does_not_compile
mod front_of_house;

pub use crate::front_of_house::hosting;

pub fn eat_at_restaurant() {
    hosting::add_to_waitlist();
}

```

</Listing>

接下来，将那些放在花括号中的代码复制到一个新的文件中，文件名为 `src/front_of_house.rs`，如清单7-22所示。编译器知道应该在这个文件中查找代码，因为它在 crate 根的模块声明中发现了名为 `front_of_house` 的模块。

<Listing number="7-22" file-name="src/front_of_house.rs" caption="Definitions inside the `front_of_house` module in *src/front_of_house.rs*">

```rust,ignore
pub mod hosting {
    pub fn add_to_waitlist() {}
}

```

</Listing>

请注意，您只需在模块树中使用 `mod` 声明一次加载文件。一旦编译器知道该文件是项目的一部分（并且由于您放置了 `mod` 语句，因此知道代码在模块树的哪个位置），项目中的其他文件就应该使用指向该文件声明的路径来引用该文件中的代码，这一点在[“在模块树中引用项的路径”][paths]<!-- ignore -->章节中有详细说明。换句话说，`mod` 并不是您在其他编程语言中可能见过的“包含”操作。

接下来，我们将 `hosting` 模块提取到单独的文件中。这个过程有点不同，因为 `hosting` 是 `front_of_house` 的子模块，而不是根模块的子模块。我们将 `hosting` 的文件放置在一个新目录中，该目录的名称将基于模块树中的祖先模块，在本例中为 _src/front_of_house_。

要开始使用 `hosting`，我们需要将 _src/front_of_house.rs_ 文件修改为仅包含 `hosting` 模块的声明：

<Listing file-name="src/front_of_house.rs">

```rust,ignore
pub mod hosting;

```

</Listing>

然后，我们创建一个名为 _src/front_of_house_ 的目录，以及一个名为 _hosting.rs_ 的文件，用于存放 `hosting` 模块中定义的内容。

<Listing file-name="src/front_of_house/hosting.rs">

```rust,ignore
pub fn add_to_waitlist() {}

```

</Listing>

如果我们把 _hosting.rs_ 放在 _src_ 目录下，编译器会认为 _hosting.rs_ 代码应该位于 crate 根目录中声明的一个 `hosting` 模块里，而不是作为一个 `front_of_house` 模块的子模块来声明。编译器的规则决定了哪些文件需要检查哪些模块的代码，这意味着目录和文件的结构与模块树更为匹配。

> ### 替代的文件路径
>
> 到目前为止，我们已经介绍了Rust编译器使用的最惯用的文件路径方式，但Rust还支持一种较旧的文件路径风格。对于在 crate 根目录中声明的名为`front_of_house`的模块，编译器会在以下位置查找该模块的代码：
>
> - _src/front_of_house.rs_（我们已介绍过的方式）
> - _src/front_of_house/mod.rs_（较旧风格，但仍被支持的路径）
>
> 对于作为`front_of_house`的子模块的名为`hosting`的模块，编译器会在以下位置查找该模块的代码：
>
> - _src/front_of_house/hosting.rs_（我们已介绍过的方式）
> - _src/front_of_house/hosting/mod.rs_（较旧风格，但仍被支持的路径）
>
> 如果你在同一模块中使用这两种风格的路径，将会出现编译器错误。在同一个项目中为不同的模块使用这两种风格是允许的，但这可能会让项目使用者感到困惑。
>
> 使用名为_mod.rs_的文件路径方式的主要缺点是，你的项目可能会有很多名为_mod.rs_的文件，这在同时打开这些文件时可能会让人感到困惑。

我们已经将每个模块的代码移动到单独的文件中，而模块结构仍然保持不变。在 `eat_at_restaurant` 中的函数调用无需任何修改即可正常工作，尽管这些函数的定义位于不同的文件中。这种技术允许你在模块的大小增长时将其移动到新的文件中。

请注意，src/lib.rs_中的`pub use crate::front_of_house::hosting`语句并没有发生变化，`use`对编译成的文件也没有任何影响。`mod`关键字用于声明模块，Rust会查找与模块名称相同的文件来查找该模块中的代码。

## 摘要

Rust允许你将一个包拆分为多个子包，再将每个子包拆分为多个模块。这样，你就可以从一个模块引用另一个模块中定义的项。你可以通过指定绝对路径或相对路径来实现这一点。这些路径可以通过`use`语句引入作用域，这样你就可以在多个地方使用更短的路径来引用该项。默认情况下，模块代码是私有的，但你可以通过添加`pub`关键字来将其定义公开。

在下一章中，我们将介绍一些标准库中的集合数据结构，这些数据结构可以让你在整洁的代码结构中加以使用。

[paths]: ch07-03-paths-for-referring-to-an-item-in-the-module-tree.html
