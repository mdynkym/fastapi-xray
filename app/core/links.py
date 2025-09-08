import os
import base64
import subprocess

from .config import (FILE_PATH, UUID, DOMAIN, WSSUB_PATH, FAKE_SNI)


def generate_subscription():
    """
    生成 VLESS+WS 单一路径订阅，写入 sub.txt
    """
    # 获取网络运营商信息
    proc = subprocess.run(['curl', '-s', 'https://speed.cloudflare.com/meta'],
                          capture_output=True,
                          text=True)
    parts = proc.stdout.split('"')
    isp = f"{parts[25]}-{parts[17]}".replace(' ', '_').strip()
    # 拼接 VLESS 链接
    link_host = FAKE_SNI if FAKE_SNI else DOMAIN
    host = DOMAIN
    uri = (f"vless://{UUID}@{link_host}:443"
           f"?encryption=none&security=tls&sni={host}"
           f"&fp=chrome&type=ws&host={host}"
           f"&path={WSSUB_PATH['vless-argo']}"
           f"#VLESS-{isp}-CDN")

    # 写入 Base64 订阅文件
    b64 = base64.b64encode(uri.encode()).decode()
    path = os.path.join(FILE_PATH, 'sub.txt')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(b64)
    print("订阅 (Base64) 已生成：")
    print(b64)
