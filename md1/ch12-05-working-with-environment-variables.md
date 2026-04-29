## 处理环境变量

我们将在 `minigrep` 二进制文件中添加一个额外功能：提供一个选项，允许用户通过环境变量来启用不区分大小写的搜索功能。我们可以将这个功能作为一个命令行选项，并要求用户在每次需要使用时都手动输入该选项。但通过将该功能设置为环境变量，用户可以只需设置一次环境变量，然后所有搜索操作在该终端会话中都将采用不区分大小写的模式。

<!-- 旧的标题。不要删除，否则链接可能会失效。 -->
<a id="writing-a-failing-test-for-the-case-insensitive-search-function"></a>

### 编写一个用于不区分大小写的搜索的失败测试

我们首先在 `minigrep` 库中添加一个新的 `search_case_insensitive` 函数。当环境变量有值时，将会调用这个函数。我们将继续遵循 TDD 流程，因此第一步还是编写一个失败的测试。我们会为新的 `search_case_insensitive` 函数添加一个新的测试，并将旧的测试从 `one_result` 更名为 `case_sensitive`，以便明确这两个测试之间的区别，如清单 12-20 所示。

<列表编号="12-20" 文件名称="src/lib.rs" 标题="为即将添加的不区分大小写函数添加一个新的失败测试">

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch12-an-io-project/listing-12-20/src/lib.rs:here}}
```

</ Listing>

请注意，我们同时也修改了旧测试中的`contents`。我们添加了一行新的代码，其中包含了`"Duct tape."`的文本，并且使用了大写的_D_符号。然而，在进行区分大小写的搜索时，这个符号不应与查询中的`"duct"`相匹配。通过这种方式修改旧测试，有助于确保不会意外破坏我们已经实现的区分大小写的搜索功能。现在，这个测试应该能够通过，而且在我们继续开发不区分大小写的搜索功能时，它也应该会继续通过。

新的`case-_insensitive_`搜索测试用例使用``"rUsT"``作为查询条件。在即将添加的``search_case_insensitive``函数中，``"rUsT"``应该能够匹配包含``"Rust:"``的行，并且该行中的`_R_`为大写；同时，即使``"Trust me."``行的格式与查询条件不同，该行也应该能够被匹配到。这就是我们的失败测试案例，由于我们尚未定义``search_case_insensitive``函数，因此测试将无法编译成功。你可以随意添加一个简单的实现，该实现始终返回一个空向量，类似于我们在Listing 12-16中的``search``函数所做的那样，以此来观察测试是否能够编译并失败。

### 实现 `search_case_insensitive` 函数

在清单 12-21 中展示的 ``search_case_insensitive`` 函数与 ``search`` 函数几乎相同。唯一的区别在于，我们会将 ``query`` 以及每一个 ``line`` 都转换为小写字母，这样无论输入参数的大小写如何，我们在检查该行是否包含查询词时，都会使用相同的处理方式。

<列表编号="12-21" 文件名称="src/lib.rs" 标题="定义 `search_case_insensitive` 函数，用于将查询字符串中的字母转换为小写，并在比较之前处理该行的内容">

```rust,noplayground
{{#rustdoc_include ../listings/ch12-an-io-project/listing-12-21/src/lib.rs:here}}
```

</ Listing>

首先，我们将 `query` 字符串转换为小写，并将其存储在一个同名的新变量中，从而遮蔽原来的 `query`。在查询上调用 `to_lowercase` 是必要的，这样无论用户的查询是 `"rust"`、`"RUST"`、`"Rust"` 还是 `"rUsT"`，我们都会将查询视为 `"rust"` 来处理，而不会受到大小写的影响。虽然 `to_lowercase` 可以处理基本的 Unicode 问题，但它并不能达到100%的准确性。如果我们是在编写真正的应用程序，我们会在这里做更多的工作，但这一部分是关于环境变量，而不是 Unicode 的问题，所以我们就到此为止吧。

请注意，`query`现在是一个`String`，而不是字符串切片，因为调用`to_lowercase`会创建新的数据，而不是引用现有的数据。以`"rUsT"`为例，那个字符串切片并不包含我们可以用来使用的 lowercase`u`或`t`，因此我们必须分配一个新的`String`来包含`"rust"`。当我们现在将`query`作为参数传递给`contains`方法时，我们需要添加一个安培符号，因为`contains`的签名被定义为接受字符串切片。

接下来，我们在每个 `line` 上调用 `to_lowercase`，将所有字符转换为小写。现在，由于我们已经将 `line` 和 `query` 转换为小写，无论查询字符串的大小写如何，我们都能找到匹配项。

让我们看看这个实现是否能通过测试：

```console
{{#include ../listings/ch12-an-io-project/listing-12-21/output.txt}}
```

太好了！他们通过了。现在让我们调用来自`run`函数的新`search_case_insensitive`函数。首先，我们需要在`Config`结构中添加一个配置选项，以便可以在区分大小写和不区分大小写的搜索之间切换。但是，添加这个字段会导致编译器报错，因为我们还没有在任何地方初始化这个字段。

<span class="filename">文件名：src/main.rs</span>

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch12-an-io-project/listing-12-22/src/main.rs:here}}
```

我们添加了 `ignore_case` 这个字段，其中包含一个布尔值。接下来，我们需要 `run` 函数来检查 `ignore_case` 字段的值，并根据该值来决定是调用 `search` 函数还是 `search_case_insensitive` 函数，如清单 12-22 所示。不过，目前这段代码仍然无法编译。

<列表编号="12-22" 文件名称="src/main.rs" 标题="根据 `config.ignore_case` 中的值调用 `search` 或 `search_case_insensitive`">

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch12-an-io-project/listing-12-22/src/main.rs:there}}
```

</ Listing>

最后，我们需要检查环境变量。处理环境变量的函数位于标准库中的`env`模块中，该模块已经在`_src/main.rs_`文件的顶部被引入。我们将使用`env`模块中的`var`函数来检查是否设置了名为`IGNORE_CASE`的环境变量的值，如清单12-23所示。

<Listing number="12-23" file-name="src/main.rs" caption="检查环境变量 `IGNORE_CASE` 中是否存在任何值">

```rust,ignore,noplayground
{{#rustdoc_include ../listings/ch12-an-io-project/listing-12-23/src/main.rs:here}}
```

</ Listing>

在这里，我们创建了一个新的变量 `ignore_case`。为了设置其值，我们调用了 `env::var` 函数，并将 `IGNORE_CASE` 环境变量的名称作为参数传递。`env::var` 函数返回一个 `Result` 对象，这个对象会在环境变量被设置时，包含该环境变量的值；如果环境变量未设置，则返回一个 `Err` 对象。

我们正在使用 `is_ok` 方法来检查 `Result` 中是否设置了环境变量，这意味着程序需要进行不区分大小写的搜索。如果 `IGNORE_CASE` 环境变量没有被设置任何值，那么 `is_ok` 将会返回 `false`，程序则需要进行区分大小写的搜索。我们并不关心环境变量的具体值，只关心它是否被设置或未被设置，因此我们使用 `is_ok` 来进行检查，而不是使用 `unwrap`、`expect`，或是我们在 `Result` 中看到的任何其他方法。

我们将 `ignore_case` 变量中的值传递给 `Config` 实例，这样 `run` 函数就可以读取该值，并决定是调用 `search_case_insensitive` 还是 `search`，正如我们在 Listing 12-22 中实现的那样。

让我们试试看！首先，我们将在不设置环境变量且使用查询`to`的情况下运行程序。这个查询应该能够匹配所有包含单词“_to_”的小写形式的行。

```console
{{#include ../listings/ch12-an-io-project/listing-12-23/output.txt}}
```

看起来仍然有效！现在让我们运行程序，将`IGNORE_CASE`设置为`1`，但查询部分保持不变，即`to`。

```console
$ IGNORE_CASE=1 cargo run -- to poem.txt
```

如果您使用的是 PowerShell，则需要设置环境变量，并将程序作为单独的命令来运行：

```console
PS> $Env:IGNORE_CASE=1; cargo run -- to poem.txt
```

这将使 `IGNORE_CASE` 在您的shell会话期间持续存在。可以使用 `Remove-Item` cmdlet来取消其设置。

```console
PS> Remove-Item Env:IGNORE_CASE
```

我们应该获取包含“to”这一词的行，这些行可能包含大写字母：

<!-- 手动重新生成
cd listings/ch12-an-io-project/listing-12-23
IGNORE_CASE=1 cargo run -- 到 poem.txt 文件
由于环境变量的问题，无法提取数据
-->

```console
Are you nobody, too?
How dreary to be somebody!
To tell your name the livelong day
To an admiring bog!
```

太好了，我们还找到了包含“_To_”的行！我们的`minigrep`程序现在可以执行由环境变量控制的不区分大小写的搜索。现在您知道了如何使用命令行参数或环境变量来设置选项。

有些程序允许同时使用参数和环境变量来指定相同的配置。在这种情况下，程序会决定哪个优先。对于另一个练习，可以尝试通过命令行参数或环境变量来控制大小写敏感性。如果程序被设置为一个参数区分大小写，另一个参数不区分大小写，那么需要确定是参数优先还是环境变量优先。

`std::env`模块包含了许多用于处理环境变量的实用功能：请查阅其文档以了解可用的功能。