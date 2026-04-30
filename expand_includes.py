import re
import sys
import argparse
from pathlib import Path

def extract_anchor_lines(file_path, anchor_name):
    """提取锚点之间的内容（不含标记行）"""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    start_marker = f"// ANCHOR: {anchor_name}"
    end_marker = f"// ANCHOR_END: {anchor_name}"
    capturing = False
    extracted = []
    for line in lines:
        if start_marker in line:
            capturing = True
            continue
        elif end_marker in line:
            capturing = False
            continue
        if capturing:
            extracted.append(line)
    return "".join(extracted)

def extract_lines_range(file_path, start, end=None):
    """提取从 start 行到 end 行的内容（行号从 1 开始）。
    如果 end 为 None，则提取到文件末尾。"""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    # 调整索引：行号 1 -> lines[0]
    start_idx = max(0, start - 1)
    if end is not None:
        end_idx = min(len(lines), end)  # 包含 end 行
    else:
        end_idx = len(lines)
    return "".join(lines[start_idx:end_idx])

def expand_includes(md_text, base_dir):
    """
    以 base_dir 为基准解析 include 路径。
    支持格式：
      {{#include file.rs}}
      {{#include file.rs:anchor}}
      {{#include file.rs:start:end}}
      {{#include file.rs:start}}
    """
    # 匹配路径 + 可选 : 片段（可能是锚点名或数字范围）
    pattern = re.compile(
        r'\{\{#(?:rustdoc_)?include\s+([^\s:}]+)'  # 文件路径
        r'(?::([^}\s]+))?\s*\}\}'                   # 可选的 : 片段
    )

    def replacer(match):
        relative_path = match.group(1).strip()
        fragment = match.group(2)  # 可能是 None, "anchor", "9:10", "9"

        abs_path = (base_dir / relative_path).resolve()
        if not abs_path.exists():
            print(f"  ⚠️  找不到：{abs_path}，保留原指令")
            return match.group(0)

        if fragment is None:
            # 整个文件
            with open(abs_path, 'r', encoding='utf-8') as f:
                return f.read()

        # 检查是否为数字范围（如 9:10 或 9）
        range_match = re.fullmatch(r'(\d+)(?::(\d+))?', fragment)
        if range_match:
            start = int(range_match.group(1))
            end_str = range_match.group(2)
            end = int(end_str) if end_str else None
            return extract_lines_range(abs_path, start, end)
        else:
            # 否则当作锚点名称处理
            return extract_anchor_lines(abs_path, fragment)

    return pattern.sub(replacer, md_text)

def process_file(input_file, output_dir, base_dir):
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    new_content = expand_includes(content, base_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / input_file.name
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"✅ 生成：{out_path}")

def main():
    parser = argparse.ArgumentParser(description="展开 mdBook 的 include 指令")
    parser.add_argument("source", help="源 md 文件所在目录")
    parser.add_argument("output", help="输出目录")
    parser.add_argument("--base", required=True,
                        help="原书 src 目录（用于解析相对路径）")
    args = parser.parse_args()

    src = Path(args.source)
    dst = Path(args.output)
    base_dir = Path(args.base)

    if not src.exists():
        print(f"❌ 源目录不存在：{src}")
        return

    md_files = list(src.rglob("*.md"))
    if not md_files:
        print(f"❌ 在 {src} 中没有找到 .md 文件")
        return

    print(f"📁 找到 {len(md_files)} 个文件，基准目录：{base_dir.resolve()}")
    for md in md_files:
        relative = md.relative_to(src)
        out_subdir = dst / relative.parent
        process_file(md, out_subdir, base_dir)

    print("🎉 全部完成")

if __name__ == "__main__":
    main()