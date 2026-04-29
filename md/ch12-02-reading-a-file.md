## 读取文件

现在，我们将为读取由`file_path`参数指定的文件添加功能。首先，我们需要一个示例文件来进行测试：我们将使用一个包含多行文本的文件，其中有一些重复的单词。列表12-3中有一段艾米莉·狄金森的诗，非常适合作为测试用。请在项目的根目录下创建一个名为_poem.txt_的文件，并将这首诗“I’m Nobody! Who are you?”写入该文件中。

<Listing number="12-3" file-name="poem.txt" caption="艾米莉·狄金森的一首诗是一个很好的测试案例。">

```text
{{#include ../listings/ch12-an-io-project/listing-12-03/poem.txt}}
```

</清单>

在文本准备就绪后，编辑`_src/main.rs_`文件，并添加代码来读取该文件，如清单12-4所示。

<列表编号="12-4" 文件名称="src/main.rs" 标题="读取由第二个参数指定的文件内容">

```rust,should_panic,noplayground
{{#rustdoc_include ../listings/ch12-an-io-project/listing-12-04/src/main.rs:here}}
```

</清单>

首先，我们通过使用`use`语句引入标准库中的相关部分：我们需要`std::fs`来处理文件。

在`main`中，新的语句`fs::read_to_string`会获取`file_path`，打开该文件，并返回一个类型为`std::io::Result<String>`的值，该值包含了文件的内容。

之后，我们再次添加一个临时的`println!`语句，该语句在文件读取后打印出`contents`的值，这样我们就可以检查程序目前是否正常运行。

让我们使用任何字符串作为第一个命令行参数来运行这段代码（因为我们还没有实现搜索部分），并将`_poem.txt_`文件作为第二个参数来运行：

```console
{{#rustdoc_include ../listings/ch12-an-io-project/listing-12-04/output.txt}}
```

太好了！代码能够读取文件内容并打印出来。不过代码中还有一些缺陷。目前，`main`这个函数承担了多个职责：通常来说，如果每个函数只负责一个功能，那么代码会更清晰且更容易维护。另一个问题是，我们还没有很好地处理错误。程序规模还很小，所以这些缺陷还不算大问题，但随着程序的扩展，这些问题将变得更加难以解决。将它们清理干净。在开发程序的过程中尽早进行重构是一个很好的做法，因为这样更容易对少量代码进行重构。接下来我们将执行这一操作。