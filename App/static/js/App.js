﻿//**************全局对象管理******************
// 声明一个全局对象Namespace，用来注册命名空间
Namespace = new Object();

// 全局对象仅仅存在register函数，参数为名称空间全路径，如"Grandsoft.GEA"
Namespace.register = function (fullNS) {
    // 将命名空间切成N部分, 比如Grandsoft、GEA等
    var nsArray = fullNS.split('.');

    var sEval = "";
    var sNS = "";
    for (var i = 0; i < nsArray.length; i++) {
        if (i != 0) sNS += ".";
        sNS += nsArray[i];
        // 依次创建构造命名空间对象（假如不存在的话）的语句
        // 比如先创建Grandsoft，然后创建Grandsoft.GEA，依次下去
        sEval += "if (typeof(" + sNS + ") == 'undefined') " + sNS + " = new Object();"
    }
    if (sEval != "") eval(sEval);
}
//**************全局对象管理******************
//注册sy对象 自定义工具 空间
Namespace.register('sy');
//***************生成32位UUID**************
function UUID() {
    this.id = this.createUUID();
}

// When asked what this Object is, lie and return it's value
UUID.prototype.valueOf = function () {
    return this.id;
}
UUID.prototype.toString = function () {
    return this.id;
}

//
// INSTANCE SPECIFIC METHODS
//

UUID.prototype.createUUID = function () {
    //
    // Loose interpretation of the specification DCE 1.1: Remote Procedure Call
    // described at http://www.opengroup.org/onlinepubs/009629399/apdxa.htm#tagtcjh_37
    // since JavaScript doesn't allow access to internal systems, the last 48 bits
    // of the node section is made up using a series of random numbers (6 octets long).
    //
    var dg = new Date(1582, 10, 15, 0, 0, 0, 0);
    var dc = new Date();
    var t = dc.getTime() - dg.getTime();
    var h = '-';
    var tl = UUID.getIntegerBits(t, 0, 31);
    var tm = UUID.getIntegerBits(t, 32, 47);
    var thv = UUID.getIntegerBits(t, 48, 59) + '1'; // version 1, security version is 2
    var csar = UUID.getIntegerBits(UUID.rand(4095), 0, 7);
    var csl = UUID.getIntegerBits(UUID.rand(4095), 0, 7);

    // since detection of anything about the machine/browser is far to buggy,
    // include some more random numbers here
    // if NIC or an IP can be obtained reliably, that should be put in
    // here instead.
    var n = UUID.getIntegerBits(UUID.rand(8191), 0, 7) +
        UUID.getIntegerBits(UUID.rand(8191), 8, 15) +
        UUID.getIntegerBits(UUID.rand(8191), 0, 7) +
        UUID.getIntegerBits(UUID.rand(8191), 8, 15) +
        UUID.getIntegerBits(UUID.rand(8191), 0, 15); // this last number is two octets long
    return tl + h + tm + h + thv + h + csar + csl + h + n;
}


//
// GENERAL METHODS (Not instance specific)
//


// Pull out only certain bits from a very large integer, used to get the time
// code information for the first part of a UUID. Will return zero's if there
// aren't enough bits to shift where it needs to.
UUID.getIntegerBits = function (val, start, end) {
    var base16 = UUID.returnBase(val, 16);
    var quadArray = new Array();
    var quadString = '';
    var i = 0;
    for (i = 0; i < base16.length; i++) {
        quadArray.push(base16.substring(i, i + 1));
    }
    for (i = Math.floor(start / 4); i <= Math.floor(end / 4); i++) {
        if (!quadArray[i] || quadArray[i] == '') quadString += '0';
        else quadString += quadArray[i];
    }
    return quadString;
}

// Numeric Base Conversion algorithm from irt.org
// In base 16: 0=0, 5=5, 10=A, 15=F
UUID.returnBase = function (number, base) {
    //
    // Copyright 1996-2006 irt.org, All Rights Reserved.
    //
    // Downloaded from: http://www.irt.org/script/146.htm
    // modified to work in this class by Erik Giberti
    var convert = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'];
    if (number < base) var output = convert[number];
    else {
        var MSD = '' + Math.floor(number / base);
        var LSD = number - MSD * base;
        if (MSD >= base) var output = this.returnBase(MSD, base) + convert[LSD];
        else var output = convert[MSD] + convert[LSD];
    }
    return output;
}

// pick a random number within a range of numbers
// int b rand(int a); where 0 <= b <= a
UUID.rand = function (max) {
    return Math.floor(Math.random() * max);
}

//**************对象数组按指定属性排序***************************
sy.createComparsion = function (propertyName, orderType) {
    return function (o1, o2) {
        var orderT = orderType || 'asc';
        var v1 = o1[propertyName];
        var v2 = o2[propertyName];
        if (v1 == v2) {
            return 0;
        }
        if (orderT == 'asc') {
            if (v1 < v2) {
                return -1;
            } else {
                return 1;
            }
        } else {
            if (v1 < v2) {
                return 1;
            } else {
                return -1;
            }
        }
    }
}
/// dddh add : use as :  var p = new sy.UUID().toString();
sy.UUID = function () {
    this.id = new UUID();
}
sy.UUID.prototype.toString = function () {
    return this.id.toString();
}

//***************时间转换字符串*********************************//


//***************Django Ajax通过csrf**************//
sy.getCookie = function (name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

sy.csrfSafeMethod = function (method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}


//***************全局用到的对象**********************
/*
 sy.logonPath 登录窗口路径
 sy.searchWindowData 向通用查询窗口传入的列信息
 sy.searchWindowReturnData 由通用查询窗口返回的过滤和排序信息
 sy.csrftoken csrf令牌
 * */
sy.apptitle = '进口货运系统';
//sy.logonPath = '';
sy.onError = function (msg, logout) {
    /*msg:错误信息
     logout:true 退出系统
     */
    var defaultMsg = '系统错误,请通知管理员：\n' + msg;
    $.messager.alert('注意', defaultMsg, 'error');
    if (logout) {
        //window.location.href = sy.logonPath;
        window.location.reload();
    }
}
sy.csrftoken = sy.getCookie('csrftoken');
sy.searchWindowUrl = '';
sy.searchWindow = undefined;

sy.searchWindowData = [];
sy.searchWindowReturnData = {
    refreshFlag: false,
    filters: [],
    sorts: [],
    cols: []
};
sy.createSearchWindow = function (datagrid) {
    sy.searchWindowData.length = 0;
    sy.searchWindowReturnData.filters.length = 0;
    sy.searchWindowReturnData.sorts.length = 0;
    sy.searchWindowReturnData.cols.length = 0;
    sy.searchWindowReturnData.refreshFlag = false;
//  sy.searchWindowSourceData = datagrid;
    if (sy.searchWindow != undefined) {
        //console.info('not undefined');
        sy.searchWindow.window('destroy');
        sy.searchWindow = null;
    } else {
        //console.info('undefined');
    }
    var columns = datagrid.datagrid('options').columns;
    for (var j = 0, jlen = columns.length; j < jlen; j++) {
        for (var i = 0, ilen = columns[j].length; i < ilen; i++) {
            if (columns[j][i].field != 'id') {
                sy.searchWindowData.push({
                    cod: columns[j][i].field,
                    text: columns[j][i].title,
                    editor: columns[j][i].editor,
                    hidden: columns[j][i].hidden
                });
            }
        }
    }
    var columns = datagrid.datagrid('options').fitColumns;
    for (var j = 0, jlen = columns.length; j < jlen; j++) {
        for (var i = 0, ilen = columns[j].length; i < ilen; i++) {
            if (columns[j][i].field != 'id') {
                sy.searchWindowData.push({
                    cod: columns[j][i].field,
                    text: columns[j][i].title,
                    editor: columns[j][i].editor,
                    hidden: columns[j][i].hidden
                });
            }
        }
    }

    sy.searchWindow = $('<div></div>').window({
        href: sy.searchWindowUrl,
        title: '查询',
        width: window.innerWidth * 0.8,
        height: window.innerHeight * 0.8,
        modal: true,
        collapsible: false,
        minimizable: false,
        maximizable: false,

        closable: true,
        onClose: function () {
            //console.info('onClose');                        
            common.createsearchform.filterdatagrid = null;
            common.createsearchform.sorterdatagrid = null;
            common.createsearchform.colsdatagrid = null;
            common.createsearchform.datagridid = null;
            sy.searchWindow.window('destroy');
            sy.searchWindow = null;
            if (sy.searchWindowReturnData.refreshFlag) {
                var columns = datagrid.datagrid('getColumnFields').concat(datagrid.datagrid('getColumnFields', true));
                for (var i = 0, ilen = columns.length; i < ilen; i++) {
                    if ($.inArray(columns[i], sy.searchWindowReturnData.cols) >= 0) {
                        datagrid.datagrid('showColumn', columns[i]);
                    } else {
                        datagrid.datagrid('hideColumn', columns[i]);
                    }
                }
                datagrid.datagrid('load', {
                    filter: sy.searchWindowReturnData.filters,
                    sort: sy.searchWindowReturnData.sorts,
                    cols: sy.searchWindowReturnData.cols
                });
            }
        }
    });
    var idarray = datagrid[0].id.split('-');
    if (isNaN(parseInt(idarray[idarray.length - 1]))) {
        common.createsearchform.datagridid = idarray.join('-');
    } else {
        idarray.length = idarray.length - 1;
        common.createsearchform.datagridid = idarray.join('-');
    }
}

//***************全局用到的对象**********************//
// 对Date的扩展，将 Date 转化为指定格式的String
// 月(M)、日(d)、小时(h)、分(m)、秒(s)、季度(q) 可以用 1-2 个占位符，
// 年(y)可以用 1-4 个占位符，毫秒(S)只能用 1 个占位符(是 1-3 位的数字)
// 例子：
// (new Date()).Format("yyyy-MM-dd hh:mm:ss.S") ==> 2006-07-02 08:09:04.423
// (new Date()).Format("yyyy-M-d h:m:s.S")      ==> 2006-7-2 8:9:4.18
Date.prototype.Format = function (fmt) { //author: meizz
    var o = {
        "M+": this.getMonth() + 1,                 //月份
        "d+": this.getDate(),                    //日
        "h+": this.getHours(),                   //小时
        "m+": this.getMinutes(),                 //分
        "s+": this.getSeconds(),                 //秒
        "q+": Math.floor((this.getMonth() + 3) / 3), //季度
        "S": this.getMilliseconds()             //毫秒
    };
    if (/(y+)/.test(fmt))
        fmt = fmt.replace(RegExp.$1, (this.getFullYear() + "").substr(4 - RegExp.$1.length));
    for (var k in o)
        if (new RegExp("(" + k + ")").test(fmt))
            fmt = fmt.replace(RegExp.$1, (RegExp.$1.length == 1) ? (o[k]) : (("00" + o[k]).substr(("" + o[k]).length)));
    return fmt;
}

//***************扩展datebox,datetimebox************//
$.extend($.fn.datebox.defaults, {
    onSelect: function (date) {
        $(this).datebox('setValue', date.Format("yyyy-MM-dd"));
        $(this).datebox('hidePanel');
    }
});
$.extend($.fn.datetimebox.defaults, {
    onSelect: function (date) {
        $(this).datetimebox('setValue', date.Format("yyyy-MM-dd hh:mm:ss"));
        $(this).datetimebox('hidePanel');
    }
});

//***************扩展datagrid editor ****************
//1.datetimebox 日期时间选择


$.extend($.fn.datagrid.defaults.editors, {
    datetimebox: {
        init: function (container, options) {
            var editor = $('<input />').appendTo(container);
            options.editable = false;
            editor.datetimebox(options);
            return editor;
        },
        getValue: function (target) {
            return $(target).datetimebox('getValue');
        },
        setValue: function (target, value) {
            $(target).datetimebox('setValue', value);
        },
        resize: function (target, width) {
            $(target).datetimebox('resize', width);
        },
        destroy: function (target) {
            $(target).datetimebox('destroy');
        }
    }
});

//***************扩展datagrid view ****************
$.extend($.fn.datagrid.defaults.view, {
    onBeforeRender: function (target, rows) {
        //console.info($(target));
        var opts = $(target).datagrid('options');
        //console.info(opts);
        if (opts.comboboxFormatFlag == true) {
            for (var j = 0, jlen = opts.columns.length; j < jlen; j++) {
                for (var i = 0, ilen = opts.columns[j].length; i < ilen; i++) {
                    if (opts.columns[j][i].hasOwnProperty('editor') &&
                        opts.columns[j][i].editor.hasOwnProperty('type') &&
                        opts.columns[j][i].editor.type == 'combobox') {
                        opts.columns[j][i].formatter = function (value, rowData, index) {
                            for (var i = 0, ilen = this.editor.options.data.length; i < ilen; i++) {
                                if (this.editor.options.data[i].value == value) {
                                    return this.editor.options.data[i].text;
                                }
                            }
                            return value;
                        }
                    }
                }
            }
        }
    },
    onAfterRender:function(target){
        $(target).datagrid('columnMoving');
    }
});
//***************扩展datagrid ***********************
$.extend($.fn.datagrid.defaults, {
    //以下为扩展属性
    autoLoad: true,  //true render完页面后，主动load数据
    loadNumber: 0,    //自datagrid创建以来load的次数，结合autoLoad，限制自动加载。
    autoSave: false, //true 在onAfterEdit()中提交'insert'和'update',在deleteData()中提交‘delete’
    childDatagrid: [],//关联的子datagrid 未启用
    parentDatagrid: null,//关联的父datagrid 未启用
    dataTable: '', //此datagrid关联的table名称
    editRow: -1,   //当前正在编辑的行index
    filterFields: [], /*过滤字段，自动传入查询参数
     {
     'cod':'client_name',
     'operatorTyp':'等于',
     'value':'值'
     }
     */
    sortFields: [], /*排序字段，自动传入查询参数{
     'cod':'client_name',
     'order_typ':'升序'
     }*/
    queryFuncName: '', //查询数据权限名称 views.dealPAjax() 参数    前台 datagrid.loader()
    updateFuncName: '', //修改数据权限名称 views.dealPAjax() 参数    前台 postUpdateAllData()
    ex_parm: {}, //扩展查询参数 load()中使用
    comboboxFormatFlag: false,
    //以上为扩展属性
    border: false,
    checkOnSelect: false,
    selectOnCheck: false,
    //fit: true,
    idField: 'id',
    method: 'post',
    pageList: [50, 100, 150, 200, 250],
    pageSize: 50,
    pagination: true,
    rownumbers: true,
    singleSelect: true,
    remoteSort: false,
    url: "./dealPAjax/",
    onDblClickRow: function (rowIndex, rowData) {
        //console.info('dbclick');
        $(this).datagrid('dbClick', rowIndex);
    },
    onClickRow: function (rowIndex, rowData) {
        //console.info('click');
        $(this).datagrid('click', rowIndex);
    },
    /*onLoadError: function () {
     sy.onError('加载数据错误', false);
     },*/
    onAfterEdit: function (rowIndex, rowData, changes) {
        if ($(this).datagrid('options').autoSave) {
            var datagridid = $(this)[0].id;
            $('a[group=' + '"' + datagridid.toString() + '"' + ']').linkbutton('disable');
            $(this).datagrid('postUpdateAllData');
            $('a[group=' + '"' + datagridid.toString() + '"' + ']').linkbutton('enable');
        }
    },
    onRowContextMenu: function (e, rowIndex, rowData) {
        e.preventDefault();
        var that = $(this);
        var opts = that.datagrid('options');
        $('#datagridcontextmenu').menu({
            onClick: function (item) {
                if (item.text == '导出Excel') {
                    var exportdata = that.datagrid('getExportExcelData');
                    var p = {
                        func: 'excel导出',
                        ex_parm: {
                            title: '',
                            cols: exportdata.cols,
                            rows: exportdata.data
                        }
                    }
                    $('#exceldownload-jpargs').val(JSON.stringify(p));
                    $('#exceldownloadform').submit();
                    /* 返回文件路径
                     $.ajax({
                     url: opts.url,
                     data: {jpargs: JSON.stringify(p)},
                     dataType:'text',
                     success: function (r, t, a) {
                     if ($.ajaxSettings.success(r, t, a, false)){
                     window.win = open(r.result);
                     }else{
                     error();
                     }
                     }
                     });
                     */
                }
            }
        }).menu('show', {
            left: e.pageX,
            top: e.pageY
        });
    },
    loader: function (param, success, error) {

        var that = $(this);
        var opts = that.datagrid('options');
        if (!opts.url) {
            return false;
        }

        var queryParam = {
            reqtype: 'query',
            func: opts.queryFuncName,
            ex_parm: opts.ex_parm
        };
        $.extend(queryParam, param);
        if (opts.filterFields.length != 0) {  //强制增加手动设置过滤条件
            if (queryParam.filter == undefined) {
                queryParam.filter = new Array();
            }
            $.each(opts.filterFields, function (index, data) {
                for (var i = 0, ilen = queryParam.filter.length; i < ilen; i++) {
                    if (queryParam.filter[i].cod == data.cod) {
                        queryParam.filter.splice(i, 1); //删掉重复的过滤字段
                        break;
                    }
                }
                queryParam.filter.splice(0, 0, data); //强制增加此datagrid的filterFields属性中的过滤条件
            });
        }
        if (opts.sortFields.length != 0) { //强制增加手动设置排序条件
            if (queryParam.sort == undefined) {
                queryParam.sort = new Array();
            }
            var ver = $.grep(opts.sortFields,function (data, index) {
                return true;
            }).reverse();
            $.each(ver, function (index, data) {
                for (var i = 0, ilen = queryParam.sort.length; i < ilen; i++) {
                    if (queryParam.sort[i].cod == data.cod) {
                        queryParam.sort.splice(i, 1);
                        break;
                    }
                }
                queryParam.sort.splice(0, 0, data);
            });

        }
        if (queryParam.cols == undefined) {
            var columns = that.datagrid('getColumnFields').concat(that.datagrid('getColumnFields', true));
            queryParam.cols = columns;
        } else {
            queryParam.cols.push('id');
        }
        if (queryParam.page == undefined) {
            queryParam.page = -1;
        }
        if (queryParam.rows == undefined) {
            queryParam.rows = -1;
        }
        opts.loadNumber++;
        if (opts.autoLoad == false && opts.loadNumber == 1) {
            return false;
        }
        //console.info(opts.id + ':loader');
        $.ajax({
            url: opts.url,
            data: {jpargs: JSON.stringify(queryParam)},
            //data:queryParam,
            success: function (r, t, a) {
                //console.info(r);
                if ($.ajaxSettings.success(r, t, a, false)) {
                    success(r);
                } else {
                    error();
                }
                //$.ajaxSettings.success(r, t, a, false);
            }
        });
    }
});

$.extend($.fn.datagrid.methods, {
    getOriginalRows: function (jq) {
        /*
         取datagrid的原始值 返回数组
         */
        return $(jq).data("datagrid").originalRows;
    },
    getExportExcelData: function (jq) {
        var cols = [];
        var coltitles = [];
        var colopts = [];
        var data = [];
        var columns = jq.datagrid('getColumnFields', true).concat(jq.datagrid('getColumnFields'));
        var colopt;
        var find = false;
        for (var i = 0, ilen = columns.length; i < ilen; i++) {
            colopt = jq.datagrid('getColumnOption', columns[i]);
            if (!colopt.hasOwnProperty('hidden') || colopt.hidden == false || colopt.hidden == 'false') {
                cols.push(colopt.field);
                coltitles.push(colopt.title);
                colopts.push(colopt);
            }
        }
        var rows = jq.datagrid('getRows');
        for (var i = 0, ilen = rows.length; i < ilen; i++) {
            data[i] = [];
            for (var j = 0, jlen = cols.length; j < jlen; j++) {
                //colopt = jq.datagrid('getColumnOption',cols[j]);
                if (!colopts[j].hasOwnProperty('editor')) {
                    data[i].push(rows[i][cols[j]]);
                } else if (!colopts[j].editor.hasOwnProperty('type')) {
                    data[i].push(rows[i][cols[j]]);
                } else if (colopts[j].editor.type == 'checkbox') {
                    if (rows[i][cols[j]] == 'true') {
                        data[i].push('是');
                    } else {
                        data[i].push('否');
                    }
                } else if (colopts[j].editor.type == 'combobox') {
                    find = false;
                    for (var m = 0, mlen = colopts[j].editor.options.data.length; m < mlen; m++) {
                        if (rows[i][cols[j]] == colopts[j].editor.options.data[m].value) {
                            data[i].push(colopts[j].editor.options.data[m].text);
                            find = true;
                            break;
                        }
                    }
                    if (find == false) {
                        data[i].push(rows[i][cols[j]]);
                    }
                } else {
                    data[i].push(rows[i][cols[j]]);
                }
            }
        }
        var p = {
            cols: coltitles,
            data: data
        };
        return p;
    },
    getChangeUpdate: function (jq) {
        /*
         取修改后的数据对数组 返回:[
         {
         id:nnn,
         col:{
         '已修改列cod':[新值,旧值]
         }
         },....
         ]
         */
        var updatePairArray = new Array();
        var updateRows = jq.datagrid('getChanges', 'updated');
        var oriRows = jq.datagrid('getOriginalRows');
        for (var i = 0, ilen = updateRows.length; i < ilen; i++) {
            var u_id = updateRows[i].id;
            var find_flag = false;
            for (var j = 0, jlen = oriRows.length; j < jlen; j++) {
                if (u_id == oriRows[j].id) {
                    var colpair = {};
                    for (var key in updateRows[i]) {
                        if (oriRows[j].hasOwnProperty(key) && updateRows[i][key] != oriRows[j][key]) {
                            colpair[key] = [updateRows[i][key], oriRows[j][key]];
                        }
                    }
                    updatePairArray.push({
                        id: u_id,
                        cols: colpair
                    });
                    find_flag = true;
                    break;
                }
            }
            if (!find_flag) {
                sy.onError('更新数据未找到原始值', false);
                return null;
            }
        }
        return updatePairArray;
    },
    //param {要插入对象}}
    insertData: function (jq, param) {
        //console.info(jq.editRow);
        var opts = jq.datagrid('options');
        if (opts.editRow == -1) {
            null;
        } else {
            if (jq.datagrid('validateRow', opts.editRow)) {
                jq.datagrid('endEdit', opts.editRow);
            } else {
                $.messager.alert('提示', '现有数据校验失败，不能增加新数据', 'info');
                return;
            }
        }
        /*jq.datagrid('insertRow', {
         index: 0,
         row: param
         });*/
        jq.datagrid('appendRow', param);
        var lastRow = jq.datagrid('getRows').length;
        jq.datagrid('selectRow', lastRow - 1);
        jq.datagrid('beginEdit', lastRow - 1);
        opts.editRow = lastRow - 1;
    },
    //param null
    deleteData: function (jq, param) {
        var selectRow = jq.datagrid('getSelected');
        var opts = jq.datagrid('options');
        var index = undefined;
        if (selectRow != null) {
            index = jq.datagrid('getRowIndex', selectRow);
            if (opts.editRow != -1) {
                if (opts.editRow > index) {
                    opts.editRow = opts.editRow - 1;
                } else {
                    if (opts.editRow == index) {
                        jq.datagrid('endEdit', opts.editRow);
                        opts.editRow = -1;
                    }
                }
            }
            jq.datagrid('deleteRow', index);
            if (opts.editRow != -1) {
                jq.datagrid('selectRow', opts.editRow);
            }
        }
        if (opts.autoSave) {
            var datagridid = jq[0].id;
            $('a[group=' + '"' + datagridid.toString() + '"' + ']').linkbutton('disable');
            jq.datagrid('postUpdateAllData');
            $('a[group=' + '"' + datagridid.toString() + '"' + ']').linkbutton('enable');
        }
    },
    //param 为null
    redo: function (jq, param) {
        var opts = jq.datagrid('options');
        opts.editRow = -1;
        jq.datagrid('rejectChanges');
        jq.datagrid('unselectAll');
    },
    //双击事件调用 先调用执行动态editor代码 再调用此函数 param 为onDblClickRow事件rowIndex
    dbClick: function (jq, param) {
        var opts = jq.datagrid('options');
        //console.info('dbClick begin' + '/' + opts.editRow);
        if (opts.editRow == -1) {
            null;
        } else {
            if (jq.datagrid('validateRow', opts.editRow)) {
                jq.datagrid('endEdit', opts.editRow);
            } else {
                return;
            }
        }
        opts.editRow = param;
        jq.datagrid('beginEdit', param);
        //console.info('dbClickend' + '/' + opts.editRow);
    },
    //单击事件调用, param 为onClickRow事件rowIndex
    click: function (jq, param) {
        var opts = jq.datagrid('options');
        //console.info('click begin' + '/' + opts.editRow);
        if (opts.editRow != -1) {
            if (jq.datagrid('validateRow', opts.editRow)) {
                jq.datagrid('endEdit', opts.editRow);
                opts.editRow = -1;
            } else {
                jq.datagrid('unselectRow', param);
                jq.datagrid('selectRow', opts.editRow);
                return;
            }
        }
        //console.info('click end' + '/' + opts.editRow);
    },
    //手动对datagrid进行编辑完成操作，一般在‘确定’按钮中进行调用 param无传入值
    manualEndEdit: function (jq, param) {
        var opts = jq.datagrid('options');
        if (opts.editRow != -1) {
            if (jq.datagrid('validateRow', opts.editRow)) {
                jq.datagrid('endEdit', opts.editRow);
                opts.editRow = -1;
            } else {
                jq.datagrid('unselectAll');
                jq.datagrid('selectRow', opts.editRow);
                return;
            }
        }
    },
    //ajax提交之前调用，param 为null
    preSave: function (jq, param) {
        var opts = jq.datagrid('options');
        var s = jq.datagrid('getSelected')
        if (s != null) {
            opts.editRow = jq.datagrid('getRowIndex', s);
        }

        if (opts.editRow == -1) {
            return 1;
        } else {
            if (jq.datagrid('validateRow', opts.editRow)) {
                jq.datagrid('endEdit', opts.editRow);
                opts.editRow = -1;
                return 1;
                ;
            } else {
                return 0;
            }
        }
    },
    //ajax提交保存成功之后调用，param 为null
    afterSave: function (jq, param) {
        //将所有row的insert_flag字段设为false
        /*
         var rows = jq.datagrid('getChanges', 'inserted')
         $.each(rows, function (index, item) {
         item.insert_flag = false;
         });
         */
        jq.datagrid('acceptChanges');
    },
    //调用方式 datagrid('addEditor',[{field : 'column名称',editor : {type : 'text'}}]) 可传数组
    addEditor: function (jq, param) {
        if (param instanceof Array) {
            $.each(param, function (index, item) {
                var e = $(jq).datagrid('getColumnOption', item.field);
                e.editor = item.editor;
            });
        } else {
            var e = $(jq).datagrid('getColumnOption', param.field);
            e.editor = param.editor;
        }
    },
    //调用方式 datagrid('removeEditor',['column名称'])  可传数组
    removeEditor: function (jq, param) {
        if (param instanceof Array) {
            $.each(param, function (index, item) {
                var e = $(jq).datagrid('getColumnOption', item);
                e.editor = {};
            });
        } else {
            var e = $(jq).datagrid('getColumnOption', param);
            e.editor = {};
        }
    },
    //返回脏数据
    getDirtyData: function (jq, type) {
        var deleteArray = new Array();
        var updateArray = new Array();
        var insertArray = new Array();
        if (type == 'delete' || type == 'all') {
            var deletedRows = $(jq).datagrid('getChanges', 'deleted');
            for (var i = 0, ilen = deletedRows.length; i < ilen; i++) {
                deleteArray.push({
                    op: 'delete',
                    table: $(jq).datagrid('options').dataTable,
                    id: deletedRows[i].id,
                    subs: {}
                });
            }
        }
        if (type == 'update' || type == 'all') {
            var updateRows = $(jq).datagrid('getChangeUpdate');
            if (updateRows != null && updateRows.length > 0) {
                $.each(updateRows, function (index, data) {
                    updateArray.push({
                        op: 'update',
                        table: $(jq).datagrid('options').dataTable,
                        cols: data.cols,
                        id: data.id,
                        subs: {}
                    });
                });
            }
        }
        if (type == 'insert' || type == 'all') {
            var insertRows = $(jq).datagrid('getChanges', 'inserted');
            for (var i = 0, ilen = insertRows.length; i < ilen; i++) {
                insertArray.push(
                    {op: 'insert',
                        table: $(jq).datagrid('options').dataTable,
                        cols: insertRows[i],
                        id: -1,
                        uuid: (new UUID()).id,
                        subs: {}
                    }
                );
            }
        }
        return {i: insertArray,
            u: updateArray,
            d: deleteArray};
    },
    //调用方式 datagrid('postUpdateAllData')
    postUpdateAllData: function (jq) {
        if ($(jq).datagrid('preSave') == 1) {
            var opts = jq.datagrid('options');
            var dirtyObj = jq.datagrid('getDirtyData', 'all');
            var dirtyArray = dirtyObj.i.concat(dirtyObj.u).concat(dirtyObj.d);
            //删除只传id值
            var p = {
                reqtype: 'update',
                func: opts.updateFuncName,
                rows: dirtyArray
            }
            if (p.rows.length == 0) {
                return;
            }
            $.ajax({
                url: opts.url,
                data: {jpargs: JSON.stringify(p)},
                success: function (returnData, returnMsg, ajaxObj) {
                    var stateCod = parseInt(returnData.stateCod);
                    if (!isNaN(stateCod)) {
                        if (returnData.stateCod == 202) { //更新成功
                            //更新id
                            if (returnData.changeid != null && dirtyObj.i.length > 0) {
                                for (var i = 0, ilen = dirtyObj.i.length; i < ilen; i++) {
                                    if (returnData.changeid.hasOwnProperty(dirtyObj.i[i].uuid)) {
                                        dirtyObj.i[i].cols.id = returnData.changeid[dirtyObj.i[i].uuid];
                                    } else {
                                        sy.onError('主键更新失败', false);
                                        return;
                                    }
                                }
                            }
                            $(jq).datagrid('afterSave');
                        }
                    }
                    $.ajaxSettings.success(returnData, returnMsg, ajaxObj, true);
                }

            });
        } else {
            sy.onError('数据验证失败', false);
        }
    },
    columnMoving: function(jq){
        return jq.each(function(){
            var target = this;
            var cells = $(this).datagrid('getPanel').find('div.datagrid-header td[field]');
            cells.draggable({
                revert:true,
                cursor:'pointer',
                edge:5,
                proxy:function(source){
                    var p = $('<div class="tree-node-proxy tree-dnd-no" style="position:absolute;border:1px solid #ff0000"/>').appendTo('body');
                    p.html($(source).text());
                    p.hide();
                    return p;
                },
                onBeforeDrag:function(e){
                    e.data.startLeft = $(this).offset().left;
                    e.data.startTop = $(this).offset().top;
                },
                onStartDrag: function(){
                    $(this).draggable('proxy').css({
                        left:-10000,
                        top:-10000
                    });
                },
                onDrag:function(e){
                    $(this).draggable('proxy').show().css({
                        left:e.pageX+15,
                        top:e.pageY+15
                    });
                    return false;
                }
            }).droppable({
                accept:'td[field]',
                onDragOver:function(e,source){
                    $(source).draggable('proxy').removeClass('tree-dnd-no').addClass('tree-dnd-yes');
                    $(this).css('border-left','1px solid #ff0000');
                },
                onDragLeave:function(e,source){
                    $(source).draggable('proxy').removeClass('tree-dnd-yes').addClass('tree-dnd-no');
                    $(this).css('border-left',0);
                },
                onDrop:function(e,source){
                    $(this).css('border-left',0);
                    var fromField = $(source).attr('field');
                    var toField = $(this).attr('field');
                    setTimeout(function(){
                        swapField(fromField,toField);
                        $(target).datagrid();
                        $(target).datagrid('columnMoving');
                    },0);
                }
            });

            // swap Field to another location
            function swapField(from,to){
                var columns = $(target).datagrid('options').columns;
                var cc = columns[0];
                _swap(from,to);
                function _swap(fromfiled,tofiled){
                    var fromtemp;
                    var totemp;
                    var fromindex = 0;
                    var toindex = 0;
                    for(var i=0; i<cc.length; i++){
                        if (cc[i].field == fromfiled){
                            fromindex = i;
                            fromtemp = cc[i];
                        }
                        if(cc[i].field == tofiled){
                            toindex = i;
                            totemp = cc[i];
                        }
                    }
                    cc.splice(fromindex,1,totemp);
                    cc.splice(toindex,1,fromtemp);
                }
            }
        });
    }

});
//***************扩展datagrid ***********************//


//***************扩展form****************************//
$.extend($.fn.form.defaults, {
    originalData: {}, //保存通过load方法加载的原始数据
    onLoadSuccess: function (data) {
        $(this).data('form').options.originalData = data;
    }
});
$.extend($.fn.form.methods, {
    getFields: function (jq) {
        var cols = new Array();
        var formcols = jq.serializeArray();
        for (var i = 0, ilen = formcols.length; i < ilen; i++) {
            cols.push(formcols[i].name);
        }
        return cols;
    },
    getOriData: function (jq) {
        //取扩展的originalData
        return $(jq).data('form').options.originalData;
    },
    extReset: function (jq) {
        //扩展reset方法，清空originalData值
        jq.form('reset');
        $(jq).data('form').options.originalData = {};
    },
    getUpdateData: function (jq) {
        var oriData = $(jq).form('getOriData');
        var dirty = {};
        $.each(jq.serializeJson(), function (name, value) {
            if (oriData.hasOwnProperty(name)) {
                if (oriData[name] != value) {
                    dirty[name] = [value, oriData[name]];
                }
            } else {
                if (value != null && value.length > 0) {
                    dirty[name] = [value, ""];
                }
            }
        });
        return dirty;
    }
});

//***************扩展JQuery包装集函数************************
//将form表单值转换成Json格式
(function ($) {
    $.fn.serializeJson = function () {
        var serializeObj = {};
        var array = this.serializeArray();
        var str = this.serialize();
        $(array).each(function () {
            if (serializeObj[this.name]) {
                if ($.isArray(serializeObj[this.name])) {
                    serializeObj[this.name].push(this.value);
                } else {
                    serializeObj[this.name] = [serializeObj[this.name], this.value];
                }
            } else {
                serializeObj[this.name] = this.value;
            }
        });
        return serializeObj;
    };
})(jQuery);

(function ($) {

    /**
     * Displays loading mask over selected element(s). Accepts both single and multiple selectors.
     *
     * @param label Text message that will be displayed on top of the mask besides a spinner (optional).
     *                If not provided only mask will be displayed without a label or a spinner.
     * @param delay Delay in milliseconds before element is masked (optional). If unmask() is called
     *              before the delay times out, no mask is displayed. This can be used to prevent unnecessary
     *              mask display for quick processes.
     */
    $.fn.mask = function (label, delay) {
        $(this).each(function () {
            if (delay !== undefined && delay > 0) {
                var element = $(this);
                element.data("_mask_timeout", setTimeout(function () {
                    $.maskElement(element, label)
                }, delay));
            } else {
                $.maskElement($(this), label);
            }
        });
    };

    /**
     * Removes mask from the element(s). Accepts both single and multiple selectors.
     */
    $.fn.unmask = function () {
        $(this).each(function () {
            $.unmaskElement($(this));
        });
    };

    /**
     * Checks if a single element is masked. Returns false if mask is delayed or not displayed.
     */
    $.fn.isMasked = function () {
        return this.hasClass("masked");
    };

    $.maskElement = function (element, label) {

        //if this element has delayed mask scheduled then remove it and display the new one
        if (element.data("_mask_timeout") !== undefined) {
            clearTimeout(element.data("_mask_timeout"));
            element.removeData("_mask_timeout");
        }

        if (element.isMasked()) {
            $.unmaskElement(element);
        }

        if (element.css("position") == "static") {
            element.addClass("masked-relative");
        }

        element.addClass("masked");

        var maskDiv = $('<div class="loadmask"></div>');

        //auto height fix for IE
        if (navigator.userAgent.toLowerCase().indexOf("msie") > -1) {
            maskDiv.height(element.height() + parseInt(element.css("padding-top")) + parseInt(element.css("padding-bottom")));
            maskDiv.width(element.width() + parseInt(element.css("padding-left")) + parseInt(element.css("padding-right")));
        }

        //fix for z-index bug with selects in IE6
        if (navigator.userAgent.toLowerCase().indexOf("msie 6") > -1) {
            element.find("select").addClass("masked-hidden");
        }

        element.append(maskDiv);

        if (label !== undefined) {
            var maskMsgDiv = $('<div class="loadmask-msg" style="display:none;"></div>');
            maskMsgDiv.append('<div>' + label + '</div>');
            element.append(maskMsgDiv);

            //calculate center position
            maskMsgDiv.css("top", Math.round(element.height() / 2 - (maskMsgDiv.height() - parseInt(maskMsgDiv.css("padding-top")) - parseInt(maskMsgDiv.css("padding-bottom"))) / 2) + "px");
            maskMsgDiv.css("left", Math.round(element.width() / 2 - (maskMsgDiv.width() - parseInt(maskMsgDiv.css("padding-left")) - parseInt(maskMsgDiv.css("padding-right"))) / 2) + "px");

            maskMsgDiv.show();
        }

    };

    $.unmaskElement = function (element) {
        //if this element has delayed mask scheduled then remove it
        if (element.data("_mask_timeout") !== undefined) {
            clearTimeout(element.data("_mask_timeout"));
            element.removeData("_mask_timeout");
        }

        element.find(".loadmask-msg,.loadmask").remove();
        element.removeClass("masked");
        element.removeClass("masked-relative");
        element.find("select").removeClass("masked-hidden");
    };

})(jQuery);


//***************扩展JQuery**************************//

//***************设置Ajax默认参数********************

$.ajaxSetup({
    async: false,
    crossDomain: false, // obviates need for sameOrigin test
    beforeSend: function (xhr, settings) {
        if (!sy.csrfSafeMethod(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", sy.csrftoken);
        }
    },
    type: 'POST',
    //contentType: 'application/x-www-form-urlencoded;charset=utf-8',

    dataType: 'json',
    success: function (returnData, returnMsg, ajaxObj, msgShow) {
        var stateCod = parseInt(returnData.stateCod);
        if (returnData && !isNaN(stateCod)) {
            if (stateCod > 0) {//返回成功
                if (msgShow == false) {
                    return true;
                }
                if (stateCod >= 101 && stateCod <= 200) {
                    $.messager.alert('提示', returnData.msg || '执行成功！', 'info');
                }
                if (stateCod >= 201 && stateCod <= 300) {
                    $.messager.show({
                        title: '',
                        msg: returnData.msg || '执行成功!',
                        timeout: 3000,
                        showType: 'slide'
                    });
                }
                return true;
            } else {//返回错误
                if (returnData.msg && returnData.msg.length > 0) {
                    $.messager.alert('提示', returnData.msg, 'info');
                }
                if (returnData.error && returnData.error.length > 0) {
                    $.messager.show({
                        title: '错误信息',
                        msg: returnData.error.join('\n'),
                        timeout: 3000,
                        showType: 'slide'
                    });
                }
                if (stateCod <= -101 && stateCod >= -200) {//系统级错误返回登录界面
                    sy.onError(returnData.msg, true);
                }
                return false;
            }
        } else {
            $.messager.alert('错误', '返回数据错误！', 'error');
            return false;
        }
    },
    error: function (xhr, msg, e) {

        sy.onError('服务器错误：' + msg, false);
    }

});

//***************设置Ajax默认参数********************//
$(document).bind('ajaxStart', function (event) {
    $('body').mask('加载数据......');
});

$(document).bind('ajaxStop', function () {
    $('body').unmask();
});


