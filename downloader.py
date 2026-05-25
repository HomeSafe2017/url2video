"""
url2video — Douyin video downloader using hellotik.app

Downloads Douyin (TikTok China) videos without watermark by automating
the hellotik.app service via Playwright.
"""

import logging
import os
import re
import time
from pathlib import Path
from typing import Optional

from playwright.sync_api import Download, sync_playwright

logger = logging.getLogger("url2video")

# hellotik.app selectors — adjust if the site updates its UI
SELECTORS = {
    "url_input": 'input[placeholder*="抖音"], input[type="text"]',
    "parse_btn": 'button:has-text("解析"), button:has-text("解析视频")',
    "download_btn": (
        'button:has-text("下载无水印视频"), '
        'button:has-text("下载视频"), '
        'button:has-text("下载")'
    ),
}

# Browser config for anti-detection
BROWSER_ARGS = [
    "--disable-blink-features=AutomationControlled",
    "--disable-infobars",
    "--no-sandbox",
    "--disable-dev-shm-usage",
]
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


def _anti_detect_script() -> str:
    """JavaScript injected before page load to mask Playwright automation."""
    return """
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    """


def _pick_resolution(page, timeout: int = 10) -> None:
    """Click the first resolution button (e.g. 720p, 1080p) if available."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        buttons = page.query_selector_all("button")
        for btn in buttons:
            text = btn.inner_text().strip()
            if re.match(r"^\d+p$", text):
                logger.info("选择分辨率: %s", text)
                btn.click()
                return
        time.sleep(1)
    logger.info("未找到分辨率选择按钮，使用默认设置")


def download_video(
    douyin_url: str,
    output_dir: str | Path = "./downloads",
    *,
    headless: bool = False,
    timeout: int = 120,
) -> Path:
    """
    使用 hellotik.app 解析并下载抖音视频。

    Args:
        douyin_url: 抖音视频分享链接 (如 https://v.douyin.com/xxx/)
        output_dir: 下载保存目录
        headless: 是否无头模式运行浏览器
        timeout: 整体超时秒数

    Returns:
        下载视频文件的绝对路径

    Raises:
        ValueError: douyin_url 为空或格式无效
        RuntimeError: 解析或下载过程中出错
    """
    if not douyin_url or not douyin_url.strip():
        raise ValueError("抖音链接不能为空")

    output_path = Path(output_dir).resolve()
    output_path.mkdir(parents=True, exist_ok=True)

    downloaded_file: Optional[Path] = None
    browser = None

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=headless,
                args=BROWSER_ARGS,
            )
            context = browser.new_context(
                user_agent=USER_AGENT,
                accept_downloads=True,
                viewport={"width": 1920, "height": 1080},
                locale="zh-CN",
            )
            page = context.new_page()
            page.add_init_script(_anti_detect_script())

            downloads: list[Download] = []
            page.on("download", lambda d: downloads.append(d))

            # 1. Navigate to hellotik
            logger.info("正在访问 hellotik.app ...")
            page.goto(
                "https://www.hellotik.app/zh/douyin",
                wait_until="networkidle",
                timeout=30_000,
            )
            page.wait_for_timeout(2000)

            # 2. Fill in the URL
            logger.info("正在填写抖音链接 ...")
            input_el = page.wait_for_selector(
                SELECTORS["url_input"],
                timeout=10_000,
            )
            if not input_el:
                raise RuntimeError("未找到输入框元素")
            input_el.click()
            page.wait_for_timeout(300)
            input_el.fill(douyin_url.strip())
            page.wait_for_timeout(500)

            # 3. Click parse button
            logger.info("正在解析视频 ...")
            parse_btn = page.wait_for_selector(
                SELECTORS["parse_btn"],
                timeout=10_000,
            )
            if not parse_btn:
                raise RuntimeError("未找到解析按钮")
            parse_btn.click()
            page.wait_for_timeout(5000)

            # 4. Pick resolution (optional)
            _pick_resolution(page)
            page.wait_for_timeout(2000)

            # 5. Download
            logger.info("正在下载视频 ...")
            download_btn = page.wait_for_selector(
                SELECTORS["download_btn"],
                timeout=10_000,
            )
            if not download_btn:
                raise RuntimeError("未找到下载按钮")

            with page.expect_download(timeout=60_000) as download_info:
                download_btn.click()
            download = download_info.value

            timestamp = int(time.time() * 1000)
            filename = f"douyin_video_{timestamp}.mp4"
            save_path = output_path / filename
            download.save_as(str(save_path))
            downloaded_file = save_path
            logger.info("视频已保存: %s", save_path)

    except Exception as e:
        raise RuntimeError(f"下载失败: {e}") from e
    finally:
        if browser:
            try:
                browser.close()
            except Exception:
                pass

    if not downloaded_file:
        raise RuntimeError("下载未产生任何文件")

    return downloaded_file


def download_from_share_text(
    share_text: str,
    output_dir: str | Path = "./downloads",
    *,
    headless: bool = False,
    timeout: int = 120,
) -> Path:
    """
    从抖音分享文本中提取链接并下载视频。

    直接传入完整的分享文本（如 "8.20 复制打开抖音，看看【作者】... https://v.douyin.com/xxx/"），
    函数自动提取链接后下载。

    Args:
        share_text: 包含抖音链接的分享文本
        output_dir: 下载保存目录
        headless: 是否无头模式
        timeout: 超时秒数

    Returns:
        下载视频文件的绝对路径

    Raises:
        ValueError: 文本中未找到抖音链接
    """
    url = extract_douyin_url(share_text)
    if not url:
        raise ValueError("文本中未找到有效的抖音链接")
    return download_video(url, output_dir, headless=headless, timeout=timeout)


def extract_douyin_url(text: str) -> Optional[str]:
    """
    从文本中提取抖音分享链接。

    支持多种格式：
    - https://v.douyin.com/xxx/
    - https://www.douyin.com/video/xxx
    - 短链 https://v.douyin.com/xxx

    Args:
        text: 包含抖音链接的文本

    Returns:
        提取到的第一个抖音链接，未找到返回 None
    """
    patterns = [
        r"https?://v\.douyin\.com/\S+",
        r"https?://www\.douyin\.com/video/\d+",
        r"https?://www\.iesdouyin\.com/share/video/\d+",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            url = match.group(0).rstrip("/")
            return url
    return None


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    test_text = (
        '8.20 复制打开抖音，看看【晓二浅谈的作品】'
        '没有调查就没有发言权，这句话到底有多恐怖？'
        'https://v.douyin.com/0iyoxiWn1Bc/'
    )

    result = download_from_share_text(test_text, "./downloads", headless=False)
    print(f"视频已下载到: {result}")
