import os
import json

from .config import (FILE_PATH, UUID, WSSUB_PATH, XRAY_PORT, MODE)


def generate_config():
    """
    生成 VLESS + WebSocket 入站配置
    TLS 由 Cloudflare 边缘负责
    """
    if MODE == 'direct':
        listen_port = XRAY_PORT
        listen_host = "0.0.0.0"
    else:
        listen_port = XRAY_PORT
        listen_host = "127.0.0.1"

    cfg = {
        "log": {
            "loglevel": "none"
        },
        "inbounds": [{
            "port": listen_port,
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
                    "path": WSSUB_PATH["vless-argo"]
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

    print(f"Xray 监听地址：{listen_host}:{listen_port}")
    print(f"Xray 配置已写入：{path}")
