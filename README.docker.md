# Mi-App Docker 部署指南

本文档提供了使用 Docker 容器化部署 Mi-App 的详细指南。

## 项目概述

Mi-App 是一个基于 Vue.js 的前端应用，该 Docker 配置将应用打包并通过 Nginx 提供 Web 服务。

## 系统要求

- Docker
- Node.js (仅用于简单部署方式)
- npm (仅用于简单部署方式)

## 部署方式

Mi-App 提供两种 Docker 部署方式：

### 方式一：简单部署（推荐）

这种方式在本地构建应用，然后将构建好的文件打包到 Docker 容器中。这种方式更加可靠，不会遇到构建环境差异问题。

**文件结构:**
```
mi-app/
├── Dockerfile.simple    # 简单的 Nginx 容器配置
├── docker-build-simple.sh  # 简单部署脚本
└── docker/
    └── nginx.conf       # Nginx 配置
```

**快速部署:**
```bash
cd mi-app
./docker-build-simple.sh
```

该脚本会执行以下操作:
1. 在本地构建 Vue 应用
2. 使用 Dockerfile.simple 创建 Docker 镜像
3. 询问是否启动容器

### 方式二：多阶段构建

这种方式使用 Docker 多阶段构建，在 Docker 容器内完成整个应用的构建和部署过程。

**文件结构:**
```
mi-app/
├── Dockerfile           # 多阶段构建配置
├── docker-compose.yml   # Docker Compose 配置
├── docker-deploy.sh     # 部署脚本
└── docker/
    └── nginx.conf       # Nginx 配置
```

**快速部署:**
```bash
cd mi-app
./docker-deploy.sh
```

脚本会提供三个选项:
1. 构建并启动容器
2. 仅构建镜像
3. 停止并移除容器

## 手动部署步骤

如果您想手动执行部署过程，可以按以下步骤操作:

### 1. 构建 Docker 镜像

```bash
cd mi-app
docker-compose build
```

### 2. 启动容器

```bash
docker-compose up -d
```

### 3. 验证部署

打开浏览器访问:
- http://localhost:9051

### 4. 停止容器

```bash
docker-compose down
```

## 配置说明

### Docker Compose 配置

`docker-compose.yml` 配置了服务:
- 端口映射: 主机的 9051 端口映射到容器的 80 端口
- 容器自动重启: 设置为 `unless-stopped`

### Nginx 配置

`docker/nginx.conf` 中包含:
- 单页应用程序 (SPA) 路由支持
- 静态文件服务

## 常见问题解决

### 端口冲突

如果 9051 端口已被占用，可以修改 `docker-compose.yml` 文件中的端口映射:

```yml
ports:
  - "另一个端口:80"
```

### 构建失败

如果构建过程失败，通常是因为:
1. Node.js 依赖安装问题
2. 构建脚本问题

查看构建日志:
```bash
docker-compose build --no-cache
```

## 高级配置

### 自定义环境变量

通过 Docker Compose 传递环境变量:

```yml
services:
  mi-app:
    build: .
    environment:
      - NODE_ENV=production
      - API_URL=http://your-api-url
```

### 使用外部 Nginx 配置

挂载自定义 Nginx 配置:

```yml
services:
  mi-app:
    volumes:
      - ./custom-nginx.conf:/etc/nginx/conf.d/default.conf
```

## 生产环境部署建议

1. 使用特定版本的基础镜像，而不是 `latest`
2. 实现健康检查
3. 设置资源限制
4. 使用 Docker 卷实现数据持久化
5. 实现日志收集与监控
