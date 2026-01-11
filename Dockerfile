# ============ 前端构建阶段 ============
FROM node:22-alpine AS frontend-builder

WORKDIR /app/react-frontend

# ---------- 安装 pnpm（使用 corepack，官方推荐） ----------
RUN corepack enable && corepack prepare pnpm@latest --activate

# ---------- 配置国内镜像 ----------
RUN pnpm config set registry https://registry.npmmirror.com && \
    npm config set registry https://registry.npmmirror.com

# ---------- 先复制依赖清单 ----------
COPY react-frontend/package.json .
COPY react-frontend/pnpm-lock.yaml .

# ---------- 安装依赖 ----------
RUN pnpm install --frozen-lockfile --prefer-offline

# ---------- 再复制源码 ----------
COPY react-frontend .

# ---------- 构建 ----------
RUN pnpm build

# ============ 后端运行阶段 ============
FROM astral/uv:python3.12-bookworm-slim

WORKDIR /app

# ---------- 时区 ----------
RUN apt-get update && apt-get install -y tzdata && \
    ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

ENV TZ=Asia/Shanghai
ENV UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ---------- Python 依赖 ----------
COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev

# ---------- 后端代码 ----------
COPY . .

# ---------- 前端构建产物 ----------
COPY --from=frontend-builder /app/templates ./templates

EXPOSE 5000

CMD ["uv", "run", "gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
