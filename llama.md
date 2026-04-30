以下是一份简洁实用的 llama.cpp 使用文档，覆盖你需要的场景：编译/下载、启动 API 服务、常用参数、性能调优。

---

# llama.cpp 快速使用指南

## 1. 获取 llama.cpp

### 方式一：下载预编译版本（推荐）
从 [GitHub Releases](https://github.com/ggml-org/llama.cpp/releases) 下载对应平台的压缩包：
- **Windows CUDA 版**（NVIDIA 显卡）：`llama-bXXXX-bin-win-cuda-cu12.4-x64.zip`
- **Windows Vulkan 版**（通用 GPU）：`llama-bXXXX-bin-win-vulkan-x64.zip`
- **macOS Metal 版**：`llama-bXXXX-bin-macos-arm64.zip`
- **Linux CUDA 版**：`llama-bXXXX-bin-linux-cuda-cu12.4-x64.tar.gz`

解压后即可使用，无需安装。

### 方式二：从源码编译
```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
cmake -B build -DGGML_CUDA=ON   # 或 -DGGML_VULKAN=ON / -DGGML_METAL=ON
cmake --build build --config Release -j
```
编译后二进制文件在 `build/bin/` 下。

---

## 2. 准备模型
需要 **GGUF 格式** 的模型，推荐量化版本：
- `Q4_K_M`：平衡速度与质量（约 1.2GB/1.8B）
- `Q5_K_M`：质量更高
- `Q8_0`：近乎无损，但体积大（约 2.0GB/1.8B）

可以从 HuggingFace 等地方下载，例如 `HY-MT1.5-1.8B-Q4_K_M.gguf`。

---

## 3. 启动 HTTP API 服务器（OpenAI 兼容）

### 基础命令
```bash
llama-server -m model.gguf --host 0.0.0.0 --port 12323
```

### 常用参数说明
| 参数 | 默认值 | 说明 |
|------|--------|------|
| `-m` | 必填 | 模型文件路径 |
| `--host` | 127.0.0.1 | 监听地址，`0.0.0.0` 允许外部访问 |
| `--port` | 8080 | 服务端口 |
| `-ngl 99` | 0 | 卸放层数到 GPU，`99` 表示全部层 |
| `-c 4096` | 2048 | 上下文长度（token 数） |
| `-b 2048` | 512 | 批处理大小，越大 prefill 越快，但耗显存 |
| `--cache-ram 0` | 8192 | 提示缓存大小（MB），`0` 禁用（推荐用于短文本翻译） |
| `--slots 1` | 4 | 并发处理槽位数，单线程任务设 1 减少竞争 |
| `-fa` | auto | 闪存注意力，可 `on`/`off`/`auto`（CUDA 下建议开启） |
| `--cont-batching` | 关闭 | 允许连续批处理，多请求时提高吞吐 |
| `--verbose` | 关闭 | 输出详细日志（调试用） |

### 推荐翻译场景配置
```bash
# Windows NVIDIA CUDA 示例
llama-server.exe -m D:\models\HY-MT1.5-1.8B-Q4_K_M.gguf \
  --host 0.0.0.0 --port 12323 \
  -ngl 99 -c 4096 -b 2048 \
  --cache-ram 0 --slots 1

# macOS Metal 示例
llama-server -m ./models/HY-MT1.5-1.8B-Q4_K_M.gguf \
  --host 0.0.0.0 --port 12323 \
  -ngl 99 -c 4096 -b 2048 \
  --cache-ram 0 --slots 1
```

---

## 4. 测试 API
启动后可用 `curl` 测试：
```bash
curl http://localhost:12323/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Hello, how are you?"}],
    "temperature": 0.0
  }'
```

返回 JSON 包含翻译/生成结果。

也可以使用 Python 的 `openai` 库（需修改 base_url）或者你的 `translate.py` 脚本。

---

## 5. 性能调优

### 速度慢？依次检查
1. **确认 GPU 被正确使用**  
   启动日志应显示 `ggml_cuda: Found 1 CUDA devices:` 或 `ggml_vulkan: Found 2 Vulkan devices:` 并且 `offloaded 33/33 layers to GPU`。  
   若没有，检查是否缺少对应后端 DLL 或驱动。

2. **使用更小量化模型**  
   `Q4_K_M` 比 `Q8_0` 快 30%~50%，质量无明显下降。

3. **关闭提示缓存**  
   `--cache-ram 0` 能消除因缓存查找/淘汰造成的延迟抖动。

4. **限制并发槽位**  
   `--slots 1` 避免多请求争抢 GPU 资源（适合串行任务）。

5. **监控显存**  
   用 `nvidia-smi` 或任务管理器查看显存使用，若接近上限则减小 `-c` 或 `-b`。

### 进一步提升吞吐量
- **并发请求**：设置 `--slots 4 --cont-batching`，然后用多线程或异步发送翻译请求。
- **静态批处理**：增大 `-b`（如 4096）可提升 prefill 速度，但需确保显存充足。

---

## 6. 常见问题

**Q：启动报错 `error loading model: invalid model file`**  
A：模型不是 GGUF 格式，需用 `convert_hf_to_gguf.py` 转换。

**Q：生成结果出现乱码或重复**  
A：尝试降低 `temperature`（如 0.0），或增大 `--repeat-penalty 1.1`。

**Q：翻译脚本报连接错误**  
A：确保 `llama-server` 正在运行，且端口一致。

**Q：如何查看支持的参数？**  
A：`llama-server --help`

---

## 7. 更多资源
- [官方仓库](https://github.com/ggml-org/llama.cpp)
- [GGUF 模型库](https://huggingface.co/models?sort=downloads&search=gguf)

---

以上足够覆盖你当前的文档翻译流程。如需深入定制（如调整采样参数），可参考官方文档或继续提问。