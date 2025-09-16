import os
import time
import socket
import subprocess
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager

from app.core.config import FILE_PATH, ENABLE_ARGO, PORT, SUB_PATH, PUBLIC_DIR, XRAY_PORT
from app.core.utils import clean_old_config, generate_caddyfile, generate_xray_config
from app.core.runner import download_and_run
from app.core.links import generate_subscription

from app.core.meta import get_cf_meta, summarize_meta
from app.core.hotspot import fetch_hot_topics
from app.core.blog import render_blog_html, write_blog, write_news_pages
from app.api import news, sub


def check_xray():
    print("\n--- Xray 启动检测 ---")
    # 进程
    try:
        ps_output = subprocess.check_output(['ps', 'aux'], text=True)
        proc_ok = 'xray' in ps_output
    except Exception as e:
        print(f"[错误] 检查进程失败: {e}")
        proc_ok = False
    # 配置
    cfg_ok = False
    cfg_path = os.path.join(FILE_PATH, 'config.json')
    if os.path.exists(cfg_path):
        try:
            result = subprocess.run([
                os.path.join(FILE_PATH, 'xray'), 'run', '-test', '-c', cfg_path
            ],
                                    capture_output=True,
                                    text=True)
            cfg_ok = (result.returncode == 0)
            if not cfg_ok:
                print(f"[错误] 配置文件无效: {result.stderr.strip()}")
        except Exception as e:
            print(f"[错误] 配置检查失败: {e}")
    else:
        print("[错误] 找不到 config.json")
    # 端口
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            port_ok = sock.connect_ex(('127.0.0.1', XRAY_PORT)) == 0
    except Exception as e:
        print(f"[错误] 检查端口失败: {e}")
        port_ok = False

    print(f"XRAY进程检查: {'✅ 正常' if proc_ok else '❌ 异常'}")
    print(f"配置文件检查: {'✅ 正常' if cfg_ok else '❌ 异常'}")
    print(f"端口监听检查: {'✅ 正常' if port_ok else '❌ 异常'}")
    if proc_ok and cfg_ok and port_ok:
        print("结论: ✅ Xray 正常运行\n")
    else:
        print("结论: ❌ Xray 异常，请检查日志和配置\n")


def check_cloudflared():
    print("\n--- Cloudflared 隧道检测 ---")
    # 进程
    try:
        ps_output = subprocess.check_output(['ps', 'aux'], text=True)
        proc_ok = 'cloudflared' in ps_output
    except Exception as e:
        print(f"[错误] 检查 Cloudflared 进程失败: {e}")
        proc_ok = False

    if proc_ok:
        print("✅ 隧道已连接 Cloudflare")
    else:
        print("❌ cloudflared 可能未启动，请检查 token 或网络")


def build_and_publish_blog():
    print("\n--- 生成节点所在地热点博客 ---")
    meta_raw = get_cf_meta()
    meta = summarize_meta(meta_raw) if meta_raw else {}
    topics = fetch_hot_topics(meta.get("city"), meta.get("country"))
    # 生成 news 下的静态页面
    topics_with_pages = write_news_pages(PUBLIC_DIR, meta, topics)
    # 首页用本地链接替换原链接
    html = render_blog_html(meta, topics_with_pages)
    path = write_blog(PUBLIC_DIR, html)
    print(f"博客已生成：{path}")


# 启动初始化逻辑
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        clean_old_config()

        print("\n--- 生成配置文件 ---")
        generate_caddyfile()
        generate_xray_config()

        # 启动 Xray / cloudflared / caddy
        download_and_run()

        build_and_publish_blog()
        
        time.sleep(3)  # 给进程一点时间启动

        # 检测 Xray
        check_xray()

        # 检测 cloudflared
        if ENABLE_ARGO:
            check_cloudflared()

        # 生成订阅
        generate_subscription()

        print(f"服务已启动，访问地址: http://localhost:{PORT}")
        print(f"订阅地址: http://localhost:{PORT}{SUB_PATH}")
        print(f"(如启用令牌则需附加)?token=***")
    except Exception as e:
        print(f"[启动异常] {e}")

    yield
    # Clean and release the resources
    print(f"服务已终止")


app = FastAPI(title="FastAPI Demo",
              version="1.5.0",
              lifespan=lifespan,
              openapi_url=None,
              docs_url=None,
              redoc_url=None)

# 挂载静态文件
app.mount("/static", StaticFiles(directory=PUBLIC_DIR), name="static")

# 路由注册
app.include_router(news.router, prefix="/api/news")
app.include_router(sub.router)


# 首页和博客页面
@app.get("/")
def index():
    fp = os.path.join(PUBLIC_DIR, "index.html")
    if os.path.exists(fp):
        return FileResponse(fp, media_type="text/html")

    return {"detail": "Blog not found"}


# 运行方式（如使用 uvicorn 启动）
# uvicorn app.main:app --host 0.0.0.0 --port 3000
