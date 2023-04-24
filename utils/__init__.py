import os

from .engines import excel

from applications.common.utils.validate import str_escape
from applications.common.utils.http import table_api, success_api, fail_api

from flask import session, jsonify

# 获取插件所在的目录（结尾没有分割符号）
dir_path = os.path.dirname(__file__).replace("\\", "/")
dir_path = dir_path[:dir_path.rfind("/")]  # 获取上一级
folder_name = dir_path[dir_path.rfind("/") + 1:]

# 导入导出引擎载入
engines = {'excel': excel.imp(dir_path)}

def secure_filename(filename: str) -> str:
    """
    文件名安全处理

    :param filename: 输入文件名
    :return: 输出文件名
    """
    if filename is None:
        return None
    if filename.strip() == "":
        return None
    filename = filename.replace("\\", "/").replace(" ", "")
    file_name, file_ext = os.path.splitext(filename)
    return file_name.replace("/", "").replace(".", "") + file_ext

def imp_render_view(args):
    """
    导入引擎模板渲染
    """
    engine = args.get('engine')
    
    if engine not in engines:
        return fail_api(msg="engine error!")
    
    return engines[engine].render_view(args)

def imp_get_dataframe(args, imp):
    """
    传入参数，获取 dataframe 对象。
    
    必要参数：
    args -- 导入引擎页面 GET 参数
    imp -- 导入引擎页面 imp 表单
    """
    # 获取参数
    engine = args.get('engine')

    if engine is None or engine not in engines:
        raise BaseException ("engine error!")
    
    args['filename'] = secure_filename(args.get("filename"))
    
    if args['filename'] is None:
        raise BaseException ("filename error!")

    return engines[engine].get_dataframe(args=args, imp=imp)

def get_args_safely(args, int_args=["index", "limit", "page", "class", "grade", "giveMark", "班级", "届数"], must_have=[], string_safe=False):
    """
    把用户提供的参数安全化。

    :param args: 所有提供的参数字典。（此函数会直接更改字典）
    :param int_args: 需要为整数型的参数，如果为空字符串且在must_have中则会变为 None。
    :param string_safe: 是否安全化字符串。默认 False，如果为 False 则会把空字符串变为 None。
    :param must_have: 必须要拥有的参数
    :return: success, msg -> 是否成功, 提示信息
    """
    if args is None:
        return False, "参数未提供，或者提供格式不正确！"
    
    must_have = must_have.copy()
    
    for x in args.keys():
        if x in int_args and isinstance(args[x], str):
            if args[x].strip() == "" and x in must_have:
                args[x] = None
            elif not args[x].isdigit():
                return False, f"请求的参数 {x} 非法。"
            else:
                args[x] = int(args[x])
        if isinstance(args[x], str):
            args[x] = args[x].strip()
            if string_safe:
                args[x] = str_escape(args[x])  # 安全化字符串
            elif args[x] == "":
                args[x] = None
        
        if x in must_have:
            must_have.remove(x)
    
    if len(must_have) != 0:
        for x in must_have:
            args[x] = None
    
    return True, "参数通过检查。"
        
def student_permissions(per=None, name=None, grade=None):
    """
    管理员或者学生是否有权限。
    学生权限判断方法：
    
    session.get("schoolmanager_name") == name and session.get("schoolmanager_grade") == grade

    :param per: 管理员权限标识:
    :param name: 学生姓名
    :param grade: 学生年段
    """
    return (per in session.get('permissions', [])) or (session.get("schoolmanager_name") == name and int(session.get("schoolmanager_grade")) == int(grade))