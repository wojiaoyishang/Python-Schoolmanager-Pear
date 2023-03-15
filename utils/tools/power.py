"""
集成了对 Pear Admin Flask 的权限操作，并给了相对应的示例。
注意：此权限相当于添加后台菜单。
"""

from applications.common import curd
from applications.extensions import db
from applications.models import Power

from applications.extensions import ma
from marshmallow import fields


class PowerOutSchema2(ma.Schema):  # 序列化类
    powerId = fields.Str(attribute="id")
    powerName = fields.Str(attribute="name")
    powerType = fields.Str(attribute="type")
    powerUrl = fields.Str(attribute="url")
    powerCode = fields.Str(attribute="code")
    openType = fields.Str(attribute="open_type")
    parentId = fields.Str(attribute="parent_id")
    icon = fields.Str()
    sort = fields.Integer()
    create_time = fields.DateTime()
    update_time = fields.DateTime()
    enable = fields.Integer()


def get_all():
    """
    获取所有权限，会返回一个含有菜单的列表。每个列表都是一个字典。

    字典构成如下::
        {
            "powerType": "0",  # 权限类型 0目录 1菜单 2按钮
            "powerUrl": None,  # 路径
            "powerCode": "",  # 权限标识
            "update_time": None,  # 更新时间
            "sort": 1,  # 排序
            "openType": None,  # 打开方式 _iframe框架 _blank新页面
            "icon": "layui-icon layui-icon-set-fill",  # 图标
            "powerName": "系统管理",  # 名称
            "create_time": None,  # 创建时间
            "parentId": "0",  # 父id
            "powerId": "1",  # 自己的id
            "enable": 1  # 是否启用
        }

    :return: 菜单列表。
    """
    power = Power.query.all()
    res = curd.model_to_dicts(schema=PowerOutSchema2, data=power)
    res.append({"powerId": 0, "powerName": "顶级权限", "parentId": -1})
    return res


def add(parentId, powerName, powerType, icon, sort: int, enable: bool, powerCode="", powerUrl="", openType=""):
    """
    新建一个菜单权限。

    参考代码::

        power.add("0", "测试", "1", "layui-icon-time", 0, True, "testfor", "https://baidu.com", "_iframe")

    :param parentId: 父ID，0为顶级菜单ID
    :param powerName: 菜单名称
    :param powerType: 权限类型（状态） 0目录 1菜单 2按钮
    :param icon: 图标，详细查看layui的图标
    :param sort: 排序
    :param enable: 是否启用

    :param powerCode: 权限标识
    :param powerUrl: 权限URL，菜单打开的网址，或者是路径。可选，菜单和按钮类型必填。
    :param openType: 打开方式，_iframe框架 _blank新页面。可选，菜单和按钮类型必填。



    :return: 返回新权限ID
    """
    power = Power(
        icon=icon,
        open_type=openType,
        parent_id=parentId,
        code=powerCode,
        name=powerName,
        type=powerType,
        url=powerUrl,
        sort=sort,
        enable=1
    )
    r = db.session.add(power)
    db.session.commit()
    return power.id


def update(powerId, data):
    """
    更新权限。

    data可选::

        "icon"
        "open_type"
        "parent_id"
        "code"
        "name"
        "type"
        "url"
        "sort"

    :param powerId: 要更新的权限ID

    :return: 是否成功
    """
    res = Power.query.filter_by(id=powerId).update(data)
    db.session.commit()
    if res:
        return True
    else:
        return False


def delete(powerId):
    """
    删除权限。

    :param powerId: 要更新的权限ID
    :return: 是否成功
    """
    power = Power.query.filter_by(id=powerId).first()
    power.role = []

    r = Power.query.filter_by(id=powerId).delete()
    db.session.commit()
    if r:
        return True
    else:
        return False
