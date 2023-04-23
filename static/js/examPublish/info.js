function recalc_average() {
    // 考试数据统计
    layui.$.ajax({
        url: '/schoolmanager/examAnalyse/average' ,
        data: {
            index: layui.form.val("exam-info-form").index,
            giveMark: (layui.form.val("exam-query-form")['查询设置'].indexOf("查看赋分成绩") != -1) ? 1 : 0
        },
        type: 'get',
        success: function(result) { 
            var html = ""
            var i = 0;

            var fields = ['语文', '数学', '外语', '政治', '历史', '地理', '物理', '化学', '生物', '技术', '总分', '主科', '副科']
            for (r of fields) {
                if (i % 7 == 0) {
                    html += "<br>"
                }

                if (result[r] == null) {
                    html += "<b>" + r + "平均分：</b>未统计&nbsp&nbsp&nbsp&nbsp"
                } else {
                    html += "<b>" + r + "平均分：</b>" + result[r].toFixed(2) + "&nbsp&nbsp&nbsp&nbsp"
                }
                i += 1
            }
            document.querySelector("#考试统计").innerHTML = html
        }
    })
}
var exam = null;
layui.use(['table', 'form', 'jquery', 'layer', 'button', 'toast', 'select', 'element'], function () {
    let table = layui.table,
        form = layui.form,
        $ = layui.jquery,
        layer = layui.layer,
        button = layui.button,
        toast = layui.toast,
        select = layui.select,
        laydate = layui.laydate;

    // 创建一个日期对象
    const date = new Date(parseInt(layui.form.val("exam-info-form")['考试时间']));

    // 获取年月日小时分钟秒数
    const year = date.getFullYear();
    const month = (date.getMonth() + 1).toString().padStart(2, '0'); // 月份从0开始，需要加1，并使用padStart函数补齐两位数
    const day = date.getDate().toString().padStart(2, '0');

    // 拼接成字符串
    const dateString = `${year}-${month}-${day}`;


    laydate.render({
        elem: '#time', //指定元素
        value: dateString
    });

    // 更新考试信息
    form.on('submit(exam-info-update)', function(data){
        console.log(data.field['考试时间'])
        data.field['考试时间'] = Date.parse(data.field['考试时间']);

        // 开始加载
        let loader = layer.load();
        let btn = button.load({elem: '.exam-info-update'});

        $.ajax({
            url: '/schoolmanager/examPublish/update',
            data: data.field,
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

        // 表格载入
        // 表格数据
        let cols = [
            [
                {type: 'radio'},
                {field: '姓名', minWidth: 100, title: '姓名'},
                {field: '语文', title: '语文'},
                {field: '数学', title: '数学'},
                {field: '外语', title: '外语'},
                {field: '政治', title: '政治'},
                {field: '历史', title: '历史'},
                {field: '地理', title: '地理'},
                {field: '物理', title: '物理'},
                {field: '化学', title: '化学'},
                {field: '生物', title: '生物'},
                {field: '技术', title: '技术'},
                {field: '总分', title: '总分'},

                {field: '语文排名', hide: true},
                {field: '数学排名', hide: true},
                {field: '外语排名', hide: true},
                {field: '政治排名', hide: true},
                {field: '历史排名', hide: true},
                {field: '地理排名', hide: true},
                {field: '物理排名', hide: true},
                {field: '化学排名', hide: true},
                {field: '生物排名', hide: true},
                {field: '技术排名', hide: true},
                {field: '总分排名', hide: true},
                {field: '主科排名', hide: true},
                {field: '副科排名', hide: true},

                {field: '备注', hide: true}
            ]
        ]

        // 渲染表格数据
        table.render({
            elem: '#data-table',
            id: 'data-table',
            url:'/schoolmanager/examPublish/exam/data',
            where: {
                index: layui.form.val("exam-info-form").index,
                name: layui.form.val("exam-query-form").name,
                class: layui.form.val("exam-query-form").class,
                setting: layui.form.val("exam-query-form")['查询设置']
            },
            method: 'post',
            limit: 30,
            cols: cols,
            page: true,
            skin: 'line',
            height: 'full-148',
            text: {none: '暂无成绩信息'},
            done: function (res, curr, count) {
                // 选中第一行
                $(".layui-table-view[lay-id='data-table'] .layui-table-body tr[data-index=0] .layui-form-radio").click();
                // 统计平均分
                recalc_average()
            }
        })

        // 查询数据
        form.on('submit(exam-query)', function(data){
            if (layui.form.val("exam-query-form")['查询设置'] == '') {
                layui.select.render()
            }

            // 数据重载
            table.reload('data-table', {
                url:'/schoolmanager/examPublish/exam/data',
                where: {
                    index: layui.form.val("exam-info-form").index,
                    name: layui.form.val("exam-query-form").name,
                    class: layui.form.val("exam-query-form").class,
                    setting: layui.form.val("exam-query-form")['查询设置']
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
        table.on('radio(data-table)', function(obj){ 
            obj.data = table.checkStatus('data-table').data[0]
            obj.data['赋分'] = obj.data['赋分'] == 1 ? '是' : '否'
            form.val("student-info-form", obj.data);
        });

        // 更新学生数据
        form.on('submit(student-info-update)', function(data){
            
            // 开始加载
            let loader = layer.load();
            let btn = button.load({elem: '.student-info-update'});

            
            data.field['赋分'] = (layui.form.val("exam-query-form")['查询设置'].indexOf("查看赋分成绩") != -1) ? "是" : "否"

            $.ajax({
                url: '/schoolmanager/examPublish/exam/update',
                data: JSON.stringify({index: layui.form.val("exam-info-form").index, data: data.field}),
                type: 'post',
                contentType: "application/json",
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


        // 删除学生数据
        form.on('submit(student-info-delete)', function(data){
            
            // 开始加载
            let loader = layer.load();
            let btn = button.load({elem: '.student-info-delete'});

            
            data.field['赋分'] = (layui.form.val("exam-query-form")['查询设置'].indexOf("查看赋分成绩") != -1) ? "是" : "否"
            layer.confirm('确定要删除这位同学的数据吗？', {
                    icon: 3,
                    title: '提示',
                    end: function (index) {
                        layer.close(loader);
                        btn.stop()
                    }                
                },  function (index) {
                    layer.close(index);

                    // 开始加载
                    let loader = layer.load();

                    $.ajax({
                        url: '/schoolmanager/examPublish/exam/delete',
                        data: JSON.stringify({index: layui.form.val("exam-info-form").index, data: data.field}),
                        type: 'post',
                        contentType: "application/json",
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

                })
            

            return false; //阻止表单跳转。如果需要表单跳转，去掉这段即可。
        });

})
