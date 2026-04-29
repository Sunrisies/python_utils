## 将模块分离到不同的文件中

到目前为止，本章中的所有示例都在一个文件中定义了多个模块。当模块变得较大时，你可能希望将其定义移到一个单独的文件中，以便更容易地浏览代码。

例如，让我们从清单7-17中的代码开始，该代码包含多个餐厅模块。我们将这些模块提取到单独的文件中，而不是将所有模块都定义在库根文件里。在这种情况下，库根文件是`src/lib.rs_`，不过这个做法也适用于那些库根文件为`_src/main.rs__`的二进制库。

首先，我们将`front_of_house`模块提取到单独的文件中。删除`front_of_house`模块内的代码，只保留`mod front_of_house;`的声明，这样src/lib.rs文件就只包含清单7-21中展示的代码。请注意，在按照清单7-22创建src/front_of_house.rs文件之前，这段代码是无法编译的。

<列表编号="7-21" 文件名称="src/lib.rs" 标题="声明 `front_of_house` 模块，其主体将位于 *src/front_of_house.rs* 中">

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch07-managing-growing-projects/listing-07-21-and-22/src/lib.rs}}
```

</清单>

接下来，将大括号中的代码放入一个新的文件中，文件名为`src/front_of_house.rs`，如清单7-22所示。编译器知道要查找这个文件，因为它在库根目录中找到了名为``front_of_house``的模块声明。

<List numbering="7-22" file-name="src/front_of_house.rs" caption="在*src/front_of_house.rs*中的`front_of_house`模块内的定义">

```rust,ignore
{{#rustdoc_include ../listings/ch07-managing-growing-projects/listing-07-21-and-22/src/front_of_house.rs}}
```

</清单>

请注意，您只需在模块树中使用一次 ``mod`` 声明来加载一个文件。一旦编译器知道该文件是项目的一部分（并且由于您放置了 ``mod`` 语句，因此知道代码在模块树的哪个位置），项目中的其他文件就应该使用指向该文件声明位置的路径来引用该文件的代码，具体细节请参阅[“在模块树中引用项目的路径”][paths]<!-- ignore -->章节。换句话说，`mod`并不属于你在其他编程语言中可能见过的“包含”操作。

接下来，我们将`hosting`模块提取到一个独立的文件中。这个过程有点不同，因为`hosting`是`front_of_house`的子模块，而不是根模块的子模块。我们将`hosting`的文件放置在一个新的目录中，该目录的名称将根据其模块树中的祖先节点来命名，在本例中为_src/front_of_house_。

为了开始执行`hosting`，我们需要将`_src/front_of_house.rs_`修改为仅包含`hosting`模块的声明：

<listing file-name="src/front_of_house.rs">

```rust,ignore
{{#rustdoc_include ../listings/ch07-managing-growing-projects/no-listing-02-extracting-hosting/src/front_of_house.rs}}
```

</清单>

然后，我们创建一个名为`_src/front_of_house_`的目录以及一个名为`_hosting.rs_`的文件，用于存放``hosting``模块中定义的内容。

<listing file-name="src/front_of_house/hosting.rs">

```rust,ignore
{{#rustdoc_include ../listings/ch07-managing-growing-projects/no-listing-02-extracting-hosting/src/front_of_house/hosting.rs}}
```

</清单>

如果我们把 _hosting.rs_ 放在 _src_ 目录下，编译器会认为 _hosting.rs_ 代码应该位于在 crate 根目录中声明的 `hosting` 模块中，而不是作为 `front_of_house` 模块的子模块来声明。编译器的规则决定了哪些文件需要检查哪些模块的代码，这意味着目录和文件与模块树的结构更为匹配。

> ### 替代的文件路径  
到目前为止，我们已经介绍了Rust编译器使用的最常用的文件路径方式，但Rust还支持一种较旧的文件路径格式。对于在 crate 根目录中定义的名为`front_of_house`的模块，编译器会在以下位置查找该模块的代码：  
- _src/front_of_house.rs_（我们之前已经介绍过的方式）  
- _src/front_of_house/mod.rs_（较旧的路径格式，仍然被支持）  

对于作为`front_of_house`子模块的`hosting`模块来说，> 编译器会在以下位置查找模块的代码：  
> - _src/front_of_house/hosting.rs_（我们之前已经讨论过的内容）  
> - _src/front_of_house/hosting/mod.rs_（较旧的样式，仍然被支持）  
> 如果你在同一模块中使用这两种样式，将会出现编译错误。  
> 在同一个项目中为不同的模块使用这两种样式是允许的，但这可能会让浏览你的项目的人感到困惑。  
> 使用名为 _mod.rs_ 的文件的这种样式的主要缺点是……项目最终可能会有很多名为`_mod.rs_`的文件，当这些文件同时被打开在编辑器中时，可能会导致混淆。

我们已经将每个模块的代码移动到单独的文件中，而模块结构仍然保持不变。在`eat_at_restaurant`中的函数调用无需任何修改即可正常工作，尽管相关的定义位于不同的文件中。这种技术允许你在模块的大小发生变化时将其移动到新的文件中。

请注意，`src/lib.rs_`中的``pub use crate::front_of_house::hosting``语句也没有发生变化，而``use``对哪些文件被编译为该软件包的一部分也没有任何影响。``mod``关键字用于声明模块，Rust会在与模块名称相同的文件中查找进入该模块的代码。

## 摘要

Rust允许你将一个包拆分为多个子包，再将每个子包拆分成多个模块，这样你就可以从一个模块引用另一个模块中定义的元素。你可以通过指定绝对路径或相对路径来实现这一点。这些路径可以通过``use``语句引入作用域，从而在该作用域内多次使用该元素时可以使用更短的路径。默认情况下，模块代码是私有的，但你可以通过添加``pub``关键字来将其定义公开为公共代码。

在下一章中，我们将介绍一些标准库中的集合数据结构，这些结构可以在你的代码中方便地使用。

[路径]: ch07-03-paths-for-referring-to-an-item-in-the-module-tree.html