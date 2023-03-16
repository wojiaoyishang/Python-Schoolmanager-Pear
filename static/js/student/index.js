layui.use(['table', 'form', 'jquery', 'layer', 'button', 'toast', 'dropdown'], function () {
    let table = layui.table,
    form = layui.form,
    $ = layui.jquery,
    layer = layui.layer,
    button = layui.button,
    toast = layui.toast,
    dropdown = layui.dropdown;
    
    
    // 表格载入
    // 表格数据
    let cols = [
        [
            {type: 'radio'},
            {field: '姓名', minWidth: 100, title: '姓名'},
            {field: '性别', title: '性别'},
            {field: '班级', title: '班级'},
            {field: '届数', title: '届数', hide: true}
        ]
    ]

    // 渲染表格数据
    table.render({
        elem: '#data-table',
        id: 'data-table',
        url:'/schoolmanager/student/data',
        method: 'post',
        limit: 30,
        cols: cols,
        page: true,
        skin: 'line',
        height: 'full-148',
        text: {none: '暂无学生信息'},
        parseData: function(res) {
            if (res.data == undefined) {
                res.data = [];
            }
            for (i = 0; i < res.data.length; i++) {

                if (res.data[i]['性别'] == 0) {
                    res.data[i]['性别'] = "女"
                } else if (res.data[i]['性别'] == 1) {
                    res.data[i]['性别'] = "男"
                } else {
                    res.data[i]['性别'] = "未定义"
                }
            }

        },
        done: function (res, curr, count) {
            // 选中第一行
            $(".layui-table-view[lay-id='data-table'] .layui-table-body tr[data-index=0] .layui-form-radio").click();
        }
    })
    
    // 单选框事件
    table.on('radio(data-table)', function(obj){ 
        // 获取学生数据
        var name = obj.data['姓名'];
        var grade = obj.data['届数'];

        let loader = layer.load();

        $.ajax({
            url: '/schoolmanager/student/get?name=' + name + "&" + "grade=" + grade,
            type: 'get',
            success: function (result) {
                
                if (result.msg) {

                    layer.close(loader);

                    document.querySelector("#表单姓名").disabled = true;
                    document.querySelector("#表单届数").disabled = true;
                    document.querySelector("#submit_add").style.display = "none";
                    document.querySelector("#submit_update").style.display = "";

                    var subjects = {
                        '选科_物': false,
                        '选科_化': false,
                        '选科_生': false,
                        '选科_政': false,
                        '选科_史': false,
                        '选科_地': false,
                        '选科_技': false,
                    };
                    
                    // 处理选科数据
                    if (result.data['选科'] != undefined) {
                        for (var i = 0; i < result.data['选科'].length; i++) {
                            subjects['选科_' + result.data['选科'][i]] = true;
                        }
                    }
                    

                    form.val("student-info-form", Object.assign({}, { 
                        "姓名": result.data['姓名'],
                        "性别": result.data['性别'],
                        "班级": result.data['班级'],
                        "家庭住址": result.data['家庭住址'],
                        "寝室": result.data['寝室'],
                        "毕业学校": result.data['毕业学校'],
                        "身份证号": result.data['身份证号'],
                        "备注": result.data['备注'],
                        "届数": grade
                    }, subjects));


                }
            }
        })

    });

    
    //监听行单击事件（双击事件为：rowDouble）
    table.on('row(data-table)', function(obj) { 
        var data = obj.data;
        selected = data;
        //选中行样式
        obj.tr.addClass('layui-table-click').siblings().removeClass('layui-table-click');
        //选中radio样式
        obj.tr.find('i[class="layui-anim layui-icon"]').trigger("click");
    })


    // 查询数据
    form.on('submit(student-query)', function(data){

        // 数据重载
        table.reload('data-table', {
            url: '/schoolmanager/student/data',
            where: {
                grade: data.field.grade,
                class: data.field.class,
                name: data.field.name
            },
            page: {
                curr: 1 //重新从第 1 页开始
            }
        });

        return false; //阻止表单跳转。如果需要表单跳转，去掉这段即可。
    });

    // 更新学生数据
    form.on('submit(student-info-update)', function(data){
        
        // 处理表单数据
        var new_data = {选科:""}

        for (key in data.field) {
            if (key.indexOf("选科_") != -1) {
                new_data["选科"] = new_data["选科"] + key.replace("选科_", "")
            } else {
                new_data[key] = data.field[key]
            }
        }
        
        // 开始加载
        let loader = layer.load();
        let btn = button.load({elem: '.student-info-update'});

        $.ajax({
            url: '/schoolmanager/student/update',
            data: new_data,
            type: 'post',
            success: function (result) {
                if (result.success) {
                    layer.close(loader);
                    btn.stop(function () {
                        toast.success({title: '数据修改成功', message: result.msg, position: 'topCenter'});
                        table.reload('data-table')
                    })
                } else {
                    layer.close(loader);
                    btn.stop(function () {
                        toast.error({title: '数据修改失败', message: result.msg, position: 'topCenter'});
                    })
                }
            }
        })

        return false; //阻止表单跳转。如果需要表单跳转，去掉这段即可。
    });

    // 添加学生数据
    form.on('submit(student-info-add)', function(data){
        
        // 处理表单数据
        var new_data = {选科:""}

        for (key in data.field) {
            if (key.indexOf("选科_") != -1) {
                new_data["选科"] = new_data["选科"] + key.replace("选科_", "")
            } else {
                new_data[key] = data.field[key]
            }
        }
        
        // 开始加载
        let loader = layer.load();
        let btn = button.load({elem: '.student-info-update'});

        $.ajax({
            url: '/schoolmanager/student/add',
            data: new_data,
            type: 'post',
            success: function (result) {
                if (result.success) {
                    layer.close(loader);
                    btn.stop(function () {
                        toast.success({title: '数据添加成功', message: result.msg, position: 'topCenter'});
                        table.reload('data-table')
                    })
                } else {
                    layer.close(loader);
                    btn.stop(function () {
                        toast.error({title: '数据添加失败', message: result.msg, position: 'topCenter'});
                    })
                }
            }
        })

        return false; //阻止表单跳转。如果需要表单跳转，去掉这段即可。
    });

    // 添加一个新学生
    $("#add_student").click(function() {
        // 更换表单作用
        document.querySelector("#表单姓名").disabled = false;
        document.querySelector("#表单届数").disabled = false;
        document.querySelector("#submit_add").style.display = "";
        document.querySelector("#submit_update").style.display = "none";
        form.val("student-info-form", { 
            "姓名": "",
            "家庭住址": "",
            "寝室": "",
            "毕业学校": "",
            "身份证号": "",
            "备注": "",
        });
    });

    // 删除一个学生
    $("#delete_student").click(function() {
        // 二次确认
        layer.confirm('确定要删除这个学生吗？', {
            icon: 3,
            title: '提示',
            end: function (index) {
                layer.close(loader);
                btn.stop()
            }   
        }, function (index) {
            layer.close(index);

            // 开始加载
            let loader = layer.load();
            let btn = button.load({elem: '.student-info-update'});

            $.ajax({
                url: '/schoolmanager/student/delete',
                data: form.val("student-info-form"),
                type: 'post',
                success: function (result) {
                    if (result.success) {
                        layer.close(loader);
                        btn.stop(function () {
                            toast.success({title: '删除学生成功', message: result.msg, position: 'topCenter'});
                            table.reload('data-table')
                        })
                    } else {
                        layer.close(loader);
                        btn.stop(function () {
                            toast.error({title: '删除学生失败', message: result.msg, position: 'topCenter'});
                        })
                    }
                }
            })
        })
    });

    // 添加一个新班级
    $("#add_class").click(function() {

        layer.prompt({
            formType: 0,
            value: '1',
            title: '新建班级（届数请在上方查询处更改）',
          }, function(value, index, elem) { 

            // 开始加载
            let loader = layer.load();
            let btn = button.load({elem: '.student-info-update'});

            $.ajax({
                url: '/schoolmanager/student/add',
                data: {班级: value, 姓名: "新学生" + Date.now().toString(), 届数: form.val("student-query-form")['grade']},
                type: 'post',
                success: function(result) { 
                    if (result.success) {
                        layer.close(loader);
                        btn.stop(function () {
                            toast.success({title: '创建班级成功', message: result.msg, position: 'topCenter'});
                            window.location.reload();
                        })
                    } else {
                        layer.close(loader);
                        btn.stop(function () {
                            toast.error({title: '创建班级失败', message: result.msg, position: 'topCenter'});
                        })
                    }
                }
            })
        })
    });

    // 添加一个年段
    $("#add_grade").click(function() {

        layer.prompt({
            formType: 0,
            value: '',
            title: '新建年段（请输入年份）',
        }, function(value, index, elem) { 

            // 开始加载
            let loader = layer.load();
            let btn = button.load({elem: '.student-info-update'});

            $.ajax({
                url: '/schoolmanager/student/grade/add',
                data: {grade: value},
                type: 'post',
                success: function(result) { 
                    if (result.success) {
                        layer.close(loader);
                        btn.stop(function () {
                            toast.success({title: '创建年段成功', message: result.msg, position: 'topCenter'});
                            window.location.reload();
                        })
                    } else {
                        layer.close(loader);
                        btn.stop(function () {
                            toast.error({title: '创建年段失败', message: result.msg, position: 'topCenter'});
                        })
                    }
                }
            })
        })
    });

    // 删除一个年段
    $("#delete_grade").click(function() {

        layer.prompt({
            formType: 0,
            value: '危险操作，请手动输入确认。',
            title: '删除年段（请输入一遍 “' + form.val("student-query-form")['grade'] + '” ）',
        }, function(value, index, elem) { 
            if (value !== form.val("student-query-form")['grade']) {
                toast.error({title: '输入错误', message: "危险操作，请手动输入确认。", position: 'topCenter'});
                return false;
            }

            // 开始加载
            let loader = layer.load();
            let btn = button.load({elem: '.student-info-update'});

            $.ajax({
                url: '/schoolmanager/student/grade/remove',
                data: {grade: value},
                type: 'post',
                success: function(result) { 
                    if (result.success) {
                        layer.close(loader);
                        btn.stop(function () {
                            toast.success({title: '删除年段成功', message: result.msg, position: 'topCenter'});
                            window.location.reload();
                        })
                    } else {
                        layer.close(loader);
                        btn.stop(function () {
                            toast.error({title: '删除年段失败', message: result.msg, position: 'topCenter'});
                        })
                    }
                }
            })
        })
    });

    // 查看证件照
    $("#see_photo").click(function() {
        if (form.val("student-info-form")['姓名'] == "") {
            return;
        }
        layer.open({
            type: 2,
            title: '查看证件照',
            shade: 0.1,
            area: ['900px', '500px'],
            content: '/schoolmanager/student/photo?grade=' + form.val("student-info-form")['届数'] + "&name=" + form.val("student-info-form")['姓名'],
            btn: ['确定']
        })
    });

    // 导入数据
    dropdown.render({
        elem: '#imp',
        data: [{
          title: '从 Excel 中导入',
          id: 0
        }],
        click: function(obj){
            if (obj.id == 0) {
                layer.open({
                    type: 2,
                    title: '从 Excel 中导入',
                    shade: 0.1,
                    area: ['100%', '100%'],
                    content:  "/schoolmanager/student/imp?engine=excel",
                    btn: ['确定']
                })
            }
        }
      });
    

})
