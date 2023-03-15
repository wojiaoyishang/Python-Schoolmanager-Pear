"""
集成了对 Pear Admin Flask 的部门的操作，并给了相对应的示例。
"""

from applications.common import curd
from applications.extensions import db
from applications.models import Dept, User
from applications.schemas import DeptOutSchema


def get_all():
    """
    获取全部权限，会返回一个列表，每个列表是一个字典。

    字典构成如下::

        {
            "address":"这是总公司",  # 地址
            "deptId":1,  # 公司ID
            "deptName":"总公司",  # 公司名
            "email":"1",  # 公司 email
            "leader":"",  # 公司领导人
            "parentId":0,  # 父ID
            "phone":"",  # 联系电话
            "sort":1,  # 排序
            "status":"1" # 状态 1-开启 0-关闭
        }

    :return: 列表
    """
    dept = Dept.query.order_by(Dept.sort).all()
    return curd.model_to_dicts(schema=DeptOutSchema, data=dept)


def add(parentId, deptName, sort, leader, phone, email, status, address):
    """
    添加一个公司

    :param parentId: 父公司ID，0未总公司
    :param deptName: 公司名称
    :param sort: 排序
    :param leader: 负责人
    :param phone: 手机
    :param email: 邮箱
    :param status: 状态 1-打开 0-关闭
    :param address: 地址
    :return: 是否成功
    """
    dept = Dept(
        parent_id=parentId,
        dept_name=deptName,
        sort=sort,
        leader=leader,
        phone=phone,
        email=email,
        status=status,
        address=address
    )
    r = db.session.add(dept)
    db.session.commit()
    if r:
        return True
    else:
        return False


def update(deptId, data):
    """
    更新公司信息

    可更新内容如下::

        "dept_name"
        "sort"
        "leader"
        "phone"
        "email"
        "status"
        "address"

    :param deptId: 公司ID
    :param data: 要更新公司字典
    :return: 是否成功
    """
    d = Dept.query.filter_by(id=deptId).update(data)
    if not d:
        return False
    db.session.commit()
    return True


def delete(deptId):
    """
    删除公司

    :param deptId: 公司ID
    :return: 是否成功
    """
    d = Dept.query.filter_by(id=deptId).delete()
    if not d:
        return False
    res = User.query.filter_by(dept_id=deptId).update({"dept_id": None})
    db.session.commit()
    if res:
        return True
    else:
        return False

