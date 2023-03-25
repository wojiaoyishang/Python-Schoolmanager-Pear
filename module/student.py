import os 
import re
import json
import sqlite3

import pandas as pd

# 获取源码所在的目录（结尾没有分割符号）
dir_path = os.path.dirname(__file__).replace("\\", "/")
dir_path = dir_path[:dir_path.rfind("/")]  # 获取上一级
folder_name = dir_path[dir_path.rfind("/") + 1:]  # 插件文件夹名称

def regexp(expr, item):
    """
    让sqlite3支持正则匹配
    """
    reg = re.compile(expr)
    return reg.search(item) is not None

def get_grades():
    """
    获取学生数据库中所有的届数。
    """
    
    studentData_con = sqlite3.connect(dir_path + "/data/studentData.db")  # 连接学生数据库
    
    cur = studentData_con.cursor()
    cur.execute(""" SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%届%' ORDER BY name; """) 
    
    data = []
    for d in cur.fetchall():
        data.append(int(d[0].replace("届学生数据", "")))
    
    cur.close()

    return data

def get_all_class(grade):
    """
    获取一个年段中所有班级
    
    :param grade: 毕业届
    """
    if grade == "":
        return [""]
    
    studentData_con = sqlite3.connect(dir_path + "/data/studentData.db")  # 连接学生数据库
    
    
    cur = studentData_con.cursor()
    cur.execute(f""" SELECT 班级 FROM "{grade}届学生数据" GROUP BY 班级; """) 

    data = [_[0] for _ in cur.fetchall() if _[0] is not None]
    
    if len(data) == 0:
        data = [""]
        
    cur.close()
    studentData_con.close()

    return data

def get_students_data(grade: int, fields="姓名,性别,班级", class_=0, name=None, page=0, limit=10) -> dict:
    """
    获取学生数据

    :param grade: 毕业届
    :param fields: 获取的字段
    :param page: 页, defaults to 0
    :param limit: 数, defaults to 10
    
    :return: {'data': data, 'count': total, 'limit': limit}
    """
    
    studentData_con = sqlite3.connect(dir_path + "/data/studentData.db")  # 连接学生数据库
    studentData_con.create_function("REGEXP", 2, regexp)

    cur = studentData_con.cursor()
    
    # 查询数据
    if class_ == 0:  # 所有班级
        sql_from = f""" "{grade}届学生数据" """
    else:
        sql_from = f""" "{grade}届学生数据" WHERE 班级 = {class_} """
    
    if name is not None:
        if sql_from.find("WHERE") != -1:
            sql_from += f""" AND 姓名 REGEXP "{name}" """
        else:
            sql_from += f""" WHERE 姓名 REGEXP "{name}" """

    cur.execute(f"SELECT {fields} FROM {sql_from} LIMIT {limit} OFFSET {(page - 1) * limit}") 
    
    # 获取数据字段
    table_head = []
    for d in cur.description:
        table_head.append(d[0])
    
    # 获取数据并对应字段
    data = []
    for d in cur.fetchall():
        _ = dict(zip(table_head, d))
        # 加入届数，方便前端处理
        _['届数'] = grade
        data.append(_)
    
    # 查询总数
    cur.execute(f""" SELECT count(*) FROM {sql_from}  """)
    total = cur.fetchone()[0]
    
    cur.close()
    studentData_con.close()

    return {'data': data, 'count': total, 'limit': limit}

def get_student_data(name, grade):
    """
    获取学生数据

    :param name: 学生姓名
    :param grade: 届数
    """
    studentData_con = sqlite3.connect(dir_path + "/data/studentData.db")  # 连接学生数据库

    
    cur = studentData_con.cursor()
    cur.execute(f""" SELECT * FROM "{grade}届学生数据" WHERE 姓名 = ? ; """,
                (name,)) 
    
    # 获取数据字段
    table_head = []
    for d in cur.description:
        table_head.append(d[0])
    
    data = cur.fetchall() 

    if len(data) == 0:
        return None
    
    # 获取数据并对应字段
    data = dict(zip(table_head, data[0]))
    
    cur.close()
    studentData_con.close()
    
    return data
    
def set_student_data(**args):
    """
    设置学生数据，此函数会自动转义字符
    """
    studentData_con = sqlite3.connect(dir_path + "/data/studentData.db")  # 连接学生数据库
    
    cur = studentData_con.cursor()
    
    fields = ['性别', '身份证号', '毕业学校', '家庭住址', '班级', '寝室', '选科', '备注']
    
    cur.execute(f""" UPDATE "{args["届数"]}届学生数据"
                SET 
                {'=?,'.join(fields)}=?
                WHERE 
                姓名 = ? ; """,
                [args[_] for _ in fields] + [args['姓名']]) 
    
    studentData_con.commit()
    studentData_con.close()
    
    return True

def add_student_data(**args):
    """
    添加学生数据，此函数会自动转义字符
    """
    studentData_con = sqlite3.connect(dir_path + "/data/studentData.db")  # 连接学生数据库
    
    cur = studentData_con.cursor()
    
    # 判断是否已经存在这位同学
    cur.execute(f""" SELECT * FROM "{args["届数"]}届学生数据" WHERE 姓名 = ?  """, (args["姓名"],))
    
    if cur.fetchone() is not None:
        raise BaseException("这位学生已经存在。")
    
    fields = ['性别', '身份证号', '毕业学校', '家庭住址', '班级', '寝室', '选科', '备注']
    
    # 查看参数是否全都有
    for f in fields:
        if f not in args:
            args[f] = ''
    cur.execute(f""" INSERT INTO "{args["届数"]}届学生数据"
                (姓名,{','.join(fields)})
                VALUES 
                (?,{("?," * len(fields))[:-1]}) ; """,
                [args["姓名"]] + [args[_] for _ in fields]) 
    
    studentData_con.commit()
    studentData_con.close()
    
    return True

def delete_student_data(**args):
    """
    删除学生数据
    """
    studentData_con = sqlite3.connect(dir_path + "/data/studentData.db")  # 连接学生数据库
    
    cur = studentData_con.cursor()

    cur.execute(f""" DELETE FROM "{args["届数"]}届学生数据" WHERE 姓名 = ?  """, (args["姓名"],))
    
    studentData_con.commit()
    studentData_con.close()
    
    # 删除证件照
    args["姓名"] = args["姓名"].replace("/", "").replace("\\", "").replace(".", "")
    if os.path.exists(dir_path + f'/data/photos/{args["届数"]}/{args["姓名"]}.jpg'):
        os.remove(dir_path + f'/data/photos/{args["届数"]}/{args["姓名"]}.jpg')
    
    return True

def add_grade(grade):
    """
    新建年段
    
    :param grade: 届数
    """
    studentData_con = sqlite3.connect(dir_path + "/data/studentData.db")  # 连接学生数据库
    
    cur = studentData_con.cursor()

    cur.execute(f""" CREATE TABLE "{grade}届学生数据" (
        "姓名"	TEXT NOT NULL,
        "性别"	INTEGER,
        "身份证号"	TEXT,
        "毕业学校"	TEXT,
        "家庭住址"	TEXT,
        "班级"	INTEGER,
        "寝室"	TEXT,
        "选科"	TEXT,
        "备注"	TEXT,
        "查询设置"	TEXT,
        PRIMARY KEY("姓名")
    );  """)
    
    studentData_con.commit()
    studentData_con.close()
    
    return True

def delete_grade(grade):
    """
    删除年段
    
    :param grade: 届数
    """
    studentData_con = sqlite3.connect(dir_path + "/data/studentData.db")  # 连接学生数据库
    
    cur = studentData_con.cursor()

    cur.execute(f""" DROP TABLE "{grade}届学生数据";  """)
    
    studentData_con.commit()
    studentData_con.close()
    
    return True

def imp_data(df1: pd.DataFrame, ext: dict):
    """
    合并并导入数据
    
    df1 -- 要导入的数据
    ext -- 网页表单额外数据
    """
    grade = ext.get("grade", "-1")
    mode = ext.get("mode", "add")

    if grade is None or not grade.isdigit():
        return False, "必须指定年级。"
    
    # 判断是否符合要求
    if '姓名' not in df1.columns:
        return False, "必须指定姓名列。"
    
    # 遍历导入数据，规定格式
    df1.set_index('姓名', inplace=True)  # 重新设置索引

    # 删除空行
    df1.dropna(inplace=True)

    # 提供数据不足
    if len(df1.columns) == 0:
        return False, "至少在选择一个除了姓名的列。"
    
    # 选科格式统一
    if '选科' in df1.columns:
        subjects = "政史地物化生技"
        for i in df1.index:
            y = ""
            for s in subjects:
                if s in df1.loc[i, '选科']:
                    y += s
            df1.loc[i, '选科'] = "语数外" + y 
 
    # 同一性别格式
    if '性别' in df1.columns:
        df1['性别'] = df1['性别'].map({'女': 0, '男': 1})
        df1['性别'] = df1['性别'].fillna(-1)
        df1['性别'].astype(int)
    
    # 同一班级格式
    if '班级' in df1.columns:
        df1['班级'] = df1['班级'].fillna(0)
        df1.loc[~df1['班级'].apply(lambda x: isinstance(x, int) or isinstance(x, float)), '班级'] = 0
        df1['班级'].astype(int)
        
    
    studentData_con = sqlite3.connect(dir_path + "/data/studentData.db")  # 连接学生数据库
    
    cur = studentData_con.cursor()
    
    # 获取数据库中原有的姓名
    names = []
    cur.execute(f""" SELECT 姓名 FROM "{ext.get("grade")}届学生数据"  """)
    for name in cur.fetchall():
        names.append(name[0])
    
    # 设定 SQL 查询字符串
    UPDATE_sql = f""" UPDATE "{ext.get("grade")}届学生数据" SET """
    INSERT_sql = f""" INSERT INTO "{ext.get("grade")}届学生数据" ("""
    
    INSERT_sql += "姓名,"
    
    # 导入所有字段
    for col in df1.columns:
        if mode == "add":
            UPDATE_sql += f"""{col} = CASE WHEN {col} IS NULL THEN ? ELSE {col} END,"""
        else:
            UPDATE_sql += f"""{col} = ? ,"""
        
        INSERT_sql += col + ","

    UPDATE_sql = UPDATE_sql[:-1] + "\n"
    INSERT_sql = INSERT_sql[:-1] + ") VALUES(" + ("?," * (len(df1.columns) + 1))[:-1] + ")"
    
    def str_n(s):
        _ = str(s)
        return None if _ in ["None", "nan"] else _
    
    # 判断导入形式
    if mode == "add" or mode == "replace":
        for i in df1.index:
            if i not in names:
                cur.execute(INSERT_sql, [i] + [ str_n(df1.loc[i, col]) for col in df1.columns ])
            else:
                cur.execute(UPDATE_sql + "WHERE 姓名=?", [ str_n(df1.loc[i, col]) for col in df1.columns] + [i])
    elif mode == "skip":
        for i in df1.index:
            if i not in names:
                cur.execute(INSERT_sql, [i] + [ str_n(df1.loc[i, col]) for col in df1.columns ])
    else:
        return False, "选择了错误的导入模式。"
                
    cur.close()
    studentData_con.commit()
    studentData_con.close()
    
    # df2.to_sql(f"{grade}届学生数据", con=studentData_con, if_exists='replace', index="姓名")
    
    return True, "导入数据成功！"

def get_setting(name, grade, key=None):
    """
    获取学生的查询设置

    :param name: 姓名
    :param grade: 届数
    :param key: 键, None 将会全部获取
    """
    studentData_con = sqlite3.connect(dir_path + "/data/studentData.db")  # 连接学生数据库
    cur = studentData_con.cursor()
    
    cur.execute(f""" SELECT 查询设置 FROM "{grade}届学生数据" WHERE 姓名 = ? """, (name,))
    data = cur.fetchone()
    
    if data is None or data[0] is None:
        return {}
    
    data_json = json.loads(data[0])
    
    if data_json is None:
        return {}

    if key is None:
        return data_json
    
    if key not in data_json:
        return None
    
    return data_json[key]


def set_setting(name, grade, key, value):
    """
    设置学生的查询设置

    :param name: 姓名
    :param grade: 届数
    :param key: 键
    :param value: 值
    """
    studentData_con = sqlite3.connect(dir_path + "/data/studentData.db")  # 连接学生数据库
    cur = studentData_con.cursor()
    
    data = get_setting(name, grade, None)
    if data is None:
        data = {}
    data[key] = value
    cur.execute(f""" UPDATE "{grade}届学生数据" SET 查询设置 = ? WHERE 姓名 = ? """, (json.dumps(data), name)) 
    
    studentData_con.commit()
    cur.close()
    studentData_con.close()

