import os
import uuid

MODE = os.environ.get('MODE', 'direct')  # argo 或 direct
ENABLE_ARGO = MODE.lower() == 'argo'

# 公共
FILE_PATH = os.environ.get('FILE_PATH', os.path.join(os.getcwd(), 'static'))
try:
    os.makedirs(FILE_PATH, exist_ok=True)  # 确保目录存在
    print(f"文件下载目录：{os.path.abspath(FILE_PATH)}")
    test_file = os.path.join(FILE_PATH, '.write_test')
    with open(test_file, 'w') as f:
        f.write('test')
    os.remove(test_file)
except Exception:
    FILE_PATH = '/tmp'
    print("[警告] 无法写入文件，使用默认路径 /tmp")

PUBLIC_DIR = os.environ.get('PUBLIC_DIR', os.path.join(FILE_PATH, 'public'))
try:
    os.makedirs(PUBLIC_DIR, exist_ok=True)  # 确保目录存在
except Exception as e:
    print(f"[警告] 创建公共目录失败: {e}")

# 平台注入的端口
PORT = int(os.environ.get('PORT', '8080'))

# 自定义的内部 FastAPI 端口，供 Caddy 反代使用
WEB_PORT = int(os.environ.get('WEB_PORT', '3000'))

UUID = os.environ.get('UUID', '')
if not UUID:
    UUID = str(uuid.uuid4())
    print(f"[提示] 未配置 UUID，已自动生成: {UUID}")

XRAY_PORT = int(os.environ.get('XRAY_PORT', '11086'))
DOMAIN = os.environ.get('DOMAIN', '')

FAKE_SNI = os.environ.get('FAKE_SNI', '')
SUB_PATH = os.environ.get("SUB_PATH", "/api/sub")
SUB_TOKEN = os.environ.get("SUB_TOKEN", "")

# Argo 模式
ARGO_TOKEN = os.environ.get('ARGO_TOKEN', '')

WS_PATH = "/nextcdn"  # WebSocket 路径，供 Caddy 反代 Xray 使用
XHTTP_PATH = "/gotocdn"  # XHTTP 路径，供 Caddy 反代 Xray 使用
