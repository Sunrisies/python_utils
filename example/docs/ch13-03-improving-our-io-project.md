## 改进我们的I/O项目

通过了解迭代器这一新知识，我们可以在第12章的I/O项目中运用迭代器，使代码中的部分内容更加清晰简洁。让我们来看看迭代器如何改进我们对`Config::build`函数和`search`函数的实现。

### 使用迭代器删除 `clone`

在 Listing 12-6 中，我们添加了代码，该代码接收一个 `String` 类型的切片，并通过索引切片和克隆值来创建 `Config` 结构的实例，从而使 `Config` 结构能够拥有这些值。在 Listing 13-17 中，我们复现了 `Config::build` 函数的实现，其实现方式与 Listing 12-23 中的相同。

<Listing number="13-17" file-name="src/main.rs" caption="Reproduction of the `Config::build` function from Listing 12-23">

```rust,ignore
impl Config {
    fn build(args: &[String]) -> Result<Config, &'static str> {
        if args.len() < 3 {
            return Err("not enough arguments");
        }

        let query = args[1].clone();
        let file_path = args[2].clone();

        let ignore_case = env::var("IGNORE_CASE").is_ok();

        Ok(Config {
            query,
            file_path,
            ignore_case,
        })
    }
}

```

</Listing>

当时，我们表示不必担心那些效率低的 `clone` 调用，因为我们将在未来移除它们。不过，现在就是那个时刻了！

在这里我们需要使用 `clone`，因为参数 `args` 包含一个包含 `String` 元素的切片，但 `build` 函数并不拥有 `args`。为了返回 `Config` 实例的所有权，我们必须从 `Config` 的 `query` 和 `file_path` 字段中克隆值，这样 `Config` 实例就可以拥有这些值了。

通过我们对迭代器的新了解，我们可以将 `build` 函数修改为：将迭代器作为参数传递，而不是借用一个切片。我们将使用迭代器功能，而不是那些用于检查切片长度并索引到特定位置的代码。这样就能明确 `Config::build` 函数的具体作用，因为迭代器会直接访问这些值。

一旦 `Config::build` 接管了迭代器，并停止使用需要借用的索引操作，我们就可以将 `String` 的值从迭代器中转移到 `Config` 中，而不是调用 `clone` 并重新分配内存。

#### 直接使用返回的迭代器

请打开您的I/O项目的`_src/main.rs_`文件，该文件应该看起来像这样：

<span class="filename"> 文件名: src/main.rs</span>

```rust,ignore
fn main() {
    let args: Vec<String> = env::args().collect();

    let config = Config::build(&args).unwrap_or_else(|err| {
        eprintln!("Problem parsing arguments: {err}");
        process::exit(1);
    });

    // --snip--
}

```

我们首先将 Listing 12-24 中使用的 `main` 函数的起始部分替换为 Listing 13-18 中的代码。这次，该代码使用了迭代器。不过，在更新 `Config::build` 之前，这段代码是无法编译的。

<Listing number="13-18" file-name="src/main.rs" caption="Passing the return value of `env::args` to `Config::build`">

```rust,ignore,does_not_compile
fn main() {
    let config = Config::build(env::args()).unwrap_or_else(|err| {
        eprintln!("Problem parsing arguments: {err}");
        process::exit(1);
    });

    // --snip--
}

```

</Listing>

`env::args`函数返回一个迭代器！与其将迭代器的值收集到向量中，然后再将切片传递给`Config::build`，现在我们直接将从`env::args`返回的迭代器的所有权传递给`Config::build`。

接下来，我们需要更新 `Config::build` 的定义。让我们将 `Config::build` 的签名改为 Listing 13-19 中的样子。不过，这样仍然无法编译，因为我们需要更新函数的主体代码。

<Listing number="13-19" file-name="src/main.rs" caption="Updating the signature of `Config::build` to expect an iterator">

```rust,ignore,does_not_compile
impl Config {
    fn build(
        mut args: impl Iterator<Item = String>,
    ) -> Result<Config, &'static str> {
        // --snip--

```

</Listing>

标准库中关于 `env::args` 函数的文档表明，该函数返回的迭代器的类型属于 `std::env::Args` 类型，并且该类型实现了 `Iterator` 特性，同时返回的是 `String` 类型的值。

我们已经更新了 `Config::build` 函数的签名，使得参数 `args` 具有带有 `impl Iterator<Item =
String>`  trait 约束的通用类型，而不是 `&[String]`。我们在第10章的[“使用特质作为参数”][impl-trait]<!-- ignore --> 部分讨论过 `impl Trait` 语法的这种用法，这意味着 `args` 可以是任何实现了 `Iterator` 特质并返回 `String` 项的类型。

因为我们将负责处理 `args`，并且会通过迭代来修改 `args`，所以我们可以在 `args` 参数的规范中添加 `mut` 关键字，使其变为可变的。

<!-- Old headings. Do not remove or links may break. -->

<a id="using-iterator-trait-methods-instead-of-indexing"></a>

#### 使用 `Iterator` 特性方法

接下来，我们将修复 `Config::build` 的主体代码。由于 `args` 实现了 `Iterator` 特性，我们知道可以调用 `next` 方法！列表 13-20 更新了列表 12-23 中的代码，使其使用 `next` 方法。

<Listing number="13-20" file-name="src/main.rs" caption="Changing the body of `Config::build` to use iterator methods">

```rust,ignore,noplayground
impl Config {
    fn build(
        mut args: impl Iterator<Item = String>,
    ) -> Result<Config, &'static str> {
        args.next();

        let query = match args.next() {
            Some(arg) => arg,
            None => return Err("Didn't get a query string"),
        };

        let file_path = match args.next() {
            Some(arg) => arg,
            None => return Err("Didn't get a file path"),
        };

        let ignore_case = env::var("IGNORE_CASE").is_ok();

        Ok(Config {
            query,
            file_path,
            ignore_case,
        })
    }
}

```

</Listing>

请注意，`env::args`返回值的第一个值是程序的名称。我们不想理会这个值，而是想要获取下一个值。因此，我们首先调用`next`，而不处理其返回值。接着，我们调用`next`来获取想要放入`query`字段中的值。如果`next`返回`Some`，我们就使用`match`来提取该值。如果它返回`None`，那就意味着提供的参数不足，此时我们会提前返回，使用`Err`作为返回值。对于`file_path`的值，我们也执行同样的操作。

<!-- Old headings. Do not remove or links may break. -->

<a id="making-code-clearer-with-iterator-adapters"></a>

### 使用迭代器适配器来阐明代码

我们还可以利用 `search` 函数中的迭代器，这一功能在我们的 I/O 项目中得到了应用。该函数的实现如清单 13-21 所示，与清单 12-19 中的实现一致。

<Listing number="13-21" file-name="src/lib.rs" caption="The implementation of the `search` function from Listing 12-19">

```rust,ignore
pub fn search<'a>(query: &str, contents: &'a str) -> Vec<&'a str> {
    let mut results = Vec::new();

    for line in contents.lines() {
        if line.contains(query) {
            results.push(line);
        }
    }

    results
}

```

</Listing>

我们可以使用迭代器适配器方法以更简洁的方式编写这段代码。这样做还可以避免使用可变的中间状态 `results` vector。函数式编程风格倾向于最小化可变状态的数量，以使代码更加清晰。去除可变状态可能会为未来的改进提供机会，使得搜索操作能够并行进行，因为我们不必管理对 `results` vector 的并发访问。列表13-22展示了这一改动。

<Listing number="13-22" file-name="src/lib.rs" caption="Using iterator adapter methods in the implementation of the `search` function">

```rust,ignore
pub fn search<'a>(query: &str, contents: &'a str) -> Vec<&'a str> {
    contents
        .lines()
        .filter(|line| line.contains(query))
        .collect()
}

```

</Listing>

请记住，`search`函数的目的是返回所有包含`query`的`contents`中的行。类似于清单13-16中的`filter`示例，这段代码使用`filter`适配器来仅保留那些由`line.contains(query)`返回`true`的行。然后，我们使用`collect`将匹配的行收集到另一个向量中。真是简单多了！你也可以对`search_case_insensitive`函数中的迭代器方法进行同样的修改。

为了进一步改进，可以通过删除 `collect` 的调用并将返回类型改为 `impl
Iterator<Item = &'a str>`，从 `search` 函数中返回一个迭代器，从而使该函数成为一个迭代器适配器。请注意，您还需要更新测试代码！在做出这个更改之前和之后，使用您的 `minigrep` 工具检查整个文件，以观察行为的差异。在做出这个更改之前，程序不会打印任何结果，直到收集完所有结果为止；而在更改之后，每当找到匹配的行时，结果就会被打印出来，因为 `for` 循环在 `run` 函数中能够利用迭代器的惰性特性。

<!-- Old headings. Do not remove or links may break. -->

<a id="choosing-between-loops-or-iterators"></a>

### 在循环和迭代器之间做出选择

下一个逻辑问题是：在自己的代码中应该选择哪种风格，以及为什么选择这种风格。 Listing 13-21 中的原始实现，还是 Listing 13-22 中使用迭代器的版本呢？（假设我们在返回结果之前先收集所有结果，而不是直接返回迭代器）。大多数 Rust 程序员更喜欢使用迭代器风格。一开始可能会有点难以掌握，但一旦你熟悉了各种迭代器适配器及其功能，迭代器就会变得更容易理解。代码不再需要繁琐地处理各种循环逻辑和创建新的向量，而是专注于循环的高层次目标。这样，一些常见的代码可以被抽象掉，从而更容易理解代码中特有的概念，比如迭代器中的每个元素都必须满足的过滤条件。

但是，这两种实现真的等价吗？人们通常会认为，底层循环会更快一些。让我们来讨论一下性能问题。

[impl-trait]: ch10-02-traits.html#traits-as-parameters
