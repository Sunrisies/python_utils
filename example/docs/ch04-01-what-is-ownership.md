## 什么是所有权？

**所有权**是一组规则，用于规范Rust程序如何管理内存。所有程序在运行时都必须管理其对计算机内存的使用方式。某些语言采用垃圾回收机制，会在程序运行过程中自动清理不再使用的内存；而在其他语言中，程序员必须主动分配和释放内存。Rust采用了第三种方法：通过一套由编译器进行验证的规则来管理内存的所有权。如果违反了这些规则，程序将无法编译。所有权的这些特性不会在程序运行时导致程序运行速度变慢。

因为所有权对许多程序员来说是一个新的概念，所以需要一些时间来适应。好消息是，你越熟悉Rust以及所有权系统的规则，就越能自然而然地编写出安全且高效的代码。坚持下去吧！

当你理解了所有权概念之后，你就能为理解让 Rust 如此独特的功能打下坚实的基础。在本章中，你将通过一些示例来学习所有权，这些示例的重点是一个非常常见的数据结构：字符串。

> ### 栈和堆
>
> 许多编程语言并不要求开发者经常考虑栈和堆的概念。但在像Rust这样的系统编程语言中，一个值是在栈上还是堆上，会影响到程序的运行方式以及为何需要做出某些决策。在本章的后面部分，将会详细讨论所有权与栈和堆的关系，因此这里先简单介绍一下相关知识。
>
> 栈和堆都是运行时可供代码使用的内存部分，但它们的结构有所不同。栈按照添加值的顺序来存储数据，并按照相反的顺序删除数据。这种存储方式被称为“后进先出”（LIFO）。可以想象一个盘子堆：当你添加更多的盘子时，会把它们放在堆的顶端；当你需要一个盘子时，就从顶端取一个出来。如果从中间或底部添加或移除盘子，效果就会大打折扣！向栈中添加数据称为“将数据压入栈中”，而从栈中移除数据则称为“从栈中弹出数据”。所有存储在栈上的数据都必须具有已知的固定大小。而在编译时大小未知或可能发生变化的数据，则必须存储在堆上。
>
> 堆的组织方式则相对松散一些：当你向堆中存储数据时，需要申请一定大小的空间。内存分配器会在堆中找到足够大的空闲空间，并将其标记为正在使用，然后返回一个“指针”，这个指针就是该位置的地址。这个过程被称为“在堆上分配内存”，有时也简称为“分配”。需要注意的是，指向堆的指针本身具有已知的固定大小，因此可以将指针存储在栈上，但当你需要实际的数据时，就必须通过指针来访问它。这就像在餐厅就座一样：当你进入餐厅时，需要告知服务员你的人数，然后服务员会为你找到一张合适的桌子。如果有人迟到，他们可以询问你的座位位置以便找到你。
>
> 向栈中压入数据比在堆上分配数据要快，因为分配器不需要再搜索新的存储位置；数据总是存储在栈的顶端。相比之下，在堆上分配空间则需要更多的操作，因为分配器需要先找到足够大的空间来存放数据，然后再进行相关的管理操作。> 分配。  
> 访问堆中的数据通常比访问栈中的数据要慢，因为需要通过一个指针来定位数据。现代处理器在内存中跳跃的次数越少，其运行速度就越快。继续这个类比，想象一家餐厅的服务器从多个桌子接收订单。最有效的方法是在处理一个桌子的订单之前，先处理另一个桌子的订单。而从桌子A获取一个订单，然后从桌子B获取一个订单，然后再从桌子A获取一个订单，最后从桌子B获取一个订单，这样的过程会慢得多。同样，如果处理器处理的数据彼此靠近（就像在栈上一样），那么它的工作效率会更高，而不是处理远离其他数据的数据（就像在堆上一样）。  
> 当你的代码调用一个函数时，被传递给函数的数据（可能包括指向堆中数据的指针）以及函数的局部变量都会被压入栈中。当函数执行完毕后，这些数据会被从栈中弹出。  
> 跟踪哪些代码部分使用了堆中的哪些数据，尽量减少堆中重复数据的数量，并清理未使用的数据，避免空间不足的问题，这些都是所有权机制需要解决的问题。一旦你理解了所有权机制，就不必经常考虑栈和堆了。但知道所有权的主要目的是为了管理堆中的数据，这有助于解释为什么堆的数据管理方式会如此运作。

### 所有权规则

首先，让我们来看看所有权规则。在通过示例来理解这些规则时，请记住这些规则：

在Rust中，每个值都有一个_所有者_。  
一次只能有一个所有者。  
当所有者超出作用域时，该值将被丢弃。

### 变量作用域

既然我们已经了解了基本的 Rust 语法，那么就不会在示例中包含所有的 `fn main() {` 代码了。因此，如果你正在跟随学习，请务必将下面的示例手动放在 `main` 函数内。这样一来，我们的示例就会更加简洁，我们可以专注于实际的内容，而不是那些样板代码。

作为所有权的第一个例子，我们将看看一些变量的作用域。所谓“作用域”，指的是在程序中某个变量有效的范围。以以下变量为例：

```rust
let s = "hello";
```

变量 `s` 指的是一个字符串字面量，该字符串的值被硬编码到程序的文本中。该变量从声明那一刻起一直有效，直到当前作用域的结束。列表4-1展示了一个程序，其中包含了注释，说明了变量 `s` 在程序中的有效范围。

<Listing number="4-1" caption="A variable and the scope in which it is valid">

```rust
    {                      // s is not valid here, since it's not yet declared
        let s = "hello";   // s is valid from this point forward

        // do stuff with s
    }                      // this scope is now over, and s is no longer valid

```

</Listing>

换句话说，这里有两个重要的时间点：

- 当 `s` 进入作用域时，它是有效的。
- 它一直保持有效，直到它离开作用域。

在这一点上，作用域与变量有效时间之间的关系与其他编程语言中的情况类似。现在，我们将在此基础上进一步学习，引入`String`这种类型。

### `String` 类型

为了说明所有权规则，我们需要一种比第3章[“数据类型”][data-types]<!-- ignore -->部分中讨论的更复杂的数据类型。之前讨论的类型都是已知大小的，可以存储在栈上，并在其作用域结束时从栈上弹出。此外，这些类型可以很容易地复制，以创建新的、独立的实例，以便在其他代码的不同作用域中需要使用相同的值。但我们现在想要研究的是存储在堆上的数据，以及Rust是如何知道何时清理这些数据的。`String`类型就是一个很好的例子。

我们将重点讨论 `String` 中与所有权相关的部分。这些方面也适用于其他复杂的数据类型，无论是标准库提供的还是由用户自己创建的数据类型。关于 `String` 中与非所有权相关的方面，我们将在[第8章][ch8]<!-- ignore -->中进行讨论。

我们已经了解了字符串字面量，其中字符串值被硬编码到程序中。字符串字面量非常方便，但它们并不适用于所有需要使用文本的情况。其中一个原因是它们是不可变的。另一个原因是，在编写代码时，我们无法预知每个字符串值的具体情况：例如，如果我们想要接收用户输入并将其存储起来，该怎么办呢？正是为了这些情况，Rust提供了`String`类型。这种类型可以管理存储在堆上的数据，因此能够存储我们在编译时无法预知的文本量。你可以使用`from`函数从字符串字面量创建一个`String`类型，如下所示：

```rust
let s = String::from("hello");
```

双冒号`::`运算符允许我们将这个特定的`from`函数命名空间放在`String`类型下，而不是使用某种像`string_from`这样的名称。我们将在第五章的[“Methods”][methods]<!--
ignore -->部分进一步讨论这种语法，同时也会在第七章的[“Paths for Referring to an Item in the Module Tree”][paths-module-tree]<!-- ignore -->部分介绍如何使用模块进行命名空间管理。

这种字符串是可以被修改的：

```rust
    let mut s = String::from("hello");

    s.push_str(", world!"); // push_str() appends a literal to a String

    println!("{s}"); // this will print `hello, world!`

```

那么，这里有什么区别呢？为什么 `String` 可以被修改，而字面量却不能呢？区别在于这两种类型在处理内存方面的方式不同。

### 内存与分配

在字符串字面量的情况下，我们可以在编译时确定其内容，因此文本会被直接硬编码到最终的可执行文件中。这就是为什么字符串字面量既快速又高效的原因。不过，这些特性仅源于字符串字面量的不可变性。不幸的是，对于那些在编译时无法确定大小，并且在程序运行过程中可能会发生变化的内容，我们无法将整个内存块直接放入二进制文件中。

在 `String` 类型中，为了支持可变的、可增长的文本数据，我们需要在堆上分配一定量内存，这部分内存的内容在编译时是未知的。这意味着：

- 内存必须在运行时从内存分配器中请求。
- 我们需要一种方式，在我们使用 `String` 结束后，将这部分内存返回给分配器。

第一部分由我们来完成：当我们调用 `String::from` 时，其实现会请求所需的内存。这在各种编程语言中都是普遍存在的现象。

不过，第二部分的情况有所不同。在那些拥有垃圾收集器的语言中，垃圾收集器会跟踪并清理不再被使用的内存，我们无需操心这个问题。而在大多数没有垃圾收集器的语言中，识别内存何时不再被使用，并调用代码来显式释放内存，就成为了我们的责任，就像我们请求分配内存一样。正确地执行这一操作历来都是一个棘手的编程问题。如果我们忽略了这一点，就会浪费内存。如果我们过早地释放内存，就会得到无效的变量。如果我们多次释放内存，那也是个错误。我们需要确保每一个 `allocate` 都对应一个确切的 `free`。

Rust采取了不同的方式：一旦拥有该内存变量的变量超出作用域，内存就会自动被归还。下面是我们从Listing 4-1中得到的代码示例，其中使用了`String`而不是字符串字面量。

```rust
    {
        let s = String::from("hello"); // s is valid from this point forward

        // do stuff with s
    }                                  // this scope is now over, and s is no
                                       // longer valid

```

在某个自然的点上，我们可以将 `String` 需要的内存返还给分配器：即当 `s` 超出作用域时。当变量超出作用域时，Rust会为我们调用一个特殊函数。这个函数被称为 `drop`，而 `String` 的作者可以在这里编写代码来返还内存。Rust 会在闭合的括号处自动调用 `drop`。

注意：在C++中，这种在对象生命周期结束时释放资源的模式有时被称为“资源获取即初始化”（RAII）。如果你曾经使用过RAII模式，那么Rust中的`drop`函数对你来说应该很熟悉。

这种模式对Rust代码的编写方式产生了深远的影响。目前看来它可能很简单，但在更复杂的情况下，当我们需要多个变量共享堆上分配的数据时，代码的行为可能会出乎意料。现在让我们来探讨一下这些情况。

<!-- Old headings. Do not remove or links may break. -->

<a id="ways-variables-and-data-interact-move"></a>

#### 变量与移动操作的数据交互

在Rust中，多个变量可以以不同的方式与相同的数据进行交互。列表4-2展示了一个使用整数的示例。

<Listing number="4-2" caption="Assigning the integer value of variable `x` to `y`">

```rust
    let x = 5;
    let y = x;

```

</Listing>

我们可以推测这是在做什么：“将值 `5` 绑定到 `x`；然后，在 `x` 中复制该值，并将其绑定到 `y`。”现在，我们有两个变量，分别是 `x` 和 `y`，这两个变量的值都等于 `5`。确实如此，因为整数是具有已知固定大小的简单值，而这两个 `5` 值被推到了栈上。

现在让我们来看看 `String` 版本：

```rust
    let s1 = String::from("hello");
    let s2 = s1;

```

看起来非常相似，因此我们可以假设其运作方式应该是相同的：也就是说，第二行会复制 `s1` 中的值，并将其绑定到 `s2` 中。但实际上并非如此。

请查看图4-1，了解 `String` 在覆盖层下发生了什么变化。一个 `String` 由三部分组成，如左侧所示：指向存储字符串内容的内存的指针、长度以及容量。这一组数据存储在栈上。右侧则是存储实际内容的堆内存。

<img alt="Two tables: the first table contains the representation of s1 on the
stack, consisting of its length (5), capacity (5), and a pointer to the first
value in the second table. The second table contains the representation of the
string data on the heap, byte by byte." src="img/trpl04-01.svg" class="center"
style="width: 50%;" />

图4-1：内存中存储的`String`，其中包含了绑定在`"hello"`上的`s1`</span>值

“长度”指的是 `String` 的内容当前所使用的内存大小，以字节为单位。“容量”则是指`String`从分配器那里获得的总内存大小，同样以字节为单位。虽然长度与容量之间存在差异，但在这种上下文中并不重要，因此目前可以忽略容量这一参数。

当我们把 `s1` 赋值给 `s2` 时， `String` 数据会被复制，也就是说，我们复制了栈上的指针、长度以及容量。但是，我们不会复制指针所指向的堆上的数据。换句话说，内存中的数据表示形式如图 4-2 所示。

<img alt="Three tables: tables s1 and s2 representing those strings on the
stack, respectively, and both pointing to the same string data on the heap."
src="img/trpl04-02.svg" class="center" style="width: 50%;" />

<span class="caption"> 图4-2：变量在内存中的表示形式  
`s2` 该变量包含指向 `s1`</span> 的指针、长度以及容量信息。

这种表示方式并不像图4-3那样，而图4-3展示的是如果Rust同时复制堆数据时的内存状态。如果Rust采用这种方式，那么当堆上的数据量较大时，操作 `s2 = s1` 在运行性能方面可能会非常低效。

<img alt="Four tables: two tables representing the stack data for s1 and s2,
and each points to its own copy of string data on the heap."
src="img/trpl04-03.svg" class="center" style="width: 50%;" />

图4-3：如果Rust也复制了堆数据，那么`s2 = s1`可能还会产生其他影响。

之前我们提到过，当变量超出作用域时，Rust会自动调用 `drop` 函数，并清理该变量的堆内存。但是，图4-2显示，两个数据指针都指向同一个位置。这是一个问题：当 `s2` 和 `s1` 都超出作用域时，它们都会试图释放相同的内存。这种情况被称为“双重释放”错误，是我们之前提到的内存安全漏洞之一。多次释放内存可能会导致内存损坏，进而可能引发安全漏洞。

为了确保内存安全，在 `let s2 = s1;` 这一行之后，Rust 认为 `s1` 不再有效。因此，当 `s1` 超出作用域时，Rust 不需要释放任何内存。请查看在 `s2` 创建之后尝试使用 `s1` 会发生什么；这是无法工作的。

```rust,ignore,does_not_compile
    let s1 = String::from("hello");
    let s2 = s1;

    println!("{s1}, world!");

```

你会遇到这样的错误，因为Rust禁止你使用已被无效的引用。

```console
$ cargo run
   Compiling ownership v0.1.0 (file:///projects/ownership)
error[E0382]: borrow of moved value: `s1`
 --> src/main.rs:5:16
  |
2 |     let s1 = String::from("hello");
  |         -- move occurs because `s1` has type `String`, which does not implement the `Copy` trait
3 |     let s2 = s1;
  |              -- value moved here
4 |
5 |     println!("{s1}, world!");
  |                ^^ value borrowed here after move
  |
  = note: this error originates in the macro `$crate::format_args_nl` which comes from the expansion of the macro `println` (in Nightly builds, run with -Z macro-backtrace for more info)
help: consider cloning the value if the performance cost is acceptable
  |
3 |     let s2 = s1.clone();
  |                ++++++++

For more information about this error, try `rustc --explain E0382`.
error: could not compile `ownership` (bin "ownership") due to 1 previous error

```

如果你在其他语言编程时听说过“浅层复制”和“深层复制”这些术语，那么复制指针、长度以及容量而不复制数据这个概念，听起来就像是一种浅层复制。但实际上，由于Rust会失效第一个变量的值，因此这种操作被称为“移动”。在示例中，我们会说 `s1` 被“移动”到了 `s2` 中。那么，实际发生的情况如图4-4所示。

<img alt="Three tables: tables s1 and s2 representing those strings on the
stack, respectively, and both pointing to the same string data on the heap.
Table s1 is grayed out because s1 is no longer valid; only s2 can be used to
access the heap data." src="img/trpl04-04.svg" class="center" style="width:
50%;" />

图4-4：在 `s1` 被无效化之后，内存中的表示形式变为 </span>

这解决了我们的问题！只有 `s2` 是有效的，当它超出作用域时，它就能单独释放内存，我们就完成了。

此外，这里还隐含了一个设计选择：Rust永远不会自动创建数据的“深度”副本。因此，任何自动复制操作在运行时性能方面可以被认为是不耗费资源的。

#### 作用域与赋值

对于通过 `drop` 函数释放内存、控制范围以及所有权之间的关系，情况也是类似的。当你将一个全新的值赋给一个现有的变量时，Rust 会立即调用 `drop` 函数来释放原始值所占用的内存。例如，考虑以下代码：

```rust
    let mut s = String::from("hello");
    s = String::from("ahoy");

    println!("{s}, world!");

```

我们首先声明一个变量 `s`，并将其绑定到值为 `"hello"` 的 `String`。接着，我们立即创建一个新的 `String`，其值为 `"ahoy"`，并将其赋值给 `s`。此时，没有任何东西再指向堆中的原始值了。图 4-5 展示了当前栈和堆的数据结构：

<img alt="One table representing the string value on the stack, pointing to
the second piece of string data (ahoy) on the heap, with the original string
data (hello) grayed out because it cannot be accessed anymore."
src="img/trpl04-05.svg" class="center" style="width: 50%;" />

图4-5：在初始值被完全替换后，内存中的表示形式

因此，原始字符串会立即超出作用域。Rust会立即执行 `drop` 函数，并且其内存也会立即被释放。当我们最后打印该值时，它将会变成 `"ahoy, world!"`。

<!-- Old headings. Do not remove or links may break. -->

<a id="ways-variables-and-data-interact-clone"></a>

#### 变量与克隆数据的交互

如果我们真的想要深度复制 `String` 的堆数据，而不仅仅是栈数据，我们可以使用一种常见的方法，叫做 `clone`。我们将在第五章中讨论这种方法的语法，但由于方法在许多编程语言中都是常见的特性，你可能之前就已经见过它们了。

以下是 `clone` 方法的一个使用示例：

```rust
    let s1 = String::from("hello");
    let s2 = s1.clone();

    println!("s1 = {s1}, s2 = {s2}");

```

这个方式运行得很正常，并且确实实现了图4-3中所示的行为，其中堆数据确实被复制了。

当你看到 `clone` 这样的调用时，就知道有一些任意的代码正在被执行，而且这些代码可能会消耗大量资源。这是一个直观的提示，表明有某些不同的事情正在发生。

#### 仅栈数据：复制

还有一个我们还没有讨论的细节。这段代码使用的是整数——其中一部分在清单4-2中展示过——它是有效且可以运行的。

```rust
    let x = 5;
    let y = x;

    println!("x = {x}, y = {y}");

```

但是这段代码似乎与我们刚刚学到的内容相矛盾：我们没有调用`clone`，而`x`仍然有效，并且没有被移动到`y`中。

原因是，像整数这样的类型在编译时具有已知的大小，它们完全存储在栈上，因此复制实际值的过程非常快速。这意味着我们没有理由阻止 `x` 在创建变量 `y` 之后仍然有效。换句话说，在这里，深度复制和浅层复制之间没有区别，因此调用 `clone` 并不会与常规的浅层复制产生任何不同，所以我们可以省略这部分代码。

Rust 有一个特殊的注解，叫做 `Copy` trait，我们可以将其应用于存储在栈上的类型。就像整数一样（我们将在[第10章][traits]<!-- ignore -->中详细讨论 trait 的更多内容）。如果一个类型实现了 `Copy` trait，那么使用该 trait 的变量不会移动，而是会被简单地复制，这样在赋值给另一个变量之后，这些变量仍然有效。

如果某个类型或其任何组成部分实现了 `Drop` 特质，Rust 不会允许我们使用 `Copy` 注解该类型。如果某个类型在值超出作用域时需要特殊处理，并且我们为该类型添加了 `Copy` 注解，将会出现编译时错误。要了解如何为类型添加 `Copy` 注解以实现该特质，请参阅附录 C 中的 [“可推导的特质”][derivable-traits]<!-- ignore -->。

那么，哪些类型实现了 `Copy` 特性呢？你可以查看相关类型的文档来确认，但一般来说，任何由简单标量值组成的组都可以实现 `Copy` 特性；而那些需要分配内存或属于某种资源类型的类型则无法实现 `Copy` 特性。以下是一些实现了 `Copy` 特性的类型：

- 所有的整数类型，例如 `u32`。
- 布尔类型， `bool`，其值为 `true` 和 `false`。
- 所有的浮点类型，例如 `f64`。
- 字符类型， `char`。
- 元组，如果它们只包含也实现了 `Copy` 的类型。例如， `(i32, i32)` 实现了 `Copy`，但 `(i32, String)` 则没有。

### 所有权与函数

将值传递给函数的机制与将值赋给变量时的机制类似。将变量传递给函数时，也会进行移动或复制操作，就像赋值时一样。列表4-3提供了一个示例，其中包含了一些注释，用来说明变量在何时进入和退出作用域。

<Listing number="4-3" file-name="src/main.rs" caption="Functions with ownership and scope annotated">

```rust
fn main() {
    let s = String::from("hello");  // s comes into scope

    takes_ownership(s);             // s's value moves into the function...
                                    // ... and so is no longer valid here

    let x = 5;                      // x comes into scope

    makes_copy(x);                  // Because i32 implements the Copy trait,
                                    // x does NOT move into the function,
                                    // so it's okay to use x afterward.

} // Here, x goes out of scope, then s. However, because s's value was moved,
  // nothing special happens.

fn takes_ownership(some_string: String) { // some_string comes into scope
    println!("{some_string}");
} // Here, some_string goes out of scope and `drop` is called. The backing
  // memory is freed.

fn makes_copy(some_integer: i32) { // some_integer comes into scope
    println!("{some_integer}");
} // Here, some_integer goes out of scope. Nothing special happens.

```

</Listing>

如果我们尝试在调用 `takes_ownership` 之后使用 `s`，Rust 会抛出编译时错误。这些静态检查可以保护我们免受错误的侵害。试着在 `main` 中添加代码，该代码使用 `s` 和 `x`，以此来了解可以在哪些地方使用它们，以及所有权规则在哪些情况下禁止了这样的使用。

### 返回值与作用域

返回值也可以转移所有权。列表4-4展示了一个函数返回某个值的例子，其注释与列表4-3中的注释类似。

<Listing number="4-4" file-name="src/main.rs" caption="Transferring ownership of return values">

```rust
fn main() {
    let s1 = gives_ownership();        // gives_ownership moves its return
                                       // value into s1

    let s2 = String::from("hello");    // s2 comes into scope

    let s3 = takes_and_gives_back(s2); // s2 is moved into
                                       // takes_and_gives_back, which also
                                       // moves its return value into s3
} // Here, s3 goes out of scope and is dropped. s2 was moved, so nothing
  // happens. s1 goes out of scope and is dropped.

fn gives_ownership() -> String {       // gives_ownership will move its
                                       // return value into the function
                                       // that calls it

    let some_string = String::from("yours"); // some_string comes into scope

    some_string                        // some_string is returned and
                                       // moves out to the calling
                                       // function
}

// This function takes a String and returns a String.
fn takes_and_gives_back(a_string: String) -> String {
    // a_string comes into
    // scope

    a_string  // a_string is returned and moves out to the calling function
}

```

</Listing>

变量的所有权始终遵循相同的模式：将值赋给另一个变量时，该变量就会失去对该值的所有权。当包含堆上数据的变量超出作用域时，除非将该数据的所有权转移给另一个变量，否则该数据会被 `drop` 回收。

虽然这种方法可以工作，但是每次函数调用时都进行所有权转移并返还所有权确实有些繁琐。如果我们希望一个函数能够使用某个值，但不希望获得该值的所有权，那该怎么办呢？如果我们想要再次使用某个值，那么除了函数体内产生的数据之外，所有传递给函数的参数也都需要被返还，这确实很麻烦。

Rust允许我们使用元组返回多个值，如清单4-5所示。

<Listing number="4-5" file-name="src/main.rs" caption="Returning ownership of parameters">

```rust
fn main() {
    let s1 = String::from("hello");

    let (s2, len) = calculate_length(s1);

    println!("The length of '{s2}' is {len}.");
}

fn calculate_length(s: String) -> (String, usize) {
    let length = s.len(); // len() returns the length of a String

    (s, length)
}

```

</Listing>

但是，对于一个本应被普遍使用的概念来说，这种仪式性和工作量实在是太多了。幸运的是，Rust 有一个功能，可以让我们使用值而不需要转移所有权：引用。

[data-types]: ch03-02-data-types.html#data-types
[ch8]: ch08-02-strings.html
[traits]: ch10-02-traits.html
[derivable-traits]: appendix-03-derivable-traits.html
[methods]: ch05-03-method-syntax.html#methods
[paths-module-tree]: ch07-03-paths-for-referring-to-an-item-in-the-module-tree.html
