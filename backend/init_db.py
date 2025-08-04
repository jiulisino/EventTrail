from app import create_app
from models import db

app = create_app()
with app.app_context():
    db.create_all()
    print('数据库初始化完成，已创建EventAnalysis表')