# Rust 文档翻译工具集

本项目包含多个用于翻译 Rust 官方文档（HTML/Markdown）的 Python 脚本。

## 环境要求

```bash
pip install torch transformers modelscope requests beautifulsoup4 chardet tqdm
```

**注意**：部分脚本需要 CUDA 支持。

---

## 脚本说明

### 1. translate_md.py（推荐）

使用 ModelScope 的 `Tencent-Hunyuan/HY-MT1.5-1.8B` 模型翻译 Markdown 文件。

```bash
# 翻译单个文件
python translate_md.py input.md output.md

# 翻译整个目录
python translate_md.py /path/to/source /path/to/output

# 参数
-v, --verbose   显示详细进度
-f, --force     强制覆盖已翻译的文件
```

**特性**：
- 代码块和行内代码保护
- 表格翻译支持
- 批量 GPU 加速

---

### 2. llama_md.py

使用本地 llama-server（OpenAI 兼容 API）翻译 Markdown 文件。

```bash
# 需要先启动 llama-server（默认 http://localhost:12323）
python llama_md.py input.md output.md

# 参数
-v, --verbose   显示详细进度
-f, --force     强制覆盖
--log file.log  日志输出
--debug-json debug.json  保存调试数据
```

**特性**：
- 占位符保护（如 `«0»`、`«h3»`）
- 表格智能处理
- 引用块 `>` 符号保留

**启动 llama-server 示例**：
```bash
llama-server -m .\dir\HY-MT1.5-1.8B-Q8_0.gguf --host 0.0.0.0 --port 12323 -ngl 99 -c 9162
```

---

### 3. main.py

使用 ModelScope 模型翻译 HTML 文件。

```bash
python main.py input.html output.html
python main.py /path/to/source /path/to/output

# 参数
-v, --verbose   显示详细进度
-f, --force     强制覆盖
```

**特性**：
- HTML 标签保留
- 跳过代码块和属性
- 文本节点和属性翻译

---

### 4. expand_includes.py

展开 mdBook 的 `{{#include}}` 指令，用于处理 Rust 官方文档的嵌入代码。

```bash
python expand_includes.py source_dir output_dir --base original_src_dir
```

**支持的格式**：
```
{{#include file.rs}}              # 整个文件
{{#include file.rs:anchor}}       # 锚点之间
{{#include file.rs:9:20}}         # 第9到20行
{{#include file.rs:9}}            # 第9行到末尾
```

---

## 其他脚本

- `latAndLon.py` - 测试用随机坐标生成
- `down.py` - 模型下载示例（已注释）

---

## 配置说明

各脚本的核心配置在文件顶部：

| 脚本 | 模型 | API 地址 | 分块大小 |
|-----|------|---------|---------|
| translate_md.py | HY-MT1.5-1.8B | ModelScope | 2500 |
| llama_md.py | 自定义 | http://localhost:12323 | 2500 |
| main.py | HY-MT1.5-1.8B | ModelScope | 300 |

---

## 注意事项

1. 代码块、变量名、URL 等不会被翻译
2. Rust 技术名词按约定翻译（如 ownership → 所有权）
3. 建议使用 GPU 加速