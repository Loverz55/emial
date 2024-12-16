# 项目名称

## 项目简介
这是一个全栈Web应用项目，采用前后端分离架构。

## 技术栈
### 前端
- Vue.js - 前端框架
- JavaScript (ES6+) - 编程语言
- Node.js - 运行环境

### 后端
- Spring Boot - 后端框架
- Java 17 - 编程语言
- MySQL - 数据库
- MyBatis - ORM框架
- Redis - 缓存服务

## 项目设置
### 前置要求
#### 前端
- Node.js (推荐 v14.0.0 或更高版本)
- npm 或 yarn 包管理器

#### 后端
- JDK 17 或更高版本
- Maven 3.6+
- MySQL 8.0+
- Redis 6.0+

### 安装和运行
#### 前端
```bash
安装依赖
cd frontend
npm install
开发环境运行
npm run dev
生产环境构建
npm run build
```

#### 后端
```bash
进入后端目录
cd backend
使用Maven编译打包
mvn clean package
运行应用
java -jar target/项目名称-0.0.1-SNAPSHOT.jar
```


## 项目结构

├── frontend/ # 前端项目目录
│ ├── src/
│ │ ├── assets/ # 静态资源
│ │ ├── components/ # Vue组件
│ │ ├── views/ # 页面视图
│ │ ├── router/ # 路由配置
│ │ ├── store/ # 状态管理
│ │ └── main.js # 应用入口
│ └── package.json
│
├── backend/ # 后端项目目录
│ ├── src/
│ │ ├── main/
│ │ │ ├── java/ # Java源代码
│ │ │ └── resources/ # 配置文件
│ │ └── test/ # 测试代码
│ └── pom.xml # Maven配置文件
│
└── README.md



## 环境配置
### 后端配置
1. 创建MySQL数据库

```sql
CREATE DATABASE your_database_name;
```


2. 修改后端配置文件 `backend/src/main/resources/application.yml`：

```yaml
spring:
datasource:
url: jdbc:mysql://localhost:3306/your_database_name
username: your_username
password: your_password
redis:
host: localhost
port: 6379
```


## API文档
后端API文档访问地址：`http://localhost:8080/swagger-ui.html`

## 浏览器支持
- Chrome (最新版本)
- Firefox (最新版本)
- Safari (最新版本)
- Edge (最新版本)

## 贡献指南
1. Fork 本仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的改动 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建一个 Pull Request

## 许可证
本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情