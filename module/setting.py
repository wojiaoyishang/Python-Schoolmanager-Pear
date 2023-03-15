import os
import json
import sqlite3


# 获取插件所在的目录（结尾没有分割符号）
dir_path = os.path.dirname(__file__).replace("\\", "/")
dir_path = dir_path[:dir_path.rfind("/")]  # 获取上一级
folder_name = dir_path[dir_path.rfind("/") + 1:]


def get(table, key):
    """
    获取一个变量值

    :param table: 所在的表
    :param key: 要获取的变量
    """
    
    systemData_con = sqlite3.connect(dir_path + "/data/systemData.db")  # 连接学生数据库
    
    cur = systemData_con.cursor()
    cur.execute(f""" SELECT value FROM `{table}` WHERE key = ? """, (key,)) 

    data = cur.fetchone()
    if data is None:
        return None
    
    return json.loads(data[0])

def set(table, key, value):
    """
    设置一个变量值

    :param table: 所在的表
    :param key: 要设置的变量
    :param value: 值
    """
    
    systemData_con = sqlite3.connect(dir_path + "/data/systemData.db")  # 连接学生数据库
    
    cur = systemData_con.cursor()
    

    cur.execute(f""" UPDATE `{table}` SET value = ? WHERE key = ? """, (json.dumps(value), key)) 
    if cur.rowcount == 0:
        cur.execute(f""" INSERT INTO `{table}` (value, key) VALUES(?, ?) """, (json.dumps(value), key))
  
    systemData_con.commit()
    cur.close()
    systemData_con.close()