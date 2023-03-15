"""
集成了对 Pear Admin Flask 的用户操作，并给了相对应的示例。

调用示例::

    user.login_required # 用户是否登录
    user.current_user  # 当前登录用户
    user.authorize("XXX", log=True)  # 用户是否有此权限

"""

from applications.extensions import db
from applications.models import Role
from applications.models import User


def filter_by(**kwargs):
    """
    用于在用户数据中查询用户信息，可以通过用户名、用户id等进行检索。（建议使用id检索）
    内部采用的是使用 User.query.filter_by(**kwargs) 进行数据库查询

    注意：此函数返回的结果为构造的 SQL的查询字符串 ，以 user_filter 命名，但是并不是用户数据。

    返回的字段如下::

        id username password_hash create_at update_at
        enable realname remark avatar dept_id
        具体参考 applications/models/admin_user.py 中的模型定义。


    参考调用如下::

        userinfo = user.filter_by(username='admin').first()  # 查询符合要求的第一个用户
        print(userinfo.realname)  # 获取用户真实名字


    :param kwargs: 查询参数
    :return: 用户数据SQL的查询字符串
    """
    return User.query.filter_by(**kwargs)


def update(user_filter, data):
    """
    更新用户数据，修改将直接保存到数据库中。
    注意：更新用户角色(role)请使用 user.update_role() 函数。

    可更新的字段如下::

        id username password_hash create_at update_at
        enable realname remark avatar dept_id
        具体参考 applications/models/admin_user.py 中的模型定义。

    参考调用如下::

        user_filter = user.filter_by(id=0)  # 获取指定用户ID的用户，注意不要使用会引起歧义的查询条件，否则会匹配到多个用户。
        user.update(user_filter, {username: 'admin'})  # 更新其用户名



    :param user_filter: user.filter_by() 的结果。
    :param data: 要更新的数据，必须是字典。
    :return: None
    """
    user_filter.update(data)
    db.session.commit()


def update_role(user_filter, roleIds):
    """
    更新用户角色，修改将直接保存到数据库中。

    参考调用如下::

        user_filter = user.filter_by(username='test')  # 获取符合要求的第一个用户
        roleIds = []
        roleIds.append(role.filter_by(code='admin').first().id)  # 管理员角色ID
        roleIds.append(role.filter_by(code='common').first().id)  # 普通用户角色ID
        user.update_role(user_filter, roleIds)


    :param user_filter: user.filter_by() 的结果。
    :param roleIds: 要更新的角色ID，作为列表传入。
    :return: None
    """
    user_filter.first().role = Role.query.filter(Role.id.in_(roleIds)).all()
    db.session.commit()


def get_role(user_filter):
    """
    获取用户的所有角色ID，将会返回一个整数列表。

    :param user_filter: user.filter_by() 的结果。
    :return: 列表 (roleIds)
    """
    checked_roles = []
    for r in user_filter.first().role:
        checked_roles.append(r.id)
    return checked_roles


def set_password(user_filter, password):
    """
    设置用户密码，此函数不会验证用户原始密码哈希值，直接写入新密码哈希值。

    参考调用如下::

        user_filter = user.filter_by(username='admin')  # 获取符合要求的用户
        user.set_password(user_filter, 'admin')  # 设置密码

    :param user_filter: user.filter_by() 的结果。
    :param password: 新密码。
    :return: None
    """
    user = user_filter.first()
    user.set_password(password)
    db.session.add(user)
    db.session.commit()


def add(username, realname, password, roleIds):
    """
    添加一个新用户。函数会判断用户名是否已存在，存在返回 False ，成功返回用户数据(userinfo)。此函数会直接写入数据库。
    注意：此函数创建出来的用户默认是禁用的，可以使用 enable 启用。

    :param username: 新用户名
    :param realname: 真实名字
    :param password: 密码字符串
    :param roleIds: 角色id列表，如 [1, 2]，角色id具体查看 dev.role.get_all() 函数。
    :return: 是否成功
    """
    if bool(User.query.filter_by(username=username).count()):
        return False
    user = User(username=username, realname=realname)
    user.set_password(password)
    db.session.add(user)
    roles = Role.query.filter(Role.id.in_(roleIds)).all()
    for r in roles:
        user.role.append(r)
    db.session.commit()
    return user


def delete(user_filter):
    """
    删除一个用户。此函数立刻写入数据库。

    :param user_filter: user.filter_by() 的结果。
    :return: 是否成功
    """
    user = user_filter.first()
    user.role = []
    res = user_filter.delete()
    db.session.commit()
    return res



