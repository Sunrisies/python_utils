## 切片类型

_Slices_允许你引用一个连续的元素序列，这个序列属于[集合](ch08-00-common-collections.md)<!-- 忽略 -->。Slice是一种引用方式，因此它没有所有权。

这是一个简单的编程问题：编写一个函数，该函数接收一个由空格分隔的单词字符串，并返回该字符串中第一个找到的单词。如果函数在字符串中找不到空格，那么整个字符串应该被视为一个单词，因此应该返回整个字符串。

注意：为了便于理解切片的概念，在本节中我们仅考虑ASCII字符的情况；关于UTF-8编码处理的更详细讨论，请参阅第8章的“使用字符串存储UTF-8编码的文本”部分。

让我们来看看如何在不使用`slices`的情况下编写这个函数的签名，以此来理解`slices`所解决的问题：

```rust,ignore
fn first_word(s: &String) -> ?
```

`first_word`函数的参数类型为`&String`。我们不需要所有权信息，所以这样是可以的。（在Rust的惯用编程中，除非有必要，否则函数不会拥有其参数的所有权，这一点在我们继续阅读的过程中会逐渐明白。）但是，我们应该返回什么呢？实际上，我们无法直接描述字符串的“部分”。不过，我们可以返回单词末尾的索引，这个索引通常由一个空格来表示。让我们尝试这样做，如清单4-7所示。

<listing number="4-7" file-name="src/main.rs" caption="返回字节索引值的`first_word`函数，该值会被赋值给`String`参数">

```rust
{{#rustdoc_include ../listings/ch04-understanding-ownership/listing-04-07/src/main.rs:here}}
```

</ Listing>

因为我们需要逐个检查`String`元素，判断某个值是否为空格，所以我们将使用`as_bytes`方法将`String`转换为字节数组。

```rust,ignore
{{#rustdoc_include ../listings/ch04-understanding-ownership/listing-04-07/src/main.rs:as_bytes}}
```

接下来，我们使用`iter`方法创建一个遍历字节数组的迭代器：

```rust,ignore
{{#rustdoc_include ../listings/ch04-understanding-ownership/listing-04-07/src/main.rs:iter}}
```

我们将在[第13章][ch13]中更详细地讨论迭代器。  
目前，请注意`iter`是一个方法，它返回集合中的每个元素；而`enumerate`则包装了`iter`的结果，并将每个元素作为元组的一部分返回。从`enumerate`返回的元组的第一个元素是索引，第二个元素则是对该元素的引用。这种方式比我们自己计算索引要方便得多。

因为 ``enumerate`` 方法返回一个元组，我们可以使用模式来解析这个元组。我们将在[第6章][ch6]中进一步讨论模式的使用。在 ``for`` 循环中，我们指定了一个模式，该模式使用 ``i`` 作为元组的索引，而使用 ``&item`` 作为元组中的单个字节。由于我们从 ``.iter().enumerate()`` 获取了元素的引用，因此我们在模式中使用了 ``&``。

在 `for` 循环中，我们通过使用字节字面量语法来查找代表空格的字节。如果找到了空格，我们就返回该位置。否则，我们通过使用 `s.len()` 来返回字符串的长度。

```rust,ignore
{{#rustdoc_include ../listings/ch04-understanding-ownership/listing-04-07/src/main.rs:inside_for}}
```

我们现在有办法找到字符串中第一个单词末尾的索引，但存在一个问题。我们返回的是一个单独的 ``usize``，然而它只有在 ``&String`` 的上下文中才具有实际意义。换句话说，因为它是一个与 ``String`` 不同的独立值，所以无法保证它在未来仍然有效。请参考清单4-8中的程序，该程序使用了来自清单4-7的 ``first_word`` 函数。

<列表编号="4-8" 文件名称="src/main.rs" 标题="存储调用 `first_word` 函数后的结果，然后修改 `String` 的内容">

```rust
{{#rustdoc_include ../listings/ch04-understanding-ownership/listing-04-08/src/main.rs:here}}
```

</ Listing>

这个程序在编译时没有任何错误，如果我们使用 ``word`` 来调用 ``s.clear()``，同样也不会出现错误。因为 ``word`` 根本与 ``s`` 的状态无关，所以 ``word`` 仍然包含 ``5`` 的值。我们可以利用这个值以及变量 ``s`` 来尝试提取出第一个单词，但这会是一个错误，因为在我们将 ``5`` 保存在 ``word`` 之后，``s`` 的内容已经发生了变化。

在`word`中，需要担心索引与`s`中的数据不同步，这既繁琐又容易出错！如果我们编写`second_word`函数的话，管理这些索引会更加困难。该函数的签名必须如下所示：

```rust,ignore
fn second_word(s: &String) -> (usize, usize) {
```

现在，我们跟踪了一个起始索引和一个结束索引，而且还有更多的值是从特定状态的数据中计算出来的，但这些值与那个状态完全无关。我们有三个不相关的变量在四处游荡，需要保持同步。

幸运的是，Rust有一个解决这个问题的方案：字符串切片。

### 字符串切片

字符串切片是指对一个`String`中连续元素序列的引用，其形式如下：

```rust
{{#rustdoc_include ../listings/ch04-understanding-ownership/no-listing-17-slice/src/main.rs:here}}
```

`hello`并不是对整个`String`的引用，而是对`String`中特定部分的引用，这部分是通过额外的`[0..5]`位来指定的。我们使用方括号内的范围来创建切片，具体方法是指定`[starting_index..ending_index]`，其中`_starting_index_`是切片中的第一个位置，`_ending_index_`则是切片中最后一个位置加1。在内部，切片数据结构存储了切片的起始位置和长度，这相当于`_ending_index_`减去`_starting_index`。因此，在`let world = &s[6..11];`的情况下，`world`将是一个切片，该切片包含指向`s`中索引为6的字节的指针，其长度值为`5`。

图4-7用图表展示了这一内容。

<img alt="三个表格：第一个表格表示s的栈数据，它指向字符串数据“hello world”在堆中的第0个字节。第三个表格表示slice world的栈数据，该slice的长度为5，指向堆数据表中的第6个字节。" src="img/trpl04-07.svg" class="center" style="width: 50%;" />

<span class="caption">图4-7：一个字符串切片，指向`String`的一部分</span>

在Rust的`..`范围语法中，如果你想从索引0开始，可以省略两个小数点之前的值。换句话说，这两个值是相等的：

```rust
let s = String::from("hello");

let slice = &s[0..2];
let slice = &s[..2];
```

同样地，如果你的切片包含了`String`的最后一个字节，那么你可以省略后面的数字。这意味着这两者是相等的：

```rust
let s = String::from("hello");

let len = s.len();

let slice = &s[3..len];
let slice = &s[3..];
```

您还可以同时提供两个值，以获取整个字符串的片段。因此，这两个值是相等的：

```rust
let s = String::from("hello");

let len = s.len();

let slice = &s[0..len];
let slice = &s[..];
```

注意：字符串切片的范围索引必须位于有效的UTF-8字符边界上。如果您尝试在多字节字符的中间位置创建字符串切片，程序将会因错误而退出。

考虑到所有这些信息，让我们重新编写 `first_word`，使其返回一个切片。表示“字符串切片”的类型被定义为 `&str`：

<code listing file-name="src/main.rs">

```rust
{{#rustdoc_include ../listings/ch04-understanding-ownership/no-listing-18-first-word-slice/src/main.rs:here}}
```

</ Listing>

我们获取单词末尾的索引的方式与清单4-7中相同，即通过查找第一个空格来实现。当找到空格时，我们使用字符串的起始位置和空格的位置作为起始和结束索引，返回一个字符串切片。

现在，当我们调用`first_word`时，我们得到的是一个与底层数据相关的单一值。这个值包含了对切片起始点的引用，以及切片中的元素数量。

返回切片同样适用于`second_word`函数：

```rust,ignore
fn second_word(s: &String) -> &str {
```

我们现在拥有一个简单明了的API，而且很难出错，因为编译器会确保对`String`的引用始终有效。还记得清单4-8中的程序中的那个错误吗？当时我们获取到了第一个单词的索引，但随后清空了字符串，导致索引变得无效。那段代码在逻辑上是不正确的，但并没有立即显示出错误。如果我们继续尝试使用被清空字符串的第一个单词索引，问题会在之后显现出来。使用切片版本`first_word`则会引发编译时错误：

<code listing file-name="src/main.rs">

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch04-understanding-ownership/no-listing-19-slice-error/src/main.rs:here}}
```

</ Listing>

以下是编译器报错信息：

```console
{{#include ../listings/ch04-understanding-ownership/no-listing-19-slice-error/output.txt}}
```

回想一下借用规则：如果我们有一个不可变的引用指向某物，那么我们就不能同时拥有一个可变的引用。因为`clear`需要截断`String`，所以它必须获取一个可变的引用。在调用`clear`之后的`println!`在`word`中使用了这个引用，因此不可变引用在那个时刻仍然必须是有效的。Rust不允许在`clear`中存在可变的引用，同时在`word`中存在不可变的引用，否则编译将会失败。这不仅使得我们的API更加易于使用，而且还消除了在编译时可能出现的一类错误！

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="字符串字面量实际上是切片"></a>

#### 字符串字面量作为切片

回想一下，我们之前讨论过字符串字面量存储在二进制数据中。现在既然了解了切片的概念，我们就可以正确地理解字符串字面量了：

```rust
let s = "Hello, world!";
```

这里的`s`的类型是`&str`：它是一个指针，指向二进制文件中的特定位置。这也是为什么字符串字面量是不可变的；`&str`实际上是一个不可变的引用。

#### 将字符串切片作为参数

了解到可以提取字面量和`String`中的值，这为我们带来了对`first_word`的进一步改进，而这就是它的核心功能：

```rust,ignore
fn first_word(s: &String) -> &str {
```

更有经验的开发者会选择使用列表4-9中展示的签名，因为这样我们可以在同一个函数中使用`&String`值和`&str`值。

<listing number="4-9" caption="通过使用字符串切片来改进 `first_word` 函数，以处理 `s` 参数的类型">

```rust,ignore
{{#rustdoc_include ../listings/ch04-understanding-ownership/listing-04-09/src/main.rs:here}}
```

</ Listing>

如果我们有一个字符串切片，我们可以直接传递它。如果我们有一个 ``String``，我们可以传递 ``String`` 的一个切片，或者对 ``String`` 的引用。这种灵活性利用了去引用强制转换的功能，这一特性我们将在第十五章的“在函数和方法中使用去引用强制转换”部分进行介绍。

定义一个函数，该函数接收一个字符串切片而不是对`String`的引用，这样可以使我们的API更加通用和实用，同时不会失去任何功能：

<code listing file-name="src/main.rs">

```rust
{{#rustdoc_include ../listings/ch04-understanding-ownership/listing-04-09/src/main.rs:usage}}
```

</ Listing>

### 其他切片

正如您所想象的那样，字符串切片是专用于字符串的。不过，还有一种更通用的切片类型。考虑这样一个数组：

```rust
let a = [1, 2, 3, 4, 5];
```

就像我们可能想要引用字符串的一部分一样，我们也可能会想要引用数组的一部分。我们可以这样做：

```rust
let a = [1, 2, 3, 4, 5];

let slice = &a[1..3];

assert_eq!(slice, &[2, 3]);
```

这个切片的类型是 ``&[i32]``。它的工作方式与字符串切片类似，通过存储对第一个元素的引用以及长度来实现。你会使用这种类型的切片来处理各种其他集合。我们将在第八章讨论向量时详细探讨这些集合。

## 总结

在Rust程序中，所有权、借用和切片的概念能够在编译时确保内存安全。Rust语言让你能够像其他系统编程语言一样控制自己的内存使用方式。但是，通过让数据的所有者在离开作用域时自动清理该数据，这意味着你不必编写额外的代码来实现这种控制。

所有权影响着Rust中许多其他部分的运作方式，因此我们在本书的后续章节中会进一步讨论这些概念。现在让我们进入第5章，了解如何将数据片段组合在一起，使用`struct`来实现这一功能。

[第13章]: ch13-02-iterators.html  
[第6章]: ch06-02-match.html#patterns-that-bind-to-values  
[字符串处理]: ch08-02-strings.html#storing-utf-8-encoded-text-with-strings  
[解引用强制类型]: ch15-02-deref.html#using-deref-coercions-in-functions-and-methods