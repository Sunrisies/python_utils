## 使用 `Drop` 特性在清理过程中运行代码

智能指针模式中的第二个重要特性是 `Drop`，它允许你自定义当某个变量即将超出作用域时会发生什么。你可以为任何类型提供 `Drop` 特性的实现，并且该代码可以用来释放诸如文件或网络连接这样的资源。

我们在智能指针的上下文中引入 `Drop` 这个特性，因为 `Drop` 特性的功能在实现智能指针时几乎总是会被用到。例如，当某个 `Box<T>` 被删除时，它会释放该智能指针所指向的堆内存。

在某些语言中，对于某些类型的数据，程序员必须每次使用完这些类型的实例后，调用代码来释放内存或资源。例如，文件句柄、套接字和锁等。如果程序员忘记这样做，系统可能会过载并崩溃。在Rust中，你可以指定每当某个值超出作用域时，就执行特定的代码，编译器会自动插入这段代码。因此，你不必担心在程序中到处放置清理代码——这样仍然可以避免资源泄漏！

你可以通过实现`Drop` trait来指定当变量超出作用域时需要运行的代码。而`Drop` trait则要求你实现一个名为`drop`的方法，该方法需要一个对`self`的可变引用。为了了解Rust是如何调用`drop`的，我们先使用`println!`语句来实现`drop`吧。

列表15-14展示了一个 `CustomSmartPointer` 结构体，其唯一的自定义功能是在实例超出作用域时打印 `Dropping CustomSmartPointer!`，以此来表明Rust正在调用 `drop` 方法。

<Listing number="15-14" file-name="src/main.rs" caption="A `CustomSmartPointer` struct that implements the `Drop` trait where we would put our cleanup code">

```rust
struct CustomSmartPointer {
    data: String,
}

impl Drop for CustomSmartPointer {
    fn drop(&mut self) {
        println!("Dropping CustomSmartPointer with data `{}`!", self.data);
    }
}

fn main() {
    let c = CustomSmartPointer {
        data: String::from("my stuff"),
    };
    let d = CustomSmartPointer {
        data: String::from("other stuff"),
    };
    println!("CustomSmartPointers created");
}

```

</Listing>

`Drop` trait被包含在prelude中，因此我们不需要将其引入到作用域中。我们在`CustomSmartPointer`上实现了`Drop` trait，并为调用`println!`的`drop`方法提供了实现。`drop`方法的主体可以用来放置当某个类型实例超出作用域时想要执行的任何逻辑。我们在这里打印一些文本，以直观地展示Rust何时会调用`drop`。

在 `main` 中，我们创建了两个 `CustomSmartPointer` 的实例，然后打印出 `CustomSmartPointers created`。在 `main` 的末尾，我们的 `CustomSmartPointer` 实例将会超出作用域，此时 Rust 会调用我们在 `drop` 方法中编写的代码，从而打印出我们的最终消息。需要注意的是，我们并不需要显式地调用 `drop` 方法。

当我们运行这个程序时，将会看到以下输出：

```console
$ cargo run
   Compiling drop-example v0.1.0 (file:///projects/drop-example)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.60s
     Running `target/debug/drop-example`
CustomSmartPointers created
Dropping CustomSmartPointer with data `other stuff`!
Dropping CustomSmartPointer with data `my stuff`!

```

当我们的实例超出作用域时，Rust会自动调用 `drop`，从而执行我们指定的代码。变量的删除顺序与创建顺序相反，因此 `d` 会在 `c` 之前被删除。这个示例的目的是让你直观地了解 `drop` 方法的工作原理；通常情况下，你会指定类型需要执行的清理代码，而不是打印消息。

<!-- Old headings. Do not remove or links may break. -->

<a id="dropping-a-value-early-with-std-mem-drop"></a>

遗憾的是，禁用 `drop` 功能并不简单。通常来说，不需要禁用 `drop`；`Drop` 特性的意义就在于它会被自动处理。不过，偶尔你可能需要提前释放某个值。例如，在使用管理锁的智能指针时，你可能需要调用 `drop` 方法来释放锁，这样同一作用域内的其他代码就可以获取该锁了。Rust 不允许手动调用 `Drop` 特性的 `drop` 方法；相反，如果你想在某个值的作用域结束之前将其释放，就必须使用标准库提供的 `std::mem::drop` 函数。

尝试通过修改清单15-14中的`main`函数来手动调用`Drop` trait的`drop`方法，但如清单15-15所示，这种方法是无效的。

<Listing number="15-15" file-name="src/main.rs" caption="Attempting to call the `drop` method from the `Drop` trait manually to clean up early">

```rust,ignore,does_not_compile
fn main() {
    let c = CustomSmartPointer {
        data: String::from("some data"),
    };
    println!("CustomSmartPointer created");
    c.drop();
    println!("CustomSmartPointer dropped before the end of main");
}

```

</Listing>

当我们尝试编译这段代码时，会遇到这个错误：

```console
$ cargo run
   Compiling drop-example v0.1.0 (file:///projects/drop-example)
error[E0040]: explicit use of destructor method
  --> src/main.rs:16:7
   |
16 |     c.drop();
   |       ^^^^ explicit destructor calls not allowed
   |
help: consider using `drop` function
   |
16 -     c.drop();
16 +     drop(c);
   |

For more information about this error, try `rustc --explain E0040`.
error: could not compile `drop-example` (bin "drop-example") due to 1 previous error

```

这条错误消息表明，我们不允许显式调用 `drop` 函数。错误消息中使用了“_destructor_”这个术语，这是编程中用来描述负责清理实例的函数的一般术语。_destructor_类似于_constructor_，后者用于创建实例。在Rust中， `drop` 函数就是一个具体的 _destructor_。

Rust不允许我们显式调用`drop`，因为Rust仍然会自动在`main`末尾的值上调用`drop`。这会导致“double free”错误，因为Rust试图对同一值进行两次清理操作。

当值超出作用域时，我们无法禁用 `drop` 的自动插入功能，也无法显式调用 `drop` 方法。因此，如果我们需要强制某值尽早被清理，就会使用 `std::mem::drop` 函数。

`std::mem::drop`函数与`Drop` trait中的`drop`方法有所不同。我们通过传递想要强制丢弃的值作为参数来调用该函数。该函数位于prelude部分，因此我们可以在Listing 15-15中修改`main`，以调用`drop`函数，如Listing 15-16所示。

<Listing number="15-16" file-name="src/main.rs" caption="Calling `std::mem::drop` to explicitly drop a value before it goes out of scope">

```rust
fn main() {
    let c = CustomSmartPointer {
        data: String::from("some data"),
    };
    println!("CustomSmartPointer created");
    drop(c);
    println!("CustomSmartPointer dropped before the end of main");
}

```

</Listing>

运行这段代码将会输出以下内容：

```console
$ cargo run
   Compiling drop-example v0.1.0 (file:///projects/drop-example)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.73s
     Running `target/debug/drop-example`
CustomSmartPointer created
Dropping CustomSmartPointer with data `some data`!
CustomSmartPointer dropped before the end of main

```

文本内容为：``Dropping CustomSmartPointer with data `some data`!`` is printed
between the `CustomSmartPointer 创建` and `CustomSmartPointer 在 main 函数结束前被丢弃` text, showing that the `丢弃` method code is called to drop
`c` at that point.

You can use code specified in a `丢弃` trait implementation in many ways to
make cleanup convenient and safe: For instance, you could use it to create your
own memory allocator! With the `丢弃` trait and Rust’s ownership system, you
don’t have to remember to clean up, because Rust does it automatically.

You also don’t have to worry about problems resulting from accidentally
cleaning up values still in use: The ownership system that makes sure
references are always valid also ensures that `丢弃` gets called only once when
the value is no longer being used.

Now that we’ve examined `Box<T>` 以及关于智能指针的一些特性。接下来，让我们看看标准库中定义的其他几种智能指针。