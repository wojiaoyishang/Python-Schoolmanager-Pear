"""
此文件集成了对于常用功能的支持，比如文件上传
"""
import os

from applications.common.utils.http import table_api, success_api, fail_api
from applications.common.utils.rights import authorize

from flask import Blueprint, render_template, request

from .utils import secure_filename, imp_render_view

# 获取插件所在的目录（结尾没有分割符号）
dir_path = os.path.dirname(__file__).replace("\\", "/")
folder_name = dir_path[dir_path.rfind("/") + 1:]

blueprint = Blueprint('utils', __name__, url_prefix="/utils")

@blueprint.get("/upload")
@authorize("SchoolManager:upload")
def upload_view():
    """
    上传文件页面
    """
    return render_template("schoolmanager_utils/upload.html")

@blueprint.post("/upload")
@authorize("SchoolManager:upload")
def upload_api():
    """
    上传文件
    """
    try:
        f = request.files['file']
        
        # 文件名安全处理
        filename = secure_filename(f.filename)
        
        save_path = dir_path + "/upload/" + filename  # 保存路径
        
        # 文件名重名处理
        i = 1
        while os.path.exists(save_path):
            filename = f"({i})" + filename
            save_path = dir_path + "/upload/" + filename
            i += 1
        
        f.save(save_path)
        return {
                "code": 0,
                "msg": "上传成功！",
                "data": {"name": filename}
            }    
    except BaseException as error:
        return {
                "code": -1,
                "msg": str(error)
            }    

@blueprint.post("/upload/files")
@authorize("SchoolManager:upload")
def get_files():
    """
    获取上传的文件
    """
    # 获取文件列表
    filenames = os.listdir(dir_path + "/upload")
    filenames = [{"文件名": filename} for filename in filenames]  # 格式化输出
    
    return table_api(msg="success", count=len(filenames), data=filenames)

@blueprint.delete("/upload/files/<string:filename>")
@authorize("SchoolManager:upload")
def delete_file(filename):
    """
    删除文件
    """
    # 文件名安全处理
    filename = secure_filename(filename)
    
    # 删除文件
    os.remove(dir_path + "/upload/" + filename)
    
    if not os.path.exists(dir_path + "/upload/" + filename):
        return success_api(msg="删除文件成功！")
    else:
        return fail_api(msg="删除文件失败！")
    
@blueprint.get("/imp")
@authorize("SchoolManager:readable")
def imp_view():
    """
    数据导入
    """
    # 判断导入引擎
    engine = request.args.get("engine")
    if engine is None:
        return fail_api(msg="Not found engine!")
    
    req = request.args.copy()
    
    req['filename'] = secure_filename(req.get("filename"))  # 文件名
    try:
        return imp_render_view(req)
    except BaseException as e:
        return f"""<script>var error="出现错误！可能是文件不支持或者损坏！{str(e)}"</script>"""
        
    
    