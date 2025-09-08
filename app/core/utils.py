import os
import shutil
import platform
import requests
from zipfile import ZipFile

from .config import FILE_PATH


def ensure_directory():
    """确保 FILE_PATH 目录存在"""
    os.makedirs(FILE_PATH, exist_ok=True)
    print(f"工作目录：{os.path.abspath(FILE_PATH)}")


def clean_old_files():
    """删除上次运行生成的文件"""
    for f in ('config.json', 'sub.txt', 'xray.zip', 'xray', 'cloudflared'):
        path = os.path.join(FILE_PATH, f)
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
        except OSError:
            pass


def detect_architecture():
    """返回 'amd' 或 'arm'"""
    arch = platform.machine().lower()
    return 'arm' if 'arm' in arch else 'amd'


def download_url_to_file(url, dest):
    """流式下载文件到本地"""
    resp = requests.get(url, stream=True, timeout=30)
    resp.raise_for_status()
    with open(dest, 'wb') as f:
        for chunk in resp.iter_content(8192):
            f.write(chunk)


def download_xray():
    """
    下载并解压 Xray-core
    官方 ZIP 包路径：
      - amd: Xray-linux-64.zip
      - arm: Xray-linux-arm64.zip
    """
    arch = detect_architecture()
    base = "https://github.com/XTLS/Xray-core/releases/latest/download"
    name = "Xray-linux-arm64.zip" if arch == 'arm' else "Xray-linux-64.zip"
    url = f"{base}/{name}"
    zip_path = os.path.join(FILE_PATH, "xray.zip")
    print(f"下载 Xray: {url}")
    download_url_to_file(url, zip_path)

    # 解压 xray 可执行文件
    with ZipFile(zip_path, 'r') as z:
        z.extract('xray', FILE_PATH)
    os.chmod(os.path.join(FILE_PATH, 'xray'), 0o755)
    os.remove(zip_path)
    print("Xray 下载并解压完成")


def download_cloudflared():
    """
    下载 Cloudflared 官方二进制：
      - amd64: cloudflared-linux-amd64
      - arm64: cloudflared-linux-arm64
    """
    arch = detect_architecture()
    base = "https://github.com/cloudflare/cloudflared/releases/latest/download"
    filename = "cloudflared-linux-arm64" if arch == 'arm' else "cloudflared-linux-amd64"
    url = f"{base}/{filename}"
    dest = os.path.join(FILE_PATH, "cloudflared")
    print(f"下载 cloudflared: {url}")
    download_url_to_file(url, dest)
    os.chmod(dest, 0o755)
    print("cloudflared 下载完成")
