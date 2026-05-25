---
title: url2video — 抖音无水印视频下载
description: 通过 hellotik.app 自动解析并下载抖音无水印视频，支持分享文本智能提取链接
category: software-development
---

# url2video — 抖音无水印视频下载

通过 hellotik.app 自动解析并下载抖音视频（无水印）。使用 Playwright 浏览器自动化，支持直接从分享文本提取链接。

## 安装

```bash
# 本地项目路径
cd /mnt/c/Users/杨佳宁/Desktop/proj_back/video_gen/url2video
pip install -e .
playwright install chromium
```

## 使用方法

### Python API

```python
from url2video import download_video, download_from_share_text

# 直接链接下载
path = download_video("https://v.douyin.com/xxx/", headless=True)

# 分享文本下载（自动提取链接）
text = "8.20 复制打开抖音... https://v.douyin.com/xxx/"
path = download_from_share_text(text, headless=True)
```

### 命令行

```bash
python -m url2video "https://v.douyin.com/xxx/"
python -m url2video "https://v.douyin.com/xxx/" --output ./videos
```

## 参数

| 参数 | 默认值 | 说明 |
|---|---|---|
| `output_dir` | `./downloads` | 下载目录 |
| `headless` | `False` | 无头模式 |
| `timeout` | `120` | 超时秒数 |

## 注意事项

- 首次使用需 `playwright install chromium`
- hellotik.app 可能需要科学上网
- `headless=False` 会弹出浏览器窗口方便调试
