__author__ = 'dddh'
import datetime
from django.db import connection
from zdCommon.sysjson import getMenuPrivilege, setMenuPrivilege, getFunc4User,\
    checkPrivilege,commonQuery,returnQueryJson,commonUpdate,returnUpdateJson
from zdCommon.dbhelp import rawsql2combodatajson
from App.ajaxRespFee import *
from App.ajaxr.ajaxRespAuth import *
from App.ajaxRespQuery import *
from App.models import *
##########################################################        GET    ----
def getsysmenu(request):
    '''功能查询 通用查询接口'''
    ldict = json.loads(request.POST['jpargs'])
    return HttpResponse(returnQueryJson(*commonQuery(SysMenu.objects.all(), ldict)))
def getsysfunc(request):
    '''权限查询 通用查询接口'''
    ldict = json.loads(request.POST['jpargs'])
    return HttpResponse(returnQueryJson(*commonQuery(SysFunc.objects.all(), ldict)))
def getsysmenufunc(request):
    '''功能权限查询 通用查询接口'''
    ldict = json.loads(request.POST['jpargs'])
    return HttpResponse(returnQueryJson(*commonQuery(SysMenuFunc.objects.all(), ldict)))
def getuser(request):
    '''用户查询 通用查询接口'''
    ldict = json.loads(request.POST['jpargs'])
    #加上密码字段过滤
    if 'pw' in ldict['cols']:
        del ldict['cols'][ldict['cols'].index('pw')]
    return HttpResponse(returnQueryJson(*commonQuery(User.objects.exclude(username='Admin'), ldict)))
def getpost(request):
    '''岗位查询'''
    ldict = json.loads(request.POST['jpargs'])
    return HttpResponse(returnQueryJson(*commonQuery(Post.objects.all(), ldict)))
def getpostuser(request):
    '''岗位用户查询'''
    ldict = json.loads(request.POST['jpargs'])
    return HttpResponse(returnQueryJson(*commonQuery(PostUser.objects.all(), ldict)))
def getclients(request):
    '''客户查询'''
    ldict = json.loads(request.POST['jpargs'])
    return HttpResponse(returnQueryJson(*commonQuery(Client.objects.all(), ldict)))
def getclientsEx(request, aSql):
    '''核销 客户查询 ？？？？'''
    ls_sql = aSql
    ldict = json.loads(request.POST['jpargs'])
    return HttpResponse(json.dumps(rawsql2json(*rawsql4request(ls_sql, ldict)), ensure_ascii=False))
def getsyscod(request):
    '''系统参数查询'''
    ldict = json.loads(request.POST['jpargs'])
    return HttpResponse(returnQueryJson(*commonQuery(SysCode.objects.all(), ldict)))
# def getAuth(request):
#     ldict = json.loads(request.POST['jpargs'])
#     ls_sql = "select " + ", ".join(ldict['cols']) + " from sys_menu where parent_id <> 0 "
#    return HttpResponse(json.dumps(rawsql2json(*rawsql4request(ls_sql, ldict)), ensure_ascii=False))
def getcntrtype(request):
    '''箱型查询'''
    ldict = json.loads(request.POST['jpargs'])
    return HttpResponse(returnQueryJson(*commonQuery(CntrType.objects.all(), ldict)))
def getaction(request):
    '''动态类型查询'''
    ldict = json.loads(request.POST['jpargs'])
    return HttpResponse(returnQueryJson(*commonQuery(Action.objects.all(), ldict)))
def getdispatch(request):
    '''发货地查询'''
    ldict = json.loads(request.POST['jpargs'])
    return HttpResponse(returnQueryJson(*commonQuery(Dispatch.objects.all(), ldict)))
def getcargo(request):
    '''货物查询'''
    ldict = json.loads(request.POST['jpargs'])
    return HttpResponse(returnQueryJson(*commonQuery(Cargo.objects.all(), ldict)))
def getcargotype(request):
    '''货物分类查询'''
    ldict = json.loads(request.POST['jpargs'])
    return HttpResponse(returnQueryJson(*commonQuery(CargoType.objects.all(), ldict)))
def getplace(request):
    '''产地查询'''
    ldict = json.loads(request.POST['jpargs'])
    return HttpResponse(returnQueryJson(*commonQuery(Place.objects.all(), ldict)))
def getfeecod(request):
    '''费用名称查询'''
    ldict = json.loads(request.POST['jpargs'])
    return HttpResponse(returnQueryJson(*commonQuery(FeeCod.objects.all(), ldict)))
def getpaytype(request):
    '''付款方式查询'''
    ldict = json.loads(request.POST['jpargs'])
    return HttpResponse(returnQueryJson(*commonQuery(PayType.objects.all(), ldict)))
def getprivilege(request):
    ldict = json.loads(request.POST['jpargs'])
    return HttpResponse(json.dumps(getMenuPrivilege(ldict['ex_parm']['postid']), ensure_ascii=False))
def getrpt(request):
    '''费用报表头查询'''
    ldict = json.loads(request.POST['jpargs'])
    return HttpResponse(returnQueryJson(*commonQuery(Rpt.objects.all(), ldict)))
def getrptitem(request):
    '''费用报表项目查询'''
    ldict = json.loads(request.POST['jpargs'])
    return HttpResponse(returnQueryJson(*commonQuery(RptItem.objects.all(), ldict)))
def getrptfee(request):
    '''费用报表费用查询'''
    ldict = json.loads(request.POST['jpargs'])
    return HttpResponse(returnQueryJson(*commonQuery(RptItemFee.objects.all(), ldict)))
def getprotocol(request):
    '''协议查询'''
    ldict = json.loads(request.POST['jpargs'])
    return HttpResponse(returnQueryJson(*commonQuery(Protocol.objects.all(), ldict)))
def getprotocolele(request):
    '''协议要素查询'''
    ldict = json.loads(request.POST['jpargs'])
    return HttpResponse(returnQueryJson(*commonQuery(FeeEle.objects.all(), ldict)))
def getprotocolelelov(request):
    '''协议要素内容查询'''
    ldict = json.loads(request.POST['jpargs'])
    return HttpResponse(returnQueryJson(*commonQuery(FeeEleLov.objects.all(), ldict)))
def getprotocolmod(request):
    '''协议模式查询'''
    ldict = json.loads(request.POST['jpargs'])
    return HttpResponse(returnQueryJson(*commonQuery(FeeMod.objects.all(), ldict)))
def getprotocolmodremark(request):
    '''协议模式备注查询'''
    ls_sql = "select id,mod_name,mod_descript from p_fee_mod"
    ldict = json.loads(request.POST['jpargs'])
    return HttpResponse(returnQueryJson(*commonQuery(FeeMod.objects.all(), ldict)))

def getprotocolfeemod(request):
    '''协议费用模式查询'''
    ls_sql = "select id,protocol_id,fee_id,mod_id,sort_no,active_flag,remark from p_protocol_fee_mod"
    ldict = json.loads(request.POST['jpargs'])
    return HttpResponse(json.dumps(rawsql2json(*rawsql4request(ls_sql, ldict)), ensure_ascii=False))
def getprotococlrat(request):
    ls_sql = "select id,protocol_id,fee_id,mod_id,fee_ele1,fee_ele2,fee_ele3,fee_ele4,fee_ele5," \
             "fee_ele6,fee_ele7,fee_ele8,fee_ele9,fee_ele10,fee_rat,discount_rat from p_protocol_rat"
    ldict = json.loads(request.POST['jpargs'])
    return HttpResponse(json.dumps(rawsql2json(*rawsql4request(ls_sql, ldict)), ensure_ascii=False))

def getcontract(request):
    ls_sql = "select id,bill_no,vslvoy,cargo_name,origin_place,client_id,cargo_piece,cargo_weight," \
             "cargo_volume,booking_date,in_port_date,return_cntr_date,custom_id,ship_corp_id,port_id," \
             "yard_id,finish_flag,finish_time,remark,contract_no,dispatch_place,custom_title1," \
             "custom_title2,landtrans_id,check_yard_id,unbox_yard_id,credit_id,cargo_type,cntr_freedays," \
             "pre_inport_date from contract"
    ldict = json.loads(request.POST['jpargs'])
    return HttpResponse(json.dumps(rawsql2json(*rawsql4request(ls_sql, ldict)), ensure_ascii=False))
def getcontractbybill(request):
    ls_sql = "select id,bill_no,vslvoy,cargo_name,client_id,in_port_date,remark from contract"
    ldict = json.loads(request.POST['jpargs'])
    return HttpResponse(json.dumps(rawsql2json(*rawsql4request(ls_sql, ldict)), ensure_ascii=False))
def getcontractaction(request):
    ls_sql = "select id,contract_id,action_id,finish_flag,finish_time,remark from contract_action"
    ldict = json.loads(request.POST['jpargs'])
    return HttpResponse(json.dumps(rawsql2json(*rawsql4request(ls_sql, ldict)), ensure_ascii=False))
def getcontractcntr(request):
    ls_sql = "select id,contract_id,cntr_type,cntr_num,check_num,remark from contract_cntr"
    ldict = json.loads(request.POST['jpargs'])
    return HttpResponse(json.dumps(rawsql2json(*rawsql4request(ls_sql, ldict)), ensure_ascii=False))
def getcontractprefeein(request):
    ls_sql = "select id,contract_id,fee_typ,fee_cod,client_id,amount,fee_tim,fee_financial_tim," \
             "lock_flag,audit_id,ex_feeid,create_flag,remark from pre_fee " \
             "where fee_typ = 'I' and ex_feeid = 'O'"
    ldict = json.loads(request.POST['jpargs'])
    return HttpResponse(json.dumps(rawsql2json(*rawsql4request(ls_sql, ldict)), ensure_ascii=False))
def getcontractprefeeout(request):
    ls_sql = "select id,contract_id,fee_typ,fee_cod,client_id,amount,fee_tim,fee_financial_tim," \
             "lock_flag,audit_id,ex_feeid,create_flag,remark from pre_fee " \
             "where fee_typ = 'O' and ex_feeid = 'O'"
    ldict = json.loads(request.POST['jpargs'])
    return HttpResponse(json.dumps(rawsql2json(*rawsql4request(ls_sql, ldict)), ensure_ascii=False))
def getJson4sql(request, aSql):
    '''已收核销查询'''
    ldict = json.loads(request.POST['jpargs'])
    return HttpResponse(json.dumps(rawsql2json(*rawsql4request(aSql, ldict)), ensure_ascii=False))
def getJson4sqlEx(request, aSql, aSqlCount):
    return HttpResponse(json.dumps(rawsql2json(aSql, aSqlCount), ensure_ascii=False))
def getSequence(aDict):
    ''' aDict = {"ex_parm": {"seqname":"seq_4_auditfee"} }
        seq_4_auidtfee  费用核销。结单号的序列号
        create sequence seq_4_auditfee increment by 1 minvalue 1 no maxvalue start with 1;
        return:        "msg":"",     "stateCod":0 、 -10、 -100、-1000 。 "":"result":
    '''
    ldict_rtn = {"msg": "成功", "stateCod": "0", "result": {}}
    ls_sql = "select nextval('" + str(aDict["ex_parm"]["seqnam"]) + "')"
    l_seq = cursorSelect(ls_sql)
    if len(l_seq) > 0:
        ldict_rtn.update({"result": {"seqno": str(l_seq[0][0])}})
    else:
        ldict_rtn.update({"stateCod": "-1"})
    return ldict_rtn
##################日志
def gettabledescription(request):
    '''表注释'''
    #ldict = json.loads(request.POST['jpargs'])
    ls_sql = "select tablename,table_description from v_tabledescription"
    ls_sqlcount = "select count(1) from v_tabledescription"
    return HttpResponse(json.dumps(rawsql2combodatajson(ls_sql, ls_sqlcount), ensure_ascii=False))

def getcoldescription(request):
    '''字段注释
       参数:exparm:{'table_name':'XXXX'}
    '''
    ldict = json.loads(request.POST['jpargs'])
    ls_sql = "select name,comment from v_coldescription where tablename = '%s' " % ldict['ex_parm']['table_name']
    ls_sqlcount = "select count(1) from v_coldescription where tablename = '%s' " % ldict['ex_parm']['table_name']
    return HttpResponse(json.dumps(rawsql2combodatajson(ls_sql, ls_sqlcount), ensure_ascii=False))
def getcolrender(request):
    '''日志查询 处理选择的表+字段 返回前台界面查询值输入框
        date和time 型返回日期框
        integer 判断是否是外键，是外键返回下拉
        其他类型返回文本框
     列表框 日期框  '''
    ldict = json.loads(request.POST['jpargs'])
    #查询指定列的数据类型
    ls_typesql = "select type from v_coldescription where table_name = '%s' and name = '%s'" %(ldict['ex_parm']['table_name'],ldict['ex_parm']['field_name'])
    #下面sql返回外键注释和关联表oid，外键注释约定为显示字段，
    ls_foreignsql = "select obj_description(f.oid),confrelid tableoid " \
             "from pg_constraint f,pg_class c,pg_attribute a " \
             "where f.contype = 'f' and f.conrelid = c.oid " \
             "and c.relname = '%s' and c.oid = a.attrelid " \
             "and a.attname = '%s' " \
             "and a.attnum =  f.conkey[1]" % (ldict['ex_parm']['table_name'],ldict['ex_parm']['field_name'])

#############################################################    UPDATE    -----
def updateRaw(aDict):
    '''
    aDict:{
        'jpargs':json.loads(request.POST['jpargs'])   通用update参数，见文件interface,
        'userid':request.session['userid']) 当前操作员id
        'time':request时间
    }
    '''
    #ldict = json.loads(request.POST['jpargs'])
    lRtn = commonUpdate(aDict['jpargs'],aDict['userid'],aDict['time'])
    return HttpResponse(returnUpdateJson(lRtn))
#####################################################  common interface ----------
def dealPAjax(request):
    ls_err = ""
    l_rtn = {}
    try:
        if ('userid' not in request.session):
            l_rtn = {
                'error': [],
                'msg': '登录过期，请重新登录',
                'stateCod': -101
            }
            return ( HttpResponse(json.dumps(l_rtn, ensure_ascii=False)))
        l_userid = request.session['userid']
        ldict = json.loads(request.POST['jpargs'])
        l_pdict = {
            'jpargs':ldict,
            'userid':l_userid,
            'time':datetime.now()
        }
        log(ldict)
        # 判断是否有调用的权限。
        if (l_userid == 1) \
                or (ldict['func'] in ('功能查询', '权限查询', '功能权限查询', 'excel导出', '文件导出',
                                      '查询条件查询', '查询体查询', '查询增加', '查询条件删除',
                                      '费用报表结构')):
            pass
        elif (ldict['func'] in getFunc4User(str(l_userid))):
            # check if the function is valid
            if checkPrivilege(ldict):
                pass
            else:
                ls_errmsg = "功能溢出权限：操作数据库表非法"
                l_rtn = {"error": [ls_errmsg],
                         "msg": ldict['func'] + " " + ls_errmsg,
                         "stateCod": -1}
                return ( HttpResponse(json.dumps(l_rtn, ensure_ascii=False)))
        else:
            l_rtn = {"error": [ls_err],
                     "msg": ldict['func'] + "没有执行权限",
                     "stateCod": -1}
            return ( HttpResponse(json.dumps(l_rtn, ensure_ascii=False)))

        with transaction.atomic():

            #########系统管理
            if ldict['func'] == '功能查询':
                return (getsysmenu(request))
            elif ldict['func'] == '功能维护':
                return (updateRaw(l_pdict))
            elif ldict['func'] == '权限查询':
                return (getsysfunc(request))
            elif ldict['func'] == '权限维护':
                return (updateRaw(l_pdict))
            elif ldict['func'] == '功能权限查询':
                return (getsysmenufunc(request))
            elif ldict['func'] == '功能权限维护':
                return (updateRaw(l_pdict))
            elif ldict['func'] == '系统参数查询':
                return (getsyscod(request))
            elif ldict['func'] == '系统参数维护':
                return (updateRaw(l_pdict))
            elif ldict['func'] == '协议要素查询':
                return (getprotocolele(request))
            elif ldict['func'] == '协议要素维护':
                return (updateRaw(l_pdict))
            elif ldict['func'] == '协议模式查询':
                return (getprotocolmod(request))
            elif ldict['func'] == '协议模式维护':
                return (updateRaw(l_pdict))
            #######系统配置管理
            elif ldict['func'] == '密码修改':
                l_rtn = changePassword(request, ldict)
                return HttpResponse(json.dumps(l_rtn, ensure_ascii=False))
            elif ldict['func'] == '用户查询':
                return (getuser(request))
            elif ldict['func'] == '用户维护':
                for i_row in l_pdict['jpargs']['rows']: #
                    if i_row['op'] in ('update', 'updatedirty'):
                        i_row['cols'].pop("pw",'ok')
                    elif i_row['op'] in ('insert'):
                        i_row['cols'].update( { 'pw': 'ok' } )
                return (updateRaw(l_pdict))
            elif ldict['func'] == '岗位查询':
                return (getpost(request))
            elif ldict['func'] == '岗位维护':
                return (updateRaw(l_pdict))
            elif ldict['func'] == '岗位用户查询':
                return (getpostuser(request))
            elif ldict['func'] == '岗位用户维护':
                return (updateRaw(l_pdict))
            elif ldict['func'] == '岗位权限查询':
                return (getprivilege(request))
            elif ldict['func'] == "岗位权限维护":
                return (HttpResponse(json.dumps(setMenuPrivilege(l_pdict), ensure_ascii=False)))



            elif ldict['func'] == '查询条件查询':
                return (getfilterhead(request))
            elif ldict['func'] == '查询体查询':
                return (getfilterbody(request))
            elif ldict['func'] == '箱型查询':
                return (getcntrtype(request))
            elif ldict['func'] == '动态类型查询':
                return (getaction(request))
            elif ldict['func'] == '发货地查询':
                return (getdispatch(request))
            elif ldict['func'] == '费用名称查询':
                return (getfeecod(request))
            elif ldict['func'] == '付款方式查询':
                return (getpaytype(request))
            elif ldict['func'] == '客户查询':
                return (getclients(request))
            elif ldict['func'] == '货物查询':
                return (getcargo(request))
            elif ldict['func'] == '货物分类查询':
                return (getcargotype(request))
            elif ldict['func'] == '产地查询':
                return (getplace(request))
            ##-----------计费协议----------------------------------
            elif ldict['func'] == '协议查询':
                return (getprotocol(request))
            elif ldict['func'] == '协议要素内容查询':
                return (getprotocolelelov(request))
            elif ldict['func'] == '模式描述查询':
                return (getprotocolmodremark(request))

            elif ldict['func'] == '协议费用模式查询':
                return (getprotocolfeemod(request))
            elif ldict['func'] == '协议费率查询':
                return (getprotococlrat(request))

            ############## 费用  ###################################
            elif ldict['func'] == '委托查询':
                return (getcontract(request))
            elif ldict['func'] == '业务明细报表查询':
                return (getContractDetail(request, ldict))
            elif ldict['func'] == '委托动态查询':
                return (getcontractaction(request))
            elif ldict['func'] == '委托箱查询':
                return (getcontractcntr(request))
            elif ldict['func'] == '提单查询':
                return (getcontractbybill(request))
            elif ldict['func'] == '委托应收查询':
                return (getcontractprefeein(request))
            elif ldict['func'] == '委托应付查询':
                return (getcontractprefeeout(request))
            #-------核销费用查询--------------------------------------------------------
            elif ldict['func'] == '已收付费用查询':
                ls_sql = "select id,client_id,fee_typ,amount,invoice_no,check_no,accept_no,pay_type,fee_tim,audit_id,ex_feeid " \
                         "from act_fee " \
                         "where ex_feeid = 'O' "
                return (getJson4sql(request, ls_sql))
            elif ldict['func'] == '已收核销已收查询':
                ls_sql = "select id,client_id,fee_typ,amount,invoice_no,check_no,pay_type,fee_tim,off_flag from act_fee"
                return (getJson4sql(request, ls_sql))
            elif ldict['func'] == '已收核销应收查询':
                l_clientid = str(ldict['ex_parm']['client_id'])
                ls_sql = "select  id,contract_id, fee_typ, fee_cod, client_id,amount,fee_tim,lock_flag, remark from pre_fee where client_id = %s" % l_clientid
                return (getJson4sql(request, ls_sql))
            elif ldict['func'] == '核销删除查询':
                l_rtn = auditDeleteQuery(request, ldict)
                return HttpResponse(json.dumps(l_rtn, ensure_ascii=False))
            elif ldict['func'] == '费用报表头查询':
                return (getrpt(request))
            elif ldict['func'] == '费用报表项目查询':
                return (getrptitem(request))
            elif ldict['func'] == '费用报表项目费用查询':
                return (getrptfee(request))
            elif ldict['func'] == '费用报表结构':
                return HttpResponse(json.dumps(getRptFeeStruct(request, ldict), ensure_ascii = False))
            elif ldict['func'] == '客户费用明细报表':
                return HttpResponse(json.dumps(queryRptFee(request, ldict), ensure_ascii = False))

            elif ldict['func'] == '核销删除':
                l_rtn = auditDelete(request, ldict)
                return HttpResponse(json.dumps(l_rtn, ensure_ascii=False))
            ##--------------------------------------------------
            elif ldict['func'] == '已收核销客户查询':
                ls_t = "select * from c_client where id > 0 "  #查询有未结费用的客户。
                return (getclientsEx(request, ls_t))
            elif ldict['func'] == '协议费用生成':
                l_rtn = contrProFeeGen(request, ldict)
                return HttpResponse(json.dumps(l_rtn, ensure_ascii=False))
            ########################################################## update
            elif ldict['func'] == '查询增加':
                return (HttpResponse(json.dumps(insert_filter(request, ldict), ensure_ascii=False)))
            elif ldict['func'] == '查询条件删除':
                return (updateRaw(request))
            elif ldict['func'] == '箱型维护':
                return (updateRaw(request))
            elif ldict['func'] == '发货地维护':
                return (updateRaw(request))
            elif ldict['func'] == '动态类型维护':
                return (updateRaw(request))
            elif ldict['func'] == '费用名称维护':
                return (updateRaw(request))
            elif ldict['func'] == '付款方式维护':
                return (updateRaw(request))
            elif ldict['func'] == '客户维护':
                return (updateRaw(request))
            elif ldict['func'] == '货物维护':
                return (updateRaw(request))
            elif ldict['func'] == '货物分类维护':
                return (updateRaw(request))
            elif ldict['func'] == '产地维护':
                return (updateRaw(request))
            elif ldict['func'] == '委托维护':
                return (updateRaw(request))
            elif ldict['func'] == '委托锁定':
                return (updateRaw(request))
            elif ldict['func'] == '委托解锁':
                return (updateRaw(request))
            elif ldict['func'] == '应收付费用维护':
                return (HttpResponse(json.dumps(update_oughtfee(request, ldict), ensure_ascii=False)))
            elif ldict['func'] == '应收付费用锁定':
                return (updateRaw(request))
            elif ldict['func'] == '应收付费用解锁':
                return (updateRaw(request))
            elif ldict['func'] == '已收付费用维护':
                return (HttpResponse(json.dumps(update_gotfee(request, ldict), ensure_ascii=False)))
            ########################################
            elif ldict['func'] == "取序列号":
                return (HttpResponse(json.dumps(getSequence(ldict), ensure_ascii=False)))
            ################################################  商务、核销     #######
            elif ldict['func'] == "核销":  # 导航
                return ( HttpResponse(json.dumps(dealAuditFee(request), ensure_ascii=False)))
            elif ldict['func'] == '实收付未核销查询':  # ajax 查询
                ls_sql = "select id,client_id,fee_typ,amount,invoice_no,check_no,pay_type,fee_tim,ex_feeid,remark " \
                         "from act_fee " \
                         "where COALESCE(audit_id,false) = false "
                return (getJson4sql(request, ls_sql))
            elif ldict['func'] == '应收付未核销查询':  # ajax 查询
                ls_sql = "select pre_fee.id,pre_fee.contract_id,contract.bill_no,pre_fee.fee_typ,pre_fee.fee_cod," \
                         "pre_fee.amount,pre_fee.fee_tim,pre_fee.ex_feeid,pre_fee.remark " \
                         "from pre_fee,contract " \
                         "where pre_fee.contract_id = contract.id and COALESCE(pre_fee.audit_id,false) = false "
                return (getJson4sql(request, ls_sql))
            elif ldict['func'] == '核销汇总查询':  # ajax 查询
                l_rtn = auditSumQuery(request, ldict)
                return HttpResponse(json.dumps(l_rtn, ensure_ascii=False))
            ##3---------------------------------------------------------------------
            elif ldict['func'] == '核销明细查询':  # ajax 查询
                l_rtn = auditDetailQuery(request, ldict)
                return HttpResponse(json.dumps(l_rtn, ensure_ascii=False))
            elif ldict['func'] == '费用报表头维护':
                return (updateRaw(request))
            elif ldict['func'] == '费用报表项目维护':
                return (updateRaw(request))
            elif ldict['func'] == '费用报表项目费用维护':
                return (updateRaw(request))
            ##-----------计费协议----------------------------------
            elif ldict['func'] == '协议维护':
                return (updateRaw(request))
            elif ldict['func'] == '协议要素内容维护':
                return (updateRaw(request))
            elif ldict['func'] == '协议要素内容初始化':
                l_rtn = initProtElemContent(request, ldict)
                return HttpResponse(json.dumps(l_rtn, ensure_ascii=False))
            elif ldict['func'] == '协议费用模式维护':
                return (updateRaw(request))
            elif ldict['func'] == '协议模式结构查询':
                l_rtn = queryProtStruct(request, ldict)
                return HttpResponse(json.dumps(l_rtn, ensure_ascii=False))
            elif ldict['func'] == '协议费率维护':
                return (updateRaw(request))
            elif ldict['func'] == '协议费率复制':
                return HttpResponse(json.dumps(copyProFeeRat(request, ldict), ensure_ascii = False))

            #########################################################3
            elif ldict['func'] == '业务汇总报表查询':
                return getBussSumary(request, ldict)
            elif ldict['func'] == '文件导出':
                return exportFile(request, ldict)
            elif ldict['func'] == 'excel导出':
                return exportExcelDirect(request, ldict)
            ##########################日志###################
            elif ldict['func'] == '表注释查询':
                return gettabledescription(request)
            elif ldict['func'] == '字段注释查询':
                return getcoldescription(request)
            else:
                pass
    except Exception as e:
        logErr("ajaxResp.dealPAjax执行错误：%s" % str(e.args))
        ls_err = str(e.args)
    # 前面没有正确返回，这里返回一个错误。
    finally:
        #sql日志
        for q in connection.queries:
            log(q)

    l_rtn = {
        "error": [ls_err],
        "msg": ldict['func'] + "执行失败",
        "stateCod": -1,
    }
    return ( HttpResponse(json.dumps(l_rtn, ensure_ascii=False)))
