from modelscope import AutoModelForCausalLM, AutoTokenizer
from transformers import TextStreamer
import torch

model_name_or_path = "Tencent-Hunyuan/HY-MT1.5-1.8B"

tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
model = AutoModelForCausalLM.from_pretrained(
    model_name_or_path, 
    device_map="cuda",
    torch_dtype=torch.float16  # 添加半精度加速
)
txt = '''
<p>Welcome to an overview of the documentation provided by the <a href="https://www.rust-lang.org">Rust
project</a>. This page contains links to various helpful references,
most of which are available offline (if opened with <code>rustup doc</code>). Many of these
resources take the form of “books”; we collectively call these “The Rust
Bookshelf.” Some are large, some are small.</p>
<p>All of these books are managed by the Rust Organization, but other unofficial
documentation resources are included here as well!</p>
<p>If you’re just looking for the standard library reference, here it is:
<a href="std/index.html">Rust API documentation</a></p>
<h2 id="learning-rust"><a class="doc-anchor" href="#learning-rust">§</a>Learning Rust</h2>
<p>If you’d like to learn Rust, this is the section for you! All of these resources
assume that you have programmed before, but not in any specific language:</p>
<h3 id="the-rust-programming-language"><a class="doc-anchor" href="#the-rust-programming-language">§</a>The Rust Programming Language</h3>
<p>Affectionately nicknamed “the book,” <a href="book/index.html">The Rust Programming Language</a>
will give you an overview of the language from first principles. You’ll build a
few projects along the way, and by the end, you’ll have a solid grasp of how to
use the language.</p>
<h3 id="rust-by-example"><a class="doc-anchor" href="#rust-by-example">§</a>Rust By Example</h3>
<p>If reading multiple hundreds of pages about a language isn’t your style, then
<a href="rust-by-example/index.html">Rust By Example</a> has you covered. RBE shows off a
bunch of code without using a lot of words. It also includes exercises!</p>
<h3 id="rustlings"><a class="doc-anchor" href="#rustlings">§</a>Rustlings</h3>
<p><a href="https://github.com/rust-lang/rustlings">Rustlings</a> guides you
through downloading and setting up the Rust toolchain, then provides an
interactive tool that teaches you how to solve coding challenges in Rust.</p>
<h3 id="rust-playground"><a class="doc-anchor" href="#rust-playground">§</a>Rust Playground</h3>
<p>The <a href="https://play.rust-lang.org">Rust Playground</a> is a great place
to try out and share small bits of code, or experiment with some of the most
popular crates.</p>
<h2 id="using-rust"><a class="doc-anchor" href="#using-rust">§</a>Using Rust</h2>
<p>Once you’ve gotten familiar with the language, these resources can help you put
it to work.</p>
<h3 id="the-standard-library"><a class="doc-anchor" href="#the-standard-library">§</a>The Standard Library</h3>
<p>Rust’s standard library has <a href="std/index.html">extensive API documentation</a>, with
explanations of how to use various things, as well as example code for
accomplishing various tasks. Code examples have a “Run” button on hover that
opens the sample in the playground.</p>
'''

# messages = [
#     {"role": "user", "content": rf"将以下<source></source>之间的文本翻译为中文，注意只需要输出翻译后的结果，不要额外解释。原文中的HTML标签需要在译文中相应的位置尽量保留。输出格式为：<target>翻译内容</target>。\n\n<source>{txt}</source>"}
# ]

messages = [
    {
        "role": "system",
        "content": (
            "你是一位专业的HTML本地化专家。请将用户提供的HTML代码中的英文文本翻译为简体中文，"
            "并严格遵守以下规则：\n"
            "1. 保留所有HTML标签、属性、类名、ID 完全不变。\n"
            "2. 不要翻译标签名（如 <div>、<p>、<a>）、属性名（如 class、href）以及属性值中的 URL 或路径。\n"
            "3. 只翻译标签之间的文本内容，以及 alt、title、placeholder 等用户可见的属性值。\n"
            "4. 保持原有的缩进和换行格式，以便对比。\n"
            "5. 跳过 <script> 和 <style> 标签内的所有内容，保持原样。\n"
            "6. 跳过 onclick、onload 等事件属性中的代码。\n"
            "7. 如果文本中有 HTML 实体（如 &nbsp;），保留原实体。\n"
            "8. 直接输出翻译后的完整HTML源码，不要包含任何额外的解释、注释或包装标签。"
        )
    },
    {
        "role": "user",
        "content": f"请将以下 HTML 翻译为简体中文：\n<source>\n{txt}\n</source>"
    }
]
tokenized_chat = tokenizer.apply_chat_template(
    messages,
    tokenize=True,
    add_generation_prompt=False,
    return_tensors="pt"
)

# 创建 streamer 对象
streamer = TextStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)

print("译文: ", end="", flush=True)  # 打印提示符，不换行

# 生成时使用 streamer
outputs = model.generate(
    tokenized_chat.to(model.device),
    max_new_tokens=2048,
    streamer=streamer,  # 添加 streamer
    do_sample=False,    # 贪心搜索，更稳定
)
print("\n\n完整输出: ", end="", flush=True)  # 打印提示符，不换行
print(tokenizer.decode(outputs[0], skip_special_tokens=True))  # 输出完整翻译结果
print("\n生成完成！")