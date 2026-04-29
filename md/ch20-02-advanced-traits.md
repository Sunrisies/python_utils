## 高级特性

我们在第10章的[“使用特质定义共享行为”][traits]<!-- ignore -->部分首先介绍了特质的相关内容，但当时并没有讨论那些更高级的细节。现在，既然您对Rust有了更多的了解，我们就可以深入讨论这些细节了。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="在特质定义中指定占位符类型与关联类型"></a>
<a id="关联类型"></a>

### 定义具有关联类型的特性

“关联类型”将一个类型占位符与某个特质连接起来，使得该特质的メソッド定义可以在其签名中使用这些占位符类型。特质的实现者会指定要使用的具体类型，而不是占位符类型。这样，我们可以定义一个使用某些类型的特质，而无需在特质被实现之前就确切知道这些类型是什么。

在本章中，我们描述了大多数高级功能，认为它们很少被需要。而相关类型则处于中间位置：它们的使用频率低于书中其他部分所介绍的功能，但比本章讨论的许多其他功能更为常见。

一个具有相关类型的特性示例是标准库提供的`Iterator`特性。该相关类型的名称是`Item`，它代表了实现`Iterator`特性的类型所遍历的值的类型。`Iterator`特性的定义如清单20-13所示。

<列表编号="20-13" 标题="定义`Iterator`特性，该特性关联的类型为`Item`">

```rust,noplayground
{{#rustdoc_include ../listings/ch20-advanced-features/listing-20-13/src/lib.rs}}
```

</清单>

类型 ``Item`` 是一个占位符，而 ``next`` 方法的定义表明它将返回类型为 ``Option<Self::Item>`` 的值。实现 ``Iterator`` 特性的开发者将指定 ``Item`` 的具体类型，而 ``next`` 方法将返回一个包含该具体类型的值的 ``Option``。

关联类型看起来与泛型概念类似，因为泛型允许我们定义函数，而不需要指定该函数可以处理哪些类型。为了探讨这两个概念之间的区别，我们将观察一个名为`Counter`的类型上`Iterator` trait的实现，该实现指定了`Item`类型就是`u32`。

<listing file-name="src/lib.rs">

```rust,ignore
{{#rustdoc_include ../listings/ch20-advanced-features/no-listing-22-iterator-on-counter/src/lib.rs:ch19}}
```

</清单>

这种语法似乎与泛型语法相当。那么，为什么不直接像清单20-14中所展示的那样，使用泛型来定义`Iterator`特性呢？

<列表编号="20-14" 标题="使用泛型对`Iterator`特性进行假设性定义">

```rust,noplayground
{{#rustdoc_include ../listings/ch20-advanced-features/listing-20-14/src/lib.rs}}
```

</清单>

区别在于，在使用泛型时，如清单20-14所示，我们必须为每个实现注解类型；因为我们可以实现`Iterator<String> for Counter`或任何其他类型，所以我们可以为`Counter`实现多个`Iterator`的实例。换句话说，当一个特质具有泛型参数时，可以为该类型多次实现它，每次都会改变泛型类型参数的具体类型。当我们使用泛型时……在`Counter`方法上使用了`next`方法，因此我们需要提供类型注解，以指明想要使用`Iterator`的哪个实现版本。

在使用了关联类型的情况下，我们不需要对类型进行注解，因为我们无法多次实现某个类型的特性。在清单20-13中，当使用关联类型的定义时，我们可以只指定`Item`的类型一次，因为`impl Iterator for Counter`只能出现一次。在每次调用`next`对`Counter`操作时，我们都不需要明确指出我们希望得到的是`u32`值的迭代器。

关联类型也成为该特质契约的一部分：该特质的实现者必须提供一个类型来替代关联的占位符类型。关联类型通常有一个名称，用于描述该类型的用途，因此在API文档中记录关联类型是一个良好的实践。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="default-generic-type-parameters-and-operator-overloading"></a>

### 使用默认通用参数和运算符重载

当我们使用泛型类型参数时，可以为泛型类型指定一个默认的具体类型。这样，如果默认类型足够好，那么 trait 的实现者就不需要再指定具体类型了。当你使用 `<PlaceholderType=ConcreteType>` 语法声明泛型类型时，就可以指定默认类型。

一个使用这种技术的典型例子是**运算符重载**，在这种情况中，你可以针对特定情况自定义某个运算符的行为（例如`+`）。

Rust不允许你创建自己的运算符或重载任意运算符。但是，你可以通过实现与运算符相关的特质来重载`std::ops`中列出的操作及其对应的特质。例如，在Listing 20-15中，我们重载了`+`运算符，用于将两个`Point`实例相加。我们通过在一个`Point`结构上实现`Add`特质来实现这一点。

<列表编号="20-15" 文件名称="src/main.rs" 标题="实现`Add`特性以覆盖`+`运算符，适用于`Point`实例">

```rust
{{#rustdoc_include ../listings/ch20-advanced-features/listing-20-15/src/main.rs}}
```

</清单>

`add`方法将两个`Point`实例的`x`值，以及两个`Point`实例的`y`值相加，从而创建一个新的`Point`。`Add`特性有一个名为`Output`的相关类型，该类型决定了`add`方法返回的类型。

此代码中的默认通用类型属于 ``Add`` 特性。以下是其定义：

```rust
trait Add<Rhs=Self> {
    type Output;

    fn add(self, rhs: Rhs) -> Self::Output;
}
```

这段代码的架构应该比较熟悉：一个带有单个方法的特质，以及一个关联类型。新添加的部分是`Rhs=Self`：这种语法被称为“默认类型参数”。`Rhs`泛型类型参数（简称“右手边”）定义了`add`方法中`rhs`参数的类型。如果我们在实现`Add`特质时不为`Rhs`指定具体的类型，那么……``Rhs``将默认使用``Self``，而``Self``正是我们在``Add``中要实现的类型。

当我们为 `Point` 实现 `Add` 时，我们使用了 `Rhs` 的默认值，因为我们想要添加两个 `Point` 实例。让我们来看一个实现 `Add` 特性的例子，在这个例子中，我们想要自定义 `Rhs` 的类型，而不是使用默认值。

我们有两个结构体，`Millimeters`和`Meters`，它们分别存储不同单位的值。这种在另一个结构体中对现有类型进行封装的做法被称为“新类型模式”，我们在[“使用新类型模式实现外部特征”][newtype]这个章节中对此进行了更详细的介绍。我们希望将毫米单位的值转换为米单位，并且让`Add`能够正确地完成这种转换。我们可以为`Add`实现这个功能。如清单20-16所示，使用`Millimeters`和`Meters`作为`Rhs`。

<列表编号="20-16" 文件名称="src/lib.rs" 标题="在`Millimeters`上实现`Add`特性，以添加`Millimeters`和`Meters`">

```rust,noplayground
{{#rustdoc_include ../listings/ch20-advanced-features/listing-20-16/src/lib.rs}}
```

</清单>

为了添加`Millimeters`和`Meters`，我们需要指定`impl Add<Meters>`来设置`Rhs`类型的参数值，而不是使用默认的`Self`。

您将使用默认类型参数以两种主要方式使用：

1. 在不破坏现有代码的情况下扩展类型  
2. 允许在大部分用户不需要的特定情况下进行自定义

标准库的 ``Add`` 特性正是第二种用途的一个例子：通常，你会添加两个类似的类型，但 ``Add`` 特性提供了更灵活的自定义选项。在 ``Add`` 特性的定义中使用默认类型参数意味着大多数情况下无需指定额外的参数。换句话说，不需要编写一些繁琐的实现代码，这使得该特性更加易于使用。

第一个目的与第二个类似，但方向相反：如果你想向现有的特质添加类型参数，可以为其指定一个默认值，从而在不破坏现有实现代码的情况下扩展该特质的功能。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="用于消除同名方法歧义的全限定语法"></a>
<a id="如何区分同名方法"></a>

### 在同名方法之间进行消歧义

在Rust中，没有任何规定禁止一个特质拥有与另一个特质的方法同名的方法。Rust也不会阻止你在同一个类型上同时实现这两个特质。此外，你也可以直接在具有与特质中的方法相同名称的类型上实现方法。

当调用同名的方法时，你需要告诉Rust你想要使用哪一个方法。请看清单20-17中的代码，我们定义了两个特性，`Pilot`和`Wizard`，这两个特性都包含一个名为`fly`的方法。然后，我们在类型`Human`上实现了这两个特性，而该类型已经实现了一个名为`fly`的方法。每个`fly`方法都有不同的功能。

<Listing number="20-17" file-name="src/main.rs" caption="定义了两个特性，它们具有`fly`方法，并且实现于`Human`类型上；此外，`fly`方法直接实现于`Human`上。">

```rust
{{#rustdoc_include ../listings/ch20-advanced-features/listing-20-17/src/main.rs:here}}
```

</清单>

当我们对`Human`的实例调用`fly`时，编译器会默认调用该类型上直接实现的方法，如清单20-18所示。

<列表编号="20-18" 文件名称="src/main.rs" 标题="在`Human`的实例上调用`fly`">

```rust
{{#rustdoc_include ../listings/ch20-advanced-features/listing-20-18/src/main.rs:here}}
```

</清单>

运行这段代码会打印出`*waving arms furiously*`，这表明Rust直接调用了在`Human`上实现的`fly`方法。

要从`Pilot`特征或`Wizard`特征中调用`fly`方法，我们需要使用更明确的语法来指定我们指的是哪个`fly`方法。清单20-19展示了这种语法。

<列表编号="20-19" 文件名称="src/main.rs" 标题="指定要调用哪个特性的`fly`方法">

```rust
{{#rustdoc_include ../listings/ch20-advanced-features/listing-20-19/src/main.rs:here}}
```

</清单>

在方法名称之前指定该特性名称，可以明确告诉Rust我们希望调用的是`fly`的哪个实现。我们也可以写成`Human::fly(&person)`，这与我们在Listing 20-19中使用的`person.fly()`是等效的，但如果不需要消除歧义的话，这种方式会稍微长一些。

运行这段代码会输出以下内容：

```console
{{#include ../listings/ch20-advanced-features/listing-20-19/output.txt}}
```

因为`fly`方法接受一个`self`参数，如果我们有两个类型都实现了某个特征，那么Rust可以根据`self`的类型来决定使用哪个实现方式。

然而，那些不是方法的关联函数并没有`self`参数。当存在多个类型或特性定义了具有相同函数名称的非方法函数时，Rust并不总是能够知道你所指的是哪种类型，除非你使用完全限定的语法。例如，在清单20-20中，我们为一家动物收容所创建了一个特性，该特性希望将所有幼犬命名为“Spot”。我们创建了一个带有非方法函数`baby_name`的`Animal`特性。`Animal` 特性是为结构体 `Dog` 实现的，我们还直接为它提供了一个关联的非方法函数 `baby_name`。

<列表编号="20-20" 文件名称="src/main.rs" 标题="一个带有相关函数的特质，以及一个具有相同名称的函数且也实现了该特质的类型">

```rust
{{#rustdoc_include ../listings/ch20-advanced-features/listing-20-20/src/main.rs}}
```

</清单>

我们在与`Animal`特征相关的`baby_name`函数中实现了对所有幼犬的命名，这些代码被定义在`Dog`上。`Dog`类型还实现了`Animal`特征，该特征描述了所有动物的共同特性。幼犬被称为“puppy”，这一点在`baby_name`函数中对`Dog`的`Animal`特征的实现中得到了体现。

在`main`中，我们调用了`Dog::baby_name`这个函数，而该函数直接调用了在`Dog`上定义的相关函数。这段代码会输出以下内容：

```console
{{#include ../listings/ch20-advanced-features/listing-20-20/output.txt}}
```

这个输出并不是我们想要的。我们希望调用的是`baby_name`这个函数，这个函数属于我们在`Dog`上实现的`Animal`特性，这样代码就会打印出`A baby dog is called a puppy`。在Listing 20-19中使用的指定特性的方法在这里并不起作用；如果我们把`main`改为Listing 20-21中的代码，就会遇到编译错误。

<列表编号="20-21" 文件名称="src/main.rs" 标题="尝试从`Animal`特征中调用`baby_name`函数，但Rust不知道应该使用哪个实现">

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch20-advanced-features/listing-20-21/src/main.rs:here}}
```

</清单>

因为 ``Animal::baby_name`` 没有 ``self`` 参数，而且可能还有其他类型实现了 ``Animal`` 特性，因此Rust无法确定我们想要的是哪种实现 ``Animal::baby_name``。我们将会收到这个编译器错误：

```console
{{#include ../listings/ch20-advanced-features/listing-20-21/output.txt}}
```

为了消除歧义，并告诉Rust我们希望在`Dog`中使用`Animal`的实现，而不是在某种其他类型上使用`Animal`的实现，我们需要使用完全限定的语法。清单20-22展示了如何使用完全限定的语法。

<列表编号="20-22" 文件名称="src/main.rs" 标题="使用完全限定语法来指定我们希望从在 `Dog` 上实现的 `Animal` 特质中调用 `baby_name` 函数">

```rust
{{#rustdoc_include ../listings/ch20-advanced-features/listing-20-22/src/main.rs:here}}
```

</清单>

我们为Rust提供了类型注解，这些注解位于尖括号内，表示我们希望调用来自``Animal``特质中的``baby_name``方法，并且希望将``Dog``类型视为``Animal``来调用该函数。这样，代码现在就能输出我们想要的结果了。

```console
{{#include ../listings/ch20-advanced-features/listing-20-22/output.txt}}
```

一般来说，完全限定的语法定义如下：

```rust,ignore
<Type as Trait>::function(receiver_if_method, next_arg, ...);
```

对于不是方法的关联函数，就不会有 ``receiver`` 这个属性：只会列出其他参数。你可以在任何调用函数或方法的地方使用完全限定的语法。不过，你可以省略那些Rust能够从程序中的其他信息中推断出来的部分。只有在存在多个实现且它们使用相同的名称，并且Rust需要帮助的情况下，才需要使用这种更冗长的语法。用于确定要调用哪种实现。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="使用超级特性来在另一个特性中实现单一特性的功能"></a>

### 使用超级特征

有时候，你可能会编写一个依赖于另一个特征的 trait 定义：为了让一个类型实现第一个特征，你需要要求该类型也必须实现第二个特征。这样做是为了让你的 trait 定义能够利用第二个特征中的相关内容。你所依赖的那个特征被称为你的 trait 的 _超 trait_。

例如，假设我们想要创建一个名为`OutlinePrint`的特质，该特质包含一个名为`outline_print`的方法，该方法会打印出一个格式化的数值，该数值用星号括起来。也就是说，给定一个实现了标准库特质`Display`的`Point`结构体，其最终结果为`(x, y)`。当我们对一个具有`1`作为`x`以及`3`作为`y`的`Point`实例调用`outline_print`方法时，就会实现上述功能。应该打印以下内容：

```text
**********
*        *
* (1, 3) *
*        *
**********
```

在实现`outline_print`方法时，我们希望使用`Display`特性的功能。因此，我们需要指定`OutlinePrint`特性仅适用于那些同时实现了`Display`并且提供了`OutlinePrint`所需功能的类型。我们可以通过在特性定义中指定`OutlinePrint: Display`来实现这一点。这种技术类似于为某个特性添加了一个绑定到该特性的特性。列表20-23展示了这一过程。`OutlinePrint` trait的实现。

<列表编号="20-23" 文件名称="src/main.rs" 标题="实现需要调用`Display`功能的`OutlinePrint`特性">

```rust
{{#rustdoc_include ../listings/ch20-advanced-features/listing-20-23/src/main.rs:here}}
```

</清单>

因为我们已经指定了`OutlinePrint`需要`Display`特性，所以我们可以使用`to_string`这个函数。这个函数会自动为任何实现了`Display`类型的类型而实现。如果我们尝试在没有加上冒号的情况下使用`to_string`，并且不在特性名称后指定`Display`特性，那么就会出错，提示在当前的范围内没有找到名为`to_string`的方法，适用于`&Self`类型。

让我们看看，当我们在没有实现 `Display` 的类型上尝试实现 `OutlinePrint` 时会发生什么，比如 `Point` 结构体。

<listing file-name="src/main.rs">

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch20-advanced-features/no-listing-02-impl-outlineprint-for-point/src/main.rs:here}}
```

</清单>

我们遇到了这样一个错误：提示`Display`是必需的，但是尚未实现。

```console
{{#include ../listings/ch20-advanced-features/no-listing-02-impl-outlineprint-for-point/output.txt}}
```

为了解决这个问题，我们在`Point`上实现了`Display`，并满足了`OutlinePrint`所要求的约束条件。

<listing file-name="src/main.rs">

```rust
{{#rustdoc_include ../listings/ch20-advanced-features/no-listing-03-impl-display-for-point/src/main.rs:here}}
```

</清单>

那么，在 `Point` 上实现 `OutlinePrint` 特性后，编译将会成功。然后我们可以在一个 `Point` 实例上调用 `outline_print`，将其显示在星号组成的标题内。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="使用新类型模式来实现外部类型上的外部特性"></a>

### 使用Newtype模式实现外部特征

在第十章的[“在类型上实现特质”][implementing-a-trait-on-a-type]<!--ignore -->部分中，我们提到了“孤儿规则”，即我们只可以在该类型本身或其特质属于我们自己的库的情况下，才可以在该类型上实现特质。不过，可以使用新类型模式来绕过这一限制，该模式涉及在结构体中使用元组结构来创建新的类型。（我们在[“使用元组结构创建不同的类型”]中已经介绍过元组结构。）在第五章的“元组结构”部分中有所介绍。元组结构包含一个字段，它是对我们要实现特性的类型的一个轻量级包装。这样一来，这个包装类型就只存在于我们的项目中，我们可以在包装类型上实现该特性。_Newtype_是一个源自Haskell编程语言的术语。使用这种模式并不会对运行性能产生任何影响，而且包装类型在编译时会被省略。

例如，假设我们希望在`Vec<T>`上实现`Display`功能，但由于孤儿规则的限制，我们无法直接进行这样的操作，因为`Display`属性和`Vec<T>`类型是在我们的库之外定义的。我们可以创建一个`Wrapper`结构体，其中包含一个`Vec<T>`的实例；然后，我们可以在`Wrapper`上实现`Display`功能，并使用`Vec<T>`的值，如清单20-24所示。

<列表编号="20-24" 文件名称="src/main.rs" 标题="在`Vec<String>`周围创建`Wrapper`类型以实现`Display`">

```rust
{{#rustdoc_include ../listings/ch20-advanced-features/listing-20-24/src/main.rs}}
```

</清单>

实现`Display`时，使用`self.0`来访问内部的`Vec<T>`。因为`Wrapper`是一个元组结构，而`Vec<T>`是元组中索引为0的元素。然后，我们可以利用`Display`特性对`Wrapper`进行操作。

使用这种技术的缺点是，``Wrapper``是一种新的类型，因此它不具备其所存储的值所具有的方法。我们必须直接在``Wrapper``上实现``Vec<T>``的所有方法，这样这些方法就可以委托给``self.0``，从而让我们能够像对待``Vec<T>``一样处理``Wrapper``。如果我们希望这种新类型拥有内部类型所拥有的所有方法，那么就需要这样做。在`Wrapper`上实现`Deref`特性，以返回内部类型，这可能是一个解决方案（我们在第15章的“将智能指针视为普通引用”部分讨论过如何实现`Deref`特性）。如果我们不希望`Wrapper`类型拥有内部类型的所有方法——例如，为了限制`Wrapper`类型的功能……行为方面——我们需要手动实现那些我们真正需要的方法。

这种新类型模式即使在没有使用特质的情况下也很有用。让我们转移一下注意力，看看一些高级的方式来与Rust的类型系统进行交互。

[新类型]: ch20-02-advanced-traits.html#implementing-external-traits-with-the-newtype-pattern  
[在类型上实现特性]: ch10-02-traits.html#implementing-a-trait-on-a-type  
[特性]: ch10-02-traits.html  
[智能指针解引用]: ch15-02-deref.html#treating-smart-pointers-like-regular-references  
[元组结构]: ch05-01-defining-structs.html#creating-different-types-with-tuple-structs