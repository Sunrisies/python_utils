## 附录A：关键词

以下列表包含了被 Rust 语言保留用于当前或未来使用的关键字。因此，这些关键字不能用作标识符（除非是原始标识符，我们在[“原始标识符”][raw-identifiers]<!-- ignore -->部分中有讨论）。_标识符_指的是函数、变量、参数、结构体字段、模块、软件包、常量、宏、静态值、属性、类型、特质或生命周期的名称。

[raw-identifiers]: #raw-identifiers

### 当前使用的关键词

以下是当前使用的关键词列表，以及它们的功能描述。

- **`as`**: 执行基本类型转换，消除特定特性的歧义，包含某个项目，或在`use`语句中重命名项目。
- **`async`**: 返回`Future`的结果，而不是阻塞当前线程。
- **`await`**: 暂停执行，直到`Future`的结果准备好。
- **`break`**: 立即退出循环。
- **`const`**: 定义常量项目或常量原始指针。
- **`continue`**: 继续到下一个循环迭代。
- **`crate`**: 在模块路径中，指的是 crate的根目录。
- **`dyn`**: 动态调用 trait 对象。
- **`else`**: 作为`if`和`if let`控制流结构的备用方案。
- **`enum`**: 定义枚举类型。
- **`extern`**: 链接外部函数或变量。
- **`false`**: 布尔假值字面量。
- **`fn`**: 定义函数或函数指针类型。
- **`for`**: 遍历迭代器中的项目，实现某个特性，或指定更高级别的生命周期。
- **`if`**: 根据条件表达式的结果进行分支判断。
- **`impl`**: 实现固有的或特性功能。
- **`in`**: 属于`for`循环语法的一部分。
- **`let`**: 绑定变量。
- **`loop`**: 无条件循环。
- **`match`**: 将值与模式进行匹配。
- **`mod`**: 定义模块。
- **`move`**: 使闭包拥有其捕获的所有内容。
- **`mut`**: 在引用、原始指针或模式绑定中表示可变性。
- **`pub`**: 在结构体字段、`impl`块或模块中表示公共可见性。
- **`ref`**: 按引用绑定。
- **`return`**: 从函数中返回。
- **`Self`**: 我们正在定义或实现的类型的别名。
- **`self`**: 方法主体或当前模块。
- **`static`**: 全局变量或在整个程序执行过程中持续存在的生命周期。
- **`struct`**: 定义结构体。
- **`super`**: 当前模块的父模块。
- **`trait`**: 定义特性。
- **`true`**: 布尔真值字面量。
- **`type`**: 定义类型别名或关联类型。
- **`union`**: 定义[union][union]<!-- ignore -->；仅在union声明中使用时才是关键字。
- **`unsafe`**: 表示不安全代码、函数、特性或实现。
- **`use`**: 将符号引入作用域。
- **`where`**: 表示约束类型的条款。
- **`while`**: 根据表达式的结果有条件地循环。

[union]: ../reference/items/unions.html

### 预留用于未来使用的关键词

以下这些关键字目前还没有任何功能，但被 Rust 保留，以备将来使用：

- `abstract`
- `become`
- `box`
- `do`
- `final`
- `gen`
- `macro`
- `override`
- `priv`
- `try`
- `typeof`
- `unsized`
- `virtual`
- `yield`

### 原始标识符

_原始标识符_是一种语法，允许你在通常不允许使用的关键词前使用它。你可以通过在关键词前加上 `r#` 来创建原始标识符。

例如，`match`是一个关键字。如果你尝试编译以下使用`match`作为名称的函数：

<span class="filename"> 文件名: src/main.rs</span>

```rust,ignore,does_not_compile
fn match(needle: &str, haystack: &str) -> bool {
    haystack.contains(needle)
}
```

你会遇到这个错误：

```text
error: expected identifier, found keyword `match`
 --> src/main.rs:4:4
  |
4 | fn match(needle: &str, haystack: &str) -> bool {
  |    ^^^^^ expected identifier, found keyword
```

该错误提示表明您不能使用关键词 `match` 作为函数标识符。若想将 `match` 用作函数名称，需要使用原始标识符语法，如下所示：

<span class="filename"> 文件名: src/main.rs</span>

```rust
fn r#match(needle: &str, haystack: &str) -> bool {
    haystack.contains(needle)
}

fn main() {
    assert!(r#match("foo", "foobar"));
}
```

这段代码可以无错误地编译。请注意函数名称前的 `r#` 前缀，以及函数在其定义中的调用位置 `main`。

原始标识符允许你使用任何你选择的单词作为标识符，即使该单词恰好是一个保留的关键字。这让我们在选择标识符名称时拥有更多的自由，同时也使我们能够与用其他语言编写的程序进行集成，这些语言中的这些单词并不被视为关键字。此外，原始标识符还允许你使用与你的 crate 使用的 Rust 版本不同的库。例如， `try` 在2015版中不是关键字，但在2018版、2021版和2024版中却是关键字。如果你依赖的库是用2015版编写的，并且包含 `try` 函数，那么你需要使用原始标识符语法，即`r#try`，才能在后续版本的代码中调用该函数。有关版本的更多信息，请参见[附录E][appendix-e]<!-- ignore -->。

[appendix-e]: appendix-05-editions.html
