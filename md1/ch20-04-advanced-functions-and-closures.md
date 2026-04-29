## 高级函数和闭包

本节探讨了与函数和闭包相关的一些高级特性，包括函数指针以及返回闭包。

### 函数指针

我们已经讨论过如何将闭包传递给函数；你也可以将普通函数传递给其他函数！这种技巧在你需要传递已经定义好的函数时非常有用，而不是重新定义一个闭包。这些函数会被强制转换为`fn`类型（使用小写的_），不要与`Fn`闭包特性混淆。`fn`类型被称为“函数指针”。通过使用带有函数指针的函数，你可以将这些函数作为其他函数的参数来使用。

指定某个参数是函数指针的语法与闭包的语法类似，如清单20-28所示。在这里，我们定义了一个名为`add_one`的函数，该函数将其参数加1。函数`do_twice`接受两个参数：一个是指向任何接受`i32`参数并返回`i32`值的函数的函数指针；另一个是`i32`值。函数`do_twice`会两次调用函数`f`，并将`arg`值作为参数传递，然后将这些函数调用的结果相加。函数`main`则使用`add_one`和`5`作为参数来调用`do_twice`。

<列表编号="20-28" 文件名称="src/main.rs" 标题="使用 `fn` 类型来接受函数指针作为参数">

```rust
{{#rustdoc_include ../listings/ch20-advanced-features/listing-20-28/src/main.rs}}
```

</ Listing>

这段代码会打印出`The answer is: 12`。我们指定在`do_twice`中的参数`f`是一个`fn`类型的函数，该函数接受一个类型为`i32`的参数，并返回一个`i32`类型的值。然后，我们可以在`do_twice`的主体中调用`f`。在`main`中，我们可以将函数名`add_one`作为第一个参数传递给`do_twice`。

与闭包不同，`fn`是一种类型，而不是一种特质。因此，我们直接将`fn`指定为参数类型，而不是使用`Fn`中的某个特质来声明一个通用类型参数。

函数指针实现了所有三个闭包特性（`Fn`、`FnMut`以及`FnOnce`），这意味着你可以始终将函数指针作为参数传递给那些需要闭包的函数。最好使用通用类型以及其中一个闭包特性来编写函数，这样你的函数就可以接受函数或闭包作为参数。

不过，有一个例子说明为什么只接受 ``fn`` 而不接受闭包的情况：当与外部没有闭包的代码进行交互时。C语言中的函数可以接受其他函数作为参数，但C语言本身并不支持闭包。

作为一个例子，说明如何在使用内联定义的闭包或命名函数时，来使用标准库中由 `Iterator` 特质提供的 `map` 方法。为了将数字向量转换为字符串向量，我们可以使用闭包，如清单 20-29 所示。

<listing number="20-29" caption="使用`map`方法将数字转换为字符串">

```rust
{{#rustdoc_include ../listings/ch20-advanced-features/listing-20-29/src/main.rs:here}}
```

</ Listing>

或者，我们可以将一个函数作为`map`的参数，而不是使用闭包。清单20-30展示了这种方式的实现效果。

<listing number="20-30" caption="使用 `String::to_string` 函数和 `map` 方法将数字转换为字符串">

```rust
{{#rustdoc_include ../listings/ch20-advanced-features/listing-20-30/src/main.rs:here}}
```

</ Listing>

请注意，我们必须使用在[“高级特性”][advanced-traits]<!-- ignore -->部分提到的完全限定语法，因为存在多个名为`to_string`的函数。

在这里，我们使用了在 `ToString` 特质中定义的 `to_string` 函数，而标准库已经为任何实现了 `Display` 的类型实现了这个函数。

请回想一下第6章中的[“枚举值”][enum-values]<!-- ignore -->部分，我们定义的每个枚举变体的名称也成为了初始化函数。我们可以将这些初始化函数作为函数指针来使用，从而实现闭包特性。这意味着我们可以将这些初始化函数作为参数传递给那些接受闭包的方法中，如清单20-31所示。

<listing number="20-31" caption="使用枚举初始化器与`map`方法，从数字创建`Status`实例">

```rust
{{#rustdoc_include ../listings/ch20-advanced-features/listing-20-31/src/main.rs:here}}
```

</ Listing>

在这里，我们使用 `u32` 中的每个值来创建 `Status::Value` 实例。同时，这些实例是通过 `Status::Value` 的初始化函数来初始化的。有些人更喜欢这种风格，而有些人则更倾向于使用闭包。不过，这两种方式编译出来的代码都是相同的，因此你可以根据个人喜好选择更清晰的表达方式。

### 返回闭包

闭包是通过特质来表示的，这意味着你不能直接返回闭包。在大多数情况下，如果你想返回一个具有该特质的类型，你可以将实现该特质的具体类型作为函数的返回值。然而，对于闭包来说，通常无法这样做，因为闭包没有可以返回的具体类型；例如，如果闭包从其作用域中捕获了任何值，那么你就不能将函数指针`fn`作为返回类型。

相反，您通常会使用我们在第10章中学到的`impl Trait`语法。您可以使用`Fn`、`FnOnce`和`FnMut`来返回任何函数类型。例如，清单20-32中的代码将会正常编译。

<Listing number="20-32" caption="使用 `impl Trait` 语法从函数中返回闭包">

```rust
{{#rustdoc_include ../listings/ch20-advanced-features/listing-20-32/src/lib.rs}}
```

</ Listing>

然而，正如我们在第13章的[“推断和注释闭包类型”][closure-types]章节中所提到的，每个闭包本身也是一种独特的类型。如果你需要处理多个具有相同签名但实现不同的函数，那么你需要使用 trait 对象来表示它们。考虑一下，如果你编写了如清单20-33所示的代码，会发生什么情况。

<list
    listing file-name="src/main.rs"
    number="20-33"
    caption="创建由返回`impl Fn`类型的函数定义的闭包`Vec<T>`"
>

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch20-advanced-features/listing-20-33/src/main.rs}}
```

</ Listing>

这里有两个函数，分别是`returns_closure`和`returns_initialized_closure`，这两个函数都返回`impl Fn(i32) -> i32`。请注意，尽管它们实现了相同的类型，但它们返回的闭包是不同的。如果我们尝试编译这个代码，Rust会提示我们这是不可行的。

```text
{{#include ../listings/ch20-advanced-features/listing-20-33/output.txt}}
```

错误信息告诉我们，每当我们返回 `impl Trait` 时，Rust会创建一个独特的 _opaque 类型_。在这种类型中，我们无法查看Rust为我们构建的具体细节，也无法猜测Rust会生成什么样的类型以便我们自己编写代码。因此，即使这些函数返回的闭包实现了相同的 trait `Fn(i32) -> i32`，但Rust为每个闭包生成的 opaque 类型是不同的。（这类似于Rust在相同的输出类型下为不同的异步块生成不同的具体类型的情况，正如我们在第17章的“`Pin` 类型与 `Unpin` trait”一节中所看到的。）我们已经多次看到解决这个问题的方法：我们可以使用 trait 对象，如清单20-34所示。

<列表编号="20-34" 标题="创建由返回 `Box<dyn Fn>` 的函数定义的闭包 `Vec<T>`，使它们具有相同的类型">

```rust
{{#rustdoc_include ../listings/ch20-advanced-features/listing-20-34/src/main.rs:here}}
```

</ Listing>

这段代码可以顺利编译。关于特质对象的其他信息，请参阅第18章中的[“使用特质对象来抽象共享行为”][trait-objects]部分。

接下来，让我们来看看宏！

[advanced-traits]: 第20章-02-advanced-traits.html#advanced-traits  
[enum-values]: 第6章-01-定义枚举.html#enum_values  
[closure-types]: 第13章-01-闭包类型.html#closure_type_inference_and_annotation  
[future-types]: 第17章-03-更多关于未来类型.html  
[trait-objects]: 第18章-02-特质对象.html