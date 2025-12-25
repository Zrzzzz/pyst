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

COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev

COPY . .

CMD ["uv", "run", "gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
