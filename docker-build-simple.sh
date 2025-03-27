#!/bin/bash
# Script to build the app locally and then containerize it using a simple Dockerfile

# 显示命令执行过程
set -x

# 退出时显示错误
set -e

echo "======= 开始构建并容器化 Mi-App (Vue.js前端应用) ======="

# 确保在mi-app目录
cd "$(dirname "$0")"

# 1. 本地构建应用
echo "正在本地构建应用..."
npm install
npm run build

# 检查构建是否成功
if [ ! -d "dist" ]; then
  echo "构建失败：未能生成dist目录!"
  exit 1
fi

# 2. 使用简单Dockerfile构建Docker镜像
echo "正在使用简单Dockerfile构建Docker镜像..."
docker build -t mi-app:latest -f Dockerfile.simple .

echo "3. 是否要启动容器？"
read -p "是否要启动容器? (y/n): " start_container

if [ "$start_container" = "y" ] || [ "$start_container" = "Y" ]; then
  echo "正在启动Mi-App容器..."
  docker stop mi-app 2>/dev/null || true
  docker rm mi-app 2>/dev/null || true
  docker run -d --name mi-app -p 9051:80 mi-app:latest
  
  # 等待容器启动
  echo "等待容器启动..."
  sleep 2
  
  # 显示容器信息
  echo "容器信息:"
  docker ps | grep mi-app
  
  # 获取本地IP地址
  SERVER_IP=$(hostname -I | awk '{print $1}')
  echo "您可以通过以下地址访问应用:"
  echo "http://localhost:9051"
  echo "http://${SERVER_IP}:9051"
else
  echo "跳过容器启动。您可以稍后使用以下命令手动启动:"
  echo "docker run -d --name mi-app -p 9051:80 mi-app:latest"
fi

echo "======= Mi-App 构建和容器化操作完成 ======="
