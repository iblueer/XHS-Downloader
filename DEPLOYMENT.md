# XHS-Downloader 服务器部署指南

本指南介绍如何将 XHS-Downloader 部署到服务器上，以 API 模式运行。

## 目录

- [方式一：Docker 部署（推荐）](#方式一docker-部署推荐)
- [方式二：源码部署](#方式二源码部署)
- [配置说明](#配置说明)
- [API 使用示例](#api-使用示例)
- [常见问题](#常见问题)

---

## 方式一：Docker 部署（推荐）

### 1. 安装 Docker

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com | sh
sudo systemctl start docker
sudo systemctl enable docker

# CentOS
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
```

### 2. 获取镜像

**方式 A：从 Docker Hub 拉取（推荐）**

```bash
docker pull joeanamier/xhs-downloader
```

**方式 B：从 GitHub Container Registry 拉取**

```bash
docker pull ghcr.io/joeanamier/xhs-downloader
```

**方式 C：本地构建镜像**

```bash
# 克隆项目
git clone https://github.com/你的用户名/XHS-Downloader.git
cd XHS-Downloader

# 构建镜像
docker build -t xhs-downloader .
```

### 3. 创建并运行容器

**API 模式（获取作品信息和下载地址）**

```bash
docker run -d \
  --name xhs-api \
  -p 5556:5556 \
  -v xhs_data:/app/Volume \
  --restart unless-stopped \
  joeanamier/xhs-downloader python main.py api
```

**MCP 模式**

```bash
docker run -d \
  --name xhs-mcp \
  -p 5556:5556 \
  -v xhs_data:/app/Volume \
  --restart unless-stopped \
  joeanamier/xhs-downloader python main.py mcp
```

### 4. 验证部署

```bash
# 查看容器状态
docker ps

# 查看日志
docker logs xhs-api

# 测试 API
curl http://localhost:5556/docs
```

### 5. 容器管理命令

```bash
# 停止容器
docker stop xhs-api

# 启动容器
docker start xhs-api

# 重启容器
docker restart xhs-api

# 删除容器
docker rm -f xhs-api

# 查看日志（实时）
docker logs -f xhs-api
```

---

## 方式二：源码部署

### 1. 环境准备

```bash
# 安装 Python 3.12
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3-pip

# CentOS (需要先添加源)
sudo yum install -y python3.12
```

### 2. 克隆项目

```bash
git clone https://github.com/你的用户名/XHS-Downloader.git
cd XHS-Downloader
```

### 3. 创建虚拟环境

```bash
python3.12 -m venv venv
source venv/bin/activate
```

### 4. 安装依赖

```bash
pip install -r requirements.txt
```

### 5. 启动服务

**前台运行（测试用）**

```bash
python main.py api
```

**后台运行（使用 nohup）**

```bash
nohup python main.py api > xhs.log 2>&1 &
```

**使用 systemd 管理（推荐生产环境）**

创建服务文件：

```bash
sudo vim /etc/systemd/system/xhs-downloader.service
```

写入以下内容：

```ini
[Unit]
Description=XHS-Downloader API Service
After=network.target

[Service]
Type=simple
User=你的用户名
WorkingDirectory=/path/to/XHS-Downloader
ExecStart=/path/to/XHS-Downloader/venv/bin/python main.py api
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启用并启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable xhs-downloader
sudo systemctl start xhs-downloader

# 查看状态
sudo systemctl status xhs-downloader

# 查看日志
sudo journalctl -u xhs-downloader -f
```

---

## 配置说明

### 配置文件位置

- Docker 部署：容器内 `/app/Volume/settings.json`
- 源码部署：项目目录 `./Volume/settings.json`

### 主要配置项

首次运行会自动生成配置文件，主要参数：

```json
{
  "work_path": "",
  "folder_name": "Download",
  "cookie": "",
  "proxy": null,
  "timeout": 10,
  "max_retry": 5,
  "image_format": "PNG",
  "record_data": false,
  "download_record": true,
  "language": "zh_CN"
}
```

| 参数 | 说明 | 默认值 |
|-----|------|-------|
| `cookie` | 小红书 Cookie（可选，无需登录） | 空 |
| `proxy` | 代理地址，如 `http://127.0.0.1:7890` | null |
| `timeout` | 请求超时时间（秒） | 10 |
| `image_format` | 图片格式：AUTO/PNG/WEBP/JPEG/HEIC | PNG |

### 修改配置（Docker）

```bash
# 进入容器
docker exec -it xhs-api bash

# 编辑配置
vi /app/Volume/settings.json

# 退出并重启
exit
docker restart xhs-api
```

---

## API 使用示例

### 接口信息

- **地址**：`http://服务器IP:5556/xhs/detail`
- **方法**：POST
- **文档**：`http://服务器IP:5556/docs`

### 请求参数

```json
{
  "url": "小红书作品链接（必需）",
  "download": false,
  "index": null,
  "cookie": null,
  "proxy": null,
  "skip": false
}
```

### 获取作品媒体链接

**curl 示例**

```bash
curl -X POST http://localhost:5556/xhs/detail \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.xiaohongshu.com/explore/xxx?xsec_token=xxx",
    "download": false
  }'
```

**Python 示例**

```python
import requests

def get_media_links(url: str) -> dict:
    """获取作品的图片/视频/live图链接"""
    response = requests.post(
        "http://localhost:5556/xhs/detail",
        json={"url": url, "download": False},
        timeout=30
    )
    result = response.json()

    if result.get("data"):
        data = result["data"]
        return {
            "作品类型": data.get("作品类型"),
            "下载地址": data.get("下载地址", []),  # 图片或视频链接
            "动图地址": data.get("动图地址", []),  # livePhoto 链接
        }
    return {"error": result.get("message")}

# 使用
links = get_media_links("https://www.xiaohongshu.com/explore/xxx?xsec_token=xxx")
print(links)
```

### 响应示例

```json
{
  "message": "获取成功",
  "params": {
    "url": "...",
    "download": false
  },
  "data": {
    "作品ID": "xxx",
    "作品类型": "图文",
    "作品标题": "...",
    "下载地址": [
      "https://ci.xiaohongshu.com/xxx?imageView2/format/png",
      "https://ci.xiaohongshu.com/xxx?imageView2/format/png"
    ],
    "动图地址": [null, null]
  }
}
```

---

## 反向代理配置（可选）

### Nginx 配置

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5556;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_connect_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

---

## 常见问题

### Q1: 端口被占用

```bash
# 查看端口占用
lsof -i:5556

# 使用其他端口
docker run -p 8080:5556 ...
```

### Q2: 请求失败或超时

1. 检查服务器网络是否能访问小红书
2. 尝试配置代理
3. 增加 timeout 参数值

### Q3: Docker 数据持久化

数据存储在 Docker Volume 中：

```bash
# 查看 volume
docker volume ls

# 查看 volume 详情
docker volume inspect xhs_data

# 备份数据
docker cp xhs-api:/app/Volume ./backup
```

### Q4: 如何更新

**Docker 方式**

```bash
docker pull joeanamier/xhs-downloader
docker stop xhs-api
docker rm xhs-api
# 重新创建容器（使用上面的 docker run 命令）
```

**源码方式**

```bash
cd XHS-Downloader
git pull
pip install -r requirements.txt
sudo systemctl restart xhs-downloader
```

---

## 安全建议

1. **不要暴露到公网**：如需公网访问，请配置防火墙和认证
2. **使用反向代理**：通过 Nginx 添加 HTTPS 和访问控制
3. **定期更新**：保持项目和依赖更新

---

## 快速命令参考

```bash
# Docker 一键部署 API 模式
docker run -d --name xhs-api -p 5556:5556 -v xhs_data:/app/Volume --restart unless-stopped joeanamier/xhs-downloader python main.py api

# 测试接口
curl -X POST http://localhost:5556/xhs/detail -H "Content-Type: application/json" -d '{"url":"你的链接","download":false}'

# 查看 API 文档
open http://localhost:5556/docs
```
