## 切片类型

_Slices_ 允许你引用一个连续的序列中的元素，这些元素属于一个[集合](ch08-00-common-collections.md)<!-- ignore -->。Slice是一种引用方式，因此它没有所有权。

这是一个简单的编程问题：编写一个函数，该函数接收一个由空格分隔的单词字符串，并返回该字符串中第一个找到的单词。如果函数在字符串中找不到空格，那么整个字符串应该被视为一个单词，因此应该返回整个字符串。

注意：为了便于理解切片的概念，本节仅假设文本为ASCII格式；关于UTF-8编码处理的更详细讨论，请参见第8章的“使用字符串存储UTF-8编码文本”部分。

让我们来看看如何在不使用切片的情况下编写这个函数的签名，以此来理解切片所解决的问题。

```rust,ignore
fn first_word(s: &String) -> ?
```

函数 `first_word` 有一个类型为 `&String` 的参数。我们不需要所有权信息，所以这样是可以的。（在Rust的惯用语法中，函数通常不会主动获取其参数的所有权，除非有特定的需求，而这样做的理由会在后续的内容中变得清晰。）但是，我们应该返回什么呢？实际上，我们并没有办法来表示字符串中的某个“部分”。不过，我们可以返回单词末尾的索引，这个索引通常由空格来表示。让我们尝试这样做，如清单4-7所示。

<Listing number="4-7" file-name="src/main.rs" caption="The `first_word` function that returns a byte index value into the `String` parameter">

```rust
fn first_word(s: &String) -> usize {
    // ANCHOR: as_bytes
    let bytes = s.as_bytes();
    // ANCHOR_END: as_bytes

    // ANCHOR: iter
    for (i, &item) in bytes.iter().enumerate() {
        // ANCHOR_END: iter
        // ANCHOR: inside_for
        if item == b' ' {
            return i;
        }
    }

    s.len()
    // ANCHOR_END: inside_for
}

```

</Listing>

因为我们需要逐个检查 `String` 中的元素，判断某个值是否为空，所以我们将 `String` 转换为字节数组，使用 `as_bytes` 方法进行处理。

```rust,ignore
    let bytes = s.as_bytes();

```

接下来，我们使用 `iter` 方法创建一个遍历字节数组的迭代器：

```rust,ignore
    for (i, &item) in bytes.iter().enumerate() {

```

我们将在[第13章][ch13]中更详细地讨论迭代器。  
目前，请了解以下概念：`iter`是一种返回集合中所有元素的方法；`enumerate`则包裹了`iter`的结果，并将每个元素作为元组的一部分返回。从`enumerate`返回的元组的第一个元素是索引，第二个元素则是对该元素的引用。这种方式比我们自己计算索引要方便得多。

因为 `enumerate` 方法返回一个元组，我们可以使用模式来分解这个元组。我们将在[第6章][ch6]<!-- ignore -->中进一步讨论模式。在 `for` 循环中，我们指定了一个模式，该模式使用 `i` 作为元组的索引，使用 `&item` 作为元组中的单个字节。由于我们从 `.iter().enumerate()` 获取了元素的引用，因此我们在模式中使用了 `&`。

在 `for` 循环中，我们通过使用字节字面量语法来查找代表空格的字节。如果找到了空格，我们就返回该位置。否则，我们就使用 `s.len()` 返回字符串的长度。

```rust,ignore
        if item == b' ' {
            return i;
        }
    }

    s.len()

```

我们现在有办法找出字符串中第一个单词的末尾索引，但存在一个问题。我们单独返回了一个 `usize` 值，但这个值在 `&String` 的上下文中才具有实际意义。换句话说，由于它是一个与 `String` 独立的值，因此无法保证它在未来仍然有效。请参考清单 4-8 中的程序，该程序使用了清单 4-7 中的 `first_word` 函数。

<Listing number="4-8" file-name="src/main.rs" caption="Storing the result from calling the `first_word` function and then changing the `String` contents">

```rust
fn main() {
    let mut s = String::from("hello world");

    let word = first_word(&s); // word will get the value 5

    s.clear(); // this empties the String, making it equal to ""

    // word still has the value 5 here, but s no longer has any content that we
    // could meaningfully use with the value 5, so word is now totally invalid!
}

```

</Listing>

这个程序在编译时没有任何错误，如果我们在使用 `s.clear()` 之后立即调用 `word`，同样也会没有错误。因为 `word` 与 `s` 的状态完全无关，所以 `word` 仍然包含 `5` 的值。我们可以使用这个值 `5` 与变量 `s` 来尝试提取第一个单词，但这会是一个错误，因为自我们保存 `5` 在 `word` 之后， `s` 的内容已经发生了变化。

担心 `word` 中的索引与 `s` 中的数据不同步，这是一件麻烦且容易出错的事情！如果我们编写一个 `second_word` 函数，管理这些索引会更加困难。该函数的签名必须如下所示：

```rust,ignore
fn second_word(s: &String) -> (usize, usize) {
```

现在，我们跟踪了一个起始索引和一个结束索引，此外还有更多的值，这些值是根据某个特定状态的数据计算出来的，但它们与那个状态完全无关。我们有三个不相关的变量在四处游荡，需要保持同步。

幸运的是，Rust有一个解决这个问题的方案：字符串切片。

### 字符串切片

字符串切片是指对一个连续的元素序列的引用，其形式如下：

```rust
    let s = String::from("hello world");

    let hello = &s[0..5];
    let world = &s[6..11];

```

与其引用整个 `String`，不如引用 `hello`，而 `hello` 又是对 `String` 中某一部分的引用，这部分的具体位置由额外的 `[0..5]` 来指定。我们通过在方括号内指定一个范围来创建切片，例如 `[starting_index..ending_index]`。其中，_`starting_index`_ 是切片中的第一个位置，而 _`ending_index`_ 则是切片中最后一个位置加一。在内部，切片数据结构会存储切片的起始位置和长度，这个长度相当于 _`ending_index`_ 减去 _`starting_index`_。因此，在 `let world = &s[6..11];` 的情况下，`world` 将是一个切片，该切片包含指向 `s` 中索引为6的字节的指针，且其长度值为 `5`。

图4-7用图表展示了这一情况。

<img alt="Three tables: a table representing the stack data of s, which points
to the byte at index 0 in a table of the string data &quot;hello world&quot; on
the heap. The third table represents the stack data of the slice world, which
has a length value of 5 and points to byte 6 of the heap data table."
src="img/trpl04-07.svg" class="center" style="width: 50%;" />

<span class="caption">图4-7：一个字符串切片，指代某部分内容  
`String`</span>

在 Rust 的 `..` 范围语法中，如果你想从索引 0 开始，可以省略两个小数点之前的值。换句话说，这两个值是相等的：

```rust
let s = String::from("hello");

let slice = &s[0..2];
let slice = &s[..2];
```

同样地，如果你的切片包含了 `String` 的最后一个字节，那么你可以省略后面的数字。这意味着这两个值是相等的：

```rust
let s = String::from("hello");

let len = s.len();

let slice = &s[3..len];
let slice = &s[3..];
```

你还可以同时提供两个值，从而获取整个字符串的片段。所以，这两个值是相等的：

```rust
let s = String::from("hello");

let len = s.len();

let slice = &s[0..len];
let slice = &s[..];
```

注意：字符串切片的范围索引必须位于有效的UTF-8字符边界上。如果您尝试在多字节字符的中间位置创建字符串切片，程序将会因错误而退出。

考虑到所有这些信息，让我们重新编写 `first_word`，使其返回一个切片。表示“字符串切片”的类型被标记为 `&str`。

<Listing file-name="src/main.rs">

```rust
fn first_word(s: &String) -> &str {
    let bytes = s.as_bytes();

    for (i, &item) in bytes.iter().enumerate() {
        if item == b' ' {
            return &s[0..i];
        }
    }

    &s[..]
}

```

</Listing>

我们获取单词末尾的索引的方式与 Listing 4-7 中相同，即通过查找第一个空格来实现。当找到空格时，我们使用字符串的起始位置和空格的索引来返回一个字符串切片，作为起始和结束的索引。

当我们调用 `first_word` 时，我们得到的是一个与底层数据相关的单一值。这个值包含了对切片起始点的引用，以及切片中的元素数量。

返回切片同样适用于 `second_word` 函数：

```rust,ignore
fn second_word(s: &String) -> &str {
```

我们现在拥有一个简单明了的API，而且很难出错，因为编译器会确保进入 `String` 的引用始终有效。还记得清单4-8中的程序中的那个错误吗？当时，我们获取到了第一个单词末尾的索引，但随后清空了字符串，导致索引变得无效。那段代码在逻辑上是不正确的，但当时并没有立即显示出错误。如果我们继续尝试在已清空字符串的情况下使用第一个单词的索引，问题就会在之后显现出来。使用 `first_word` 的切片版本则会引发编译时错误。

<Listing file-name="src/main.rs">

```rust,ignore,does_not_compile
fn main() {
    let mut s = String::from("hello world");

    let word = first_word(&s);

    s.clear(); // error!

    println!("the first word is: {word}");
}

```

</Listing>

以下是编译器提示的错误信息：

```console
$ cargo run
   Compiling ownership v0.1.0 (file:///projects/ownership)
error[E0502]: cannot borrow `s` as mutable because it is also borrowed as immutable
  --> src/main.rs:18:5
   |
16 |     let word = first_word(&s);
   |                           -- immutable borrow occurs here
17 |
18 |     s.clear(); // error!
   |     ^^^^^^^^^ mutable borrow occurs here
19 |
20 |     println!("the first word is: {word}");
   |                                   ---- immutable borrow later used here

For more information about this error, try `rustc --explain E0502`.
error: could not compile `ownership` (bin "ownership") due to 1 previous error

```

请回想一下借用规则：如果我们有一个对某个对象的不可变引用，那么我们就不能同时拥有一个可变的引用。因为 `clear` 需要截断 `String`，所以它必须得到一个可变的引用。在调用 `clear` 之后的 `println!` 会使用 `word` 中的引用，因此不可变引用在那个时刻仍然必须是有效的。Rust 不允许在 `clear` 中存在可变的引用，同时在 `word` 中存在不可变的引用，否则编译将会失败。Rust 不仅使我们的 API 更易于使用，而且还消除了在编译时出现的整类错误！

<!-- Old headings. Do not remove or links may break. -->

<a id="string-literals-are-slices"></a>

#### 字符串字面量作为切片

回想一下，我们之前讨论过字符串字面量存储在二进制数据中。现在，既然我们已经了解了切片的概念，我们就可以正确地理解字符串字面量了。

```rust
let s = "Hello, world!";
```

这里的类型 `s` 实际上是 `&str`：它是一个切片，指向二进制结构中的那个特定位置。这也是为什么字符串字面量是不可变的； `&str` 实际上是一个不可变的引用。

#### 将字符串切片作为参数

了解到可以提取字面量的一部分，并且可以获取 `String` 类型的值，这让我们能够进一步改进 `first_word` 类型。而这就是 `first_word` 类型的标志性特性。

```rust,ignore
fn first_word(s: &String) -> &str {
```

更有经验的 Rustacean 会像清单 4-9 中那样编写签名，因为这样我们可以在同一个函数上同时使用 `&String` 值和 `&str` 值。

<Listing number="4-9" caption="Improving the `first_word` function by using a string slice for the type of the `s` parameter">

```rust,ignore
fn first_word(s: &str) -> &str {

```

</Listing>

如果我们有一个字符串切片，我们可以直接传递它。如果我们有一个 `String`，我们可以传递 `String` 的切片或 `String` 的引用。这种灵活性利用了去引用强制转换的功能，这一特性我们将在第十五章的[“在函数和方法中使用去引用强制转换”][deref-coercions]<!--
ignore -->部分进行介绍。

定义一个函数，该函数接收一个字符串切片，而不是对 `String` 的引用，这样可以使我们的 API 更加通用和实用，同时不会丢失任何功能。

<Listing file-name="src/main.rs">

```rust
fn main() {
    let my_string = String::from("hello world");

    // `first_word` works on slices of `String`s, whether partial or whole.
    let word = first_word(&my_string[0..6]);
    let word = first_word(&my_string[..]);
    // `first_word` also works on references to `String`s, which are equivalent
    // to whole slices of `String`s.
    let word = first_word(&my_string);

    let my_string_literal = "hello world";

    // `first_word` works on slices of string literals, whether partial or
    // whole.
    let word = first_word(&my_string_literal[0..6]);
    let word = first_word(&my_string_literal[..]);

    // Because string literals *are* string slices already,
    // this works too, without the slice syntax!
    let word = first_word(my_string_literal);
}

```

</Listing>

### 其他切片

正如您所想象的那样，字符串切片是特定于字符串的。不过，还有一种更通用的切片类型。请考虑这个数组：

```rust
let a = [1, 2, 3, 4, 5];
```

就像我们可能想要引用字符串的一部分一样，我们也可能想要引用数组的一部分。我们可以这样做：

```rust
let a = [1, 2, 3, 4, 5];

let slice = &a[1..3];

assert_eq!(slice, &[2, 3]);
```

这个切片的类型是 `&[i32]`。它的工作方式与字符串切片类似，都是通过存储对第一个元素的引用以及长度来实现。你可以用这种切片来处理各种其他类型的集合。我们将在第八章讨论向量时，详细探讨这些集合。

## 摘要

在Rust程序中，所有权、借用和切片的概念能够在编译时确保内存安全。Rust语言让你能够像其他系统编程语言一样控制内存的使用方式。但是，通过让数据的所有者在离开作用域时自动清理该数据，这意味着你不必编写额外的代码来实现这种控制。

所有权影响着Rust中许多其他部分的运作方式，因此我们在本书的后续章节中将进一步讨论这些概念。现在让我们进入第5章，了解如何将数据片段组合在一起使用。

[ch13]: ch13-02-iterators.html
[ch6]: ch06-02-match.html#patterns-that-bind-to-values
[strings]: ch08-02-strings.html#storing-utf-8-encoded-text-with-strings
[deref-coercions]: ch15-02-deref.html#using-deref-coercions-in-functions-and-methods
