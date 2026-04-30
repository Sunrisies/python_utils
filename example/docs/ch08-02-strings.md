## 使用字符串存储UTF-8编码的文本

我们在第4章中讨论过字符串，但现在我们将更深入地探讨它们。  
新的Rust开发者常常在字符串方面遇到困难，原因主要有三个：Rust容易引入潜在错误，字符串是一种比许多程序员所认为的更复杂的数据结构，以及UTF-8编码问题。这些因素结合在一起，可能会让那些来自其他编程语言的人感到难以理解。

我们在集合的上下文中讨论字符串，因为字符串实际上是由字节组成的集合，同时还有一些方法用于在字节被解释为文本时提供有用的功能。在本节中，我们将讨论所有集合类型所拥有的操作，比如创建、更新和读取字符串。我们还将探讨`String`与其他集合的不同之处，即，由于人和计算机对`String`数据的解释方式不同，因此对`String`进行索引会变得复杂。

<!-- Old headings. Do not remove or links may break. -->

<a id="what-is-a-string"></a>

### 定义字符串

首先，我们来定义“字符串”这一术语的含义。在Rust的核心语言中，只有一种字符串类型，那就是通常被称为 `str` 的字符串切片类型，而它通常以 borrowed 的形式存在，即 `&str`。在第四章中，我们讨论过字符串切片，它们是对存储在其他地方的一些UTF-8编码字符串数据的引用。例如，字符串字面量实际上存储在程序的二进制文件中，因此也属于字符串切片的一种。

`String`类型是由Rust的标准库提供的，而不是直接编码在核心语言中。它是一种可增长的、可变的、受所有权的管理、采用UTF-8编码的字符串类型。当Rust开发者在Rust中提到“字符串”时，他们可能指的是`String`类型或字符串切片`&str`类型，而不仅仅是其中的一种类型。虽然这一部分主要讨论的是`String`类型，但这两种类型在Rust的标准库中被广泛使用，而且`String`类型和字符串切片都是采用UTF-8编码的。

### 创建新的字符串

许多在 `Vec<T>` 中可用的操作，同样也可以在 `String` 中使用。因为 `String` 实际上是一个围绕字节向量的封装层，它提供了一些额外的功能、限制和保证。一个在 `Vec<T>` 和 `String` 中工作方式相同的函数示例是 `new` 函数，该函数用于创建实例，如清单 8-11 所示。

<Listing number="8-11" caption="Creating a new, empty `String`">

```rust
    let mut s = String::new();

```

</Listing>

这行代码创建了一个新的空字符串，名为 `s`，我们可以在这个字符串中加载数据。通常，我们会有一些初始数据，希望从这些数据开始构建字符串。为此，我们可以使用 `to_string` 方法，该方法适用于任何实现了 `Display` 特性的类型，就像字符串字面量一样。列表 8-12 展示了两个示例。

<Listing number="8-12" caption="Using the `to_string` method to create a `String` from a string literal">

```rust
    let data = "initial contents";

    let s = data.to_string();

    // The method also works on a literal directly:
    let s = "initial contents".to_string();

```

</Listing>

这段代码创建了一个包含 `initial contents` 的字符串。

我们还可以使用函数 `String::from` 来从一个字符串字面量中创建 `String`。列表 8-13 中的代码等同于使用 `to_string` 的列表 8-12 中的代码。

<Listing number="8-13" caption="Using the `String::from` function to create a `String` from a string literal">

```rust
    let s = String::from("initial contents");

```

</Listing>

由于字符串被用于许多不同的场景，我们可以为字符串使用许多不同的通用API，从而提供大量的选择。其中一些选项可能看起来有些冗余，但它们都有各自的作用！在这种情况下， `String::from` 和 `to_string` 的作用是相同的，因此选择哪一个取决于风格和可读性。

请记住，字符串都是用 UTF-8 编码的，因此我们可以在其中包含任何正确编码的数据，如清单 8-14 所示。

<Listing number="8-14" caption="Storing greetings in different languages in strings">

```rust
    let hello = String::from("السلام عليكم");
    let hello = String::from("Dobrý den");
    let hello = String::from("Hello");
    let hello = String::from("שלום");
    let hello = String::from("नमस्ते");
    let hello = String::from("こんにちは");
    let hello = String::from("안녕하세요");
    let hello = String::from("你好");
    let hello = String::from("Olá");
    // ANCHOR: russian
    let hello = String::from("Здравствуйте");
    // ANCHOR_END: russian
    // ANCHOR: spanish
    let hello = String::from("Hola");
    // ANCHOR_END: spanish

```

</Listing>

所有这些都是有效的 `String` 值。

### 更新字符串

A `String` 可以扩大规模，其内容也可以发生变化，就像 `Vec<T>` 的内容一样，如果你向其中添加更多数据。此外，你可以方便地使用 `+` 运算符或 `format!` 宏来连接 `String` 的值。

<!-- Old headings. Do not remove or links may break. -->

<a id="appending-to-a-string-with-push_str-and-push"></a>

#### 使用 `push_str` 或 `push` 进行追加操作

我们可以使用 `push_str` 方法添加一个字符串切片，从而生成 `String`，如清单 8-15 所示。

<Listing number="8-15" caption="Appending a string slice to a `String` using the `push_str` method">

```rust
    let mut s = String::from("foo");
    s.push_str("bar");

```

</Listing>

在这两行代码之后，`s`将包含`foobar`。`push_str`方法接受一个字符串切片，因为我们不一定想要拥有该参数。例如，在清单8-16中的代码中，我们希望在将内容追加到`s1`之后，能够使用`s2`。

<Listing number="8-16" caption="Using a string slice after appending its contents to a `String`">

```rust
    let mut s1 = String::from("foo");
    let s2 = "bar";
    s1.push_str(s2);
    println!("s2 is {s2}");

```

</Listing>

如果 `push_str` 方法取得了 `s2` 的所有权，那么我们就无法在最后一行打印出其值了。不过，这段代码仍然按照我们的预期正常工作！

`push`方法接受一个字符作为参数，并将其添加到`String`中。列表8-17展示了如何使用`push`方法将字母_l_添加到`String`中。

<Listing number="8-17" caption="Adding one character to a `String` value using `push`">

```rust
    let mut s = String::from("lo");
    s.push('l');

```

</Listing>

因此，`s` 将包含 `lol`。

<!-- Old headings. Do not remove or links may break. -->

<a id="concatenation-with-the--operator-or-the-format-macro"></a>

#### 使用 `+` 或 `format!` 进行连接

通常，您会希望将两个现有的字符串合并在一起。其中一种方法是使用 `+` 运算符，如清单 8-18 所示。

<Listing number="8-18" caption="Using the `+` operator to combine two `String` values into a new `String` value">

```rust
    let s1 = String::from("Hello, ");
    let s2 = String::from("world!");
    let s3 = s1 + &s2; // note s1 has been moved here and can no longer be used

```

</Listing>

字符串 `s3` 将包含 `Hello, world!`。之所以 `s1` 在添加后不再有效，而我们使用 `s2` 作为引用，是因为这与使用 `+` 运算符时调用的方法的签名有关。`+` 运算符使用的是 `add` 方法，其签名大致如下：

```rust,ignore
fn add(self, s: &str) -> String {
```

在标准库中，你会看到 `add` 是通过泛型及相关类型来定义的。在这里，我们替换了具体类型，这就是当我们使用 `String` 的值调用此方法时会发生的情况。我们将在第十章讨论泛型。这个签名为我们理解 `+` 运算符的复杂部分提供了必要的线索。

首先，`s2`有一个`&`，这意味着我们将第二个字符串的引用添加到第一个字符串中。这是因为`add`函数中包含了`s`参数：我们只能向`String`中添加字符串切片，而无法将两个`String`值合并在一起。但是等等——`&s2`的类型是`&String`，而不是`&str`，正如`add`的第二个参数所指定的那样。那么，为什么 Listing 8-18 能够编译呢？

我们能够在使用 `add` 时调用 `&s2` 的原因是，编译器可以将 `&String` 参数强制转换为 `&str`。当我们调用 `add` 方法时，Rust 会执行一种去引用转换，将 `&s2` 转换为 `&s2[..]`。我们将在第十五章中更深入地讨论去引用转换。因为 `add` 不会占用 `s` 参数的所有权，所以经过这个操作之后， `s2` 仍然是一个有效的 `String`。

其次，我们可以在签名中看到，`add`拥有`self`的所有权，因为`self`并没有`&`。这意味着清单8-18中的`s1`将被移动到`add`中，之后将不再有效。因此，虽然`let s3 = s1 + &s2;`看起来像是复制了两个字符串并创建一个新的字符串，但实际上它只是拥有`s1`的所有权，将`s2`的内容复制进去，然后返回结果的所有权。换句话说，它看起来像是做了很多复制操作，但实际上并非如此；这种实现方式比直接复制要高效得多。

如果我们需要连接多个字符串，`+`运算符的行为就会变得难以处理：

```rust
    let s1 = String::from("tic");
    let s2 = String::from("tac");
    let s3 = String::from("toe");

    let s = s1 + "-" + &s2 + "-" + &s3;

```

此时，`s`将变为`tic-tac-toe`。再加上所有`+`和`"`字符，很难理解到底发生了什么。为了以更复杂的方式组合字符串，我们可以使用`format!`宏：

```rust
    let s1 = String::from("tic");
    let s2 = String::from("tac");
    let s3 = String::from("toe");

    let s = format!("{s1}-{s2}-{s3}");

```

这段代码还将 `s` 设置为 `tic-tac-toe`。`format!` 宏的工作方式类似于`println!`，但它不是将输出打印到屏幕上，而是返回一个包含相应内容的`String`。使用 `format!` 的版本代码更容易阅读，而由 `format!` 宏生成的代码则使用引用机制，因此这种调用不会占用任何参数的所有权。

### 对字符串进行索引

在许多其他编程语言中，通过索引来访问字符串中的单个字符是一种有效且常见的操作。然而，如果在Rust中使用索引语法尝试访问某个子字符串的部分内容，将会出现错误。请参考清单8-19中的无效代码。

<Listing number="8-19" caption="Attempting to use indexing syntax with a `String`">

```rust,ignore,does_not_compile
    let s1 = String::from("hi");
    let h = s1[0];

```

</Listing>

这段代码会导致以下错误：

```console
$ cargo run
   Compiling collections v0.1.0 (file:///projects/collections)
error[E0277]: the type `str` cannot be indexed by `{integer}`
 --> src/main.rs:3:16
  |
3 |     let h = s1[0];
  |                ^ string indices are ranges of `usize`
  |
  = help: the trait `SliceIndex<str>` is not implemented for `{integer}`
  = note: you can use `.chars().nth()` or `.bytes().nth()`
          for more information, see chapter 8 in The Book: <https://doc.rust-lang.org/book/ch08-02-strings.html#indexing-into-strings>
  = help: the following other types implement trait `SliceIndex<T>`:
            `usize` implements `SliceIndex<ByteStr>`
            `usize` implements `SliceIndex<[T]>`
  = note: required for `String` to implement `Index<{integer}>`

For more information about this error, try `rustc --explain E0277`.
error: could not compile `collections` (bin "collections") due to 1 previous error

```

这个错误揭示了这样一个事实：Rust中的字符串并不支持索引操作。但为什么会出现这种情况呢？要解答这个问题，我们需要探讨Rust是如何在内存中存储字符串的。

#### 内部表示

A `String` 是一个基于 `Vec<u8>` 的封装。让我们来看看清单8-14中一些正确编码的UTF-8字符串。首先，这是其中一个例子：

```rust
    let hello = String::from("Hola");

```

在这种情况下，`len`将会变成`4`，这意味着存储字符串`"Hola"`的向量长度为4字节。在UTF-8编码下，每个字符需要1字节来表示。不过，下面这一行可能会让你感到惊讶（请注意，这个字符串以大写西里尔字母_Ze_开头，而不是数字3）：

```rust
    let hello = String::from("Здравствуйте");

```

如果你被问到字符串的长度，你可能会回答12。但实际上，Rust的答案是24：这是因为用UTF-8编码“Здравствуйте”需要24个字节，因为字符串中的每个Unicode标量值都需要2个字节的存储空间。因此，字符串的字节索引并不总能与有效的Unicode标量值相对应。为了说明这一点，请看这段无效的Rust代码：

```rust,ignore,does_not_compile
let hello = "Здравствуйте";
let answer = &hello[0];
```

您已经知道，`answer`并不等于`З`，第一个字符就是如此。在UTF-8编码中，`З`的第一个字节是`208`，第二个字节是`151`。因此，似乎`answer`实际上应该等于`208`，但是`208`本身并不是一个有效的字符。返回`208`可能并不是用户想要的结果，尤其是当他们请求这个字符串的第一个字符时；然而，这是Rust在字节索引0处唯一拥有的数据。通常，用户并不希望得到字节值的返回，即使字符串只包含拉丁字母。如果`&"hi"[0]`是一个有效的代码，它能够返回字节值的话，那么它将会返回`104`，而不是`h`。

因此，为了避免返回意外的值并导致可能不会被立即发现的错误，Rust根本不会编译这段代码，从而在开发过程的早期就避免了误解。

<!-- Old headings. Do not remove or links may break. -->

<a id="bytes-and-scalar-values-and-grapheme-clusters-oh-my"></a>

#### 字节、标量值以及图素簇

关于UTF-8的另一个要点是，从Rust的角度来看，处理字符串实际上有三种相关方式：以字节为单位、作为标量值，以及以字符簇的形式（这最接近我们所说的“字母”）。

如果我们看一下用天城文书写的印地语单词“नमस्ते”，它会被存储为一个 `u8` 值的向量，看起来像这样：

```text
[224, 164, 168, 224, 164, 174, 224, 164, 184, 224, 165, 141, 224, 164, 164,
224, 165, 135]
```

这相当于18个字节，这也是计算机最终存储这些数据的方式。如果我们把它们视为Unicode标量值，也就是Rust的`char`类型所表示的，那么这些字节看起来就是这样的：

```text
['न', 'म', 'स', '्', 'त', 'े']
```

这里共有六个 `char` 值，但第四个和第六个值并不是字母：它们实际上是用于标注的符号，单独来看是没有意义的。如果我们把它们视为字符群，那么就能得到人们所说的构成印地语单词的四个字母。

```text
["न", "म", "स्", "ते"]
```

Rust提供了多种方式来解释计算机存储的原始字符串数据，这样每个程序都可以选择自己需要的解释方式，无论这些数据使用的是哪种人类语言。

最后，Rust不允许我们对 `String` 进行索引以获取某个字符的原因在于，索引操作应该始终以常数时间（O(1)）完成。但是，对于 `String`，我们无法保证性能，因为Rust需要从头到尾遍历内容，以确定有多少个有效的字符。

### 字符串切片

对字符串进行索引通常不是一个好主意，因为不清楚字符串索引操作的返回类型应该是什么：是字节值、字符、字符簇，还是字符串切片。因此，如果你真的需要使用索引来创建字符串切片，Rust会要求你提供更具体的说明。

与其使用 `[]` 来索引单个数字，不如使用 `[]` 并指定一个范围，从而创建一个包含特定字节的字符串切片。

```rust
let hello = "Здравствуйте";

let s = &hello[0..4];
```

在这里，`s`将是一个包含字符串前4个字节的`&str`。之前我们提到过，这些字符每个都是2个字节，这意味着`s`将变成`Зд`。

如果我们试图仅使用类似`&hello[0..1]`的工具来分割字符的某些字节，Rust会在运行时引发panic，这就像在向量中访问了无效的索引一样。

```console
$ cargo run
   Compiling collections v0.1.0 (file:///projects/collections)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.43s
     Running `target/debug/collections`

thread 'main' panicked at src/main.rs:4:19:
byte index 1 is not a char boundary; it is inside 'З' (bytes 0..2) of `Здравствуйте`
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace

```

在创建带有范围的字符串切片时，应该非常小心，因为这样做可能会导致程序崩溃。

<!-- Old headings. Do not remove or links may break. -->

<a id="methods-for-iterating-over-strings"></a>

### 遍历字符串

处理字符串的最佳方式是明确说明你是想要字符还是字节。对于单个Unicode标量值，可以使用`chars`方法。对“Зд”调用`chars`方法会将其拆分成两个类型为`char`的值，你可以遍历这个结果来访问每个元素。

```rust
for c in "Зд".chars() {
    println!("{c}");
}
```

这段代码将输出以下内容：

```text
З
д
```

或者，`bytes`方法会返回每个原始字节，这可能对你的领域来说比较合适：

```rust
for b in "Зд".bytes() {
    println!("{b}");
}
```

这段代码将输出构成这个字符串的4个字节：

```text
208
151
208
180
```

但请务必记住，有效的 Unicode 标量值可能由超过1个字节组成。

从字符串中提取字符集群的过程与处理天城文一样复杂，因此标准库并不提供这一功能。如果你需要这个功能，可以在[crates.io](https://crates.io/)上找到相关的小包。

<!-- Old headings. Do not remove or links may break. -->

<a id="strings-are-not-so-simple"></a>

### 处理字符串中的复杂性

总结来说，字符串处理非常复杂。不同的编程语言在处理这种复杂性时采取不同的方式。Rust选择将正确处理 `String` 数据作为所有Rust程序的默认行为，这意味着程序员在处理UTF-8数据时需要更加注意。这种权衡使得字符串处理的复杂性比其他编程语言更为明显，但它可以避免在开发周期后期处理非ASCII字符引发的错误。

好消息是，标准库提供了许多基于 `String` 和 `&str` 类型的功能，以帮助正确处理这些复杂情况。请务必查阅相关文档，了解诸如 `contains` 用于字符串搜索的方法，以及 `replace` 用于用另一字符串替换字符串中部分内容的方法。

让我们来尝试一些稍微简单一些的东西：哈希映射！