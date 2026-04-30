## 处理环境变量

我们将通过添加一个额外功能来改进 `minigrep` 二进制搜索方式：用户可以通过一个环境变量来启用不区分大小写的搜索功能。我们可以将这个功能设置为命令行选项，并要求用户在每次使用它时都进行输入。但通过将这个功能设置为环境变量，用户可以只设置一次环境变量，然后在其使用的所有终端会话中都能实现不区分大小写的搜索。

<!-- Old headings. Do not remove or links may break. -->
<a id="writing-a-failing-test-for-the-case-insensitive-search-function"></a>

### 编写针对不区分大小写的搜索的失败测试

我们首先在 `minigrep` 库中添加一个新的 `search_case_insensitive` 函数。当环境变量有值时，将会调用这个函数。我们将继续遵循 TDD 流程，因此第一步还是编写一个失败的测试。我们将为新的 `search_case_insensitive` 函数添加一个新的测试，并将旧的测试从 `one_result` 更名为 `case_sensitive`，以便明确这两个测试之间的区别，如清单 12-20 所示。

<Listing number="12-20" file-name="src/lib.rs" caption="Adding a new failing test for the case-insensitive function we’re about to add">

```rust,ignore,does_not_compile
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn case_sensitive() {
        let query = "duct";
        let contents = "\
Rust:
safe, fast, productive.
Pick three.
Duct tape.";

        assert_eq!(vec!["safe, fast, productive."], search(query, contents));
    }

    #[test]
    fn case_insensitive() {
        let query = "rUsT";
        let contents = "\
Rust:
safe, fast, productive.
Pick three.
Trust me.";

        assert_eq!(
            vec!["Rust:", "Trust me."],
            search_case_insensitive(query, contents)
        );
    }
}

```

</Listing>

请注意，我们同时也修改了旧测试中的 `contents`。我们添加了一行新的文本，内容为 `"Duct tape."`，并使用了大写的 _D_，这样就不会与查询中的 `"duct"` 产生冲突，尤其是在进行区分大小写的搜索时。通过这种方式修改旧测试，有助于确保我们不会意外破坏已经实现的区分大小写的搜索功能。现在，这个测试应该能够通过，而且在我们继续开发不区分大小写的搜索功能时，它仍然会保持通过状态。

对于这种“不区分大小写”的搜索，新的测试使用了 `"rUsT"` 作为查询条件。在即将添加的 `search_case_insensitive` 函数中，查询 `"rUsT"` 应该能够匹配包含大写 _R_ 的 `"Rust:"` 行，并且也能匹配 `"Trust me."` 行，尽管这两行的大小写与查询条件不同。这是我们的失败测试，因为尚未定义 `search_case_insensitive` 函数，所以测试将无法编译。你可以随意添加一个简单的实现，该实现始终返回一个空向量，类似于我们在 Listing 12-16 中为 `search` 函数所做的处理，这样测试就能编译并失败。

### 实现 `search_case_insensitive` 函数

在清单 12-21 中展示的 `search_case_insensitive` 函数，与 `search` 函数几乎相同。唯一的区别在于，我们将 `query` 和每个 `line` 都转换为小写形式，这样无论输入参数的大小写如何，我们在检查行是否包含查询时，这些参数的大小写都会保持一致。

<Listing number="12-21" file-name="src/lib.rs" caption="Defining the `search_case_insensitive` function to lowercase the query and the line before comparing them">

```rust,noplayground
pub fn search_case_insensitive<'a>(
    query: &str,
    contents: &'a str,
) -> Vec<&'a str> {
    let query = query.to_lowercase();
    let mut results = Vec::new();

    for line in contents.lines() {
        if line.to_lowercase().contains(&query) {
            results.push(line);
        }
    }

    results
}

```

</Listing>

首先，我们将`query`字符串转换为小写，并将其存储在一个同名的新变量中，从而覆盖原来的`query`。在查询中调用`to_lowercase`是必要的，这样无论用户的查询是`"rust"`、`"RUST"`、`"Rust"`还是`"rUsT"`，我们都会将查询视为`"rust"`来处理，从而不会受到大小写的影响。虽然`to_lowercase`可以处理基本的Unicode问题，但它并不能保证100%的准确性。如果我们是在编写实际的应用程序，我们会在这里做更多的工作，但这一部分是关于环境变量的，而不是Unicode的，所以在这里我们就先不处理这个问题了。

请注意，`query`现在变成了`String`，而不是字符串切片。因为调用`to_lowercase`会创建新的数据，而不是引用现有的数据。以`"rUsT"`为例：那个字符串切片中不包含我们可以使用的小写字母`u`或`t`，因此我们必须分配一个新的`String`来包含`"rust"`。当我们现在将`query`作为参数传递给`contains`方法时，我们需要添加一个&符号，因为`contains`的签名定义为接受字符串切片。

接下来，我们在每个 `line` 上添加对 `to_lowercase` 的调用，以将所有字符转换为小写。现在，我们已经将 `line` 和 `query` 转换为小写，那么无论查询的大小写如何，我们都能找到匹配项。

让我们看看这个实现是否能通过测试：

```console
$ cargo test
   Compiling minigrep v0.1.0 (file:///projects/minigrep)
    Finished `test` profile [unoptimized + debuginfo] target(s) in 1.33s
     Running unittests src/lib.rs (target/debug/deps/minigrep-9cd200e5fac0fc94)

running 2 tests
test tests::case_insensitive ... ok
test tests::case_sensitive ... ok

test result: ok. 2 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

     Running unittests src/main.rs (target/debug/deps/minigrep-9cd200e5fac0fc94)

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

   Doc-tests minigrep

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s


```

太好了！他们通过了。现在让我们为从 `run` 函数中派生出的新函数 `search_case_insensitive` 命名。首先，我们需要在 `Config` 结构中添加一个配置选项，以便可以在区分大小写和不区分大小写的搜索之间切换。但是，添加这个字段会导致编译器报错，因为我们还没有在任何地方初始化这个字段。

<span class="filename"> 文件名: src/main.rs</span>

```rust,ignore,does_not_compile
pub struct Config {
    pub query: String,
    pub file_path: String,
    pub ignore_case: bool,
}

```

我们添加了 `ignore_case` 这个字段，它存储一个布尔值。接下来，我们需要 `run` 这个函数来检查 `ignore_case` 字段的值，并根据该值来决定是调用 `search` 函数还是 `search_case_insensitive` 函数，如清单 12-22 所示。不过，目前这段代码仍然无法编译。

<Listing number="12-22" file-name="src/main.rs" caption="Calling either `search` or `search_case_insensitive` based on the value in `config.ignore_case`">

```rust,ignore,does_not_compile
use minigrep::{search, search_case_insensitive};

// --snip--

fn run(config: Config) -> Result<(), Box<dyn Error>> {
    let contents = fs::read_to_string(config.file_path)?;

    let results = if config.ignore_case {
        search_case_insensitive(&config.query, &contents)
    } else {
        search(&config.query, &contents)
    };

    for line in results {
        println!("{line}");
    }

    Ok(())
}

```

</Listing>

最后，我们需要检查环境变量。处理环境变量的函数位于标准库中的 `env` 模块中，该模块已经位于 _src/main.rs_ 文件的顶部。我们将使用 `env` 模块中的 `var` 函数来检查名为 `IGNORE_CASE` 的环境变量是否设置了任何值，如清单 12-23 所示。

<Listing number="12-23" file-name="src/main.rs" caption="Checking for any value in an environment variable named `IGNORE_CASE`">

```rust,ignore,noplayground
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

在这里，我们创建一个新的变量 `ignore_case`。为了设置它的值，我们调用 `env::var` 函数，并传递 `IGNORE_CASE` 环境变量的名称。`env::var` 函数返回一个 `Result`，这个 `Result` 就是成功的 `Ok` 变体，如果环境变量被设置，那么这个 `Result` 就会包含环境变量的值。如果环境变量没有被设置，那么会返回 `Err` 变体。

我们正在使用 `is_ok` 方法来检查 `Result` 中是否设置了环境变量，这意味着程序需要进行不区分大小写的搜索。如果 `IGNORE_CASE` 环境变量没有任何值，那么 `is_ok` 将返回 `false`，程序则需要进行区分大小写的搜索。我们并不关心环境变量的值，只关心它是否被设置或未被设置，因此我们使用 `is_ok` 而不是 `unwrap`、 `expect`，或是我们在 `Result` 中看到的其他方法。

我们将 `ignore_case` 变量中的值传递给 `Config` 实例，这样 `run` 函数就可以读取该值，并决定是否调用 `search_case_insensitive` 或 `search`，正如我们在 Listing 12-22 中实现的那样。

让我们试一试吧！首先，我们将在不设置环境变量且使用查询 `to` 的情况下运行程序。这样的查询应该能够匹配所有包含单词 _to_ 的小写字母行。

```console
$ cargo run -- to poem.txt
   Compiling minigrep v0.1.0 (file:///projects/minigrep)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.0s
     Running `target/debug/minigrep to poem.txt`
Are you nobody, too?
How dreary to be somebody!

```

看起来仍然有效！现在让我们运行程序，将 `IGNORE_CASE` 设置为 `1`，但使用相同的查询 `to`：

```console
$ IGNORE_CASE=1 cargo run -- to poem.txt
```

如果您使用的是 PowerShell，则需要设置环境变量，并将程序作为单独的命令来运行。

```console
PS> $Env:IGNORE_CASE=1; cargo run -- to poem.txt
```

这将使 `IGNORE_CASE` 在您的 shell 会话剩余时间内持续生效。可以使用 `Remove-Item` cmdlet 来取消其生效状态。

```console
PS> Remove-Item Env:IGNORE_CASE
```

我们应该获取包含“to”的行，这些行可能包含大写字母：

<!-- manual-regeneration
cd listings/ch12-an-io-project/listing-12-23
IGNORE_CASE=1 cargo run -- to poem.txt
can't extract because of the environment variable
-->

```console
Are you nobody, too?
How dreary to be somebody!
To tell your name the livelong day
To an admiring bog!
```

太好了，我们还找到了包含“To”的行！我们的 `minigrep` 程序现在可以执行环境变量控制的不区分大小写的搜索。现在您知道了如何使用命令行参数或环境变量来设置选项。

有些程序允许为相同的配置同时使用参数和环境变量。在这种情况下，程序会决定哪个优先。对于另一个自我练习，可以尝试通过命令行参数或环境变量来控制大小写敏感性。如果程序被设置为一个参数使用大小写敏感，另一个参数使用不区分大小写的模式，请判断是参数还是环境变量应该具有优先权。

`std::env`模块包含了许多用于处理环境变量的实用功能：请查阅其文档以了解可用的功能。