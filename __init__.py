"""
url2video — 抖音无水印视频下载器

使用 hellotik.app 服务通过 Playwright 自动化下载抖音视频。
"""

from .downloader import download_video, download_from_share_text, extract_douyin_url

__all__ = [
    "download_video",
    "download_from_share_text",
    "extract_douyin_url",
]

__version__ = "0.2.0"
