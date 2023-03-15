import os

from .engines import excel

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
    filename = filename.replace("\\", "/")
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