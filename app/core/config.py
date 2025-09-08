import os

MODE = os.environ.get('MODE', 'argo')  # argo 或 direct
ENABLE_ARGO = MODE.lower() == 'argo'

# 公共
FILE_PATH = os.environ.get('FILE_PATH', './tmp')
# Cloud Foundry 注入的端口
PORT = int(os.environ.get('PORT', '3000'))

UUID = os.environ.get('UUID', '')
XRAY_PORT = int(os.environ.get('XRAY_PORT', '3001'))
DOMAIN = os.environ.get('DOMAIN', '')

FAKE_SNI = os.environ.get('FAKE_SNI', '')
SUB_PATH = os.environ.get("SUB_PATH", "/api/sub")
SUB_TOKEN = os.environ.get("SUB_TOKEN", "")

# Argo 模式
ARGO_TOKEN = os.environ.get('ARGO_TOKEN', '')

WSSUB_PATH = {
    "vless": "/rtfcast",
    "vless-argo": "/dfcast",
    "vmess-argo": "/mlfcast"
}
