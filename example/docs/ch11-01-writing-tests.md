## 如何编写测试

_测试_是Rust中的函数，用于验证非测试代码是否按预期方式运行。测试函数的主体通常会执行以下三个操作：

- 设置所有需要的数据或状态。  
- 运行你想要测试的代码。  
- 验证结果是否符合预期。

让我们来看看Rust为编写执行这些操作的测试而提供的一些特性，其中包括`test`属性、几个宏，以及`should_panic`属性。

<!-- Old headings. Do not remove or links may break. -->

<a id="the-anatomy-of-a-test-function"></a>

### 测试函数的结构设计

在Rust中，测试最简单的形式就是一个带有 `test` 属性的函数。属性是关于Rust代码的元数据；例如，在第5章中我们使用的 `derive` 属性用于结构体。要将一个函数转换为测试函数，需要在 `fn` 之前的行添加 `#[test]`。当你使用 `cargo test` 命令运行测试时，Rust会构建一个测试运行程序，该程序会执行这些带有属性的函数，并报告每个测试函数是否通过或失败。

每当我们使用 Cargo 创建一个新的库项目时，系统会自动生成一个包含测试函数的测试模块。这个模块为你提供了编写测试的模板，这样你就不需要每次开始新项目时都去查找具体的结构和语法了。你可以根据需要添加任意数量的额外测试函数和测试模块！

我们将通过实验模板 `test` 来探索测试的工作原理。在实际测试任何代码之前，我们先进行这样的实验。然后，我们会编写一些实际场景的测试，这些测试会调用我们编写的一些代码，并验证其行为是否正确。

让我们创建一个新的库项目，名为 `adder`，该项目将添加两个数字：

```console
$ cargo new adder --lib
     Created library `adder` project
$ cd adder
```

你的 `adder` 库中的 _src/lib.rs_ 文件的内容应该如下所示：
列表 11-1.

<Listing number="11-1" file-name="src/lib.rs" caption="The code generated automatically by `cargo new`">

<!-- manual-regeneration
cd listings/ch11-writing-automated-tests
rm -rf listing-11-01
cargo new listing-11-01 --lib --name adder
cd listing-11-01
echo "$ cargo test" > output.txt
RUSTFLAGS="-A unused_variables -A dead_code" RUST_TEST_THREADS=1 cargo test >> output.txt 2>&1
git diff output.txt # commit any relevant changes; discard irrelevant ones
cd ../../..
-->

```rust,noplayground
pub fn add(left: u64, right: u64) -> u64 {
    left + right
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn it_works() {
        let result = add(2, 2);
        assert_eq!(result, 4);
    }
}

```

</Listing>

该文件以示例函数 `add` 开始，这样我们就有东西可以测试了。

目前，让我们只关注 `it_works` 这个函数。请注意 `#[test]` 的注释：这个属性表明这是一个测试函数，因此测试运行器会将其视为测试函数来处理。在 `tests` 模块中，可能还有一些非测试函数，用于设置常见场景或执行常见操作。因此，我们必须始终明确哪些函数是测试函数。

这个示例函数体使用了 `assert_eq!` 宏来断言 `result` 的结果，该结果是通过将 `add` 与 2 和 2 一起调用后得到的，结果为 4。这个断言是一个典型测试格式的例子。让我们运行一下，看看这个测试是否通过。

`cargo test`命令会运行我们项目中的所有测试，如清单11-2所示。

<Listing number="11-2" caption="The output from running the automatically generated test">

```console
$ cargo test
   Compiling adder v0.1.0 (file:///projects/adder)
    Finished `test` profile [unoptimized + debuginfo] target(s) in 0.57s
     Running unittests src/lib.rs (target/debug/deps/adder-01ad14159ff659ab)

running 1 test
test tests::it_works ... ok

test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

   Doc-tests adder

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s


```

</Listing>

Cargo已经编译并运行了测试。我们看到一行代码为 `running 1 test`。下一行显示了生成的测试函数的名称，即 `tests::it_works`，而运行该测试的结果是 `ok`。整体总结 `test
result: ok.` 表示所有测试都通过了，而 `1
passed; 0 failed` 则统计了通过或失败的测试数量。

可以将某个测试标记为“忽略”，这样在特定的情况下该测试就不会被执行；我们将在本章后面的[“除非特别请求，否则忽略测试”][ignoring]<!-- ignore -->部分详细介绍这一点。由于我们在这里没有这样做，因此摘要显示的是`0 ignored`。我们还可以向`cargo test`命令传递一个参数，以仅运行名称与某个字符串匹配的测试；这被称为_过滤_，我们将在[“按名称运行部分测试”][subset]<!-- ignore -->部分进行介绍。在这里，我们没有过滤正在运行的测试，因此摘要的结尾显示的是`0 filtered out`。

`0 measured`这个统计指标用于衡量性能的参数测试。  
截至本文撰写时，这种参数测试仅在Rust的夜间版本中可用。如需了解更多相关信息，请参阅[关于参数测试的文档][bench]。

接下来部分的测试输出从 `Doc-tests adder` 开始，内容是关于任何文档测试的结果。目前我们还没有进行任何文档测试，但Rust可以编译我们API文档中的任何代码示例。这个功能有助于保持文档和代码的一致性！我们将在第十四章的[“将文档注释作为测试”][doc-comments]<!-- ignore -->部分讨论如何编写文档测试。目前，我们暂时忽略 `Doc-tests` 的输出内容。

让我们开始根据我们的需求自定义这个测试。首先，将 `it_works` 函数的名称改为另一个名称，比如 `exploration`，如下所示：

<span class="filename">文件名: src/lib.rs</span>

```rust,noplayground
pub fn add(left: u64, right: u64) -> u64 {
    left + right
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn exploration() {
        let result = add(2, 2);
        assert_eq!(result, 4);
    }
}

```

然后，再次运行 `cargo test`。现在输出结果显示为 `exploration`，而不是`it_works`。

```console
$ cargo test
   Compiling adder v0.1.0 (file:///projects/adder)
    Finished `test` profile [unoptimized + debuginfo] target(s) in 0.59s
     Running unittests src/lib.rs (target/debug/deps/adder-92948b65e88960b4)

running 1 test
test tests::exploration ... ok

test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

   Doc-tests adder

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s


```

现在，我们将添加另一个测试，但这次我们会编写一个会失败的测试！当测试函数中的某部分发生 panic 时，测试就会失败。每个测试都在一个新的线程中运行，当主线程发现某个测试线程已经终止时，该测试就会被标记为失败。在第九章中，我们讨论了最简单的方式来引发 panic，那就是调用 `panic!` 宏。现在，我们将新的测试作为一个名为 `another` 的函数来编写，这样你的 _src/lib.rs_ 文件看起来就像 Listing 11-3 所示。

<Listing number="11-3" file-name="src/lib.rs" caption="Adding a second test that will fail because we call the `panic!` macro">

```rust,panics,noplayground
pub fn add(left: u64, right: u64) -> u64 {
    left + right
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn exploration() {
        let result = add(2, 2);
        assert_eq!(result, 4);
    }

    #[test]
    fn another() {
        panic!("Make this test fail");
    }
}

```

</Listing>

使用 `cargo test` 再次运行测试。输出结果应类似于 Listing 11-4，这表明我们的 `exploration` 测试通过了，而 `another` 测试失败了。

<Listing number="11-4" caption="Test results when one test passes and one test fails">

```console
$ cargo test
   Compiling adder v0.1.0 (file:///projects/adder)
    Finished `test` profile [unoptimized + debuginfo] target(s) in 0.72s
     Running unittests src/lib.rs (target/debug/deps/adder-92948b65e88960b4)

running 2 tests
test tests::another ... FAILED
test tests::exploration ... ok

failures:

---- tests::another stdout ----

thread 'tests::another' panicked at src/lib.rs:17:9:
Make this test fail
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace


failures:
    tests::another

test result: FAILED. 1 passed; 1 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

error: test failed, to rerun pass `--lib`

```

</Listing>

<!-- manual-regeneration
rg panicked listings/ch11-writing-automated-tests/listing-11-03/output.txt
check the line number of the panic matches the line number in the following paragraph
 -->

在 `ok` 的替代方案中，出现了 `test tests::another` 这一行，其中又包含了 `FAILED`。在各个测试结果和总结之间新增了两个部分：第一部分详细说明了每次测试失败的原因。在这个例子中，我们了解到 `tests::another` 之所以失败，是因为在 _src/lib.rs_ 文件的第17行出现了 `Make
this test fail` 这样的错误信息。接下来的部分则列出了所有失败测试的名称，这在测试数量众多且失败测试的输出信息非常详细时非常有用。我们可以利用失败测试的名称来单独运行该测试，从而更轻松地进行调试；我们将在[“控制测试的运行方式”][controlling-how-tests-are-run]<!-- ignore -->部分进一步讨论如何运行测试。

总结行显示在最后：总体而言，我们的测试结果是 `FAILED`。我们有一项测试通过，一项测试失败。

既然你已经了解了在不同场景下测试结果的样子，
接下来让我们看看除了 `panic!` 之外，在测试中还有哪些有用的宏。

<!-- Old headings. Do not remove or links may break. -->

<a id="checking-results-with-the-assert-macro"></a>

### 使用 `assert!` 检查结果

标准库提供的`assert!`宏在需要确保某个测试条件满足`true`时非常有用。我们给`assert!`宏一个可以评估为布尔值的参数。如果该值为`true`，则不会发生任何事情，测试通过。如果值为`false`，则`assert!`宏会调用`panic!`来使测试失败。使用`assert!`宏可以帮助我们检查代码是否按照我们的预期运行。

在第五章的清单5-15中，我们使用了`Rectangle` struct和`can_hold`方法，这些在清单11-5中也有重复出现。请将这段代码放在src/lib.rs_文件中，然后使用`assert!`宏编写一些测试。

<Listing number="11-5" file-name="src/lib.rs" caption="The `Rectangle` struct and its `can_hold` method from Chapter 5">

```rust,noplayground
#[derive(Debug)]
struct Rectangle {
    width: u32,
    height: u32,
}

impl Rectangle {
    fn can_hold(&self, other: &Rectangle) -> bool {
        self.width > other.width && self.height > other.height
    }
}

```

</Listing>

`can_hold`方法返回一个布尔值，这意味着它是`assert!`宏的一个完美用例。在列表11-6中，我们编写了一个测试，通过创建一个宽度为8、高度为7的`Rectangle`实例来测试`can_hold`方法，并验证该实例是否能够容纳另一个宽度为5、高度为1的`Rectangle`实例。

<Listing number="11-6" file-name="src/lib.rs" caption="A test for `can_hold` that checks whether a larger rectangle can indeed hold a smaller rectangle">

```rust,noplayground
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn larger_can_hold_smaller() {
        let larger = Rectangle {
            width: 8,
            height: 7,
        };
        let smaller = Rectangle {
            width: 5,
            height: 1,
        };

        assert!(larger.can_hold(&smaller));
    }
}

```

</Listing>

请注意 `tests` 模块内的 `use super::*;` 行。 `tests` 模块是一个常规模块，遵循我们在 [“在模块树中引用项目的路径”][paths-for-referring-to-an-item-in-the-module-tree]<!-- ignore --> 章节中讨论的常规可见性规则。由于 `tests` 模块是一个内部模块，我们需要将外部模块中受测试的代码引入到内部模块的作用域内。在这里我们使用全局变量，因此外部模块中定义的任何内容都可供这个 `tests` 模块使用。

我们已经为我们的测试命名为 `larger_can_hold_smaller`，并且已经创建了两个所需的 `Rectangle` 实例。然后，我们调用了 `assert!` 宏，并将 `larger.can_hold(&smaller)` 的调用结果传递给它。这个表达式应该返回 `true`，所以我们的测试应该能够通过。让我们来看看结果吧！

```console
$ cargo test
   Compiling rectangle v0.1.0 (file:///projects/rectangle)
    Finished `test` profile [unoptimized + debuginfo] target(s) in 0.66s
     Running unittests src/lib.rs (target/debug/deps/rectangle-6584c4561e48942e)

running 1 test
test tests::larger_can_hold_smaller ... ok

test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

   Doc-tests rectangle

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s


```

确实如此！让我们再添加一个测试，这次来验证较小的矩形无法容纳较大的矩形：

<span class="filename">文件名: src/lib.rs</span>

```rust,noplayground
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn larger_can_hold_smaller() {
        // --snip--
    }

    #[test]
    fn smaller_cannot_hold_larger() {
        let larger = Rectangle {
            width: 8,
            height: 7,
        };
        let smaller = Rectangle {
            width: 5,
            height: 1,
        };

        assert!(!smaller.can_hold(&larger));
    }
}

```

因为在这种情况下，`can_hold`函数的正确结果是`false`，所以在将结果传递给`assert!`宏之前，我们需要先对这个结果进行取反操作。这样一来，如果`can_hold`返回的是`false`，那么我们的测试就会通过。

```console
$ cargo test
   Compiling rectangle v0.1.0 (file:///projects/rectangle)
    Finished `test` profile [unoptimized + debuginfo] target(s) in 0.66s
     Running unittests src/lib.rs (target/debug/deps/rectangle-6584c4561e48942e)

running 2 tests
test tests::larger_can_hold_smaller ... ok
test tests::smaller_cannot_hold_larger ... ok

test result: ok. 2 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

   Doc-tests rectangle

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s


```

两个测试都通过了！现在让我们看看，当我们在代码中引入一个错误时，测试结果会发生什么变化。我们将修改 `can_hold` 方法的实现，把大于号（`>`）替换为小于号（`<`)
when it compares the widths:

```rust,not_desired_behavior,noplayground
// --snip--
impl Rectangle {
    fn can_hold(&self, other: &Rectangle) -> bool {
        self.width < other.width && self.height > other.height
    }
}

```

Running the tests now produces the following:

```console
$ cargo test
   Compiling rectangle v0.1.0 (file:///projects/rectangle)
    Finished `test` profile [unoptimized + debuginfo] target(s) in 0.66s
     Running unittests src/lib.rs (target/debug/deps/rectangle-6584c4561e48942e)

running 2 tests
test tests::larger_can_hold_smaller ... FAILED
test tests::smaller_cannot_hold_larger ... ok

failures:

---- tests::larger_can_hold_smaller stdout ----

thread 'tests::larger_can_hold_smaller' panicked at src/lib.rs:28:9:
assertion failed: larger.can_hold(&smaller)
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace


failures:
    tests::larger_can_hold_smaller

test result: FAILED. 1 passed; 1 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

error: test failed, to rerun pass `--lib`

```

Our tests caught the bug! Because `larger.width` is `8` and `smaller.width` is
`5`, the comparison of the widths in `can_hold` now returns `false`: 8 is not
less than 5.

<!-- Old headings. Do not remove or links may break. -->

<a id="testing-equality-with-the-assert_eq-and-assert_ne-macros"></a>

### Testing Equality with `），并做一些相应的调整。具体代码如下：

```rust
assert_eq!` and `
assert_ne!`

A common way to verify functionality is to test for equality between the result
of the code under test and the value you expect the code to return. You could
do this by using the `
assert!` macro and passing it an expression using the
`==` operator. However, this is such a common test that the standard library
provides a pair of macros—`
assert_eq!` and `
assert_ne!`—to perform this test
more conveniently. These macros compare two arguments for equality or
inequality, respectively. They’ll also print the two values if the assertion
fails, which makes it easier to see _why_ the test failed; conversely, the
`
assert!` macro only indicates that it got a `false` value for the `==`
expression, without printing the values that led to the `false` value.

In Listing 11-7, we write a function named `
add_two` that adds `2` to its
parameter, and then we test this function using the `
assert_eq!` macro.

<Listing number="11-7" file-name="src/lib.rs" caption="Testing the function `add_two` using the `assert_eq!` macro">

```rust,noplayground
pub fn add_two(a: u64) -> u64 {
    a + 2
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn it_adds_two() {
        let result = add_two(2);
        assert_eq!(result, 4);
    }
}

```

</Listing>

Let’s check that it passes!

```console
$ cargo test
   Compiling adder v0.1.0 (file:///projects/adder)
    Finished `test` profile [unoptimized + debuginfo] target(s) in 0.58s
     Running unittests src/lib.rs (target/debug/deps/adder-92948b65e88960b4)

running 1 test
test tests::it_adds_two ... ok

test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

   Doc-tests adder

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s


```

We create a variable named `result` that holds the result of calling
`
add_two(2)`. Then, we pass `result` and `4` as the arguments to the
`
assert_eq!` macro. The output line for this test is `test tests::it_adds_two
... ok`, and the `ok` text indicates that our test passed!

Let’s introduce a bug into our code to see what `
assert_eq!` looks like when it
fails. Change the implementation of the `
add_two` function to instead add `3`:

```rust,not_desired_behavior,noplayground
pub fn add_two(a: u64) -> u64 {
    a + 3
}

```

Run the tests again:

```console
$ cargo test
   Compiling adder v0.1.0 (file:///projects/adder)
    Finished `test` profile [unoptimized + debuginfo] target(s) in 0.61s
     Running unittests src/lib.rs (target/debug/deps/adder-92948b65e88960b4)

running 1 test
test tests::it_adds_two ... FAILED

failures:

---- tests::it_adds_two stdout ----

thread 'tests::it_adds_two' panicked at src/lib.rs:12:9:
assertion `left == right` failed
  left: 5
 right: 4
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace


failures:
    tests::it_adds_two

test result: FAILED. 0 passed; 1 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

error: test failed, to rerun pass `--lib`

```

Our test caught the bug! The `
tests::it_adds_two` test failed, and the message
tells us that the assertion that failed was `
left == right` and what the `
left`
and `
right` values are. This message helps us start debugging: The `
left`
argument, where we had the result of calling `
add_two(2)`, was `
5`, but the
`
right` argument was `
4`. You can imagine that this would be especially helpful
when we have a lot of tests going on.

Note that in some languages and test frameworks, the parameters to equality
assertion functions are called `
expected` and `
actual`, and the order in which
we specify the arguments matters. However, in Rust, they’re called `
left` and
`
right`, and the order in which we specify the value we expect and the value
the code produces doesn’t matter. We could write the assertion in this test as
`
assert_eq!(4, result)`, which would result in the same failure message that
displays `
` assertion `
left == right` failed `
`.

The `
assert_ne!` macro will pass if the two values we give it are not equal and
will fail if they are equal. This macro is most useful for cases when we’re not
sure what a value _will_ be, but we know what the value definitely _shouldn’t_
be. For example, if we’re testing a function that is guaranteed to change its
input in some way, but the way in which the input is changed depends on the day
of the week that we run our tests, the best thing to assert might be that the
output of the function is not equal to the input.

Under the surface, the `
assert_eq!` and `
assert_ne!` macros use the operators
`
==` and `
!=`, respectively. When the assertions fail, these macros print their
arguments using debug formatting, which means the values being compared must
implement the `
PartialEq` and `
Debug` traits. All primitive types and most of
the standard library types implement these traits. For structs and enums that
you define yourself, you’ll need to implement `
PartialEq` to assert equality of
those types. You’ll also need to implement `
Debug` to print the values when the
assertion fails. Because both traits are derivable traits, as mentioned in
Listing 5-12 in Chapter 5, this is usually as straightforward as adding the
`
#[derive(PartialEq, Debug)]` annotation to your struct or enum definition. See
Appendix C, [“Derivable Traits,”][derivable-traits]<!-- ignore --> for more
details about these and other derivable traits.

### Adding Custom Failure Messages

You can also add a custom message to be printed with the failure message as
optional arguments to the `
assert!`, `
assert_eq!`, and `
assert_ne!` macros. Any
arguments specified after the required arguments are passed along to the
`
format!` macro (discussed in [“Concatenating with `
+` or
`
format!`”][concatenating]<!--
ignore --> in Chapter 8), so you can pass a format string that contains `
{}`
placeholders and values to go in those placeholders. Custom messages are useful
for documenting what an assertion means; when a test fails, you’ll have a better
idea of what the problem is with the code.

For example, let’s say we have a function that greets people by name and we
want to test that the name we pass into the function appears in the output:

<span class="filename">Filename: src/lib.rs</span>

```rust,noplayground
pub fn greeting(name: &str) -> String {
    format!("Hello {name}!")
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn greeting_contains_name() {
        let result = greeting("Carol");
        assert!(result.contains("Carol"));
    }
}

```

The requirements for this program haven’t been agreed upon yet, and we’re
pretty sure the `
Hello` text at the beginning of the greeting will change. We
decided we don’t want to have to update the test when the requirements change,
so instead of checking for exact equality to the value returned from the
`
greeting` function, we’ll just assert that the output contains the text of the
input parameter.

Now let’s introduce a bug into this code by changing `
greeting` to exclude
`
name` to see what the default test failure looks like:

```rust,not_desired_behavior,noplayground
pub fn greeting(name: &str) -> String {
    String::from("Hello!")
}

```

Running this test produces the following:

```console
$ cargo test
   Compiling greeter v0.1.0 (file:///projects/greeter)
    Finished `test` profile [unoptimized + debuginfo] target(s) in 0.91s
     Running unittests src/lib.rs (target/debug/deps/greeter-170b942eb5bf5e3a)

running 1 test
test tests::greeting_contains_name ... FAILED

failures:

---- tests::greeting_contains_name stdout ----

thread 'tests::greeting_contains_name' panicked at src/lib.rs:12:9:
assertion failed: result.contains("Carol")
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace


failures:
    tests::greeting_contains_name

test result: FAILED. 0 passed; 1 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

error: test failed, to rerun pass `--lib`

```

This result just indicates that the assertion failed and which line the
assertion is on. A more useful failure message would print the value from the
`
greeting` function. Let’s add a custom failure message composed of a format
string with a placeholder filled in with the actual value we got from the
`
greeting` function:

```rust,ignore
    #[test]
    fn greeting_contains_name() {
        let result = greeting("Carol");
        assert!(
            result.contains("Carol"),
            "Greeting did not contain name, value was `{result}`"
        );
    }

```

Now when we run the test, we’ll get a more informative error message:

```console
$ cargo test
   Compiling greeter v0.1.0 (file:///projects/greeter)
    Finished `test` profile [unoptimized + debuginfo] target(s) in 0.93s
     Running unittests src/lib.rs (target/debug/deps/greeter-170b942eb5bf5e3a)

running 1 test
test tests::greeting_contains_name ... FAILED

failures:

---- tests::greeting_contains_name stdout ----

thread 'tests::greeting_contains_name' panicked at src/lib.rs:12:9:
Greeting did not contain name, value was `Hello!`
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace


failures:
    tests::greeting_contains_name

test result: FAILED. 0 passed; 1 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

error: test failed, to rerun pass `--lib`

```

We can see the value we actually got in the test output, which would help us
debug what happened instead of what we were expecting to happen.

### Checking for Panics with `
should_panic`

In addition to checking return values, it’s important to check that our code
handles error conditions as we expect. For example, consider the `
Guess` type
that we created in Chapter 9, Listing 9-13. Other code that uses `
Guess`
depends on the guarantee that `
Guess` instances will contain only values
between 1 and 100. We can write a test that ensures that attempting to create a
`
Guess` instance with a value outside that range panics.

We do this by adding the attribute `
should_panic` to our test function. The
test passes if the code inside the function panics; the test fails if the code
inside the function doesn’t panic.

Listing 11-8 shows a test that checks that the error conditions of `
Guess::new`
happen when we expect them to.

<Listing number="11-8" file-name="src/lib.rs" caption="Testing that a condition will cause a `panic!`">

```rust,noplayground
pub struct Guess {
    value: i32,
}

impl Guess {
    pub fn new(value: i32) -> Guess {
        if value < 1 || value > 100 {
            panic!("Guess value must be between 1 and 100, got {value}.");
        }

        Guess { value }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    #[should_panic]
    fn greater_than_100() {
        Guess::new(200);
    }
}

```

</Listing>

We place the `
#[should_panic]` attribute after the `
#[test]` attribute and
before the test function it applies to. Let’s look at the result when this test
passes:

```console
$ cargo test
   Compiling guessing_game v0.1.0 (file:///projects/guessing_game)
    Finished `test` profile [unoptimized + debuginfo] target(s) in 0.58s
     Running unittests src/lib.rs (target/debug/deps/guessing_game-57d70c3acb738f4d)

running 1 test
test tests::greater_than_100 - should panic ... ok

test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

   Doc-tests guessing_game

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s


```

Looks good! Now let’s introduce a bug in our code by removing the condition
that the `
new` function will panic if the value is greater than 100:

```rust,not_desired_behavior,noplayground
// --snip--
impl Guess {
    pub fn new(value: i32) -> Guess {
        if value < 1 {
            panic!("Guess value must be between 1 and 100, got {value}.");
        }

        Guess { value }
    }
}

```

When we run the test in Listing 11-8, it will fail:

```console
$ cargo test
   Compiling guessing_game v0.1.0 (file:///projects/guessing_game)
    Finished `test` profile [unoptimized + debuginfo] target(s) in 0.62s
     Running unittests src/lib.rs (target/debug/deps/guessing_game-57d70c3acb738f4d)

running 1 test
test tests::greater_than_100 - should panic ... FAILED

failures:

---- tests::greater_than_100 stdout ----
note: test did not panic as expected at src/lib.rs:21:8

failures:
    tests::greater_than_100

test result: FAILED. 0 passed; 1 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

error: test failed, to rerun pass `--lib`

```

We don’t get a very helpful message in this case, but when we look at the test
function, we see that it’s annotated with `
#[should_panic]`. The failure we got
means that the code in the test function did not cause a panic.

Tests that use `
should_panic` can be imprecise. A `
should_panic` test would
pass even if the test panics for a different reason from the one we were
expecting. To make `
should_panic` tests more precise, we can add an optional
`
expected` parameter to the `
should_panic` attribute. The test harness will
make sure that the failure message contains the provided text. For example,
consider the modified code for `
Guess` in Listing 11-9 where the `
new` function
panics with different messages depending on whether the value is too small or
too large.

<Listing number="11-9" file-name="src/lib.rs" caption="Testing for a `panic!` with a panic message containing a specified substring">

```rust,noplayground
// --snip--

impl Guess {
    pub fn new(value: i32) -> Guess {
        if value < 1 {
            panic!(
                "Guess value must be greater than or equal to 1, got {value}."
            );
        } else if value > 100 {
            panic!(
                "Guess value must be less than or equal to 100, got {value}."
            );
        }

        Guess { value }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    #[should_panic(expected = "less than or equal to 100")]
    fn greater_than_100() {
        Guess::new(200);
    }
}

```

</Listing>

This test will pass because the value we put in the `
should_panic` attribute’s
`
expected` parameter is a substring of the message that the `
Guess::new`
function panics with. We could have specified the entire panic message that we
expect, which in this case would be `
Guess 的值必须小于或等于 100，实际得到的是 200`. What you choose to specify depends on how much of the panic
message is unique or dynamic and how precise you want your test to be. In this
case, a substring of the panic message is enough to ensure that the code in the
test function executes the `
否则如果值大于 100` case.

To see what happens when a `
应该会抛出错误` test with an `
预期结果` message
fails, let’s again introduce a bug into our code by swapping the bodies of the
`
如果值小于或等于 100< 1` and the `else if value >
应该是 100` blocks:

```rust,ignore,not_desired_behavior
        if value < 1 {
            panic!(
                "Guess value must be less than or equal to 100, got {value}."
            );
        } else if value > 100 {
            panic!(
                "Guess value must be greater than or equal to 1, got {value}."
            );
        }

```

This time when we run the `
应该会抛出错误` test, it will fail:

```console
$ cargo test
   Compiling guessing_game v0.1.0 (file:///projects/guessing_game)
    Finished `test` profile [unoptimized + debuginfo] target(s) in 0.66s
     Running unittests src/lib.rs (target/debug/deps/guessing_game-57d70c3acb738f4d)

running 1 test
test tests::greater_than_100 - should panic ... FAILED

failures:

---- tests::greater_than_100 stdout ----

thread 'tests::greater_than_100' panicked at src/lib.rs:12:13:
Guess value must be greater than or equal to 1, got 200.
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace
note: panic did not contain expected string
      panic message: "Guess value must be greater than or equal to 1, got 200."
 expected substring: "less than or equal to 100"

failures:
    tests::greater_than_100

test result: FAILED. 0 passed; 1 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

error: test failed, to rerun pass `--lib`

```

The failure message indicates that this test did indeed panic as we expected,
but the panic message did not include the expected string `
必须小于或等于 100`. The panic message that we did get in this case was `
Guess 的值必须大于或等于 1，实际得到的是 200`. Now we can start figuring out where
our bug is!

### Using `
Result<T, E>
` in Tests

All of our tests so far panic when they fail. We can also write tests that use
`
Result<T, E>
`! Here’s the test from Listing 11-1, rewritten to use `
Result<T,
E>
` and return an `
Err` instead of panicking:

```rust,noplayground
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn it_works() -> Result<(), String> {
        let result = add(2, 2);

        if result == 4 {
            Ok(())
        } else {
            Err(String::from("two plus two does not equal four"))
        }
    }
}

```

The `
it_works` function now has the `
Result<(), String>
⊂PH105

[concatenating]: ch08-02-strings.html#concatenating-with--or-format
[bench]: ../unstable-book/library-features/test.html
[ignoring]: ch11-02-running-tests.html#ignoring-tests-unless-specifically-requested
[subset]: ch11-02-running-tests.html#running-a-subset-of-tests-by-name
[controlling-how-tests-are-run]: ch11-02-running-tests.html#controlling-how-tests-are-run
[derivable-traits]: appendix-03-derivable-traits.html
[doc-comments]: ch14-02-publishing-to-crates-io.html#documentation-comments-as-tests
[paths-for-referring-to-an-item-in-the-module-tree]: ch07-03-paths-for-referring-to-an-item-in-the-module-tree.html
