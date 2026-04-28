# import sys
# import torch
# import threading
# from modelscope import AutoModelForCausalLM, AutoTokenizer
# from transformers import TextIteratorStreamer
# import time

# model_name_or_path = "Tencent-Hunyuan/HY-MT1.5-1.8B"

# tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
# model = AutoModelForCausalLM.from_pretrained(
#     model_name_or_path,
#     device_map="cuda",
#     torch_dtype=torch.float16,          # 推荐用 torch_dtype 而不是 dtype
# )

# if len(sys.argv) < 3:
#     print("用法: python translate_html.py <输入文件> <输出文件>")
#     sys.exit(1)

# input_file = sys.argv[1]
# output_file = sys.argv[2]

# with open(input_file, "r", encoding="utf-8") as f:
#     html_content = f.read()

# start_time = time.time()                # ① 避免变量覆盖

# messages = [
#     {
#         "role": "system",
#         "content": "你是一位专业的HTML本地化专家。请将用户提供的HTML代码中的英文文本翻译为简体中文，并严格遵守以下规则：\n1. 保留所有HTML标签、属性、类名、ID 完全不变。\n2. 不要翻译标签名（如 <div>、<p>、<a>）、属性名（如 class、href）以及属性值中的 URL 或路径。\n3. 只翻译标签之间的文本内容，以及 alt、title、placeholder 等用户可见的属性值。\n4. 保持原有的缩进和换行格式，以便对比。\n5. 跳过 <script> 和 <style> 标签内的所有内容，保持原样。\n6. 跳过 onclick、onload 等事件属性中的代码。\n7. 如果文本中有 HTML 实体（如 &nbsp;），保留原实体。\n8. 直接输出翻译后的完整HTML源码，不要包含任何额外的解释、注释或包装标签。"
#     },
#     {
#         "role": "user",
#         "content": f"请将以下 HTML 翻译为简体中文：\n<source>\n{html_content}\n</source>"
#     }
# ]

# tokenized_chat = tokenizer.apply_chat_template(
#     messages,
#     tokenize=True,
#     add_generation_prompt=False,
#     return_tensors="pt"
# )

# # 确保得到 input_ids 张量
# if hasattr(tokenized_chat, 'input_ids'):
#     tokenized_chat = tokenized_chat.input_ids
# elif isinstance(tokenized_chat, dict) and 'input_ids' in tokenized_chat:
#     tokenized_chat = tokenized_chat['input_ids']
# tokenized_chat = tokenized_chat.to(model.device)

# # 计算输入的 token 数量（可选）
# input_token_count = tokenized_chat.shape[1]
# print(f"输入 token 数: {input_token_count}")

# streamer = TextIteratorStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)

# generation_kwargs = dict(
#     inputs=tokenized_chat,
#     max_new_tokens=4096,
#     do_sample=False,                     #  greedy decoding 速度最快
#     streamer=streamer,
# )

# thread = threading.Thread(target=model.generate, kwargs=generation_kwargs)
# thread.start()

# generated_text = ""
# print("开始翻译...")
# for new_text in streamer:
#     print(new_text, end="", flush=True)
#     generated_text += new_text

# thread.join()

# # 提取 <source> 标签之间的内容（如果模型输出了闭合标签）
# if "<source>" in generated_text and "</source>" in generated_text:
#     source_start = generated_text.find("<source>") + len("<source>")
#     source_end = generated_text.find("</source>")
#     generated_text = generated_text[source_start:source_end].strip()

# with open(output_file, "w", encoding="utf-8") as f:
#     f.write(generated_text)

# # ② 正确统计生成 token 数
# output_tokens = tokenizer.encode(generated_text, add_special_tokens=False)
# num_output_tokens = len(output_tokens)

# elapsed = time.time() - start_time
# print(f"\n\n翻译完成！结果已保存至: {output_file}")
# print(f"生成耗时 {elapsed:.1f} 秒")
# print(f"生成 token 数: {num_output_tokens}  |  速度: {num_output_tokens/elapsed:.1f} tokens/秒")


import sys
import time
import threading
from typing import List

import torch
from modelscope import AutoModelForCausalLM, AutoTokenizer
from transformers import TextIteratorStreamer
from bs4 import BeautifulSoup, NavigableString, Comment

# ================== 配置 ==================
MODEL_NAME = "Tencent-Hunyuan/HY-MT1.5-1.8B"
MAX_CHUNK_CHARS = 500          # 每个文本块的最大字符数（避免过长）
MAX_NEW_TOKENS = 1024          # 每个块生成的最大 token 数（原 4096 太大）
SYSTEM_PROMPT = (
    "你是一位专业的HTML本地化专家。请将用户提供的英文文本翻译为简体中文，并严格遵守以下规则：\n"
    "1. 只输出翻译结果，不要添加任何额外的解释、注释或标签。\n"
    "2. 保持原文的换行和标点符号风格。"
)

# ================== 模型加载 ==================
print("正在加载模型（FP16）...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    device_map="cuda",
    torch_dtype=torch.float16,
    trust_remote_code=True,
)
print("模型加载完成")

# ================== 文本分块工具 ==================
def split_text_by_length(text: str, max_length: int = MAX_CHUNK_CHARS) -> List[str]:
    """将长文本按字符长度切分，尽量在句子边界处切分"""
    if len(text) <= max_length:
        return [text]

    # 按常见句子分隔符预切分
    sentences = text.replace('。', '。\n').replace('！', '！\n').replace('？', '？\n').replace(';', ';\n').split('\n')
    chunks = []
    current = ""

    for sent in sentences:
        if len(current) + len(sent) + 1 <= max_length:
            current += sent
        else:
            if current:
                chunks.append(current.strip())
            # 如果单个句子超长，强制按字符切分
            if len(sent) > max_length:
                for i in range(0, len(sent), max_length):
                    chunks.append(sent[i:i+max_length].strip())
                current = ""
            else:
                current = sent

    if current:
        chunks.append(current.strip())
    return chunks

# ================== 翻译核心（保留原流式风格）==================
def translate_single_chunk(text: str) -> str:
    """翻译单个文本块（同步调用，内部使用流式输出）"""
    if not text or not text.strip():
        return text

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"请翻译以下内容为简体中文：\n{text}"}
    ]

    inputs = tokenizer.apply_chat_template(
        messages,
        tokenize=True,
        add_generation_prompt=True,
        return_tensors="pt"
    )
    # 兼容不同的返回格式
    if hasattr(inputs, 'input_ids'):
        inputs = inputs.input_ids
    elif isinstance(inputs, dict) and 'input_ids' in inputs:
        inputs = inputs['input_ids']
    inputs = inputs.to(model.device)

    streamer = TextIteratorStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)

    generation_kwargs = dict(
        inputs=inputs,
        max_new_tokens=MAX_NEW_TOKENS,
        do_sample=False,
        streamer=streamer,
    )

    thread = threading.Thread(target=model.generate, kwargs=generation_kwargs)
    thread.start()

    translated = ""
    for new_text in streamer:
        print(new_text, end="", flush=True)   # 实时显示每个块的翻译结果
        translated += new_text

    thread.join()
    return translated.strip()

def translate_long_text(text: str) -> str:
    """处理可能超长的文本（自动分块、翻译、拼接）"""
    chunks = split_text_by_length(text, MAX_CHUNK_CHARS)
    if len(chunks) == 1:
        return translate_single_chunk(chunks[0])
    translated_chunks = []
    for idx, chunk in enumerate(chunks):
        print(f"\n--- 翻译块 {idx+1}/{len(chunks)} ---")
        translated_chunks.append(translate_single_chunk(chunk))
    return "".join(translated_chunks)

# ================== HTML 处理 ==================
def translate_html(html_content: str) -> str:
    """解析 HTML，仅翻译可见文本节点和特定属性，保留标签结构"""
    soup = BeautifulSoup(html_content, 'html.parser')

    # 1. 跳过 script/style 标签内的内容（直接移除，不翻译）
    for tag in soup(['script', 'style']):
        tag.decompose()

    # 2. 翻译文本节点
    for element in soup.find_all(string=True):
        if isinstance(element, NavigableString) and not isinstance(element, Comment):
            parent = element.parent
            # 可在此处添加额外过滤（例如跳过某些特定父标签，本例简单处理）
            if parent and parent.name in ['script', 'style']:
                continue
            original_text = str(element)
            if original_text.strip():
                translated = translate_long_text(original_text)
                element.replace_with(translated)

    # 3. 翻译特定属性值（alt, title, placeholder）
    for attr in ['alt', 'title', 'placeholder']:
        for tag in soup.find_all(attrs={attr: True}):
            old_val = tag[attr]
            if old_val and old_val.strip():
                new_val = translate_long_text(old_val)
                tag[attr] = new_val

    return str(soup)

# ================== 主函数 ==================
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python translate_html.py <输入文件> <输出文件>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    with open(input_file, "r", encoding="utf-8") as f:
        html_content = f.read()

    start_time = time.time()
    print("开始翻译...")
    translated_html = translate_html(html_content)
    elapsed = time.time() - start_time

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(translated_html)

    output_tokens = tokenizer.encode(translated_html, add_special_tokens=False)
    print(f"\n\n翻译完成！结果已保存至: {output_file}")
    print(f"总耗时 {elapsed:.1f} 秒")
    print(f"输出 token 数: {len(output_tokens)}  |  速度: {len(output_tokens)/elapsed:.1f} tokens/秒")