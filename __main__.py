"""url2video CLI entry point — python -m url2video "share_text_or_url" """

import argparse
import logging
import sys

from .downloader import download_from_share_text, extract_douyin_url


def main() -> None:
    parser = argparse.ArgumentParser(
        description="抖音无水印视频下载器 — Download Douyin videos without watermark",
    )
    parser.add_argument(
        "text",
        help="抖音分享文本或视频链接",
    )
    parser.add_argument(
        "-o", "--output",
        default="./downloads",
        help="下载保存目录 (default: ./downloads)",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="无头模式运行浏览器（不显示窗口）",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=120,
        help="超时秒数 (default: 120)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="显示详细日志",
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    # 检查文本中是否包含链接
    url = extract_douyin_url(args.text)
    if not url:
        print("错误: 文本中未找到抖音链接")
        print("示例链接格式: https://v.douyin.com/xxx/")
        sys.exit(1)

    print(f"检测到链接: {url}")
    print(f"输出目录: {args.output}")
    print(f"无头模式: {'是' if args.headless else '否'}")
    print()

    try:
        path = download_from_share_text(
            args.text,
            output_dir=args.output,
            headless=args.headless,
            timeout=args.timeout,
        )
        print(f"\n✅ 下载完成: {path}")
    except Exception as e:
        print(f"\n❌ 下载失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
