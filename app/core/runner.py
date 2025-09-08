import os
import time
import subprocess

from .config import FILE_PATH, ENABLE_ARGO, ARGO_TOKEN
from .utils import download_xray, download_cloudflared


def run_xray():
    """后台启动 Xray 核心"""
    bin_path = os.path.join(FILE_PATH, 'xray')
    cmd = f"nohup {bin_path} -c {os.path.join(FILE_PATH,'config.json')} >/dev/null 2>&1 &"
    subprocess.Popen(cmd, shell=True)
    time.sleep(1)
    print("Xray 已启动")


def run_cloudflared():
    """使用 cloudflared Tunnel run --token 启动 Argo 隧道"""
    log = os.path.join(FILE_PATH, 'cloudflared.log')
    bin_path = os.path.join(FILE_PATH, 'cloudflared')
    cmd = (
        f"nohup {bin_path} tunnel --loglevel warn --logfile {log}  run --protocol http2 --token {ARGO_TOKEN} "
    )
    subprocess.Popen(cmd, shell=True)
    print(f"cloudflared 隧道启动中，日志写入：{log}")


def authorize_and_run():
    """
    1. 下载并授权 xray 与 cloudflared
    2. 启动 Xray；如启用 Argo，则启动 cloudflared
    """
    download_xray()
    if ENABLE_ARGO and ARGO_TOKEN:
        download_cloudflared()

    run_xray()
    if ENABLE_ARGO and ARGO_TOKEN:
        run_cloudflared()
