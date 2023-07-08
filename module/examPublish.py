import os
import re
import time
import sqlite3

import pandas as pd

from applications.common.utils.validate import str_escape

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

def imp_data(df1: pd.DataFrame, ext: dict):
    """
    合并并导入数据
    
    df1 -- 要导入的数据
    ext -- 网页表单额外数据
    """
    grade = ext.get("grade", "-1")
    mode = ext.get("mode", "add")
    examName = str_escape(ext.get("examName", "IlovePikachu"))  # 考试名称
    giveMark = int(ext.get("giveMark") == "on")  # 是否赋分

    if grade is None or not grade.isdigit():
        return False, "必须指定年级。"
    
    if examName is None:
        return False, "必须指定考试名称。"
    
    # 判断是否符合要求
    if '姓名' not in df1.columns:
        return False, "必须指定姓名列。"
    
    # 遍历导入数据，规定格式
    df1.set_index('姓名', inplace=True)  # 重新设置索引

    # 设定数据格式
    for col in df1.columns:
        if col not in ('姓名', '备注'):
            df1[col] = df1[col].apply(lambda x: x if isinstance(x, (int, float)) else None)

    # 提供数据不足
    if len(df1.columns) == 0:
        return False, "至少在选择一个除了姓名的列。"

    # 连接数据库
    examData_con = sqlite3.connect(dir_path + "/data/examData.db")
    cur = examData_con.cursor()
    
    # 写入考试数据
    cur.execute(f""" SELECT 考试名称 FROM "考试数据表" WHERE 届数 = ? AND 考试名称 = ? """, (grade, examName))  # 判断是否已经写入
    if len(cur.fetchall()) == 0:
        cur.execute(f"""
            INSERT INTO "考试数据表" 
            (届数, 考试名称, 考试时间, 考试备注, 特控线分数, 语文总分, 数学总分, 外语总分, 政治总分, 历史总分, 地理总分, 物理总分, 化学总分, 生物总分, 技术总分)
            VALUES (?, ?, ?, NULL, 590, 150, 150, 150, 100, 100, 100, 100, 100, 100, 100)
            """, (grade, examName, int(time.time() * 1000)))
    
    # 创建一张考试表
    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS "{grade}届_{examName}" (
            "index"	INTEGER NOT NULL UNIQUE,
            "姓名"	TEXT NOT NULL,
            "备注"	TEXT,
            "赋分"	INTEGER NOT NULL,
            "语文"	REAL,
            "语文排名"	INTEGER,
            "数学"	REAL,
            "数学排名"	INTEGER,
            "外语"	REAL,
            "外语排名"	INTEGER,
            "政治"	REAL,
            "政治排名"	INTEGER,
            "历史"	REAL,
            "历史排名"	INTEGER,
            "地理"	REAL,
            "地理排名"	INTEGER,
            "物理"	REAL,
            "物理排名"	INTEGER,
            "化学"	REAL,
            "化学排名"	INTEGER,
            "生物"	REAL,
            "生物排名"	INTEGER,
            "技术"	REAL,
            "技术排名"	INTEGER,
            "总分"	REAL,
            "总分排名"	INTEGER,
            "主科"	REAL,
            "主科排名"	INTEGER,
            "副科"	REAL,
            "副科排名"	INTEGER,
            PRIMARY KEY("index" AUTOINCREMENT)
        );
    """)
    
    # 获取数据库中原有的姓名
    names = []
    cur.execute(f""" SELECT 姓名 FROM "{grade}届_{examName}" WHERE 赋分 = {giveMark} """)
    for name in cur.fetchall():
        names.append(name[0])
    
    # 设定 SQL 查询字符串
    UPDATE_sql = f""" UPDATE "{grade}届_{examName}" SET """
    INSERT_sql = f""" INSERT INTO "{grade}届_{examName}" ("""
    
    INSERT_sql += "赋分,姓名,"
    
    # 导入所有字段
    for col in df1.columns:
        if mode == "add":
            UPDATE_sql += f"""{col} = CASE WHEN {col} IS NULL THEN ? ELSE {col} END,"""
        else:
            UPDATE_sql += f"""{col} = ? ,"""
        
        INSERT_sql += col + ","

    UPDATE_sql = UPDATE_sql[:-1] + "\n"
    INSERT_sql = INSERT_sql[:-1] + ") VALUES(" + f"{giveMark}," + ("?," * (len(df1.columns) + 1))[:-1] + ")"
    
    def str_n(s):
        _ = str(s)
        return None if _ in ["None", "nan"] else _
    
    # 判断导入形式
    if mode == "add" or mode == "replace":
        for i in df1.index:
            if i not in names:
                
                cur.execute(INSERT_sql, [i] + [ str_n(df1.loc[i, col]) for col in df1.columns ])
            else:
                cur.execute(UPDATE_sql + f"WHERE 姓名=? AND 赋分={giveMark}", [ str_n(df1.loc[i, col]) for col in df1.columns] + [i])
    elif mode == "skip":
        for i in df1.index:
            if i not in names:
                cur.execute(INSERT_sql, [i] + [ str_n(df1.loc[i, col]) for col in df1.columns ])
    else:
        return False, "选择了错误的导入模式。"
                
    cur.close()
    examData_con.commit()
    examData_con.close()
    
    return True, "导入数据成功！"

def get_all_exam(fields="考试名称", index=None, grade=None, name=None, startDate=None, endDate=None, page=0, limit=10):
    """
    获取考试数据
    """
    # 连接数据库
    examData_con = sqlite3.connect(dir_path + "/data/examData.db")
    examData_con.create_function("REGEXP", 2, regexp)
    
    cur = examData_con.cursor()
    
    sql_from = ""
    
    if grade is not None:
        sql_from += f"WHERE 届数 = {grade}"
    
    if index is not None:
        if sql_from.find("WHERE") != -1:
            sql_from += f""" AND "index" = {int(index)} """
        else:
            sql_from += f""" WHERE "index" = {int(index)} """
    
    if name is not None:
        if sql_from.find("WHERE") != -1:
            sql_from += f""" AND 考试名称 REGEXP "{name}" """
        else:
            sql_from += f""" WHERE 考试名称 REGEXP "{name}" """
    
    if startDate is not None or endDate is not None:
        if sql_from.find("WHERE") != -1:
            sql_from += f""" AND 考试时间 BETWEEN {startDate} AND {endDate} """
        else:
            sql_from += f""" WHERE 考试时间 BETWEEN {startDate} AND {endDate} """
    
    if page is None or limit is None:
        cur.execute(f""" SELECT {fields} FROM "考试数据表" {sql_from} ORDER BY 考试时间""")
    else:
        cur.execute(f""" SELECT {fields} FROM "考试数据表" {sql_from} ORDER BY 考试时间 LIMIT {limit} OFFSET {(page - 1) * limit} """)

    # 获取数据字段
    table_head = []
    for d in cur.description:
        table_head.append(d[0])
    
    # 获取数据并对应字段
    data = []
    for d in cur.fetchall():
        data.append(dict(zip(table_head, d)))
    
    # 查询总数
    cur.execute(f""" SELECT count(*) FROM "考试数据表" {sql_from} """)
    
    total = cur.fetchone()[0]
    
    cur.close()
    examData_con.close()
    
    return {'data': data, 'count': total, 'limit': limit}

def delete_exam(name, grade):
    """
    删除一次考试

    :param name: 考试名称
    :param grade: 届数
    """
    # 连接数据库
    examData_con = sqlite3.connect(dir_path + "/data/examData.db")
    cur = examData_con.cursor()
    
    # 删除数据记录
    cur.execute(""" DELETE FROM "考试数据表" WHERE 考试名称 = ? AND 届数 = ? """, (name, grade))
    
    # 删除考试数据
    cur.execute(f""" DROP TABLE "{grade}届_{name}" """)
    
    examData_con.commit()
    
    cur.close()
    examData_con.close()

def add_exam(name, grade):
    """
    创建一次考试

    :param name: 考试名称
    :param grade: 对应的届数
    """
    # 连接数据库
    examData_con = sqlite3.connect(dir_path + "/data/examData.db")
    cur = examData_con.cursor()
    
    cur.execute(f""" SELECT 考试名称 FROM "考试数据表" WHERE 届数 = ? AND 考试名称 = ? """, (grade, name))  # 判断是否已经写入

    if len(cur.fetchall()) == 0:
        cur.execute(f"""
            INSERT INTO "考试数据表" 
            (届数, 考试名称, 考试时间, 考试备注, 特控线分数, 语文总分, 数学总分, 外语总分, 政治总分, 历史总分, 地理总分, 物理总分, 化学总分, 生物总分, 技术总分)
            VALUES (?, ?, ?, NULL, 590, 150, 150, 150, 100, 100, 100, 100, 100, 100, 100)
            """, (grade, name, int(time.time() * 1000)))
    else:
        return False, "考试已存在。"

    # 创建一张考试表
    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS "{grade}届_{name}" (
            "index"	INTEGER NOT NULL UNIQUE,
            "姓名"	TEXT NOT NULL,
            "备注"	TEXT,
            "赋分"	INTEGER NOT NULL,
            "语文"	REAL,
            "语文排名"	INTEGER,
            "数学"	REAL,
            "数学排名"	INTEGER,
            "外语"	REAL,
            "外语排名"	INTEGER,
            "政治"	REAL,
            "政治排名"	INTEGER,
            "历史"	REAL,
            "历史排名"	INTEGER,
            "地理"	REAL,
            "地理排名"	INTEGER,
            "物理"	REAL,
            "物理排名"	INTEGER,
            "化学"	REAL,
            "化学排名"	INTEGER,
            "生物"	REAL,
            "生物排名"	INTEGER,
            "技术"	REAL,
            "技术排名"	INTEGER,
            "总分"	REAL,
            "总分排名"	INTEGER,
            "主科"	REAL,
            "主科排名"	INTEGER,
            "副科"	REAL,
            "副科排名"	INTEGER,
            PRIMARY KEY("index" AUTOINCREMENT)
        );
    """)
    

    
    examData_con.commit()
    cur.close()
    examData_con.close()
    
    return True, "创建考试成功。"


def set_exam_info(**args):
    """
    设置学生数据
    """
    
    fields = ['届数', '考试时间', '考试名称', '考试备注', '特控线分数', '语文总分', '数学总分', '外语总分',
              '政治总分', '历史总分', '地理总分', '物理总分', '化学总分', '生物总分', '技术总分']
    
    
    # 连接数据库
    examData_con = sqlite3.connect(dir_path + "/data/examData.db")
    cur = examData_con.cursor()
    
    
    # 获取原来的考试名称
    cur.execute(f""" SELECT 考试名称, 届数 FROM "考试数据表" WHERE "index" = {int(args['index'])} """)
    name, grade = cur.fetchone()  # 原来的名称与年级
    cur.execute(f""" UPDATE "考试数据表" SET { '=?,'.join(fields) }=? WHERE "index" = {int(args['index'])} """, [args[_] for _ in fields])  # 判断是否已经写入
    
    if f"{grade}届_{name}" != f"{args['届数']}届_{args['考试名称']}":
        cur.execute(f""" ALTER TABLE "{grade}届_{name}" RENAME TO "{args['届数']}届_{args['考试名称']}"; """)
    
    examData_con.commit()
    cur.close()
    examData_con.close()
    
    return True, "更新数据成功！"

def get_exam(index, limit=50, page=1, giveMark=True, name=None, class_=None, ascending=False):
    """
    获取考试成绩

    :param index: 考试ID
    :param limit: 一页数量, defaults to 50
    :param page: 页数, defaults to 1
    :param name: 学生姓名
    :param class_: 班级
    :param ascending: 是否升序
    """
    
    # 连接数据库
    examData_con = sqlite3.connect(dir_path + "/data/examData.db")
    examData_con.create_function("REGEXP", 2, regexp)
    
    # 构造定位语句
    sql_form = ""
    
    if name is not None:
        sql_form = f""" AND 姓名 REGEXP "{name}" """
        
    cur = examData_con.cursor()
    
    # 找到存储的考试表
    cur.execute(f""" SELECT * FROM "考试数据表" WHERE "index" = ? """, (index,))
    
    # 获取数据字段
    table_head = []
    for d in cur.description:
        table_head.append(d[0])
    
    # 获取数据并对应字段
    exam_info = dict(zip(table_head, cur.fetchone()))
    
    exam_name = exam_info["考试名称"]
    grade = exam_info["届数"]
    
    if class_ is not None:
        cur.execute(f""" ATTACH DATABASE '{dir_path + "/data/studentData.db"}' AS studentData  """)
        if name is not None:
            sql_form = f""" AND 姓名 IN (SELECT 姓名 FROM studentData.'{grade}届学生数据' WHERE 班级={class_} AND 姓名 REGEXP "{name}") """
        else:
            sql_form = f""" AND 姓名 IN (SELECT 姓名 FROM studentData.'{grade}届学生数据' WHERE 班级={class_}) """

    if ascending:
        cur.execute(f""" SELECT * FROM "{grade}届_{exam_name}" WHERE 赋分 = ? {sql_form} ORDER BY 总分 ASC LIMIT {limit} OFFSET {(page - 1) * limit} """, (int(giveMark),))
    else:
        cur.execute(f""" SELECT * FROM "{grade}届_{exam_name}" WHERE 赋分 = ? {sql_form} ORDER BY 总分 DESC LIMIT {limit} OFFSET {(page - 1) * limit} """, (int(giveMark),))
    
    # 获取数据字段
    table_head = []
    for d in cur.description:
        table_head.append(d[0])
    
    # 获取数据并对应字段
    data = []
    for d in cur.fetchall():
        data.append(dict(zip(table_head, d)))
    
    if len(data) != 0:
        for k in list(data[0].keys()):
            if k not in ("index", "姓名", "备注", "赋分") and k.find("排名") == -1:
                cur.execute(f""" SELECT count(*) FROM "{grade}届_{exam_name}" WHERE `{k}` != 0 AND 赋分 = ? """, (int(giveMark),))
                data[0][k + "人数"] = cur.fetchone()[0]
    
    # 查询总数
    cur.execute(f""" SELECT count(*) FROM "{grade}届_{exam_name}" WHERE 赋分 = ? {sql_form} """, (int(giveMark),))
    
    total = cur.fetchone()[0]
    
    cur.close()
    examData_con.close()
    
    # 移除没用数据
    del exam_info['index']
    del exam_info['届数']
    del exam_info['考试名称']
    
    # 数据合并
    data[0].update(exam_info)
    
    return {'data': data, 'count': total, 'limit': limit}

def recalc_exam(index):
    """
    重新生成总分与排名数据

    :param index: 考试id
    """
    
    # 连接数据库
    examData_con = sqlite3.connect(dir_path + "/data/examData.db")
    cur = examData_con.cursor()
    
    # 获取考试信息
    cur.execute(f""" SELECT 考试名称, 届数 FROM "考试数据表" WHERE "index" = ? """, (index,))
    exam_name, grade = cur.fetchone()
    
    # 对于主科分数同步
    cur.execute(f"""
        UPDATE "{grade}届_{exam_name}" AS t1
        SET "语文" = CASE WHEN "语文" IS NULL THEN (SELECT "语文" FROM "{grade}届_{exam_name}" AS t2 WHERE t2."姓名" = t1."姓名" AND t2."赋分" = 1) ELSE "语文" END,
            "数学" = CASE WHEN "数学" IS NULL THEN (SELECT "数学" FROM "{grade}届_{exam_name}" AS t2 WHERE t2."姓名" = t1."姓名" AND t2."赋分" = 1) ELSE "数学" END,
            "外语" = CASE WHEN "外语" IS NULL THEN (SELECT "外语" FROM "{grade}届_{exam_name}" AS t2 WHERE t2."姓名" = t1."姓名" AND t2."赋分" = 1) ELSE "外语" END
        WHERE "赋分" = 0
    """)
    
    cur.execute(f"""
        UPDATE "{grade}届_{exam_name}" AS t1
        SET "语文" = CASE WHEN "语文" IS NULL THEN (SELECT "语文" FROM "{grade}届_{exam_name}" AS t2 WHERE t2."姓名" = t1."姓名" AND t2."赋分" = 0) ELSE "语文" END,
            "数学" = CASE WHEN "数学" IS NULL THEN (SELECT "数学" FROM "{grade}届_{exam_name}" AS t2 WHERE t2."姓名" = t1."姓名" AND t2."赋分" = 0) ELSE "数学" END,
            "外语" = CASE WHEN "外语" IS NULL THEN (SELECT "外语" FROM "{grade}届_{exam_name}" AS t2 WHERE t2."姓名" = t1."姓名" AND t2."赋分" = 0) ELSE "外语" END
        WHERE "赋分" = 1
    """)
    
    # 统计分数
    cur.execute(f"""
        UPDATE "{grade}届_{exam_name}"
        SET "总分" = IFNULL("语文", 0) + IFNULL("数学", 0) + IFNULL("外语", 0) + IFNULL("政治", 0) + IFNULL("历史", 0) + IFNULL("地理", 0) + IFNULL("物理", 0) + IFNULL("化学", 0) + IFNULL("生物", 0) + IFNULL("技术", 0)""")
    
    cur.execute(f"""
        UPDATE "{grade}届_{exam_name}"
        SET "主科" = IFNULL("语文", 0) + IFNULL("数学", 0) + IFNULL("外语", 0)""")
    
    cur.execute(f"""
        UPDATE "{grade}届_{exam_name}"
        SET "副科" = IFNULL("政治", 0) + IFNULL("历史", 0) + IFNULL("地理", 0) + IFNULL("物理", 0) + IFNULL("化学", 0) + IFNULL("生物", 0) + IFNULL("技术", 0)""")
  
    # 统计排名
    fields = ['语文', '数学', '外语', '政治', '历史', '地理', '物理', '化学', '生物', '技术', '总分', '主科', '副科']
    
    for field in fields:

        cur.execute(f""" UPDATE "{grade}届_{exam_name}"
                    SET "{field}排名" = (
                        SELECT "rank"
                        FROM (
                            SELECT "index", RANK() OVER (PARTITION BY "赋分" ORDER BY "{field}" DESC) AS "rank"
                            FROM "{grade}届_{exam_name}"
                        ) AS t1
                        WHERE t1."index" = "{grade}届_{exam_name}"."index"
                    );
            """)
    
    examData_con.commit()
    cur.close()
    examData_con.close()

def update_exam_data(index, data):
    """
    更新或添加一条成绩

    :param index: 考试ID
    :param data: 包含数据的data
    """
    
    # 连接数据库
    examData_con = sqlite3.connect(dir_path + "/data/examData.db")
    cur = examData_con.cursor()
    
    # 获取考试信息

    cur.execute(f""" SELECT 考试名称, 届数 FROM "考试数据表" WHERE "index" = ? """, (index,))
    exam_name, grade = cur.fetchone()
    
    fields = ['语文', '数学', '外语', '政治', '历史', '地理', '物理', '化学', '生物', '技术', '备注']
    
    # 查看一下记录行是否存在
    cur.execute(f""" SELECT * FROM "{grade}届_{exam_name}" WHERE  姓名=? AND 赋分=? """, [data['姓名'], data['赋分']])

    if len(cur.fetchmany()) == 0:
        cur.execute(f""" INSERT INTO "{grade}届_{exam_name}" ({",".join(fields)},姓名,赋分) VALUES  ({ '?,' * len(fields) }?,?) """, 
                    [(data[_] if data[_].strip() != "" else None) for _ in fields] + [data['姓名'], data['赋分']])
    else:
        cur.execute(f"""
            UPDATE "{grade}届_{exam_name}"
            SET {'=?,'.join(fields)}=? WHERE 姓名=? AND 赋分=? """, [(data[_] if data[_].strip() != "" else None) for _ in fields] + [data['姓名'], data['赋分']])
    
    examData_con.commit()
    cur.close()
    examData_con.close()
    
    
def delete_exam_data(index, data):
    """
    删除一条数据

    :param index: 考试ID
    :param data: 包含数据的data
    """
    # 连接数据库
    examData_con = sqlite3.connect(dir_path + "/data/examData.db")
    cur = examData_con.cursor()
    
    # 获取考试信息
    cur.execute(f""" SELECT 考试名称, 届数 FROM "考试数据表" WHERE "index" = ? """, (index,))
    exam_name, grade = cur.fetchone()
    
    cur.execute(f""" DELETE FROM "{grade}届_{exam_name}" WHERE 姓名=? AND 赋分=? """, 
                    [data['姓名'], data['赋分']])
    
    examData_con.commit()
    cur.close()
    examData_con.close()
    