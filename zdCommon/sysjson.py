__author__ = 'dh'

import json

from django.db import connection

from App.models import SysMenu,SysMenuFunc,PostMenu,PostUser,PostMenuFunc
from zdCommon.dbhelp import cursorSelect,getModelByTableName,ServerToClientJsonEncoder
from zdCommon.utils import logErr, log


def loginOnly():
    pass



def commonQuery(aQuerySet,aRequestDict):
    '''
    通用查询
    :param aQuerySet: 指定model.objects.all()
    :param aRequestDict: request参数,见interface文件
    :return: (查询分页ValuesQuerySet ,查询总行数rowCount)
    '''
    values = aQuerySet
    if 'page' not in aRequestDict:
        li_page = None
    else:
        li_page = int(aRequestDict.get('page', 1))
    if 'rows' not in aRequestDict:
        li_rows = None
    else:
        li_rows = int(aRequestDict.get('rows', 50))

    ld_sort = aRequestDict.get('sort', {})
    ld_filter = aRequestDict.get('filter', {})
    ld_cols = aRequestDict.get('cols',[])
    filter_kwargs = {}
    exclude_kwargs = {}
    sort_args = []
    for f in ld_filter:
        if f['cod'] == None or len(f['cod']) == 0:
            raise Exception("无法识别的属性，请重新输入")
        if f['value'] == None:
            raise Exception("无法识别的属性值，请重新输入")
        if f['operatorTyp'] == '等于':
            filter_kwargs[f['cod'] + '__exact'] = f['value']
        elif f['operatorTyp'] == '大于':
            filter_kwargs[f['cod'] + '__gt'] = f['value']
        elif f['operatorTyp'] == '小于':
            filter_kwargs[f['cod'] + '__lt'] = f['value']
        elif f['operatorTyp'] == '大于等于':
            filter_kwargs[f['cod'] + '__gte'] = f['value']
        elif f['operatorTyp'] == '小于等于':
            filter_kwargs[f['cod'] + '__lte'] = f['value']
        elif f['operatorTyp'] == '不等于':
            exclude_kwargs[f['cod'] + '__exact'] = f['value']
        elif f['operatorTyp'] == '包含':
            filter_kwargs[f['cod'] + '__contains'] = f['value']
        elif f['operatorTyp'] == '不包含':
            exclude_kwargs[f['cod'] + '__contains'] = f['value']
        elif f['operatorTyp'] == '属于':
            filter_kwargs[f['cod'] + '__in'] = f['value'].split(',')
        elif f['operatorTyp'] == '不属于':
            exclude_kwargs[f['cod'] + '__in'] = f['value'].split(',')
        elif f['operatorTyp'] == '介于':
            v_array = f['value'].split(',')
            if len(v_array) != 2:
                raise Exception("缺少属性值，请重新输入")
            filter_kwargs[f['cod'] + '__range'] = f['value']
        elif f['operatorTyp'] == '不介于':
            v_array = f['value'].split(',')
            if len(v_array) != 2:
                raise Exception("缺少属性值，请重新输入")
            exclude_kwargs[f['cod'] + '__range'] = f['value']
        else:
            logErr("无法识别的操作符号%s" % f['operatorTyp'])
            raise Exception("无法识别的操作符号，请通知管理员")
    if len(exclude_kwargs) > 0:
        values = values.exclude(**exclude_kwargs)
    if len(filter_kwargs) > 0:
        values = values.filter(**filter_kwargs)
    rowsCount = values.count()
    for s in ld_sort:
        if s['cod'] == None :
            raise Exception("无法识别的排序属性，请重新输入")
        if s['order_typ'] == None:
            raise Exception("无法识别的属性值，请重新输入")
        if s['order_typ'] == '升序':
            sort_args.append(s['cod'])
        elif s['order_typ'] == '降序':
            sort_args.append('-' + s['cod'])
        else:
            logErr("无法识别的排序类型%s" % s['order_typ'])
            raise Exception("无法识别的排序类型，请通知管理员")
    if len(sort_args) > 0:
        values = values.order_by(*sort_args)
    if li_page != None and li_rows != None:
        values = values[(li_page-1)*li_rows:li_page*li_rows]
    values = values.values(*ld_cols)
    return (values,rowsCount)
def returnQueryJson(aQuerySet, aRowsCount):
    '''
        根据aQuerySet语句，返回数据和记录总数。.
    '''

    l_rtn = {"msg": "查询完毕", "error":[] }
    try:
        l_rtn.update( { "stateCod": 1 if len(aQuerySet) > 0 else 201  , "total":aRowsCount, "rows": list(aQuerySet) } )
    except Exception as e:
        logErr("查询失败：%s" % str(e.args))
        raise e
    return json.dumps(l_rtn,ensure_ascii=False,cls=ServerToClientJsonEncoder).replace('true','"true"').replace('false','"false"')
def commonUpdate(aDict,aRec_nam,aRec_tim,aRtn = None):
    '''
    通用update
    :param rDict:request参数 见文件interface
    :return:见文件interface
    '''
    if aRtn == None:
        aRtn = {
            'stateCod':202,
            'msg':'修改成功',
            'changeid':{}
        }
    l_rows = aDict['rows']
    try:
        for item in l_rows:
            tm = getModelByTableName(item['table'])
            if tm == None:
                raise Exception("表参数错误")
            if item['op'] == 'insert':
                l_cols = item['cols']
                l_cols.pop('id',0)
                l_cols.update({'rec_nam':aRec_nam,'rec_tim':aRec_tim})
                o = tm(**l_cols)
                o.save()
                l_newid = o.id
                aRtn['changeid'].update({
                        item['uuid']:l_newid
                })
                if len(item['uuid']) > 10 and 'rows' in item['subs']:
                    for s_item in item['subs']['rows']:
                        for (k,v) in s_item['cols'].items():
                            if v == item['uuid']:
                                s_item['cols'][k] = l_newid

            elif item['op'] in ['update','updatedirty']:
                l_cols = item['cols']
                l_cols.pop('id',0)
                l_oldid = item['id']
                o = tm.objects.get(id=l_oldid)
                for k,v in l_cols.items():
                    if item['op'] == 'update':
                        if o[k] == v[1]:
                            o[k] = v[0]
                        else:
                            raise Exception("更新数据已发生变动，修改数据失败")
                    else:
                        o[k] = v[0]
                o.save(update_fields=list(l_cols.keys()))
            elif item['op'] == 'delete':
                l_oldid = item['id']
                tm.objects.filter(id__in=l_oldid).delete()
                #o = tm.objects.get(id=l_oldid)
                #o.delete()
            else:
                raise Exception("修改类型错误")
            if 'rows' in item['subs']:
                commonUpdate(item['subs'],aRec_nam,aRec_tim,aRtn)
    except Exception as e:
        logErr("错误：%s" % str(e.args))
        raise e
    return aRtn
def returnUpdateJson(aResult):
    l_rtn = {"error": [],
             "msg":"修改失败",
             "stateCod": -4 ,
             "effectnum": 0 ,
             "changeid" : {},
             "result":{}
    }
    try:
        l_rtn.update(aResult)
    except Exception as e:
        logErr("数据库执行错误：%s" % str(e.args))
        l_rtn.update({"stateCod": -4, "error": str(l_rtn['error']), "msg":"执行失败" })
        raise e
    return json.dumps(l_rtn,ensure_ascii=False,cls=ServerToClientJsonEncoder)

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
    l_menu1 = PostMenu.objects.filter(post__in=l_post,menu__sys_flag='N',menu__parent=0).\
        order_by('menu','menu__sortno').\
        distinct('menu','menu__sortno').\
        values('menu','menu__menushowname','menu__menuname')
    ldict_1 = []
    if len(l_menu1) > 0:  # 有1级菜单，循环读出到dict中。
        for i_m1 in l_menu1:
            l_menu2 = SysMenu.objects.filter(parent=i_m1['menu'],sys_flag='N').order_by('sortno').values('id','menuname','menushowname')
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

def getMenuPrivilege(aPostid):
    l_postid = int(aPostid)
    l_menu1 = SysMenu.objects.filter(parent=0,sys_flag='N').exclude(id=0).\
        order_by('sortno').values('id','menushowname')
    ldict_1 = []
    for m1 in l_menu1:
        l_menu2 = SysMenu.objects.filter(parent=m1['id']).order_by('sortno').values('id','menushowname')
        ldict_2 = []
        for m2 in l_menu2:
            l_func = SysMenuFunc.objects.filter(menu=m2['id']).values('func','func__funcname')
            ldict_3 = []
            for f in l_func:
                l_oldval = False
                l_fCount = PostMenuFunc.objects.filter(post=l_postid,menu=m2['id'],func=f['func']).count()
                if l_fCount > 0:
                    l_oldval = True
                l_attr = { "type": "func", "id": str(f['func']), "oldval": l_oldval }
                l_id = "m" + str(m2['id']) + "f" + str(f['func'])
                ldict_3.append( { "id": l_id, "text": f['func__funcname'], "checked": l_oldval, "attributes": l_attr } )   #把菜单有的权限列出来
            l_oldval = False
            l_m2Count = PostMenu.objects.filter(post=l_postid,menu=m2['id']).count()
            if l_m2Count > 0:
                l_oldval = True
            l_attr = { "type": "menu", "id": str(m2['id']), "oldval": l_oldval }
            ldict_2.append({"id": m2['id'], "text": m2['menushowname'], "attributes": l_attr, "children": ldict_3 } ) # , "checked": l_oldval  }  )
        l_oldval = False
        l_m1Count = PostMenu.objects.filter(post=l_postid,menu=m1['id']).count()  # menu的func功能。
        if l_m1Count > 0 :
            l_oldval = True
        l_attr = { "type": "menu", "id": str(m1['id']) , "oldval": l_oldval }
        ldict_1.append( { "id": m1['id'], "text": m1['menushowname'], "attributes": l_attr, 'children': ldict_2 } ) # , "checked": l_oldval  } )
    l_rtn = { "msg":"查询成功", "stateCod": 1, "error": [], "rows": ldict_1 }
    return(l_rtn)

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

