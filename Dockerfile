# Build stage
FROM node:16-alpine as build-stage
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .

# Create a tsconfig.json file from jsconfig.json
RUN if [ -f jsconfig.json ] && [ ! -f tsconfig.json ]; then \
    cp jsconfig.json tsconfig.json; \
    fi

# Make vue.config.js not require typescript checking
RUN echo "module.exports = { transpileDependencies: true, parallel: false, chainWebpack: config => config.plugins.delete('fork-ts-checker') }" > vue.config.js.tmp && \
    cat vue.config.js >> vue.config.js.tmp && \
    mv vue.config.js.tmp vue.config.js

RUN npm run build

# Production stage
FROM nginx:stable-alpine as production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
