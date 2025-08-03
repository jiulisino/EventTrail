# 来龙去脉事件追踪器

一个帮助用户高效追踪事件完整过程及后续动态的Web应用。

## 项目结构

```
EventTrail/
├── backend/                 # 后端Flask应用
│   ├── app.py              # Flask主应用
│   ├── config.py           # 配置文件
│   ├── models.py           # 数据模型
│   ├── routes/             # 路由模块
│   │   ├── __init__.py
│   │   ├── auth.py         # 用户认证路由
│   │   ├── events.py       # 事件相关路由
│   │   └── favorites.py    # 收藏功能路由
│   ├── services/           # 业务逻辑服务
│   │   ├── __init__.py
│   │   ├── coze_service.py # 扣子平台工作流调用
│   │   └── sms_service.py  # 短信验证码服务
│   ├── utils/              # 工具函数
│   │   ├── __init__.py
│   │   └── database.py     # 数据库工具
│   └── requirements.txt    # Python依赖
├── frontend/               # 前端Vue3应用
│   ├── public/
│   ├── src/
│   │   ├── components/     # Vue组件
│   │   ├── views/          # 页面视图
│   │   ├── router/         # 路由配置
│   │   ├── store/          # 状态管理
│   │   ├── utils/          # 工具函数
│   │   ├── App.vue         # 根组件
│   │   └── main.js         # 入口文件
│   ├── package.json        # Node.js依赖
│   └── vite.config.js      # Vite配置
└── docs/                   # 项目文档
    ├── 来龙去脉软件开发文档.md
    └── 扣子平台工作流调用说明.md
```

## 技术栈

### 后端
- Python 3.8+
- Flask 2.3+
- SQLite
- 扣子(coze)工作流API

### 前端
- Vue 3
- Element Plus
- Vue Router
- Axios

## 快速开始

### 后端启动

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

### 前端启动

```bash
cd frontend
npm install
npm run dev
```

## 功能特性

1. **事件信息查询**：输入事件名称，自动搜索相关新闻并分析事件要素
2. **事件收藏**：登录用户可收藏感兴趣的事件
3. **动态更新**：定时检查收藏事件的最新进展
4. **用户系统**：手机号注册登录，短信验证码验证

## API文档

### 事件相关API

- `POST /api/events/search` - 搜索事件
- `POST /api/events/analyze` - 分析事件
- `GET /api/events/news` - 获取新闻列表

### 用户认证API

- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/send-code` - 发送验证码

### 收藏功能API

- `GET /api/favorites` - 获取收藏列表
- `POST /api/favorites` - 添加收藏
- `DELETE /api/favorites/<id>` - 删除收藏
- `POST /api/favorites/<id>/refresh` - 刷新事件进展 