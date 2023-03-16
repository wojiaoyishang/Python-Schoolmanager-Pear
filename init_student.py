import os
import json
import traceback

from applications.common.utils.http import table_api, success_api, fail_api
from applications.common.utils.rights import authorize
from applications.common.utils.validate import str_escape

from flask_login import current_user
from flask import Blueprint, render_template, request, send_file, session

from .utils import imp_get_dataframe
from .module import student

# 获取插件所在的目录（结尾没有分割符号）
dir_path = os.path.dirname(__file__).replace("\\", "/")
folder_name = dir_path[dir_path.rfind("/") + 1:]

blueprint = Blueprint('student', __name__, url_prefix="/student")

@blueprint.get("/")
@authorize("SchoolManager:student")
def index():
    """
    学生管理主页面
    """
    # 获取所有数据库数据
    grades = student.get_grades()  # 所有届数
    if len(grades) == 0:
        classes = []
    else:
        classes = student.get_all_class(grades[0])  # 所有班级（默认第一个年段）
    
    return render_template("schoolmanager_student/index.html", grades=grades, classes=classes)

@blueprint.get("/photo")
@authorize("SchoolManager:student")
def photo_view():
    """
    学生证件照主页面
    """
    grades = student.get_grades()
    if len(grades) == 0:
        return fail_api("No grade.")
    grade = request.args.get('grade', str(grades[0]))
    name = str_escape(request.args.get('name'))
    
    return render_template("schoolmanager_student/photo.html", grade=grade, name=name)

@blueprint.get("/photo/view")
def photo():
    """
    学生证件照
    """
    grades = student.get_grades()
    if len(grades) == 0:
        return fail_api("No grade.")
    grade = request.args.get('grade', str(grades[0]))
    name = str_escape(request.args.get('name'))
    
    if name is None:
        return fail_api(msg="Bad name.")
    
    if not "SchoolManager:student" in session.get('permissions', []) or (session.get("schoolmanager_name") == name and int(session.get("schoolmanager_grade")) == grade):
    
        name = name.replace("/", "").replace("\\", "").replace(".", "")
        
        photo_path = dir_path + f"/data/photos/{grade}/{name}.jpg"
        if not os.path.exists(photo_path):
            return fail_api("No image found.")
    
        return send_file(photo_path)
    
    return fail_api("没有权限！")

@blueprint.post("/photo/upload")
@authorize("SchoolManager:student")
def photo_upload():
    """
    学生证件照上传
    """
    try:
        grade = request.form.get('grade')
        name = str_escape(request.form.get('name'))
        
        if name is None or grade is None or not grade.isdigit():
            return {
                "code": -1,
                "msg": str("bad name or grade!")
            }    
        
        name = name.replace("/", "").replace("\\", "").replace(".", "")
        
        # 判断保存文件夹是否存在
        if not os.path.exists(dir_path + f"/data/photos/{grade}"):
            os.mkdir(dir_path + f"/data/photos/{grade}")
        
        f = request.files['file']
        ext = os.path.splitext(f.filename)[1]
        if ext.lower() not in ['.jpg', '.png']:
            return {
                "code": -1,
                "msg": str("bad filename!")
            }
            
        f.save(dir_path + f"/data/photos/{grade}/{name}.jpg")
        return {
                "code": 0,
                "msg": "上传成功！",
                "data": {}
            }    
    except BaseException as error:
        return {
                "code": -1,
                "msg": str(error)
            }    

@blueprint.get("/imp")
@authorize("SchoolManager:student")
def imp_view():
    """
    学生管理导入页面
    """
    # 获取所有数据库数据
    grades = student.get_grades()  # 所有届数
    
    return render_template("schoolmanager_student/imp.html", grades=grades)

@blueprint.post("/imp")
@authorize("SchoolManager:student")
def imp():
    """
    学生管理导入接口
    """
    # 这里会传入 args 、 imp 数据 与 ext 数据
    data = request.get_json()
    if  data is None:
        return fail_api("不正确的参数！")
    
    if not ('args' in data and 'ext' in data and 'imp' in data):
        return fail_api("不正确的参数！")
    
    # 删除掉不允许的字段
    allow_field = ['姓名', '性别', '班级', '寝室', '选科', '身份证号', '毕业学校', '家庭住址', '备注']
    
    for field in data['imp'].keys():
        if field not in allow_field:
            del data['imp'][field]
    
    try:
        success, msg = student.imp_data(imp_get_dataframe(args=data['args'], imp=data['imp']), data['ext'])
    except BaseException as e:
        return fail_api(msg="导入失败！" + str(e))
        
    if success:
        return success_api(msg=msg)
    else:
        return fail_api(msg=msg)


@blueprint.post("/data")
@authorize("SchoolManager:student")
def data():
    """
    表格数据
    """
    page = int(request.form.get('page', 0))
    limit = int(request.form.get('limit', 10))
    
    grades = student.get_grades()
    if len(grades) == 0:
        return fail_api("没有年段。")
    grade = request.form.get('grade', str(grades[0]))
    class_ = request.form.get('class', "0")
    name = str_escape(request.form.get('name'))
    
    # 判断提供参数正确
    if grade.isdigit():
        grade = int(grade)
    else:
        return fail_api(msg="没有提供正确的届数！")
    
    if class_.isdigit():
        class_ = int(class_)
    else:
        return fail_api(msg="没有提供正确的班级！")
    
    try:
        return table_api(msg="success", **student.get_students_data(grade, fields="姓名,性别,班级", class_=class_, name=name, page=page, limit=limit))
    except BaseException as e:
        return fail_api(msg="没有提供正确的参数！" + str(e))
        
@blueprint.get("/get")
def get():
    """
    学生数据
    """
    name = request.args.get('name')
    grade = request.args.get('grade', '-1')
    
    if not grade.isdigit():
        return fail_api(msg="没有提供正确的参数。")
    
    if name is None:
        return fail_api(msg="没有提供正确的参数。")

    try:
        if not "SchoolManager:student" in session.get('permissions', []) or (session.get("schoolmanager_name") == name and int(session.get("schoolmanager_grade")) == grade):
            student_data = student.get_student_data(name, grade)
            
            if student_data['查询设置'] in (None, ''):
                student_data['查询设置'] = {}
            else:
                student_data['查询设置'] = json.loads(student_data['查询设置'])
            
            question = student_data['查询设置'].get("验证问题")
            anwser = student_data['查询设置'].get("验证答案")

            student_data['查询设置']['验证问题'] = question
            student_data['查询设置']['验证答案'] = anwser
            
            student_data['查询设置'] = json.dumps(student_data['查询设置'])
        
            
            
            return table_api(msg="success", data=student_data)
        else:
            return fail_api(msg="没有权限！")
    except BaseException as e:
        traceback.print_exc()
        return fail_api(msg="没有提供正确的参数！" + str(e))

@blueprint.post("/update")
@authorize("SchoolManager:student")
def update():
    """
    更新学生数据
    """
    form = request.form.copy()
    
    # 处理数据
    if not form.get("届数", "-1").isdigit():
        return fail_api("届数错误。")
    
    if form.get("姓名", "").strip() == "":
        return fail_api("姓名未提供。")
    
    if form.get("性别", "0").isdigit() or form.get("性别", "0") == "-1":
        form['性别'] = int(form.get("性别", "0"))
    else:
        return fail_api("性别错误。")
    
    if form.get("班级", "0").isdigit() or form.get("班级", "0") == "-1":
        form['班级'] = int(form.get("班级", "0"))
    else:
        return fail_api("班级错误。")
    
    # 处理选科
    form['选科'] = form.get('选科', "语数外")
    subjects = ""
    all_subjects = "语数外政史地物化生技"
    for s in all_subjects:
        if s in form['选科']:
            subjects += s
    
    form['选科'] = subjects
    
    try:
        student.set_student_data(**form)
        return success_api("数据更新成功。")
    except BaseException as e:
        return fail_api("更新数据失败！" + str(e))

@blueprint.post("/add")
@authorize("SchoolManager:student")
def add():
    """
    添加学生数据
    """
    form = request.form.copy()
    
    # 处理数据
    if not form.get("届数", "-1").isdigit():
        return fail_api("届数错误。")
    
    if form.get("姓名", "").strip() == "":
        return fail_api("姓名未提供。")
    
    if form.get("性别", "0").isdigit() or form.get("性别", "0") == "-1":
        form['性别'] = int(form.get("性别", "0"))
    else:
        return fail_api("性别错误。")
    
    if form.get("班级", "0").isdigit() or form.get("班级", "0") == "-1":
        form['班级'] = int(form.get("班级", "0"))
    else:
        return fail_api("班级错误。")
    
    
    
    # 处理选科
    form['选科'] = form.get('选科', "语数外")
    subjects = ""
    all_subjects = "语数外政史地物化生技"
    for s in all_subjects:
        if s in form['选科']:
            subjects += s
    
    form['选科'] = subjects
    
    try:
        student.add_student_data(**form)
        return success_api("数据添加成功。")
    except BaseException as e:
        return fail_api("数据添加失败！" + str(e))
    
    
@blueprint.post("/delete")
@authorize("SchoolManager:student")
def delete():
    """
    删除学生数据
    """
    form = request.form.copy()
    
    # 处理数据
    if not form.get("届数", "-1").isdigit():
        return fail_api("届数错误。")
    
    if form.get("姓名", "").strip() == "":
        return fail_api("姓名未提供。")
    
    try:
        student.delete_student_data(**form)
        return success_api("数据删除成功。")
    except BaseException as e:
        return fail_api("数据删除失败！" + str(e))
    
@blueprint.post("/grade/add")
@authorize("SchoolManager:student")
def add_grade():
    """
    新建年段
    """
    form = request.form.copy()
    
    # 处理数据
    if not form.get("grade", "-1").isdigit():
        return fail_api("届数错误。")

    grade = int(form.get("grade"))
    
    try:
        student.add_grade(grade)
        return success_api("添加年段成功。")
    except BaseException as e:
        return fail_api("添加年段失败！" + str(e))
    
    
@blueprint.post("/grade/remove")
@authorize("SchoolManager:student")
def delete_grade():
    """
    删除年段
    """
    form = request.form.copy()
    
    # 处理数据
    if not form.get("grade", "-1").isdigit():
        return fail_api("届数错误。")

    grade = int(form.get("grade"))
    
    try:
        student.delete_grade(grade)
        return success_api("删除年段成功。")
    except BaseException as e:
        return fail_api("删除年段失败！" + str(e))

@blueprint.get("/setting")
def setting():
    """
    设置查询问题
    """
    name = request.args.get('name')
    grade = request.args.get('grade', '-1')
    
    if not grade.isdigit():
        return fail_api(msg="没有提供正确的参数。")
    
    if name is None:
        return fail_api(msg="没有提供正确的参数。")
    
    try:
        if not "SchoolManager:student" in session.get('permissions', []) or (session.get("schoolmanager_name") == name and int(session.get("schoolmanager_grade")) == grade):
            question = request.args.get('question', None)
            answer = request.args.get('answer', None)
            if question in (None, '') or answer in (None, ''):
                return fail_api("验证问题或者密码不能为空！")
            print(question, answer)
            student.set_setting(name, grade, '验证问题', question)
            student.set_setting(name, grade, '验证答案', answer)
            return success_api("设置成功！")
        else:
            return fail_api("没有权限。")
    except BaseException as e:
        traceback.print_exc()
        return fail_api("出现错误！" + str(e))
    