__author__ = 'dh'

import json

from django.db import connection

from App.models import SysMenu,PostMenu,PostUser
from zdCommon.dbhelp import cursorSelect
from zdCommon.utils import logErr, log


def loginOnly():
    pass


def getMenuList():
    '''导航菜单 返回除根节点外的所有节点对象数组'''
    l_menu1 = SysMenu.objects.filter(parent=0).exclude(id=0).order_by('sortno').values('id','menuname','menushowname')
    ldict_1 = []
    if len(l_menu1) > 0:  # 有1级菜单，循环读出到dict中。
        for i_m1 in l_menu1:
            l_menu2 = SysMenu.objects.filter(parent=i_m1['id']).order_by('sortno').values('id','menuname','menushowname')
            ldict_2 = []
            if len(l_menu2) > 0 :
                for i_m2 in l_menu2:
                    ldict_2.append({"id": i_m2['id'], "text": i_m2['menushowname'], "attributes": i_m2['menuname']})
            else:
                pass # no child
            ldict_1.append( { "id": i_m1['id'], "text": i_m1['menushowname'], "attributes": i_m1['menuname'], 'children': ldict_2  } )
    else:
        pass   # no top menu ... how that posible ....
    return(ldict_1)


def getMenuListByUser(aUserId):
    '''
        根据用户id得到菜单结构,排除系统菜单sys_menu.sys_falg = true。
    '''
    if aUserId == 1:
        return getMenuList()
    l_post = PostUser.objects.filter(user=aUserId).values_list('post',flat=True)
    l_menu1 = PostMenu.objects.filter(post__in=l_post,menu__sys_flag=False,menu__parent=0).\
        order_by('menu','menu__sortno').\
        distinct('menu','menu__sortno').\
        values('menu','menu__menushowname','menu__menuname')
    ldict_1 = []
    if len(l_menu1) > 0:  # 有1级菜单，循环读出到dict中。
        for i_m1 in l_menu1:
            l_menu2 = SysMenu.objects.filter(parent=i_m1['menu'],sys_flag=False).order_by('sortno').values('id','menuname','menushowname')
            ldict_2 = []
            if len(l_menu2) > 0 :
                for i_m2 in l_menu2:
                    ldict_2.append({"id": i_m2['id'], "text": i_m2['menushowname'], "attributes": i_m2['menuname']})
            else:
                pass # no child
            ldict_1.append( { "id": i_m1['menu'], "text": i_m1['menu__menushowname'], "attributes": i_m1['menu__menuname'], 'children': ldict_2  } )
    else:
        pass   # no top menu ... how that posible ....
    return(ldict_1)

def checkPrivilege(aDict):
    #  according to  aDict["func"]  ,check the aDict["rows"]    'op': 'insert',
    #            'table': 'c_client',
    #    'subs': { rows: [递归] } //没有就空着

    if aDict['reqtype'] == 'query':
        return True

    ls_sql = "select ref_tables from sys_func where funcname = '%s';" % str(aDict["func"])
    l_table = cursorSelect(ls_sql)    #  l_userFunc[0][0]   [(1), (2)] ...
    ls_tableSet = ",".join( [ i[0] for i in l_table ] ) + ","

    if "rows" in aDict.keys():
        l_rows = aDict["rows"]
        return checkAllRows(l_rows, ls_tableSet )
    else:
        return True

def checkAllRows(aRows, aTableSet):
    for i in aRows:
        l_mark = True
        if "table" in i.keys():
            l_find = i["table"] + ","
            if aTableSet.find(l_find) > -1:
                # 查找子列所有的对象。
                if "subs" in i.keys():
                    if "rows" in i["subs"].keys():
                        if checkAllRows(i["subs"]['rows'], aTableSet):
                            pass
                        else:
                            l_mark = False
            else:
                l_mark = False
        if not l_mark:
            return False
    return True

#@login_required
def getFunc4User(aUserId):
    '''
        返回funcid的list    post_id > 0;
    '''
    ls_sqlfunc = 'select distinct funcname from s_postmenufunc as a, sys_func as b where a.func_id = b.id and a.post_id in (select post_id from s_postuser where user_id = %s)' % str(aUserId)
    l_userFunc = cursorSelect(ls_sqlfunc)    #  l_userFunc[0][0]   [(1), (2)] ...
    return [i[0] for i in l_userFunc]

def getAuth4post(aPostId, aMenuId):
    '''
        返回这个岗位在menu下面都有那些权限。
    '''
    l_postAuth = cursorSelect('select func_id from s_postmenufunc where post_id=%d and menu_id=%d' % (aPostId, aMenuId) )  # menu下的func功能
    # select a.func_id , b.funcname from s_postmenufunc as a  , sys_func  as b where menu_id = 9 and post_id = 2 and a.id = b.id


def getMenuPrivilege(aPostid):
    l_postid = int(aPostid)
    l_func = dict(cursorSelect('select id, funcname from sys_func'))
    #l_funcid = [i[0] for i in l_func]       # 得到功能id 的list
    #l_funcname = [i[1] for i in l_func]       # 得到功能名称 的list
    l_rtn = { }
    l_menu1 = cursorSelect('select id, menuname, menushowname from sys_menu where parent_id = 0 and id <> 0 and sys_flag = false order by sortno;')
    ldict_1 = []
    if len(l_menu1) > 0:  # 有1级菜单，循环读出到dict中。
        for i_m1 in l_menu1:
            l_menu2 = cursorSelect('select id,menuname, menushowname from sys_menu where parent_id = %d order by sortno;' % i_m1[0])
            ldict_2 = []
            if len(l_menu2) > 0 :
                for i_m2 in l_menu2:
                    l_menu3 = cursorSelect('select func_id from sys_menu_func where menu_id = %d' % i_m2[0])  # menu下的func功能。
                    ldict_3 = []
                    if len(l_menu3) > 0 :
                        for i_m3 in l_menu3:   # 列出menu下的func权限，看看当前post有没有这个权限。   checked    indeterminate unckecked
                            l_oldval = False
                            l_countfunc = cursorSelect('select count(1) from s_postmenufunc where post_id=%d and menu_id=%d and func_id=%d' % (l_postid, i_m2[0], i_m3[0]))  # menu下的func功能。
                            if l_countfunc[0][0] > 0 :
                                l_oldval = True
                            l_attr = { "type": "func", "id": str(i_m3[0]), "oldval": l_oldval }
                            l_id = "m" + str(i_m2[0]) + "f" + str(i_m3[0])
                            ldict_3.append( { "id": l_id, "text": l_func[i_m3[0]], "checked": l_oldval, "attributes": l_attr } )   #把菜单有的权限列出来
                    else:
                        pass

                    l_oldval = False
                    l_countmenu2 = cursorSelect('select count(1) from s_postmenu where post_id=%d and menu_id=%d' % (l_postid, i_m2[0]))  # menu下的func功能。
                    if l_countmenu2[0][0] > 0 :
                        l_oldval = True
                    l_attr = { "type": "menu", "id": str(i_m2[0]), "oldval": l_oldval }
                    ldict_2.append({"id": i_m2[0], "text": i_m2[2], "attributes": l_attr, "children": ldict_3 } ) # , "checked": l_oldval  }  )
            else:
                pass # no child
            l_oldval = False
            l_countmenu1 = cursorSelect('select count(1) from s_postmenu where post_id=%d and menu_id=%d' % (l_postid, i_m1[0]))  # menu的func功能。
            if l_countmenu1[0][0] > 0 :
                l_oldval = True
            l_attr = { "type": "menu", "id": str(i_m1[0]) , "oldval": l_oldval }
            ldict_1.append( { "id": i_m1[0], "text": i_m1[2], "attributes": l_attr, 'children': ldict_2 } ) # , "checked": l_oldval  } )
    else:
        pass   # no top menu ... how that posible ....
    #log(ldict_1)
    l_rtn = { "msg":"查询成功", "stateCod": 1, "error": [], "rows": ldict_1   }
    return(l_rtn)

def setMenuPrivilege(request):
    ldict = json.loads( request.POST['jpargs'] )
    '''
    jpargs:{"reqtype":"sysfunc",
        "func":"menufuncpost",
        "rows": [  {"op":"insert",
                    "table":"menu",
                    "menuid":"3",
                    "funcid":-1,
                    "postid":"3" } ,
                    {"op":"insert",
                    "table":"menu",
                    "menuid":"4",
                    "funcid":-1,
                    "postid":"3"    }
                ] }
    s_postmenu( the post menu see or not );   s_postmenufunc ( if the post have the right to do somthing . )
    sys_menu  --  sys_menu_func   -- sys_func
    '''
    l_rtn = {   "error": [""],
                "msg":"",
                "stateCod":  0 ,
                "effectnum": 0 ,
                "changeid" : {'uuid1':'id1'} }
    l_JsonRows = ldict['rows']
    lb_err  = False
    li_count = 0
    try:
        l_cur = connection.cursor()
        for i_row in  l_JsonRows:
            ls_sql = ""
            if i_row['table'] == "menu":     # insert
                if i_row['op'] == "insert":  # ii
                    ls_sql = "insert into s_postmenu(post_id, menu_id, rec_nam, rec_tim) values(%s, %s, %s, now() )" % ( str(i_row['postid']), str(i_row['menuid']), "1" )
                elif i_row['op'] == "delete":  # ii
                    ls_sql = "delete from s_postmenu where post_id = %s and menu_id = %s " % ( str(i_row['postid']), str(i_row['menuid']) )
                else:
                    pass
            elif i_row['table'] == "func":
                if i_row['op'] == "insert":  # ii
                    ls_sql = "insert into s_postmenufunc(post_id, menu_id, func_id, rec_nam, rec_tim) values(%s, %s, %s, %s, now() )" % ( str(i_row['postid']), str(i_row['menuid']), str(i_row['funcid']), "1" )
                elif i_row['op'] == "delete":  # ii
                    ls_sql = "delete from s_postmenufunc where post_id = %s and menu_id = %s and func_id = %s" % ( str(i_row['postid']), str(i_row['menuid']),  str(i_row['funcid']) )
                else:
                    pass
            else:
                pass
            log(ls_sql)
            l_cur.execute(ls_sql)
            li_count += l_cur.cursor.rowcount
    except Exception as e:
        l_rtn["error"].append("注意：" + str(e.args))
        lb_err = True
        logErr("数据库执行错误：%s" % str(e.args))
    finally:
        l_cur.close()
    if lb_err :
        l_rtn["msg"] = "执行失败。"
        l_rtn["stateCod"] = -1
    else:
        l_rtn["msg"] = "执行成功。"
        l_rtn["stateCod"] = 202
    l_rtn["effectnum"] = str(li_count)
    log(l_rtn)
    return(l_rtn)

