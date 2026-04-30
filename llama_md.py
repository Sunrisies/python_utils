import sys
import time
import re
import argparse
from pathlib import Path
from typing import Iterator, Dict

import requests
import chardet

try:
    from tqdm import tqdm as _tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False
    _tqdm = None

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
    if _tqdm is None:
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
    "6. 对于 Markdown 链接 `[text](url)` 和图片 `![alt](url)`，只翻译方括号内的显示文本，保留 URL 和全部分隔符。\n"
    "7. 保持原有的列表符号（-、*、1. 等）和引用符号（>）不变，不要添加或删除。\n"
    "8. 如果遇到无法确定或无法准确翻译的术语，直接保留原文。\n"
    "9. 仅翻译自然语言文本（普通句子、段落、标题、列表项），技术名词按上述规则处理。"
)

# ================== 翻译核心 ==================
def translate_text(text: str, verbose: bool = False,
                   max_tokens: int = MAX_NEW_TOKENS) -> str:
    if not text or not text.strip():
        return text

    # ----- 保护所有 «N» / «hN» 占位符，防止模型篡改 -----
    ph_pattern = re.compile(r'«(h?\d+)»')
    temp_map = {}
    counter = [0]
    def _protect(m):
        key = f"⊂PH{counter[0]}⊃"
        temp_map[key] = m.group(0)   # 保存原始占位符，如 «53», «h3»
        counter[0] += 1
        return key
    protected_text = ph_pattern.sub(_protect, text)

    # 原有翻译逻辑，但改用 protected_text
    payload = {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"请翻译以下内容为简体中文：\n{protected_text}"}
        ],
        "max_tokens": max_tokens,
        "temperature": 0.0
    }

    try:
        resp = requests.post(SERVER_URL, json=payload, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"].strip()
        if verbose:
            usage = data.get("usage", {})
            safe_print(f"    输入 tokens: {usage.get('prompt_tokens', '?')}, "
                       f"输出 tokens: {usage.get('completion_tokens', '?')}")
    except Exception as e:
        safe_print(f"  [翻译失败] {e}，保留原文")
        return text   # 失败时返回原始 text（注意此处返回的是保护前的text，保持占位符不变）

    # ----- 恢复临时标记 → 原始占位符 «N» -----
    for key, orig_ph in temp_map.items():
        content = content.replace(key, orig_ph)

    return content



# ================== 占位符工具 ==================
def normalize_ph(text: str) -> str:
    """修复 LLM 可能引入的占位符空格"""
    text = re.sub(r'«\s*h\s*(\d+)\s*»', r'«h\1»', text)
    text = re.sub(r'«\s*(\d+)\s*»', r'«\1»', text)
    return text

def restore_ph(text: str, ph_map: Dict[str, str]) -> str:
    """
    恢复占位符，按编号降序以防止嵌套残留。
    增加对中文引号「」、｢｣ 等模型翻译产生的变体的模糊匹配。
    """
    text = normalize_ph(text)

    def _num(ph: str) -> int:
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

            # 模糊匹配候选：模型可能生成的变体
            candidates = [
                f'[{prefix}{n}]',
                f'<{prefix}{n}>',
                f'« {prefix}{n}»',          # 带空格
                f'«{prefix}{n} »',
                f'「{prefix}{n}」',         # 中文引号
                f'｢{prefix}{n}｣',         # 半角引号
                f'『{prefix}{n}』',         # 双中文引号
            ]
            for alt in candidates:
                if alt in text and alt != ph:
                    # 避免误改 Markdown 链接：[N](url)
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
def split_text_preserve_placeholders(text: str, max_length: int) -> list:
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
            if _is_table_line(seg.split('\n')[0]):
                table_parts = [seg]
                j = i + 1
                while j < len(paragraphs):
                    nxt = paragraphs[j]
                    if nxt.strip() and _is_table_line(nxt.split('\n')[0]):
                        table_parts.append(nxt); j += 1
                    elif nxt.strip() == '':
                        if j + 1 < len(paragraphs) and _is_table_line(paragraphs[j + 1].split('\n')[0]):
                            table_parts.append(nxt); j += 1
                        else:
                            break
                    else:
                        break
                if current.strip():
                    cur_lines = current.rstrip('\n').split('\n')
                    prefix = []
                    while cur_lines and not _is_table_line(cur_lines[-1]) and cur_lines[-1].strip():
                        prefix.insert(0, cur_lines.pop())
                    if prefix:
                        table_parts.insert(0, '\n'.join(prefix))
                        current = '\n'.join(cur_lines)
                full_table = '\n'.join(table_parts)
                if current.strip():
                    chunks.append(current.strip()); current = ""
                if len(full_table) <= max_length:
                    chunks.append(full_table.strip())
                else:
                    tl = full_table.split('\n')
                    hdr, data, found = [], [], False
                    for row in tl:
                        if _is_table_separator(row.strip()):
                            hdr.append(row); found = True
                        elif not found:
                            hdr.append(row)
                        else:
                            data.append(row)
                    hdr_block = '\n'.join(hdr)
                    sub = hdr_block
                    for d in data:
                        if len(sub) + len(d) + 1 > max_length:
                            if sub.strip(): chunks.append(sub.strip())
                            sub = d
                        else:
                            sub += '\n' + d
                    if sub.strip(): chunks.append(sub.strip())
                i = j; continue
            if len(current) + len(seg) <= max_length:
                current += seg
            else:
                if current.strip(): chunks.append(current.strip())
                sents = re.split(r'(?<=[。！？;.!\n])', seg)
                current = ""
                for s in sents:
                    if len(current) + len(s) <= max_length:
                        current += s
                    else:
                        if current.strip(): chunks.append(current.strip())
                        if len(s) > max_length:
                            for k in range(0, len(s), max_length):
                                chunks.append(s[k:k + max_length].strip())
                            current = ""
                        else:
                            current = s
            i += 1
        if current.strip(): chunks.append(current.strip())

    final = []
    for chunk in chunks:
        for orig_ph, tmp_ph in temp_map.items():
            chunk = chunk.replace(tmp_ph, orig_ph)
        final.append(chunk)
    return final

def translate_long_text(text: str, verbose: bool = False) -> str:
    chunks = split_text_preserve_placeholders(text, MAX_CHUNK_CHARS)
    if not chunks:
        return ""
    if len(chunks) == 1:
        return translate_text(chunks[0], verbose)
    translated = []
    for i, chunk in enumerate(chunks):
        if verbose:
            ph_count = len(re.findall(r'«h?\d+»', chunk))
            extra = f" (含{ph_count}个占位符)" if ph_count else ""
            safe_print(f"      [分块 {i+1}/{len(chunks)}] ({len(chunk)} 字符){extra}")
        translated.append(translate_text(chunk, verbose))
    return "".join(translated)

# ================== 表格翻译（保护全局占位符） ==================
def translate_markdown_table(table_text: str, verbose: bool = False) -> str:
    """
    批量翻译 Markdown 表格。
    - 首先保护表格内已有的全局占位符 «N»，防止模型篡改
    - 再保护 HTML 标签，分批翻译
    """
    # 0. 保护全局占位符 «N»，使用临时标记 ⊂PH{N}⊃（模型几乎不会改动）
    global_phs = {}   # 临时标记 → 原始 «N»
    def _protect_global(m):
        orig = m.group(0)
        key = f"⊂PH{len(global_phs)}⊃"
        global_phs[key] = orig
        return key
    protected_text = re.sub(r'«\d+»', _protect_global, table_text)

    lines = protected_text.strip().split('\n')
    if len(lines) < 2:
        return translate_long_text(table_text, verbose)

    # 分离表前内容
    pre_table_lines = []
    table_start = 0
    for idx, line in enumerate(lines):
        if _is_table_line(line):
            table_start = idx; break
        pre_table_lines.append(line)
    table_lines = lines[table_start:]
    if len(table_lines) < 2:
        return translate_long_text(table_text, verbose)

    # 标准化
    norm = []
    for line in table_lines:
        line = line.strip()
        if not line.startswith('|'): line = '|' + line
        if not line.endswith('|'):   line = line + '|'
        norm.append(line)

    sep_idx = -1
    for idx, line in enumerate(norm):
        if _is_table_separator(line):
            sep_idx = idx; break
    if sep_idx < 0:
        return translate_long_text(table_text, verbose)

    # 保护 HTML 标签（用 «hN»）
    full_table = '\n'.join(norm)
    html_phs: Dict[str, str] = {}
    tag_i = [0]
    def _repl_tag(m):
        ph = f"«h{tag_i[0]}»"
        html_phs[ph] = m.group(0)
        tag_i[0] += 1
        return ph
    protected_full = re.sub(r'<[^>]+>', _repl_tag, full_table)

    # 拆分批次
    prot_lines = protected_full.split('\n')
    header_block = '\n'.join(prot_lines[:sep_idx + 1])
    data_rows    = prot_lines[sep_idx + 1:]

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

    # 逐批次翻译
    translated_batches = []
    for i, batch in enumerate(batches):
        if verbose:
            safe_print(f"      [表格批次 {i+1}/{len(batches)}] ({len(batch)} 字符)")
        trans = translate_text(batch, verbose=False, max_tokens=TABLE_MAX_TOKENS)
        translated_batches.append(trans)

    # 合并
    if len(translated_batches) == 1:
        translated_table = translated_batches[0]
    else:
        combined = translated_batches[0]
        for bt in translated_batches[1:]:
            blines = bt.split('\n')
            skip = 0
            for j, bl in enumerate(blines):
                if _is_table_separator(bl.strip()):
                    skip = j + 1; break
            rest = '\n'.join(blines[skip:]) if skip < len(blines) else bt
            if rest.strip():
                combined += '\n' + rest
        translated_table = combined

    # 恢复 HTML 标签
    translated_table = restore_ph(translated_table, html_phs)

    # 恢复全局占位符 «N»
    for tmp, orig in global_phs.items():
        translated_table = translated_table.replace(tmp, orig)

    # 翻译表前内容（对已保护的部分单独处理）
    translated_pre = []
    for line in pre_table_lines:
        if line.strip() and not re.fullmatch(r'⊂PH\d+⊃', line.strip()):
            # 恢复临时标记后再翻译安全些
            temp_restored = line
            for tmp, orig in global_phs.items():
                temp_restored = temp_restored.replace(tmp, orig)
            translated_pre.append(translate_long_text(temp_restored, verbose=verbose))
        else:
            translated_pre.append(line)
    # 恢复表前行中的临时标记
    result_pre = '\n'.join(translated_pre)
    for tmp, orig in global_phs.items():
        result_pre = result_pre.replace(tmp, orig)
    # 同样恢复 translated_table 可能残留的临时标记（上面已处理）

    parts = []
    if result_pre.strip():
        parts.append(result_pre)
    parts.append(translated_table)
    return '\n\n'.join(parts)

# ================== Markdown 主处理 ==================
def protect_and_translate_markdown(markdown: str, verbose: bool = False,
                                   file_label: str = "") -> str:
    regular_phs: Dict[str, str] = {}
    table_phs: Dict[str, str] = {}
    counter = [0]

    def _make_ph(content, is_table=False):
        ph = f"«{counter[0]}»"
        counter[0] += 1
        (table_phs if is_table else regular_phs)[ph] = content
        return ph

    text = re.sub(r'<!--[\s\S]*?-->', lambda m: _make_ph(m.group(0)), markdown)
    text = re.sub(r'```[\s\S]*?```',   lambda m: _make_ph(m.group(0)), text, flags=re.MULTILINE)
    text = re.sub(r'<[^>]+>',          lambda m: _make_ph(m.group(0)), text)
    text = re.sub(r'`[^`]+`',          lambda m: _make_ph(m.group(0)), text)

    table_pattern = (
        r'(?:^[^|]*?\n)?'
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

    paragraphs = re.split(r'\n\s*\n', text)
    if verbose:
        safe_print(f"  [{file_label}] 段落总数: {len(paragraphs)}")
    translated_paras = []
    pbar = tqdm(paragraphs, desc="翻译段落", unit="段") if verbose else paragraphs
    for para in pbar:
        if not para.strip():
            translated_paras.append(para); continue
        if re.fullmatch(r'(«\d+»\s*)+', para.strip()):
            translated_paras.append(para); continue
        translated_paras.append(translate_long_text(para, verbose=verbose))
    translated_text = '\n\n'.join(translated_paras)
    translated_text = normalize_ph(translated_text)

    if verbose:
        safe_print(f"  [{file_label}] 正在恢复保护元素...")

    # 先恢复表格
    for ph, orig in table_phs.items():
        trans_tbl = translate_markdown_table(orig, verbose=verbose)
        translated_text = translated_text.replace(ph, trans_tbl)

    # 恢复普通占位符（降序）
    translated_text = restore_ph(translated_text, regular_phs)
    return translated_text

# ================== 文件处理（保持不变） ==================
def detect_encoding(file_path: Path) -> str:
    with open(file_path, 'rb') as f:
        raw = f.read(10000)
        result = chardet.detect(raw)
        return result['encoding'] or 'utf-8'

def collect_markdown_files(root: Path, extensions: tuple = ('.md', '.markdown')) -> Iterator[Path]:
    for ext in extensions:
        for f in root.glob(f'*{ext}'):
            if f.is_file():
                yield f
    for subdir in sorted([d for d in root.iterdir() if d.is_dir()]):
        yield from collect_markdown_files(subdir, extensions)

def translate_directory(input_dir: str, output_dir: str,
                        extensions: tuple = ('.md', '.markdown'),
                        verbose: bool = False, force: bool = False):
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    if not input_path.exists():
        raise FileNotFoundError(f"输入目录不存在: {input_dir}")
    all_files = list(collect_markdown_files(input_path, extensions))
    print(f"找到 {len(all_files)} 个 Markdown 文件待处理\n")
    skipped = processed = failed = 0
    file_iter = tqdm(all_files, desc="文件进度", unit="个") if verbose else all_files
    for src in file_iter:
        rel = src.relative_to(input_path)
        dst = output_path / rel.with_suffix('.md')
        dst.parent.mkdir(parents=True, exist_ok=True)
        if not force and dst.exists() and dst.stat().st_size > 0:
            if verbose: safe_print(f"  跳过已存在: {rel}")
            skipped += 1
            continue
        try:
            enc = detect_encoding(src)
            with open(src, 'r', encoding=enc) as f:
                md = f.read()
            translated = protect_and_translate_markdown(md, verbose=verbose, file_label=rel.name)
            with open(dst, 'w', encoding='utf-8') as f:
                f.write(translated)
            processed += 1
        except Exception as e:
            safe_print(f"\n  错误处理 {rel}: {e}")
            failed += 1
    print(f"\n处理完成: 翻译 {processed} 个, 跳过 {skipped} 个, 失败 {failed} 个")

def main():
    parser = argparse.ArgumentParser(description="翻译 Markdown 文件（llama-server API）")
    parser.add_argument("input", help="输入文件或目录")
    parser.add_argument("output", help="输出文件或目录")
    parser.add_argument("--verbose", "-v", action="store_true", help="显示详细进度")
    parser.add_argument("--force", "-f", action="store_true", help="强制覆盖已翻译文件")
    parser.add_argument("--log", default=None, help="将详细日志写入文件")
    args = parser.parse_args()

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
        translated = protect_and_translate_markdown(md, verbose=args.verbose, file_label=input_path.name)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(translated)
        elapsed = time.time() - start_time
        print(f"\n完成: {output_path}")
        print(f"耗时 {elapsed:.1f} 秒")
    elif input_path.is_dir():
        output_path.mkdir(parents=True, exist_ok=True)
        translate_directory(str(input_path), str(output_path),
                           verbose=args.verbose, force=args.force)
        elapsed = time.time() - start_time
        print(f"总耗时 {elapsed:.1f} 秒")
    else:
        print("错误：输入路径无效")
        sys.exit(1)

    if log_file:
        sys.stdout = sys.__stdout__
        log_file.close()

if __name__ == "__main__":
    main()