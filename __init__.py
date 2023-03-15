r"""
初始化插件
C:\userfiles\pear admin flask\venv\Scripts\python.exe
"""
import os

from flask import Flask, Blueprint
from .utils.tools import power, role

from .init_utils import blueprint as utils_blueprint
from .init_student import blueprint as student_blueprint
from .init_examPublish import blueprint as examPublish_blueprint
from .init_examAnalyse import blueprint as examAnalyse_blueprint


# 获取插件所在的目录（结尾没有分割符号）
dir_path = os.path.dirname(__file__).replace("\\", "/")
folder_name = dir_path[dir_path.rfind("/") + 1:]  # 插件文件夹名称

def register_power():
    """
    注册菜单
    """
    # 查看菜单是否已经被注册
    if len(power.Power.query.filter_by(code="SchoolManager:index").all()) == 0:
        print("SchoolManager: 未注册菜单，正在添加注册.......")
        # 注册后台管理菜单
        powerids = []

        # 注册父菜单
        p_parentId = power.add(0, "学校数据管理", 0, "layui-icon layui-icon-read", 2, True, "SchoolManager:index")
        powerids.append(p_parentId)
        
        # 注册子菜单
        # powerids.append(power.add(p_parentId, "巡段管理", 1, "", 0, True, "SchoolManager:dailyRecode", "/schoolmanager/dailyRecode"))
        powerids.append(power.add(p_parentId, "考试分析", 1, "", 1, True, "SchoolManager:examAnalyse", "/schoolmanager/examAnalyse"))
        powerids.append(power.add(p_parentId, "成绩发布", 1, "", 2, True, "SchoolManager:examPublish", "/schoolmanager/examPublish"))
        powerids.append(power.add(p_parentId, "学生管理", 1, "", 3, True, "SchoolManager:student", "/schoolmanager/student"))
        
        # 权限管理
        powerids.append(power.add(p_parentId, "文件上传", 2, "", 3, True, "SchoolManager:upload", "/"))  # 文件上传权限
        powerids.append(power.add(p_parentId, "文件读取", 2, "", 3, True, "SchoolManager:readable", "/"))  # 文件读取权限

        adminid_filterby = role.filter_by(code='admin')  # 寻找管理员权限
        power_list = role.get_power(adminid_filterby)  # 获取管理员全部权限
        power_list = power_list + powerids  # 添加访问学校管理模块权限
        role.set_power(adminid_filterby, power_list)  #  设置权限

def unregister_power():
    """
    取消注册菜单
    """
    # 取消后台菜单的注册
    for p in power.get_all():
        if 'powerCode' not in p:
            continue
        if 'SchoolManager' in p['powerCode']:
            power.delete(p['powerId'])

def event_enable():
    """当此插件被启用时会调用此处"""
    # print(f"启用插件，dir_path: {dir_path} ; folder_name: {folder_name}")
    register_power()
    

def event_disable():
    """当此插件被禁用时会调用此处"""
    # print(f"禁用插件，dir_path: {dir_path} ; folder_name: {folder_name}")
    unregister_power()


def event_init(app: Flask):
    """初始化完成时会调用这里"""
    # 绑定到 admin.index 页面（后台管理页面）
    origin_function = app.view_functions['admin.index']  # 获取原视图函数
    def new_function():
        register_power()  # 在获取后台页面之前，看看菜单是否被注册。
        return origin_function()
    app.view_functions['admin.index'] = new_function  # 拦截原识图函数

    # 注册主要视图函数
    schoolmanager_blueprint = Blueprint('schoolmanager', __name__, template_folder='templates', static_folder="static",
                       url_prefix="/schoolmanager")
    
    
    # 文件上传、表头分析视图注册
    schoolmanager_blueprint.register_blueprint(utils_blueprint)
    # 学生数据管理功能视图注册
    schoolmanager_blueprint.register_blueprint(student_blueprint)
    # 成绩发布功能视图注册
    schoolmanager_blueprint.register_blueprint(examPublish_blueprint)
    # 成绩分享功能视图注册
    schoolmanager_blueprint.register_blueprint(examAnalyse_blueprint)
    
    # 直接访问跳转到成绩查询页面
    @schoolmanager_blueprint.route("/")
    def index():
        return """<script>if (window.location.pathname === '/schoolmanager/' || window.location.pathname === '/schoolmanager') {
            window.location.href = '/schoolmanager/examAnalyse/view' + window.location.search;
        }</script>"""
    
    app.register_blueprint(schoolmanager_blueprint)
