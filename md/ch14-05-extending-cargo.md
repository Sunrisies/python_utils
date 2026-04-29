## 通过自定义命令扩展Cargo

Cargo的设计使得你可以轻松地添加新的子命令，而无需对其进行修改。如果你在`$PATH`中的二进制文件被命名为`cargo-something`，那么你可以通过运行`cargo something`来像运行Cargo的子命令一样执行它。这样的自定义命令在运行`cargo --list`时也会被列出。能够使用`cargo install`来安装扩展功能，然后像使用内置的Cargo工具一样来运行它们，这是Cargo设计的一个非常方便的功能！

## 摘要

与Cargo以及[crates.io](https://crates.io/)分享代码，是使Rust生态系统适用于许多不同任务的一部分。Rust的标准库规模较小且稳定，但crates的共享、使用以及改进过程与语言本身相比更为灵活。在[crates.io](https://crates.io/)上分享对你有用的代码是完全可以的；这样的代码很可能会对其他人也很有用！