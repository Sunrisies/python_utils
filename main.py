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
    torch_dtype=torch.float16,          # 推荐用 torch_dtype 而不是 dtype
)

if len(sys.argv) < 3:
    print("用法: python translate_html.py <输入文件> <输出文件>")
    sys.exit(1)

input_file = sys.argv[1]
output_file = sys.argv[2]

with open(input_file, "r", encoding="utf-8") as f:
    html_content = f.read()

start_time = time.time()                # ① 避免变量覆盖

messages = [
    {
        "role": "system",
        "content": "你是一位专业的HTML本地化专家。请将用户提供的HTML代码中的英文文本翻译为简体中文，并严格遵守以下规则：\n1. 保留所有HTML标签、属性、类名、ID 完全不变。\n2. 不要翻译标签名（如 <div>、<p>、<a>）、属性名（如 class、href）以及属性值中的 URL 或路径。\n3. 只翻译标签之间的文本内容，以及 alt、title、placeholder 等用户可见的属性值。\n4. 保持原有的缩进和换行格式，以便对比。\n5. 跳过 <script> 和 <style> 标签内的所有内容，保持原样。\n6. 跳过 onclick、onload 等事件属性中的代码。\n7. 如果文本中有 HTML 实体（如 &nbsp;），保留原实体。\n8. 直接输出翻译后的完整HTML源码，不要包含任何额外的解释、注释或包装标签。"
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
)

# 确保得到 input_ids 张量
if hasattr(tokenized_chat, 'input_ids'):
    tokenized_chat = tokenized_chat.input_ids
elif isinstance(tokenized_chat, dict) and 'input_ids' in tokenized_chat:
    tokenized_chat = tokenized_chat['input_ids']
tokenized_chat = tokenized_chat.to(model.device)

# 计算输入的 token 数量（可选）
input_token_count = tokenized_chat.shape[1]
print(f"输入 token 数: {input_token_count}")

streamer = TextIteratorStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)

generation_kwargs = dict(
    inputs=tokenized_chat,
    max_new_tokens=4096,
    do_sample=False,                     #  greedy decoding 速度最快
    streamer=streamer,
)

thread = threading.Thread(target=model.generate, kwargs=generation_kwargs)
thread.start()

generated_text = ""
print("开始翻译...")
for new_text in streamer:
    print(new_text, end="", flush=True)
    generated_text += new_text

thread.join()

# 提取 <source> 标签之间的内容（如果模型输出了闭合标签）
if "<source>" in generated_text and "</source>" in generated_text:
    source_start = generated_text.find("<source>") + len("<source>")
    source_end = generated_text.find("</source>")
    generated_text = generated_text[source_start:source_end].strip()

with open(output_file, "w", encoding="utf-8") as f:
    f.write(generated_text)

# ② 正确统计生成 token 数
output_tokens = tokenizer.encode(generated_text, add_special_tokens=False)
num_output_tokens = len(output_tokens)

elapsed = time.time() - start_time
print(f"\n\n翻译完成！结果已保存至: {output_file}")
print(f"生成耗时 {elapsed:.1f} 秒")
print(f"生成 token 数: {num_output_tokens}  |  速度: {num_output_tokens/elapsed:.1f} tokens/秒")