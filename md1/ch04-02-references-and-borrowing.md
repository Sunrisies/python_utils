## 参考文献与借用

在 Listing 4-5 中的元组代码中存在一个问题：我们必须将 `String` 返回给调用函数，这样在调用 `calculate_length` 之后，我们仍然可以使用 `String`。因为 `String` 已经被移到了 `calculate_length` 中。相反，我们可以提供一个对 `String` 值的引用。引用就像指针一样，它是一个地址，我们可以通过这个地址来访问存储在该地址的数据；这些数据属于某个其他变量。与指针不同的是，引用在整个引用有效期内都保证指向特定类型的有效值。

以下是如何定义和使用一个 ``calculate_length`` 函数的方法，该函数的参数是一个对象引用，而不是直接拥有该值：

<code listing file-name="src/main.rs">

```rust
{{#rustdoc_include ../listings/ch04-understanding-ownership/no-listing-07-reference/src/main.rs:all}}
```

</ Listing>

首先，请注意在变量声明和函数返回值中所有的元组代码都消失了。其次，我们注意到我们将`&s1`传递给`calculate_length`，并且在`calculate_length`的定义中，我们使用了`&String`而不是`String`。这些反斜杠表示引用，它们允许你引用某个值而不需要拥有该值的所有权。图4-6展示了这个概念。

<img alt="三个表格：s的表格仅包含对s1的表格的指针。s1的表格包含了s1的栈数据，并且指向堆中的字符串数据。" src="img/trpl04-06.svg" class="center" />

<span class="caption">图4-6：`&String`与`s`指向`String`与`s1`的示意图</span>

注意：使用 ``&``进行引用的相反操作是“解引用”，这可以通过解引用运算符 ``*``来实现。我们将在第八章中看到一些解引用运算符的用法，并在第十五章中详细讨论解引用的细节。

让我们仔细看看这里的函数调用：

```rust
{{#rustdoc_include ../listings/ch04-understanding-ownership/no-listing-07-reference/src/main.rs:here}}
```

`&s1`语法允许我们创建一个引用，该引用指向`s1`中的值，但并不拥有该值。由于这个引用并不拥有该值，因此当不再使用这个引用时，它所指向的值不会被丢弃。

同样，该函数的签名使用`&`来表明参数`s`的类型是一个引用。让我们添加一些解释性注释：

```rust
{{#rustdoc_include ../listings/ch04-understanding-ownership/no-listing-08-reference-with-annotations/src/main.rs:here}}
```

变量 ``s`` 的有效范围与任何函数的参数范围相同，但是当 ``s`` 不再被使用时，该变量所指向的值并不会被丢弃，因为 ``s`` 并不拥有该变量。当函数以引用形式传递参数时，我们无需返回具体的值来归还所有权，因为我们从来就没有真正拥有过该变量。

我们将创建引用的操作称为“借用”。就像在现实生活中一样，如果一个人拥有某物，那么你可以从他们那里借用它。当你使用完之后，你必须把它归还给他们。此时，你并不真正拥有那件物品。

那么，如果我们试图修改我们正在使用的某些内容会怎么样呢？请尝试使用 Listing 4-6 中的代码。剧透一下：这样做是行不通的！

<listing number="4-6" file-name="src/main.rs" caption="尝试修改被借用的值">

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch04-understanding-ownership/listing-04-06/src/main.rs}}
```

</ Listing>

以下是错误信息：

```console
{{#include ../listings/ch04-understanding-ownership/listing-04-06/output.txt}}
```

正如变量默认是不可变的，引用也是不可变的。我们不允许修改那些被引用到的对象。

### 可变引用

我们可以通过对 Listing 4-6 中的代码进行少量修改，从而允许我们修改被借用的数值。这些修改使用的是 _可变引用_。

<code listing file-name="src/main.rs">

```rust
{{#rustdoc_include ../listings/ch04-understanding-ownership/no-listing-09-fixes-listing-04-06/src/main.rs}}
```

</ Listing>

首先，我们将`s`改为`mut`。然后，我们使用`&mut s`创建一个可变引用，在该引用中调用`change`函数，并更新该函数的签名，使其能够接受带有`some_string: &mut String`的可变引用。这样就能清楚地表明`change`函数会修改它所引用的数值。

可变的引用有一个很大的限制：如果你有一个对某个值的可变引用，那么你就不能再有其他对该值的引用。这段代码试图创建两个对`s`的可变引用，但这将会失败：

<code listing file-name="src/main.rs">

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch04-understanding-ownership/no-listing-10-multiple-mut-not-allowed/src/main.rs:here}}
```

</ Listing>

以下是错误信息：

```console
{{#include ../listings/ch04-understanding-ownership/no-listing-10-multiple-mut-not-allowed/output.txt}}
```

这个错误提示指出，这段代码无效，因为我们不能多次将`s`视为可变的。第一次可变引用发生在`r1`中，并且必须持续到在`println!`中使用为止。但在创建该可变引用及其使用之间，我们尝试在`r2`中创建另一个可变引用，该引用也使用了与`r1`相同的数据。

这种限制禁止同时有多个可变引用指向同一数据，这样可以实现修改，但必须以非常可控的方式进行。这是新学习Rust的开发者们难以掌握的地方，因为大多数语言都允许你在任何时候进行修改。设置这种限制的好处是，Rust可以在编译时防止数据竞争。所谓“数据竞争”，类似于竞态条件，当以下三种情况发生时，就会引发数据竞争：

- 两个或多个指针同时访问相同的数据。
- 至少有一个指针用于写入数据。
- 没有机制用于同步对数据的访问。

数据竞争会导致未定义的行为，在运行时试图追踪它们时，诊断和修复这些问题可能会非常困难；Rust通过拒绝编译包含数据竞争的代码来避免这个问题！

一如既往，我们可以使用花括号来创建一个新的作用域，从而允许多个可变引用，但只能同时使用其中的一个引用：

```rust
{{#rustdoc_include ../listings/ch04-understanding-ownership/no-listing-11-muts-in-separate-scopes/src/main.rs:here}}
```

Rust对组合可变引用和不可变引用也实施了类似的规则。  
这段代码会导致错误：

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch04-understanding-ownership/no-listing-12-immutable-and-mutable-not-allowed/src/main.rs:here}}
```

以下是错误信息：

```console
{{#include ../listings/ch04-understanding-ownership/no-listing-12-immutable-and-mutable-not-allowed/output.txt}}
```

哎呀！当我们对同一个值拥有不可变引用时，我们也无法使用可变的引用。

使用不可变引用的人不会期望数据会突然在他们控制范围之外发生变化！不过，允许多个不可变引用是有原因的，因为仅仅阅读数据的用户无法影响其他用户的读取操作。

请注意，引用的范围从它被引入的地方开始，一直持续到最后一次使用该引用为止。例如，这段代码可以编译，因为不可变引用的最后一次使用是在`println!`中，而在那里之前并没有引入可变的引用。

```rust
{{#rustdoc_include ../listings/ch04-understanding-ownership/no-listing-13-reference-scope-ends/src/main.rs:here}}
```

不可变引用`r1`和`r2`的作用域在`println!`之后结束，它们最后一次被使用的位置是在可变引用`r3`被创建之前。这些作用域不会重叠，因此这段代码是允许的：编译器能够判断出该引用在作用域结束之前就已经不再被使用了。

尽管借用错误有时可能会让人感到沮丧，但请记住，是Rust编译器在编译时指出潜在的错误，并明确指出问题的具体位置。这样，你就不需要去追踪为什么数据并不像你想象的那样了。

### 悬空引用

在支持指针的语言中，很容易因为释放某些内存而错误地创建“悬空指针”——即指向可能已经分配给其他人的内存位置的指针。相比之下，Rust的编译器确保引用永远不会成为悬空引用：如果你有对某数据的引用，编译器会确保在引用该数据之前，该数据不会超出作用域。

让我们尝试创建一个悬空引用，看看Rust是如何通过编译时错误来防止这种情况发生的：

<code listing file-name="src/main.rs">

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch04-understanding-ownership/no-listing-14-dangling-reference/src/main.rs}}
```

</ Listing>

以下是错误信息：

```console
{{#include ../listings/ch04-understanding-ownership/no-listing-14-dangling-reference/output.txt}}
```

这条错误消息涉及了一个我们尚未讨论的功能：生命周期。我们将在第十章中详细讨论生命周期。不过，如果你忽略关于生命周期的部分，这条消息确实揭示了这段代码存在问题的关键原因。

```text
this function's return type contains a borrowed value, but there is no value
for it to be borrowed from
```

让我们更仔细地看看我们的 `dangle` 代码的每个阶段到底发生了什么：

<code listing file-name="src/main.rs">

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch04-understanding-ownership/no-listing-15-dangling-reference-annotated/src/main.rs:here}}
```

</ Listing>

因为 ``s`` 是在 ``dangle`` 内部创建的，所以当 ``dangle`` 的代码执行完毕后，``s`` 将会被释放内存。但是，我们试图返回对它的引用。这意味着这个引用会指向一个无效的``String``对象。这是不可接受的！Rust不允许我们这样做。

这里的解决方案是直接返回 `String`：

```rust
{{#rustdoc_include ../listings/ch04-understanding-ownership/no-listing-16-no-dangle/src/main.rs:here}}
```

这运行得非常顺利。所有权已经转移出去，而且没有任何内存被释放的情况发生。

### 引用规则

让我们回顾一下我们关于引用所讨论的内容：

- 在任何时候，你可以拥有一个可变引用，或者任意数量的不变引用。
- 引用必须始终有效。

接下来，我们将介绍另一种引用方式：切片。