## 在哈希映射中存储带有关联值的键

我们常见的数据结构之一就是哈希映射。这种数据结构将类型为 `K` 的键映射到类型为 `V` 的值上，具体实现是通过一个 _哈希函数_ 来决定的，该函数决定了键和值在内存中的存储方式。许多编程语言都支持这种数据结构，但它们通常使用不同的名称来指代它，比如 _哈希表_、_映射_、_对象_、_字典_或_关联数组_等。

哈希映射在需要以非索引方式查找数据时非常有用，就像在向量中那样，但这里的键可以是任何类型。例如，在游戏中，你可以将每个队伍的得分存储在哈希映射中，其中每个键是队伍的名称，每个值则是该队伍的得分。给定一个队伍名称，你可以检索出该队伍的得分。

在本节中，我们将介绍哈希映射的基本 API，但标准库在 `HashMap<K, V>` 上定义的函数中还隐藏着许多其他有用的功能。如常，如需更多信息，请查阅标准库的文档。

### 创建新的哈希映射

创建空哈希映射的一种方法是使用 `new` 来添加元素，然后使用 `insert` 来添加更多元素。在 Listing 8-20 中，我们记录了两支队伍的分数，这两支队伍的名字分别是 _Blue_ 和 _Yellow_。蓝队以 10 分开始，黄队以 50 分开始。

<Listing number="8-20" caption="Creating a new hash map and inserting some keys and values">

```rust
    use std::collections::HashMap;

    let mut scores = HashMap::new();

    scores.insert(String::from("Blue"), 10);
    scores.insert(String::from("Yellow"), 50);

```

</Listing>

请注意，我们需要先对标准库中的集合部分进行 `use` 操作，然后再处理 `HashMap`。在我们的三个常用集合中，这个集合使用频率最低，因此不会自动包含在序言中介绍的功能中。哈希映射在标准库中的支持也较少；例如，标准库中没有内置的宏可以用来创建哈希映射。

与向量类似，哈希映射也将其数据存储在堆上。这种数据结构具有类型 `String` 的键和类型 `i32` 的值。与向量一样，哈希映射也是同质的：所有的键必须属于同一类型，所有的值也必须属于同一类型。

### 在哈希映射中访问值

我们可以通过向 `get` 方法提供哈希图的键来获取其值，如清单8-21所示。

<Listing number="8-21" caption="Accessing the score for the Blue team stored in the hash map">

```rust
    use std::collections::HashMap;

    let mut scores = HashMap::new();

    scores.insert(String::from("Blue"), 10);
    scores.insert(String::from("Yellow"), 50);

    let team_name = String::from("Blue");
    let score = scores.get(&team_name).copied().unwrap_or(0);

```

</Listing>

在这里，`score`的值将与蓝队相关联，而结果将是`10`。`get`方法返回一个`Option<&V>`；如果哈希映射中没有该键的值，则`get`将返回`None`。这个程序通过调用`copied`来获取`Option<i32>`，而不是`Option<&i32>`，然后如果`scores`中没有该键的条目，则通过`unwrap_or`将`score`设置为零来处理`Option`。

我们可以以与处理向量类似的方式，使用 `for` 循环来遍历哈希映射中的每个键值对。

```rust
    use std::collections::HashMap;

    let mut scores = HashMap::new();

    scores.insert(String::from("Blue"), 10);
    scores.insert(String::from("Yellow"), 50);

    for (key, value) in &scores {
        println!("{key}: {value}");
    }

```

这段代码会以任意顺序打印每一对元素：

```text
Yellow: 50
Blue: 10
```

<!-- Old headings. Do not remove or links may break. -->

<a id="hash-maps-and-ownership"></a>

### 在哈希映射中管理所有权

对于实现了 `Copy` 特性的类型，比如 `i32`，其值会被复制到哈希映射中。而对于像 `String` 这样的被拥有的类型，其值会被移动，而哈希映射将成为这些值的拥有者，如清单 8-22 所示。

<Listing number="8-22" caption="Showing that keys and values are owned by the hash map once they’re inserted">

```rust
    use std::collections::HashMap;

    let field_name = String::from("Favorite color");
    let field_value = String::from("Blue");

    let mut map = HashMap::new();
    map.insert(field_name, field_value);
    // field_name and field_value are invalid at this point, try using them and
    // see what compiler error you get!

```

</Listing>

在通过调用 `insert` 将变量 `field_name` 和 `field_value` 移入哈希映射之后，我们无法再使用它们。

如果我们向哈希映射中插入对值的引用，这些值并不会被移动到哈希映射中。引用所指向的值必须至少与哈希映射的存活时间一样长。我们将在第十章的[“利用生命周期验证引用”][validating-references-with-lifetimes]<!-- ignore -->中进一步讨论这些问题。

### 更新哈希映射

虽然键和值对的数量是可以增长的，但每个唯一的键一次只能关联一个值（反之亦然：例如，Blue队和Yellow队都可以将值 `10` 存储在 `scores` 哈希表中）。

当你想要修改哈希映射中的数据时，你必须决定如何处理这样一种情况：某个键已经分配了一个值。你可以用新值替换旧值，完全忽略旧值。你也可以保留旧值，而不考虑新值，只有当键还没有值时才添加新值。或者，你可以同时保留旧值和新值。让我们来看看如何分别实现这些操作！

#### 覆盖一个值

如果我们向哈希映射中插入一个键和一个值，然后再插入同一个键但使用不同的值，那么该键对应的值将会被替换。尽管清单8-23中的代码两次调用了 `insert`，但由于我们两次都插入了蓝色队伍对应的键值对，因此哈希映射中只会包含一个键值对。

<Listing number="8-23" caption="Replacing a value stored with a particular key">

```rust
    use std::collections::HashMap;

    let mut scores = HashMap::new();

    scores.insert(String::from("Blue"), 10);
    scores.insert(String::from("Blue"), 25);

    println!("{scores:?}");

```

</Listing>

这段代码将会输出 `{"Blue": 25}`。原本的 `10` 已经被覆盖了。

<!-- Old headings. Do not remove or links may break. -->

<a id="only-inserting-a-value-if-the-key-has-no-value"></a>

#### 仅在不存在某个键的情况下才添加该键及其对应的值

通常，我们会先检查哈希映射中是否存在某个特定的键以及该键对应的数值。然后根据以下情况采取相应的操作：如果键确实存在于哈希映射中，那么原有的数值保持不变；如果键不存在，则将其插入哈希映射，并为其分配一个数值。

哈希映射有一个专门的API，名为 `entry`，它接受你想要检查的键作为参数。 `entry` 方法的返回值是一个枚举类型，名为 `Entry`，该枚举类型表示可能存在或不存在的值。假设我们想要检查Yellow团队对应的键是否有一个关联的值。如果不存在，我们就需要插入该值 `50`，同样地，Blue团队对应的键也需要进行相同的操作。使用 `entry` API，代码如下所示，如 Listing 8-24 所示。

<Listing number="8-24" caption="Using the `entry` method to only insert if the key does not already have a value">

```rust
    use std::collections::HashMap;

    let mut scores = HashMap::new();
    scores.insert(String::from("Blue"), 10);

    scores.entry(String::from("Yellow")).or_insert(50);
    scores.entry(String::from("Blue")).or_insert(50);

    println!("{scores:?}");

```

</Listing>

在 `Entry` 上定义的 `or_insert` 方法，如果对应的 `Entry` 键存在，则返回一个可变引用，指向该键的值；如果不存在，则将该参数作为该键的新值，并返回一个可变引用，指向这个新值。这种实现方式比我们自己编写逻辑要简洁得多，而且还能更好地与借用检查器协同工作。

运行清单8-24中的代码将会打印出 `{"Yellow": 50, "Blue": 10}`。第一次调用 `entry` 会插入 Yellow 队的键，其值为 `50`，因为 Yellow 队还没有这个键的值。第二次调用 `entry` 并不会改变哈希映射，因为 Blue 队已经拥有值 `10`。

#### 根据旧值更新值

哈希映射的另一个常见用途是查找某个键对应的值，然后根据旧值对其进行更新。例如，清单8-25展示了用于计算某个文本中每个单词出现次数的代码。我们使用一个哈希映射，将单词作为键，并增加对应的值，以记录该单词出现的次数。如果这是我们第一次遇到某个单词，我们会先将其值设置为 `0`。

<Listing number="8-25" caption="Counting occurrences of words using a hash map that stores words and counts">

```rust
    use std::collections::HashMap;

    let text = "hello world wonderful world";

    let mut map = HashMap::new();

    for word in text.split_whitespace() {
        let count = map.entry(word).or_insert(0);
        *count += 1;
    }

    println!("{map:?}");

```

</Listing>

这段代码会输出 `{"world": 2, "hello": 1, "wonderful": 1}`。你可能会看到相同的键值对以不同的顺序出现：回想一下在[“在哈希映射中访问值”][access]<!-- ignore -->中的内容，哈希映射中的迭代顺序是随机的。

`split_whitespace`方法返回一个迭代器，该迭代器遍历由空白字符分隔的`text`中的子切片。`or_insert`方法返回一个可变引用（`&mut V`），指向指定键对应的值。在这里，我们将这个可变引用存储在`count`变量中，因此要赋值给该值，必须先使用星号（`*`）来解引用`count`。这个可变引用在`for`循环结束时就会超出作用域，因此所有这些更改都是安全的，并且符合借用规则。

### 哈希函数

默认情况下， `HashMap` 使用一种名为 _SipHash_ 的哈希函数，该函数能够抵抗涉及哈希表的拒绝服务攻击[^siphash]<!-- ignore -->。这并不是最快的哈希算法，但为了提高安全性而不得不接受的性能下降是值得的。如果你对代码进行性能分析，发现默认的哈希函数对于你的需求来说速度太慢，那么你可以通过指定不同的哈希器来更换该函数。_哈希器_是一种实现了`BuildHasher` trait的类型。我们将在[第10章][traits]<!-- ignore -->中讨论 trait 以及如何实现它们。你不必从零开始自己实现哈希器；[crates.io](https://crates.io/)<!-- ignore -->提供了许多其他 Rust 用户共享的库，这些库提供了实现多种常见哈希算法的哈希器。

[^siphash]: [https://en.wikipedia.org/wiki/SipHash](https://en.wikipedia.org/wiki/SipHash)

## 摘要

向量、字符串和哈希映射提供了在程序中存储、访问和修改数据所需的大量功能。以下是一些你现在应该能够解决的练习：

1. 给定一个整数列表，使用向量来返回该列表的中位数（排序后位于中间位置的值）和众数（出现次数最多的数值；这里使用哈希映射会非常有帮助）。

1. 将字符串转换为Pig Latin。每个单词的第一个辅音会被移动到单词的末尾，并加上“ay”，例如“first”变成“irst-fay”。以元音开头的单词则会在末尾加上“hay”，例如“apple”变成“apple-hay”。请注意UTF-8编码的相关细节！

1. 使用哈希映射和向量，创建一个文本界面，允许用户将员工姓名添加到公司的某个部门中。例如，“将Sally添加到工程部”或“将Amir添加到销售部”。然后，允许用户按部门或公司名称的字母顺序，检索某个部门的所有人员或公司所有人员的列表。

标准库API文档中描述了向量、字符串和哈希映射所具有的方法，这些方法对于完成这些练习非常有帮助！

我们即将进入更复杂的程序，在这些程序中，操作可能会失败，因此现在是讨论错误处理的最佳时机。接下来我们将进行这方面的讨论！

[validating-references-with-lifetimes]: ch10-03-lifetime-syntax.html#validating-references-with-lifetimes
[access]: #accessing-values-in-a-hash-map
[traits]: ch10-02-traits.html
