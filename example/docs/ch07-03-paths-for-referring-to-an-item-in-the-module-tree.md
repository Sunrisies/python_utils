## 在模块树中引用项目的路径

在模块树中查找某个项的位置，我们可以使用与在文件系统中导航时相同的路径方式。要调用一个函数，我们需要了解它的路径。

路径可以有两种形式：

- 绝对路径是指从 crate 根目录开始的完整路径；对于来自外部 crate 的代码，绝对路径以 crate 名称开头；而对于来自当前 crate 的代码，则以字面量 `crate` 开头。
- 相对路径则从当前模块开始，使用 `self`、 `super` 或当前模块中的标识符作为路径起点。

绝对路径和相对路径后面都跟着一个或多个标识符，这些标识符之间用双冒号分隔（`::`）。

回到清单7-1，假设我们想要调用`add_to_waitlist`这个函数。这相当于在问：`add_to_waitlist`函数的调用路径是什么？清单7-3包含了去掉了一些模块和函数的清单7-1。

我们将展示两种从新函数`eat_at_restaurant`中调用 `add_to_waitlist` 的方法，该函数定义在 crate 的根目录中。这两种路径都是正确的，但还有一个问题存在，这会使得这个示例无法按原样编译。我们会在稍后解释原因。

`eat_at_restaurant`函数是我们库公共API的一部分，因此我们使用`pub`关键字来标识它。在[“使用`pub`关键字公开路径”][pub]<!-- ignore -->章节中，我们将详细介绍`pub`函数。

<Listing number="7-3" file-name="src/lib.rs" caption="Calling the `add_to_waitlist` function using absolute and relative paths">

```rust,ignore,does_not_compile
mod front_of_house {
    mod hosting {
        fn add_to_waitlist() {}
    }
}

pub fn eat_at_restaurant() {
    // Absolute path
    crate::front_of_house::hosting::add_to_waitlist();

    // Relative path
    front_of_house::hosting::add_to_waitlist();
}

```

</Listing>

在 `eat_at_restaurant` 中首次调用 `add_to_waitlist` 函数时，我们使用绝对路径。 `add_to_waitlist` 函数定义在同一 crate 中，与 `eat_at_restaurant` 相同，因此我们可以使用 `crate` 关键字来启动绝对路径。接着，我们依次包含各个模块，直到到达 `add_to_waitlist`。你可以想象一个具有相同结构的文件系统：我们会指定 `/front_of_house/hosting/add_to_waitlist` 路径来运行 `add_to_waitlist` 程序；使用 `crate` 从 crate 根开始，就像在 shell 中使用 `/` 从文件系统根开始一样。

在 `eat_at_restaurant` 中第二次调用 `add_to_waitlist` 时，我们使用相对路径。该路径以 `front_of_house` 开始，这是与 `eat_at_restaurant` 处于同一模块树级别的模块的名称。在文件系统中，这相当于使用路径 `front_of_house/hosting/add_to_waitlist`。以模块名称作为起点意味着路径是相对的。

选择使用相对路径还是绝对路径，这取决于你的项目需求。如果你更倾向于将项目定义代码与使用该代码的代码分开或合并在一起，那么就需要做出相应的选择。例如，如果我们把 `front_of_house` 模块和 `eat_at_restaurant` 函数移入到名为 `customer_experience` 的模块中，那么就需要更新绝对路径为 `add_to_waitlist`，但相对路径仍然有效。然而，如果我们把 `eat_at_restaurant` 函数单独移入到名为 `dining` 的模块中，那么调用 `add_to_waitlist` 的绝对路径保持不变，但相对路径则需要更新。一般来说，我们更倾向于使用绝对路径，因为通常情况下，我们会希望将代码定义和项目调用分开进行。

让我们尝试编译清单7-3，看看为什么它目前无法编译！我们得到的错误信息显示在清单7-4中。

<Listing number="7-4" caption="Compiler errors from building the code in Listing 7-3">

```console
$ cargo build
   Compiling restaurant v0.1.0 (file:///projects/restaurant)
error[E0603]: module `hosting` is private
 --> src/lib.rs:9:28
  |
9 |     crate::front_of_house::hosting::add_to_waitlist();
  |                            ^^^^^^^  --------------- function `add_to_waitlist` is not publicly re-exported
  |                            |
  |                            private module
  |
note: the module `hosting` is defined here
 --> src/lib.rs:2:5
  |
2 |     mod hosting {
  |     ^^^^^^^^^^^

error[E0603]: module `hosting` is private
  --> src/lib.rs:12:21
   |
12 |     front_of_house::hosting::add_to_waitlist();
   |                     ^^^^^^^  --------------- function `add_to_waitlist` is not publicly re-exported
   |                     |
   |                     private module
   |
note: the module `hosting` is defined here
  --> src/lib.rs:2:5
   |
 2 |     mod hosting {
   |     ^^^^^^^^^^^

For more information about this error, try `rustc --explain E0603`.
error: could not compile `restaurant` (lib) due to 2 previous errors

```

</Listing>

错误信息显示，模块 `hosting` 是私有的。换句话说，我们已经获得了 `hosting` 模块和 `add_to_waitlist` 函数的正确路径，但由于 Rust 无法访问这些私有部分，因此无法使用它们。在 Rust 中，所有项（函数、方法、结构体、枚举、模块和常量）默认都是对父模块私有的。如果你想将一个函数或结构体等项设为私有，就需要将其放在一个模块中。

父模块中的项不能使用子模块内部的私有项，但子模块中的项可以使用其祖先模块中的项。这是因为子模块会隐藏其实现细节，但子模块可以了解其被定义的环境。用比喻来说，可以把这些隐私规则想象成餐厅的后台操作：后台发生的事情对餐厅顾客来说是私密的，但办公室经理可以查看并操作餐厅内的所有事务。

Rust选择以这种方式实现模块系统，这样隐藏内部实现细节就是默认设置。这样一来，你可以知道哪些内部代码部分可以修改，而不会破坏外部代码。不过，Rust确实提供了一种选项，即使用 `pub` 关键字来将子模块的内部代码部分暴露给外部祖先模块，从而将其设为公开项。

### 使用 `pub` 关键字公开路径

让我们回到清单7-4中的错误，该错误告诉我们 `hosting` 模块是私有的。我们希望父模块中的 `eat_at_restaurant` 函数能够访问子模块中的 `add_to_waitlist` 函数，因此我们使用 `pub` 关键字来标记 `hosting` 模块，如清单7-5所示。

<Listing number="7-5" file-name="src/lib.rs" caption="Declaring the `hosting` module as `pub` to use it from `eat_at_restaurant`">

```rust,ignore,does_not_compile
mod front_of_house {
    pub mod hosting {
        fn add_to_waitlist() {}
    }
}

// -- snip --

```

</Listing>

不幸的是，如清单7-6所示，清单7-5中的代码仍然会导致编译器错误。

<Listing number="7-6" caption="Compiler errors from building the code in Listing 7-5">

```console
$ cargo build
   Compiling restaurant v0.1.0 (file:///projects/restaurant)
error[E0603]: function `add_to_waitlist` is private
  --> src/lib.rs:10:37
   |
10 |     crate::front_of_house::hosting::add_to_waitlist();
   |                                     ^^^^^^^^^^^^^^^ private function
   |
note: the function `add_to_waitlist` is defined here
  --> src/lib.rs:3:9
   |
 3 |         fn add_to_waitlist() {}
   |         ^^^^^^^^^^^^^^^^^^^^

error[E0603]: function `add_to_waitlist` is private
  --> src/lib.rs:13:30
   |
13 |     front_of_house::hosting::add_to_waitlist();
   |                              ^^^^^^^^^^^^^^^ private function
   |
note: the function `add_to_waitlist` is defined here
  --> src/lib.rs:3:9
   |
 3 |         fn add_to_waitlist() {}
   |         ^^^^^^^^^^^^^^^^^^^^

For more information about this error, try `rustc --explain E0603`.
error: could not compile `restaurant` (lib) due to 2 previous errors

```

</Listing>

发生了什么？在 `mod hosting` 前面添加 `pub` 关键字后，该模块就变成了公开模块。通过这种修改，如果我们能够访问 `front_of_house`，那么我们也能够访问 `hosting`。但是 `hosting` 的内容仍然是私有的；将模块变为公开状态并不会使其内容变得公开。在模块上使用 `pub` 关键字，只是允许其祖先模块中的代码引用该模块，而不是访问其内部的代码。由于模块本质上是容器，仅仅将模块变为公开状态并不能起到太大作用；我们需要进一步采取措施，将模块内的一个或多个项也设置为公开状态。

清单 7-6 中的错误表明 `add_to_waitlist` 函数是私有的。  
隐私规则适用于结构体、枚举、函数、方法以及模块。

让我们通过在其定义前添加 `pub` 这个关键字，来将 `add_to_waitlist` 函数公开化，就像 Listing 7-7 中那样。

<Listing number="7-7" file-name="src/lib.rs" caption="Adding the `pub` keyword to `mod hosting` and `fn add_to_waitlist` lets us call the function from `eat_at_restaurant`.">

```rust,noplayground,test_harness
mod front_of_house {
    pub mod hosting {
        pub fn add_to_waitlist() {}
    }
}

// -- snip --

```

</Listing>

现在代码可以编译了！为了理解为什么添加 `pub` 这个关键字可以让我们在 `eat_at_restaurant` 中使用这些路径，同时遵守隐私规则，让我们来看看绝对路径和相对路径的区别。

在绝对路径中，我们从 `crate` 开始，这是我们 crate 模块树的根节点。`front_of_house` 模块定义在 crate 的根目录下。而 `front_of_house` 并不是公共模块，因为 `eat_at_restaurant` 函数定义在与 `front_of_house` 相同的模块中（也就是说，`eat_at_restaurant` 和 `front_of_house` 是兄弟模块）。不过，我们可以从 `eat_at_restaurant` 中引用 `front_of_house`。接下来是标有 `pub` 的 `hosting` 模块。我们可以访问 `hosting` 的父模块，因此也可以访问 `hosting`。最后，`add_to_waitlist` 函数被标记为 `pub`，我们可以访问它的父模块，因此这个函数的调用是有效的！

在相对路径中，逻辑与绝对路径相同，唯一的区别在于第一步：路径不是从 crate 的根目录开始，而是从 `front_of_house` 开始。`front_of_house` 模块定义在同一模块内，与 `eat_at_restaurant` 相同，因此从定义 `eat_at_restaurant` 的模块开始的相对路径是有效的。此外，因为 `hosting` 和 `add_to_waitlist` 都被标记为 `pub`，所以路径的其余部分也是有效的，因此这个函数调用是有效的！

如果您计划分享您的库 crate，以便其他项目可以使用您的代码，那么您的公共 API 就是您与 crate 用户之间的契约，它决定了他们如何与您的代码进行交互。在管理公共 API 的变更时，有许多需要考虑的因素，以便人们能够更轻松地依赖您的 crate。这些考虑因素超出了本书的范围；如果您对此感兴趣，请参考 [Rust API 指南][api-guidelines]。

> #### 包含二进制文件和库包的最佳实践  
> 我们提到，一个包可以包含 _src/main.rs_ 形式的二进制 crate 根，以及 _src/lib.rs_ 形式的库 crate 根。默认情况下，这两个 crate 都会使用相同的包名。通常，采用这种模式的包中，二进制 crate 只包含足够的代码来启动一个可执行文件，该可执行文件会调用库 crate 中定义的代码。这样，其他项目就可以充分利用该包提供的功能，因为库 crate 的代码可以被共享。  
> 模块树应该定义在 _src/lib.rs_ 中。然后，任何公开的内容都可以通过以包名开头的路径在二进制 crate 中使用。二进制 crate 就像完全独立的 crate 一样使用库 crate：它只能使用库 crate 中的公开 API。这有助于设计良好的 API；你不仅是包的作者，也是使用该包的客户！  
> 在[第12章][ch12]中，我们将通过一个命令行程序来演示这种组织方式，该程序同时包含二进制 crate 和库 crate。

### 使用 `super` 开始相对路径

我们可以通过在路径开头使用 `super` 来构建从父模块开始的相对路径，而不是从当前模块或 crate 根目录开始。这类似于使用 `..` 语法来启动文件系统路径，表示进入父目录。使用 `super` 则允许我们引用一个我们知道存在于父模块中的项，这可以在模块与父模块关系紧密但父模块将来可能会移动到模块树的其他位置时，更轻松地重新安排模块结构。

请参考清单7-8中的代码，该代码模拟了厨师修正错误订单后亲自将订单送到客户手中的情况。在 `back_of_house` 模块中定义的函数 `fix_incorrect_order`，通过指定路径 `deliver_order` 来调用在父模块中定义的函数 `deliver_order`，路径从 `super` 开始。

<Listing number="7-8" file-name="src/lib.rs" caption="Calling a function using a relative path starting with `super`">

```rust,noplayground,test_harness
fn deliver_order() {}

mod back_of_house {
    fn fix_incorrect_order() {
        cook_order();
        super::deliver_order();
    }

    fn cook_order() {}
}

```

</Listing>

`fix_incorrect_order`函数位于`back_of_house`模块中，因此我们可以使用`super`来访问`back_of_house`的父模块，在这种情况下，父模块就是`crate`，即根模块。从那里，我们查找`deliver_order`并找到了它。成功！我们认为`back_of_house`模块和`deliver_order`函数很可能保持相同的关系，如果决定重新组织该包的模块结构，那么这两个模块就可以一起移动。因此，我们使用`super`，这样如果这段代码被移动到不同的模块中，将来更新代码的地方就会减少。

### 将结构体与枚举类型公开化

我们还可以使用 `pub` 来指定结构体和集合类型为公共类型。但是，在使用 `pub` 处理结构体和集合类型时，有一些额外的细节需要注意。如果在结构体定义之前使用 `pub`，那么该结构体会被设为公共类型，但结构体的字段仍然为私有类型。我们可以根据具体情况分别将每个字段设为公共类型或私有类型。在 Listing 7-9 中，我们定义了一个公共类型的 `back_of_house::Breakfast` 结构体，该结构体有一个公共类型的 `toast` 字段，但有一个私有类型的 `seasonal_fruit` 字段。这模拟了餐厅中的情况：顾客可以选择餐点附带的面包类型，而厨师则根据当季供应和库存情况来决定搭配的水果。可用的水果种类会很快发生变化，因此顾客无法选择水果，甚至无法看到他们将获得哪些水果。

<Listing number="7-9" file-name="src/lib.rs" caption="A struct with some public fields and some private fields">

```rust,noplayground
mod back_of_house {
    pub struct Breakfast {
        pub toast: String,
        seasonal_fruit: String,
    }

    impl Breakfast {
        pub fn summer(toast: &str) -> Breakfast {
            Breakfast {
                toast: String::from(toast),
                seasonal_fruit: String::from("peaches"),
            }
        }
    }
}

pub fn eat_at_restaurant() {
    // Order a breakfast in the summer with Rye toast.
    let mut meal = back_of_house::Breakfast::summer("Rye");
    // Change our mind about what bread we'd like.
    meal.toast = String::from("Wheat");
    println!("I'd like {} toast please", meal.toast);

    // The next line won't compile if we uncomment it; we're not allowed
    // to see or modify the seasonal fruit that comes with the meal.
    // meal.seasonal_fruit = String::from("blueberries");
}

```

</Listing>

因为在 `back_of_house::Breakfast` 结构体中的 `toast` 字段是公用的，所以在 `eat_at_restaurant` 中我们可以使用点符号来访问和读取 `toast` 字段。请注意，我们不能在 `eat_at_restaurant` 中使用 `seasonal_fruit` 字段，因为 `seasonal_fruit` 是私有的。试着取消注释那行代码，看看会收到什么错误！

另外，需要注意的是，由于 `back_of_house::Breakfast` 拥有一个私有字段，因此该结构体需要提供一个公共的关联函数，用于创建 `Breakfast` 的实例（我们在这里将其命名为 `summer`）。如果 `Breakfast` 没有这样的函数，我们就无法在 `eat_at_restaurant` 中创建 `Breakfast` 的实例，因为我们无法在 `eat_at_restaurant` 中设置私有字段 `seasonal_fruit` 的值。

相比之下，如果我们将一个枚举变量设为公共变量，那么其所有的变体也都会成为公共变量。我们只需要在 `enum` 关键字之前加上 `pub`，如清单7-10所示。

<Listing number="7-10" file-name="src/lib.rs" caption="Designating an enum as public makes all its variants public.">

```rust,noplayground
mod back_of_house {
    pub enum Appetizer {
        Soup,
        Salad,
    }
}

pub fn eat_at_restaurant() {
    let order1 = back_of_house::Appetizer::Soup;
    let order2 = back_of_house::Appetizer::Salad;
}

```

</Listing>

因为我们将 `Appetizer` 枚举公开化了，所以我们可以在 `eat_at_restaurant` 中使用 `Soup` 和 `Salad` 这两种变体。

枚举类型除非其变体是公开的，否则并不十分有用；每次都需要为所有枚举变体添加 `pub` 的注释，这确实很麻烦。因此，枚举变体的默认值是公开的。而结构体在没有公开其字段的情况下通常很有用，所以结构体的字段默认都是私有的，除非被添加了 `pub` 的注释。

还有另一种涉及 `pub` 的情况，这是我们尚未讨论的。那就是我们的最后一个模块系统特性：`use` 关键字。我们先单独介绍 `use`，然后再说明如何组合 `pub` 和 `use`。

[pub]: ch07-03-paths-for-referring-to-an-item-in-the-module-tree.html#exposing-paths-with-the-pub-keyword
[api-guidelines]: https://rust-lang.github.io/api-guidelines/
[ch12]: ch12-00-an-io-project.html
