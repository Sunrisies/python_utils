import re
import sys
import argparse
from pathlib import Path

def extract_anchor_lines(file_path, anchor_name):
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

def expand_includes(md_text, base_dir):
    """
    以 base_dir 为基准解析 include 路径。
    base_dir 应指向原书的 src 目录（即原本存放这些 .md 的位置）
    """
    pattern = re.compile(r'\{\{#(?:rustdoc_)?include\s+([^\s:}]+)(?::(\S+))?\s*\}\}')

    def replacer(match):
        relative_path = match.group(1).strip()
        anchor = match.group(2)

        # 从 base_dir 出发解析相对路径
        abs_path = (base_dir / relative_path).resolve()
        if not abs_path.exists():
            print(f"  ⚠️  找不到：{abs_path}，保留原指令")
            return match.group(0)

        if anchor:
            return extract_anchor_lines(abs_path, anchor)
        else:
            with open(abs_path, 'r', encoding='utf-8') as f:
                return f.read()

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
                        help="原书 src 目录（即原始 .md 所在目录，用于解析 ../listings 相对路径）")
    args = parser.parse_args()

    src = Path(args.source)
    dst = Path(args.output)
    base_dir = Path(args.base)

    if not src.exists():
        print(f"❌ 源目录不存在：{src}")
        return

    # base_dir 可以不实际存在，但 resolve() 会将其转为绝对路径，不影响解析
    # 如果需要确保其父目录存在，可以手动创建，但通常不需要
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