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
MAX_CHUNK_CHARS = 500          # 每个文本块的最大字符数
MAX_NEW_TOKENS = 1024          # 每个块生成的最大 token 数
SYSTEM_PROMPT = (
    "你是一位专业的HTML本地化专家。请将用户提供的英文文本翻译为简体中文，并严格遵守以下规则：\n"
    "1. 只输出翻译结果，不要添加任何额外的解释、注释或标签。\n"
    "2. 保留原文中的所有换行、空格和标点风格。\n"
    "3. **绝对不要翻译任何代码片段、变量名、函数名、路径、URL、命令行指令**。\n"
    "4. 如果看到反引号 ` 包裹的内容、尖括号内的属性值或大段代码块，请原样保留。\n"
    "5. 仅翻译自然语言文本（普通句子、段落、标签说明文字）。"
)

# 需要完全跳过翻译的标签（内部文本原样保留）
SKIP_TAGS = {
    'script', 'style',
    'pre', 'code', 'kbd', 'samp', 'var', 'tt', 'output',
    'dfn', 'plaintext', 'xmp'
}

# ================== 模型加载 ==================
print("正在加载模型（FP16）...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    device_map="cuda",
    torch_dtype=torch.float16,
    trust_remote_code=True,
)
print("模型加载完成\n")

# ================== 文本分块工具 ==================
def split_text_by_length(text: str, max_length: int = MAX_CHUNK_CHARS) -> List[str]:
    """将长文本按字符长度切分，尽量在句子边界处切分"""
    if len(text) <= max_length:
        return [text]

    sentences = text.replace('。', '。\n').replace('！', '！\n').replace('？', '？\n').replace(';', ';\n').split('\n')
    chunks = []
    current = ""

    for sent in sentences:
        if len(current) + len(sent) + 1 <= max_length:
            current += sent
        else:
            if current:
                chunks.append(current.strip())
            if len(sent) > max_length:
                for i in range(0, len(sent), max_length):
                    chunks.append(sent[i:i+max_length].strip())
                current = ""
            else:
                current = sent
    if current:
        chunks.append(current.strip())
    return chunks

# ================== 翻译核心（无实时打印）==================
def translate_single_chunk(text: str) -> str:
    """翻译单个文本块，不打印任何中间内容"""
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
        translated += new_text   # 不打印，只收集结果
    thread.join()
    return translated.strip()

def translate_long_text(text: str) -> str:
    """处理可能超长的文本，自动分块并翻译"""
    chunks = split_text_by_length(text, MAX_CHUNK_CHARS)
    if len(chunks) == 1:
        return translate_single_chunk(chunks[0])
    translated_chunks = [translate_single_chunk(chunk) for chunk in chunks]
    return "".join(translated_chunks)

# ================== HTML 处理（不删除任何标签）==================
def should_skip_translation(element):
    """判断元素（文本节点或标签）是否应该跳过翻译"""
    return element.find_parent(tuple(SKIP_TAGS)) is not None

def translate_html(html_content: str) -> str:
    """解析 HTML，翻译可见文本节点和特定属性，跳过代码块等区域"""
    soup = BeautifulSoup(html_content, 'html.parser')

    # 1. 收集需要翻译的文本节点
    text_nodes = []
    for element in soup.find_all(string=True):
        if isinstance(element, NavigableString) and not isinstance(element, Comment):
            if should_skip_translation(element):
                continue
            if element.strip():
                text_nodes.append(element)

    total = len(text_nodes)
    print(f"发现 {total} 个需要翻译的文本节点（已跳过代码块/脚本/样式）\n")

    # 2. 翻译文本节点（只显示进度，不输出内容）
    for idx, element in enumerate(text_nodes, start=1):
        print(f"--- 文本节点 {idx}/{total} ---")
        original_text = str(element)
        translated = translate_long_text(original_text)
        element.replace_with(translated)

    # 3. 翻译特定属性值（同样跳过禁止区域）
    for attr in ['alt', 'title', 'placeholder']:
        # 收集所有包含该属性的标签，且不在跳过区域内
        tags = [tag for tag in soup.find_all(attrs={attr: True}) if not should_skip_translation(tag)]
        if not tags:
            continue
        print(f"\n--- 翻译属性 '{attr}'，共 {len(tags)} 处 ---")
        for i, tag in enumerate(tags, start=1):
            old_val = tag[attr]
            if old_val and old_val.strip():
                print(f"  [{i}/{len(tags)}] {attr} 属性")
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

    print(f"读取输入文件: {input_file}")
    with open(input_file, "r", encoding="utf-8") as f:
        html_content = f.read()

    start_time = time.time()
    print("开始翻译...\n")
    translated_html = translate_html(html_content)
    elapsed = time.time() - start_time

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(translated_html)

    output_tokens = tokenizer.encode(translated_html, add_special_tokens=False)
    print(f"\n\n翻译完成！结果已保存至: {output_file}")
    print(f"总耗时 {elapsed:.1f} 秒")
    print(f"输出 token 数: {len(output_tokens)}  |  速度: {len(output_tokens)/elapsed:.1f} tokens/秒")