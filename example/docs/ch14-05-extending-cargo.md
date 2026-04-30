## 通过自定义命令扩展Cargo

Cargo的设计使得你可以轻松地添加新的子命令，而无需对其进行修改。如果你在 `$PATH` 中的二进制文件被命名为 `cargo-something`，那么你可以像使用Cargo的子命令一样运行它，只需运行 `cargo something`。这样的自定义命令在运行 `cargo --list` 时也会被列出。能够使用 `cargo install` 来安装扩展功能，然后像使用内置的Cargo工具一样运行这些扩展功能，确实是Cargo设计的一个非常方便的特性！

## 摘要

通过Cargo和[crates.io](https://crates.io/)分享代码，是使Rust生态系统适用于多种任务的原因之一。Rust的标准库规模较小且稳定，但库可以轻松共享、使用，并且可以在与语言本身不同的时间轴上进行改进。在[crates.io](https://crates.io/)上分享对你有用的代码时，不必害羞；这样的代码很可能也会对其他人有用！