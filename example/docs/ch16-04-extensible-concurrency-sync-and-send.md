<!-- Old headings. Do not remove or links may break. -->

<a id="extensible-concurrency-with-the-sync-and-send-traits"></a>
<a id="extensible-concurrency-with-the-send-and-sync-traits"></a>

## 可扩展的并发机制，采用 `Send` 和 `Sync`

有趣的是，我们在本章中讨论的几乎所有并发特性，其实都是标准库的一部分，而不是语言本身的一部分。处理并发的方式并不局限于语言或标准库；你可以自己编写并发特性，或者使用其他人编写的相关功能。

不过，在语言中嵌入的关键并发概念中，而非标准库中，有 `std::marker` traits `Send` 和 `Sync`。

<!-- Old headings. Do not remove or links may break. -->

<a id="allowing-transference-of-ownership-between-threads-with-send"></a>

### 在线程之间转移所有权

`Send`标记表示，实现`Send`类型的值的所有权可以在线程之间转移。几乎每一种Rust类型都实现了`Send`，但也有一些例外，包括`Rc<T>`：`Rc<T>`无法实现`Send`，因为如果你克隆了一个`Rc<T>`值，并试图将克隆后的所有权转移给另一个线程，那么两个线程可能会同时更新引用计数。因此，`Rc<T>`被实现出来，用于单线程环境，这样就不必承受线程安全性能上的代价。

因此，Rust的类型系统和特质约束确保你永远无法不小心地将 `Rc<T>` 类型的值在不安全的多线程环境中传递。在清单 16-14 中尝试这样做时，我们遇到了错误 `` the trait `Send` is not implemented
for `Rc<Mutex<i32>>` ``. When we switched to `Arc<T>`, which does implement
`Send`, the code compiled.

Any type composed entirely of `Send` types is automatically marked as `Send` as
well. Almost all primitive types are `Send`, aside from raw pointers, which
we’ll discuss in Chapter 20.

<!-- Old headings. Do not remove or links may break. -->

<a id="allowing-access-from-multiple-threads-with-sync"></a>

### Accessing from Multiple Threads

The `Sync` marker trait indicates that it is safe for the type implementing
`Sync` to be referenced from multiple threads. In other words, any type `T`
implements `Sync` if `&T` (an immutable reference to `T`) implements `Send`,
meaning the reference can be sent safely to another thread. Similar to `Send`,
primitive types all implement `Sync`, and types composed entirely of types that
implement `Sync` also implement `Sync`.

The smart pointer `Rc<T>` also doesn’t implement `Sync` for the same reasons
that it doesn’t implement `Send`. The `RefCell<T>` type (which we talked about
in Chapter 15) and the family of related `Cell<T>` types don’t implement
`Sync`. The implementation of borrow checking that `RefCell<T>` does at runtime
is not thread-safe. The smart pointer `Mutex<T>` implements `Sync` and can be
used to share access with multiple threads, as you saw in [“Shared Access to
`Mutex<T>`”][shared-access]<!-- ignore -->.

### Implementing `Send` and `Sync` Manually Is Unsafe

Because types composed entirely of other types that implement the `Send` and
`Sync` traits also automatically implement `Send` and `Sync`, we don’t have to
implement those traits manually. As marker traits, they don’t even have any
methods to implement. They’re just useful for enforcing invariants related to
concurrency.

Manually implementing these traits involves implementing unsafe Rust code.
We’ll talk about using unsafe Rust code in Chapter 20; for now, the important
information is that building new concurrent types not made up of `Send` and
`Sync` parts requires careful thought to uphold the safety guarantees. [“The
Rustonomicon”][nomicon] has more information about these guarantees and how to
uphold them.

## Summary

This isn’t the last you’ll see of concurrency in this book: The next chapter
focuses on async programming, and the project in Chapter 21 will use the
concepts in this chapter in a more realistic situation than the smaller
examples discussed here.

As mentioned earlier, because very little of how Rust handles concurrency is
part of the language, many concurrency solutions are implemented as crates.
These evolve more quickly than the standard library, so be sure to search
online for the current, state-of-the-art crates to use in multithreaded
situations.

The Rust standard library provides channels for message passing and smart
pointer types, such as `Mutex<T>` and `Arc<T>` 在并发环境中是安全使用的。类型系统和借用检查器确保使用这些解决方案的代码不会遇到数据竞争或无效引用的问题。一旦你的代码能够编译成功，你就可以放心地知道它能够在多个线程上运行，而不会出现其他语言中常见的难以追踪的错误。并发编程已经不再是一个需要害怕的概念了：大胆地让你的程序实现并发吧！

[shared-access]: ch16-03-shared-state.html#shared-access-to-mutext
[nomicon]: ../nomicon/index.html
