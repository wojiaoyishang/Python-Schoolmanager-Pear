import os

import pandas as pd

from applications.common.utils.http import table_api, success_api, fail_api

from flask import render_template

class imp():
    def __init__(self, dir_path) -> None:
        self.dir_path = dir_path
        return
    
    def render_view(self, args):
        """
        获取导入页面
        
        args 为请求参数所含的列表
        
        GET 传入参数说明：
        filename -- 要导入的文件名
        sheetname -- 导入 excel 的指定表
        header -- 第几行作为表头
        impColums -- 设定好的新表头
        
        通过 iframe 框架获取好新旧表头对应关系，预导入数据。
        """
        # 获取 GET 参数
        filename = args.get("filename")  # 文件名
        sheetname = args.get("sheetname", 0)  # sheet名
        header = args.get("header", "0")  # 作为表头的行
        impColumns = args.get("impColumns", "").split(",")  # 新表头
        
        
        # 判断是否有效
        if filename is None:
            return fail_api(msg="Bad Filename!")
        filepath = self.dir_path + "/upload/" + filename
        if not os.path.exists(filepath):
            return fail_api(msg="Bad Filename!")
        
        if header.isdigit():
            header = int(header)
        else:
            header = 0
        
        # 重新设置，方便前台调用
        args['header'] = header
        
        # pandas 读取文件
        df = pd.read_excel(filepath, sheet_name=None)
        
        # 获取所有 sheet
        sheets = list(df.keys())
        
        # 如果 sheet 一个都没有
        if len(sheets) == 0:
            return fail_api(msg="No sheets found!")
            
        # 如果没有指定 sheet 那么选择一个 sheet
        if sheetname is None:
            sheetname = sheets[0]
            
        # 重新取出数据
        df = pd.read_excel(filepath, sheet_name=sheetname, header=header)
        
        # 取出表头与前五行数据
        columns = list(df.columns)
        length = len(df)
        data = df.head(10).values
        
        return render_template("schoolmanager_utils/engines/excel_imp.html",
                            sheets=sheets,
                            sheetname=sheetname,
                            columns=columns,
                            data=data,
                            length=length,
                            impColumns=impColumns,
                            args=args)
    
    
    def get_dataframe(self, args: dict, imp: dict):
        """
        获取 df 对象
        
        必要参数：
        args -- 导入引擎页面 GET 参数
        imp -- 导入引擎页面 imp 表单
        """
        # 获取 GET 参数
        filename = args.get("filename")  # 文件名
        sheetname = args.get("sheetname", 0)  # sheet名
        header = args.get("header", "0")  # 作为表头的行

        # 判断是否有效
        if filename is None:
            raise BaseException("Bad Filename!")
        filepath = self.dir_path + "/upload/" + filename
        
        if not os.path.exists(filepath):
            raise BaseException("Bad Filename!")

        if header.isdigit():
            header = int(header)
        else:
            header = 0

        # 取出数据
        df = pd.read_excel(filepath, sheet_name=sheetname, header=header, usecols=[_ for _ in imp.values() if _ != ""])
        
        # 对应表头（更改表头）
        for f in imp.keys():
            if imp[f].strip() != "":
                df.rename(columns={imp[f]: f}, inplace=True)
        return df
        
        