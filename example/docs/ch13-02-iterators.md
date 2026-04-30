## 使用迭代器处理一系列项目

迭代器模式允许你依次对一系列元素执行某些操作。迭代器负责遍历每个元素的逻辑，并判断序列是否已完成。使用迭代器时，你不必自己重新实现这些逻辑。

在Rust中，迭代器是“惰性”的，这意味着在你调用消耗迭代器的方法之前，迭代器并不会产生任何效果。例如，Listing 13-10中的代码通过调用定义在 `Vec<T>` 上的 `iter` 方法，来创建一个遍历向量 `v1` 中的元素的迭代器。这段代码本身并不会执行任何有用的操作。

<Listing number="13-10" file-name="src/main.rs" caption="Creating an iterator">

```rust
    let v1 = vec![1, 2, 3];

    let v1_iter = v1.iter();

```

</Listing>

这个迭代器被存储在 `v1_iter` 变量中。一旦我们创建了一个迭代器，就可以以多种方式使用它。在 Listing 3-5 中，我们使用 `for` 循环遍历一个数组，对数组中的每个元素执行一些操作。在底层，这隐式地创建了一个迭代器，然后将其使用完毕，但直到现在，我们还没有详细了解这一过程是如何工作的。

在 Listing 13-11 的示例中，我们将迭代器的创建与在 `for` 循环中对该迭代器的使用分离开来。当使用 `v1_iter` 中的迭代器调用 `for` 循环时，迭代器中的每个元素都会在循环的每次迭代中被使用，从而打印出每个值。

<Listing number="13-11" file-name="src/main.rs" caption="Using an iterator in a `for` loop">

```rust
    let v1 = vec![1, 2, 3];

    let v1_iter = v1.iter();

    for val in v1_iter {
        println!("Got: {val}");
    }

```

</Listing>

在那些标准库没有提供迭代器的语言中，你可能需要通过以索引0开始一个变量，然后使用该变量来索引向量以获取值，并在循环中不断增加该变量的值，直到达到向量中项目的总数。

迭代器会处理所有这些逻辑，从而减少了可能出错的重复代码。迭代器让你可以更灵活地使用相同的逻辑来处理多种不同类型的序列，而不只是像向量那样可以索引的数据结构。让我们来看看迭代器是如何实现这一点的。

### `Iterator` 特质与 `next` 方法

所有迭代器都实现了一种名为 `Iterator` 的特质，该特质在标准库中定义。这个特质的定义如下所示：

```rust
pub trait Iterator {
    type Item;

    fn next(&mut self) -> Option<Self::Item>;

    // methods with default implementations elided
}
```

请注意，这个定义使用了一些新的语法：`type Item`和`Self::Item`，它们用于定义具有该特性的关联类型。我们将在第20章中详细讨论关联类型。目前，你需要知道的是，这段代码表明，要实现`Iterator`特性，就必须同时定义`Item`类型，而`Item`类型则用于`next`方法的返回类型。换句话说，`Item`类型将是迭代器返回的类型的类型。

`Iterator` trait 要求实现者只定义一个方法：`next`方法。该方法的每次调用都会从迭代器中获取一个元素，这些元素会被包装在`Some`中。当迭代结束后，该方法会返回`None`。

我们可以直接对迭代器调用 `next` 方法；清单 13-12 展示了在从向量创建的迭代器上重复调用 `next` 时返回的值。

<Listing number="13-12" file-name="src/lib.rs" caption="Calling the `next` method on an iterator">

```rust,noplayground
    #[test]
    fn iterator_demonstration() {
        let v1 = vec![1, 2, 3];

        let mut v1_iter = v1.iter();

        assert_eq!(v1_iter.next(), Some(&1));
        assert_eq!(v1_iter.next(), Some(&2));
        assert_eq!(v1_iter.next(), Some(&3));
        assert_eq!(v1_iter.next(), None);
    }

```

</Listing>

请注意，我们需要将 `v1_iter` 设置为可变属性。在迭代器上调用 `next` 方法会更改迭代器内部的状态，从而改变迭代器在序列中的当前位置。换句话说，这段代码会“消耗”掉迭代器。每次调用 `next` 都会从迭代器中获取一个元素。当我们使用 `for` 循环时，不需要将 `v1_iter` 设置为可变属性，因为循环会自行负责 `v1_iter`，并在后台将其设置为可变属性。

另外需要注意的是，我们从 `next` 的调用中得到的值是不可变的，它们只是对向量中值的引用。而 `iter` 方法会生成一个迭代器，该迭代器只能操作不可变引用。如果我们想要创建一个能够获取 `v1` 中的值并返回这些值的迭代器，我们可以调用 `into_iter` 而不是 `iter`。同样地，如果我们想要遍历可变引用，可以调用 `iter_mut` 而不是 `iter`。

### 消耗迭代器的方法

`Iterator` trait 包含了许多不同的方法，这些方法的默认实现由标准库提供；您可以通过查阅标准库中关于`Iterator` trait的API文档来了解这些方法。其中一些方法在其定义中调用了`next`方法，这就是为什么在实现`Iterator` trait时，必须实现`next`方法的原因。

那些调用 `next` 的方法被称为_消耗型适配器_，因为调用它们会消耗掉迭代器。一个例子就是 `sum` 方法，它会占用迭代器的所有权，并通过反复调用 `next` 来遍历其中的元素，从而消耗掉迭代器。在遍历过程中，它会将每个元素累加到总和中，并在遍历完成后返回总和。列表 13-13 展示了一个使用 `sum` 方法的示例。

<Listing number="13-13" file-name="src/lib.rs" caption="Calling the `sum` method to get the total of all items in the iterator">

```rust,noplayground
    #[test]
    fn iterator_sum() {
        let v1 = vec![1, 2, 3];

        let v1_iter = v1.iter();

        let total: i32 = v1_iter.sum();

        assert_eq!(total, 6);
    }

```

</Listing>

在调用 `sum` 之后，我们不允许使用 `v1_iter`，因为 `sum` 会接管我们对其调用的迭代器。

### 生成其他迭代器的方法

_Iterator适配器_是在`Iterator` trait上定义的方法，这些方法不会消耗原始迭代器。相反，它们通过改变原始迭代器的某些特性来生成不同的迭代器。

清单13-14展示了调用iterator适配器方法 `map` 的一个示例。该方法在遍历元素时，会为每个元素调用一个闭包来进行处理。 `map` 方法返回一个新的迭代器，该迭代器会生成经过修改后的元素。这里的闭包会创建一个新的迭代器，该迭代器中的每个元素都会增加1。

<Listing number="13-14" file-name="src/main.rs" caption="Calling the iterator adapter `map` to create a new iterator">

```rust,not_desired_behavior
    let v1: Vec<i32> = vec![1, 2, 3];

    v1.iter().map(|x| x + 1);

```

</Listing>

然而，这段代码会产生一个警告：

```console
$ cargo run
   Compiling iterators v0.1.0 (file:///projects/iterators)
warning: unused `Map` that must be used
 --> src/main.rs:4:5
  |
4 |     v1.iter().map(|x| x + 1);
  |     ^^^^^^^^^^^^^^^^^^^^^^^^
  |
  = note: iterators are lazy and do nothing unless consumed
  = note: `#[warn(unused_must_use)]` on by default
help: use `let _ = ...` to ignore the resulting value
  |
4 |     let _ = v1.iter().map(|x| x + 1);
  |     +++++++

warning: `iterators` (bin "iterators") generated 1 warning
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.47s
     Running `target/debug/iterators`

```

清单 13-14 中的代码并不执行任何操作；我们指定的闭包永远不会被调用。这个警告提醒我们为什么：迭代器适配器是惰性加载的，因此我们需要在这里直接使用迭代器。

为了消除这个警告并继续使用迭代器，我们将使用 `collect` 方法。我们在 Listing 12-1 中使用了 `env::args` 方法。这个方法会消耗迭代器，并将得到的值收集到一个集合数据类型中。

在 Listing 13-15 中，我们遍历了从 `map` 调用中返回的迭代器，并将结果收集到一个向量中。这个向量最终会包含原始向量中的每个元素，并且每个元素的值都会增加 1。

<Listing number="13-15" file-name="src/main.rs" caption="Calling the `map` method to create a new iterator, and then calling the `collect` method to consume the new iterator and create a vector">

```rust
    let v1: Vec<i32> = vec![1, 2, 3];

    let v2: Vec<_> = v1.iter().map(|x| x + 1).collect();

    assert_eq!(v2, vec![2, 3, 4]);

```

</Listing>

因为`map`需要一个闭包，我们可以指定任何想要对每个元素执行的操作。这是一个很好的例子，说明了闭包如何让你在重用`Iterator`特质提供的迭代行为的同时，自定义某些行为。

你可以连续调用多个迭代器适配器，以以一种易于理解的方式执行复杂的操作。但由于所有迭代器都是惰性计算的，因此你需要调用其中一个消费适配器的方法，才能从对迭代器适配器的调用中获得结果。

<!-- Old headings. Do not remove or links may break. -->

<a id="using-closures-that-capture-their-environment"></a>

### 能够捕获其环境的闭包

许多迭代器适配器会将闭包作为参数传递，而通常，我们指定给迭代器适配器的闭包都是能够捕获其环境的闭包。

在这个示例中，我们将使用 `filter` 方法，该方法需要一个闭包作为参数。该闭包从迭代器中获取一个元素，并返回一个 `bool`。如果闭包返回 `true`，那么该值将被包含在由 `filter` 产生的迭代结果中。如果闭包返回 `false`，那么该值则不会被包含在内。

在 Listing 13-16 中，我们使用 `filter` 并结合一个闭包，来捕获来自其环境的 `shoe_size` 变量，从而遍历一系列 `Shoe` 结构实例。该方法只会返回符合指定尺码的鞋子。

<Listing number="13-16" file-name="src/lib.rs" caption="Using the `filter` method with a closure that captures `shoe_size`">

```rust,noplayground
#[derive(PartialEq, Debug)]
struct Shoe {
    size: u32,
    style: String,
}

fn shoes_in_size(shoes: Vec<Shoe>, shoe_size: u32) -> Vec<Shoe> {
    shoes.into_iter().filter(|s| s.size == shoe_size).collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn filters_by_size() {
        let shoes = vec![
            Shoe {
                size: 10,
                style: String::from("sneaker"),
            },
            Shoe {
                size: 13,
                style: String::from("sandal"),
            },
            Shoe {
                size: 10,
                style: String::from("boot"),
            },
        ];

        let in_my_size = shoes_in_size(shoes, 10);

        assert_eq!(
            in_my_size,
            vec![
                Shoe {
                    size: 10,
                    style: String::from("sneaker")
                },
                Shoe {
                    size: 10,
                    style: String::from("boot")
                },
            ]
        );
    }
}

```

</Listing>

`shoes_in_size`函数接受鞋子的向量和鞋码作为参数。它返回一个只包含指定尺码鞋子的向量。

在 `shoes_in_size` 的主体中，我们调用 `into_iter` 来创建一个迭代器，该迭代器会拥有该向量。然后，我们调用 `filter` 来将该迭代器适配成一个新的迭代器，这个新迭代器只包含那些使得闭包返回 `true` 的元素。

该闭包从环境中获取 `shoe_size` 参数，并将该值与每只鞋子的尺寸进行比较，只保留符合指定尺寸的鞋子。最后，调用 `collect` 会将适应迭代器返回的值收集到一个向量中，该向量由该函数返回。

测试表明，当我们调用 `shoes_in_size` 时，返回的结果只有那些与我们指定的尺寸相同的鞋子。