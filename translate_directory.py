#!/usr/bin/env python3
"""
Rust 官方英文文档 Markdown 翻译脚本 —— 多文件并发版（llama-server CUDA）

特性：
- 将 <Listing> 自定义标签转为 Markdown 标准格式
- 保护行内代码 → HTML 标签，避免截断
- 隔离表格内部占位符编号
- 强化 prompt + 后处理防止引用符号 > 丢失
- 未翻译内容自动检测与重试
- 调试 JSON 记录完整翻译前/原始/后内容
- 支持目录递归翻译
- **多文件并发处理**：每个文件内部串行，文件间并行
"""

import argparse
import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from threading import Lock
from typing import Iterator, Dict, List, Optional

import requests

try:
    from tqdm import tqdm as _tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False
    _tqdm = None

try:
    import chardet
except ImportError:
    chardet = None

# ================== 日志工具 ==================
class Tee:
    def __init__(self, *files):
        self.files = files

    def write(self, obj):
        for f in self.files:
            f.write(obj)
            f.flush()

    def flush(self):
        for f in self.files:
            f.flush()

def tqdm(iterable=None, *args, **kwargs):
    if not HAS_TQDM:
        return iterable
    kwargs.setdefault('file', sys.stdout)
    return _tqdm(iterable, *args, **kwargs)

def safe_print(message: str):
    if HAS_TQDM:
        _tqdm.write(message, file=sys.stdout, end='\n')
    else:
        print(message, flush=True)

# ================== 配置 ==================
SERVER_URL = "http://localhost:12323/v1/chat/completions"
MAX_CHUNK_CHARS = 2500
MAX_NEW_TOKENS = 1024
TABLE_MAX_TOKENS = 4096
REQUEST_TIMEOUT = 300
MAX_RETRIES = 2
DEFAULT_WORKERS = 4                     # 并发文件数

SYSTEM_PROMPT = (
    "你是一位专业的 Markdown 本地化专家，专注于 Rust 语言文档的翻译。请将用户提供的英文文本翻译为简体中文，并严格遵守以下规则：\n"
    "1. 只输出翻译结果，不要添加任何额外的解释、注释或标签。\n"
    "2. 保留原文中的所有换行、空格、标点风格和缩进结构。\n"
    "3. **绝对不要翻译**：代码片段、变量名、函数名、路径、URL、命令行指令、文件扩展名。\n"
    "4. 对于 Rust 技术名词，遵循以下约定：\n"
    "   - 保留不译的：`crate`、`trait`、`match`（关键字）、`impl`、`unsafe`、`macro`；\n"
    "   - 统一翻译的：`ownership` → 所有权，`lifetime` → 生命周期，`borrow checker` → 借用检查器，`closure` → 闭包，`iterator` → 迭代器，`pattern matching` → 模式匹配，`smart pointer` → 智能指针；\n"
    "   - 表格中的英文说明文字（如 'Left-shift'、'Bitwise OR'）属于自然语言，应翻译为中文。\n"
    "5. 所有用 «» 包围的占位符（如 `«0»`、`«42»`、`«h3»`）是系统保护标记，**必须原样保留**，不要修改、翻译或在其中添加空格或换行。\n"
    "   同样，任何 `⊂PH数字⊃` 格式的标记也是保护标记，禁止改动。\n"
    "6. 对于 Markdown 链接 `[text](url)` 和图片 `![alt](url)`，只翻译方括号内的显示文本，保留 URL 和全部分隔符。\n"
    "7. 保持原有的 Markdown 块引用符号（每行开头的 `> ` 必须完整保留，不要删除或修改）。列表符号（-、*、1. 等）也必须原样保留。\n"
    "8. 如果遇到无法确定或无法准确翻译的术语，直接保留原文。\n"
    "9. **所有英文句子或段落都必须翻译成中文**，即使包含技术词汇也不能保留英文原文。\n"
    "10. 仅翻译自然语言文本（普通句子、段落、标题、列表项），技术名词按上述规则处理。"
)

# ================== 调试数据收集（线程安全） ==================
DEBUG_SAMPLES: List[Dict] = []
DEBUG_ENABLED = False
DEBUG_LOCK = Lock()

# ================== 转换 <Listing> 为 Markdown ==================
def convert_listing_to_markdown(text: str) -> str:
    """
    将 <Listing number="..." file-name="..." caption="..."> ... </Listing>
    转换为标准 Markdown 格式。
    """
    listing_re = re.compile(
        r'<Listing\s+number="(?P<num>[^"]*)"\s+file-name="(?P<file>[^"]*)"\s+caption="(?P<cap>[^"]*)"\s*>\s*'
        r'(?P<body>[\s\S]*?)'
        r'</Listing>',
        re.IGNORECASE
    )

    def replacer(m):
        num = m.group('num')
        fname = m.group('file')
        cap = m.group('cap')
        body = m.group('body').strip('\n')
        header = f"**Listing {num}:** *{fname}* — {cap}"
        return header + '\n\n' + body

    return listing_re.sub(replacer, text)

# ================== 翻译核心 ==================
def translate_text(text: str, verbose: bool = False,
                   max_tokens: int = MAX_NEW_TOKENS,
                   file_label: str = "",
                   para_idx: int = -1,
                   chunk_idx: int = -1,
                   temperature: float = 0.0) -> str:
    if not text or not text.strip():
        return text

    # 保护占位符为临时标记
    ph_pattern = re.compile(r'«(h?\d+)»')
    temp_map: Dict[str, str] = {}
    counter = [0]
    def _protect(m):
        key = f"⊂PH{counter[0]}⊃"
        temp_map[key] = m.group(0)
        counter[0] += 1
        return key
    protected_text = ph_pattern.sub(_protect, text)

    payload = {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"请翻译以下内容为简体中文：\n{protected_text}"}
        ],
        "max_tokens": max_tokens,
        "temperature": temperature
    }

    try:
        resp = requests.post(SERVER_URL, json=payload, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        raw_content = data["choices"][0]["message"]["content"].strip()
        if verbose:
            usage = data.get("usage", {})
            safe_print(f"    输入 tokens: {usage.get('prompt_tokens', '?')}, "
                       f"输出 tokens: {usage.get('completion_tokens', '?')}")
    except Exception as e:
        if DEBUG_ENABLED:
            with DEBUG_LOCK:
                DEBUG_SAMPLES.append({
                    "file": file_label,
                    "paragraph_index": para_idx,
                    "chunk_index": chunk_idx,
                    "protected_text": protected_text,
                    "translated_raw": None,
                    "translated_final": text,
                    "original_text_preview": text[:200],
                    "error": str(e)
                })
        safe_print(f"  [翻译失败] {e}，保留原文")
        return text

    # 恢复临时标记（模糊匹配）
    content = raw_content
    for key, orig_ph in temp_map.items():
        if key in content:
            content = content.replace(key, orig_ph)
        else:
            n = re.search(r'\d+', key).group()
            variants = [
                f'⊂PH{n}⊃', f'⊂PH{n}', f'PH{n}⊃', f'⊂PH{n} ',
                f'⊂PH{n}⊂', f'⊂PH{n}⊃',
            ]
            found = False
            for var in variants:
                if var in content:
                    content = content.replace(var, orig_ph)
                    found = True
                    break
            if not found:
                safe_print(f"    ⚠ 临时标记 {key} 丢失，使用正则强制恢复")
                content = re.sub(r'⊂\s*PH\s*' + n + r'[^⊂⊂⊃]*⊃?', orig_ph, content)

    content = re.sub(r'⊂\s*PH\s*\d+\s*⊃?', '', content)

    # 修复丢失的引用符号 >
    if text.lstrip().startswith('>') and not content.lstrip().startswith('>'):
        leading = text[:text.find('>')]
        content = leading + '>' + content.lstrip()

    final_content = content

    # 记录调试信息
    if DEBUG_ENABLED:
        with DEBUG_LOCK:
            DEBUG_SAMPLES.append({
                "file": file_label,
                "paragraph_index": para_idx,
                "chunk_index": chunk_idx,
                "protected_text": protected_text,
                "translated_raw": raw_content,
                "translated_final": final_content,
                "original_text_preview": text[:200]
            })

    return final_content

# ================== 占位符工具 ==================
def normalize_ph(text: str) -> str:
    text = re.sub(r'«\s*h\s*(\d+)\s*»', r'«h\1»', text)
    text = re.sub(r'«\s*(\d+)\s*»', r'«\1»', text)
    return text

def restore_ph(text: str, ph_map: Dict[str, str]) -> str:
    text = normalize_ph(text)
    def _num(ph):
        m = re.search(r'«h?(\d+)»', ph)
        return int(m.group(1)) if m else 0
    sorted_items = sorted(ph_map.items(), key=lambda kv: _num(kv[0]), reverse=True)
    for ph, orig in sorted_items:
        if ph in text:
            text = text.replace(ph, orig)
        else:
            m = re.search(r'«(h?)(\d+)»', ph)
            if not m:
                continue
            prefix, n = m.group(1), m.group(2)
            cand = [f'[{prefix}{n}]', f'<{prefix}{n}>', f'« {prefix}{n}»', f'«{prefix}{n} »',
                    f'「{prefix}{n}」', f'｢{prefix}{n}｣', f'『{prefix}{n}』']
            for alt in cand:
                if alt in text and alt != ph:
                    if alt.startswith('[') and re.search(re.escape(alt) + r'\(', text):
                        continue
                    text = text.replace(alt, orig, 1)
                    break
    return text

# ================== 表格行判断 ==================
def _is_table_line(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith('|') and stripped.count('|') >= 2

def _is_table_separator(line: str) -> bool:
    stripped = line.strip()
    return bool(re.match(r'^(\|[\s\-:]+)+\|$', stripped))

# ================== 分块（表格感知） ==================
def split_text_preserve_placeholders(text: str, max_length: int) -> List[str]:
    ph_pattern = re.compile(r'«h?\d+»')
    phs_found = ph_pattern.findall(text)
    temp_map = {}
    tmp_counter = [0]
    def _to_temp(m):
        ph = m.group(0)
        if ph not in temp_map:
            temp_map[ph] = f"⟨PH{tmp_counter[0]}⟩"
            tmp_counter[0] += 1
        return temp_map[ph]
    text = ph_pattern.sub(_to_temp, text)

    if len(text) <= max_length:
        chunks = [text]
    else:
        paragraphs = re.split(r'(\n\s*\n)', text)
        chunks, current = [], ""
        i = 0
        while i < len(paragraphs):
            seg = paragraphs[i]
            if seg.strip() and _is_table_line(seg.split('\n')[0]):
                table_parts = [seg]
                j = i + 1
                while j < len(paragraphs):
                    nxt = paragraphs[j]
                    if nxt.strip() and _is_table_line(nxt.split('\n')[0]):
                        table_parts.append(nxt)
                        j += 1
                    elif nxt.strip() == '':
                        if j + 1 < len(paragraphs) and _is_table_line(paragraphs[j + 1].split('\n')[0]):
                            table_parts.append(nxt)
                            j += 1
                        else:
                            break
                    else:
                        break
                full_table = '\n'.join(table_parts)
                if current.strip():
                    chunks.append(current.strip())
                    current = ""
                if len(full_table) <= max_length:
                    chunks.append(full_table.strip())
                else:
                    tl = full_table.split('\n')
                    hdr, data, found = [], [], False
                    for row in tl:
                        if _is_table_separator(row.strip()):
                            hdr.append(row)
                            found = True
                        elif not found:
                            hdr.append(row)
                        else:
                            data.append(row)
                    hdr_block = '\n'.join(hdr)
                    sub = hdr_block
                    for d in data:
                        if len(sub) + len(d) + 1 > max_length:
                            if sub.strip():
                                chunks.append(sub.strip())
                            sub = d
                        else:
                            sub += '\n' + d
                    if sub.strip():
                        chunks.append(sub.strip())
                i = j
                continue
            if len(current) + len(seg) <= max_length:
                current += seg
            else:
                if current.strip():
                    chunks.append(current.strip())
                sents = re.split(r'(?<=[。！？;.!\n])', seg)
                current = ""
                for s in sents:
                    if len(current) + len(s) <= max_length:
                        current += s
                    else:
                        if current.strip():
                            chunks.append(current.strip())
                        if len(s) > max_length:
                            for k in range(0, len(s), max_length):
                                chunks.append(s[k:k + max_length].strip())
                            current = ""
                        else:
                            current = s
            i += 1
        if current.strip():
            chunks.append(current.strip())

    final = []
    for chunk in chunks:
        for orig_ph, tmp_ph in temp_map.items():
            chunk = chunk.replace(tmp_ph, orig_ph)
        final.append(chunk)
    return final

def _is_pure_placeholder(text: str) -> bool:
    cleaned = re.sub(r'«h?\d+»|⊂PH\d+⊃|\s', '', text)
    return cleaned == ""

# ================== 长文本翻译（含重试） ==================
def translate_long_text(text: str, verbose: bool = False,
                        file_label: str = "", para_idx: int = -1) -> str:
    chunks = split_text_preserve_placeholders(text, MAX_CHUNK_CHARS)
    if not chunks:
        return ""
    if len(chunks) == 1:
        return _translate_single_with_retry(chunks[0], verbose, file_label, para_idx, 0)

    translated = []
    for i, chunk in enumerate(chunks):
        if _is_pure_placeholder(chunk):
            translated.append(chunk)
            if verbose:
                safe_print(f"      [分块 {i+1}/{len(chunks)}] 纯占位符，已跳过翻译")
            continue
        if verbose:
            ph_count = len(re.findall(r'«h?\d+»', chunk))
            extra = f" (含{ph_count}个占位符)" if ph_count else ""
            safe_print(f"      [分块 {i+1}/{len(chunks)}] ({len(chunk)} 字符){extra}")
        translated.append(_translate_single_with_retry(chunk, verbose, file_label, para_idx, i))
    return "".join(translated)

def _translate_single_with_retry(text: str, verbose: bool, file_label: str,
                                 para_idx: int, chunk_idx: int) -> str:
    result = translate_text(text, verbose=verbose, file_label=file_label,
                            para_idx=para_idx, chunk_idx=chunk_idx, temperature=0.0)
    if _needs_retry(result, text):
        for attempt in range(1, MAX_RETRIES + 1):
            safe_print(f"    ⚠ 检测到未翻译内容，重试 ({attempt}/{MAX_RETRIES})")
            result = translate_text(text, verbose=verbose, file_label=file_label,
                                    para_idx=para_idx, chunk_idx=chunk_idx,
                                    temperature=0.2)
            if not _needs_retry(result, text):
                break
    return result

def _needs_retry(translated: str, original: str) -> bool:
    clean_trans = re.sub(r'«h?\d+»|⊂PH\d+⊃', '', translated).strip()
    if len(clean_trans) < 5:
        return False
    orig_clean = re.sub(r'«h?\d+»|⊂PH\d+⊃', '', original)
    eng_words = len(re.findall(r'\b[a-zA-Z]{2,}\b', clean_trans))
    total_words = len(clean_trans.split())
    if total_words == 0:
        return False
    orig_eng = len(re.findall(r'\b[a-zA-Z]{2,}\b', orig_clean))
    orig_total = len(orig_clean.split()) or 1
    if orig_eng / orig_total < 0.5:
        return False
    return (eng_words / total_words) > 0.3

# ================== 表格翻译 ==================
def translate_markdown_table(table_text: str, verbose: bool = False) -> str:
    lines = table_text.strip().split('\n')
    if len(lines) < 2:
        return translate_long_text(table_text, verbose)

    pre_table_lines = []
    table_start = 0
    for idx, line in enumerate(lines):
        if _is_table_line(line):
            table_start = idx
            break
        pre_table_lines.append(line)
    table_lines = lines[table_start:]
    if len(table_lines) < 2:
        return translate_long_text(table_text, verbose)

    norm = []
    for line in table_lines:
        line = line.strip()
        if not line.startswith('|'):
            line = '|' + line
        if not line.endswith('|'):
            line = line + '|'
        norm.append(line)

    sep_idx = -1
    for idx, line in enumerate(norm):
        if _is_table_separator(line):
            sep_idx = idx
            break
    if sep_idx < 0:
        return translate_long_text(table_text, verbose)

    full_table = '\n'.join(norm)
    html_phs: Dict[str, str] = {}
    tag_counter = [0]
    def _repl_tag(m):
        ph = f"«th{tag_counter[0]}»"
        html_phs[ph] = m.group(0)
        tag_counter[0] += 1
        return ph
    protected_full = re.sub(r'<[^>]+>', _repl_tag, full_table)

    prot_lines = protected_full.split('\n')
    header_block = '\n'.join(prot_lines[:sep_idx + 1])
    data_rows = prot_lines[sep_idx + 1:]

    batches = []
    cur = header_block
    for row in data_rows:
        if len(cur) + len(row) + 1 > MAX_CHUNK_CHARS and cur != header_block:
            batches.append(cur)
            cur = header_block + '\n' + row
        else:
            cur += '\n' + row
    if cur.strip():
        batches.append(cur)
    if not batches:
        batches = [protected_full]

    translated_batches = []
    for i, batch in enumerate(batches):
        if verbose:
            safe_print(f"      [表格批次 {i+1}/{len(batches)}] ({len(batch)} 字符)")
        trans = translate_text(batch, verbose=False, max_tokens=TABLE_MAX_TOKENS)
        translated_batches.append(trans)

    if len(translated_batches) == 1:
        translated_table = translated_batches[0]
    else:
        combined = translated_batches[0]
        for bt in translated_batches[1:]:
            blines = bt.split('\n')
            skip = 0
            for j, bl in enumerate(blines):
                if _is_table_separator(bl.strip()):
                    skip = j + 1
                    break
            rest = '\n'.join(blines[skip:]) if skip < len(blines) else bt
            if rest.strip():
                combined += '\n' + rest
        translated_table = combined

    translated_table = restore_ph(translated_table, html_phs)

    translated_pre = []
    for line in pre_table_lines:
        if line.strip():
            translated_pre.append(translate_long_text(line, verbose=verbose))
        else:
            translated_pre.append(line)

    parts = []
    if translated_pre:
        parts.append('\n'.join(translated_pre))
    parts.append(translated_table)
    return '\n\n'.join(parts)

# ================== Markdown 主处理 ==================
def protect_and_translate_markdown(markdown: str, verbose: bool = False,
                                   file_label: str = "") -> str:
    # ① 转换 <Listing> 为 Markdown
    markdown = convert_listing_to_markdown(markdown)

    regular_phs: Dict[str, str] = {}
    table_phs: Dict[str, str] = {}
    counter = [0]

    def _make_ph(content, is_table=False):
        ph = f"«{counter[0]}»"
        counter[0] += 1
        (table_phs if is_table else regular_phs)[ph] = content
        return ph

    # ② 保护阶段
    text = re.sub(r'<!--[\s\S]*?-->', lambda m: _make_ph(m.group(0)), markdown)
    text = re.sub(r'```[\s\S]*?```',   lambda m: _make_ph(m.group(0)), text, flags=re.MULTILINE)
    text = re.sub(r'`[^`]+`',          lambda m: _make_ph(m.group(0)), text)
    text = re.sub(r'<[^>]+>',          lambda m: _make_ph(m.group(0)), text)

    link_def_re = r'^\[[^]]+\]:\s*\S.*(?:\n[ \t]+.*)*'
    text = re.sub(link_def_re, lambda m: _make_ph(m.group(0)), text, flags=re.MULTILINE)

    link_use_re = r'\[([^\[\]]+)\]\[([^\[\]]*)\]'
    text = re.sub(link_use_re, lambda m: _make_ph(m.group(0)), text)

    table_pattern = (
        r'(?:^\|.+\|[ \t]*\n)+'
        r'^\|[\s\-:|]+\|[ \t]*\n'
        r'(?:^\|.+\|[ \t]*\n?)+'
    )
    text = re.sub(table_pattern,
                  lambda m: _make_ph(m.group(0), is_table=True),
                  text, flags=re.MULTILINE)

    if verbose:
        safe_print(f"  [{file_label}] {len(regular_phs)} 个普通占位符, "
                   f"{len(table_phs)} 个表格占位符")

    # ③ 按段落翻译
    paragraphs = re.split(r'\n\s*\n', text)
    if verbose:
        safe_print(f"  [{file_label}] 段落总数: {len(paragraphs)}")
    translated_paras = []
    # 并发环境下，进度条可能会重叠，仅在 verbose 时显示简单计数
    for para in paragraphs:
        if not para.strip():
            translated_paras.append(para)
            continue
        if _is_pure_placeholder(para):
            translated_paras.append(para)
            continue
        translated_paras.append(translate_long_text(para, verbose=verbose,
                                                    file_label=file_label))
    translated_text = '\n\n'.join(translated_paras)
    translated_text = normalize_ph(translated_text)

    if verbose:
        safe_print(f"  [{file_label}] 正在恢复保护元素...")

    # ④ 先恢复表格
    for ph, orig in table_phs.items():
        trans_tbl = translate_markdown_table(orig, verbose=verbose)
        translated_text = translated_text.replace(ph, trans_tbl)

    # ⑤ 恢复普通占位符
    translated_text = restore_ph(translated_text, regular_phs)
    return translated_text

# ================== 文件处理（用于并发任务） ==================
def detect_encoding(file_path: Path) -> str:
    if chardet:
        with open(file_path, 'rb') as f:
            raw = f.read(10000)
            result = chardet.detect(raw)
            return result['encoding'] or 'utf-8'
    return 'utf-8'

def _process_one_file(src: Path, input_base: Path, output_base: Path,
                      verbose: bool, force: bool) -> dict:
    """处理单个文件的翻译，返回状态字典。用于并发"""
    rel = src.relative_to(input_base)
    dst = output_base / rel.with_suffix('.md')
    status = {"file": str(rel), "result": "skipped", "error": None}

    if not force and dst.exists() and dst.stat().st_size > 0:
        return status

    try:
        enc = detect_encoding(src)
        with open(src, 'r', encoding=enc) as f:
            md = f.read()
        translated = protect_and_translate_markdown(md, verbose=verbose,
                                                    file_label=rel.name)
        dst.parent.mkdir(parents=True, exist_ok=True)
        with open(dst, 'w', encoding='utf-8') as f:
            f.write(translated)
        status["result"] = "processed"
    except Exception as e:
        status["result"] = "failed"
        status["error"] = str(e)
    return status

def collect_markdown_files(root: Path, extensions: tuple = ('.md', '.markdown')) -> Iterator[Path]:
    for ext in extensions:
        for f in root.glob(f'*{ext}'):
            if f.is_file():
                yield f
    for subdir in sorted([d for d in root.iterdir() if d.is_dir()]):
        yield from collect_markdown_files(subdir, extensions)

def translate_directory(input_dir: str, output_dir: str,
                        extensions: tuple = ('.md', '.markdown'),
                        verbose: bool = False, force: bool = False,
                        workers: int = DEFAULT_WORKERS):
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    if not input_path.exists():
        raise FileNotFoundError(f"输入目录不存在: {input_dir}")

    all_files = list(collect_markdown_files(input_path, extensions))
    print(f"找到 {len(all_files)} 个 Markdown 文件待处理，使用 {workers} 个工作线程并发\n")

    skipped = processed = failed = 0
    # 并发处理文件
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {}
        for src in all_files:
            future = executor.submit(_process_one_file, src, input_path, output_path, verbose, force)
            futures[future] = src

        # 进度条包装
        pbar = tqdm(total=len(all_files), desc="文件进度", unit="个") if verbose else None
        for future in as_completed(futures):
            status = future.result()
            if status["result"] == "processed":
                processed += 1
            elif status["result"] == "skipped":
                skipped += 1
            elif status["result"] == "failed":
                failed += 1
                safe_print(f"\n  错误处理 {status['file']}: {status['error']}")
            if pbar:
                pbar.update(1)
        if pbar:
            pbar.close()

    print(f"\n处理完成: 翻译 {processed} 个, 跳过 {skipped} 个, 失败 {failed} 个")

# ================== 主函数 ==================
def main():
    global DEBUG_ENABLED, DEBUG_SAMPLES
    parser = argparse.ArgumentParser(description="翻译 Markdown 文件（多文件并发版）")
    parser.add_argument("input", help="输入文件或目录")
    parser.add_argument("output", help="输出文件或目录")
    parser.add_argument("--verbose", "-v", action="store_true", help="显示详细进度")
    parser.add_argument("--force", "-f", action="store_true", help="强制覆盖已翻译文件")
    parser.add_argument("--log", default=None, help="将详细日志写入文件")
    parser.add_argument("--debug-json", default=None, help="将所有待翻译文本保存到 JSON 文件（调试用）")
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS, help="并发文件处理线程数 (默认: 4)")
    args = parser.parse_args()

    if args.debug_json:
        DEBUG_ENABLED = True

    log_file = None
    if args.log:
        log_file = open(args.log, 'w', encoding='utf-8')
        sys.stdout = Tee(sys.stdout, log_file)

    input_path = Path(args.input)
    output_path = Path(args.output)
    if not input_path.exists():
        print(f"错误：输入路径不存在: {input_path}")
        sys.exit(1)

    start_time = time.time()
    if input_path.is_file():
        print(f"读取文件: {input_path}")
        enc = detect_encoding(input_path)
        with open(input_path, 'r', encoding=enc) as f:
            md = f.read()
        print("翻译中...")
        translated = protect_and_translate_markdown(md, verbose=args.verbose,
                                                    file_label=input_path.name)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(translated)
        elapsed = time.time() - start_time
        print(f"\n完成: {output_path}")
        print(f"耗时 {elapsed:.1f} 秒")
    elif input_path.is_dir():
        output_path.mkdir(parents=True, exist_ok=True)
        translate_directory(str(input_path), str(output_path),
                            verbose=args.verbose, force=args.force,
                            workers=args.workers)
        elapsed = time.time() - start_time
        print(f"总耗时 {elapsed:.1f} 秒")
    else:
        print("错误：输入路径无效")
        sys.exit(1)

    if args.debug_json and DEBUG_SAMPLES:
        with open(args.debug_json, 'w', encoding='utf-8') as f:
            json.dump(DEBUG_SAMPLES, f, ensure_ascii=False, indent=2)
        print(f"调试数据已保存到: {args.debug_json}")

    if log_file:
        sys.stdout = sys.__stdout__
        log_file.close()

if __name__ == "__main__":
    main()