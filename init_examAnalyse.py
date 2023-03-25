import os
import json
import time
import requests

from applications.common.utils.http import table_api, success_api, fail_api
from applications.common.utils.rights import authorize
from applications.common.utils.validate import str_escape

from flask import Blueprint, render_template, request, send_file, session, Response

from .utils import imp_get_dataframe, get_args_safely, student_permissions
from .module import examPublish, student, examAnalyse, setting

# 获取插件所在的目录（结尾没有分割符号）
dir_path = os.path.dirname(__file__).replace("\\", "/")
folder_name = dir_path[dir_path.rfind("/") + 1:]

blueprint = Blueprint('examAnalyse', __name__, url_prefix="/examAnalyse")

@blueprint.get("/")
@authorize("SchoolManager:examAnalyse")
def index():
    """
    后台页面
    """
    grades = student.get_grades()  # 所有届数
    
    return render_template("schoolmanager_examAnalyse/index.html", grades=grades)

@blueprint.route("/average")
@authorize("SchoolManager:examAnalyse")
def exam_average_api():
    """
    获取平均分
    """
    form = request.args.copy()
    success, msg = get_args_safely(form, must_have=['index', 'giveMark'])
    if not success:
        return fail_api(msg)
    
    index = form.get('index')
    giveMark = form.get('giveMark')
    
    if index is None or giveMark is None:
        return fail_api(msg="缺少参数！")
    
    return examAnalyse.get_average(index, giveMark)

@blueprint.route("/specMarkStudent")
@authorize("SchoolManager:examAnalyse")
def exam_specMarkStudent_api():
    """
    获取特控线人数
    """
    form = request.args.copy()
    success, msg = get_args_safely(form, must_have=['grade', 'giveMark'])
    if not success:
        return fail_api(msg)
    
    grade = form.get('grade')
    giveMark = form.get('giveMark')
    
    if grade is None or giveMark is None:
        return fail_api(msg="缺少参数！")
    
    # 获取所有考试数据
    exams = examPublish.get_all_exam("`index`, 考试名称", grade=grade)['data']

    examName = []
    examCount = []
    
    for exam in exams:
        examName.append(exam['考试名称'])
        examCount.append(examAnalyse.get_specMarkStudent(exam['index'], giveMark))
        
    return {'examName': examName, 'examCount': examCount}

@blueprint.route("/specMarkStudent_by_class")
@authorize("SchoolManager:examAnalyse")
def exam_specMarkStudent_by_class_api():
    """
    获取特控线人数
    """
    form = request.args.copy()
    success, msg = get_args_safely(form, must_have=['grade', 'giveMark'])
    if not success:
        return fail_api(msg)
    
    grade = form.get('grade')
    giveMark = form.get('giveMark')
    
    if grade is None or giveMark is None:
        return fail_api(msg="缺少参数！")
    
    # 获取所有考试数据
    exams = examPublish.get_all_exam("`index`, 考试名称", grade=grade)['data']

    examName = []
    examCount = []
    
    for exam in exams:
        examName.append(exam['考试名称'])
        examCount.append(examAnalyse.get_specMarkStudent_by_class(exam['index'], giveMark))
        
    return {'examName': examName, 'examCount': examCount}

@blueprint.route("/getAllExam")
@authorize("SchoolManager:examAnalyse")
def getAllExam_api():
    """
    获取所有考试树
    """
    grades = student.get_grades()  # 所有届数
    
    data = []
    
    for grade in grades:
        
        children = []
        
        # 获取所有考试数据
        exams = examPublish.get_all_exam("`index`, 考试名称", grade=grade)['data']
        
        for exam in exams:
            children.append({
                'title': exam['考试名称'],
                'id': exam['index'],
            })
        
        data.append({
          'title': str(grade) + "届考试",
          'spread': True,
          'children': children
        })
    
    return table_api(msg="success", data=data)
        
@blueprint.route("/countStudent")
@authorize("SchoolManager:examAnalyse")
def countStudent_api():
    """
    获取分数段前人数
    """
    form = request.args.copy()
    success, msg = get_args_safely(form, must_have=['rank', 'index', 'giveMark'])
    if not success:
        return fail_api(msg)
    
    index = form.get('index')
    rank = form.get('rank')
    giveMark = form.get('giveMark')
    
    if index is None or rank is None or giveMark is None:
        return fail_api(msg="缺少参数！")
    
    return examAnalyse.get_countStudent(index, giveMark, rank)


###### 前台成绩查询页面 ######

@blueprint.get("/view")
def view_index():
    """
    前台成绩查询页面
    """
    grades = student.get_grades()  # 所有届数
    
    settings = {
        "标题": setting.get("考试查询", "标题"),
        "提示": setting.get("考试查询", "提示"),
        "公告": setting.get("考试查询", "公告")
    }

    settings['标题'] = settings['标题'] if settings['标题'] not in (None, '') else "学校数据查询"
    settings['提示'] = settings['提示'] if settings['提示'] not in (None, '') else ""
    
    return render_template("schoolmanager_examAnalyse/view_index.html", grades=grades, settings=settings)


@blueprint.post("/view")
def view_api():
    """
    前台成绩查询
    """
    form = request.form.copy()
    success, msg = get_args_safely(form, must_have=['name', 'grade', 'user_answer'])
    if not success:
        return fail_api(msg)
    
    name = str_escape(form.get("name"))
    grade = str_escape(form.get("grade"))
    user_answer = str_escape(form.get("answer"))
    code = form.get('captcha').__str__().lower()
    
    if name is None:
        return fail_api(msg="姓名未提供！")
    
    if grade is None:
        return fail_api(msg="届数未提供或错误！")
    
    s_code = session.get("code", None)
    
    if not all([code, s_code]):
        return fail_api(msg="验证码错误")

    if code != s_code:
        return fail_api(msg="验证码错误")
    
    # 获取学生的查询设置
    student_data = student.get_student_data(name, grade)
    
    if student_data is None:
        return fail_api(msg="数据库中没有这位同学，请确认是否输入正确！")
        
    question = student.get_setting(name, grade, "验证问题")
    anwser = student.get_setting(name, grade, "验证答案")

    # 如果没有设置验证答案
    if anwser is None:
        idc = student_data['身份证号']
        if idc is None or idc == '':
            anwser = None
        else:
            anwser = idc[6:14] 
    
    # 如果没有设置验证问题
    if question is None:
        if anwser is None:
            question = "默认答案是 123456 "
            anwser = "123456"
        else:
            question = "Ta的公历生日是？(eg:2023.1.1->20230101)"

    if user_answer is None:
        return success_api(msg=question)
    
    # 输入了答案
    session["code"] = None  # 更新验证码
        
    if user_answer == anwser:
        session["schoolmanager_name"] = name
        session["schoolmanager_grade"] = str(grade)
        return success_api("验证成功，即将跳转！")
    else:
        return fail_api("验证失败！请再想想！")
    
@blueprint.get("/view/analyse")
def view_analyse():
    """
    成绩分析
    """
    args = request.args.copy()
    success, msg = get_args_safely(args, must_have=['name', 'grade'])
    if not success:
        return fail_api(msg)
    
    grade = args.get('grade')
    name = args.get('name')
    
    if grade is None or name is None:
        return fail_api(msg="没有提供正确的参数。")
    
    if student_permissions("SchoolManager:student", name, grade):
        return render_template("schoolmanager_examAnalyse/view_analyse.html")
    else:
        return "<script>window.location.href = '/schoolmanager/examAnalyse/view'</script>"

@blueprint.get("/view/chatGPTWords_stream")
def view_chatGPTWords_stream():
    """
    AI 激励
    """
    # 获取参数
    args = request.args.copy()
    success, msg = get_args_safely(args, must_have=['name', 'grade', 'giveMark'])
    if not success:
        return fail_api(msg)
    
    grade = args.get('grade')
    name = args.get('name')
    giveMark = args.get('giveMark')
    
    if grade is None or name is None or giveMark is None:
        return fail_api(msg="没有提供正确的参数。")
    
    # 查看一下是否已经生成
    student_setting = student.get_setting(name, grade, None)
    chatGPT_words = student_setting.get("chatGPT_words_" + str(giveMark))
    chatGPT_count = student_setting.get("chatGPT_count_" + str(giveMark))  # 生成时候的考试数量
    
    all_exam_data = examPublish.get_all_exam("`index`", grade=grade)['data']
    
    if chatGPT_count == len(all_exam_data):  # 现在的考试数量
        def generate():
            for chunk in chatGPT_words:  
                time.sleep(0.05)
                yield chunk
        return Response(generate(), mimetype='text/event-stream')

    
    # 生成考试分析，将历次排名与参加考试人数找出来
    ranks = []
    totals = []
    for d in all_exam_data:
        index = d['index']
        _ = examPublish.get_exam(index=index, name=name, giveMark=giveMark)
        exam_data = _['data']
        _ = examPublish.get_exam(index=index, giveMark=giveMark)
        count = _['count']
        if len(exam_data) == 0:
            continue
        ranks.append(exam_data[0]['总分排名'])
        totals.append(count)
    
    # 连接 chatGPT
    prompt = """你是用户的朋友，也是一个成绩分析AI，你需要帮助分析用户的历次排名成绩， 要求：""" + \
        """使用中文聊天，多使用名言或者诗歌来鼓励用户，请不要说诸如“你参加了这次考试”的话，""" + \
        """排名(ranks)越小越好，同时用户还会提供所有参加考试的人数(totals)，你需要结合并给出建议，一定要结合排名，比如排名进退等等。""" + \
        """大概300字，请尽可能鼓励用户，每次参加考试人数与用户历次排名一一对应，最好计算百分比来判断用户所处的水平。"""
    
    api_key = setting.get("考试查询", "openai_key")
    proxy = setting.get("考试查询", "openai_proxy")
    
    if api_key is None or api_key == "":
        return "很抱歉 chatGPT 还未被唤醒！请加油！我们一直都在！"
    
    data = {}
    data['model'] = "gpt-3.5-turbo-0301"
    data['stream'] = True
    data['max_tokens'] = 500
    data['messages'] = []
    data['messages'].append({"role": "system", "content": prompt})
    data['messages'].append({"role": "user", "content": "ranks=" + str(ranks) + \
                        "totals=" + str(totals)})

    data = json.dumps(data)
    
    result = requests.post("https://api.openai.com/v1/chat/completions", 
                  headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + api_key},
                  data=data, proxies={'http': proxy, 'https': proxy}, stream=True)
    
    def generate():
        """还没有生成的生成"""
        content = b""
        full_content = ""
        for chunk in result.iter_content(chunk_size=1):  
            if chunk:
                content += chunk
                if chunk == b"\n":
                    if not (content.decode() == "data: [DONE]\n" or content.decode() == '\n'):
                        try:
                            json_data = json.loads(content.decode().strip("data: ").strip("\n"))
                        except:
                            return f"很抱歉 chatGPT 还未被唤醒！请加油！我们一直都在！"
                        try:
                            if 'content' in json_data['choices'][0]['delta']:
                                full_content += json_data['choices'][0]['delta']['content']
                                yield json_data['choices'][0]['delta']['content']
                        except BaseException as error:
                            return f"很抱歉 chatGPT 还未被唤醒！请加油！我们一直都在！（错误代码：{str(error)}）"
                            
                    elif content.decode() == "data: [DONE]\n":
                        student.set_setting(name, grade, "chatGPT_words_" + str(giveMark), full_content)
                        student.set_setting(name, grade, "chatGPT_count_" + str(giveMark), len(all_exam_data))
                        print("已使用chatGPT生成：", student.get_setting(name, grade, None))
                    content = b""

    return Response(generate(), mimetype='text/event-stream')