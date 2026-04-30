## 使用生命周期验证引用

生命周期是另一种我们一直使用的通用机制。与其确保类型具有我们想要的行为，不如说生命周期的作用是确保引用在我们需要使用它们的整个期间都是有效的。

在第四章的[“参考文献与借用”][references-and-borrowing]<!-- ignore -->这一节中，我们没有讨论的一个细节是：在Rust中，每一个引用都有一个生命周期，这个生命周期就是该引用有效的范围。大多数情况下，生命周期是隐式的，由编译器推断出来，就像大多数情况下类型也是由编译器推断出来的。我们只需要对可能包含多种类型的类型进行注释。同样地，当引用的生命周期可能有多种不同的关联方式时，我们也必须对这些生命周期进行注释。Rust要求我们使用泛型生命周期参数来注释这些关系，以确保运行时实际使用的引用一定是有效的。

注释生命周期并不是其他大多数编程语言所拥有的概念，因此这会让人感到陌生。虽然在本章中我们不会全面介绍生命周期，但我们会讨论一些常见的生命周期语法，以便您能够熟悉这一概念。

<!-- Old headings. Do not remove or links may break. -->

<a id="preventing-dangling-references-with-lifetimes"></a>

### 悬空引用

生命周期的主要目的就是防止悬空引用出现。如果允许悬空引用存在，那么程序就会引用到与其预期引用的数据不同的数据。请参考清单10-16中的程序，该程序包含一个外部作用域和一个内部作用域。

<Listing number="10-16" caption="An attempt to use a reference whose value has gone out of scope">

```rust,ignore,does_not_compile
fn main() {
    let r;

    {
        let x = 5;
        r = &x;
    }

    println!("r: {r}");
}

```

</Listing>

注意：在列表10-16、10-17和10-23中，变量都是在未赋予初始值的情况下声明的，因此变量名只存在于外部作用域中。乍一看，这似乎与Rust不允许使用null值的规定相矛盾。然而，如果我们试图在给变量赋值时使用它，将会出现编译时错误，这证明了Rust确实不允许使用null值。

外部作用域声明了一个名为 `r` 的变量，该变量没有初始值。内部作用域则声明了一个名为 `x` 的变量，其初始值为 `5`。在内部作用域中，我们尝试将 `r` 的值设置为对 `x` 的引用。之后，内部作用域结束，我们尝试打印 `r` 中的值。然而，这段代码无法编译，因为 `r` 所引用的变量在我们尝试使用它之前就已经超出了作用域。以下是错误信息：

```console
$ cargo run
   Compiling chapter10 v0.1.0 (file:///projects/chapter10)
error[E0597]: `x` does not live long enough
 --> src/main.rs:6:13
  |
5 |         let x = 5;
  |             - binding `x` declared here
6 |         r = &x;
  |             ^^ borrowed value does not live long enough
7 |     }
  |     - `x` dropped here while still borrowed
8 |
9 |     println!("r: {r}");
  |                   - borrow later used here

For more information about this error, try `rustc --explain E0597`.
error: could not compile `chapter10` (bin "chapter10") due to 1 previous error

```

错误信息显示，变量 `x` 的生存期不够长。原因是当第7行内部作用域结束时， `x` 就会超出其作用域。但是 `r` 仍然在外部作用域中有效；由于其作用域更大，我们因此认为它“生存期更长”。如果Rust允许这段代码运行，那么 `r` 将会引用到 `x` 超出作用域时已经被释放的内存，这样一来，任何试图使用 `r` 的操作都将无法正确执行。那么，Rust是如何判断这段代码无效的呢？它使用了借用检查器。

### 借用检查器

Rust 编译器拥有一种“借用检查器”，该工具通过比较作用域来判断所有借用是否合法。列表 10-17 展示了与列表 10-16 相同的代码，但其中添加了注释来标明变量的生命周期。

<Listing number="10-17" caption="Annotations of the lifetimes of `r` and `x`, named `'a` and `'b`, respectively">

```rust,ignore,does_not_compile
fn main() {
    let r;                // ---------+-- 'a
                          //          |
    {                     //          |
        let x = 5;        // -+-- 'b  |
        r = &x;           //  |       |
    }                     // -+       |
                          //          |
    println!("r: {r}");   //          |
}                         // ---------+

```

</Listing>

在这里，我们标注了 `r` 的生命周期为 `'a`，以及 `x` 的生命周期为 `'b`。如您所见，内部的 `'b` 块比外部的 `'a` 生命周期要短得多。在编译时，Rust 会比较两个生命周期的大小，发现 `r` 的生命周期为 `'a`，但它所引用的内存的生命周期为 `'b`。因此，程序会被拒绝执行，因为 `'b` 的生命周期比 `'a` 短：引用对象的生命周期不足以支持引用。

列表10-18修复了代码，使其不再存在悬空引用，并且可以无错误地编译。

<Listing number="10-18" caption="A valid reference because the data has a longer lifetime than the reference">

```rust
fn main() {
    let x = 5;            // ----------+-- 'b
                          //           |
    let r = &x;           // --+-- 'a  |
                          //   |       |
    println!("r: {r}");   //   |       |
                          // --+       |
}                         // ----------+

```

</Listing>

在这里，`x`的生命周期为`'b`，而`'b`的寿命又大于`'a`。这意味着`r`可以引用`x`，因为Rust知道在`r`中的引用始终有效，而`x`也有效。

现在您已经了解了引用对象的生命周期是如何确定的，以及Rust是如何分析这些生命周期以确保引用始终有效。接下来，让我们探讨一下函数参数和返回值中的通用生命周期问题。

### 函数中的通用生命周期

我们将编写一个函数，该函数返回两个字符串切片中较长的那个。这个函数会接收两个字符串切片，并返回一个新的字符串切片。在实现了 `longest` 函数之后，列表 10-19 中的代码应该能够输出 `The longest string is abcd`。

<Listing number="10-19" file-name="src/main.rs" caption="A `main` function that calls the `longest` function to find the longer of two string slices">

```rust,ignore
fn main() {
    let string1 = String::from("abcd");
    let string2 = "xyz";

    let result = longest(string1.as_str(), string2);
    println!("The longest string is {result}");
}

```

</Listing>

请注意，我们希望这个函数能够接受字符串切片作为参数，这些切片实际上是引用，而不是字符串本身。因为我们不希望 `longest` 函数对其参数拥有所有权。关于为什么我们在 Listing 10-19 中使用的参数就是我们需要的参数，可以参考第4章中的“将字符串切片作为参数”相关内容。

如果我们尝试像清单10-20中那样实现 `longest` 函数，它将无法编译。

<Listing number="10-20" file-name="src/main.rs" caption="An implementation of the `longest` function that returns the longer of two string slices but does not yet compile">

```rust,ignore,does_not_compile
fn longest(x: &str, y: &str) -> &str {
    if x.len() > y.len() { x } else { y }
}

```

</Listing>

相反，我们遇到了以下关于生命周期的错误：

```console
$ cargo run
   Compiling chapter10 v0.1.0 (file:///projects/chapter10)
error[E0106]: missing lifetime specifier
 --> src/main.rs:9:33
  |
9 | fn longest(x: &str, y: &str) -> &str {
  |               ----     ----     ^ expected named lifetime parameter
  |
  = help: this function's return type contains a borrowed value, but the signature does not say whether it is borrowed from `x` or `y`
help: consider introducing a named lifetime parameter
  |
9 | fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
  |           ++++     ++          ++          ++

For more information about this error, try `rustc --explain E0106`.
error: could not compile `chapter10` (bin "chapter10") due to 1 previous error

```

帮助文本指出，返回类型需要一个通用的生命周期参数，因为Rust无法判断返回的引用是指向`x`还是`y`。实际上，我们也不知道具体的情况，因为该函数体内的`if`块返回的是指向`x`的引用，而`else`块则返回的是指向`y`的引用！

在定义这个函数时，我们不知道会传递给这个函数的具体值，因此我们无法确定是执行 `if` 情况还是 `else` 情况。我们还不知道被传递的引用的具体生命周期，因此无法像在 Listing 10-17 和 Listing 10-18 中那样来查看作用域，以确定我们返回的引用是否始终有效。借用检查器也无法确定这一点，因为它不知道 `x` 和 `y` 的生命周期与返回值生命周期之间的关系。为了修复这个错误，我们将添加通用的生命周期参数，以定义引用之间的关系，这样借用检查器就可以进行其分析了。

### 生命周期注解语法

生命周期注释并不会改变任何引用所存在的时长。相反，它们描述了多个引用之间的生命周期关系，而不会影响实际的生命周期。就像函数可以通过指定泛型类型参数来接受任何类型的参数一样，函数也可以通过指定泛型生命周期参数来接受具有任何生命周期的引用。

生命周期注释的语法有些特殊：生命周期参数的名称必须以撇号开头（`'`），并且通常都是小写，长度也很短，类似于泛型类型。大多数人会使用`'a`作为第一个生命周期注释。我们将生命周期参数注释放在引用符号`&`之后，并使用空格将注释与引用的类型分开。

以下是一些示例——一个没有生命周期参数的 `i32`，一个带有名为 `'a` 的生命周期参数的 `i32`，以及一个可变引用，该引用也带有生命周期 `'a`。

```rust,ignore
&i32        // a reference
&'a i32     // a reference with an explicit lifetime
&'a mut i32 // a mutable reference with an explicit lifetime
```

单独来看，生命周期注解并没有太多意义，因为这些注解的目的是告诉Rust，多个引用所使用的泛型生命周期参数之间是如何相互关联的。让我们来探讨一下，在 `longest` 函数的上下文中，这些生命周期注解是如何相互关联的。

<!-- Old headings. Do not remove or links may break. -->

<a id="lifetime-annotations-in-function-signatures"></a>

### 函数签名说明

要在函数签名中使用生命周期注解，我们需要在函数名称和参数列表之间，使用尖括号来声明泛型生命周期参数，就像我们处理泛型类型参数一样。

我们希望该签名能够表达以下约束条件：只要两个参数都有效，返回的引用也一定是有效的。这就是参数生命周期与返回值生命周期之间的关系。我们将这种关系命名为`'a`，然后将其添加到每个引用中，如清单10-21所示。

<Listing number="10-21" file-name="src/main.rs" caption="The `longest` function definition specifying that all the references in the signature must have the same lifetime `'a`">

```rust
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() { x } else { y }
}

```

</Listing>

当我们在 Listing 10-19 中使用`main`函数时，这段代码应该能够成功编译，并生成我们期望的结果。

现在，函数签名告诉Rust：对于某个生命周期`'a`，该函数接受两个参数，这两个参数都是字符串切片，其长度至少与生命周期`'a`相同。函数签名还告诉Rust：从该函数返回的字符串切片的长度也至少与生命周期`'a`相同。实际上，这意味着由`longest`函数返回的引用的生命周期，与函数参数所引用的值的生命周期中较短的那个相同。这些关系正是我们希望Rust在分析这段代码时能够使用的。

请记住，当我们在这个函数签名中指定生命周期参数时，我们并没有改变传入或返回的任何值的生命周期。相反，我们只是指定了借用检查器应该拒绝那些不符合这些约束值的变量。需要注意的是，`longest`这个函数不需要确切知道`x`和`y`会存在多久，它只需要知道有一些作用域可以替代`'a`，从而满足这个签名的要求。

在函数中标注生命周期时，这些标注应该放在函数签名中，而不是函数体内。生命周期的标注成为了函数契约的一部分，就像签名中的类型一样。如果函数签名包含了生命周期的约束信息，那么Rust编译器的分析就会更加简单。如果函数的标注方式或调用方式存在问题，编译器会给出具体的错误提示，从而更精确地指出问题的所在以及相关的约束条件。相反，如果Rust编译器能够更精确地推断出我们对于生命周期关系的意图，那么编译器可能只能指出代码中某个步骤的错误，而无法直接定位到问题的根源。

当我们传递具体类型的引用给 `longest` 时，被替换的具体生命周期实际上是 `x` 的作用域中与 `y` 的作用域重叠的部分。换句话说，泛型生命周期 `'a` 将获得等于 `x` 和 `y` 中较短生命周期的那个生命周期。由于我们将返回的引用标注了相同的生命周期参数 `'a`，因此返回的引用在 `x` 和 `y` 中较短的生命周期持续时间内仍然有效。

让我们看看生命周期注释是如何通过传入具有不同具体生命周期的引用来限制 `longest` 函数的。列表 10-22 就是一个简单的例子。

<Listing number="10-22" file-name="src/main.rs" caption="Using the `longest` function with references to `String` values that have different concrete lifetimes">

```rust
fn main() {
    let string1 = String::from("long string is long");

    {
        let string2 = String::from("xyz");
        let result = longest(string1.as_str(), string2.as_str());
        println!("The longest string is {result}");
    }
}

```

</Listing>

在这个示例中，`string1`在外部作用域的末尾之前是有效的，`string2`在内部作用域的末尾之前是有效的，而`result`引用的是在内部作用域的末尾之前仍然有效的内容。运行这段代码后，你会看到借用检查器会批准该代码；程序会成功编译，并输出`The longest string
is long string is long`。

接下来，让我们来看一个例子，这个例子说明了在`result`中引用的对象的生命周期必须是两个参数中较短的一个。我们将`result`变量的声明移出内部作用域，而将`result`变量的值的赋值操作保留在`string2`的作用域内。然后，我们将使用`result`的`println!`移出内部作用域，但必须在内部作用域结束之后才进行这一操作。这样，Listing 10-23中的代码将无法编译。

<Listing number="10-23" file-name="src/main.rs" caption="Attempting to use `result` after `string2` has gone out of scope">

```rust,ignore,does_not_compile
fn main() {
    let string1 = String::from("long string is long");
    let result;
    {
        let string2 = String::from("xyz");
        result = longest(string1.as_str(), string2.as_str());
    }
    println!("The longest string is {result}");
}

```

</Listing>

当我们尝试编译这段代码时，会遇到这个错误：

```console
$ cargo run
   Compiling chapter10 v0.1.0 (file:///projects/chapter10)
error[E0597]: `string2` does not live long enough
 --> src/main.rs:6:44
  |
5 |         let string2 = String::from("xyz");
  |             ------- binding `string2` declared here
6 |         result = longest(string1.as_str(), string2.as_str());
  |                                            ^^^^^^^ borrowed value does not live long enough
7 |     }
  |     - `string2` dropped here while still borrowed
8 |     println!("The longest string is {result}");
  |                                      ------ borrow later used here

For more information about this error, try `rustc --explain E0597`.
error: could not compile `chapter10` (bin "chapter10") due to 1 previous error

```

该错误表明，为了使 `result` 对 `println!` 语句有效，`string2` 需要在外部作用域的整个范围内都有效。Rust 能够识别这一点，因为我们使用了相同的生命周期参数 `'a` 来标注函数参数和返回值的生命周期。

作为人类，我们可以观察这段代码，发现 `string1` 的长度比 `string2` 更长，因此，`result` 会包含对 `string1` 的引用。由于 `string1` 尚未超出作用域，因此对 `println!` 语句的引用仍然有效。然而，编译器无法确认这种引用是有效的。我们告诉 Rust，由 `longest` 函数返回的引用的生命周期与传入的引用的生命周期中较短的那个相同。因此，借用检查器不允许 Listing 10-23 中的代码存在无效的引用。

请尝试设计更多的实验，这些实验会改变传递给 `longest` 函数的引用的数值和生命周期，以及返回的引用是如何被使用的。在编译之前，对实验是否能够通过借用检查器做出假设；然后，验证你的假设是否正确！

<!-- Old headings. Do not remove or links may break. -->

<a id="thinking-in-terms-of-lifetimes"></a>

### 关系

你需要指定生命周期参数的方式取决于你的函数所做的事情。例如，如果我们修改了`longest`函数的实现，使其总是返回第一个参数，而不是最长的字符串片段，那么我们就不需要在`y`参数上指定生命周期。以下代码可以成功编译：

<Listing file-name="src/main.rs">

```rust
fn longest<'a>(x: &'a str, y: &str) -> &'a str {
    x
}

```

</Listing>

我们已经为参数 `x` 和返回值指定了生命周期参数 `'a`，但并未为参数 `y` 指定生命周期参数，因为 `y` 的生命周期与 `x` 的生命周期或返回值没有任何关系。

当从函数中返回引用时，返回类型的生命周期参数需要与其中一个参数的生命周期参数相匹配。如果返回的引用并不指向任何一个参数，那么它必须指向在该函数内部创建的值。然而，这种引用被称为“悬空引用”，因为该值会在函数执行结束时超出作用域。请考虑以下无法编译的 `longest` 函数实现：

<Listing file-name="src/main.rs">

```rust,ignore,does_not_compile
fn longest<'a>(x: &str, y: &str) -> &'a str {
    let result = String::from("really long string");
    result.as_str()
}

```

</Listing>

在这里，尽管我们为返回类型指定了生命周期参数 `'a`，但此实现仍然无法编译，因为返回值的生命周期与参数的生命周期完全无关。我们得到的错误信息如下：

```console
$ cargo run
   Compiling chapter10 v0.1.0 (file:///projects/chapter10)
error[E0515]: cannot return value referencing local variable `result`
  --> src/main.rs:11:5
   |
11 |     result.as_str()
   |     ------^^^^^^^^^
   |     |
   |     returns a value referencing data owned by the current function
   |     `result` is borrowed here

For more information about this error, try `rustc --explain E0515`.
error: could not compile `chapter10` (bin "chapter10") due to 1 previous error

```

问题在于 `result` 在 `longest` 函数的末尾超出了作用域范围，并被清理掉了。我们还试图从函数中返回对 `result` 的引用。我们无法指定能够改变这种悬空引用的生命周期参数，而Rust也不允许我们创建这样的悬空引用。在这种情况下，最好的解决办法是返回一个拥有所有权的数据类型，而不是引用，这样调用函数就负责清理该值了。

归根结底，生命周期语法旨在连接函数各个参数和返回值的生命周期。一旦这些生命周期被正确连接，Rust就拥有足够的信息来执行内存安全操作，同时禁止那些会导致指针悬空或违反内存安全性的操作。

<!-- Old headings. Do not remove or links may break. -->

<a id="lifetime-annotations-in-struct-definitions"></a>

### 在结构体定义中

到目前为止，我们所定义的结构体都包含拥有型数据。我们可以定义结构体来包含引用，但在这种情况下，我们需要在结构体定义中的每个引用上添加生命周期注解。列表10-24中有一个名为 `ImportantExcerpt` 的结构体，它包含一个字符串切片。

<Listing number="10-24" file-name="src/main.rs" caption="A struct that holds a reference, requiring a lifetime annotation">

```rust
struct ImportantExcerpt<'a> {
    part: &'a str,
}

fn main() {
    let novel = String::from("Call me Ishmael. Some years ago...");
    let first_sentence = novel.split('.').next().unwrap();
    let i = ImportantExcerpt {
        part: first_sentence,
    };
}

```

</Listing>

该结构体包含一个名为 `part` 的单个字段，该字段持有一个字符串切片，且这个字符串切片是一个引用。与通用数据类型类似，我们将通用生命周期参数的名称放在结构体名称的尖括号内，这样我们就可以在结构体定义的内部使用这个生命周期参数。这种注解意味着 `ImportantExcerpt` 的实例不会超出其在 `part` 字段中引用的对象的生命周期。

这里的 `main` 函数创建了一个 `ImportantExcerpt` 结构的实例，该实例持有一个对 `String` 中第一句话的引用，而 `String` 又由变量 `novel` 所拥有。`novel` 中的数据在 `ImportantExcerpt` 的实例创建之前就已经存在了。此外，`novel` 在 `ImportantExcerpt` 的实例离开作用域之前不会离开其作用域，因此 `ImportantExcerpt` 中的引用是有效的。

### 生命周期省略

你已经了解到，每个引用都有一个生命周期，并且需要使用生命周期参数来指定那些使用引用的函数或结构体。然而，在清单4-9中有一个函数，其编译时并未添加生命周期注释，这一情况在清单10-25中再次展示。

<Listing number="10-25" file-name="src/lib.rs" caption="A function we defined in Listing 4-9 that compiled without lifetime annotations, even though the parameter and return type are references">

```rust
fn first_word(s: &str) -> &str {
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

这个函数能够编译而无需使用生命周期注释，这是出于历史原因：在Rust的早期版本（1.0之前），这样的代码是无法编译的，因为每一个引用都需要明确指定其生命周期。在那个时候，函数的签名会被这样编写：

```rust,ignore
fn first_word<'a>(s: &'a str) -> &'a str {
```

在编写了大量的Rust代码之后，Rust团队发现，在某些特定情况下，Rust程序员会反复使用相同的生命周期注解。这些情况是可以预测的，并且遵循一些确定的模式。开发者将这些模式编入了编译器的代码中，这样借用检查器就可以在这些情况下推断出生命周期，而无需显式的注解。

这段Rust历史之所以重要，是因为可能会出现更多确定性模式，并且这些模式会被添加到编译器中。未来，可能只需要更少的生命周期注解了。

在Rust中，用于分析引用模式的规则被称为“生命周期省略规则”。这些并不是程序员需要遵循的规则；它们是一组编译器会考虑的特定情况。如果你的代码符合这些情况，就不需要显式地声明生命周期。

这些省略规则并不能提供完全的推理功能。如果在Rust应用这些规则之后，仍然存在关于引用所属生命周期的歧义，编译器不会猜测剩余引用的生命周期。相反，编译器会发出错误提示，你可以通过添加生命周期注释来解决问题。

函数或方法参数上的生命周期被称为_输入生命周期_，而返回值上的生命周期则被称为_输出生命周期_。

编译器使用三条规则来确定引用对象的生命周期，当没有明确的注释时。第一条规则适用于输入对象的生命周期，第二条和第三条规则适用于输出对象的生命周期。如果编译器执行完这三条规则后，仍然有一些引用对象的生命周期无法确定，那么编译器将会报错并停止执行。这些规则既适用于 `fn` 定义，也适用于 `impl` 块。

第一条规则是，编译器会为每个引用类型的参数分配一个生命周期参数。换句话说，一个只有一个参数的函数会得到一个生命周期参数：`fn foo<'a>(x: &'a i32)`；而一个有两个参数的函数则会得到两个独立的生命周期参数：`fn foo<'a, 'b>(x: &'a i32,
y: &'b i32)`；以此类推。

第二条规则是，如果输入生命周期参数恰好只有一个，那么该生命周期参数将被分配给所有输出生命周期参数： `fn foo<'a>(x: &'a i32)
-> &'a i32`。

第三条规则是：如果存在多个输入生命周期参数，但其中有一个是 `&self` 或 `&mut self`，因为这是一个方法，那么 `self` 的生命周期会被分配给所有输出生命周期参数。这条规则使得方法的读写更加简洁，因为需要的符号更少。

让我们假设自己是编译器。我们将应用这些规则来推断 Listing 10-25 中 `first_word` 函数中的引用的生命周期。该函数的签名开始时，与引用无关的生命周期信息并未出现：

```rust,ignore
fn first_word(s: &str) -> &str {
```

然后，编译器应用第一条规则，该规则规定每个参数都有自己的生命周期。我们像往常一样将其称为 `'a`，因此现在的签名就是 this:

```rust,ignore
fn first_word<'a>(s: &'a str) -> &str {
```

第二条规则适用，因为输入的生命周期恰好只有一个。第二条规则规定，唯一一个输入参数的生命周期会被分配给输出生命周期，因此现在的签名是这样的：

```rust,ignore
fn first_word<'a>(s: &'a str) -> &'a str {
```

现在，这个函数签名中的所有引用都有各自的生命周期，编译器可以继续进行解析，而无需程序员在函数签名中标注这些生命周期。

让我们再看一个例子，这次使用的是 `longest` 函数。在我们在 Listing 10-20 中开始使用这个函数时，该函数并没有生命周期参数。

```rust,ignore
fn longest(x: &str, y: &str) -> &str {
```

让我们应用第一条规则：每个参数都有自己的生命周期。这次我们有两个参数，而不是一个，因此我们有两个生命周期。

```rust,ignore
fn longest<'a, 'b>(x: &'a str, y: &'b str) -> &str {
```

可以看到，第二条规则并不适用，因为存在多个输入生命周期。第三条规则同样不适用，因为 `longest` 是一个函数而不是方法，因此没有任何参数的生命周期是 `self`。经过对三条规则的逐一分析后，我们仍然无法确定返回值的生命周期。这就是为什么在编译清单 10-20 中的代码时出现了错误：编译器虽然处理了生命周期省略规则，但仍然无法确定签名中引用的所有对象的生命周期。

因为第三条规则实际上只适用于方法签名，接下来我们将在那种情况下探讨生命周期，以了解为什么第三条规则意味着我们不必经常在方法签名中标注生命周期。

<!-- Old headings. Do not remove or links may break. -->

<a id="lifetime-annotations-in-method-definitions"></a>

### 方法定义

当我们在一个结构体上实现带有生命周期的方法时，我们使用与泛型类型参数相同的语法，如清单10-11所示。何时声明和使用生命周期参数，取决于这些参数是与结构体字段相关，还是与方法参数和返回值相关。

结构体字段的生命周期名称必须在 `impl` 关键字之后声明，并且必须在结构体名称之后使用，因为这些生命周期是结构体类型的一部分。

在 `impl` 块中的方法签名中，引用可能会与结构体字段中引用的对象的生命周期绑定在一起，也可能相互独立。此外，生命周期省略规则通常使得在方法签名中不需要使用生命周期注释。让我们来看一些使用我们在 Listing 10-24 中定义的名为 `ImportantExcerpt` 的结构的例子。

首先，我们将使用一个名为 `level` 的方法，该方法的唯一参数是一个对`self`的引用，而其返回值是一个 `i32`，这个值并不指向任何东西。

```rust
impl<'a> ImportantExcerpt<'a> {
    fn level(&self) -> i32 {
        3
    }
}

```

在 `impl` 之后的生命周期参数声明以及类型名称之后的使用是必需的，但由于第一个省略规则的存在，我们不需要对 `self` 的引用生命周期进行注释。

以下是一个适用第三生命周期省略规则的例子：

```rust
impl<'a> ImportantExcerpt<'a> {
    fn announce_and_return_part(&self, announcement: &str) -> &str {
        println!("Attention please: {announcement}");
        self.part
    }
}

```

这里有两种输入生命周期，因此Rust会应用第一个生命周期省略规则，分别为 `&self` 和 `announcement` 分配各自的生命周期。由于其中一个参数是 `&self`，所以返回类型的生命周期被设置为 `&self`。这样一来，所有的生命周期都得到了妥善处理。

### 静态生命周期

我们需要讨论的一个特殊生命周期是 `'static`，它表示受影响的引用可以在程序的整个运行期间存在。所有的字符串字面量都具有 `'static` 生命周期，我们可以这样标注：

```rust
let s: &'static str = "I have a static lifetime.";
```

该字符串的文本直接存储在程序的二进制文件中，而该二进制文件始终是可用的。因此，所有字符串字面量的生命周期都是 `'static`。

您可能会在错误信息中看到建议使用 `'static` 生命周期。但在指定 `'static` 作为引用的生命周期之前，请考虑该引用是否真的需要贯穿整个程序的生命周期，以及您是否希望如此。大多数情况下，出现错误信息的提示是因为试图创建悬挂引用或存在可用的生命周期不匹配的情况。在这种情况下，解决方法是修复这些问题，而不是指定 `'static` 生命周期。

<!-- Old headings. Do not remove or links may break. -->

<a id="generic-type-parameters-trait-bounds-and-lifetimes-together"></a>

## 通用类型参数、特质边界与生命周期

让我们简要看一下在一个函数中指定泛型类型参数、特质边界和生命周期的语法！

```rust
use std::fmt::Display;

fn longest_with_an_announcement<'a, T>(
    x: &'a str,
    y: &'a str,
    ann: T,
) -> &'a str
where
    T: Display,
{
    println!("Announcement! {ann}");
    if x.len() > y.len() { x } else { y }
}

```

这是来自清单10-21的`longest`函数，它返回两个字符串切片中较长的那个。但现在它增加了一个额外的参数`ann`，该参数属于泛型类型`T`。这个额外参数可以由任何实现了`Display`特性的类型来填充，具体细节由`where`条款规定。这个额外参数将通过`{}`进行打印，这就是为什么需要`Display`特性绑定。由于生命周期是一种泛型特性，因此生命周期参数`'a`和泛型类型参数`T`应该放在函数名称后面的方括号中的同一列表中。

## 摘要

在本章中，我们讨论了很多内容！现在，既然你已经了解了泛型类型参数、特质和特质边界，以及泛型生命周期参数，那么你就能够编写出适用于多种不同情况的代码，而无需重复编写相同的代码。泛型类型参数使你能够将这些代码应用于不同的类型。特质和特质边界则确保，即使类型是泛型的，代码的行为仍然符合预期。你还学习了如何使用生命周期注解来确保这种灵活的代码不会产生悬空引用。而所有这些分析都在编译时完成，因此不会影响运行时的性能！

信不信由你，关于本章讨论的主题还有很多内容需要学习：第18章介绍了 trait 对象，这是使用 trait 的另一种方式。此外，还有涉及生命周期注解的更复杂场景，这些场景通常只会在非常高级的情境中出现；对于这类内容，你应该阅读[Rust 参考手册]。接下来，你将学习如何在 Rust 中编写测试，以确保你的代码能够正常运行。

[references-and-borrowing]: ch04-02-references-and-borrowing.html#references-and-borrowing
[string-slices-as-parameters]: ch04-03-slices.html#string-slices-as-parameters
[reference]: ../reference/trait-bounds.html
