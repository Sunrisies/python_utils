<!-- Old headings. Do not remove or links may break. -->

<a id="defining-modules-to-control-scope-and-privacy"></a>

## 使用模块控制作用域和隐私

在本节中，我们将讨论模块以及模块系统中的其他组成部分。具体来说，包括_路径_，它允许你为模块中的项命名；`use`关键字，用于将路径引入作用域；以及`pub`关键字，用于使模块中的项公开可见。我们还将讨论`as`关键字、外部包以及glob操作符。

### 模块速查表

在讨论模块和路径的详细内容之前，我们先简要介绍一下模块、路径、`use`关键字以及`pub`关键字在编译器中的工作原理，以及大多数开发者是如何组织他们的代码的。在本章中，我们会通过示例来讲解这些规则，但这里是一个很好的地方，可以借此回顾一下模块的工作原理。

- **从 crate 根开始编译**：在编译一个 crate 时，编译器首先会在 crate 根文件（对于库 crate 通常是 _src/lib.rs_，对于二进制 crate 则是 _src/main.rs_）中寻找待编译的代码。
- **声明模块**：在 crate 根文件中，可以声明新的模块；例如，如果你声明了一个名为 “garden” 的模块，其模块路径为 `mod garden;`。编译器会在以下位置查找该模块的代码：
  - 内联方式，即在 `mod
    garden` 后面的分号位置之后的花括号内
  - 在 _src/garden.rs_ 文件中
  - 在 _src/garden/mod.rs_ 文件中
- **声明子模块**：除了 crate 根文件之外，还可以在其他任何文件中声明子模块。例如，你可以在 _src/garden.rs_ 中声明 `mod vegetables;`。编译器会在以下位置查找该子模块的代码：
  - 内联方式，即直接跟随 `mod vegetables`，在花括号内而不是分号位置
  - 在 _src/garden/vegetables.rs_ 文件中
  - 在 _src/garden/vegetables/mod.rs_ 文件中
- **模块中代码的路径**：一旦一个模块成为你的 crate 的一部分，你就可以在同一 crate 的其他位置引用该模块中的代码，只要符合隐私规则，并且使用正确的代码路径。例如，在 garden vegetables 模块中定义的 `Asparagus` 类型，其路径为 `crate::garden::vegetables::Asparagus`。
- **私有与公有**：默认情况下，模块内的代码对其父模块是私有的。要将一个模块设为公有，需要使用 `pub mod` 而不是 `mod` 进行声明。若要使公有模块中的项也变为公有，则需要在声明前使用 `pub`。
- ** `use` 关键字**：在作用域内， `use` 关键字可以创建快捷方式，以减少重复编写长路径。在任何可以引用 `crate::garden::vegetables::Asparagus` 的作用域中，都可以使用 `use
  crate::garden::vegetables::Asparagus;` 创建快捷方式，之后只需使用 `Asparagus` 即可在作用域内使用该类型。

在这里，我们创建了一个名为 `backyard` 的二进制 crate，它展示了这些规则。这个 crate 的目录也命名为 _backyard_，其中包含以下文件和目录：

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

<Listing file-name="src/main.rs">

```rust,noplayground,ignore
use crate::garden::vegetables::Asparagus;

pub mod garden;

fn main() {
    let plant = Asparagus {};
    println!("I'm growing {plant:?}!");
}

```

</Listing>

The `pub mod garden;`这一行告诉编译器包含它在/src/garden.rs_中找到的代码，该代码的内容如下：

<Listing file-name="src/garden.rs">

```rust,noplayground,ignore
pub mod vegetables;

```

</Listing>

在这里，`pub mod vegetables;`表示也会包含_garden/vegetables.rs_中的代码。该代码内容如下：

```rust,noplayground,ignore
#[derive(Debug)]
pub struct Asparagus {}

```

现在让我们详细了解这些规则，并通过实际例子来演示它们！

### 将相关代码分组到模块中

_模块_ 可以帮助我们在一个软件包内组织代码，以便于阅读和提高代码的复用性。  
模块还允许我们控制代码的_隐私性_，因为模块内的代码默认是私有的。私有代码属于内部实现细节，不对外公开。我们可以选择将模块及其内的代码设为公开状态，这样外部代码就可以使用这些代码，并依赖它们。

例如，让我们编写一个库，提供餐厅的功能。我们会定义函数的签名，但让它们的实现为空，以便专注于代码的组织，而不是餐厅的具体实现。

在餐饮行业，餐厅的某些区域被称为“前台”和“后台”。_前台_是顾客所在的地方；这包括服务员接待顾客、处理点餐和付款，以及调酒师制作饮品的工作。_后台_则是厨师和厨师们在厨房工作的地方，洗碗工负责清洁，而管理人员则负责行政工作。

为了以这种方式构建我们的库，我们可以将函数组织到嵌套的模块中。通过运行 `cargo new
restaurant --lib` 创建一个新的名为 `restaurant` 的库。然后，将 Listing 7-1 中的代码放入 _src/lib.rs_ 中，以定义一些模块和函数签名；这段代码就是库的前置部分。

<Listing number="7-1" file-name="src/lib.rs" caption="A `front_of_house` module containing other modules that then contain functions">

```rust,noplayground
mod front_of_house {
    mod hosting {
        fn add_to_waitlist() {}

        fn seat_at_table() {}
    }

    mod serving {
        fn take_order() {}

        fn serve_order() {}

        fn take_payment() {}
    }
}

```

</Listing>

我们定义了一个使用 `mod` 关键字的模块，后面跟着模块的名称（在本例中为 `front_of_house`）。然后，模块的内容被放在花括号内。在模块内部，我们可以放置其他模块，比如这里的 `hosting` 和 `serving`。模块还可以包含对其他元素的定义，例如结构体、枚举、常量、特质，以及像列表 7-1 中那样的函数。

通过使用模块，我们可以将相关的定义组合在一起，并说明它们之间的关联。使用这些代码的程序员可以根据这些分组来导航代码，而不需要阅读所有的定义，这样就能更容易地找到与他们相关的定义。为这段代码添加新功能的程序员也会知道应该将代码放在哪里，以保持程序的整洁性。

之前我们提到过，_src/main.rs_ 和 _src/lib.rs_ 被称为 _crate roots_。它们被这样命名的原因是，这两个文件的内容共同构成了一个名为 `crate` 的模块，而这个模块位于整个crate的模块结构的根部，也被称为 _module tree_。

列表7-2展示了列表7-1中所述结构的模块树结构。

<Listing number="7-2" caption="The module tree for the code in Listing 7-1">

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

</Listing>

这棵树展示了某些模块是如何嵌套在其他模块中的；例如，`hosting`嵌套在`front_of_house`内部。这棵树还表明，有些模块是“兄弟模块”，也就是说它们定义在同一模块中；`hosting`和`serving`就是定义在`front_of_house`内的兄弟模块。如果模块A被包含在模块B内部，那么我们说模块A是模块B的“子模块”，而模块B则是模块A的“父模块”。请注意，整个模块树都根植于一个名为`crate`的隐含模块之下。

模块树可能会让你联想到电脑上的文件系统目录结构；这种比较非常恰当！就像文件系统中的目录一样，你使用模块来组织代码。同样地，就像目录中的文件一样，我们需要一种方法来找到我们的模块。