## 注释

所有程序员都努力让他们的代码易于理解，但有时需要额外的解释。在这种情况下，程序员会在源代码中留下一些注释，这些注释虽然会被编译器忽略，但阅读代码的人可能会觉得它们很有用。

这是一个简单的注释：

```rust
// hello, world
```

在Rust中，惯用的注释风格是用两个斜杠开始注释，然后继续直到行尾。对于需要跨越多行的注释，你需要在每一行都包含`//`，如下所示：

```rust
// So we're doing something complicated here, long enough that we need
// multiple lines of comments to do it! Whew! Hopefully, this comment will
// explain what's going on.
```

在包含代码的行末尾也可以添加注释：

<span class="filename">文件名：src/main.rs</span>

```rust
{{#rustdoc_include ../listings/ch03-common-programming-concepts/no-listing-24-comments-end-of-line/src/main.rs}}
```

但是，你更经常会看到它们以这种格式使用，即注释位于代码上方的单独一行中：

<span class="filename">文件名：src/main.rs</span>

```rust
{{#rustdoc_include ../listings/ch03-common-programming-concepts/no-listing-25-comments-above-line/src/main.rs}}
```

Rust还拥有另一种注释类型，即文档注释。我们将在第十四章的[“将Crate发布到Crates.io”][publishing]这一节中讨论相关内容。

[发布]: ch14-02-将内容发布到Crates.IO.html