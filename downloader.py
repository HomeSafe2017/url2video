from pickle import TRUE
import re
import os
import time
import requests
from pathlib import Path
from typing import Optional
from playwright.sync_api import sync_playwright, Page, Browser, Download


def extract_douyin_url(text: str) -> Optional[str]:
    """
    从文本中提取抖音分享链接
    
    Args:
        text: 包含抖音链接的文本，如 "8.20 复制打开抖音... https://v.douyin.com/xxx/"
    
    Returns:
        提取到的抖音链接，如果未找到则返回 None
    """
    return text
    patterns = [
        r'https?://v\.douyin\.com/[A-Za-z0-9]+/?',
        r'https?://www\.douyin\.com/video/\d+',
        r'https?://www\.iesdouyin\.com/share/video/\d+',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    
    return None


def download_video_with_hellotik(
    douyin_url: str, 
    output_dir: str,
    timeout: int = 120,
    headless: bool = False
) -> str:
    """
    使用 hellotik.app 解析并下载抖音视频
    
    Args:
        douyin_url: 抖音视频链接
        output_dir: 输出目录
        timeout: 超时时间(秒)
        headless: 是否无头模式运行浏览器
    
    Returns:
        下载视频的本地路径
    """
    os.makedirs(output_dir, exist_ok=True)
    output_dir = os.path.abspath(output_dir)
    
    downloaded_file = None
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-infobars',
                '--no-sandbox',
                '--disable-dev-shm-usage',
            ]
        )
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            accept_downloads=True,
            viewport={'width': 1920, 'height': 1080},
            locale='zh-CN',
        )
        page = context.new_page()
        
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        downloads = []
        
        def handle_download(download: Download):
            downloads.append(download)
        
        page.on('download', handle_download)
        
        try:
            page.goto('https://www.hellotik.app/zh/douyin', wait_until='networkidle', timeout=30000)
            
            time.sleep(2)
            
            input_element = page.query_selector('input[placeholder*="抖音"]')
            if not input_element:
                input_element = page.query_selector('input[type="text"]')
            
            if not input_element:
                raise RuntimeError("未找到输入框")
            
            input_element.click()
            time.sleep(0.3)
            input_element.fill(douyin_url)
            time.sleep(0.5)
            
            parse_btn = page.query_selector('button:has-text("解析")')
            if not parse_btn:
                parse_btn = page.query_selector('button:has-text("解析视频")')
            
            if parse_btn:
                parse_btn.click()
            else:
                raise RuntimeError("未找到解析按钮")
            
            time.sleep(5)
            
            resolution_btns = page.query_selector_all('button')
            for btn in resolution_btns:
                text = btn.inner_text().strip()
                if re.match(r'^\d+p$', text):
                    print(f"找到分辨率按钮: {text}")
                    btn.click()
                    time.sleep(2)
                    break
            
            time.sleep(2)
            
            download_btn = page.query_selector('button:has-text("下载无水印视频")')
            if not download_btn:
                download_btn = page.query_selector('button:has-text("下载视频")')
            if not download_btn:
                download_btn = page.query_selector('button:has-text("下载")')
            
            if download_btn:
                print("点击下载按钮...")
                with page.expect_download(timeout=60000) as download_info:
                    download_btn.click()
                download = download_info.value
                
                timestamp = int(time.time() * 1000)
                filename = f"douyin_video_{timestamp}.mp4"
                output_path = os.path.join(output_dir, filename)
                
                download.save_as(output_path)
                downloaded_file = output_path
                print(f"视频已保存: {output_path}")
            
            browser.close()
            
        except Exception as e:
            browser.close()
            raise RuntimeError(f"解析视频失败: {str(e)}")
        
        if not downloaded_file:
            raise RuntimeError("无法下载视频")
        
        return downloaded_file


def download_douyin_video(
    text: str, 
    output_dir: str = "./downloads",
    timeout: int = 200,
    headless: bool = True
) -> str:
    """
    从包含抖音链接的文本中解析并下载视频
    
    Args:
        text: 包含抖音链接的文本，如 "8.20 复制打开抖音，看看【晓二浅谈的作品】... https://v.douyin.com/xxx/"
        output_dir: 输出目录，默认为 "./downloads"
        timeout: 超时时间(秒)，默认 120 秒
        headless: 是否无头模式运行浏览器，默认 False
    
    Returns:
        下载视频的本地路径
    
    Raises:
        ValueError: 文本中未找到有效的抖音链接
        RuntimeError: 下载过程中发生错误
    
    Example:
        >>> text = "8.20 复制打开抖音，看看【晓二浅谈的作品】没有调查就没有发言权 https://v.douyin.com/xxx/"
        >>> video_path = download_douyin_video(text, "./videos")
        >>> print(video_path)
        ./videos/douyin_video_1234567890.mp4
    """
    douyin_url = extract_douyin_url(text)
    if not douyin_url:
        raise ValueError("文本中未找到有效的抖音链接")
    
    output_dir = os.path.abspath(output_dir)
    
    return os.path.abspath(download_video_with_hellotik(douyin_url, output_dir, timeout, headless))


if __name__ == "__main__":
    test_text = '8.20 复制打开抖音，看看【晓二浅谈的作品】没有调查就没有发言权，这句话到底有多恐怖？ # 寻... https://v.douyin.com/0iyoxiWn1Bc/ QkC:/ F@H.ip 11/10'
    
    result = download_douyin_video(test_text, "./downloads")
    print(f"视频已下载到: {result}")
