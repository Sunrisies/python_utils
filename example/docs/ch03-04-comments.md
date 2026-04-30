## 评论

所有程序员都努力让他们的代码易于理解，但有时需要额外的解释。在这种情况下，程序员会在源代码中留下注释，这些注释会被编译器忽略，但阅读代码的人可能会觉得它们很有用。

以下是一个简单的注释：

```rust
// hello, world
```

在Rust中，惯用的注释风格是用两个斜杠开始注释，然后继续书写直到行尾。如果注释需要跨越多行，那么需要在每一行都加上 `//`，如下所示：

```rust
// So we're doing something complicated here, long enough that we need
// multiple lines of comments to do it! Whew! Hopefully, this comment will
// explain what's going on.
```

在包含代码的行末尾也可以添加注释：

<span class="filename"> 文件名: src/main.rs</span>

```rust
fn main() {
    let lucky_number = 7; // I'm feeling lucky today
}

```

但是，你更经常会看到它们以这种格式使用，即注释位于代码上方的单独一行中，用来说明该代码的含义。

<span class="filename"> 文件名: src/main.rs</span>

```rust
fn main() {
    // I'm feeling lucky today
    let lucky_number = 7;
}

```

Rust还拥有另一种注释类型，即文档注释。我们将在第十四章的[“将包发布到Crates.io”][publishing]<!-- ignore -->部分中讨论这一内容。

[publishing]: ch14-02-publishing-to-crates-io.html
