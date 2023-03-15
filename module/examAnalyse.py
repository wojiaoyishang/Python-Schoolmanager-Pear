import os
import re
import time
import sqlite3

import pandas as pd

from applications.common.utils.validate import str_escape
from applications.common.utils.http import table_api, success_api, fail_api

# 获取源码所在的目录（结尾没有分割符号）
dir_path = os.path.dirname(__file__).replace("\\", "/")
dir_path = dir_path[:dir_path.rfind("/")]  # 获取上一级
folder_name = dir_path[dir_path.rfind("/") + 1:]  # 插件文件夹名称

def get_average(index, giveMark):
    """
    获取各科平均分  不包括 NULL 和 零分

    :param index: 考试ID
    :param giveMark: 赋分
    :return: 字典
    """
    
    # 连接数据库
    examData_con = sqlite3.connect(dir_path + "/data/examData.db")
    cur = examData_con.cursor()
    
    # 获取考试信息
    cur.execute(f""" SELECT 考试名称, 届数 FROM "考试数据表" WHERE "index" = ? """, (index,))
    try:
        exam_name, grade = cur.fetchone()
    except TypeError:
        return fail_api(msg="错误的考试ID！")
    
    fields = ['语文', '数学', '外语', '政治', '历史', '地理', '物理', '化学', '生物', '技术', '总分', '主科', '副科']
    
    sql = """SELECT """
    
    for f in fields:
        sql += f"AVG(CASE WHEN {f} > 0 THEN {f} ELSE NULL END) AS {f},"
    
    sql = sql[:-1] + f""" FROM "{grade}届_{exam_name}" WHERE 赋分 = {int(giveMark)}; """
    
    cur.execute(sql)
    
    # 获取数据字段
    table_head = []
    for d in cur.description:
        table_head.append(d[0])
    
    # 获取数据并对应字段
    data = []
    for d in cur.fetchall():
        data.append(dict(zip(table_head, d)))
    
    cur.close()
    examData_con.close()
        
    return data[0]

def get_specMarkStudent(index, giveMark):
    """
    获取特控线人数

    :param index: 考试ID
    :param giveMark: 是否赋分
    """
    
    # 连接数据库
    examData_con = sqlite3.connect(dir_path + "/data/examData.db")
    cur = examData_con.cursor()
    
    # 获取考试信息
    cur.execute(f""" SELECT 考试名称, 届数, 特控线分数 FROM "考试数据表" WHERE "index" = ? """, (index,))
    try:
        exam_name, grade, mark = cur.fetchone()
    except TypeError:
        return fail_api(msg="错误的考试ID！")
    
    cur.execute(f"""SELECT count(*) FROM "{grade}届_{exam_name}" WHERE 总分 >= {mark} AND 赋分 = {int(giveMark)};""")
    
    total = cur.fetchone()[0]
    
    cur.close()
    examData_con.close()
    
    return total
    
def get_specMarkStudent_by_class(index, giveMark):
    """
    获取特控线人数，但是按照班级分类。

    :param index: 考试ID
    :param giveMark: 是否赋分
    """
    # 连接数据库
    examData_con = sqlite3.connect(dir_path + "/data/examData.db")
    cur = examData_con.cursor()
    
    # 获取考试信息
    cur.execute(f""" SELECT 考试名称, 届数, 特控线分数 FROM "考试数据表" WHERE "index" = ? """, (index,))
    try:
        exam_name, grade, mark = cur.fetchone()
    except TypeError:
        return fail_api(msg="错误的考试ID！")
    
    cur.execute(f""" ATTACH DATABASE '{dir_path + "/data/studentData.db"}' AS studentData  """)
    cur.execute(f"""
        WITH Top AS (
            SELECT 姓名
            FROM "{grade}届_{exam_name}"
            WHERE 总分 >= {mark} AND 赋分 = {int(giveMark)}
        )
        SELECT studentData.'{grade}届学生数据'.班级, COUNT(*) as 人数
        FROM Top
        JOIN studentData.'{grade}届学生数据' ON Top.姓名 = studentData.'{grade}届学生数据'.姓名
        GROUP BY studentData.'{grade}届学生数据'.班级;
    """)
    
    data = {}

    for d in cur.fetchall():
        data[d[0]] = d[1]
    
    cur.close()
    examData_con.close()

    return data

def get_countStudent(index, giveMark, rank):
    """
    排名人数人数，按照班级分类。

    :param index: 考试ID
    :param giveMark: 是否赋分
    :param rank: 排名线
    """
    # 连接数据库
    examData_con = sqlite3.connect(dir_path + "/data/examData.db")
    cur = examData_con.cursor()
    
    # 获取考试信息
    cur.execute(f""" SELECT 考试名称, 届数 FROM "考试数据表" WHERE "index" = ? """, (index,))
    try:
        exam_name, grade = cur.fetchone()
    except TypeError:
        return fail_api(msg="错误的考试ID！")
    
    cur.execute(f""" ATTACH DATABASE '{dir_path + "/data/studentData.db"}' AS studentData  """)
    cur.execute(f"""
        WITH Top AS (
            SELECT 姓名
            FROM "{grade}届_{exam_name}"
            WHERE 总分排名 <= {rank} AND 赋分 = {int(giveMark)}
        )
        SELECT studentData.'{grade}届学生数据'.班级, COUNT (Top.姓名) as 人数
        FROM studentData.'{grade}届学生数据' LEFT JOIN Top ON studentData.'{grade}届学生数据'.姓名 = Top.姓名
        GROUP BY studentData.'{grade}届学生数据'.班级;
    """)
  
    data = {}

    for d in cur.fetchall():
        if d[0] is None:
            continue
        data[d[0]] = d[1]
    
    cur.close()
    examData_con.close()

    return data
