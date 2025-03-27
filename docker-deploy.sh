#!/bin/bash
# Script to build and deploy mi-app Docker container

# 显示命令执行过程
set -x

# 退出时显示错误
set -e

echo "======= 开始Docker部署Mi-App (Vue.js前端应用) ======="

# 确保在mi-app目录
cd "$(dirname "$0")"

# 询问部署模式
echo "请选择部署模式:"
echo "1) 构建并启动容器"
echo "2) 仅构建镜像"
echo "3) 停止并移除容器"
read -p "请选择 (1/2/3): " deploy_mode

case $deploy_mode in
  1)
    # 构建并启动
    echo "正在构建并启动Mi-App容器..."
    docker-compose up --build -d
    echo "Mi-App容器已启动!"
    
    # 显示容器信息
    echo "容器信息:"
    docker-compose ps
    
    # 获取本地IP地址
    SERVER_IP=$(hostname -I | awk '{print $1}')
    echo "您可以通过以下地址访问应用:"
    echo "http://localhost:9051"
    echo "http://${SERVER_IP}:9051"
    ;;
    
  2)
    # 仅构建镜像
    echo "正在构建Mi-App Docker镜像..."
    docker-compose build
    echo "Mi-App Docker镜像构建完成!"
    
    # 显示镜像信息
    echo "镜像信息:"
    docker images | grep mi-app
    ;;
    
  3)
    # 停止并移除容器
    echo "正在停止并移除Mi-App容器..."
    docker-compose down
    echo "Mi-App容器已停止并移除!"
    ;;
    
  *)
    echo "无效的选择!"
    exit 1
    ;;
esac

echo "======= Mi-App Docker操作完成 ======="
