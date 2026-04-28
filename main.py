# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-

# import sys
# import time
# import threading
# import argparse
# import os
# from pathlib import Path
# from typing import List

# import torch
# import chardet
# from modelscope import AutoModelForCausalLM, AutoTokenizer
# from transformers import TextIteratorStreamer
# from bs4 import BeautifulSoup, NavigableString, Comment

# # ================== 配置 ==================
# MODEL_NAME = "Tencent-Hunyuan/HY-MT1.5-1.8B"
# MAX_CHUNK_CHARS = 300          # 每个文本块的最大字符数（调小避免超长）
# MAX_NEW_TOKENS = 4096          # 每个块生成的最大 token 数（足够大）
# SYSTEM_PROMPT = (
#     "你是一位专业的HTML本地化专家。请将用户提供的英文文本翻译为简体中文，并严格遵守以下规则：\n"
#     "1. 只输出翻译结果，不要添加任何额外的解释、注释或标签。\n"
#     "2. 保留原文中的所有换行、空格和标点风格。\n"
#     "3. **绝对不要翻译任何代码片段、变量名、函数名、路径、URL、命令行指令**。\n"
#     "4. 如果看到反引号 ` 包裹的内容、尖括号内的属性值或大段代码块，请原样保留。\n"
#     "5. 仅翻译自然语言文本（普通句子、段落、标签说明文字）。"
# )

# # 需要完全跳过翻译的标签（内部文本原样保留）
# SKIP_TAGS = {
#     'script', 'style',
#     'pre', 'code', 'kbd', 'samp', 'var', 'tt', 'output',
#     'dfn', 'plaintext', 'xmp'
# }

# # ================== 模型加载 ==================
# print("正在加载模型（FP16）...")
# tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
# model = AutoModelForCausalLM.from_pretrained(
#     MODEL_NAME,
#     device_map="cuda",
#     torch_dtype=torch.float16,
#     trust_remote_code=True,
# )
# print("模型加载完成\n")

# # ================== 文本分块工具 ==================
# def split_text_by_length(text: str, max_length: int = MAX_CHUNK_CHARS) -> List[str]:
#     """将长文本按字符长度切分，尽量在句子边界处切分"""
#     if len(text) <= max_length:
#         return [text]

#     sentences = text.replace('。', '。\n').replace('！', '！\n').replace('？', '？\n').replace(';', ';\n').split('\n')
#     chunks = []
#     current = ""

#     for sent in sentences:
#         if len(current) + len(sent) + 1 <= max_length:
#             current += sent
#         else:
#             if current:
#                 chunks.append(current.strip())
#             if len(sent) > max_length:
#                 for i in range(0, len(sent), max_length):
#                     chunks.append(sent[i:i+max_length].strip())
#                 current = ""
#             else:
#                 current = sent
#     if current:
#         chunks.append(current.strip())
#     return chunks

# # ================== 翻译核心 ==================
# def translate_single_chunk(text: str, chunk_idx: int = None, total_chunks: int = None) -> str:
#     """翻译单个文本块"""
#     if not text or not text.strip():
#         return text

#     messages = [
#         {"role": "system", "content": SYSTEM_PROMPT},
#         {"role": "user", "content": f"请翻译以下内容为简体中文：\n{text}"}
#     ]

#     inputs = tokenizer.apply_chat_template(
#         messages,
#         tokenize=True,
#         add_generation_prompt=True,
#         return_tensors="pt"
#     )
#     if hasattr(inputs, 'input_ids'):
#         inputs = inputs.input_ids
#     elif isinstance(inputs, dict) and 'input_ids' in inputs:
#         inputs = inputs['input_ids']
#     inputs = inputs.to(model.device)

#     streamer = TextIteratorStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)
#     generation_kwargs = dict(
#         inputs=inputs,
#         max_new_tokens=MAX_NEW_TOKENS,
#         do_sample=False,
#         streamer=streamer,
#         pad_token_id=tokenizer.eos_token_id,
#     )

#     thread = threading.Thread(target=model.generate, kwargs=generation_kwargs)
#     thread.start()

#     translated = ""
#     for new_text in streamer:
#         translated += new_text
#     thread.join()
    
#     if chunk_idx is not None and total_chunks is not None:
#         # 仅在详细模式下打印块进度（调用者会控制verbose）
#         pass
    
#     return translated.strip()

# def translate_long_text(text: str, verbose: bool = False) -> str:
#     """处理可能超长的文本，自动分块并翻译"""
#     chunks = split_text_by_length(text, MAX_CHUNK_CHARS)
#     if len(chunks) == 1:
#         return translate_single_chunk(chunks[0])
#     translated_chunks = []
#     total = len(chunks)
#     for idx, chunk in enumerate(chunks, start=1):
#         if verbose:
#             print(f"    ↳ 翻译块 {idx}/{total} (长度 {len(chunk)})", flush=True)
#         translated = translate_single_chunk(chunk, chunk_idx=idx, total_chunks=total)
#         translated_chunks.append(translated)
#     return "".join(translated_chunks)

# # ================== HTML 处理 ==================
# def should_skip_translation(element):
#     """判断文本节点或标签是否应该跳过翻译"""
#     return element.find_parent(tuple(SKIP_TAGS)) is not None

# def translate_html(html_content: str, verbose: bool = False) -> str:
#     """解析 HTML，翻译可见文本节点和特定属性，跳过代码块等区域"""
#     soup = BeautifulSoup(html_content, 'html.parser')

#     # 1. 收集需要翻译的文本节点
#     text_nodes = []
#     for element in soup.find_all(string=True):
#         if isinstance(element, NavigableString) and not isinstance(element, Comment):
#             if should_skip_translation(element):
#                 continue
#             if element.strip():
#                 text_nodes.append(element)

#     total = len(text_nodes)
#     if verbose:
#         print(f"  发现 {total} 个需要翻译的文本节点（已跳过代码块/脚本/样式）")

#     # 2. 翻译文本节点
#     for idx, element in enumerate(text_nodes, start=1):
#         original_text = str(element)
#         if verbose:
#             print(f"  --- 文本节点 {idx}/{total} (原长 {len(original_text)}) ---")
#         translated = translate_long_text(original_text, verbose=verbose)
#         if verbose:
#             print(f"      翻译后长度: {len(translated)}")
#         element.replace_with(translated)

#     # 3. 翻译特定属性值（同样跳过禁止区域）
#     for attr in ['alt', 'title', 'placeholder']:
#         tags = [tag for tag in soup.find_all(attrs={attr: True}) if not should_skip_translation(tag)]
#         if not tags:
#             continue
#         if verbose:
#             print(f"\n  --- 翻译属性 '{attr}'，共 {len(tags)} 处 ---")
#         for i, tag in enumerate(tags, start=1):
#             old_val = tag[attr]
#             if old_val and old_val.strip():
#                 if verbose:
#                     print(f"    [{i}/{len(tags)}] {attr} 属性 (原长 {len(old_val)})")
#                 new_val = translate_long_text(old_val, verbose=verbose)
#                 tag[attr] = new_val

#     return str(soup)

# # ================== 编码检测 ==================
# def detect_encoding(file_path: Path) -> str:
#     """检测文件编码"""
#     with open(file_path, 'rb') as f:
#         raw = f.read(10000)  # 读取前10KB进行检测
#         result = chardet.detect(raw)
#         return result['encoding'] or 'utf-8'

# # ================== 目录批量处理 ==================
# def translate_directory(input_dir: str, output_dir: str, 
#                         extensions: tuple = ('.html', '.htm'),
#                         verbose: bool = False, force: bool = False):
#     """递归处理目录下所有 HTML 文件，跳过已翻译的文件（除非 force=True）"""
#     input_path = Path(input_dir)
#     output_path = Path(output_dir)
#     if not input_path.exists():
#         raise FileNotFoundError(f"输入目录不存在: {input_dir}")

#     # 收集所有待处理文件
#     files = []
#     for ext in extensions:
#         files.extend(input_path.rglob(f'*{ext}'))
#     files = sorted(files)
#     total = len(files)
#     print(f"找到 {total} 个 HTML 文件待处理\n")

#     skipped = 0
#     processed = 0
#     failed = 0

#     for idx, src in enumerate(files, start=1):
#         rel = src.relative_to(input_path)
#         dst = output_path / rel
#         dst.parent.mkdir(parents=True, exist_ok=True)

#         # 检查是否跳过
#         skip = False
#         if not force and dst.exists() and dst.stat().st_size > 0:
#             # 可选：校验修改时间 (如需更严格，取消下行注释)
#             # if src.stat().st_mtime <= dst.stat().st_mtime:
#             skip = True
#             skipped += 1
#             print(f"[{idx}/{total}] 跳过已翻译: {rel}")
#             continue

#         print(f"[{idx}/{total}] 处理: {rel}")
#         try:
#             # 检测输入编码
#             enc = detect_encoding(src)
#             with open(src, 'r', encoding=enc) as f:
#                 html = f.read()
            
#             translated = translate_html(html, verbose=verbose)
            
#             with open(dst, 'w', encoding='utf-8') as f:
#                 f.write(translated)
#             print(f"  ✅ 完成 -> {dst}")
#             processed += 1
            
#             # 清理显存缓存
#             if torch.cuda.is_available():
#                 torch.cuda.empty_cache()
                
#         except Exception as e:
#             print(f"  ❌ 错误: {type(e).__name__}: {e}")
#             failed += 1
#             continue
        
#         print()  # 空行分隔

#     print(f"\n处理完成: 新翻译 {processed} 个, 跳过 {skipped} 个, 失败 {failed} 个")

# # ================== 主函数 ==================
# def main():
#     parser = argparse.ArgumentParser(description="翻译 HTML 文件或目录（跳过代码块）")
#     parser.add_argument("input", help="输入 HTML 文件或目录")
#     parser.add_argument("output", help="输出 HTML 文件或目录")
#     parser.add_argument("--verbose", "-v", action="store_true", help="显示详细翻译进度")
#     parser.add_argument("--force", "-f", action="store_true", help="强制重新翻译所有文件（覆盖已有输出）")
#     args = parser.parse_args()

#     input_path = Path(args.input)
#     output_path = Path(args.output)

#     if not input_path.exists():
#         print(f"错误：输入路径不存在: {input_path}")
#         sys.exit(1)

#     if input_path.is_file():
#         # 单文件模式
#         print(f"读取输入文件: {input_path}")
#         # 检测编码
#         enc = detect_encoding(input_path)
#         with open(input_path, 'r', encoding=enc) as f:
#             html_content = f.read()
        
#         start_time = time.time()
#         print("开始翻译...\n")
#         translated_html = translate_html(html_content, verbose=args.verbose)
#         elapsed = time.time() - start_time
        
#         # 确保输出目录存在
#         output_path.parent.mkdir(parents=True, exist_ok=True)
#         with open(output_path, 'w', encoding='utf-8') as f:
#             f.write(translated_html)
        
#         output_tokens = tokenizer.encode(translated_html, add_special_tokens=False)
#         print(f"\n翻译完成！结果已保存至: {output_path}")
#         print(f"总耗时 {elapsed:.1f} 秒")
#         print(f"输出 token 数: {len(output_tokens)}  |  速度: {len(output_tokens)/elapsed:.1f} tokens/秒")
    
#     elif input_path.is_dir():
#         # 目录模式
#         translate_directory(str(input_path), str(output_path), 
#                            verbose=args.verbose, force=args.force)
#     else:
#         print(f"错误：输入路径既不是文件也不是目录: {input_path}")
#         sys.exit(1)

# if __name__ == "__main__":
#     main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
import threading
import argparse
from pathlib import Path
from typing import List, Iterator

import torch
import chardet
from modelscope import AutoModelForCausalLM, AutoTokenizer
from transformers import TextIteratorStreamer
from bs4 import BeautifulSoup, NavigableString, Comment

# ================== 配置 ==================
MODEL_NAME = "Tencent-Hunyuan/HY-MT1.5-1.8B"
MAX_CHUNK_CHARS = 300          # 每个文本块的最大字符数
MAX_NEW_TOKENS = 4096          # 每个块生成的最大 token 数
SYSTEM_PROMPT = (
    "你是一位专业的HTML本地化专家。请将用户提供的英文文本翻译为简体中文，并严格遵守以下规则：\n"
    "1. 只输出翻译结果，不要添加任何额外的解释、注释或标签。\n"
    "2. 保留原文中的所有换行、空格和标点风格。\n"
    "3. **绝对不要翻译任何代码片段、变量名、函数名、路径、URL、命令行指令**。\n"
    "4. 如果看到反引号 ` 包裹的内容，请原样保留。\n"
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

# ================== HTML 处理 ==================
def should_skip_translation(element):
    """判断是否应该跳过翻译"""
    return element.find_parent(tuple(SKIP_TAGS)) is not None

def translate_html(html_content: str, verbose: bool = False) -> str:
    """翻译 HTML，保留所有标签"""
    soup = BeautifulSoup(html_content, 'html.parser')

    # 收集需要翻译的文本节点
    text_nodes = []
    for element in soup.find_all(string=True):
        if isinstance(element, NavigableString) and not isinstance(element, Comment):
            if should_skip_translation(element):
                continue
            if element.strip():
                text_nodes.append(element)

    total = len(text_nodes)
    if verbose:
        print(f"  发现 {total} 个需要翻译的文本节点")

    # 翻译文本节点
    for idx, element in enumerate(text_nodes, start=1):
        original = str(element)
        if verbose:
            print(f"  --- 文本节点 {idx}/{total} (原长 {len(original)}) ---")
        translated = translate_long_text(original, verbose=verbose)
        if verbose:
            print(f"      翻译后长度: {len(translated)}")
        element.replace_with(translated)

    # 翻译属性
    for attr in ['alt', 'title', 'placeholder']:
        tags = [tag for tag in soup.find_all(attrs={attr: True}) if not should_skip_translation(tag)]
        if not tags:
            continue
        if verbose:
            print(f"\n  --- 翻译属性 '{attr}'，共 {len(tags)} 处 ---")
        for i, tag in enumerate(tags, start=1):
            old = tag[attr]
            if old and old.strip():
                if verbose:
                    print(f"    [{i}/{len(tags)}] {attr} (原长 {len(old)})")
                new = translate_long_text(old, verbose=verbose)
                tag[attr] = new

    return str(soup)

# ================== 编码检测 ==================
def detect_encoding(file_path: Path) -> str:
    with open(file_path, 'rb') as f:
        raw = f.read(10000)
        result = chardet.detect(raw)
        return result['encoding'] or 'utf-8'

# ================== 广度优先收集 HTML 文件 ==================
def collect_html_files(root: Path, extensions: tuple) -> Iterator[Path]:
    """
    广度优先遍历目录：先返回当前目录下的所有 HTML 文件，
    然后再递归地处理子目录（每个子目录内部依然先处理当前目录的文件）
    """
    # 1. 当前目录下的文件
    files = []
    for ext in extensions:
        for f in root.glob(f'*{ext}'):
            if f.is_file():
                files.append(f)
    for f in sorted(files):
        yield f

    # 2. 再递归处理子目录（按名称排序，保证顺序可预测）
    for subdir in sorted([d for d in root.iterdir() if d.is_dir()]):
        yield from collect_html_files(subdir, extensions)

# ================== 目录批量处理 ==================
def translate_directory(input_dir: str, output_dir: str,
                        extensions: tuple = ('.html', '.htm'),
                        verbose: bool = False, force: bool = False):
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    if not input_path.exists():
        raise FileNotFoundError(f"输入目录不存在: {input_dir}")

    # 收集所有文件（广度优先顺序）
    all_files = list(collect_html_files(input_path, extensions))
    total = len(all_files)
    print(f"找到 {total} 个 HTML 文件待处理（广度优先顺序）\n")

    skipped = 0
    processed = 0
    failed = 0

    for idx, src in enumerate(all_files, start=1):
        rel = src.relative_to(input_path)
        dst = output_path / rel
        dst.parent.mkdir(parents=True, exist_ok=True)

        # 跳过已翻译（除非 force）
        if not force and dst.exists() and dst.stat().st_size > 0:
            skipped += 1
            print(f"[{idx}/{total}] 跳过已翻译: {rel}")
            continue

        print(f"[{idx}/{total}] 处理: {rel}")
        try:
            enc = detect_encoding(src)
            with open(src, 'r', encoding=enc) as f:
                html = f.read()

            translated = translate_html(html, verbose=verbose)

            with open(dst, 'w', encoding='utf-8') as f:
                f.write(translated)
            print(f"  ✅ 完成 -> {dst}")
            processed += 1

            # 清理显存
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

        except Exception as e:
            print(f"  ❌ 错误: {type(e).__name__}: {e}")
            failed += 1

        print()  # 空行

    print(f"\n处理完成: 新翻译 {processed} 个, 跳过 {skipped} 个, 失败 {failed} 个")

# ================== 主函数 ==================
def main():
    parser = argparse.ArgumentParser(description="翻译 HTML 文件或目录（跳过代码块，广度优先）")
    parser.add_argument("input", help="输入 HTML 文件或目录")
    parser.add_argument("output", help="输出 HTML 文件或目录")
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
            html = f.read()

        start = time.time()
        print("开始翻译...\n")
        translated = translate_html(html, verbose=args.verbose)
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