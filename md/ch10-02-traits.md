<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="塑造共同行为的特征"></a>

## 通过特质定义共享行为

**特性**定义了特定类型所具有的功能，并且可以与其他类型共享这些功能。我们可以使用特性来以抽象的方式定义共同的行为。我们还可以通过**特性约束**来指定一个泛型类型可以是任何具有某些行为的类型。

注意：特性与其他语言中常被称为“接口”的功能类似，尽管两者之间存在一些差异。

### 定义特征

一个类型的行为包括我们可以对该类型调用的方法。如果我们可以在所有这些类型上调用相同的方法，那么不同的类型就会具有相同的行为。特质定义是一种将方法签名组合在一起的方式，以定义实现某种目的所需的一系列行为。

例如，假设我们有多个结构体，它们分别存储不同类型和数量的文本：一个`NewsArticle`结构体，用于保存存放在特定位置的新闻报道；另一个`SocialPost`结构体，最多可以包含280个字符，并且带有元数据，用来指示这是新帖子、重复发布还是对另一篇帖子的回复。

我们想要创建一个名为`aggregator`的媒体聚合库，它能够显示存储在`NewsArticle`或`SocialPost`实例中的数据的摘要。为此，我们需要每种类型的摘要，我们将通过调用实例上的`summarize`方法来获取这些摘要。列表10-12展示了实现这一功能的公共`Summary`特性的定义。

<列表编号="10-12" 文件名称="src/lib.rs" 标题="一个由`summarize`方法提供行为的`Summary`特质">

```rust,noplayground
{{#rustdoc_include ../listings/ch10-generic-types-traits-and-lifetimes/listing-10-12/src/lib.rs}}
```

</清单>

在这里，我们使用``trait``关键字声明一个特质，然后是该特质的名称，在本例中为``Summary``。我们还将该特质声明为``pub``，这样依赖于此 crate 的其他 crate 也可以使用这个特质，我们将在几个示例中看到这一点。在花括号内，我们声明了描述实现此特质类型的类型的行为的方法签名，在本例中是``fn summarize(&self) -> String``。

在方法签名之后，我们不使用花括号来提供实现，而是使用分号。每个实现此特性的类型都必须为该方法的定义提供自己的自定义行为。编译器会确保任何具有`Summary`特性的类型都会定义具有该签名的方法`summarize`。

一个特性在其体内可以包含多个方法：这些方法签名每行列出一个，并且每行的末尾都加上分号。

### 在类型上实现特性

现在我们已经定义了`Summary`特性方法的期望签名，接下来可以在我们的媒体聚合器中的类型上实现它。列表10-13展示了在`NewsArticle`结构体上实现`Summary`特性的示例，该结构体使用标题、作者和位置来创建`summarize`的返回值。对于`SocialPost`结构体，我们将`summarize`定义为用户名。随后是帖子的完整内容，前提是帖子的内容已经限制在280个字符以内。

<列表编号="10-13" 文件名称="src/lib.rs" 标题="在 `NewsArticle` 和 `SocialPost` 类型上实现 `Summary` 特性">

```rust,noplayground
{{#rustdoc_include ../listings/ch10-generic-types-traits-and-lifetimes/listing-10-13/src/lib.rs:here}}
```

</清单>

在类型上实现 trait 与实现常规方法类似。不同之处在于，在 `impl` 之后，我们需要输入想要实现的 trait 名称，然后使用 `for` 关键字，接着指定希望实现 trait 的类型名称。在 `impl` 块中，我们需要插入 trait 定义中定义的方法签名。无需在每个签名后面加上分号。在签名部分，我们使用花括号来定义方法体，在其中指定我们希望该特性中的方法对于特定类型所具有的具体行为。

现在，该库已经在`NewsArticle`和`SocialPost`上实现了`Summary`特性。因此，使用该库的用户可以像调用常规方法一样，调用`NewsArticle`和`SocialPost`实例上的特性方法。唯一的区别是，用户必须同时将特性以及相关类型带入作用域中。以下是一个二进制库如何使用我们的`aggregator`库的示例：

```rust,ignore
{{#rustdoc_include ../listings/ch10-generic-types-traits-and-lifetimes/no-listing-01-calling-trait-method/src/main.rs}}
```

这段代码会打印出：`1个新帖子：horse_ebooks：当然，正如你可能已经知道的那样，人们`。

其他依赖于`aggregator` crate的 crate也可以将`Summary` trait引入到其作用域中，以便在它们自己的类型上实现`Summary`。需要注意的是，我们只能在 trait 或者类型本身，或者两者都是属于我们 crate 内部的情况下，才能在某个类型上实现 trait。例如，我们可以在自定义类型如`SocialPost`上实现标准库中的 trait，如`Display`。由于类型`SocialPost`仅存在于我们的`aggregator` crate中，因此我们可以在其上实现`Summary`功能。同样，由于trait `Summary`也仅存在于我们的`aggregator` crate中，我们也可以在`Vec<T>`上实现`aggregator`功能。

但是，我们无法在外部类型上实现外部特性。例如，我们无法在`aggregator`框架内为`Vec<T>`实现`Display`特性，因为`Display`和`Vec<T>`都定义在标准库中，并不属于`aggregator`框架的局部内容。这种限制是_一致性_属性的一部分，更具体地说，就是所谓的_孤儿规则_。父类型不存在。这条规则确保了其他人的代码不会破坏你的代码，反之亦然。如果没有这条规则，两个 crate可能会为同一个类型实现相同的特性，而Rust将无法判断应该使用哪个实现。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="默认实现"></a>

### 使用默认实现

有时候，为某个或某些方法在特质中设置默认行为会很有用，这样就不必为每个类型上的所有方法都提供实现。因此，当我们在一个特定类型上实现这个特质时，我们可以保留或覆盖每个方法的默认行为。

在清单10-14中，我们为`Summary`特性的`summarize`方法指定了一个默认字符串，而不是像在清单10-12中那样只定义方法签名。

<列表编号="10-14" 文件名称="src/lib.rs" 标题="定义带有`summarize`方法默认实现的`Summary`特质">

```rust,noplayground
{{#rustdoc_include ../listings/ch10-generic-types-traits-and-lifetimes/listing-10-14/src/lib.rs:here}}
```

</清单>

为了使用默认实现来总结 `NewsArticle` 的实例，我们需要使用一个空的 `impl` 块，并在其中使用 `impl Summary for NewsArticle {}`。

尽管我们不再直接在`NewsArticle`上定义`summarize`方法，但我们提供了一个默认的实现，并且指定了`NewsArticle`实现了`Summary`特性。因此，我们仍然可以像这样调用`NewsArticle`实例上的`summarize`方法：

```rust,ignore
{{#rustdoc_include ../listings/ch10-generic-types-traits-and-lifetimes/no-listing-02-calling-default-impl/src/main.rs:here}}
```

这段代码会打印出`New article available! (Read more...)`。

创建默认实现并不需要我们在 Listing 10-13 中的 `SocialPost` 对 `Summary` 的实现进行任何修改。因为覆盖默认实现的语法与实现没有默认实现的特征方法的语法是相同的。

默认实现可以调用同一特质中的其他方法，即使那些其他方法没有默认实现。通过这种方式，一个特质可以提供许多有用的功能，而只需要实现者指定其中的一小部分功能。例如，我们可以定义`Summary`特质，使其包含一个`summarize_author`方法，该方法的实现是必需的；然后定义一个`summarize`方法，该方法具有默认实现，该默认实现会调用`summarize_author`方法。

```rust,noplayground
{{#rustdoc_include ../listings/ch10-generic-types-traits-and-lifetimes/no-listing-03-default-impl-calls-other-methods/src/lib.rs:here}}
```

要使用这个版本的`Summary`，我们只需要在一个类型上实现该特性时定义`summarize_author`即可。

```rust,ignore
{{#rustdoc_include ../listings/ch10-generic-types-traits-and-lifetimes/no-listing-03-default-impl-calls-other-methods/src/lib.rs:impl}}
```

在我们定义了`summarize_author`之后，我们可以在`SocialPost`结构的实例上调用`summarize`。而`summarize`的默认实现会调用我们提供的`summarize_author`的定义。由于我们已经实现了`summarize_author`，因此`Summary`特性让我们能够使用`summarize`方法，而无需编写更多的代码。以下是具体的实现方式：

```rust,ignore
{{#rustdoc_include ../listings/ch10-generic-types-traits-and-lifetimes/no-listing-03-default-impl-calls-other-methods/src/main.rs:here}}
```

这段代码会打印出`1 new post: (Read more from @horse_ebooks...)`。

请注意，无法从同一方法的覆盖实现中调用默认实现。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="traits-as-parameters"></a>

### 将特征作为参数使用

现在您已经学会了如何定义和实现特质，我们可以探讨如何利用特质来定义能够接受多种不同类型的数据的函数。我们将使用在 Listing 10-13 中为 `NewsArticle` 和 `SocialPost` 类型实现的 `Summary` 特质，来定义一个 `notify` 函数。该函数在 `item` 参数上调用 `summarize` 方法，而 `item` 参数是一个实现了 `Summary` 接口的类型。特征。为此，我们使用``impl Trait``语法，如下所示：

```rust,ignore
{{#rustdoc_include ../listings/ch10-generic-types-traits-and-lifetimes/no-listing-04-traits-as-parameters/src/lib.rs:here}}
```

与其为`item`参数指定具体的类型，我们更倾向于使用`impl`关键字以及该特性的名称。这个参数可以接受任何实现了该特性的类型。在`notify`的内部，我们可以调用来自`Summary`特性的`item`上的任何方法，比如`summarize`。我们还可以调用`notify`，并传入`NewsArticle`或`SocialPost`的任何实例。调用这些方法的代码就是如此。使用任何其他类型的函数，例如 ``String`` 或 ``i32``，将无法编译，因为这些类型没有实现 ``Summary`` 功能。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="修复具有属性限制的最大函数"></a>

#### 特质绑定语法

`impl Trait`语法适用于简单的情况，但实际上它是更长形式的一种语法糖，这种形式被称为“特质绑定”；其格式如下：

```rust,ignore
pub fn notify<T: Summary>(item: &T) {
    println!("Breaking news! {}", item.summarize());
}
```

这种较长的形式与上一节中的示例相当，但内容更为详细。我们将特性边界与泛型类型参数的声明放在冒号之后，并在尖括号内。

`impl Trait`语法非常方便，在简单的情况下可以使得代码更加简洁。而更完整的trait绑定语法则可以在其他情况下表达更复杂的逻辑。例如，我们可以有两个参数，它们都实现了`Summary`的功能。使用`impl Trait`语法时，这样的实现方式如下所示：

```rust,ignore
pub fn notify(item1: &impl Summary, item2: &impl Summary) {
```

如果我们希望这个函数允许`item1`和`item2`拥有不同的类型（只要这两种类型都实现了`Summary`），那么使用`impl Trait`是合适的。然而，如果我们希望两个参数都具有相同的类型，那么我们必须使用 trait 绑定，如下所示：

```rust,ignore
pub fn notify<T: Summary>(item1: &T, item2: &T) {
```

通用类型 ``T`` 被指定为参数 ``item1`` 和 ``item2`` 的类型。该类型对函数的限制是，作为参数传递给 ``item1`` 和 ``item2`` 的具体类型必须相同。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="使用--语法指定多个属性边界"></a>

#### 使用 ``+`` 语法定义多个属性边界

我们还可以指定多个特征绑定。假设我们希望`notify`使用显示格式，同时`item`上的`summarize`也使用相同的格式：我们可以在`notify`的定义中指定`item`必须同时实现`Display`和`Summary`的功能。我们可以使用`+`语法来实现这一点。

```rust,ignore
pub fn notify(item: &(impl Summary + Display)) {
```

`+`语法在泛型类型的特征边界中也是有效的：

```rust,ignore
pub fn notify<T: Summary + Display>(item: &T) {
```

在指定了这两个特性边界之后，``notify`` 的主体可以调用 ``summarize``，并使用 ``{}`` 来格式化 ``item``。

使用 ``where`` 子句可以更清晰地定义特征边界

使用过多的特性边界有其缺点。每个泛型类型都有自己的特性边界，因此具有多个泛型类型参数的函数可能会在函数名称及其参数列表中包含大量的特性边界信息，这会使函数签名难以阅读。因此，Rust提供了另一种语法，用于在函数签名之后的`where`子句中指定特性边界。所以，与其这样写：

```rust,ignore
fn some_function<T: Display + Clone, U: Clone + Debug>(t: &T, u: &U) -> i32 {
```

我们可以使用一个``where``子句，如下所示：

```rust,ignore
{{#rustdoc_include ../listings/ch10-generic-types-traits-and-lifetimes/no-listing-07-where-clause/src/lib.rs:here}}
```

这个函数的命名更为简洁：函数名、参数列表以及返回类型都紧密排列在一起，类似于那些没有太多特征边界的函数。

### 返回实现了特定特征的类型

我们还可以使用``impl Trait``语法在返回位置返回一个实现了特定特性的值，如下所示：

```rust,ignore
{{#rustdoc_include ../listings/ch10-generic-types-traits-and-lifetimes/no-listing-05-returning-impl-trait/src/lib.rs:here}}
```

通过使用 ``impl Summary`` 作为返回类型，我们指定了 ``returns_summarizable`` 函数返回一个实现了 ``Summary`` 特性的类型，而无需明确具体类型。在这种情况下，``returns_summarizable`` 返回一个 ``SocialPost`` 类型的值，但调用此函数的代码不需要知道这一点。

仅通过函数实现的特质来指定返回类型的能力，在闭包和迭代器的上下文中特别有用。这些内容我们将在第13章中讨论。闭包和迭代器创建的类型只有编译器才知道，或者这些类型的描述非常冗长。`impl Trait`语法允许你简洁地指定一个函数返回实现了`Iterator`特质的某种类型，而无需编写非常冗长的类型描述。

不过，只有当你返回单一类型时才能使用`impl Trait`。例如，这段代码如果返回的是`NewsArticle`或`SocialPost`，并且返回类型的指定为`impl Summary`的话，那么这段代码将无法正常工作。

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch10-generic-types-traits-and-lifetimes/no-listing-06-impl-trait-returns-one-type/src/lib.rs:here}}
```

由于编译器中对`impl Trait`语法的实现存在限制，因此返回`NewsArticle`或`SocialPost`是不允许的。我们将在第十八章的“使用特质对象来抽象共享行为”部分中介绍如何编写具有此类行为的函数。

### 使用特性边界来条件性地实现方法

通过使用与``impl``块相关联的特质，并利用泛型类型参数，我们可以为实现了指定特质的类型有条件地实现方法。例如，清单10-15中的类型``Pair<T>``总是会实现``new``函数，该函数会返回``Pair<T>``的新实例（回想一下第5章的[“MethodSyntax”][methods]<!-- ignore -->章节，``Self``是一种类型）。这里，``impl``类型的别名是``Pair<T>``。但在下一个``impl``块中，``Pair<T>``只有在其内部类型``T``实现了允许进行比较的``PartialOrd``特性，并且实现了允许打印的``Display``特性时，才会实现``cmp_display``方法。

<列表编号="10-15" 文件名称="src/lib.rs" 标题="根据特质边界条件在泛型类型上有条件地实现方法">

```rust,noplayground
{{#rustdoc_include ../listings/ch10-generic-types-traits-and-lifetimes/listing-10-15/src/lib.rs}}
```

</清单>

我们还可以有条件地为一个实现了其他特性的类型实现该特性。对于满足特定约束条件的任何类型，其上的特性实现被称为“泛化实现”，在Rust标准库中得到了广泛应用。例如，标准库会在实现了`Display`特性的任何类型上实现`ToString`特性。标准库中的`impl`代码块看起来类似于以下代码：

```rust,ignore
impl<T: Display> ToString for T {
    // --snip--
}
```

由于标准库提供了这种通用的实现方式，我们可以调用由 `ToString` 特征定义的 `to_string` 方法，而该方法可以应用于任何实现了 `Display` 特征的类型。例如，我们可以将整数转换为相应的 `String` 值，因为整数实现了 `Display` 功能。

```rust
let s = 3.to_string();
```

在文档的“实现者”部分中，可以看到关于该特性的全面实现说明。

`Trait`和`Trait Bound`让我们能够编写使用泛型类型参数的代码，从而减少重复代码，同时向编译器明确说明我们希望该泛型类型具有特定的行为。然后，编译器可以利用`Trait Bound`的信息来确保所有在代码中使用的具体类型都表现出正确的行为。在动态类型语言中，如果我们对一个没有定义该方法的类型调用某个方法，将会在运行时出现错误。但在Rust中则不会这样。这些错误被移到了编译阶段，因此我们不得不在代码运行之前就解决这些问题。此外，我们不必编写在运行时检查行为的代码，因为我们已经在编译阶段进行了检查。这样做可以提高性能，同时又不牺牲泛型的灵活性。

[trait-objects]: ch18-02-trait-objects.html#使用特质对象来抽象共享行为  
[methods]: ch05-03-method-syntax.html#方法语法