#!/bin/bash

echo "========================================"
echo "来龙去脉事件追踪器启动脚本"
echo "========================================"

echo ""
echo "正在启动后端服务..."

cd backend

# 检查虚拟环境是否存在
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

echo "安装依赖..."
pip install -r requirements.txt

echo "启动后端服务..."
python app.py &
BACKEND_PID=$!

echo ""
echo "等待后端服务启动..."
sleep 5

echo ""
echo "正在启动前端服务..."

cd ../frontend

# 检查node_modules是否存在
if [ ! -d "node_modules" ]; then
    echo "安装前端依赖..."
    npm install
fi

echo "启动前端服务..."
npm run dev &
FRONTEND_PID=$!

echo ""
echo "========================================"
echo "服务启动完成！"
echo "后端地址: http://localhost:5000"
echo "前端地址: http://localhost:3000"
echo "========================================"
echo ""
echo "按 Ctrl+C 停止服务..."

# 等待用户中断
trap "echo '正在停止服务...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait 