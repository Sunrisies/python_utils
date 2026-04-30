# 泛型类型、特质与生命周期

每种编程语言都有用于处理概念重复的工具。在Rust中，其中一种工具就是_泛型_：它们是对具体类型或其他属性的抽象替代。我们可以在不了解在编译和运行代码时具体使用什么的情况下，描述泛型的行为以及它们与其他泛型的关联。

函数可以接受一些通用类型的参数，而不是像 `i32` 或 `String` 那样接受具体类型的参数。同样地，它们也可以接受未知值的参数，从而在多个具体值上运行相同的代码。实际上，我们在第6章中已经使用了泛型，通过 `Option<T>`；在第8章中，通过 `Vec<T>` 和 `HashMap<K, V>`；而在第9章中，则通过 `Result<T, E>`。在本章中，你将学习如何使用泛型来定义自己的类型、函数和方法！

首先，我们将学习如何提取一个函数来减少代码重复。然后，我们将使用相同的技术，从两个仅参数类型不同的函数中创建一个通用函数。我们还将解释如何在结构体定义和枚举定义中使用泛型类型。

然后，你将学习如何使用特质来以通用方式定义行为。你可以将特质与泛型类型结合起来，从而限制一个泛型类型只能接受那些具有特定行为的类型，而不是任何类型。

最后，我们将讨论 _生命周期_：这是一种泛型机制，能够向编译器提供有关引用之间关系的详细信息。生命周期让我们能够向编译器提供足够多的关于借用值的信息，从而确保引用在更多情况下都是有效的，而无需我们的帮助。

## 通过提取函数来消除重复内容

泛型允许我们用一个占位符来替代特定的类型，这个占位符可以代表多种类型，从而消除代码重复。在深入讨论泛型语法之前，我们先来看看如何以一种不涉及泛型类型的方式消除重复代码。具体来说，就是提取一个函数，该函数可以将特定的值替换为代表多种值的占位符。然后，我们将同样的技术应用到泛型函数的提取上！通过了解如何识别可以提取到函数中的重复代码，你就能开始意识到那些可以利用泛型来解决的重复代码了。

我们将从清单 10-1 中的简短程序开始，该程序用于找出列表中的最大数字。

<Listing number="10-1" file-name="src/main.rs" caption="Finding the largest number in a list of numbers">

```rust
fn main() {
    let number_list = vec![34, 50, 25, 100, 65];

    let mut largest = &number_list[0];

    for number in &number_list {
        if number > largest {
            largest = number;
        }
    }

    println!("The largest number is {largest}");
}

```

</Listing>

我们将一个整数列表存储在变量 `number_list` 中，并将列表中的第一个数字的引用存储在名为 `largest` 的变量中。然后，我们遍历列表中的所有数字，如果当前数字大于 `largest` 中存储的数字，我们就更新该变量中的引用。然而，如果当前数字小于或等于迄今为止遇到的最大数字，那么这个变量就不会发生变化，代码会继续处理列表中的下一个数字。在遍历完列表中的所有数字之后， `largest` 应该指向最大的数字，在这个例子中是 100。

我们现在需要找到两个不同数字列表中的最大数字。为此，我们可以选择复制 Listing 10-1 中的代码，并在程序的两个不同的位置使用相同的逻辑，如 Listing 10-2 所示。

<Listing number="10-2" file-name="src/main.rs" caption="Code to find the largest number in *two* lists of numbers">

```rust
fn main() {
    let number_list = vec![34, 50, 25, 100, 65];

    let mut largest = &number_list[0];

    for number in &number_list {
        if number > largest {
            largest = number;
        }
    }

    println!("The largest number is {largest}");

    let number_list = vec![102, 34, 6000, 89, 54, 2, 43, 8];

    let mut largest = &number_list[0];

    for number in &number_list {
        if number > largest {
            largest = number;
        }
    }

    println!("The largest number is {largest}");
}

```

</Listing>

虽然这段代码可以运行，但重复编写代码既繁琐又容易出错。此外，当我们想要修改代码时，还需要在多个地方进行更新。

为了消除这种重复，我们将通过定义一个函数来实现抽象化，该函数可以处理作为参数传递的任何整数列表。这种解决方案使我们的代码更加清晰，并且能够抽象地表达找到列表中最大数的概念。

在 Listing 10-3 中，我们将用于找出最大数的代码提取到一个名为 `largest` 的函数中。然后，我们调用这个函数来找出 Listing 10-2 中两个列表中的最大数。将来，我们也可以将这个函数应用于其他包含 `i32` 值的列表中。

<Listing number="10-3" file-name="src/main.rs" caption="Abstracted code to find the largest number in two lists">

```rust
fn largest(list: &[i32]) -> &i32 {
    let mut largest = &list[0];

    for item in list {
        if item > largest {
            largest = item;
        }
    }

    largest
}

fn main() {
    let number_list = vec![34, 50, 25, 100, 65];

    let result = largest(&number_list);
    println!("The largest number is {result}");

    let number_list = vec![102, 34, 6000, 89, 54, 2, 43, 8];

    let result = largest(&number_list);
    println!("The largest number is {result}");
}

```

</Listing>

`largest`函数有一个名为`list`的参数，它代表我们传递给函数的任何具体的`i32`值的切片。因此，当我们调用这个函数时，代码会针对我们传入的具体值来执行。

总结来说，我们将代码从清单10-2修改为清单10-3所涉及的步骤如下：

1. 识别重复的代码。  
1. 将重复的代码提取到函数的主体中，并在函数签名中明确该代码的输入和返回值。  
1. 将重复的代码的两个实例替换为调用该函数。

接下来，我们将使用相同的通用化方法来减少代码重复。就像函数体可以操作抽象类型 `list` 而不是具体的数值一样，通用化也允许代码操作抽象类型。

例如，假设我们有两个函数：一个用于找出 `i32` 值集中最大的元素，另一个用于找出 `char` 值集中最大的元素。我们该如何消除这种重复呢？让我们来了解一下吧！