from flask import Blueprint

# 创建一个蓝图对象，名字为 'admin'，并将其与当前模块关联
admin_bp = Blueprint('admin', __name__)

# 导入 views.py 中的路由和视图函数
from . import views

