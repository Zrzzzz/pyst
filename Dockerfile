# ============ 前端构建阶段 ============
FROM node:18-alpine as frontend-builder
WORKDIR /app/react-frontend

# 复制前端代码
COPY react-frontend .

# 安装依赖并构建
RUN pnpm install && pnpm build


# ============ 后端运行阶段 ============
FROM astral/uv:python3.12-bookworm-slim
WORKDIR /app

# 设置时区为Shanghai
RUN apt-get update && apt-get install -y tzdata && \
    ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

ENV UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TZ=Asia/Shanghai

# 复制 Python 依赖配置
COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev

# 复制后端代码
COPY . .

# 复制前端构建产物到 templates 目录
COPY --from=frontend-builder /app/react-frontend/templates ./templates

# 暴露端口
EXPOSE 5000

# 启动应用
CMD ["uv", "run", "gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
