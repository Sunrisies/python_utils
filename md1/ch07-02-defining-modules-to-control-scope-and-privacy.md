<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="定义模块以控制作用域和隐私">

## 使用模块控制作用域与隐私

在本节中，我们将讨论模块以及模块系统中的其他组成部分。具体来说，包括`_paths_`，它允许你为模块中的项命名；``use``关键字，用于将某个路径引入作用域；以及``pub``关键字，用于使模块中的项公开可见。我们还将讨论``as``关键字、外部包，以及`glob`操作符。

### 模块速查表

在讨论模块和路径的具体细节之前，我们先简要介绍一下模块、路径、``use``关键字以及``pub``关键字在编译器中的工作原理，以及大多数开发者是如何组织代码的。在本章中，我们会通过示例来讲解这些规则，但这里是一个很好的地方，可以借此回顾一下模块的工作原理。

- **从 crate 根开始编译**：在编译一个 cratge 时，编译器首先会在 crate 根文件中进行代码编译，通常对于库 crate 来说，这个文件是 _src/lib.rs_，而对于二进制 crate 来说，则是 _src/main.rs_。
- **声明模块**：在 crate 根文件中，可以声明新的模块；例如，如果你声明了一个名为“garden”的模块，并使用了 `mod garden;`，那么编译器会在以下位置查找该模块的代码：
  - 在 `mod garden` 后面的分号之后的花括号内
  - 在 _src/garden.rs_ 文件中
  - 在 _src/garden/mod.rs_ 文件中
- **声明子模块**：除了 crate 根文件之外，还可以在其他任何文件中声明子模块。例如，你可以在 _src/garden.rs_ 中声明 `mod vegetables;`。编译器会在以下位置查找子模块的代码：
  - 在 `mod vegetables` 之后的花括号内
  - 在 _src/garden/vegetables.rs_ 文件中
  - 在 _src/garden/vegetables/mod.rs_ 文件中
- **访问模块中的代码**：一旦某个模块成为你的 cratge 的一部分，你就可以在同一 cratge 的其他地方引用该模块中的代码，只要符合隐私规则即可。例如，在 garden vegetables 模块中输入的 `Asparagus` 可以通过 `crate::garden::vegetables::Asparagus` 来访问。
- **私有与公有**：默认情况下，模块内的代码对其父模块是私有的。要将一个模块设为公有的，需要使用 `pub mod` 而不是 `mod` 进行声明。若要使公有模块中的项目也变为公有，则需要在声明前使用 `pub`。
- **`use` 关键字**：在作用域内，`use` 关键字可以用来创建快捷方式，从而减少冗长的路径引用。在任何可以引用 `crate::garden::vegetables::Asparagus` 的作用域中，都可以使用 `use crate::garden::vegetables::Asparagus;` 来创建快捷方式，之后只需编写 `Asparagus` 即可在作用域内使用该类型。

在这里，我们创建了一个名为 `backyard` 的二进制 crate，用于演示这些规则。该 crate 的目录也命名为 _backyard_，其中包含以下文件和目录：

```text
backyard
├── Cargo.lock
├── Cargo.toml
└── src
    ├── garden
    │   └── vegetables.rs
    ├── garden.rs
    └── main.rs
```

在这种情况下，这个 crate 的根文件是 `_src/main.rs_`，它包含以下内容：

<code listing file-name="src/main.rs">

```rust,noplayground,ignore
{{#rustdoc_include ../listings/ch07-managing-growing-projects/quick-reference-example/src/main.rs}}
```

</ Listing>

`pub mod garden;`这一行代码告诉编译器包含在src/garden.rs文件中找到的代码，该文件的内容如下：

<Listing file-name="src/garden.rs">

```rust,noplayground,ignore
{{#rustdoc_include ../listings/ch07-managing-growing-projects/quick-reference-example/src/garden.rs}}
```

</ Listing>

在这里，`pub mod vegetables;`表示`_src/garden/vegetables.rs_`中的代码也会被包含进来。该代码的内容如下：

```rust,noplayground,ignore
{{#rustdoc_include ../listings/ch07-managing-growing-projects/quick-reference-example/src/garden/vegetables.rs}}
```

现在让我们详细了解这些规则，并通过实际例子来演示它们！

### 将相关代码分组到模块中

_模块_ 让我们在 crate 内组织代码，以便于阅读和提高代码的复用性。  
模块还允许我们控制项目的_隐私性_，因为模块内的代码默认是私有的。私有项目是内部实现细节，不允许外部使用。我们可以选择将模块及其内的项目设为公开，这样外部代码就可以使用并依赖它们。

例如，让我们编写一个库，提供餐厅的功能。我们会定义函数的签名，但让它们的实现为空，以便我们专注于代码的组织，而不是餐厅的具体实现。

在餐饮行业，餐厅的部分区域被称为“前台”和“后台”。_前台_是顾客所在的地方；这包括服务员接待顾客、处理点餐和付款，以及调酒师制作饮品的工作。_后台_则是厨师和厨师们在厨房工作、洗碗工进行清洁，以及管理人员处理行政事务的地方。

为了以这种方式构建我们的库，我们可以将其中的函数组织到嵌套的模块中。通过运行 `cargo new restaurant --lib` 创建一个新的名为 ``restaurant`` 的库。然后，将 Listing 7-1 中的代码复制到 `_src/lib.rs_`文件中，以定义一些模块和函数签名；这段代码就是库的前端部分。

<列表编号="7-1" 文件名称="src/lib.rs" 标题="一个包含其他模块的`front_of_house`模块，而这些模块中又包含函数">

```rust,noplayground
{{#rustdoc_include ../listings/ch07-managing-growing-projects/listing-07-01/src/lib.rs}}
```

</ Listing>

我们定义一个模块，使用 ``mod`` 关键字，后面跟着模块的名称（在本例中为 ``front_of_house``）。然后，模块的代码部分被放在花括号内。在模块内部，我们可以放置其他模块，比如这里的 ``hosting`` 和 ``serving``。模块还可以包含对其他元素的定义，例如结构体、枚举、常量、特质，以及像清单 7-1 中那样的函数。

通过使用模块，我们可以将相关的定义组合在一起，并说明它们之间的关联。使用此代码的程序员可以根据这些分组来导航代码，而不需要阅读所有的定义，这样就能更容易地找到与他们相关的定义。为这段代码添加新功能的程序员也会知道应该将代码放在哪里，以保持程序的整洁性。

之前我们提到过，_src/main.rs_ 和 _src/lib.rs_ 被称为 _crate roots_。它们被这样命名的原因是，这两个文件的内容在 crate 的模块结构的根目录下形成了一个名为 `crate` 的模块，这个模块被称为 _module tree_。

清单7-2展示了清单7-1中所述结构的模块树结构。

<Listing number="7-2" caption="Listing 7-1 中代码的模块树">

```text
crate
 └── front_of_house
     ├── hosting
     │   ├── add_to_waitlist
     │   └── seat_at_table
     └── serving
         ├── take_order
         ├── serve_order
         └── take_payment
```

</ Listing>

这棵树展示了某些模块是如何嵌套在其他模块中的；例如，`hosting`嵌套在`front_of_house`内部。这棵树还表明，有些模块是“兄弟模块”，也就是说它们被定义在同一模块中；`hosting`和`serving`就是被定义在`front_of_house`内的兄弟模块。如果模块A被包含在模块B内部，那么我们说模块A是模块B的“子模块”，而模块B则是模块A的“父模块”。请注意，整个模块树都根植于一个名为`crate`的隐式模块之下。

模块树可能会让你联想到电脑上的文件系统目录结构；这是一个非常恰当的类比！就像文件系统中的目录一样，你使用模块来组织你的代码。同样地，就像目录中的文件一样，我们需要一种方法来找到我们的模块。