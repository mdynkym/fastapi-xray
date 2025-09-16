import os
import shutil
import platform
import requests

import platform
import shutil
import urllib.request
import stat
import tarfile
import tempfile

from zipfile import ZipFile
import json

from .config import (FILE_PATH, UUID, XRAY_PORT, MODE, PORT, WS_PATH,
                     XHTTP_PATH, WEB_PORT)


def clean_old_config():
    """删除上次运行生成的文件"""
    for f in ('config.json', 'sub.txt', 'Caddyfile'):
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
    dest = os.path.join(FILE_PATH, "xray")
    if os.path.exists(dest):
        print(f"xray 已存在: {dest}")
        return

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
    os.chmod(dest, 0o755)
    os.remove(zip_path)
    print("Xray 下载并解压完成")


def download_cloudflared():
    """
    下载 Cloudflared 官方二进制：
      - amd64: cloudflared-linux-amd64
      - arm64: cloudflared-linux-arm64
    """
    dest = os.path.join(FILE_PATH, "cloudflared")
    if os.path.exists(dest):
        print(f"cloudflared 已存在: {dest}")
        return
    arch = detect_architecture()
    base = "https://github.com/cloudflare/cloudflared/releases/latest/download"
    filename = "cloudflared-linux-arm64" if arch == 'arm' else "cloudflared-linux-amd64"
    url = f"{base}/{filename}"

    print(f"下载 cloudflared: {url}")
    download_url_to_file(url, dest)
    os.chmod(dest, 0o755)
    print("cloudflared 下载完成")


def download_caddy():
    """
    自动下载 caddy 二进制文件
    """
    caddy_path = os.path.join(FILE_PATH, "caddy")
    if os.path.exists(caddy_path):
        print(f"Caddy 已存在: {caddy_path}")
        return
    system = platform.system().lower()
    arch = platform.machine().lower()
    if arch in ("x86_64", "amd64"):
        arch = "amd64"
    elif arch in ("aarch64", "arm64"):
        arch = "arm64"
    else:
        raise RuntimeError(f"不支持的架构: {arch}")
    if system == "linux":
        # 获取最新版本号
        api_url = "https://api.github.com/repos/caddyserver/caddy/releases/latest"
        resp = requests.get(api_url, timeout=10)
        resp.raise_for_status()
        latest_tag = resp.json()["tag_name"].lstrip("v")
        url = f"https://github.com/caddyserver/caddy/releases/download/v{latest_tag}/caddy_{latest_tag}_{system}_{arch}.tar.gz"
    else:
        raise RuntimeError(f"不支持的系统: {system}")
    print(f"下载 Caddy: {url}")

    with tempfile.TemporaryDirectory() as tmpdir:
        tgz_path = os.path.join(tmpdir, "caddy.tar.gz")
        urllib.request.urlretrieve(url, tgz_path)
        with tarfile.open(tgz_path, "r:gz") as tar:
            tar.extractall(tmpdir)
        for fname in os.listdir(tmpdir):
            if fname == "caddy":
                shutil.move(os.path.join(tmpdir, fname), caddy_path)
                os.chmod(caddy_path,
                         os.stat(caddy_path).st_mode | stat.S_IEXEC)
                print(f"Caddy 下载完成: {caddy_path}")
                return
    raise RuntimeError("Caddy 下载失败")


def generate_xray_config():
    """
    生成 VLESS + WebSocket 入站配置
    TLS 由 Cloudflare 边缘负责
    """
    if MODE == 'direct':
        listen_host = "0.0.0.0"
    else:
        listen_host = "127.0.0.1"

    cfg = {
        "log": {
            "loglevel": "none"
        },
        "inbounds": [{
            "port": XRAY_PORT,
            "listen": listen_host,
            "protocol": "vless",
            "settings": {
                "clients": [{
                    "id": UUID
                }],
                "decryption": "none"
            },
            "streamSettings": {
                "network": "ws",
                "security": "none",
                "wsSettings": {
                    "path": WS_PATH
                }
            }
        }, {
            "port": XRAY_PORT + 1,
            "listen": listen_host,
            "protocol": "vless",
            "settings": {
                "clients": [{
                    "id": UUID
                }],
                "decryption": "none"
            },
            "streamSettings": {
                "network": "xhttp",
                "security": "none",
                "xhttpSettings": {
                    "path": XHTTP_PATH
                }
            }
        }],
        "dns": {
            "servers": ["https+local://8.8.8.8/dns-query"]
        },
        "outbounds": [{
            "protocol": "freedom"
        }]
    }
    path = os.path.join(FILE_PATH, 'config.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)

    print(f"Xray 监听地址：{listen_host}:{XRAY_PORT}")
    print(f"Xray 配置已写入：{path}")


def generate_caddyfile():
    """
    生成 Caddyfile 配置，反代 FastAPI 和 Xray WebSocket
    """
    caddyfile = f"""
{{
    auto_https off
}}

:{PORT} {{
    encode gzip
    @ws_path {{
        path {WS_PATH}
    }}
    reverse_proxy @ws_path 127.0.0.1:{XRAY_PORT}
    @xhttp_path {{  
        path {XHTTP_PATH}
    }}
    reverse_proxy @xhttp_path 127.0.0.1:{XRAY_PORT+1}
    reverse_proxy /api/* 127.0.0.1:{WEB_PORT}
    reverse_proxy / 127.0.0.1:{WEB_PORT}
}}
"""
    caddyfile_path = os.path.join(FILE_PATH, "Caddyfile")
    with open(caddyfile_path, "w", encoding="utf-8") as f:
        f.write(caddyfile)
    print(f"Caddyfile 已生成: {caddyfile_path}")
