## 附录A：关键词

以下列表中包含那些被Rust语言预留用于当前或未来使用的关键字。因此，它们不能用作标识符（除非是原始标识符，我们在[“原始标识符”][raw-identifiers]<!-- ignore -->部分中有讨论）。**标识符**是指函数、变量、参数、结构字段、模块、软件包、常量、宏、静态值、属性、类型、特质或生命周期的名称。

[raw-identifiers]: #raw-identifiers

### 当前使用的关键词

以下是当前使用的关键词列表，以及它们的功能描述。

- **`as`**：执行基本类型转换，消除包含特定项的歧义，或在`use`语句中重命名这些项。  
- **`async`**：返回`Future`的结果，而不是阻塞当前线程。  
- **`await`**：暂停执行，直到`Future`的结果准备好为止。  
- **`break`**：立即退出循环。  
- **`const`**：定义常量项或常量原始指针。
- **`continue`**: 继续到下一个循环迭代。  
- **`crate`**: 在模块路径中，指的是crate的根目录。  
- **`dyn`**: 动态调用一个trait对象。  
- **`else`**: `if`和`if let`控制流结构的备用方案。  
- **`enum`**: 定义一个枚举类型。  
- **`extern`**: 链接一个外部函数或变量。  
- **`false`**: 布尔值的false字面量。
- **`fn`**: 定义函数或函数指针类型。  
- **`for`**: 遍历迭代器中的项目，实现特定特征，或指定更高的生命周期等级。  
- **`if`**: 根据条件表达式的结果进行分支处理。  
- **`impl`**: 实现固有的或特征性的功能。  
- **`in`**: 属于`for`循环语法的一部分。  
- **`let`**: 绑定一个变量。  
- **`loop`**: 无条件地执行循环。
- **`match`**: 将值与模式进行匹配。  
- **`mod`**: 定义模块。  
- **`move`**: 使闭包拥有所有捕获的数据。  
- **`mut`**: 表示引用、原始指针或模式绑定中的可变性。  
- **`pub`**: 在结构体字段、`impl`块或模块中表示公共可见性。  
- **`ref`**: 通过引用进行绑定。  
- **`return`**: 从函数中返回。
- **`Self`**: 我们正在定义或实现的类型别名。  
- **`self`**: 方法主体或当前模块。  
- **`static`**: 全局变量，或在整个程序执行过程中一直存在的变量。  
- **`struct`**: 定义结构体。  
- **`super`**: 当前模块的父模块。  
- **`trait`**: 定义特质。  
- **`true`**: 布尔值的真值。  
- **`type`**: 定义类型别名或相关类型。
- **`union`**: 定义一个[联合][union]；仅在联合声明中使用时才会作为关键字使用。  
- **`unsafe`**: 表示不安全的代码、函数、特质或实现方式。  
- **`use`**: 将符号引入作用域中。  
- **`where`**: 表示用于约束类型的条款。  
- **`while`**: 根据表达式的结果有条件地执行循环。

[联合体]:../reference/items/unions.html

### 关键词仅供将来使用

以下这些关键字目前还没有任何功能，但被Rust保留，以备将来使用：

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

**原始标识符**是一种语法，允许你在通常不允许使用的关键词前加上`r#`前缀。通过这种方式，你可以在这些关键词被限制使用的场合下使用它们。

例如，``match``是一个关键字。如果你尝试编译以下函数，并且该函数的名称使用了``match``，那么将会发生错误。

<span class="filename">文件名：src/main.rs</span>

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

该错误表明您不能使用关键字 ``match`` 作为函数标识符。若想使用 ``match`` 作为函数名称，则需要使用原始标识符语法，如下所示：

<span class="filename">文件名：src/main.rs</span>

```rust
fn r#match(needle: &str, haystack: &str) -> bool {
    haystack.contains(needle)
}

fn main() {
    assert!(r#match("foo", "foobar"));
}
```

这段代码可以无错误地编译。请注意，在函数的定义中函数名称前有`r#`的前缀，同时也在`main`中指定了函数的调用位置。

原始标识符允许您使用任何您选择的单词作为标识符，即使该单词恰好是一个保留的关键字。这为我们选择标识符名称提供了更大的自由度，同时也使我们能够与用其他语言编写的程序集成，而这些语言中的这些单词并不被视为关键字。此外，原始标识符还允许您使用与您的 crate 使用的 Rust 版本不同的库。例如，``try`` 在 2015 版中不是关键字，但在 2018 版、2021 版中却是。以及2024版本。如果您使用的库是基于2015版本编写的，并且包含`try`这个函数，那么您需要在后续版本的代码中使用原始标识符语法`r#try`来调用该函数。有关版本的更多信息，请参阅[附录E][appendix-e]<!-- ignore -->。

[附录E]: appendix-05-editions.html