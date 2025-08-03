chcp 65001
@echo off
echo ========================================
echo 来龙去脉事件追踪器启动脚本
echo ========================================

echo.
echo 正在启动后端服务...
cd backend
if not exist venv (
    echo 创建虚拟环境...
    python -m venv venv
)
call venv\Scripts\activate
echo 安装依赖...
pip install -r requirements.txt
echo 启动后端服务...
start "后端服务" python app.py

echo.
echo 等待后端服务启动...
timeout /t 5 /nobreak > nul

echo.
echo 正在启动前端服务...
cd ..\frontend
if not exist node_modules (
    echo 安装前端依赖...
    npm install
)
echo 启动前端服务...
start "前端服务" npm run dev

echo.
echo ========================================
echo 服务启动完成！
echo 后端地址: http://localhost:5000
echo 前端地址: http://localhost:3000
echo ========================================
echo.
echo 按任意键退出...
pause > nul 