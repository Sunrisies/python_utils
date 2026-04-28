#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
import threading
import argparse
import re
from pathlib import Path
from typing import List, Iterator, Tuple

import torch
import chardet
from modelscope import AutoModelForCausalLM, AutoTokenizer
from transformers import TextIteratorStreamer

# ================== 配置 ==================
MODEL_NAME = "Tencent-Hunyuan/HY-MT1.5-1.8B"
MAX_CHUNK_CHARS = 500          # 每个文本块的最大字符数（Markdown段落通常较短，可稍大）
MAX_NEW_TOKENS = 2048          # 每个块生成的最大 token 数
SYSTEM_PROMPT = (
    "你是一位专业的Markdown本地化专家。请将用户提供的英文文本翻译为简体中文，并严格遵守以下规则：\n"
    "1. 只输出翻译结果，不要添加任何额外的解释、注释或标签。\n"
    "2. 保留原文中的所有换行、空格和标点风格。\n"
    "3. **绝对不要翻译任何代码片段、变量名、函数名、路径、URL、命令行指令**。\n"
    "4. 如果看到反引号 ` 包裹的内容，请原样保留（这些已由预处理保护）。\n"
    "5. 仅翻译自然语言文本（普通句子、段落、标题、列表项）。"
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

# ================== 翻译核心 ==================
def translate_single_chunk(text: str) -> str:
    """翻译单个文本块"""
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
        pad_token_id=tokenizer.eos_token_id,
    )

    thread = threading.Thread(target=model.generate, kwargs=generation_kwargs)
    thread.start()

    translated = ""
    for new_text in streamer:
        translated += new_text
    thread.join()
    return translated.strip()

def translate_long_text(text: str, verbose: bool = False) -> str:
    """处理可能超长的文本，自动分块并翻译"""
    chunks = split_text_by_length(text, MAX_CHUNK_CHARS)
    if len(chunks) == 1:
        return translate_single_chunk(chunks[0])
    translated_chunks = []
    total = len(chunks)
    for idx, chunk in enumerate(chunks, start=1):
        if verbose:
            print(f"    ↳ 块 {idx}/{total} (长度 {len(chunk)})", flush=True)
        translated = translate_single_chunk(chunk)
        translated_chunks.append(translated)
    return "".join(translated_chunks)

# ================== Markdown 保护与翻译 ==================
def protect_code_blocks(markdown: str) -> Tuple[str, List[str]]:
    """
    用占位符替换所有代码块（```...```）和行内代码（`...`），
    返回替换后的文本和原始代码列表。
    """
    placeholders = []
    # 保护代码块 ```...``` (非贪婪匹配，但支持多行)
    def repl_code_block(match):
        code = match.group(0)
        placeholder = f"__CODE_BLOCK_{len(placeholders)}__"
        placeholders.append(code)
        return placeholder

    # 先处理多行代码块
    pattern_block = r'```[\s\S]*?```'
    text = re.sub(pattern_block, repl_code_block, markdown, flags=re.MULTILINE)

    # 保护行内代码 `...` (但不能匹配已经被占位符包裹的)
    def repl_inline(match):
        code = match.group(0)
        placeholder = f"__INLINE_CODE_{len(placeholders)}__"
        placeholders.append(code)
        return placeholder

    # 使用负向前瞻避免匹配占位符
    pattern_inline = r'(?<!_)`(?!_)(.*?)`(?!_)'
    text = re.sub(pattern_inline, repl_inline, text)

    return text, placeholders

def restore_code_blocks(text: str, placeholders: List[str]) -> str:
    """将占位符恢复为原始代码"""
    for i, code in enumerate(placeholders):
        # 根据占位符类型替换
        if code.startswith('```'):
            placeholder = f"__CODE_BLOCK_{i}__"
        else:
            placeholder = f"__INLINE_CODE_{i}__"
        text = text.replace(placeholder, code)
    return text

def translate_markdown(markdown: str, verbose: bool = False) -> str:
    """
    翻译 Markdown 文件：
      1. 保护代码块和行内代码 -> 占位符
      2. 将剩余纯文本分块翻译
      3. 恢复代码块
    """
    # 保护代码
    protected_text, placeholders = protect_code_blocks(markdown)

    # 将保护后的文本按段落分割（简单按空行分块，避免一次性翻译整个文件）
    # 注意：我们仍需要保留 Markdown 语法（标题、列表等），模型会在翻译时保留它们（提示词已要求）
    # 为了更好控制，我们可以将整个 protected_text 作为长文本处理，但为了效率按块分割更佳。
    # 这里采用简单策略：按两个换行符分割段落，对每个段落翻译，然后拼接。
    paragraphs = re.split(r'\n\s*\n', protected_text)
    if verbose:
        print(f"  将文本分为 {len(paragraphs)} 个段落块")

    translated_paragraphs = []
    for idx, para in enumerate(paragraphs, 1):
        if not para.strip():
            translated_paragraphs.append(para)
            continue
        if verbose:
            print(f"  --- 段落 {idx}/{len(paragraphs)} (原长 {len(para)}) ---")
        translated = translate_long_text(para, verbose=verbose)
        if verbose:
            print(f"      翻译后长度: {len(translated)}")
        translated_paragraphs.append(translated)

    translated_text = "\n\n".join(translated_paragraphs)

    # 恢复代码块
    final_text = restore_code_blocks(translated_text, placeholders)
    return final_text

# ================== 编码检测 ==================
def detect_encoding(file_path: Path) -> str:
    with open(file_path, 'rb') as f:
        raw = f.read(10000)
        result = chardet.detect(raw)
        return result['encoding'] or 'utf-8'

# ================== 广度优先收集 Markdown 文件 ==================
def collect_markdown_files(root: Path, extensions: tuple = ('.md', '.markdown')) -> Iterator[Path]:
    """
    广度优先遍历目录：先返回当前目录下的所有 .md 文件，
    然后再递归地处理子目录（每个子目录内部依然先处理当前目录的文件）
    """
    files = []
    for ext in extensions:
        for f in root.glob(f'*{ext}'):
            if f.is_file():
                files.append(f)
    for f in sorted(files):
        yield f

    for subdir in sorted([d for d in root.iterdir() if d.is_dir()]):
        yield from collect_markdown_files(subdir, extensions)

# ================== 目录批量处理 ==================
def translate_directory(input_dir: str, output_dir: str,
                        extensions: tuple = ('.md', '.markdown'),
                        verbose: bool = False, force: bool = False):
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    if not input_path.exists():
        raise FileNotFoundError(f"输入目录不存在: {input_dir}")

    # 收集所有文件（广度优先顺序）
    all_files = list(collect_markdown_files(input_path, extensions))
    total = len(all_files)
    print(f"找到 {total} 个 Markdown 文件待处理（广度优先顺序）\n")

    skipped = 0
    processed = 0
    failed = 0

    for idx, src in enumerate(all_files, start=1):
        rel = src.relative_to(input_path)
        dst = output_path / rel.with_suffix('.md')  # 输出统一 .md 后缀
        dst.parent.mkdir(parents=True, exist_ok=True)

        if not force and dst.exists() and dst.stat().st_size > 0:
            skipped += 1
            print(f"[{idx}/{total}] 跳过已翻译: {rel}")
            continue

        print(f"[{idx}/{total}] 处理: {rel}")
        try:
            enc = detect_encoding(src)
            with open(src, 'r', encoding=enc) as f:
                md = f.read()

            translated = translate_markdown(md, verbose=verbose)

            with open(dst, 'w', encoding='utf-8') as f:
                f.write(translated)
            print(f"  ✅ 完成 -> {dst}")
            processed += 1

            if torch.cuda.is_available():
                torch.cuda.empty_cache()

        except Exception as e:
            print(f"  ❌ 错误: {type(e).__name__}: {e}")
            failed += 1

        print()

    print(f"\n处理完成: 新翻译 {processed} 个, 跳过 {skipped} 个, 失败 {failed} 个")

# ================== 主函数 ==================
def main():
    parser = argparse.ArgumentParser(description="翻译 Markdown 文件（保护代码块，广度优先）")
    parser.add_argument("input", help="输入 Markdown 文件或目录")
    parser.add_argument("output", help="输出 Markdown 文件或目录")
    parser.add_argument("--verbose", "-v", action="store_true", help="显示详细翻译进度")
    parser.add_argument("--force", "-f", action="store_true", help="强制重新翻译所有文件（覆盖已有输出）")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        print(f"错误：输入路径不存在: {input_path}")
        sys.exit(1)

    if input_path.is_file():
        # 单文件模式
        print(f"读取输入文件: {input_path}")
        enc = detect_encoding(input_path)
        with open(input_path, 'r', encoding=enc) as f:
            md = f.read()

        start = time.time()
        print("开始翻译...\n")
        translated = translate_markdown(md, verbose=args.verbose)
        elapsed = time.time() - start

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(translated)

        tokens = tokenizer.encode(translated, add_special_tokens=False)
        print(f"\n翻译完成！结果已保存至: {output_path}")
        print(f"总耗时 {elapsed:.1f} 秒")
        print(f"输出 token 数: {len(tokens)}  |  速度: {len(tokens)/elapsed:.1f} tokens/秒")

    elif input_path.is_dir():
        translate_directory(str(input_path), str(output_path),
                            verbose=args.verbose, force=args.force)
    else:
        print(f"错误：输入路径既不是文件也不是目录: {input_path}")
        sys.exit(1)

if __name__ == "__main__":
    main()