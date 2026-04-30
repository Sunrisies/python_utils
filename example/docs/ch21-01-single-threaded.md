## 构建单线程Web服务器

我们将从让单线程的Web服务器运行开始。在开始之前，先快速了解一下构建Web服务器所涉及的协议。这些协议的详细内容超出了本书的范围，但简要的概述将为你提供所需的信息。

在网页服务器中，主要使用的两种协议是 _超文本传输协议_（HTTP）和 _传输控制协议_（TCP）。这两种协议都是 _请求-响应_ 协议，也就是说，由 _客户端_ 发起请求，而 _服务器_ 会监听这些请求并向客户端返回响应。这些请求和响应的内容是由协议本身来定义的。

TCP是一种底层协议，它描述了信息如何从一台服务器传输到另一台服务器，但并没有具体说明这些信息的具体内容。HTTP是在TCP的基础上构建的，它定义了请求和响应的内容。从技术上讲，可以使用HTTP与其他协议一起使用，但在绝大多数情况下，HTTP是通过TCP来传输数据的。我们将使用TCP和HTTP请求与响应的原始字节数据进行处理。

### 监听 TCP 连接

我们的网络服务器需要监听一个TCP连接，所以这是我们首先要处理的部分。标准库提供了一个名为 `std::net` 的模块，可以帮助我们实现这一功能。让我们以常规方式创建一个新的项目：

```console
$ cargo new hello
     Created binary (application) `hello` project
$ cd hello
```

现在在 _src/main.rs_ 文件中输入 Listing 21-1 中的代码以开始运行。这段代码会监听本地地址 `127.0.0.1:7878`，以接收传入的 TCP 流。当接收到流时，它会打印出 `Connection established!`。

**清单 21-1:** *src/main.rs* — 监听传入的流，并在接收到流时打印一条消息

```rust,no_run
use std::net::TcpListener;

fn main() {
    let listener = TcpListener::bind("127.0.0.1:7878").unwrap();

    for stream in listener.incoming() {
        let stream = stream.unwrap();

        println!("Connection established!");
    }
}

```

使用 `TcpListener`，我们可以监听地址`127.0.0.1:7878`上的TCP连接。在这个地址中，冒号前面的部分是一个IP地址，它代表你的计算机（这个IP地址在每台计算机上都是相同的，并不是特指作者的计算机）。而 `7878`则是端口号。我们选择这个端口有两点原因：通常情况下，HTTP协议不会使用这个端口，因此我们的服务器不太可能与你机器上运行的其他Web服务器产生冲突；另外，数字7878在电话中发音与“rust”这个单词很相似。

在这种情况下，函数 `bind` 的工作方式与函数 `new` 类似，它都会返回一个新的 `TcpListener` 实例。之所以称这个函数为 `bind`，是因为在网络领域，连接到某个端口以进行监听的行为被称为“绑定到端口”。

函数 `bind` 返回一个 `Result<T, E>`，这表明绑定可能会失败。例如，如果我们运行了两个版本的程序，那么就会有两个程序监听同一个端口。由于我们编写的是一个用于学习的简单服务器，因此不必担心处理这类错误。相反，我们使用 `unwrap` 来在出现错误时停止程序。

在 `TcpListener` 上定义的 `incoming` 方法返回一个迭代器，该迭代器为我们提供一系列流（更具体地说，是类型为 `TcpStream` 的流）。一个单独的 _Stream_ 代表了客户端与服务器之间的开放连接。_Connection_ 是指整个请求和响应过程的总称，在这个过程中，客户端连接到服务器，服务器生成响应，然后服务器关闭连接。因此，我们将从 `TcpStream` 中读取客户端发送的数据，然后将数据写入相应的流中，以将数据发送回客户端。总体而言，这个 `for` 循环会依次处理每个连接，并生成一系列我们需要处理的流。

目前，我们对流的处理方式是调用 `unwrap` 来在流出现任何错误时终止程序；如果没有错误，程序会打印一条消息。我们将在下一个代码示例中添加更多针对成功情况的 기능。当我们客户端连接到服务器时，可能会从 `incoming` 方法中收到错误，原因是我们实际上并不是在迭代连接，而是在迭代_连接尝试_。连接失败可能有多种原因，其中许多原因与操作系统有关。例如，许多操作系统都有对同时可支持的开放连接数量的限制；超过该数量的新的连接尝试将会产生错误，直到一些开放的连接被关闭为止。

让我们尝试运行这段代码吧！在终端中调用 `cargo run`，然后在网页浏览器中加载 _127.0.0.1:7878_。浏览器应该会显示一条错误消息，比如“连接重置”，因为服务器目前没有返回任何数据。但是，当你查看终端时，你会看到一些在浏览器连接到服务器时打印出来的消息！

```text
     Running `target/debug/hello`
Connection established!
Connection established!
Connection established!
```

有时候，同一个浏览器请求会显示多条消息。这可能是因为浏览器不仅请求了页面内容，还请求了其他资源，比如出现在浏览器标签页中的 _favicon.ico_ 图标。

也可能是浏览器试图多次连接到服务器，因为服务器没有返回任何数据。当 `stream` 超出作用范围并在循环结束时被丢弃时，连接作为 `drop` 实现的一部分被关闭了。浏览器有时会通过重试来处理已关闭的连接，因为问题可能是暂时的。

浏览器有时也会打开多个与服务器的连接，而无需发送任何请求。这样，当它们最终确实发送请求时，这些请求就能更快地完成。在这种情况下，我们的服务器会看到每一个连接，无论该连接是否有任何请求在进行中。例如，许多基于Chrome浏览器的版本都会采用这种优化方式；你可以通过使用隐私浏览模式或使用其他浏览器来禁用这种优化。

重要的是，我们成功建立了一个 TCP连接！

在运行特定版本的代码时，请记得通过按下 <kbd>ctrl</kbd>-<kbd>C</kbd> 来停止程序。然后，在每次对代码进行更改后，再次通过调用 `cargo run` 命令来重新启动程序，以确保运行的是最新版本的代码。

### 阅读请求信息

让我们实现从浏览器读取请求的功能吧！为了将获取连接以及后续操作这两个步骤分开处理，我们将创建一个新的函数来处理连接。在这个新的 `handle_connection` 函数中，我们将从 TCP 流中读取数据并打印出来，这样我们就可以看到从浏览器发送过来的数据。请修改代码，使其类似于 Listing 21-2 所示。

**清单 21-2:** *src/main.rs* — 从 `TcpStream` 读取数据并打印出来

```rust,no_run
use std::{
    io::{BufReader, prelude::*},
    net::{TcpListener, TcpStream},
};

fn main() {
    let listener = TcpListener::bind("127.0.0.1:7878").unwrap();

    for stream in listener.incoming() {
        let stream = stream.unwrap();

        handle_connection(stream);
    }
}

fn handle_connection(mut stream: TcpStream) {
    let buf_reader = BufReader::new(&stream);
    let http_request: Vec<_> = buf_reader
        .lines()
        .map(|result| result.unwrap())
        .take_while(|line| !line.is_empty())
        .collect();

    println!("Request: {http_request:#?}");
}

```

我们将 `std::io::BufReader` 和 `std::io::prelude` 纳入范围，以便访问那些允许我们读取和写入流的数据类型和 trait。在 `for` 循环中，使用 `main` 函数时，我们不再打印一条表示我们已经建立连接的消息，而是调用新的 `handle_connection` 函数，并将 `stream` 作为参数传递给它。

在 `handle_connection` 函数中，我们创建了一个新的 `BufReader` 实例，该实例会引用 `stream`。 `BufReader` 通过管理对 `std::io::Read` 特性方法的调用，实现了缓冲功能。

我们创建了一个名为 `http_request` 的变量来收集浏览器发送到我们服务器的请求行。为了将这些行存储在一个向量中，我们添加了 `Vec<_>` 类型的注释。

`BufReader` 实现了 `std::io::BufRead` 特质，该特质提供了 `lines` 方法。`lines` 方法在遇到换行符时，通过分割数据流来返回一个 `Result<String,
std::io::Error>` 的迭代器。为了获取每个 `String`，我们需要 `map` 和 `unwrap` 每个 `Result`。如果数据不是有效的 UTF-8 编码，或者从流中读取数据时出现问题，`Result` 可能会出错。当然，一个生产级程序应该能够更优雅地处理这些错误，但出于简单性的考虑，我们选择在出现错误的情况下终止程序。

浏览器通过连续发送两个换行字符来指示HTTP请求结束。为了从流中获取一个请求，我们需要不断读取行，直到遇到一个空字符串。一旦我们将这些行收集到向量中，就会使用漂亮的调试格式将它们打印出来，这样我们就可以查看网络浏览器发送给我们的服务器中的指令。

让我们尝试这段代码吧！启动程序，并在网页浏览器中再次发起请求。请注意，在浏览器中我们仍然会看到错误页面，但程序在终端中的输出现在看起来会像这样：

<!-- manual-regeneration
cd listings/ch21-web-server/listing-21-02
cargo run
make a request to 127.0.0.1:7878
Can't automate because the output depends on making requests
-->

```console
$ cargo run
   Compiling hello v0.1.0 (file:///projects/hello)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.42s
     Running `target/debug/hello`
Request: [
    "GET / HTTP/1.1",
    "Host: 127.0.0.1:7878",
    "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:99.0) Gecko/20100101 Firefox/99.0",
    "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language: en-US,en;q=0.5",
    "Accept-Encoding: gzip, deflate, br",
    "DNT: 1",
    "Connection: keep-alive",
    "Upgrade-Insecure-Requests: 1",
    "Sec-Fetch-Dest: document",
    "Sec-Fetch-Mode: navigate",
    "Sec-Fetch-Site: none",
    "Sec-Fetch-User: ?1",
    "Cache-Control: max-age=0",
]
```

根据您的浏览器不同，您可能会看到略微不同的输出结果。现在，当我们打印出请求数据后，通过观察请求第一行中 `GET` 后面的路径，我们可以理解为什么同一个浏览器请求会触发多次连接。如果这些重复的连接都是请求 _/_，那么我们可以判断浏览器试图反复获取 _/_，因为它没有从我们的程序中获得任何响应。

让我们分析一下这些请求数据，以了解浏览器对我们的程序提出了什么要求。

<!-- Old headings. Do not remove or links may break. -->

<a id="a-closer-look-at-an-http-request"></a>
<a id="looking-closer-at-an-http-request"></a>

### 更仔细地观察一个HTTP请求

HTTP是一种基于文本的协议，一个请求的格式如下：

```text
Method Request-URI HTTP-Version CRLF
headers CRLF
message-body
```

第一行是 _请求行_，其中包含了客户端请求的相关信息。请求行的第一部分表示所使用的方法，例如 `GET` 或 `POST`，这些描述了客户端是如何发起请求的。我们的客户端使用了 `GET` 请求，这意味着它正在请求信息。

请求行的下一部分是_/_，它表示客户端请求的_统一资源标识符_（URI）。URI几乎与_统一资源定位器_（URL）相同，但并不完全一样。在本章中，URI和URL之间的区别并不重要，但HTTP规范使用术语_URI_，因此在这里我们可以将_URI_简称为_URL_。

最后一部分是客户端使用的 HTTP 版本，然后请求行以 CRLF 序列结尾。_CRLF_ 代表 _carriage return_ 和 _line feed_，这些术语源自打字机时代！CRLF 序列也可以写作 `\r\n`，其中 `\r` 是回车，而 `\n` 是换行。这个 CRLF 序列用于将请求行与请求数据的其余部分分开。需要注意的是，当打印出 CRLF 时，我们看到的是新的一行，而不是 `\r\n`。

查看到目前为止我们从运行程序时收到的请求行数据，我们发现 `GET` 是方法名，_/_ 是请求 URI，而 `HTTP/1.1` 则是版本号。

在请求行之后，从 `Host:` 开始的剩余行都是头部信息。 `GET` 请求没有正文内容。

尝试使用不同的浏览器发起请求，或者请求不同的地址，例如 _127.0.0.1:7878/test_，以观察请求数据的变化。

既然我们已经知道了浏览器在请求什么，那么现在就发送一些数据回去吧！

### 编写响应

我们将实现根据客户端请求发送数据的功能。  
响应的格式如下：

```text
HTTP-Version Status-Code Reason-Phrase CRLF
headers CRLF
message-body
```

第一行是一个_状态行_，其中包含响应中使用的HTTP版本、总结请求结果的数字状态代码，以及提供状态代码文本描述的说明短语。在CRLF序列之后是任何头部信息、另一个CRLF序列，以及响应的主体内容。

以下是一个示例响应，它使用 HTTP 1.1 版本，状态码为 200，原因短语为 “OK”，没有头部信息，也没有正文：

```text
HTTP/1.1 200 OK\r\n\r\n
```

状态码 200 是标准的成功响应。该文本表示一个成功的 HTTP 响应。我们将使用 Listing 21-3 中的代码来生成这个响应，以回应一个成功的请求！从 `handle_connection` 函数中，移除负责打印请求数据的 `println!` 部分，并用 Listing 21-3 中的代码替换它。

**清单 21-3:** *src/main.rs* — 向流中写入一个小型成功的 HTTP 响应

```rust,no_run
fn handle_connection(mut stream: TcpStream) {
    let buf_reader = BufReader::new(&stream);
    let http_request: Vec<_> = buf_reader
        .lines()
        .map(|result| result.unwrap())
        .take_while(|line| !line.is_empty())
        .collect();

    let response = "HTTP/1.1 200 OK\r\n\r\n";

    stream.write_all(response.as_bytes()).unwrap();
}

```

第一行定义了 `response` 变量，用于存储成功消息的数据。然后，我们在 `response` 中调用 `as_bytes` 方法，将字符串数据转换为字节数据。 `stream` 上的 `write_all` 方法接受一个 `&[u8]` 参数，并将这些字节数据直接通过连接传输。由于 `write_all` 操作可能会失败，我们像之前一样使用 `unwrap` 来处理任何错误结果。当然，在实际应用中，你还需要在这里添加错误处理。

经过这些修改后，让我们运行代码并发起请求。我们不再向终端输出任何数据，因此除了 Cargo 的输出之外，我们看不到任何其他输出。当你在网页浏览器中加载 _127.0.0.1:7878_ 时，你应该会看到空白页面，而不是错误信息。你刚刚手动编写了接收 HTTP 请求并发送响应的代码！

### 返回真实的 HTML

让我们实现返回不仅仅是空白页面的功能。在项目的根目录下创建新的文件 _hello.html_，而不是在 _src_ 目录下。你可以输入任何你想要的 HTML；列表 21-4 展示了一个可能的实现方式。

**清单 21-4:** *hello.html* — 一个用于返回响应的示例 HTML 文件

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>Hello!</title>
  </head>
  <body>
    <h1>Hello!</h1>
    <p>Hi from Rust</p>
  </body>
</html>

```

这是一份简单的 HTML5 文档，包含一个标题和一些文本。当收到请求时，我们需要从服务器返回此文档。为此，我们将像 Listing 21-5 中所示那样修改 `handle_connection`，使其读取 HTML 文件，将其作为正文添加到响应中，然后发送出去。

**清单 21-5:** *src/main.rs* — 将 *hello.html* 的内容作为响应的主体发送

```rust,no_run
use std::{
    fs,
    io::{BufReader, prelude::*},
    net::{TcpListener, TcpStream},
};
// --snip--

fn handle_connection(mut stream: TcpStream) {
    let buf_reader = BufReader::new(&stream);
    let http_request: Vec<_> = buf_reader
        .lines()
        .map(|result| result.unwrap())
        .take_while(|line| !line.is_empty())
        .collect();

    let status_line = "HTTP/1.1 200 OK";
    let contents = fs::read_to_string("hello.html").unwrap();
    let length = contents.len();

    let response =
        format!("{status_line}\r\nContent-Length: {length}\r\n\r\n{contents}");

    stream.write_all(response.as_bytes()).unwrap();
}

```

我们在 `use` 语句中添加了 `fs`，以便将标准库的文件系统模块纳入范围。用于将文件内容读取到字符串中的代码应该很熟悉；我们在 Listing 12-4 中的 I/O 项目中就使用过这段代码来读取文件内容。

接下来，我们使用 `format!` 来将文件的内容作为成功的响应主体。为了确保获得有效的 HTTP 响应，我们添加了 `Content-Length` 头信息，该头信息被设置为我们响应主体的大小——在这种情况下，就是 `hello.html` 的大小。

请使用 `cargo run` 运行以下代码，并在浏览器中设置地址为 _127.0.0.1:7878_，你应该能看到你的 HTML 被渲染的效果！

目前，我们忽略了 `http_request` 中的请求数据，而是无条件地返回 HTML 文件的内容。这意味着，如果您在浏览器中尝试请求 _127.0.0.1:7878/something-else_，您仍然会收到相同的 HTML 响应。目前，我们的服务器功能非常有限，无法实现大多数网络服务器的功能。我们希望根据请求的内容来定制响应，并且只向 /_ 发送格式良好的 HTML 文件。

### 验证请求并选择性响应

目前，我们的网络服务器会返回文件中的HTML内容，无论客户端请求了什么。让我们添加一些功能，以检查浏览器是否真正请求了 _/_，并在返回HTML文件之前进行验证。如果浏览器请求了其他内容，则会产生错误。为此，我们需要修改 `handle_connection` 代码，如清单 21-6 所示。这段新代码会将接收到的请求内容与我们已知的 _/_ 请求格式进行比较，并添加 `if` 和 `else` 代码来处理不同的请求。

**清单 21-6:** *src/main.rs* — 对 */* 的请求与其他请求的处理方式不同

```rust,no_run
// --snip--

fn handle_connection(mut stream: TcpStream) {
    let buf_reader = BufReader::new(&stream);
    let request_line = buf_reader.lines().next().unwrap().unwrap();

    if request_line == "GET / HTTP/1.1" {
        let status_line = "HTTP/1.1 200 OK";
        let contents = fs::read_to_string("hello.html").unwrap();
        let length = contents.len();

        let response = format!(
            "{status_line}\r\nContent-Length: {length}\r\n\r\n{contents}"
        );

        stream.write_all(response.as_bytes()).unwrap();
    } else {
        // some other request
    }
}

```

我们只会关注 HTTP 请求的第一行，因此，我们没有将整个请求读入一个向量，而是调用 `next` 来获取迭代器的第一个元素。第一个 `unwrap` 负责处理 `Option`，如果迭代器没有元素，则会使程序停止运行。第二个 `unwrap` 则处理 `Result`，其效果与 `map` 中的 `unwrap` 相同，而 `map` 被添加到清单 21-2 中。

接下来，我们检查 `request_line` 是否等于对 _/_ 路径的 GET 请求的请求行。如果确实如此，那么 `if` 块就会返回我们 HTML 文件的内容。

如果 `request_line` 不等于对 _/_ 路径的 GET 请求，那就意味着我们收到了其他请求。我们马上会在 `else` 块中添加代码来响应所有其他请求。

现在运行这段代码，并请求 _127.0.0.1:7878_; 你应该会在 _hello.html_ 文件中看到相应的 HTML。如果你尝试其他请求，比如 _127.0.0.1:7878/something-else_，你会收到连接错误，就像在运行 Listing 21-1 和 Listing 21-2 时看到的那样。

现在，让我们在 `else` 块中添加 Listing 21-7 中的代码，以返回状态码为 404 的响应。这个状态码表示请求的内容未被找到。我们还会返回一些 HTML 内容，以便在浏览器中显示给最终用户。

**清单 21-7:** *src/main.rs* — 如果请求的内容不是 */*，则返回状态码 404 并显示错误页面

```rust,no_run
    // --snip--
    } else {
        let status_line = "HTTP/1.1 404 NOT FOUND";
        let contents = fs::read_to_string("404.html").unwrap();
        let length = contents.len();

        let response = format!(
            "{status_line}\r\nContent-Length: {length}\r\n\r\n{contents}"
        );

        stream.write_all(response.as_bytes()).unwrap();
    }

```

在这里，我们的响应包含一个状态行，状态代码为 404，并且还有相应的原因说明。响应体的内容将是文件 _404.html_ 中的 HTML 内容。你需要创建一个与 _hello.html_ 相邻的 _404.html_ 文件来作为错误页面；当然，你可以自由使用任何你想要的 HTML，或者参考 Listing 21-8 中的示例 HTML。

**列表 21-8:** *404.html* — 用于返回 404 响应页面的示例内容

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>Hello!</title>
  </head>
  <body>
    <h1>Oops!</h1>
    <p>Sorry, I don't know what you're asking for.</p>
  </body>
</html>

```

经过这些修改后，再次运行你的服务器。请求 _127.0.0.1:7878_ 应该返回 _hello.html_ 的内容，而任何其他请求，比如 _127.0.0.1:7878/foo_，则应该返回 _404.html_ 中的错误页面。

<!-- Old headings. Do not remove or links may break. -->

<a id="a-touch-of-refactoring"></a>

### 重构

目前，`if`和`else`这两行代码存在很多重复的内容：它们都在读取文件，并将文件内容写入流中。唯一的区别是状态行和文件名。为了让代码更加简洁，我们可以将这些差异提取到单独的`if`和`else`行中，并将状态行和文件名的数值分别赋值给变量；然后我们可以在代码中无条件地使用这些变量来读取文件和写入响应。列表21-9展示了替换了庞大的`if`和`else`代码后的结果代码。

**清单 21-9:** *src/main.rs* — 将 `if` 和 `else` 块重构为仅包含两种情况之间不同的代码

```rust,no_run
// --snip--

fn handle_connection(mut stream: TcpStream) {
    // --snip--

    let (status_line, filename) = if request_line == "GET / HTTP/1.1" {
        ("HTTP/1.1 200 OK", "hello.html")
    } else {
        ("HTTP/1.1 404 NOT FOUND", "404.html")
    };

    let contents = fs::read_to_string(filename).unwrap();
    let length = contents.len();

    let response =
        format!("{status_line}\r\nContent-Length: {length}\r\n\r\n{contents}");

    stream.write_all(response.as_bytes()).unwrap();
}

```

现在， `if` 和 `else` 块仅返回一个元组，该元组包含状态行和文件名的相应值。然后，我们使用解构赋值将这两个值分别分配给 `status_line` 和 `filename`，这一过程是通过 `let` 语句中的模式来实现的，具体方法将在第19章中详细讨论。

之前重复使用的代码现在位于 `if` 和 `else` 块之外，并且使用了 `status_line` 和 `filename` 变量。这样更容易区分这两种情况，同时意味着如果我们想要改变文件读取和响应写入的方式，只需要在一个地方更新代码即可。 Listing 21-9 中的代码行为与 Listing 21-7 中的相同。

太棒了！现在我们用大约40行Rust代码实现了一个简单的网络服务器。该服务器能够响应一个请求，返回相应的内容；而对于所有其他请求，则返回一个404错误响应。

目前，我们的服务器运行在一个线程中，这意味着它一次只能处理一个请求。让我们通过模拟一些缓慢的请求来观察这可能会带来什么问题。然后，我们将进行修复，使我们的服务器能够同时处理多个请求。