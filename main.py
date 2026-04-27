import sys
import torch
import threading
from modelscope import AutoModelForCausalLM, AutoTokenizer
from transformers import TextIteratorStreamer
import time

model_name_or_path = "Tencent-Hunyuan/HY-MT1.5-1.8B"

tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
model = AutoModelForCausalLM.from_pretrained(
    model_name_or_path,
    device_map="cuda",
    dtype=torch.float16,
)

# 读取文件
if len(sys.argv) < 3:
    print("用法: python translate_html.py <输入文件> <输出文件>")
    sys.exit(1)

input_file = sys.argv[1]
output_file = sys.argv[2]

with open(input_file, "r", encoding="utf-8") as f:
    html_content = f.read()
start = time.time()
# 构建消息
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
        "content": f"请将以下 HTML 翻译为简体中文：\n<source>\n{html_content}\n</source>"
    }
]

tokenized_chat = tokenizer.apply_chat_template(
    messages,
    tokenize=True,
    add_generation_prompt=False,
    return_tensors="pt"
).to(model.device)

# 使用 TextIteratorStreamer 实现进度显示 + 文本收集
streamer = TextIteratorStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)

# 生成参数
generation_kwargs = dict(
    inputs=tokenized_chat,
    max_new_tokens=4096,
    do_sample=False,
    streamer=streamer,
)

# 启动生成线程
thread = threading.Thread(target=model.generate, kwargs=generation_kwargs)
thread.start()

# 收集生成的文本并实时打印
generated_text = ""
print("开始翻译...")
for new_text in streamer:
    print(new_text, end="", flush=True)          # 实时打印
    generated_text += new_text                    # 累计完整文本

thread.join()

# 提取 <source> 标签之间的内容（若模型输出包含该标签）
if "<source>" in generated_text and "</source>" in generated_text:
    start = generated_text.find("<source>") + len("<source>")
    end = generated_text.find("</source>")
    generated_text = generated_text[start:end].strip()

# 写入文件
with open(output_file, "w", encoding="utf-8") as f:
    f.write(generated_text)

print(f"\n\n翻译完成！结果已保存至: {output_file}")
elapsed = time.time() - start
print(f"生成  耗时 {elapsed:.1f} 秒")
num_tokens = len(generated_text)
print(f"生成 {num_tokens} tokens 耗时 {elapsed:.1f} 秒，速度 {num_tokens/elapsed:.1f} tokens/秒")
