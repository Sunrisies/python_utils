## 参考文献与借用内容

在Listing 4-5中的元组代码存在的问题是，我们必须将`String`返回给调用函数，这样在调用`calculate_length`之后，我们仍然可以使用`String`。因为`String`已经被移到了`calculate_length`中。相反，我们可以提供一个对`String`值的引用。引用就像指针一样，它是一个地址，我们可以通过这个地址来访问存储在该地址的数据；而该数据则属于另一个变量。与指针不同，引用在引用存在期间始终会指向特定类型的有效值。

以下是如何定义和使用一个``calculate_length``函数的示例，该函数在作为参数时引用一个对象，而不是直接拥有该值：

<listing file-name="src/main.rs">

```rust
{{#rustdoc_include ../listings/ch04-understanding-ownership/no-listing-07-reference/src/main.rs:all}}
```

</清单>

首先，请注意在变量声明和函数返回值中的所有元组代码都已经消失了。其次，我们注意到我们将`&s1`传递给`calculate_length`，并且在`calculate_length`的定义中，我们使用的是`&String`而不是`String`。这些斜杠表示引用关系，它们允许你引用某个值而不需要拥有该值。图4-6展示了这个概念。

<img alt="三个表格：s的表格仅包含对s1的表格的指针。s1的表格包含了s1的堆栈数据，并且指向堆中的字符串数据。" src="img/trpl04-06.svg" class="center" />

<span class="caption">图4-6：`&String`与`s`指向`String`与`s1`的示意图</span>

注意：使用 ``&``进行引用的相反操作是“解引用”，这可以通过解引用运算符 ``*``来实现。我们将在第八章中看到一些解引用运算符的用途，并在第十五章中详细讨论解引用的细节。

让我们仔细看看这里的函数调用：

```rust
{{#rustdoc_include ../listings/ch04-understanding-ownership/no-listing-07-reference/src/main.rs:here}}
```

`&s1`语法允许我们创建一个引用，该引用指向`s1`的值，但并不拥有该值。由于这个引用并不拥有该值，因此当不再使用这个引用时，它所指向的值不会被丢弃。

同样，该函数的签名使用`&`来表示参数`s`的类型是一个引用。让我们添加一些解释性注释：

```rust
{{#rustdoc_include ../listings/ch04-understanding-ownership/no-listing-08-reference-with-annotations/src/main.rs:here}}
```

变量 ``s`` 的生效范围与任何函数的参数范围相同，但是当 ``s`` 不再被使用时，该变量所指向的值并不会被丢弃，因为 ``s`` 并不拥有该变量的所有权。当函数以引用形式传递参数时，我们无需返回具体的值来归还所有权，因为我们原本就没有拥有该变量的所有权。

我们将创建引用的行为称为“借用”。就像在现实生活中一样，如果一个人拥有某物，你可以从他们那里借用它。借用结束后，你必须归还它。你并不真正拥有它。

那么，如果我们试图修改我们借用的一些代码，会发生什么呢？请尝试使用 Listing 4-6 中的代码。剧透一下：这样做是行不通的！

<列表编号="4-6" 文件名称="src/main.rs" 标题="尝试修改已借用的值">

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch04-understanding-ownership/listing-04-06/src/main.rs}}
```

</清单>

出现以下错误：

```console
{{#include ../listings/ch04-understanding-ownership/listing-04-06/output.txt}}
```

正如变量默认是不可变的，引用也是不可变的。我们不允许修改那些被引用的对象。

### 可变引用

我们可以通过对代码进行少量调整，使其允许我们修改被借用的数值。这些调整使用的是一种“可变的引用”。

<listing file-name="src/main.rs">

```rust
{{#rustdoc_include ../listings/ch04-understanding-ownership/no-listing-09-fixes-listing-04-06/src/main.rs}}
```

</清单>

首先，我们将`s`改为`mut`。然后，我们使用`&mut s`创建一个可变的引用，在其中调用`change`函数，并更新函数签名，使其接受带有`some_string: &mut String`的可变引用。这样就能清楚地表明`change`函数会修改它所引用的数值。

可变的引用有一个很大的限制：如果你有一个对某个值的可变引用，那么你就不能再有其他对该值的引用。这段代码试图创建两个对`s`的可变引用，但会失败。

<listing file-name="src/main.rs">

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch04-understanding-ownership/no-listing-10-multiple-mut-not-allowed/src/main.rs:here}}
```

</清单>

出现以下错误：

```console
{{#include ../listings/ch04-understanding-ownership/no-listing-10-multiple-mut-not-allowed/output.txt}}
```

这个错误提示说，这段代码无效，因为我们不能多次使用``s``作为可变对象。第一次使用``s``作为可变对象是在``r1``中，并且必须一直保持这种状态，直到在``println!``中使用它。但在创建该可变引用之后，我们又尝试在``r2``中创建另一个可变引用，该引用也使用了与``r1``相同的数据。

这种限制禁止同时有多个可变引用指向同一数据，这样可以实现变异操作，但必须严格遵循一定的规则。这是新学习Rust的开发者们需要面对的问题，因为大多数语言都允许在任意时刻进行变异操作。设置这种限制的好处是，Rust可以在编译时防止数据竞争。所谓“数据竞争”，类似于竞态条件，当以下三种情况发生时，就会引发数据竞争：

- 两个或多个指针同时访问相同的数据。
- 至少有一个指针用于写入数据。
- 没有机制来同步对数据的访问。

数据竞争会导致未定义的行为，在运行时试图追踪它们时，诊断和修复这些问题可能会非常困难；Rust通过拒绝编译包含数据竞争的代码来避免这个问题！

一如既往，我们可以使用花括号来创建一个新的作用域，从而允许多个可变引用，但只能同时拥有有限数量的引用：

```rust
{{#rustdoc_include ../listings/ch04-understanding-ownership/no-listing-11-muts-in-separate-scopes/src/main.rs:here}}
```

Rust在合并可变引用和不可变引用时也遵循类似的规则。  
这段代码会导致错误：

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch04-understanding-ownership/no-listing-12-immutable-and-mutable-not-allowed/src/main.rs:here}}
```

出现以下错误：

```console
{{#include ../listings/ch04-understanding-ownership/no-listing-12-immutable-and-mutable-not-allowed/output.txt}}
```

哎呀！当我们有一个不可变引用指向同一个值时，我们也无法拥有可变的引用。

使用不可变引用的人不会期望该值会突然在他们面前发生变化！不过，允许多个不可变引用是有原因的，因为仅仅阅读数据的人无法影响其他人对数据的读取。

请注意，一个引用的范围从它被引入的地方开始，一直持续到该引用最后一次被使用的时候。例如，这段代码可以编译，因为不可变引用最后一次的使用是在`println!`中，而在可变引用被引入之前。

```rust
{{#rustdoc_include ../listings/ch04-understanding-ownership/no-listing-13-reference-scope-ends/src/main.rs:here}}
```

不可变引用`r1`和`r2`的作用域在`println!`之后结束，它们最后一次被使用的位置是在可变的引用`r3`被创建之前。这些作用域不会重叠，因此这段代码是允许的：编译器能够判断出该引用在作用域结束之前就不再被使用了。

尽管借用错误有时可能会让人感到沮丧，但请记住，Rust编译器会在编译时而不是运行时指出潜在的错误，并明确指出问题的具体位置。这样，你就不需要去追踪为什么数据并不像你想象的那样了。

### 悬空引用

在支持指针的语言中，很容易因释放某些内存而错误地创建“悬空指针”——即指向可能被分配给其他人的内存位置的指针。相比之下，在Rust中，编译器保证引用永远不会成为悬空引用：如果你有对某数据的引用，编译器会确保在引用该数据之前，该数据不会超出作用域。

让我们尝试创建一个悬空引用，看看Rust是如何通过编译时错误来防止这种情况发生的：

<listing file-name="src/main.rs">

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch04-understanding-ownership/no-listing-14-dangling-reference/src/main.rs}}
```

</清单>

出现以下错误：

```console
{{#include ../listings/ch04-understanding-ownership/no-listing-14-dangling-reference/output.txt}}
```

这条错误消息涉及一个我们尚未讨论的特性：生命周期。我们将在第十章中详细讨论生命周期。不过，如果你忽略与生命周期相关的部分，这条消息仍然包含了为什么这段代码存在问题的关键原因。

```text
this function's return type contains a borrowed value, but there is no value
for it to be borrowed from
```

让我们更仔细地看看我们的`dangle`代码的每个阶段到底发生了什么：

<listing file-name="src/main.rs">

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch04-understanding-ownership/no-listing-15-dangling-reference-annotated/src/main.rs:here}}
```

</清单>

因为 ``s`` 是在 ``dangle`` 内部创建的，当 ``dangle`` 的代码执行完毕后，``s`` 将会被释放。但是，我们试图返回一个对它的引用。这意味着这个引用会指向一个无效的``String``对象。这是不可接受的！Rust不允许我们这样做。

这里的解决方案是直接返回`String`。

```rust
{{#rustdoc_include ../listings/ch04-understanding-ownership/no-listing-16-no-dangle/src/main.rs:here}}
```

这个操作没有任何问题。所有权已经转移出去，而且没有任何资源被重新分配。

### 引用规则

让我们回顾一下我们关于引用的讨论内容：

- 在任何时候，你可以拥有一个可变引用，或者任意数量的不变引用。
- 引用必须始终有效。

接下来，我们将介绍另一种引用方式：切片。