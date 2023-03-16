# Python Schoolmanager Pear

## 项目介绍与设计理念
这是一个基于 Python Flask 的学校数据管理插件，后台界面采用开源项目 Pear Admin Flask，并且以插件的形式接入 Pear Admin Flask。

随着信息化的推进，学校数据管理的需求越来越高，如何有效地收集、分析和利用学校数据，提高教育质量和效率，是一个亟待解决的问题。为此，我开发了一个基于 Python Flask 的学校数据管理插件，旨在为学校提供一个简单、灵活、安全的数据管理平台。

我们学校经常和其他学校一起举办考试，考完后，如何对联合体的成绩进行分析和评价是一个重要的问题。对于老师，处理成绩，一直是一个头疼的问题，它通常耗时间耗经历。对于同学，如何查看历次考试的成绩、如何分析考试成绩，也是一个问题。为此我开始筹划“学校数据管理系统”的编写。

此项目使用 SQLite3 作为数据库存储数据，并采用 Jinja2 作为模板引擎渲染页面。此外，此项目还支持用户验证和权限控制，保证了数据的安全性。

我的设计理念是：简单而不简陋，灵活而不混乱。我希望通过我的插件，能够帮助学校实现高效、便捷、智能的数据管理。

## 项目说明
项目基于我参与开发的 [Pear Admin Flask](https://gitee.com/pear-admin/pear-admin-flask)，但是并**不修改原项目**，而是以插件的形式接入。当今时代，开源共建为热门话题，越来越多的企业和个人参与到开源项目中，分享自己的代码和经验，共同推动技术创新和社会进步。开源共建不仅能够提高软件质量和安全性，还能够激发创造力和协作精神，形成良好的生态环境，而此项目以插件的形式接入有利于项目的二次开发。

所以在搭建项目前，可以参考 [Pear Admin Flask 配置搭建](https://pear-admin.gitee.io/pear-admin-site/doc/index.html) 的相关内容。

**采用 Python 版本：** ```3.8.6```  _在开发项目时，推荐使用 >= 3.8.6 的 Python 运行此项目_ 

**采用 IDE：** ```Visual Studio Code```  _推荐使用 Visual Studio Code、PyCharm 等IDE开发_ 

## 快速预览

|  |  |
|---------------------|---------------------|
|![输入图片说明](images/image1.png)| ![输入图片说明](images/image2.png) |
|![输入图片说明](images/image3.png)| ![输入图片说明](images/image4.png) |
|![输入图片说明](images/image5.png)| ![输入图片说明](images/image6.png) |
|![输入图片说明](images/image7.png)|![输入图片说明](images/image8.png) |


## 设计计划


- [X] 后台学生信息管理
- [X] 后台成绩发布功能
- [X] 后台成绩基本分析功能
- [X] Excel 导入功能
- [X] 前台学生成绩基本查询与成绩分析
- [ ] 前台学生各次考试分析
- [ ] 学生 PK 功能（学生与学生对比）
- [ ] 历次考试对比功能（考试与考试对比）
- [ ] Excel 导出功能
- [ ] 多学校管理功能

## 安装教程

### 安装 Python

安装 Python 过程不过多赘述，请到 [Python 官网](https://www.python.org/) 下载。如果您不想要复杂的安装步骤，我们推荐使用**虞颖健**老师打包的 [Python 懒人版](https://gitee.com/yu-yingjian/day_day_up?_from=gitee_search)。点击查看 --> [视频安装教程](https://www.bilibili.com/video/BV1Vd4y197se/?spm_id_from=333.999.0.0)

### 搭建 Pear Admin Flask

Pear Admin Flask 的搭建步骤详细可以参考其官方文档，这里进行摘录（注意：此插件是基于 **Pear Admin Flask master** 分支的）：

#### 环境要求
- Python >= 3.6
- Mysql >= 5.7.0

#### 克隆远程仓库

您可以使用 git 来克隆远程仓库：

```shell
# 进入项目主目录
cd Pear Admin Flask

# 使用 git 克隆远程仓库
git clone https://gitee.com/pear-admin/pear-admin-flask.git

# 切换分支
git checkout master  # master, main or mini
```

或者直接前往 Pear Admin Flask 项目的[Gitee 主页](https://gitee.com/pear-admin/pear-admin-flask)下载项目仓库。

#### 搭建开发环境

我们推荐使用 Python 的虚拟环境来开发该项目，这样便于项目的迁移与二次开发。当然，您也可以选择使用原 Python 环境。

如果你想创建 Python 虚拟环境，你可以使用下面的命令行：

```shell
# 在当前目录的venv文件夹创建虚拟环境
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate
```

**如果在创建虚拟环境时报错 “ModuleNotFoundError” ，这说明您的 Python 版本小于 3.3 。**

#### 安装项目依赖

```shell
# 使用 pip 安装必要模块（对于 master 分支）
pip install -r requirement\requirement.txt
```

或者您可以尝试：

```shell
# 使用 pip 安装必要模块（对于 master 分支）
python -m pip install -r requirement\requirement.txt
```

### 安装学校数据管理插件（Python Schoolmanager Pear）

克隆此仓库的所有文件到 Pear Admin Flask 的 plugins/SchoolManager 文件夹下（需要手动创建 SchoolManager 文件夹），并在 ```.flaskenv``` 文件中做如下修改：

```
# 插件配置
PLUGIN_ENABLE_FOLDERS = ["helloworld"]
```

添加（或替换上）```SchoolManager```，如：

```
# 插件配置
PLUGIN_ENABLE_FOLDERS = ["helloworld", "SchoolManager"]
```

**注意：如果文件夹不是“SchoolManager”，则需要修改上述的名称为您创建的文件夹的名称。**


## 使用说明

1.  xxxx
2.  xxxx
3.  xxxx

## 参与贡献

1.  Fork 本仓库
2.  新建 Feat_xxx 分支
3.  提交代码
4.  新建 Pull Request


## 特技

1.  使用 Readme\_XXX.md 来支持不同的语言，例如 Readme\_en.md, Readme\_zh.md
2.  Gitee 官方博客 [blog.gitee.com](https://blog.gitee.com)
3.  你可以 [https://gitee.com/explore](https://gitee.com/explore) 这个地址来了解 Gitee 上的优秀开源项目
4.  [GVP](https://gitee.com/gvp) 全称是 Gitee 最有价值开源项目，是综合评定出的优秀开源项目
5.  Gitee 官方提供的使用手册 [https://gitee.com/help](https://gitee.com/help)
6.  Gitee 封面人物是一档用来展示 Gitee 会员风采的栏目 [https://gitee.com/gitee-stars/](https://gitee.com/gitee-stars/)
