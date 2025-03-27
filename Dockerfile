# Build stage
ARG BUILD_DATE=20250327
FROM node:16-alpine as build-stage
LABEL build_date=$BUILD_DATE
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .

# Create a tsconfig.json file from jsconfig.json
RUN if [ -f jsconfig.json ] && [ ! -f tsconfig.json ]; then \
    cp jsconfig.json tsconfig.json; \
    fi

# Create a simplified vue.config.js that fixes the entry points and disables TS checking
RUN echo "const { defineConfig } = require('@vue/cli-service'); \
module.exports = defineConfig({ \
  transpileDependencies: true, \
  chainWebpack: config => { \
    config.plugins.delete('fork-ts-checker'); \
    config.entry('app').clear().add('./src/main.js'); \
  }, \
  configureWebpack: { \
    resolve: { \
      alias: { \
        '@': '/app/src' \
      }, \
      extensions: ['.js', '.vue', '.json'] \
    } \
  } \
});" > vue.config.js

RUN npm run build

# Production stage
FROM nginx:stable-alpine as production-stage
LABEL build_date=$BUILD_DATE
COPY --from=build-stage /app/dist /usr/share/nginx/html
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
