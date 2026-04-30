## 不安全 Rust

到目前为止，我们所讨论的所有代码都遵循了 Rust 的内存安全保证，这些保证是在编译时强制执行的。然而，Rust 内部还隐藏着一种语言，它并不遵循这些内存安全保证：这种语言被称为 _unsafe Rust_。它虽然功能与普通的 Rust 相同，但提供了额外的功能。

Unsafe Rust的存在是因为，本质上，静态分析是一种保守的方法。当编译器试图判断代码是否遵守了相关规范时，与其接受一些无效的代码，不如拒绝一些有效的代码。虽然这些代码可能暂时没有问题，但如果Rust编译器没有足够的信息来做出判断，它就会拒绝这些代码。在这种情况下，你可以使用unsafe代码来告诉编译器：“相信我，我知道自己在做什么。”不过需要注意的是，使用Unsafe Rust是你自己的风险：如果你错误地使用了unsafe代码，可能会因为内存安全问题而出现问题，比如空指针解引用。

Rust 拥有“不安全”版本的另一个原因是，底层的计算机硬件本身就不安全。如果 Rust 不允许进行不安全操作，那么就无法执行某些任务。Rust 需要允许你进行底层系统编程，比如直接与操作系统交互，甚至编写自己的操作系统。进行底层系统编程正是该语言的目标之一。让我们来探讨一下如何使用不安全的 Rust，以及如何实现这一点。

<!-- Old headings. Do not remove or links may break. -->

<a id="unsafe-superpowers"></a>

### 行使不安全的超能力

要切换到不安全的 Rust，使用 `unsafe` 关键字，然后开始一个新的代码块来包含不安全的代码。在不安全的 Rust 中，你可以执行一些在安全的 Rust 中无法执行的操作，我们将其称为 _不安全的超级能力_。这些超级能力包括：

1. 解引用原始指针。  
1. 调用不安全的函数或方法。  
1. 访问或修改可变的静态变量。  
1. 实现不安全的特性。  
1. 访问 `union`s 的字段。

需要明白的是，`unsafe`并不会关闭借用检查器，也不会禁用Rust的其他安全检查机制。如果你在unsafe代码中使用了引用，仍然会进行相关检查。而`unsafe`这个关键字只是让你能够访问这五个特性，这些特性在内存安全方面不会受到编译器的检查。因此，在unsafe代码块内，你仍然可以获得一定程度的安全性保障。

此外， `unsafe` 并不意味着该代码块中的内容一定具有危险性，或者一定会存在内存安全方面的问题。其目的是作为程序员，你需要确保 `unsafe` 代码块中的代码能够以正确的方式访问内存。

人都是会犯错的，错误是难免的，但是通过要求这五种不安全操作必须放在带有 `unsafe` 注释的块内，你就可以确保任何与内存安全相关的错误都只能发生在 `unsafe` 块内。尽量保持 `unsafe` 块的小规模；当你调查内存漏洞时，你会为此感到庆幸的。

为了尽可能隔离不安全的代码，最好将这些代码封装在一个安全的抽象层中，并提供安全的API。我们将在后面的章节中讨论如何设计不安全的函数和方法。标准库中的某些部分是通过对不安全的代码进行审计后，将其封装为安全的抽象层来实现的。将不安全的代码封装在安全的抽象层中，可以防止使用 `unsafe` 代码时，其功能泄露到那些你或你的用户可能希望使用 `unsafe` 代码实现的功能区域。因为使用安全的抽象层本身就是安全的。

让我们依次来看看这五个不安全的强大功能。我们还将探讨一些为不安全代码提供安全接口的概念。

### 解引用原始指针

在第四章的 [“Dangling References”][dangling-references]<!-- ignore
--> 部分中，我们提到编译器会确保引用始终有效。Unsafe Rust 中有两种新的类型，称为 _raw 指针_，它们与引用类似。与引用一样，raw 指针可以是不可变的，也可以是可变的，分别被表示为 `*const T` 和 `*mut T`。星号并不是解引用操作符；它是类型名称的一部分。在 raw 指针的上下文中，_不可变_意味着解引用后指针不能被直接赋值。

与引用和智能指针不同，原始指针：

- 允许通过同时使用不可变和可变指针，或者多个可变指针指向同一个位置来忽略借用规则
- 不保证指向的有效内存
- 允许为 null
- 不实现任何自动清理机制

通过选择不让 Rust 执行这些保证，你可以放弃有保障的安全性，以获得更高的性能，或者能够与那些 Rust 的保证不适用其他语言或硬件进行交互。

清单20-1展示了如何创建不可变和可变的基础指针。

<Listing number="20-1" caption="Creating raw pointers with the raw borrow operators">

```rust
    let mut num = 5;

    let r1 = &raw const num;
    let r2 = &raw mut num;

```

</Listing>

请注意，在这段代码中我们没有使用 `unsafe` 这个关键字。我们可以在安全的代码中创建原始指针；但是，我们不能在不安全的代码块之外解引用原始指针，这一点你稍后会了解到。

我们通过使用原始借用运算符来创建原始指针： `&raw const num` 用于创建不可变的原始指针，而 `&raw mut num` 则用于创建可变的原始指针。由于我们是直接从局部变量中创建这些指针的，因此我们知道这些特定的原始指针是有效的。但是，我们不能对任何原始指针都做出这样的假设。

为了演示这一点，接下来我们将创建一个原始指针，我们无法确定其有效性。我们将使用关键字 `as` 来转换一个值，而不是使用原始借用运算符。清单 20-2 展示了如何创建一个指向内存中任意位置的原始指针。尝试使用任意内存是未定义的：那个地址可能有数据，也可能没有数据；编译器可能会优化代码，使得根本不存在内存访问；或者程序可能会因分段错误而终止。通常，没有充分的理由编写这样的代码，尤其是在可以使用原始借用运算符的情况下。不过，这种情况也是存在的。

<Listing number="20-2" caption="Creating a raw pointer to an arbitrary memory address">

```rust
    let address = 0x012345usize;
    let r = address as *const i32;

```

</Listing>

请注意，在安全的代码中我们可以创建原始指针，但我们不能通过解引用原始指针来读取它所指向的数据。在 Listing 20-3 中，我们对一个需要 `unsafe` 块的原始指针使用了解引用运算符 `*`。

<Listing number="20-3" caption="Dereferencing raw pointers within an `unsafe` block">

```rust
    let mut num = 5;

    let r1 = &raw const num;
    let r2 = &raw mut num;

    unsafe {
        println!("r1 is: {}", *r1);
        println!("r2 is: {}", *r2);
    }

```

</Listing>

创建指针本身并没有什么坏处；只有当我们试图访问该指针所指向的值时，才可能会遇到无效的值。

另外需要注意的是，在 Listing 20-1 和 20-3 中，我们创建了两个 raw 指针，它们都指向同一个内存位置，而 `num` 存储在这个位置。如果我们尝试创建对 `num` 的不可变引用和可变引用，那么代码将无法编译，因为 Rust 的所有权规则不允许同时存在可变引用和不可变引用。使用 raw 指针时，我们可以创建一个可变指针和一个不可变指针，指向同一个位置，并通过可变指针来修改数据，这可能会导致数据竞争。请注意！

面对这些危险，为什么还要使用原始指针呢？其中一个主要的应用场景是与C语言代码进行交互，正如我们在下一节中将看到的那样。另一个应用场景是构建那些借用检查器无法理解的安全抽象结构。我们将介绍`unsafe`函数，然后以一个使用`unsafe`代码的安全抽象结构的例子为例进行说明。

### 调用不安全的函数或方法

在 unsafe 块中可以执行的第二种操作是调用 unsafe 函数。unsafe 函数和方法的样子与普通函数和方法完全相同，但在定义的其他部分之前，会多出一个 `unsafe`。在这种情况下， `unsafe` 关键字表示该函数有一些我们在调用时必须遵守的要求，因为 Rust 无法保证我们满足了这些要求。通过在 `unsafe` 块中调用 unsafe 函数，我们表明已经阅读了该函数的文档，并且我们愿意承担履行该函数契约的责任。

这里有一个名为 `dangerous` 的不安全函数，在其主体中没有任何操作：

```rust
    unsafe fn dangerous() {}

    unsafe {
        dangerous();
    }

```

我们必须在一个独立的 `unsafe` 块内调用 `dangerous` 函数。如果我们试图在没有 `unsafe` 块的 `dangerous` 中调用该函数，将会出现错误：

```console
$ cargo run
   Compiling unsafe-example v0.1.0 (file:///projects/unsafe-example)
error[E0133]: call to unsafe function `dangerous` is unsafe and requires unsafe block
 --> src/main.rs:4:5
  |
4 |     dangerous();
  |     ^^^^^^^^^^^ call to unsafe function
  |
  = note: consult the function's documentation for information on how to avoid undefined behavior

For more information about this error, try `rustc --explain E0133`.
error: could not compile `unsafe-example` (bin "unsafe-example") due to 1 previous error

```

通过使用 `unsafe` 块，我们向 Rust 表明我们已经阅读了该函数的文档，了解如何正确使用它，并且已经确认自己能够履行该函数的契约要求。

在 `unsafe` 函数的主体中执行不安全操作时，你仍然需要使用 `unsafe` 块，就像在普通函数中一样。如果你忘记了这个规则，编译器会发出警告。这样做有助于我们将 `unsafe` 块保持尽可能小，因为整个函数主体中可能并不需要不安全操作。

#### 对不安全代码进行安全抽象化

仅仅因为某个函数包含不安全的代码，并不意味着我们需要将该整个函数标记为不安全的。实际上，将不安全的代码封装在一个安全的函数中是一种常见的抽象方式。例如，让我们来研究一下标准库中的 `split_at_mut` 函数，该函数包含一些不安全的代码。我们将探讨如何实现它。这种安全的方法是基于可变的切片来定义的：它接受一个切片，并通过在给定索引处分割该切片来将其变为两个切片。清单 20-4 展示了如何使用 `split_at_mut` 函数。

<Listing number="20-4" caption="Using the safe `split_at_mut` function">

```rust
    let mut v = vec![1, 2, 3, 4, 5, 6];

    let r = &mut v[..];

    let (a, b) = r.split_at_mut(3);

    assert_eq!(a, &mut [1, 2, 3]);
    assert_eq!(b, &mut [4, 5, 6]);

```

</Listing>

我们无法仅使用安全的 Rust 来实现这个函数。尝试的方式可能类似于 Listing 20-5，但这样的代码是无法编译的。为了简单起见，我们将 `split_at_mut` 实现为一个函数，而不是方法，并且仅适用于 `i32` 值的切片，而不是适用于 generic type `T`。

<Listing number="20-5" caption="An attempted implementation of `split_at_mut` using only safe Rust">

```rust,ignore,does_not_compile
fn split_at_mut(values: &mut [i32], mid: usize) -> (&mut [i32], &mut [i32]) {
    let len = values.len();

    assert!(mid <= len);

    (&mut values[..mid], &mut values[mid..])
}

```

</Listing>

这个函数首先获取切片的总长度。然后，它通过检查索引是否小于或等于切片长度，来确保传递的索引确实在切片范围内。这个断言意味着，如果我们传递一个大于切片长度的索引来分割切片，函数在尝试使用该索引之前会触发panic。

然后，我们返回一个元组中的两个可变切片：一个从原始切片的起始位置到 `mid` 索引，另一个从 `mid` 到切片的末尾。

当我们尝试编译清单 20-5 中的代码时，会遇到一个错误：

```console
$ cargo run
   Compiling unsafe-example v0.1.0 (file:///projects/unsafe-example)
error[E0499]: cannot borrow `*values` as mutable more than once at a time
 --> src/main.rs:6:31
  |
1 | fn split_at_mut(values: &mut [i32], mid: usize) -> (&mut [i32], &mut [i32]) {
  |                         - let's call the lifetime of this reference `'1`
...
6 |     (&mut values[..mid], &mut values[mid..])
  |     --------------------------^^^^^^--------
  |     |     |                   |
  |     |     |                   second mutable borrow occurs here
  |     |     first mutable borrow occurs here
  |     returning this value requires that `*values` is borrowed for `'1`
  |
  = help: use `.split_at_mut(position)` to obtain two mutable non-overlapping sub-slices

For more information about this error, try `rustc --explain E0499`.
error: could not compile `unsafe-example` (bin "unsafe-example") due to 1 previous error

```

Rust的借用检查器无法理解我们实际上是借用了切片的不同部分；它只知道我们两次都是从同一个切片中借用的。借用切片的不同部分在本质上是可以接受的，因为这两个切片并不重叠。不过，Rust的智能不足以判断这一点。当我们认为某种行为是可以接受的，但Rust却无法判断时，我们就需要使用`unsafe`代码来实现。

清单20-6展示了如何使用 `unsafe` 块、一个原始指针以及一些 unsafe 函数的调用，来实现 `split_at_mut` 的功能。

<Listing number="20-6" caption="Using unsafe code in the implementation of the `split_at_mut` function">

```rust
use std::slice;

fn split_at_mut(values: &mut [i32], mid: usize) -> (&mut [i32], &mut [i32]) {
    let len = values.len();
    let ptr = values.as_mut_ptr();

    assert!(mid <= len);

    unsafe {
        (
            slice::from_raw_parts_mut(ptr, mid),
            slice::from_raw_parts_mut(ptr.add(mid), len - mid),
        )
    }
}

```

</Listing>

请回想一下第4章中 [“The Slice Type”][the-slice-type]<!-- ignore --> 部分的内容。在那里提到，切片是指向某些数据以及切片长度的指针。我们使用 `len` 方法来获取切片的长度，而使用 `as_mut_ptr` 方法来访问切片的原始指针。在这种情况下，由于我们有一个可变的切片，因此 `i32` 会返回类型为 `*mut i32` 的原始指针，我们将该指针存储在变量 `ptr` 中。

我们保持这样的断言：`mid`索引位于该切片内。接下来，我们进入不安全的代码部分：`slice::from_raw_parts_mut`函数接受一个原始指针和一个长度，然后创建一个切片。我们使用这个函数来创建一个从`ptr`开始，长度为`mid`的切片。然后，我们调用`add`方法，并将`mid`作为参数传入`ptr`，以获取一个从`mid`开始的原始指针。接着，我们使用该指针以及剩余的`mid`项来创建一个切片，其长度为剩余的项数。

函数 `slice::from_raw_parts_mut` 是不安全的，因为它接受一个原始指针，并且必须确保这个指针是有效的。对原始指针的 `add` 方法也是不安全的，因为它必须确保偏移位置也是一个有效的指针。因此，我们必须在调用 `slice::from_raw_parts_mut` 和 `add` 之前加上 `unsafe` 块，这样我们才能调用它们。通过查看代码，并添加断言 `mid` 必须小于或等于 `len`，我们可以确定 `unsafe` 块中使用的所有原始指针都是有效的数据指针。这种使用 `unsafe` 的方式是可行且合适的。

请注意，我们不需要将结果函数标记为 `split_at_mut`，而是可以直接从安全的 Rust 环境中调用这个函数。我们为 unsafe 代码创建了一个安全的抽象层，该抽象层实现了这个函数，并且以安全的方式使用 `unsafe` 代码，因为该函数仅从该函数能够访问的数据中创建出有效的指针。

相比之下，在 Listing 20-7 中使用了 `slice::from_raw_parts_mut` 时，当使用切片时很可能会引发崩溃。这段代码获取了一个任意的内存位置，并创建了一个包含 10,000 个元素的切片。

<Listing number="20-7" caption="Creating a slice from an arbitrary memory location">

```rust
    use std::slice;

    let address = 0x01234usize;
    let r = address as *mut i32;

    let values: &[i32] = unsafe { slice::from_raw_parts_mut(r, 10000) };

```

</Listing>

我们并不拥有这个任意位置的内存，也无法保证这段代码所创建的切片包含有效的 `i32` 值。试图将 `values` 当作有效的切片使用，会导致未定义的行为。

#### 使用 `extern` 函数调用外部代码

有时候，你的 Rust 代码可能需要与用其他语言编写的代码进行交互。为此，Rust 提供了关键字 `extern`，它有助于创建和使用_Foreign Function Interface (FFI)__，这是一种让一种编程语言定义函数，并让另一种不同的（外语）编程语言调用这些函数的方式。

清单20-8展示了如何设置与C标准库中的`abs`函数的集成。在`extern`块中声明的函数通常不适合在Rust代码中调用，因此`extern`块也必须进行标记。其原因是其他语言并不强制执行Rust的规则和保证，而Rust也无法进行这些检查，因此确保安全的责任落在程序员身上。

**清单 20-8:** *src/main.rs* — 声明并调用一个在另一种语言中定义的 `extern` 函数

```rust
unsafe extern "C" {
    fn abs(input: i32) -> i32;
}

fn main() {
    unsafe {
        println!("Absolute value of -3 according to C: {}", abs(-3));
    }
}

```

在 `unsafe extern "C"` 块中，我们列出了我们希望调用其他语言的外部函数的名称和签名。 `"C"` 部分定义了该外部函数所使用的 _应用程序二进制接口 (ABI)_：ABI 决定了在汇编级别如何调用该函数。 `"C"` ABI 是最常见的类型，遵循 C 编程语言中的 ABI 规范。关于 Rust 支持的所有 ABI 的信息可以在 [the Rust Reference][ABI] 中找到。

在 `unsafe extern` 块中声明的每个项都是隐式地不安全的。然而，某些外部库函数是可以安全调用的。例如，C语言标准库中的 `abs` 函数没有任何内存安全方面的考虑，我们知道它可以以任何 `i32` 形式被调用。在这种情况下，我们可以使用 `safe` 关键字来表明这个特定的函数即使位于 `unsafe extern` 块中也是安全的。一旦我们进行了这样的修改，调用它就不再需要 `unsafe` 块了，如清单20-9所示。

**清单 20-9:** *src/main.rs* — 在 `unsafe extern` 块内明确地将函数标记为 `safe`，并安全地调用该函数

```rust
unsafe extern "C" {
    safe fn abs(input: i32) -> i32;
}

fn main() {
    println!("Absolute value of -3 according to C: {}", abs(-3));
}

```

将某个函数标记为 `safe` 并不能使其本质上变得安全！这实际上相当于你向 Rust 做出的一个承诺，即该函数是安全的。确保这个承诺得到履行仍然属于你的责任！

#### 使用其他语言调用 Rust 函数

我们还可以使用 `extern` 来创建一个接口，让其他语言能够调用 Rust 函数。我们不会创建一个完整的 `extern` 块，而是添加 `extern` 关键字，并在 `fn` 关键字之前指定要使用的 ABI。我们还需要添加 `#[unsafe(no_mangle)]` 注释，以告诉 Rust 编译器不要修改这个函数的名称。_名称修改_是指编译器将我们为函数指定的名称改为另一个名称，这个新的名称包含了更多信息，供编译过程的其他部分使用，但可读性较差。每种编程语言的编译器对名称的修改方式都不同，因此为了让 Rust 函数可以被其他语言调用，我们必须禁用 Rust 编译器的名称修改功能。这样做是不安全的，因为在没有内置名称修改功能的情况下，不同库之间可能会出现名称冲突。因此，我们有责任确保所选的名称在未被修改的情况下是安全的，适合导出。

在以下示例中，我们使得 `call_from_c` 函数能够在 C 代码中访问，该函数经过编译后成为一个共享库，并可以从 C 代码中链接使用。

```
#[unsafe(no_mangle)]
pub extern "C" fn call_from_c() {
    println!("Just called a Rust function from C!");
}
```

这种使用 `extern` 的方式要求在属性中使用 `unsafe`，而不是在 `extern` 块中。

### 访问或修改可变静态变量

在这本书中，我们还没有讨论全局变量。虽然 Rust 支持全局变量，但在 Rust 的所有权规则下，使用全局变量可能会带来问题。如果两个线程访问同一个可变的全局变量，可能会导致数据竞争。

在Rust中，全局变量被称为_静态_变量。清单20-10展示了一个静态变量的声明和使用示例，该变量的值是一个字符串切片。

**清单 20-10:** *src/main.rs* — 定义和使用不可变的静态变量

```rust
static HELLO_WORLD: &str = "Hello, world!";

fn main() {
    println!("value is: {HELLO_WORLD}");
}

```

静态变量与常量类似，我们在第3章的[“Declaring Constants”][constants]<!-- ignore -->部分讨论过。按照惯例，静态变量的名称采用 `SCREAMING_SNAKE_CASE` 格式。静态变量只能存储具有 `'static` 生命周期的引用，这意味着Rust编译器可以自行确定生命周期，我们无需显式进行注释说明。访问不可变的静态变量是安全的。

常数与不可变静态变量之间的一个微妙区别在于，静态变量中的值在内存中具有固定的地址。使用这些值时，总是会访问相同的数据。而常数则可以在使用时复制其数据。另一个区别是，静态变量可以是可变的。访问和修改可变的静态变量是_不安全的_。清单20-11展示了如何声明、访问和修改一个名为 `COUNTER` 的可变静态变量。

**列表 20-11:** *src/main.rs* — 对可变静态变量进行读取或写入是不安全的。

```rust
static mut COUNTER: u32 = 0;

/// SAFETY: Calling this from more than a single thread at a time is undefined
/// behavior, so you *must* guarantee you only call it from a single thread at
/// a time.
unsafe fn add_to_count(inc: u32) {
    unsafe {
        COUNTER += inc;
    }
}

fn main() {
    unsafe {
        // SAFETY: This is only called from a single thread in `main`.
        add_to_count(3);
        println!("COUNTER: {}", *(&raw const COUNTER));
    }
}

```

与普通变量一样，我们使用 `mut` 关键字来指定可变性。任何从 `COUNTER` 读取或写入数据的代码都必须位于 `unsafe` 块内。清单 20-11 中的代码能够编译并输出 `COUNTER: 3`，因为该程序是单线程的。如果多个线程访问 `COUNTER`，可能会导致数据竞争，因此这属于未定义的行为。因此，我们需要将整个函数标记为 `unsafe`，并说明其安全限制，以便调用该函数的人了解其中的风险以及不允许进行的操作。

每当我们编写不安全的函数时，通常会以 `SAFETY` 开头写一条注释，解释调用者需要做什么来确保函数能够安全地被调用。同样地，每当我们执行不安全的操作时，也会以 `SAFETY` 开头写一条注释，来解释如何遵守安全规则。

此外，编译器默认会拒绝任何试图通过编译器检查来创建对可变静态变量的引用的尝试。你必须通过添加`#[allow(static_mut_refs)]`注释，或者通过使用某些原始借用运算符来创建原始指针，来明确排除这些检查的保护措施。这包括那些以不可见方式创建引用的情况，比如在代码清单中的`println!`用法。要求对静态可变变量的引用必须通过原始指针来创建，有助于使使用这些变量的安全要求更加明确。

由于可变数据是可以全局访问的，因此很难确保不会出现数据竞争。这就是为什么Rust认为可变静态变量是不安全的。在可能的情况下，最好使用我们在第16章中讨论的并发技术和线程安全的智能指针，这样编译器就能检查不同线程之间的数据访问是否安全进行。

### 实现 Unsafe 特性

我们可以使用 `unsafe` 来实现一个不安全的特性。当一个特性的至少有一个方法包含编译器无法验证的不变性时，该特性就被称为不安全的。我们通过在 `trait` 前面添加 `unsafe` 关键字，并将特性的实现标记为 `unsafe` 来声明一个特性是 `unsafe` 的，如清单 20-12 所示。

<Listing number="20-12" caption="Defining and implementing an unsafe trait">

```rust
unsafe trait Foo {
    // methods go here
}

unsafe impl Foo for i32 {
    // method implementations go here
}

```

</Listing>

通过使用 `unsafe impl`，我们承诺会维护那些编译器无法验证的不变量。

例如，请回想我们在第16章的[“Extensible Concurrency with `Send` and `Sync`”][send-and-sync]<!-- ignore -->⊂部分讨论过的`Send`和`Sync`标记特性。如果我们的类型完全由实现`Send`和`Sync`的其他类型组成，编译器会自动实现这些特性。如果我们实现了一个包含未实现`Send`或`Sync`的类型，比如原始指针，并且我们希望将该类型标记为`Send`或`Sync`，那么我们必须使用`unsafe`。Rust无法验证我们的类型是否能够安全地跨线程传输或从多个线程访问；因此，我们需要手动进行这些检查，并通过`unsafe`来标明这一点。

### 访问联合类型的字段

最后一个仅适用于 `unsafe` 的操法是访问联合体的字段。  
*联合体* 类似于 `struct`，但在特定实例中一次只使用一个声明过的字段。联合体主要用于与 C 代码中的联合体进行交互。访问联合体的字段是不安全的，因为 Rust 无法保证联合体实例中当前存储的数据的类型。您可以在 [the Rust Reference][unions] 中了解更多关于联合体的信息。

### 使用 Miri 检查不安全代码

在编写不安全代码时，你可能需要检查自己所编写的代码是否真正安全且正确。实现这一目标的最佳方法之一就是使用Miri，这是Rust官方提供的用于检测未定义行为的工具。虽然借用检查器是一种在编译时生效的静态工具，但Miri则是一种在运行时生效的动态工具。它通过运行你的程序或其测试套件来检测你的代码，并判断你是否违反了Rust所规定的规则。

使用 Miri 需要安装夜版 Rust（关于夜版 Rust的详细信息，我们将在[Appendix G: How Rust is Made and “Nightly Rust”][nightly]<!-- ignore -->中详细讨论）。你可以通过输入 `rustup
+nightly component add miri` 来安装夜版 Rust 和 Miri 工具。这并不会改变你的项目所使用的 Rust 版本；它只是将工具添加到你的系统中，以便你在需要的时候使用它。你可以通过输入 `cargo +nightly miri run` 或 `cargo +nightly miri test` 来运行 Miri 对某个项目进行处理。

为了了解这有多么有用，请考虑当我们将其应用于清单20-7时会发生什么。

```console
$ cargo +nightly miri run
   Compiling unsafe-example v0.1.0 (file:///projects/unsafe-example)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.01s
     Running `file:///home/.rustup/toolchains/nightly/bin/cargo-miri runner target/miri/debug/unsafe-example`
warning: integer-to-pointer cast
 --> src/main.rs:5:13
  |
5 |     let r = address as *mut i32;
  |             ^^^^^^^^^^^^^^^^^^^ integer-to-pointer cast
  |
  = help: this program is using integer-to-pointer casts or (equivalently) `ptr::with_exposed_provenance`, which means that Miri might miss pointer bugs in this program
  = help: see https://doc.rust-lang.org/nightly/std/ptr/fn.with_exposed_provenance.html for more details on that operation
  = help: to ensure that Miri does not miss bugs in your program, use Strict Provenance APIs (https://doc.rust-lang.org/nightly/std/ptr/index.html#strict-provenance, https://crates.io/crates/sptr) instead
  = help: you can then set `MIRIFLAGS=-Zmiri-strict-provenance` to ensure you are not relying on `with_exposed_provenance` semantics
  = help: alternatively, `MIRIFLAGS=-Zmiri-permissive-provenance` disables this warning
  = note: BACKTRACE:
  = note: inside `main` at src/main.rs:5:13: 5:32

error: Undefined Behavior: pointer not dereferenceable: pointer must be dereferenceable for 40000 bytes, but got 0x1234[noalloc] which is a dangling pointer (it has no provenance)
 --> src/main.rs:7:35
  |
7 |     let values: &[i32] = unsafe { slice::from_raw_parts_mut(r, 10000) };
  |                                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ Undefined Behavior occurred here
  |
  = help: this indicates a bug in the program: it performed an invalid operation, and caused Undefined Behavior
  = help: see https://doc.rust-lang.org/nightly/reference/behavior-considered-undefined.html for further information
  = note: BACKTRACE:
  = note: inside `main` at src/main.rs:7:35: 7:70

note: some details are omitted, run with `MIRIFLAGS=-Zmiri-backtrace=full` for a verbose backtrace

error: aborting due to 1 previous error; 1 warning emitted


```

Miri正确地提醒我们，我们将一个整数强制转换为指针，这可能会带来问题。但是，Miri无法确定是否存在问题，因为她不知道指针的起源。此外，Miri返回的错误会导致 Listing 20-7 中的代码出现未定义行为，因为我们有一个指向无效地址的指针。多亏了Miri，我们现在知道存在未定义行为的风险，并且我们可以思考如何使代码更加安全。在某些情况下，Miri甚至能够给出关于如何修复错误的建议。

Miri并不能捕捉到你在编写不安全代码时可能犯的所有错误。Miri是一个动态分析工具，因此它只能捕捉到实际运行时的代码问题。这意味着你需要结合良好的测试技术来使用它，以提高对编写的不安全代码的信心。此外，Miri并不能涵盖代码可能出现的所有问题。

换句话说，如果Miri确实发现了问题，那就意味着存在错误。但是，仅仅因为Miri没有发现错误，并不意味着就没有问题存在。不过，Miri确实有可能发现很多问题。试着在本章中其他不安全的代码示例上运行它，看看它会显示什么结果吧！

您可以在 [its GitHub repository][miri] 了解更多关于 Miri 的信息。

<!-- Old headings. Do not remove or links may break. -->

<a id="when-to-use-unsafe-code"></a>

### 正确使用 Unsafe 代码

使用 `unsafe` 来使用刚才提到的五种超能力之一并没有错，甚至也不会引起不满。但是，要正确使用 `unsafe` 代码则更为复杂，因为编译器无法确保内存安全性的正确实现。当你有理由使用 `unsafe` 代码时，你可以这样做。而使用显式的 `unsafe` 注释则有助于在问题出现时更容易追踪问题的来源。每当你编写不安全代码时，可以使用 Miri 来帮助你更加确信所编写的代码符合 Rust 的规则。

如需深入了解如何有效使用不安全的 Rust，请阅读 Rust 的官方指南 `unsafe`, [The Rustonomicon][nomicon]。

[dangling-references]: ch04-02-references-and-borrowing.html#dangling-references
[ABI]: ../reference/items/external-blocks.html#abi
[constants]: ch03-01-variables-and-mutability.html#declaring-constants
[send-and-sync]: ch16-04-extensible-concurrency-sync-and-send.html
[the-slice-type]: ch04-03-slices.html#the-slice-type
[unions]: ../reference/items/unions.html
[miri]: https://github.com/rust-lang/miri
[editions]: appendix-05-editions.html
[nightly]: appendix-07-nightly-rust.html
[nomicon]: https://doc.rust-lang.org/nomicon/
