var exam = null;
layui.use(['table', 'form', 'jquery', 'layer', 'button', 'toast', 'dropdown'], function () {
    let table = layui.table,
    form = layui.form,
    $ = layui.jquery,
    layer = layui.layer,
    button = layui.button,
    toast = layui.toast,
    dropdown = layui.dropdown,
    laydate = layui.laydate;
    
    //执行一个laydate实例
    laydate.render({
        elem: '#date_choose',
        range: ["#startDate", "#endDate"],
        isInitValue: false,
        done: function (value, date, endDate) {
            let start = date.year + "-" + date.month + "-" + date.date
            let end = endDate.year + "-" + endDate.month + "-" + endDate.date
        }
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
                    content:  "/schoolmanager/examPublish/imp?engine=excel",
                    btn: ['确定']
                })
            }
        }
        });
    

    // 数据表格渲染

    let cols = [
        [
            {type: 'radio'},
            {field: 'index', hide: true},
            {field: '考试名称', minWidth: 100, title: '考试名称'},
            {field: '届数', title: '届数'},
            {field: '考试时间', title: '考试时间'},
            {field: '特控线分数', title: '特控线分数'},
            {field: '考试备注', title: '考试备注'}
        ]
    ]

    // 渲染表格数据
    table.render({
        elem: '#data-table',
        id: 'data-table',
        url:'/schoolmanager/examPublish/data',
        method: 'post',
        limit: 30,
        cols: cols,
        page: true,
        skin: 'line',
        height: 'full-148',
        text: {none: '暂无考试信息'},
        parseData: function(res) {
            if (res.data == undefined) {
                res.data = [];
            }
            for (i = 0; i < res.data.length; i++) {

                for (i = 0; i < res.data.length; i++) {
                    // 时间戳转化为时间
                    const ts = res.data[i]['考试时间'];

                    // 创建一个日期对象
                    const date = new Date(ts);

                    // 获取年月日小时分钟秒数
                    const year = date.getFullYear();
                    const month = (date.getMonth() + 1).toString().padStart(2, '0'); // 月份从0开始，需要加1，并使用padStart函数补齐两位数
                    const day = date.getDate().toString().padStart(2, '0');

                    // 拼接成字符串
                    const dateString = `${year}年${month}月${day}日`;

                    res.data[i]['考试时间'] = dateString;
                }

            }

        },
        done: function (res, curr, count) {
            // 选中第一行
            $(".layui-table-view[lay-id='data-table'] .layui-table-body tr[data-index=0] .layui-form-radio").click();
        }
    })

    // 查询数据
    form.on('submit(exam-query)', function(data){

        data.field['startDate'] = new Date(data.field['startDate']).getTime()
        data.field['endDate'] = new Date(data.field['endDate']).getTime()
        
        if (isNaN(data.field['startDate']) || isNaN(data.field['endDate'])) {
            data.field['startDate'] = null
            data.field['endDate'] = null
        }

        // 数据重载
        table.reload('data-table', {
            url: '/schoolmanager/examPublish/data',
            where: {
                grade: data.field.grade,
                startDate: data.field['startDate'],
                endDate: data.field['endDate'],
                name: data.field.name
            },
            page: {
                curr: 1 //重新从第 1 页开始
            }
        });

        return false; //阻止表单跳转。如果需要表单跳转，去掉这段即可。
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

    // 单选框事件
    table.on('radio(data-table)', function(obj) { 
        exam = table.checkStatus('data-table').data[0];
    });

    // 查看考试数据
    $("#info").click(function() {
        if (exam != null) {
            top.layui.admin.jump(100 + exam['index'], "“"+exam['考试名称']+"”数据编辑", "/schoolmanager/examPublish/info?index=" + exam['index'], true)
        }
    });

    // 删除考试数据
    $("#delete").click(function() {
        // 二次确认
        layer.confirm('确定要删除“' + exam['考试名称'] + '”考试吗？', {
            icon: 3,
            title: '提示'
        }, function (index) {
            layer.close(index);

            // 开始加载
            let loader = layer.load();

            $.ajax({
                url: '/schoolmanager/examPublish/delete',
                data: {name: exam['考试名称'], grade: exam['届数']},
                type: 'post',
                success: function (result) {
                    if (result.success) {
                        layer.close(loader);
                    
                        toast.success({title: '删除考试成功', message: result.msg, position: 'topCenter'});
                        table.reload('data-table')
                        exam = null;
                        
                    } else {
                        layer.close(loader);
                        toast.error({title: '删除考试失败', message: result.msg, position: 'topCenter'});
                    }
                }
            })
        })
    });

    // 添加考试
    $("#add").click(function() {

        layer.prompt({
            formType: 0,
            value: '',
            title: '新建考试（请输入考试名称）',
        }, function(name, index, elem) { 
            
            layer.prompt({
                formType: 0,
                value: '',
                title: '对应届数（请输入对应的年段）',
            }, function(grade, index, elem) { 
                // 开始加载
                let loader = layer.load();

                $.ajax({
                    url: '/schoolmanager/examPublish/add',
                    data: {grade: grade, name: name},
                    type: 'post',
                    success: function(result) { 
                        if (result.success) {
                            layer.close(loader);
                            
                            toast.success({title: '创建考试成功', message: result.msg, position: 'topCenter'});
                            window.location.reload();
                            
                        } else {
                            layer.close(loader);

                            toast.error({title: '创建考试失败', message: result.msg, position: 'topCenter'});
                            
                        }
                    }
                })

            })

        })
    });

    $("#setting").click(function() {
        if (form.val("student-info-form")['姓名'] == "") {
            return;
        }
        layer.open({
            type: 2,
            title: '查询设置',
            shade: 0.1,
            area: ['900px', '500px'],
            content: '/schoolmanager/examPublish/setting',
            btn: ['确定'],
            yes: function(index, layero){
                var iframeWin = window[layero.find('iframe')[0]['name']]; //得到iframe页的窗口对象，执行iframe页的方法：iframeWin.method();
                $.ajax({
                    url: '/schoolmanager/examPublish/setting',
                    data: iframeWin.layui.form.val("setting-form"),
                    type: 'post',
                    success: function(result) { 
                        if (result.success) {
                
                            toast.success({title: '修改查询设置成功', message: result.msg, position: 'topCenter'});
                            layer.close(index); //如果设定了yes回调，需进行手工关闭
                            
                        } else {

                            toast.error({title: '修改查询设置失败', message: result.msg, position: 'topCenter'});
                            
                        }
                    }
                })
                
            }
        })
    });

})
