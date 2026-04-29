## 函数

在Rust代码中，函数非常常见。你已经看到了该语言中最重要的函数之一：`main`函数，它是许多程序的入口点。你还看到了`fn`这个关键字，它允许你声明新的函数。

在Rust代码中，函数和变量的命名通常采用传统的_蛇形书写法_，即所有字母都使用小写，并用下划线分隔单词。下面有一个包含示例函数定义的程序：

<span class="filename">文件名：src/main.rs</span>

```rust
{{#rustdoc_include ../listings/ch03-common-programming-concepts/no-listing-16-functions/src/main.rs}}
```

在Rust中定义函数时，需要输入`fn`，随后是函数名称和一对圆括号。大括号用于告诉编译器函数的主体从何处开始到哪里结束。

我们可以通过输入函数的名称后跟一对括号来调用我们定义过的任何函数。因为`another_function`是在程序中定义的，所以可以从`main`函数内部调用它。请注意，我们在源代码中在`main`函数之后定义了`another_function`；我们也可以在之前就定义它。Rust并不关心你如何定义函数，只关心这些函数是否在一个可以被调用者访问的作用域内被定义。

让我们开始一个新的二进制项目，名为`_functions_`，以进一步探索函数相关的内容。将`another_function`示例放在`_src/main.rs_`文件中，然后运行它。你应该会看到如下输出：

```console
{{#include ../listings/ch03-common-programming-concepts/no-listing-16-functions/output.txt}}
```

这些行按照在 `main` 函数中出现的顺序执行。首先打印出“Hello, world!”，然后调用 `another_function`，并打印出其内容。

#### 参数

我们可以定义具有参数的函数，这些参数属于函数的签名的一部分。当函数有参数时，可以为这些参数提供具体的值。从技术上讲，这些具体的值被称为_参数_，但在日常对话中，人们往往将_参数_和_自变量_这两个词互换使用，指代函数定义中的变量或在调用函数时传递的具体值。

在这个版本的`another_function`中，我们增加了一个参数：

<span class="filename">文件名：src/main.rs</span>

```rust
{{#rustdoc_include ../listings/ch03-common-programming-concepts/no-listing-17-functions-with-parameters/src/main.rs}}
```

请尝试运行这个程序；你应该会得到如下输出：

```console
{{#include ../listings/ch03-common-programming-concepts/no-listing-17-functions-with-parameters/output.txt}}
```

声明 ``another_function`` 有一个名为 ``x`` 的参数。``x``的类型被指定为 ``i32``。当我们把 ``5`` 传递给 ``another_function`` 时，``println!`` 宏会将包含 ``x`` 的括号对放置在格式字符串的位置。

在函数签名中，你必须声明每个参数的类型。这是Rust设计中的一个刻意选择：在函数定义中要求类型注解意味着编译器几乎不需要在代码的其他地方使用类型注解来推断参数的类型。如果编译器知道函数期望哪些类型，它也能提供更有用的错误信息。

在定义多个参数时，用逗号将参数声明分开，如下所示：

<span class="filename">文件名：src/main.rs</span>

```rust
{{#rustdoc_include ../listings/ch03-common-programming-concepts/no-listing-18-functions-with-multiple-parameters/src/main.rs}}
```

这个示例创建了一个名为 ``print_labeled_measurement``的函数，该函数有两个参数。第一个参数的名称是 ``value``，其类型实际上是 ``i32``。第二个参数的名称是 ``unit_label``，其类型则是 ``char``。该函数在内部打印包含 ``value``和 ``unit_label``的文本。

让我们尝试运行这段代码。将当前位于你的`_functions_`项目中的`_src/main.rs_`文件替换为上面的示例代码，然后使用`cargo run`来运行它。

```console
{{#include ../listings/ch03-common-programming-concepts/no-listing-18-functions-with-multiple-parameters/output.txt}}
```

因为我们将函数调用中的`5`作为`value`的值，将`'h'`作为`unit_label`的值，所以程序的输出中包含了这些值。

### 语句与表达式

函数体由一系列语句组成，这些语句可以选择以表达式结尾。到目前为止，我们所讨论的函数并没有包含以表达式结尾的语句，但你已经看到过作为语句一部分的表达式。由于Rust是一种基于表达式的语言，因此理解这一区别非常重要。其他语言则没有这种区分，所以让我们来看看什么是语句和表达式，以及它们之间的差异如何影响函数的体。

- **语句**是执行某些操作但不返回值的指令。  
- **表达式**则会被计算出一个结果值。

让我们来看一些例子。

实际上，我们已经使用过语句和表达式了。使用 ``let`` 关键字创建变量并将其赋值给某个值，这就是一个语句。在 Listing 3-1 中，`let y = 6;` 也是一个语句。

<列表编号="3-1" 文件名称="src/main.rs" 标题="一个包含一条语句的`main`函数声明">

```rust
{{#rustdoc_include ../listings/ch03-common-programming-concepts/listing-03-01/src/main.rs}}
```

</ Listing>

函数定义也是一种语句；前面的整个例子本身就是一个语句。（正如我们稍后会看到的，调用函数并不是一种语句。）

语句不会返回值。因此，你不能将`let`语句赋值给另一个变量，因为如下代码试图这样做时会导致错误：

<span class="filename">文件名：src/main.rs</span>

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch03-common-programming-concepts/no-listing-19-statements-vs-expressions/src/main.rs}}
```

当你运行这个程序时，你会看到这样的错误：

```console
{{#include ../listings/ch03-common-programming-concepts/no-listing-19-statements-vs-expressions/output.txt}}
```

``let y = 6``语句并不返回任何值，因此``x``无法绑定到任何东西。这与其他语言如C和Ruby的情况不同，在那些语言中，赋值操作会返回被赋的值。在这些语言中，你可以编写``x = y = 6``，这样``x``和``y``都会获得``6``的值；但在Rust中情况并非如此。

表达式会计算出一个值，并且构成了你在Rust中编写的大部分代码。以数学运算为例，比如`5 + 6`，它是一个表达式，其计算结果为`11`。表达式也可以是语句的一部分：在清单3-1中，语句`let y = 6;`中的`6`就是一个表达式，其计算结果为`6`。调用函数也是一个表达式。调用宏同样是一个表达式。例如，用大括号创建的新作用域块也是一个表达式。

<span class="filename">文件名：src/main.rs</span>

```rust
{{#rustdoc_include ../listings/ch03-common-programming-concepts/no-listing-20-blocks-are-expressions/src/main.rs}}
```

这个表达式：

```rust,ignore
{
    let x = 3;
    x + 1
}
```

这是一个块，在这种情况下，其值为`4`。该值被绑定到`y`上，作为`let`语句的一部分。请注意`x + 1`这一行没有在末尾加上分号，这与你目前看到的大多数行不同。表达式并不包含结束的分号。如果你在表达式的末尾加上分号，就会将其变成一个语句，此时它将不再返回任何值。在接下来探讨函数的返回值和表达式时，请记住这一点。

### 具有返回值的函数

函数可以将值返回给调用它们的代码。我们不会为返回值命名，但必须在箭头符号(`->`)之后声明其类型。在Rust中，函数的返回值等同于函数主体块中最后一个表达式的值。你可以使用`return`关键字来提前从函数中返回某个值，但大多数函数都会隐式地返回最后一个表达式的结果。以下是一个返回值的函数示例：

<span class="filename">文件名：src/main.rs</span>

```rust
{{#rustdoc_include ../listings/ch03-common-programming-concepts/no-listing-21-function-return-values/src/main.rs}}
```

在 `five` 函数中，没有函数调用、宏，甚至没有 `let` 语句——只有数字 `5` 而已。这在 Rust 中是完全有效的函数定义。需要注意的是，函数的返回类型也已经被明确指定，如 `-> i32` 所示。试着运行这段代码，输出结果应该如下所示：

```console
{{#include ../listings/ch03-common-programming-concepts/no-listing-21-function-return-values/output.txt}}
```

在 `five` 中的 `5` 是函数的返回值，因此返回类型为 `i32`。让我们更详细地分析一下。这里有两个重要的点：
首先，`let x = five();` 这一行表明我们正在使用函数的返回值来初始化一个变量。由于函数 `five` 返回的是 `5`，所以这一行与下面的代码实际上是相同的。

```rust
let x = 5;
```

其次，`five`这个函数没有参数，并且定义了返回值的类型。但是，这个函数的主体只是一个单独的`5`，没有分号，因为它是一个表达式，我们想返回这个表达式的值。

让我们再看一个例子：

<span class="filename">文件名：src/main.rs</span>

```rust
{{#rustdoc_include ../listings/ch03-common-programming-concepts/no-listing-22-function-parameter-and-return/src/main.rs}}
```

运行这段代码会打印出`The value of x is: 6`。但是，如果我们在该行末尾加上一个分号，将`x + 1`从表达式改为语句，会发生什么情况呢？

<span class="filename">文件名：src/main.rs</span>

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch03-common-programming-concepts/no-listing-23-statements-dont-return-values/src/main.rs}}
```

编译这段代码会产生如下错误：

```console
{{#include ../listings/ch03-common-programming-concepts/no-listing-23-statements-dont-return-values/output.txt}}
```

主要的错误信息 `mismatched types` 揭示了这段代码中的核心问题。函数 `plus_one` 的定义表明它应该返回一个 `i32` 类型的值，但实际上语句并没有被评估为任何值，这一点通过 `()` 这个单位类型来表示。因此，实际上没有任何值被返回，这与函数定义相矛盾，从而导致错误。在输出中，Rust提供了一个消息，可能有助于解决这个问题：建议删除分号，这样就能修复错误。