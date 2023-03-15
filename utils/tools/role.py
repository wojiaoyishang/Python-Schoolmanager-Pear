"""
集成了对 Pear Admin Flask 的角色操作，并给了相对应的示例。
"""
from applications.extensions import db
from applications.models import Role, Power
from applications.schemas import PowerOutSchema2


def filter_by(**kwargs):
    """
    检索角色字段信息，可用于获取角色ID等。系统中默认管理员角色id为1，普通用户为2。
    内部采用的是使用 Role.query.filter_by(**kwargs) 进行数据库查询。

    注意：此函数返回的结果为构造的 SQL的查询字符串 ，以 role_filter 命名，但是并不是用户数据。

    返回的字段如下::

        id name code enable remark details sort create_time update_time power
        具体参考 applications/models/admin_role.py 中的模型定义。

    参考调用如下::

        roleinfo = role.filter_by(code='admin').first()  # 第一个符合要求的角色信息
        print(role.id, role.name)  # 输出角色名称与角色标识

        # 找出所有角色id
        for role in role.filter_by().all():
            print(role.id, role.name)

    :param kwargs: 查询参数
    :return: 角色SQL的查询字符串
    """
    return Role.query.filter_by(**kwargs)


def add(roleName, roleCode, enable, sort, details):
    """
    添加一个角色。此函数直接写入数据库。此函数不会检测角色是否已经存在（官方在API接口中也没有检测）。

    :param roleName: 角色名称 (如管理员)
    :param roleCode: 角色标识 (如admin)
    :param enable: 是否启用 True or False
    :param sort: 排序
    :param details: 描述
    :return: None
    """
    role = Role(
        details=details,
        enable=enable,
        code=roleCode,
        name=roleName,
        sort=sort
    )
    db.session.add(role)
    db.session.commit()


def get_power(role_filter, detail=False, p=0):
    """
    获取角色的权限。

    如果是非详细数据，会返回一个含有权限id的列表。
    如果是详细数据返回此函数，将会返回一个列表，列表中会包含字典，字典的键如下::

        {
            "checkArr": "1", # 是否有权限 1 为有 0为无
            "create_time": null, # 权限创建
            "enable": 1, # 权限是否启用
            "icon": "layui-icon layui-icon-set-fill", # 权限图标
            "openType": null,  # 开启状态
            "parentId": "0",  # 父权限ID
            "powerId": "1",  # 权限ID
            "powerName": "系统管理",  # 权限名称
            "powerType": "0",  # 权限类型
            "powerUrl": null,  # 权限URL
            "sort": 1,  # 权限排序
            "update_time": null  # 权限更新时间
        }


    :param role_filter: role.filter_by() 返回结果。
    :param detail: 返回详细数据
    :param p: 如果有多个结果被找到，p可以确定使用第几个结果。内部使用 role_filter.all()[p]
    :return: 用户拥有的权限列表。
    """
    role = role_filter.all()[p]
    check_powers = role.power
    check_powers_list = []
    for cp in check_powers:
        check_powers_list.append(cp.id)
    if not detail:
        return check_powers_list
    powers = Power.query.all()
    power_schema = PowerOutSchema2(many=True)  # 用已继承ma.ModelSchema类的自定制类生成序列化类
    output = power_schema.dump(powers)  # 生成可序列化对象
    for i in output:
        if int(i.get("powerId")) in check_powers_list:
            i["checkArr"] = "1"
        else:
            i["checkArr"] = "0"
    return output


def set_power(role_filter, powerIds, p=0):
    """
    保存角色权限。此函数会直接写入数据库。

    :param role_filter: role.filter_by() 返回结果。
    :param powerIds: 必须是一个包含权限ID的列表。如 [1, 2, 3]
    :param p: 如果有多个结果被找到，p可以确定使用第几个结果。内部使用 role_filter.all()[p]
    :return: None
    """
    role = role_filter.all()[p]
    powers = Power.query.filter(Power.id.in_(powerIds)).all()
    role.power = powers

    db.session.commit()


def update(role_filter, data):
    """
    更新角色数据。此功能将直接写入数据库。

    可更新的字段如下::

        id name code enable remark details sort create_time update_time power
        具体参考 applications/models/admin_role.py 中的模型定义。

    参考调用如下::

        role_filter = role.filter_by(id=0)  # 获取指定角色ID的角色，注意不要使用会引起歧义的查询条件，否则会匹配到多个角色。
        role.update(role_filter, {enable: 0})  # 禁用

    :param role_filter: role.filter_by() 返回结果。
    :param data: 要更新的数据，必须是字典。
    :return: None
    """
    role_filter.update(data)
    db.session.commit()


def delete(role_filter):
    """
    删除角色。此功能将直接写入数据库。

    :param role_filter: role.filter_by() 返回结果。
    :return: 是否成功。
    """
    role = role_filter.first()
    # 删除该角色的权限和用户
    role.power = []
    role.user = []

    r = role_filter.delete()
    db.session.commit()
    return r

