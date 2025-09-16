# fastapi-xray

## 项目简介
本项目基于 FastAPI 构建，集成 Xray 节点管理、Cloudflared 隧道检测、热点博客自动生成及订阅服务。

## 目录结构
```
app/
├── main.py         # FastAPI 应用入口
├── api/            # 路由模块
├── core/           # 业务逻辑/工具
```

## 快速启动

1. 安装依赖
   ```bash
   pip install -r requirements.txt
   ```

2. 启动服务
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 3000
   ```

3. 访问首页
   ```
   http://localhost:3000/
   ```

4. 订阅地址
   ```
   http://localhost:3000{SUB_PATH}
   ```

## 主要功能
- Xray 节点配置与检测
- Cloudflared 隧道检测
- 热点博客自动生成
- 订阅链接生成与校验

## 贡献与许可
欢迎提交 issue 或 PR。请遵循 MIT 许可协议。
