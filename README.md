# url2video — 抖音无水印视频下载器

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

通过 hellotik.app 服务自动解析并下载**抖音无水印视频**。支持直接从分享文本提取链接，自动选择分辨率，一键下载。

---

## 功能

- ✅ **无水印下载** — 自动解析并下载抖音视频，去除水印
- ✅ **智能链接提取** — 支持多种抖音链接格式（短链、长链、分享文本）
- ✅ **自动选择分辨率** — 自动检测并点击最高可用分辨率
- ✅ **Playwright 自动化** — 浏览器自动化防检测
- ✅ **简单易用的 API** — Python 包和命令行都可用

## 安装

```bash
# 1. 克隆仓库
git clone https://github.com/HomeSafe2017/url2video.git
cd url2video

# 2. 安装依赖
pip install -e .

# 3. 安装 Playwright 浏览器
playwright install chromium
```

## 快速开始

### 命令行使用

```bash
# 直接传抖音分享文本
python -m url2video "8.20 复制打开抖音，看看【晓二浅谈的作品】... https://v.douyin.com/xxx/"

# 只传链接
python -m url2video "https://v.douyin.com/xxx/"

# 指定输出目录
python -m url2video "https://v.douyin.com/xxx/" --output ./videos
```

### 在 Python 中使用

```python
from url2video import download_video, download_from_share_text

# 方式 1：直接传抖音链接
path = download_video(
    "https://v.douyin.com/xxx/",
    output_dir="./downloads",
    headless=True,     # 无头模式（不显示浏览器窗口）
)
print(f"视频已保存到: {path}")

# 方式 2：传完整的分享文本（自动提取链接）
text = "8.20 复制打开抖音，看看【作者】... https://v.douyin.com/xxx/"
path = download_from_share_text(text, headless=True)
print(f"视频已保存到: {path}")
```

## API 参考

| 函数 | 说明 | 参数 |
|---|---|---|
| `download_video(url, output_dir, headless, timeout)` | 直接下载抖音链接 | `url` — 抖音视频链接 |
| `download_from_share_text(text, output_dir, headless, timeout)` | 从分享文本提取链接后下载 | `text` — 分享文本 |
| `extract_douyin_url(text)` | 从文本中提取抖音链接 | `text` — 文本内容 |

### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `output_dir` | `str` / `Path` | `./downloads` | 下载保存目录 |
| `headless` | `bool` | `False` | 是否无头模式（不显示浏览器） |
| `timeout` | `int` | `120` | 整体超时秒数 |

## 工作流程

```
分享文本 ──→ extract_douyin_url() ──→ 抖音链接
                                          │
                                          ▼
                               hellotik.app 页面
                                          │
                              ┌───────────┴───────────┐
                              ▼                       ▼
                         填写链接                 选择分辨率
                              │                       │
                              └───────────┬───────────┘
                                          ▼
                                      点击下载
                                          │
                                          ▼
                                   无水印视频 ✅
```

## 文件结构

```
url2video/
├── downloader.py      # 核心下载逻辑
├── __init__.py        # 包入口
├── pyproject.toml     # 项目配置
├── README.md          # 说明文档
└── SKILL.md           # Hermes Agent skill
```

## 依赖

- **Python ≥ 3.10**
- **playwright** — 浏览器自动化
- **Chromium**（通过 `playwright install chromium` 安装）

## 注意事项

1. **首次使用**需要运行 `playwright install chromium` 安装浏览器
2. `headless=False`（默认）会弹出浏览器窗口，方便观察过程；部署时可设为 `True`
3. hellotik.app 可能需要科学上网
4. 请遵守抖音的用户协议和版权规定

## 许可证

MIT License © 2024 杨佳宁
