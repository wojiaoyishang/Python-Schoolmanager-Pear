import os

import traceback

from applications.common.utils.http import table_api, success_api, fail_api
from applications.common.utils.rights import authorize
from applications.common.utils.validate import str_escape

from flask import Blueprint, render_template, request, session

from .utils import imp_get_dataframe
from .module import examPublish, student, setting

# 获取插件所在的目录（结尾没有分割符号）
dir_path = os.path.dirname(__file__).replace("\\", "/")
folder_name = dir_path[dir_path.rfind("/") + 1:]

blueprint = Blueprint('examPublish', __name__, url_prefix="/examPublish")

@blueprint.get("/")
@authorize("SchoolManager:examPublish")
def index():
    """
    后台页面
    """
    # 获取所有数据库数据
    grades = student.get_grades()  # 所有届数
    if len(grades) == 0:
        classes = []
    else:
        classes = student.get_all_class(grades[0])  # 所有班级（默认第一个年段）
    
    return render_template("schoolmanager_examPublish/index.html", grades=grades, classes=classes)

@blueprint.get("/setting")
@authorize("SchoolManager:examPublish")
def setting_view():
    """
    设置页面
    """
    settings = {
        "标题": setting.get("考试查询", "标题"),
        "提示": setting.get("考试查询", "提示"),
        "公告": setting.get("考试查询", "公告")
    }
    
    settings['标题'] = settings['标题'] if settings['标题'] not in (None, '') else "学校数据查询"
    settings['提示'] = settings['提示'] if settings['提示'] not in (None, '') else ""
    settings['公告'] = settings['公告'] if settings['公告'] not in (None, '') else ""
    
    return render_template("schoolmanager_examPublish/setting.html", settings=settings)

@blueprint.post("/setting")
@authorize("SchoolManager:examPublish")
def setting_api():
    """
    设置页面api
    """
    form = request.form.copy()
    
    form["标题"] = form.get("标题")
    
    if form["标题"] is None:
        form["标题"] = "学校数据查询"
    elif form["标题"].strip() == "":
        form["标题"] = "学校数据查询"
    
    try:
        setting.set("考试查询", "标题", form.get("标题"))
        setting.set("考试查询", "公告", form.get("公告"))
        setting.set("考试查询", "提示", form.get("提示"))
    except BaseException as e:
        return fail_api(msg="设置失败！" + str(e))
        
    return success_api(msg="设置成功！")

@blueprint.get("/imp")
@authorize("SchoolManager:examPublish")
def imp_view():
    """
    考试数据导入页面
    """
    # 获取所有数据库数据
    grades = student.get_grades()  # 所有届数
    
    # 获取所有考试数据
    examNames = [_['考试名称'] for _ in examPublish.get_all_exam("考试名称")['data']]
    
    return render_template("schoolmanager_examPublish/imp.html", grades=grades, examNames=examNames)

@blueprint.get("/info")
@authorize("SchoolManager:examPublish")
def info_view():
    """
    考试数据编辑查看页面
    """
    form = request.args.copy()

    info = examPublish.get_all_exam(fields="*", index=form.get('index'))['data'][0]
    
    grades = student.get_grades()  # 所有届数
    
    classes = student.get_all_class(info['届数'])
    
    return render_template("schoolmanager_examPublish/info.html", grades=grades, info=info, classes=classes)

@blueprint.post("/imp")
@authorize("SchoolManager:examPublish")
def imp():
    """
    考试数据导入接口
    """
    # 这里会传入 args 、 imp 数据 与 ext 数据
    data = request.get_json()
    
    if  data is None:
        return fail_api("不正确的参数！")
    
    if not ('args' in data and 'ext' in data and 'imp' in data):
        return fail_api("不正确的参数！")
    
    # 删除掉不允许的字段
    allow_field = ["姓名", "语文", "数学", "外语", "政治", "历史", "地理", "物理", "化学", "生物", "技术", "备注"]
    
    for field in data['imp'].keys():
        if field not in allow_field:
            del data['imp'][field]
    
    try:
        success, msg = examPublish.imp_data(imp_get_dataframe(args=data['args'], imp=data['imp']), data['ext'])
        # 统计数据
        if success:
            index = examPublish.get_all_exam("`index`", name=str_escape(data['ext'].get("examName", "IlovePikachu")), grade=data['ext'].get("grade", "-1"))['data'][0]['index']
            examPublish.recalc_exam(index)
    except BaseException as e:
        traceback.print_exc()
        return fail_api(msg="导入失败！" + str(e))

    if success:
        return success_api(msg=msg)
    else:
        return fail_api(msg=msg)

@blueprint.post("/data")
@authorize("SchoolManager:examPublish")
def data():
    """
    表格数据
    """
    page = int(request.form.get('page', 0))
    limit = int(request.form.get('limit', 10))
    
    grade = request.form.get('grade', '')
    name = str_escape(request.form.get('name'))
    startDate = request.form.get('startDate', '')
    endDate = request.form.get('endDate', '')
    
    
    # 判断提供参数正确
    if not grade.isdigit() or grade == '':
        grade = None
    
    if not startDate.isdigit() or startDate == '':
        startDate = None
    
    if not endDate.isdigit() or endDate == '':
        endDate = None
    
    try:
        return table_api(msg="success", **examPublish.get_all_exam(fields="*", grade=grade, page=page, limit=limit, 
                                                                   name=name, startDate=startDate, endDate=endDate))
    except BaseException as e:
        traceback.print_exc()
        return fail_api(msg="没有提供正确的参数！" + str(e))
    
@blueprint.post("/delete")
@authorize("SchoolManager:examPublish")
def delete():
    """
    删除考试数据
    """
    form = request.form.copy()
    
    # 处理数据
    if not form.get("grade", "-1").isdigit():
        return fail_api("届数错误。")
    
    if form.get("name", "").strip() == "":
        return fail_api("姓名未提供。")
    
    try:
        examPublish.delete_exam(**form)
        return success_api("数据删除成功。")
    except BaseException as e:
        traceback.print_exc()
        return fail_api("数据删除失败！" + str(e))
    
@blueprint.post("/add")
@authorize("SchoolManager:examPublish")
def add():
    """
    添加考试数据
    """
    form = request.form.copy()

    # 处理数据
    if not form.get("grade", "-1").isdigit():          
        return fail_api("届数错误。")
    if int(form.get("grade", "-1")) not in student.get_grades():
            return fail_api("届数不存在。")   
    
    try:
        success, msg = examPublish.add_exam(**form)
    except BaseException as e:
        traceback.print_exc()
        return fail_api(msg="创建失败！" + str(e))

    if success:
        return success_api(msg=msg)
    else:
        return fail_api(msg=msg)
    
@blueprint.post("/update")
@authorize("SchoolManager:examPublish")
def update():
    """
    更新考试信息
    """
    form = request.form.copy()

    
    # 处理数据
    if not form.get("届数", "-1").isdigit():    
        return fail_api("届数错误。")
    if int(form.get("届数", "-1")) not in student.get_grades():
            return fail_api("届数不存在。")   

    try:
        success, msg = examPublish.set_exam_info(**form)
    except BaseException as e:
        traceback.print_exc()
        return fail_api(msg="创建失败！" + str(e))

    if success:
        return success_api(msg=msg)
    else:
        return fail_api(msg=msg)
    
    
@blueprint.post("/exam/data")
@authorize("SchoolManager:examPublish")
def exam_data():
    """
    获取成绩信息
    """
    form = request.form.copy()

    # 处理数据
    if not form.get("index", "-1").isdigit():    
        return fail_api("考试ID错误。") 

    limit = int(form.get("limit"))
    page = int(form.get("page"))
    
    
    index = int(form.get("index"))
    class_ = form.get("class")
    if class_ in (None, ""):
        class_ = None

    name = str_escape(form.get("name"))
    if name in (None, ''):
        name = None
        
    # 查询设置
    setting = form.get("setting", '').split(",")
    
    # 获取赋分成绩
    giveMark = '查看赋分成绩' in setting
    
    # 降序
    ascending = '降序' not in setting

    try:
        examPublish.recalc_exam(index)
        return table_api(msg="success", **examPublish.get_exam(index=index, giveMark=giveMark, limit=limit, page=page, 
                                                               name=name, class_=class_,
                                                               ascending=ascending))
    except BaseException as e:
        traceback.print_exc()
        return fail_api(msg="出现错误！" + str(e))

@blueprint.post("/exam/update")
@authorize("SchoolManager:examPublish")
def exam_update():
    """
    更新一条成绩信息
    """
    form = request.get_json()
    
    if  data is None:
        return fail_api("不正确的参数！")
    
     
    try:
        index = int(form.get("index"))
    except BaseException as e:
        return fail_api("考试ID错误。") 
        
    if 'data' not in form:
        return fail_api(msg="参数错误！")

    # 处理允许的字段
    fields = ['姓名', '赋分', '语文', '数学', '外语', '政治', '历史', '地理', '物理', '化学', '生物', '技术', '备注']
    
    for f in list(form['data'].keys()):
        if f not in fields:
            del form['data'][f]
    
    form['data']['赋分'] = 1 if form['data']['赋分'] == "是" else 0
    
    try:
        examPublish.update_exam_data(index=index, data=form['data'])
        return success_api(msg="成功数据成功！")
    except BaseException as e:
        return fail_api(msg="出现错误！" + str(e))


@blueprint.post("/exam/delete")
@authorize("SchoolManager:examPublish")
def exam_delete():
    """
    删除一条成绩信息
    """
    form = request.get_json()
    
    if  data is None:
        return fail_api("不正确的参数！")
    
     
    try:
        index = int(form.get("index"))
    except BaseException as e:
        return fail_api("考试ID错误。") 
        
    if 'data' not in form:
        return fail_api(msg="参数错误！")
    
    form['data']['赋分'] = 1 if form['data']['赋分'] == "是" else 0
    
    try:
        examPublish.delete_exam_data(index=index, data=form['data'])
        return success_api(msg="成功数据成功！")
    except BaseException as e:
        return fail_api(msg="出现错误！" + str(e))

@blueprint.post("/studentExams")
def studentExams():
    """
    表格数据
    """
    grade = request.form.get('grade', '')
    name = str_escape(request.form.get('name'))
    giveMark = request.form.get('giveMark', '1') == '1'
    
    # 判断提供参数正确
    if not grade.isdigit() or grade == '':
        grade = None

    try:
        if ("SchoolManager:examPublish" in session.get('permissions', [])) or (session.get("schoolmanager_name") == name and session.get("schoolmanager_grade") == grade):
            # 获取所有考试
            exams = examPublish.get_all_exam(fields="`index`, 考试名称", grade=grade, page=None, limit=None)['data']
            data = []
            for d in exams:
                index, exam_name = d['index'], d['考试名称']
                _ = examPublish.get_exam(index=index, name=name, giveMark=giveMark)['data']
                if len(_) == 0:
                    continue
                _[0]['考试名称'] = exam_name
                data.append(_[0])
            return table_api(msg="success", data=data)
        else:
            return fail_api(msg="没有权限！")
    except BaseException as e:
        traceback.print_exc()
        return fail_api(msg="没有提供正确的参数！" + str(e))