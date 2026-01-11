# 部署指南

## 前后端一体化部署

本项目采用前后端一体化部署方案，前端构建产物集成到 Python 后端中。

### 项目结构

```
pyst/
├── react-frontend/          # 前端项目
│   ├── src/
│   ├── vite.config.ts       # 配置输出到 ../templates
│   └── package.json
├── templates/               # 前端构建产物（自动生成）
│   ├── index.html
│   └── assets/
├── app.py                   # Flask 应用
├── Dockerfile               # Docker 构建文件
├── docker-compose.yml       # Docker Compose 配置
└── pyproject.toml
```

### 部署步骤

#### 方式 1：使用 Docker Compose（推荐）

```bash
# 1. 构建并启动应用
docker-compose up -d

# 2. 查看日志
docker-compose logs -f pyst

# 3. 停止应用
docker-compose down
```

#### 方式 2：使用 Docker 命令

```bash
# 1. 构建镜像
docker build -t pyst:latest .

# 2. 运行容器
docker run -d \
  --name pyst-app \
  -p 5000:5000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/stock_data.db:/app/stock_data.db \
  pyst:latest

# 3. 查看日志
docker logs -f pyst-app

# 4. 停止容器
docker stop pyst-app
docker rm pyst-app
```

### 访问应用

部署完成后，访问：
- **Web 应用**：http://localhost:5000
- **API 接口**：http://localhost:5000/api/stocks/both

### 构建过程说明

Dockerfile 采用多阶段构建：

1. **前端构建阶段**：
   - 使用 Node.js 18 Alpine 镜像
   - 安装前端依赖
   - 执行 `pnpm build`，输出到 `templates` 目录

2. **后端运行阶段**：
   - 使用 Python 3.12 镜像
   - 安装 Python 依赖
   - 复制前端构建产物到 `templates` 目录
   - 启动 Gunicorn 服务器

### 环境变量

在 `docker-compose.yml` 中可以配置：

```yaml
environment:
  - FLASK_ENV=production
  - PYTHONUNBUFFERED=1
  - TZ=Asia/Shanghai
```

### 数据持久化

应用数据存储在以下位置：

- `./data/` - 数据文件目录
- `./stock_data.db` - SQLite 数据库文件

这些目录通过 Docker volumes 挂载，确保容器重启后数据不丢失。

### 健康检查

Docker Compose 配置了健康检查，每 30 秒检查一次应用是否正常运行。

### 常见问题

**Q: 如何修改前端代码？**
A: 修改 `react-frontend/src` 中的代码，然后重新构建：
```bash
docker-compose down
docker-compose up -d --build
```

**Q: 如何查看应用日志？**
A: 使用 `docker-compose logs -f pyst` 查看实时日志

**Q: 如何访问数据库？**
A: 数据库文件位于 `./stock_data.db`，可以使用 SQLite 工具打开

### 性能优化

- 使用 Gunicorn 作为 WSGI 服务器
- 前端资源通过 Flask 静态文件服务
- 启用了 CORS 支持跨域请求
- 配置了定时任务自动刷新数据

