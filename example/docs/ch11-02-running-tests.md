## 控制测试的执行方式

就像 `cargo run` 会编译你的代码并运行生成的二进制文件一样，`cargo test` 会在测试模式下编译你的代码，并运行相应的测试二进制文件。`cargo test` 生成的二进制文件的默认行为是并行运行所有测试，并捕获测试过程中生成的输出，从而避免输出被显示，使得与测试结果相关的输出更容易阅读。不过，你可以指定命令行选项来更改这一默认行为。

一些命令行选项会直接传递给 `cargo test`，而另一些则会被传递到最终的测试二进制文件上。为了区分这两种类型的参数，你需要先列出那些会直接传递给 `cargo test` 的参数，然后使用分隔符 `--` 来分隔它们，最后列出那些会被传递到测试二进制文件上的参数。运行 `cargo test --help` 可以显示可以与 `cargo test` 一起使用的选项，而运行 `cargo test -- --help` 则可以显示在分隔符之后可以使用的选项。这些选项也在《The `rustc` Book_》的“Tests”章节中有详细说明。[tests]

[tests]: https://doc.rust-lang.org/rustc/tests/index.html

### 并行或连续运行测试

当你运行多个测试时，默认情况下，这些测试会通过线程并行执行，这意味着它们会更快地完成，并且你可以更快地获得反馈。由于测试是同时进行的，因此你必须确保测试之间不相互依赖，也不依赖于任何共享状态，包括共享环境，比如当前的工作目录或环境变量。

例如，假设每个测试都会运行一些代码，这些代码会在磁盘上创建一个名为`_test-output.txt`的文件，并将一些数据写入该文件。然后，每个测试都会读取该文件中的数据，并断言文件中包含特定的值，而这些值在每个测试中是不同的。由于测试是同时运行的，一个测试可能会在另一个测试写入和读取文件之间的时间内覆盖该文件。这样一来，第二个测试就会失败，但这不是因为代码本身有问题，而是因为测试在并行运行时相互干扰了。一种解决方案是确保每个测试写入不同的文件；另一种解决方案则是一次只运行一个测试。

如果您不想并行运行测试，或者希望对使用的线程数量进行更精细的控制，可以向测试二进制文件发送 `--test-threads` 标志以及您希望使用的线程数量。请参考以下示例：

```console
$ cargo test -- --test-threads=1
```

我们将测试线程的数量设置为 `1`，这样程序就不会使用任何并行处理。使用单个线程进行测试所需的时间会比并行测试更长，但如果测试之间共享状态的话，它们就不会互相干扰。

### 显示函数输出

默认情况下，如果测试通过，Rust的测试库会捕获所有输出到标准输出的内容。例如，如果我们在一个测试中调用 `println!`，并且测试通过，那么我们在终端上不会看到 `println!` 的输出内容，而只会看到表示测试通过的行。如果测试失败，我们就会看到所有输出到标准输出的内容，以及失败的其余信息。

例如，列表11-10中有一个简单的功能，它打印出参数的值，并返回10。此外，还有一个通过测试的例子和一个未通过测试的例子。

<Listing number="11-10" file-name="src/lib.rs" caption="Tests for a function that calls `println!`">

```rust,panics,noplayground
fn prints_and_returns_10(a: i32) -> i32 {
    println!("I got the value {a}");
    10
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn this_test_will_pass() {
        let value = prints_and_returns_10(4);
        assert_eq!(value, 10);
    }

    #[test]
    fn this_test_will_fail() {
        let value = prints_and_returns_10(8);
        assert_eq!(value, 5);
    }
}

```

</Listing>

当我们使用 `cargo test` 运行这些测试时，将会看到以下输出：

```console
$ cargo test
   Compiling silly-function v0.1.0 (file:///projects/silly-function)
    Finished `test` profile [unoptimized + debuginfo] target(s) in 0.58s
     Running unittests src/lib.rs (target/debug/deps/silly_function-160869f38cff9166)

running 2 tests
test tests::this_test_will_fail ... FAILED
test tests::this_test_will_pass ... ok

failures:

---- tests::this_test_will_fail stdout ----
I got the value 8

thread 'tests::this_test_will_fail' panicked at src/lib.rs:19:9:
assertion `left == right` failed
  left: 10
 right: 5
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace


failures:
    tests::this_test_will_fail

test result: FAILED. 1 passed; 1 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

error: test failed, to rerun pass `--lib`

```

请注意，在这个输出中，我们并没有看到 `I got the value 4`，这个符号是在测试通过时打印出来的。该输出已经被记录下来。而测试失败的输出，即 `I got the value 8`，则出现在测试总结的输出部分，该部分还说明了测试失败的原因。

如果我们还想看到通过测试时的输出结果，我们可以告诉Rust，让它同时显示成功测试的输出结果，使用 `--show-output`：

```console
$ cargo test -- --show-output
```

当我们再次使用 `--show-output` 标志运行清单 11-10 中的测试时，我们得到以下输出：

```console
$ cargo test -- --show-output
   Compiling silly-function v0.1.0 (file:///projects/silly-function)
    Finished `test` profile [unoptimized + debuginfo] target(s) in 0.60s
     Running unittests src/lib.rs (target/debug/deps/silly_function-160869f38cff9166)

running 2 tests
test tests::this_test_will_fail ... FAILED
test tests::this_test_will_pass ... ok

successes:

---- tests::this_test_will_pass stdout ----
I got the value 4


successes:
    tests::this_test_will_pass

failures:

---- tests::this_test_will_fail stdout ----
I got the value 8

thread 'tests::this_test_will_fail' panicked at src/lib.rs:19:9:
assertion `left == right` failed
  left: 10
 right: 5
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace


failures:
    tests::this_test_will_fail

test result: FAILED. 1 passed; 1 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

error: test failed, to rerun pass `--lib`

```

### 按名称运行部分测试

运行整个测试套件有时可能需要很长时间。如果你正在某个特定区域进行代码开发，你可能只想运行与那些代码相关的测试。你可以通过传递你想运行的测试的名称作为参数来选择要运行的测试。

为了演示如何运行部分测试，我们将首先为我们的 `add_two` 函数创建三个测试，如清单 11-11 所示，然后选择要运行的测试。

<Listing number="11-11" file-name="src/lib.rs" caption="Three tests with three different names">

```rust,noplayground
pub fn add_two(a: u64) -> u64 {
    a + 2
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn add_two_and_two() {
        let result = add_two(2);
        assert_eq!(result, 4);
    }

    #[test]
    fn add_three_and_two() {
        let result = add_two(3);
        assert_eq!(result, 5);
    }

    #[test]
    fn one_hundred() {
        let result = add_two(100);
        assert_eq!(result, 102);
    }
}

```

</Listing>

如果我们在不传递任何参数的情况下运行测试，正如我们之前看到的那样，所有测试都将并行运行。

```console
$ cargo test
   Compiling adder v0.1.0 (file:///projects/adder)
    Finished `test` profile [unoptimized + debuginfo] target(s) in 0.62s
     Running unittests src/lib.rs (target/debug/deps/adder-92948b65e88960b4)

running 3 tests
test tests::add_three_and_two ... ok
test tests::add_two_and_two ... ok
test tests::one_hundred ... ok

test result: ok. 3 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

   Doc-tests adder

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s


```

#### 运行单个测试

我们可以传递任何测试函数的名称给 `cargo test`，以便仅运行该测试。

```console
$ cargo test one_hundred
   Compiling adder v0.1.0 (file:///projects/adder)
    Finished `test` profile [unoptimized + debuginfo] target(s) in 0.69s
     Running unittests src/lib.rs (target/debug/deps/adder-92948b65e88960b4)

running 1 test
test tests::one_hundred ... ok

test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 2 filtered out; finished in 0.00s


```

只有名为 `one_hundred` 的测试运行了；其他两个测试并没有使用那个名称。测试输出显示，还有更多的测试没有运行，这些测试的名称被标记为 `2 filtered out`。

我们无法以这种方式指定多个测试的名称；只会使用传给 `cargo test` 的第一个值。不过，还是有办法运行多个测试。

#### 过滤以运行多个测试

我们可以指定某个测试的名称的一部分，任何名称与该部分匹配的测试都会被运行。例如，因为我们的两个测试的名称中都包含 `add`，我们可以通过运行 `cargo test add` 来运行这两个测试。

```console
$ cargo test add
   Compiling adder v0.1.0 (file:///projects/adder)
    Finished `test` profile [unoptimized + debuginfo] target(s) in 0.61s
     Running unittests src/lib.rs (target/debug/deps/adder-92948b65e88960b4)

running 2 tests
test tests::add_three_and_two ... ok
test tests::add_two_and_two ... ok

test result: ok. 2 passed; 0 failed; 0 ignored; 0 measured; 1 filtered out; finished in 0.00s


```

该命令执行了所有以 `add` 为名称的测试，并过滤掉了名为 `one_hundred` 的测试。另外需要注意的是，某个测试所在的模块会成为该测试名称的一部分，因此我们可以通过过滤模块名称来运行某个模块中的所有测试。

<!-- Old headings. Do not remove or links may break. -->

<a id="ignoring-some-tests-unless-specifically-requested"></a>

### 除非特别要求，否则忽略测试

有时候，一些特定的测试执行起来会非常耗时，因此你可能希望在大多数 `cargo test` 的运行过程中将其排除在外。与其将所有需要运行的测试作为参数列出，不如使用 `ignore` 属性来标记那些耗时的测试，从而将其排除在外，如下所示：

<span class="filename">文件名: src/lib.rs</span>

```rust,noplayground
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn it_works() {
        let result = add(2, 2);
        assert_eq!(result, 4);
    }

    #[test]
    #[ignore]
    fn expensive_test() {
        // code that takes an hour to run
    }
}

```

在 `#[test]` 之后，我们在想要排除的测试中添加了 `#[ignore]` 这一行。现在，当我们运行测试时， `it_works` 会运行，而 `expensive_test` 则不会运行。

```console
$ cargo test
   Compiling adder v0.1.0 (file:///projects/adder)
    Finished `test` profile [unoptimized + debuginfo] target(s) in 0.60s
     Running unittests src/lib.rs (target/debug/deps/adder-92948b65e88960b4)

running 2 tests
test tests::expensive_test ... ignored
test tests::it_works ... ok

test result: ok. 1 passed; 0 failed; 1 ignored; 0 measured; 0 filtered out; finished in 0.00s

   Doc-tests adder

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s


```

函数 `expensive_test` 被列为 `ignored`。如果我们只想运行被忽略的测试，可以使用 `cargo test -- --ignored`。

```console
$ cargo test -- --ignored
   Compiling adder v0.1.0 (file:///projects/adder)
    Finished `test` profile [unoptimized + debuginfo] target(s) in 0.61s
     Running unittests src/lib.rs (target/debug/deps/adder-92948b65e88960b4)

running 1 test
test tests::expensive_test ... ok

test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 1 filtered out; finished in 0.00s

   Doc-tests adder

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s


```

通过控制哪些测试会运行，你可以确保 `cargo test` 的结果能够尽快被返回。当你认为检查 `ignored` 测试的结果是有意义的，并且你有时间等待这些结果时，可以选择运行 `cargo test -- --ignored`。如果你想运行所有测试，无论它们是否被忽略，就可以选择运行 `cargo test -- --include-ignored`。