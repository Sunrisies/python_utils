## 使用 `Drop` 特性在清理过程中运行代码

智能指针模式中第二个重要的特性是`Drop`，它允许你自定义当某个值即将超出作用域时会发生什么。你可以为任何类型提供`Drop`特性的实现，而这段代码可以用来释放资源，比如文件或网络连接。

我们在智能指针的上下文中引入了 ``Drop``，因为在使用智能指针时，几乎总是需要调用 ``Drop`` 特性所提供的功能。例如，当某个 ``Box<T>`` 被释放时，它会释放该智能指针所指向的堆内存空间。

在某些语言中，对于某些类型的数据，程序员必须每次使用完这些类型的实例后，调用代码来释放内存或资源。例如，文件句柄、套接字和锁等。如果程序员忘记这样做，系统可能会过载并崩溃。在Rust中，你可以指定每当某个值超出作用域时，就执行特定的代码，编译器会自动插入这段代码。因此，你不必担心在程序中到处放置清理代码——这样仍然可以避免资源泄漏！

您可以通过实现 ``Drop`` 特质来指定当某个变量超出作用域时需要运行的代码。而 ``Drop`` 特质则要求您实现一个名为 ``drop`` 的方法，该方法接受一个对 ``self`` 的可变引用。为了观察 Rust 是如何调用 ``drop`` 的，我们先使用 ``println!`` 语句来实现 ``drop``。

清单15-14展示了一个`CustomSmartPointer`结构体。它的唯一特殊功能是在实例超出作用域时打印`Dropping CustomSmartPointer!`，以此来表明Rust何时调用`drop`方法。

<列表编号="15-14" 文件名称="src/main.rs" 标题="一个实现 `Drop` 特性的 `CustomSmartPointer` 结构体，我们将在这里放置清理代码">

```rust
{{#rustdoc_include ../listings/ch15-smart-pointers/listing-15-14/src/main.rs}}
```

</ Listing>

`Drop` 特质被包含在序言中，因此我们不需要将其引入作用域。我们在 `CustomSmartPointer` 上实现了 `Drop` 特质，并为 `drop` 方法提供了实现，该方法会调用 `println!`。`drop` 方法的主体区域可以放置任何希望在类型实例超出作用域时执行的逻辑。我们在这里打印一些文本，以便直观地展示 Rust 何时会调用 `drop`。

在 `main` 中，我们创建了两个 `CustomSmartPointer` 的实例，然后打印出 `CustomSmartPointers created` 的内容。在 `main` 的末尾，我们的 `CustomSmartPointer` 的实例将会超出作用域，此时 Rust 会调用我们在 `drop` 方法中编写的代码，最终打印出我们的最后一条消息。需要注意的是，我们并不需要显式地调用 `drop` 方法。

当我们运行这个程序时，将会看到如下输出：

```console
{{#include ../listings/ch15-smart-pointers/listing-15-14/output.txt}}
```

当我们的实例超出作用域时，Rust会自动调用`drop`，从而执行我们指定的代码。变量的删除顺序与创建的顺序相反，因此`d`会在`c`之前被删除。这个示例的目的是让你直观地了解`drop`方法的工作原理；通常情况下，你会指定类型需要执行的清理代码，而不是打印消息。

<!-- 旧的标题。不要删除，否则链接可能会失效。-->

<a id="提前丢弃值使用std-mem-drop"></a>

遗憾的是，禁用自动的 ``drop`` 功能并不简单。通常来说，不需要禁用 `__INLINE_CODE_43}$；`Drop` 特性的意义就在于它会被自动处理。不过，偶尔你可能需要提前释放某个值。例如，在使用管理锁的智能指针时，你可能希望调用 ``drop`` 方法来释放锁，这样同一作用域内的其他代码就能获取该锁。Rust 不允许手动调用 `Drop` 特性中的 ``drop`` 方法；相反，如果你想在某个值的作用域结束之前将其释放，就必须使用标准库提供的 ``std::mem::drop`` 函数。

尝试通过修改清单15-14中的`main`函数来手动调用`Drop` trait的`drop`方法，但如清单15-15所示，这种方法是无效的。

<列表编号="15-15" 文件名称="src/main.rs" 标题="尝试手动调用来自 `Drop` 特征中的 `drop` 方法以提前进行清理">

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch15-smart-pointers/listing-15-15/src/main.rs:here}}
```

</ Listing>

当我们尝试编译这段代码时，会遇到这个错误：

```console
{{#include ../listings/ch15-smart-pointers/listing-15-15/output.txt}}
```

这条错误消息表明，我们不允许显式调用`drop`。错误消息中使用了“_destructor”这个术语，这是编程中用来描述负责清理实例的函数的一般术语。_destructor_类似于_constructor_，后者用于创建实例。在Rust中，`drop`函数就是一个具体的_destructor_。

Rust不允许我们显式地调用`drop`，因为Rust仍然会自动在`main`末尾的值上调用`drop`。这会导致“双重释放”错误，因为Rust试图对同一值进行两次清理操作。

我们无法在值超出作用域时禁用`drop`的自动插入，也无法显式调用`drop`方法。因此，如果我们需要强制某个值尽早被清理，就会使用`std::mem::drop`函数。

在`Drop` trait中，`std::mem::drop`函数与`drop`方法不同。我们是通过传递想要强制丢弃的值来调用该函数的。该函数位于前奏部分，因此我们可以在Listing 15-15中修改`main`，以调用`drop`函数，如Listing 15-16所示。

<列表编号="15-16" 文件名称="src/main.rs" 标题="调用 `std::mem::drop` 在值超出作用域之前显式删除该值">

```rust
{{#rustdoc_include ../listings/ch15-smart-pointers/listing-15-16/src/main.rs:here}}
```

</ Listing>

运行这段代码将会输出以下内容：

```console
{{#include ../listings/ch15-smart-pointers/listing-15-16/output.txt}}
```

以下文本 ``使用数据 `some data`来丢弃 CustomSmartPointer！在 `CustomSmartPointer created` 和 `CustomSmartPointer` 被丢弃之后，会在 main` text, showing that the `drop 方法代码的末尾调用 `c` 来丢弃该对象。

您可以使用在 ``Drop``  trait 实现中指定的代码，以多种方式来实现便捷且安全的清理操作：例如，您可以利用它来创建自己的内存分配器！借助 ``Drop`` trait 以及 Rust 的所有权系统，您无需手动进行清理工作，因为 Rust 会自动完成这一操作。

您也不必担心因意外清理仍在使用中的值而引发的问题：该所有权系统能够确保引用始终有效，同时也能保证在值不再被使用时，`drop`只会被调用一次。

现在我们已经了解了`Box<T>`以及一些智能指针的特性，接下来让我们看看标准库中定义的其他一些智能指针。