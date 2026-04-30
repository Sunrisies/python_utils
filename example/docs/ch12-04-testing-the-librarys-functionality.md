<!-- Old headings. Do not remove or links may break. -->
<a id="developing-the-librarys-functionality-with-test-driven-development"></a>

## 通过测试驱动开发增添功能

现在，我们已经在`_src/lib.rs_`中分离出了与`main`函数的搜索逻辑，因此编写代码核心功能的测试变得更加容易了。我们可以直接使用各种参数调用函数，并检查返回值，而无需通过命令行调用我们的二进制文件。

在本节中，我们将使用测试驱动开发（TDD）流程，按照以下步骤将搜索逻辑添加到 `minigrep` 程序中：

1. 编写一个会失败的测试，并运行它，以确保测试因你预期的原因而失败。
2. 编写或修改适量的代码，使新的测试能够通过。
3. 对刚刚添加或修改的代码进行重构，并确保测试仍然能够通过。
4. 重复步骤1！

虽然TDD只是编写软件的方法之一，但它可以帮助推动代码设计的发展。在编写能够通过这些测试的代码之前先编写测试，有助于在整个过程中保持较高的测试覆盖率。

我们将测试一下实现这一功能的过程，该功能能够在实际中搜索文件内容中的查询字符串，并生成与查询字符串匹配的行列表。我们将把这个功能添加到一个名为`search`的函数中。

### 编写失败测试

在`_src/lib.rs_`文件中，我们将添加一个 `tests` 模块，并为其添加一个测试函数，就像在[第11章][ch11-anatomy]<!-- ignore -->中所做的那样。这个测试函数指定了我们希望 `search` 函数具有的行为：它会接收一个查询以及需要搜索的文本，然后仅返回包含该查询的文本中的行。列表12-15展示了这个测试函数。

<Listing number="12-15" file-name="src/lib.rs" caption="Creating a failing test for the `search` function for the functionality we wish we had">

```rust,ignore,does_not_compile
// --snip--

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn one_result() {
        let query = "duct";
        let contents = "\
Rust:
safe, fast, productive.
Pick three.";

        assert_eq!(vec!["safe, fast, productive."], search(query, contents));
    }
}

```

</Listing>

该测试旨在查找字符串 `"duct"`。我们搜索的文本共有三行，其中只有一行包含 `"duct"`（注意，双引号后的反斜杠告诉Rust不要在该字符串字面量的开头添加新行字符）。我们断言，从 `search` 函数返回的值中只包含我们期望的那一行内容。

如果我们运行这个测试，目前会失败，因为 `unimplemented!` 宏在调用时会出现“未实现”的错误提示。根据TDD原则，我们将采取一个小步骤来添加足够的代码，使得在调用该函数时测试不会出现错误。具体来说，我们通过定义 `search` 函数，使其始终返回一个空向量，如清单12-16所示。这样，测试应该能够编译出来，但由于空向量与包含 `"safe,
fast, productive."` 行的向量不匹配，测试仍然会失败。

<Listing number="12-16" file-name="src/lib.rs" caption="Defining just enough of the `search` function so that calling it won’t panic">

```rust,noplayground
pub fn search<'a>(query: &str, contents: &'a str) -> Vec<&'a str> {
    vec![]
}

```

</Listing>

现在让我们讨论一下，为什么我们需要在 `search` 的签名中明确定义一个显式的 lifetime `'a`，并且将这个 lifetime 与 `contents` 的参数以及返回值一起使用。回想一下在[第10章][ch10-lifetimes]<!-- ignore -->中， lifetime 参数指定了哪个参数的 lifetime 与返回值的 lifetime 相关联。在这种情况下，我们表示返回的向量应该包含引用参数 `contents` 中切片中的字符串切片的切片（而不是引用参数 `query` 中的切片）。

换句话说，我们告诉Rust，`search`函数返回的数据将一直存在，直到`contents`参数中传递给`search`函数的数据被销毁为止。这一点非常重要！只有通过切片引用的数据才具有有效性；如果编译器认为我们是在使用`query`而不是`contents`进行字符串切片操作，那么它的安全检查就会出错。

如果我们忘记使用生命周期注释，然后尝试编译这个函数，就会遇到这个错误：

```console
$ cargo build
   Compiling minigrep v0.1.0 (file:///projects/minigrep)
error[E0106]: missing lifetime specifier
 --> src/lib.rs:1:51
  |
1 | pub fn search(query: &str, contents: &str) -> Vec<&str> {
  |                      ----            ----         ^ expected named lifetime parameter
  |
  = help: this function's return type contains a borrowed value, but the signature does not say whether it is borrowed from `query` or `contents`
help: consider introducing a named lifetime parameter
  |
1 | pub fn search<'a>(query: &'a str, contents: &'a str) -> Vec<&'a str> {
  |              ++++         ++                 ++              ++

For more information about this error, try `rustc --explain E0106`.
error: could not compile `minigrep` (lib) due to 1 previous error

```

Rust无法知道我们需要哪个参数来生成输出结果，因此我们必须明确指定这个参数。请注意，帮助文本建议为所有参数和输出类型指定相同的生命周期参数，但这是不正确的！因为`contents`这个参数包含了我们所有的文本，而我们希望返回的是与这些文本相匹配的部分，所以我们知道`contents`这个参数才应该通过生命周期语法与返回值关联起来。

其他编程语言并不要求你将参数与签名中的返回值进行连接，但随着时间的推移，这种做法会变得更加简单。你可以将这个例子与第10章中“使用生命周期验证引用”部分的例子进行比较。

### 编写代码以通过测试

目前，我们的测试失败了，因为我们总是返回一个空的向量。为了修复这个问题并实现 `search`，我们的程序需要按照以下步骤进行：

1. 遍历内容的每一行。
2. 检查该行是否包含我们的查询字符串。
3. 如果包含，则将其添加到我们返回的值列表中。
4. 如果不包含，则不执行任何操作。
5. 返回匹配的结果列表。

让我们逐步进行，首先从遍历行开始。

#### 使用 `lines` 方法遍历行

Rust 提供了一种方便的方法来处理字符串的逐行迭代，该方法被命名为 `lines`，其实现方式如清单 12-17 所示。请注意，目前这个代码还无法编译。

<Listing number="12-17" file-name="src/lib.rs" caption="Iterating through each line in `contents`">

```rust,ignore,does_not_compile
pub fn search<'a>(query: &str, contents: &'a str) -> Vec<&'a str> {
    for line in contents.lines() {
        // do something with line
    }
}

```

</Listing>

`lines`方法返回一个迭代器。我们将在[第13章][ch13-iterators]<!-- ignore -->中详细讨论迭代器。不过请记住，你在[清单3-5][ch3-iter]<!-- ignore -->中看到了这种使用迭代器的方式，其中我们使用了一个带有迭代器的`for`循环，来对集合中的每个元素执行某些操作。

#### 逐行搜索查询内容

接下来，我们将检查当前行是否包含我们的查询字符串。幸运的是，字符串有一个非常有用的方法，名为 `contains`，它可以帮助我们完成这一任务！在 `search` 函数中添加对 `contains` 方法的调用，如清单 12-18 所示。请注意，目前这段代码仍然无法编译。

<Listing number="12-18" file-name="src/lib.rs" caption="Adding functionality to see whether the line contains the string in `query`">

```rust,ignore,does_not_compile
pub fn search<'a>(query: &str, contents: &'a str) -> Vec<&'a str> {
    for line in contents.lines() {
        if line.contains(query) {
            // do something with line
        }
    }
}

```

</Listing>

目前，我们正在逐步完善功能。为了让代码能够编译，我们需要像在函数签名中指示的那样，从函数体内返回一个值。

#### 存储匹配行

为了完成这个函数，我们需要一种方式来存储我们想要返回的匹配行。为此，我们可以在 `for` 循环之前创建一个可变向量，然后调用 `push` 方法来将 `line` 存储到向量中。在 `for` 循环结束后，我们返回这个向量，如清单 12-19 所示。

<Listing number="12-19" file-name="src/lib.rs" caption="Storing the lines that match so that we can return them">

```rust,ignore
// ANCHOR: ch13
pub fn search<'a>(query: &str, contents: &'a str) -> Vec<&'a str> {
    let mut results = Vec::new();

    for line in contents.lines() {
        if line.contains(query) {
            results.push(line);
        }
    }

    results
}
// ANCHOR_END: ch13

```

</Listing>

现在，`search`函数应该只返回包含`query`的行，而我们的测试应该能够通过。让我们运行这个测试吧：

```console
$ cargo test
   Compiling minigrep v0.1.0 (file:///projects/minigrep)
    Finished `test` profile [unoptimized + debuginfo] target(s) in 1.22s
     Running unittests src/lib.rs (target/debug/deps/minigrep-9cd200e5fac0fc94)

running 1 test
test tests::one_result ... ok

test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

     Running unittests src/main.rs (target/debug/deps/minigrep-9cd200e5fac0fc94)

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

   Doc-tests minigrep

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s


```

我们的测试通过了，所以我们知道它是有效的！

此时，我们可以考虑对搜索函数的实现进行重构，同时确保测试仍然能够通过，以保持相同的功能。搜索函数中的代码并不糟糕，但它没有充分利用迭代器的一些有用特性。我们将在[第13章][ch13-iterators]中再次讨论这个例子，届时我们会详细探讨迭代器，并研究如何改进它。

现在整个程序应该可以正常运行了！让我们先尝试使用一个能够从艾米莉·狄金森的诗中返回恰好一行内容的单词：_frog_。

```console
$ cargo run -- frog poem.txt
   Compiling minigrep v0.1.0 (file:///projects/minigrep)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.38s
     Running `target/debug/minigrep frog poem.txt`
How public, like a frog

```

太好了！现在让我们尝试使用一个可以匹配多行的单词，比如`_body_:`

```console
$ cargo run -- body poem.txt
   Compiling minigrep v0.1.0 (file:///projects/minigrep)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.0s
     Running `target/debug/minigrep body poem.txt`
I'm nobody! Who are you?
Are you nobody, too?
How dreary to be somebody!

```

最后，我们需要确保在搜索那些不在诗中出现的单词时，不会出现任何行。例如，像“monomorphization”这样的单词。

```console
$ cargo run -- monomorphization poem.txt
   Compiling minigrep v0.1.0 (file:///projects/minigrep)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.0s
     Running `target/debug/minigrep monomorphization poem.txt`

```

太好了！我们自己开发了一个经典工具的迷你版本，并且学到了很多关于如何构建应用程序的知识。我们还了解了一些关于文件输入和输出、生命周期、测试以及命令行解析的知识。

为了完成这个项目，我们将简要演示如何操作环境变量以及如何将输出打印到标准错误输出。在编写命令行程序时，这两点都非常有用。

[validating-references-with-lifetimes]: ch10-03-lifetime-syntax.html#validating-references-with-lifetimes
[ch11-anatomy]: ch11-01-writing-tests.html#the-anatomy-of-a-test-function
[ch10-lifetimes]: ch10-03-lifetime-syntax.html
[ch3-iter]: ch03-05-control-flow.html#looping-through-a-collection-with-for
[ch13-iterators]: ch13-02-iterators.html
