__author__ = 'blaczom@163.com'

import json
from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db import connection
from django.http import HttpResponse

from App.models import *
from zdCommon.dbhelp import rawsql2json,rawsql4request
from zdCommon.dbhelp import  cursorExec2, json2upd
from importhy.settings import DOWNLOAD_PATH, DOWNLOAD_URL


def update_user(request, adict):
    '''  change pass 密码  '''
    l_rtn = { }
    for i_row in adict['rows']: #
        if i_row['op'] in ('update', 'updatedirty'):
            i_row['cols'].pop("password")
        elif i_row['op'] in ('insert'):
            i_row['cols'].update( { 'password': 'ok' } )
    l_rtn.update( json2upd(adict) )
    return l_rtn
def setSessionLogonFail(request):
    request.session['userid'] = None
    request.session['username'] = None
    request.session['logon'] = False

def logon(request):
    '''
        登录
        1.验证此客户+应用是否可用
        2.验证此应用登录,每客户一天最多登录失败3次
    :param request:	{"companyname":"公司代码","name":"用户名","password":"密码"}
    :return: success - {"stateCod": 2, "msg": "登录成功。"}
             fail - {"stateCod": -1, "msg": "登录失败。","error":["失败信息1","失败信息2",....]}
    '''

    l_get = json.loads( request.POST['jpargs'] )
    ls_company = l_get["companyname"]
    ls_user = l_get["name"]
    ls_pass = l_get["password"]
    # if ls_company == "L":
    #     DATABASES["default"]["HOST"] = '127.0.0.1'
    #     DATABASES["default"]["NAME"] = 'importhy'
    # else:
    #     DATABASES["default"]["HOST"] = '172.40.68.103'
    #     DATABASES["default"]["NAME"] = 'yard'
    try:
        l_rtn = {}
        user = User.objects.get(username=ls_user)
        if user.lock == True:
            setSessionLogonFail(request)
            l_rtn = { "stateCod": -2 , "msg": "用户已锁定，请联系管理员解锁"}
            raise Exception
        if user.password == ls_pass:
            request.session['userid'] = user.id
            request.session['username'] = user.username
            request.session['logon'] = True
            user.logon_number = 0
            user.logon_time = datetime.now()
            user.save(update_fields=['logon_number','logon_time'])
            l_rtn = { "stateCod" : 2, "msg": "登录成功。"}
        else:
            setSessionLogonFail(request)
            user.logon_number = 1 if (user.logon_number == None or
                                      (user.logon_time.date() != datetime.now().date())) else (user.logon_number+1)
            user.logon_time = datetime.now()
            if user.logon_number >= 3:
                user.logon_number = None
                user.lock = True
                l_rtn = { "stateCod": -2 ,
                          "msg": "登录失败，用户锁定，请联系管理员解锁"}
            else:
                l_rtn = { "stateCod": -2 ,
                          "msg": "登录失败，密码错误。剩余登录次数:%s" % str(3 - user.logon_number)}
            user.save(update_fields=['logon_number','logon_time','lock'])
    except ObjectDoesNotExist as e:
        l_rtn = { "stateCod": -2 , "msg": "登录失败，用户名不存在。"}
    except Exception as e:
        if len(l_rtn) == 0:
            l_rtn = { "stateCod": -2,"msg":e.args}
    return HttpResponse(json.dumps(l_rtn,ensure_ascii = False))

def logout(request):
    setSessionLogonFail(request)
    return HttpResponse(json.dumps({ "stateCod": 3 },ensure_ascii = False))


# jpargs:{"func":"密码修改","ex_parm":{"oldpw":"ok","newpw":"123"}}
def changePassword(request,ldict):
    l_rtn = { "stateCod" : -2, "msg": "密码更改失败。"}
    l_userid =  request.session['userid']
    if l_userid > 0 :
        ls_newpass = ldict["ex_parm"]["newpw"]
        ls_oldpass = ldict["ex_parm"]["oldpw"]
        l_cur = connection.cursor()
        lrtn = cursorExec2("update s_user set password = %s where id = %s and password = %s ", [ls_newpass,l_userid, ls_oldpass])
        if lrtn > 0 :
            l_rtn = { "stateCod" : 202, "msg": "密码更改成功。"}
            return l_rtn
    return l_rtn

def insert_filter(request,adict):
    l_rtn = { }
    for i_row in adict['rows']: #
        if i_row['op'] in ('insert'):
            i_row['cols'].update( { 'filter_owner': request.session['userid'] } )
    l_rtn.update( json2upd(adict) )
    return l_rtn
def getfilterhead(request):
    '''查询条件查询'''
    ls_sql = "select id,datagrid,filter_type,filter_name from s_filter_head " \
             "where (filter_type = 'G' or filter_owner = %s)" % (request.session['userid'])
    ldict = json.loads( request.POST['jpargs'] )
    return HttpResponse(json.dumps(rawsql2json(*rawsql4request(ls_sql, ldict)),ensure_ascii = False))
def getfilterbody(request):
    '''查询体查询'''
    ldict = json.loads( request.POST['jpargs'] )
    ls_sql = "select " + ", ".join(ldict['cols']) + " from s_filter_body "
    return HttpResponse(json.dumps(rawsql2json(*rawsql4request(ls_sql, ldict)),ensure_ascii = False))


def exportFile(request, adict):
    # 生成文件返回。
    l_rtn = {  "msg":"成功",  "stateCod": "004", "error": [""],
               "result": {"filepath":""}      #  成功返回文件下载路径，失败为空  stateCod -3
    }
    # 保存文件到static，然后返回url
    try:
        l_parm = adict['ex_parm']
        l_parm['title']  # : '文档标题', //如果非空，将第一行各列合并居中写入title
        l_parm['cols']   # :['列名1','列名2','列名3'], //列标题
        l_parm['rows']   # :[      ['行1列1','行1列2','行1列3'],       #         ['行2列1','行2列2','行2列3'],
        import uuid
        import xlsxwriter
        tt = uuid.uuid1().fields
        ls_fileName = str(tt[0]) + str(tt[3]) + str(tt[4]) + ".xlsx"
        ls_file = DOWNLOAD_PATH + ls_fileName
        workbook = xlsxwriter.Workbook(ls_file)
        worksheet = workbook.add_worksheet()
        # Widen the first column to make the text clearer.
        #worksheet.set_column('A:A', 20)
        # Add a bold format to use to highlight cells.
        #bold = workbook.add_format({'bold': True})
        # Write some simple text.
        worksheet.write('A1',l_parm['title'])
        # Text with formatting.              ..........  write( row, cols, content )
        for i in range(len(l_parm['cols'])):
            worksheet.write(1, i, l_parm['cols'][i])
        for i in range(len(l_parm['rows'] )):
            for j in range(len(l_parm['rows'][i])):
                worksheet.write(i + 2, j, l_parm['rows'][i][j])
        workbook.close()
        l_rtn.update({"result": DOWNLOAD_URL + ls_fileName} )
    except Exception as e:
        ls_err = str(e.args)
        l_rtn.update( {  "msg":"失败",  "stateCod": "-3", "error": [ls_err],
               "result": {"filepath":""}      #  成功返回文件下载路径，失败为空  stateCod -3
            } )

    return HttpResponse(json.dumps(l_rtn,ensure_ascii = False))

def exportExcelDirect(request, adict):
    try:
        l_parm = adict['ex_parm']
        l_parm['title']  # : '文档标题', 第一行各列合并居中写入title
        l_parm['cols']   # :['列名1','列名2','列名3'], //列标题
        l_parm['rows']   # :[      ['行1列1','行1列2','行1列3'],       #         ['行2列1','行2列2','行2列3'],
        import io
        from xlsxwriter import Workbook
        output = io.BytesIO()
        workbook = Workbook(output)
        worksheet = workbook.add_worksheet('export')
        worksheet.write('A1',l_parm['title'])
        # Text with formatting.              ..........  write( row, cols, content )
        for i in range(len(l_parm['cols'])):
            worksheet.write(1, i, l_parm['cols'][i])
        for i in range(len(l_parm['rows'] )):
            for j in range(len(l_parm['rows'][i])):
                worksheet.write(i + 2, j, l_parm['rows'][i][j])
        workbook.close()
        output.seek(0)
        response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    except Exception as e:
        ls_err = str(e.args)
        response = HttpResponse(str("导出excel失败：" + ls_err), content_type="application/text")

    response['Content-Disposition'] = "attachment; filename=test.xlsx"
    return response