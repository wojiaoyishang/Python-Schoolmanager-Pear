function bar_chart(ElementID, yAxisName, seriesName, legendName, xAxisData, seriesData) {
    layui.use(['echarts'], function () {
        let echarts = layui.echarts;

        var column = echarts.init(document.getElementById(ElementID), null);

        if (!column.isDisposed()) {
            // 图表已经显示
            // 在这里清除图表
            column.clear();
        }

        option = {
            tooltip: {
                trigger: 'axis',
                axisPointer: { 
                    type: 'shadow' ,
                    color: '#fff',
                    fontSize: '26'
                }
            },
            legend: {
                top:'5%',
                right:'10%',
                data: [legendName],
                fontSize:12,
                color:'#808080',
                icon:'rect'
            },
            grid: {
                top:60,
                left:50,
                bottom:60,
                right:60
            },
            xAxis: [{
                type: 'category',
                axisTick:{
                    show:false
                },
                axisLine:{
                    show:false
                },
                axisLabel:{
                    color:'#4D4D4D',
                    fontSize:14,
                    margin:21,
                    fontWeight:'bold'
                },
                data: xAxisData,
            
            }],
            yAxis: [{
                name: yAxisName,
                nameTextStyle:{
                    color:'#808080',
                    fontSize:12,
                    padding:[0, 0, 0, -5]
                },
                type: 'value',
                axisLine:{
                    show:false
                },
                axisLabel:{
                    color:'#808080',
                    fontSize:12,
                    margin:5
                },
                splitLine:{
                    show:false
                },
                axisTick:{
                    show:false
                }
            }],
            series: [{
                    name: seriesName,
                    type: 'bar',
                    label:{
                        show:true,
                        position:'top',
                        fontSize:14,
                        color:'#3DC3F0',
                        fontWeight:'bold'
                    },
                    barMaxWidth:60,           
                    color: {
                        type: 'linear',
                        x: 0,
                        y: 0,
                        x2: 0,
                        y2: 1,
                        colorStops: [{
                            offset: 0, color: '#3DC3F0' // 0% 处的颜色
                        }, {
                            offset: 1, color: '#CCF2FF' // 100% 处的颜色
                        }]
                    },            
                    data: seriesData
                }]
        };

        column.setOption(option);
        window.onresize = function() {
            column.resize();
        }
      
        

    })

}


function line_chart_1(ElementID, xData, legendData, seriesData, colorList=["#9E87FF", '#73DDFF', '#fe9a8b', '#F56948', '#9E87FF']) {
    layui.use(['echarts'], function() {
        let echarts = layui.echarts;
    
        var line = echarts.init(document.getElementById(ElementID), null);

        if (!line.isDisposed()) {
            // 图表已经显示
            // 在这里清除图表
            line.clear();
        }

        option = {
            backgroundColor: '#fff',
            color: colorList,
            tooltip: {
                trigger: 'axis',
                axisPointer: {
                    type: 'cross',
                    crossStyle: {
                        color: '#999'
                    },
                    lineStyle: {
                        type: 'dashed'
                    }
                }
            },
            grid: {
                left: '25',
                right: '25',
                bottom: '24',
                top: '75',
                containLabel: true
            },
            legend: {
                data: legendData,
                orient: 'horizontal',
                icon: "rect",
                show: true,
                left: 20,
                top: 25,
            },
            xAxis: {
                type: 'category',
                data: xData,
                splitLine: {
                    show: false
                },
                axisTick: {
                    show: false
                },
                axisLine: {
                    show: false
                },
            },
            yAxis: {
                type: 'value',
                minInterval: 1,
                axisLabel: {
                    color: '#999',				
                    fontSize: 12				
                },
                splitLine: {
                    show: true,
                    lineStyle: {
                        color: '#F3F4F4'
                    }
                },
                axisTick: {
                    show: false
                },
                axisLine: {
                    show: false
                },
            },
            series: seriesData
        };
    
        line.setOption(option);
    
        window.onresize = function() {
            line.resize();
        }
        
    })
    
}