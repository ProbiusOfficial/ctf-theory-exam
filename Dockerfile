FROM python:3.12-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 赋予 entrypoint 执行权限
RUN chmod +x docker-entrypoint.sh

# 暴露端口
EXPOSE 5000

# 使用 entrypoint 处理 FLAG
ENTRYPOINT ["./docker-entrypoint.sh"]
