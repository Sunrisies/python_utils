## 在模块树中引用项目的路径

在Rust中，要显示模块树中某个项的所在位置，我们使用路径，这与在文件系统中进行导航时使用路径的方式相同。要调用一个函数，我们需要了解它的路径。

路径可以有两种形式：

- **绝对路径**是从库根开始的完整路径；对于来自外部库的代码，绝对路径以库名称开头；而对于来自当前库的代码，则以字面量``crate``开头。  
- **相对路径**则从当前模块开始，使用``self``、``super``或当前模块中的标识符作为路径起点。

绝对路径和相对路径后面都跟着一个或多个标识符，这些标识符之间用双冒号(`::`)分隔。

回到清单7-1，假设我们想要调用`add_to_waitlist`这个函数。这相当于在问：`add_to_waitlist`函数的路径是什么？清单7-3包含了去掉了一些模块和函数的清单7-1。

我们将展示两种从新函数`add_to_waitlist`中调用该函数的方法，该新函数定义在库的根目录中，即`eat_at_restaurant`。这两种路径都是正确的，但还存在另一个问题，这会使这个示例无法按当前方式编译。我们会在稍后解释原因。

`eat_at_restaurant`函数是我们的库包公共API的一部分，因此我们使用`pub`关键字来标识它。在“使用`pub`关键字公开路径”部分中，我们将更详细地介绍`pub`的功能。

<列表编号="7-3" 文件名称="src/lib.rs" 标题="使用绝对路径和相对路径调用`add_to_waitlist`函数">

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch07-managing-growing-projects/listing-07-03/src/lib.rs}}
```

</清单>

当我们第一次在`eat_at_restaurant`中调用`add_to_waitlist`函数时，我们使用了绝对路径。`add_to_waitlist`函数在与`eat_at_restaurant`相同的目录中定义，这意味着我们可以使用`crate`关键字来启动绝对路径。然后，我们依次包含各个模块，直到到达`add_to_waitlist`。你可以想象一个具有相同结构的文件系统：我们会指定路径`/front_of_house/hosting/add_to_waitlist`来执行`add_to_waitlist`程序。使用 ``crate`` 从 crate 根目录开始，就像在 shell 中使用 ``/`` 从文件系统根目录开始一样。

第二次在`eat_at_restaurant`中调用`add_to_waitlist`时，我们使用了一个相对路径。该路径以`front_of_house`开头，这是与`eat_at_restaurant`处于同一模块树级别的模块的名称。在这里，文件系统上的对应路径应该是`front_of_house/hosting/add_to_waitlist`。以模块名称作为起点意味着路径是相对的。

选择使用相对路径还是绝对路径取决于你的项目需求，以及你是否更倾向于将元素定义代码与使用该元素的代码分开处理。例如，如果我们把`front_of_house`模块和`eat_at_restaurant`函数移动到名为`customer_experience`的模块中，那么我们就需要更新到`add_to_waitlist`的绝对路径，而相对路径则保持不变。仍然有效。不过，如果我们把`eat_at_restaurant`这个函数单独移到一个名为`dining`的模块中，那么到`add_to_waitlist`调用的绝对路径保持不变，但相对路径需要更新。我们通常更倾向于使用绝对路径，因为更有可能我们需要独立地移动代码定义和项目调用。

让我们尝试编译清单7-3，看看为什么它目前无法编译！我们得到的错误信息显示在清单7-4中。

<列表编号="7-4" 标题="在清单7-3中编译代码时出现的编译器错误">

```console
{{#include ../listings/ch07-managing-growing-projects/listing-07-03/output.txt}}
```

</清单>

错误信息显示，模块`hosting`是私有的。换句话说，我们已经获得了`hosting`模块和`add_to_waitlist`函数的正确路径，但Rust不允许我们使用它们，因为它无法访问这些私有部分。在Rust中，所有项目（函数、方法、结构体、枚举、模块和常量）默认都是对父模块私有的。如果你想将一个项目（如函数或结构体）设为私有，就需要将其放在一个模块中。

父模块中的项目不能使用子模块内部的私有项目，但子模块中的项目可以使用其祖先模块中的项目。这是因为子模块会隐藏其实现细节，但子模块可以了解它们被定义的环境。继续用这个比喻来说吧，可以把这些隐私规则想象成餐厅的后台操作：在那里发生的事情对餐厅顾客来说是私密的。办公室经理可以查看并操作他们所经营的餐厅中的所有事务。

Rust选择让模块系统以这种方式运作，这样隐藏内部实现细节就是默认设置。这样一来，你可以知道哪些内部代码部分可以修改，而不会破坏外部代码。不过，Rust确实提供了一种选项，即通过使用`pub`关键字，可以将子模块的内部代码部分暴露给外部祖先模块，从而将其设为公开成员。

### 使用`pub`关键字暴露路径

让我们回到清单7-4中的错误，该错误告诉我们`hosting`模块是私有的。我们希望父模块中的`eat_at_restaurant`函数能够访问子模块中的`add_to_waitlist`函数，因此我们在`hosting`模块上添加了`pub`关键字，如清单7-5所示。

<列表编号="7-5" 文件名称="src/lib.rs" 标题="将 `hosting` 模块声明为 `pub`，以便从 `eat_at_restaurant` 中使用它">

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch07-managing-growing-projects/listing-07-05/src/lib.rs:here}}
```

</清单>

不幸的是，Listing 7-5中的代码仍然会导致编译器错误，如Listing 7-6所示。

<列表编号="7-6" 标题="在清单7-5中编译代码时出现的编译器错误">

```console
{{#include ../listings/ch07-managing-growing-projects/listing-07-05/output.txt}}
```

</清单>

发生了什么？在`mod hosting`之前加上`pub`关键字，会使该模块变为公共模块。通过这一修改，如果我们能够访问`front_of_house`，那么我们就可以访问`hosting`。但是`hosting`的内容仍然是私有的；因此，即使模块被设为公共模块，其内部的代码仍然不可访问。`pub`关键字仅允许模块中的代码引用该模块，而不能直接访问其内部代码。因为模块是容器，所以仅仅将模块公开并不能起到太大作用；我们需要进一步采取措施，选择将模块内的一个或多个项目也公开。

清单7-6中的错误表明，``add_to_waitlist``函数是私有的。隐私规则适用于结构体、枚举类型、函数和方法以及模块。

让我们通过在其定义之前添加 ``pub`` 关键字，来将 `add_to_waitlist` 函数公开化，就像在清单 7-7 中那样。

<Listing number="7-7" file-name="src/lib.rs" caption="在`mod hosting`和`fn add_to_waitlist`中添加`pub`关键字，可以让我们从`eat_at_restaurant`调用该函数。">

```rust,noplayground,test_harness
{{#rustdoc_include ../listings/ch07-managing-growing-projects/listing-07-07/src/lib.rs:here}}
```

</清单>

现在代码可以编译了！为了理解为什么在`pub`中添加`eat_at_restaurant`关键字后，我们可以按照隐私规则使用这些路径，让我们来看看绝对路径和相对路径的区别。

在绝对路径中，我们从`crate`开始，这是我们模块树的根节点。`front_of_house`模块定义在模块树的根目录下。虽然`front_of_house`不是公共的，因为`eat_at_restaurant`函数与`front_of_house`定义在同一个模块中（也就是说，`eat_at_restaurant`和`front_of_house`是兄弟模块），但我们可以从`eat_at_restaurant`引用`front_of_house`。接下来是标记为`pub`的`hosting`模块。我们可以……可以访问`hosting`的父模块，这样我们就可以访问`hosting`。最后，`add_to_waitlist`这个函数被标记为`pub`，我们可以访问它的父模块，因此这个函数调用是有效的！

在相对路径中，逻辑与绝对路径相同，唯一的区别是起始点：不是从crate的根目录开始，而是从`front_of_house`开始。`front_of_house`模块定义在同一模块内，即`eat_at_restaurant`所在的模块中，因此从包含`eat_at_restaurant`的模块开始的相对路径是有效的。此外，由于`hosting`和`add_to_waitlist`被标记为`pub`，因此剩余的路径也是有效的。函数调用是有效的！

如果您计划分享您的库代码，以便其他项目可以使用您的代码，那么您的公共API就是您与用户之间的契约，它决定了他们如何与您的代码进行交互。在管理公共API的变更时，有许多需要考虑的因素，以让人们能够更轻松地依赖您的库。这些考虑因素超出了本书的范围；如果您对此感兴趣，请参阅[Rust API指南]。

> #### 包含二进制文件和库的程序包的最佳实践>> 我们提到，一个程序包可以包含一个名为`_src/main.rs_`的二进制 crate，以及一个名为`_src/lib.rs_`的库 crate。默认情况下，这两个 crate 都将具有相同的包名称。通常，采用这种模式包含库和二进制文件的程序包，其二进制 crate 中的代码仅足以启动一个可执行文件，该可执行文件会调用库中定义的代码。> 这个包允许其他项目受益于该包所提供的所有功能，因为该库的代码可以被共享。>> 模块树应该定义在`_src/lib.rs_`文件中。然后，任何公开的内容都可以通过以包名开头的路径在二进制包中使用。> 二进制包就像完全独立的包一样使用库包：它只能使用公开的API。> 这有助于设计出一个良好的API。你不仅是作者，还是客户！在[第12章][ch12]中，我们将通过一个命令行程序来演示这种组织方式，该程序会包含二进制 crate 和库 crate。

### 以`super`开头指定相对路径

我们可以通过在路径开头使用 ``super`` 来构建从父模块开始的相对路径，而不是从当前模块或库根开始。这类似于使用 ``..``语法来启动一个文件系统路径，表示要进入父目录。使用 ``super``则允许我们引用那些我们知道存在于父模块中的项，这可以在模块与父模块关系密切时，更轻松地重新安排模块树的结构。有朝一日，它可能会被移动到模块树的其他位置。

请考虑清单7-8中的代码，它模拟了厨师修正错误订单后亲自将商品送到客户手中的情况。在`back_of_house`模块中定义的函数`fix_incorrect_order`通过指定路径`deliver_order`来调用在父模块中定义的函数`deliver_order`，该路径从`super`开始。

<列表编号="7-8" 文件名称="src/lib.rs" 标题="使用以`super`开头的相对路径调用函数">

```rust,noplayground,test_harness
{{#rustdoc_include ../listings/ch07-managing-growing-projects/listing-07-08/src/lib.rs}}
```

</清单>

`fix_incorrect_order`函数位于`back_of_house`模块中，因此我们可以使用`super`来访问`back_of_house`的父模块，在这种情况下，父模块就是`crate`，即根模块。从那里，我们寻找`deliver_order`并找到了它。成功了！我们认为`back_of_house`模块和`deliver_order`函数很可能保持相同的关系，如果我们决定重新组织模块的层次结构，它们也会被一起移动。因此，使用了 ``super``，这样如果这段代码被移到了不同的模块中，将来我们就不需要在多个地方更新这段代码了。

### 将结构体和枚举声明为公共成员

我们还可以使用 ``pub`` 来指定结构体和集合类型为公开类型。不过，``pub`` 在用于结构体和集合类型时有一些额外的细节需要注意。如果我们在一个结构体定义之前使用 ``pub``，那么该结构体就会变成公开类型，但结构体的各个字段仍然会是私有类型。我们可以根据具体情况分别将每个字段设置为公开类型或不公开类型。在清单7-9中，我们定义了一个公开的 ``back_of_house::Breakfast`` 结构体。该模型描述了一个餐厅的情境：顾客可以选择随餐提供的面包类型，但厨师会根据当季供应的情况来决定搭配哪种水果。可供选择的水果种类会很快发生变化，因此顾客无法选择水果，甚至无法知道会得到什么水果。

<列表编号="7-9" 文件名称="src/lib.rs" 标题="一个包含一些公共字段和一些私有字段的结构体">

```rust,noplayground
{{#rustdoc_include ../listings/ch07-managing-growing-projects/listing-07-09/src/lib.rs}}
```

</清单>

因为 ``back_of_house::Breakfast`` 结构体中的 ``toast`` 字段是公用的，所以在 ``eat_at_restaurant``中，我们可以使用点符号来读写 ``toast`` 字段的值。请注意，在 ``eat_at_restaurant``中不能使用 ``seasonal_fruit`` 字段，因为 ``seasonal_fruit`` 是私有的。尝试取消注释修改 ``seasonal_fruit`` 字段值的那一行代码，看看会遇到什么错误！

另外，需要注意的是，由于`back_of_house::Breakfast`拥有一个私有字段，因此该结构体需要提供一个公共的关联函数，用于创建`Breakfast`的实例（在这里我们将其命名为`summer`）。如果`Breakfast`没有这样的函数，我们就无法在`eat_at_restaurant`中创建`Breakfast`的实例，因为我们无法在`eat_at_restaurant`中设置私有字段`seasonal_fruit`的值。

相比之下，如果我们将枚举变量公开，那么所有的变体也会变得公开。我们只需要保留在`enum`关键字之前的`pub`部分，如清单7-10所示。

<List numbering="7-10" file-name="src/lib.rs" caption="将枚举类型指定为公共类型后，其所有变体也将变为公共类型。">

```rust,noplayground
{{#rustdoc_include ../listings/ch07-managing-growing-projects/listing-07-10/src/lib.rs}}
```

</清单>

因为我们将 `Appetizer` 声明为公共枚举类型，所以我们可以在 `eat_at_restaurant` 中使用 `Soup` 和 `Salad` 这两个变体。

枚举类型除非其变体是公开的，否则并不十分有用；每次都需要为所有枚举变体添加 ``pub`` 的注释，这非常麻烦。因此，默认情况下，枚举变体应该是公开的。而结构体在没有公开其字段的情况下通常很有用，所以结构体的字段默认都是私有的，除非被添加了 ``pub`` 的注释。

还有另一种涉及`pub`的情况，这是我们尚未讨论的。那就是我们的最后一个模块系统特性：`use`关键字。我们先单独介绍`use`，然后会展示如何结合使用`pub`和`use`。

[pub]: ch07-03-paths-for-referring-to-an-item-in-the-module-tree.html#exposing-paths-with-the-pub-keyword  
[api-guidelines]: https://rust-lang.github.io/api-guidelines/  
[ch12]: ch12-00-an-io-project.html