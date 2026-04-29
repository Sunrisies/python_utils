## 改进我们的I/O项目

通过了解迭代器这一新知识，我们可以在第12章的I/O项目中运用迭代器，使代码中的部分内容更加清晰简洁。让我们来看看迭代器如何改进我们对`Config::build`函数和`search`函数的实现。

### 使用迭代器删除一个 `clone`

在清单12-6中，我们添加了代码，该代码获取`String`数组中的值，并通过索引和克隆这些值来创建`Config`结构的实例。这样一来，`Config`结构就可以拥有这些值了。在清单13-17中，我们复现了`Config::build`函数的实现，其内容与清单12-23中的相同。

<Listing number="13-17" file-name="src/main.rs" caption="复制清单12-23中的`Config::build`函数">

```rust,ignore
{{#rustdoc_include ../listings/ch13-functional-features/listing-12-23-reproduced/src/main.rs:ch13}}
```

</ Listing>

当时，我们表示不必担心那些效率低的`clone`调用，因为我们将在未来移除它们。不过，现在就是那个时刻了！

我们需要在这里使用`clone`，因为参数`args`包含一个由`String`个元素组成的切片，而`build`函数并不拥有`args`。为了将`Config`实例的所有权返回给`build`，我们必须从`Config`的`query`和`file_path`字段中克隆这些值，这样`Config`实例才能拥有这些值的所有权。

通过我们对迭代器的新了解，我们可以修改`build`函数，使其将迭代器作为参数来接收，而不是借用一个切片。我们将使用迭代器功能，而不是那些用于检查切片长度并索引到特定位置的代码。这样就能明确`Config::build`函数的具体作用，因为迭代器会直接访问这些值。

一旦 `Config::build` 接管了迭代器的所有权，并且不再使用需要借用的索引操作，我们就可以将 `String` 中的值直接从迭代器中获取，而不是调用 `clone` 来进行新的分配。

#### 直接使用返回的迭代器

打开你的I/O项目的`_src/main.rs_`文件，该文件应该看起来像这样：

<span class="filename">文件名：src/main.rs</span>

```rust,ignore
{{#rustdoc_include ../listings/ch13-functional-features/listing-12-24-reproduced/src/main.rs:ch13}}
```

我们首先将 Listing 12-24 中 `main` 函数的起始部分替换为 Listing 13-18 中的代码。这次，该代码使用了迭代器。在更新 `Config::build` 之前，这段代码无法编译。

<列表编号="13-18" 文件名称="src/main.rs" 标题="将 `env::args` 的返回值传递给 `Config::build`">

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch13-functional-features/listing-13-18/src/main.rs:here}}
```

</ Listing>

`env::args`函数返回一个迭代器！与其将迭代器的值收集到向量中，然后再将切片传递给`Config::build`，我们现在直接将来自`env::args`的迭代器的所有权传递给`Config::build`。

接下来，我们需要更新 `Config::build`的定义。让我们将 `Config::build`的签名改为类似清单13-19所示的形式。不过，这样仍然无法编译成功，因为我们还需要更新函数的主体代码。

<列表编号="13-19" 文件名称="src/main.rs" 标题="更新 `Config::build` 的签名，使其期望接收一个迭代器">

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch13-functional-features/listing-13-19/src/main.rs:here}}
```

</ Listing>

标准库中关于`env::args`函数的文档表明，该函数返回的迭代器的类型就是`std::env::Args`，而且这个类型实现了`Iterator`特性，并且返回的是`String`类型的值。

我们已经更新了 `Config::build` 函数的签名，使得参数 `args` 具有通用类型，并且该类型具备我们曾在第10章的[“使用特质作为参数”][impl-trait]<!-- ignore -->部分讨论过的特性：`impl Iterator<Item = String>` instead of `&[String]`. This usage of the `impl Trait`。这意味着 `args` 可以是任何实现了 `Iterator` 特质并返回 `String` 项的类型。

因为我们将负责 `args` 的所有权，并且会通过遍历 `args` 来对其进行修改，所以我们可以在 `args` 参数的定义中添加 `mut` 这个关键字，使其变为可变的。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="使用迭代器特性方法代替索引操作"></a>

#### 使用 `Iterator` 特质方法

接下来，我们将修复 `Config::build` 的主体代码。由于 `args` 实现了 `Iterator` 特性，我们知道可以对其调用 `next` 方法！清单 13-20 更新了来自清单 12-23 的代码，使其使用 `next` 方法。

<列表编号="13-20" 文件名称="src/main.rs" 标题="将 `Config::build` 中的内容修改为使用迭代器方法">

```rust,ignore,noplayground
{{#rustdoc_include ../listings/ch13-functional-features/listing-13-20/src/main.rs:here}}
```

</ Listing>

请注意，``env::args``返回值的第一个值是程序的名称。我们不想理会这个值，而是想要获取下一个值。因此，我们首先调用``next``，并不处理其返回值。接着，我们调用``next``，以获取想要放入``Config``中``query``字段的值。如果``next``返回``Some``，我们就使用``match``来提取该值。如果它返回``None``，则表示没有提供足够的参数，此时我们会提前返回一个``Err``值。对于``file_path``的值，我们也执行同样的操作。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="使用迭代器适配器使代码更清晰"></a>

### 使用迭代器适配器来阐明代码

我们还可以利用 ``search`` 函数中包含的迭代器，该函数在我们的 I/O 项目中被使用，其代码如清单 13-21 所示，与清单 12-19 中的内容相同。

<Listing number="13-21" file-name="src/lib.rs" caption="实现来自Listing 12-19中的`search`函数">

```rust,ignore
{{#rustdoc_include ../listings/ch12-an-io-project/listing-12-19/src/lib.rs:ch13}}
```

</ Listing>

我们可以使用迭代器适配器方法以更简洁的方式编写这段代码。这样做还可以避免使用可变的``results``向量。函数式编程风格倾向于最小化可变状态的数量，以使代码更加清晰。去除可变状态可能会为未来的改进提供机会，使得搜索操作能够并行进行，因为我们不必再管理对``results``向量的并发访问。清单13-22展示了这一改动。

<Listing number="13-22" file-name="src/lib.rs" caption="在实现 `search` 函数时使用迭代器适配器方法">

```rust,ignore
{{#rustdoc_include ../listings/ch13-functional-features/listing-13-22/src/lib.rs:here}}
```

</ Listing>

请注意，`search`函数的目的是返回`contents`中所有包含`query`的行。类似于清单13-16中的`filter`示例，这段代码使用`filter`适配器来仅保留那些由`line.contains(query)`返回`true`的行。然后，我们通过`collect`将匹配的行收集到另一个向量中。真是简单多了！您也可以对`search_case_insensitive`函数中的迭代器方法进行同样的修改。

为了进一步改进，需要从 ``search`` 函数中返回一个迭代器，方法是移除对 ``collect`` 的调用，并将返回类型改为 `impl Iterator<Item = &'a str>`，这样该函数就变成了一个迭代器适配器。请注意，您还需要更新测试代码！在做出这个更改之前和之后，使用您的 ``minigrep`` 工具来测试整个文件，以观察行为上的差异。在做出这个更改之前，程序不会打印任何结果，直到收集完所有结果为止；但在更改之后，每当找到匹配的行时，结果就会被打印出来，因为 ``for`` 中的循环能够利用迭代器的惰性计算特性。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="选择循环还是迭代器"></a>

### 在循环和迭代器之间做出选择

下一个逻辑问题是：在自己的代码中应该选择哪种风格，以及为什么选择这种风格。是清单13-21中的原始实现方式，还是清单13-22中使用迭代器的方式（假设我们在返回结果之前先收集所有结果，而不是直接返回迭代器）。大多数Rust程序员更喜欢使用迭代器风格。一开始可能会有点难以掌握，但一旦你熟悉了各种迭代器适配器及其功能，迭代器就会变得更容易理解。与其不断调整循环中的各种细节并创建新的向量，不如将代码的重点放在循环的高层次目标上。这样可以将一些常见的代码抽象掉，从而更容易理解这段代码中独有的概念，比如迭代器中的每个元素都必须满足的过滤条件。

但是这两种实现真的等价吗？直观的假设可能是，底层循环会更快一些。让我们来讨论一下性能问题。

[impl-trait]: ch10-02-traits.html#traits-as-parameters