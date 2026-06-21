# ============ 前端构建阶段 ============
FROM node:22-alpine AS frontend-builder

WORKDIR /app/react-frontend

# ---------- 配置国内 npm 镜像并安装 pnpm ----------
# 直接走 npmmirror 安装，避免 corepack 走默认 registry.npmjs.org 在国内被拦截
# 固定 pnpm 9（lockfile v9.0），避免 pnpm 10 对 ignored build scripts 报错退出
RUN npm config set registry https://registry.npmmirror.com && \
    npm install -g pnpm@9 && \
    pnpm config set registry https://registry.npmmirror.com

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
