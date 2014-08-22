__author__ = 'blaczom@163.com'

import json
from django.db import transaction
from zdCommon.dbhelp import rawSql2JsonDict
from zdCommon.utils import log, logErr
from zdCommon.dbhelp import cursorSelect, cursorExec, cursorExec2, json2upd, cursorDict
from datetime import datetime

def dealAuditFee(request):
    '''
     "func" : "处理已收费用核销",
     "ex_parm": {"actfeeid": l_actId , "prefeeid":l_preId}
    '''
    ldict = json.loads( request.POST['jpargs'] )
    list_actId = ldict['ex_parm']["actfeeid"]
    list_preId = ldict['ex_parm']["prefeeid"]
    #  前台bug排除，就没用了。
    if (len(set(list_actId)) != len(list_actId)):
        raise Exception("已收费用id重复")
    if (len(set(list_preId)) != len(list_preId)):
        raise Exception("应收费用id重复")
    # 得到一个处理的seq{"seqnam":aSeqNam }
    ls_sql = "select nextval('seq_4_auditfee')"
    l_seq = cursorSelect(ls_sql)
    ls_seq = ""
    if len(l_seq) > 0 :
        ls_seq = str(l_seq[0][0])
    else:
        raise Exception("取序列号失败")
    #
    l_sumact = 0.0    # 实收费用
    l_sumpre = 0.0
    list_actId.reverse()
    list_preId.reverse()
    l_actId = 0
    l_preId = 0
    ls_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    l_recnam = request.session['userid']
    while True:
        if l_sumact <= l_sumpre:
            if len(list_actId) > 0 :  # 还有 实收 费用。
                l_actId = list_actId.pop()
                l_sumact += float( cursorSelect("select amount from act_fee where id =  " + str(l_actId))[0][0] )
                ls_exec = "update act_fee set ex_over = %s, audit_id=true, audit_tim='%s' where id = %s" % ( ls_seq, ls_now, str(l_actId))
                if cursorExec(ls_exec) < 0 :
                    raise Exception("数据库执行失败")
            else  :# 没有实际费用了，prefee要多，所以插入剩下的prefee
                l_actRecord = cursorSelect("select client_id, fee_typ, fee_cod, contract_id from pre_fee where id = " + str(l_preId ) )
                l_clientid = l_actRecord[0][0]
                l_feetyp = l_actRecord[0][1]
                l_feecod = l_actRecord[0][2]
                l_contractid = l_actRecord[0][3]
                ls_ins = "insert into pre_fee(client_id, contract_id, fee_typ, fee_cod, amount,  fee_tim, rec_nam, rec_tim, ex_from, ex_feeid, remark  )"
                ls_ins += "values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                la_list = list((l_clientid, l_contractid, l_feetyp, l_feecod, l_sumpre - l_sumact, ls_now, l_recnam, ls_now,  ls_seq, 'E','核销自动生成'))
                cursorExec2(ls_ins, la_list)
                break # 退出。没有实际费用
        else:
            if len(list_preId) > 0 :  # 还有 应收 费用。
                l_preId = list_preId.pop()
                l_sumpre += float(cursorSelect("select amount from pre_fee where id =  " + str(l_preId))[0][0] )
                ls_exec = "update pre_fee set ex_over = %s, audit_id=true, audit_tim='%s' where id = %s" % (ls_seq, ls_now, str(l_preId))
                if cursorExec(ls_exec) < 0 :
                    raise Exception("数据库执行失败")
            else:
                l_actRecord = cursorSelect("select client_id, fee_typ, pay_type from act_fee where id = " + str( l_actId ) )
                l_clientid = l_actRecord[0][0]
                l_feetyp = l_actRecord[0][1]
                l_paytype = l_actRecord[0][2]
                ls_ins = "insert into act_fee(client_id, fee_typ, amount, pay_type, fee_tim, rec_nam, rec_tim, ex_from, ex_feeid ,remark )"
                ls_ins += "values(%s, %s, %s, %s,  %s, %s, %s, %s, %s , %s)"
                la_list = list((l_clientid, l_feetyp, l_sumact-l_sumpre, l_paytype, ls_now, l_recnam, ls_now, ls_seq, 'E', '核销自动生成'))
                cursorExec2(ls_ins, la_list)
                break

    ldict_rtn = { "msg": "成功", "stateCod": "202" , "result":{} }
    return(ldict_rtn)

def auditDeleteQuery(request, ldict):
    l_rtn = {}
    l_clientid = str(ldict['ex_parm']['client_id'])
    l_feetyp = str(ldict['ex_parm']['fee_typ'])
    ls_sql = "select ex_over, audit_tim from act_fee where client_id=%s and fee_typ='%s' and audit_id=true order by id desc limit 1 " % (l_clientid, l_feetyp)
    l_actRecord = cursorSelect(ls_sql)
    if len(l_actRecord) > 0 :
        pass
    else:
        l_rtn.update( {"msg": "查询成功，但没有符合条件记录", "error": '',"stateCod":1,"result":{"act":[], "pre":[]} } )
        return l_rtn
    ls_auditTim = l_actRecord[0][1]
    ls_exOver = l_actRecord[0][0]
    ls_sqlpre1 = "select id,contract_id,fee_typ,fee_cod,client_id,amount," \
                 "fee_tim,lock_flag,fee_financial_tim,remark,ex_from,ex_over,ex_feeid,audit_id,audit_tim " \
                 "from pre_fee where audit_id = true " \
                 "and audit_tim = '%s' and ex_over='%s' " % (ls_auditTim, ls_exOver)
    ls_sqlpre2 = "select id,contract_id,fee_typ,fee_cod,client_id,(0-amount) amount," \
                 "fee_tim,lock_flag,fee_financial_tim,remark,ex_from,ex_over,ex_feeid,audit_id,audit_tim " \
                 "from pre_fee where audit_id = false and rec_tim = '%s' and ex_from='%s' " % (ls_auditTim, ls_exOver)
    ls_sqlact1 = "select id,client_id,fee_typ,amount,invoice_no,check_no,pay_type," \
                 "fee_tim,remark,ex_from,ex_over,ex_feeid,audit_id,audit_tim,accept_no " \
                 "from act_fee where audit_id = true " \
                 "and audit_tim = '%s' and ex_over='%s' " % (ls_auditTim, ls_exOver)
    ls_sqlact2 = "select id,client_id,fee_typ,(0-amount) amount,invoice_no,check_no,pay_type," \
                 "fee_tim,remark,ex_from,ex_over,ex_feeid,audit_id,audit_tim,accept_no " \
                 "from act_fee where audit_id = false and rec_tim = '%s' and ex_from='%s' " % (ls_auditTim, ls_exOver)
    try:
        list_pre = rawSql2JsonDict(ls_sqlpre1)
        list_pre.extend(rawSql2JsonDict(ls_sqlpre2))
        list_act = rawSql2JsonDict(ls_sqlact1)
        list_act.extend(rawSql2JsonDict(ls_sqlact2))
        l_result = { "act":list_act, "pre":list_pre }
        l_rtn.update( {"msg": "查询成功", "error":[], "stateCod" : 1, "result": l_result } )
    except Exception as e:
        l_rtn.update( {"msg": "查询失败", "error": list( (str(e.args),) ) , "stateCod" : -5 } )
    return l_rtn

def auditDelete(request, ldict):
    ls_exOver = str(ldict['ex_parm']['ex_over'])
    l_rtn = { }
    if len(ls_exOver) < 1 :
        l_rtn.update( {"msg": "核销删除失败", "error":"没有核销号。请选择已核销的单据" , "stateCod" : -1 } )
        return l_rtn
    ls_sqlPre = "select count(*) from pre_fee where ex_from ='%s' and ex_over<>'' " % ls_exOver
    ls_sqlAct = "select count(*) from act_fee where ex_from ='%s' and ex_over<>'' " % ls_exOver

    li_pre = int(cursorSelect(ls_sqlPre)[0][0])
    li_act = int(cursorSelect(ls_sqlAct)[0][0])
    if li_act + li_pre > 0 :
        l_rtn.update( {"msg": "核销删除失败", "error":"核销号不是最后一次。请选择最后一次进行核销" , "stateCod" : -1 } )
    else:  # 可以删除该核销，删除掉生成的记录，然后update回去原来的号码。
        try:
            l_sql = []
            with transaction.atomic():
                l_sql.append("delete from pre_fee where ex_from='%s'" % ls_exOver)
                l_sql.append("delete from act_fee where ex_from='%s'" % ls_exOver)
                l_sql.append("update act_fee set ex_over = '', audit_id=false, audit_tim=null where ex_over='%s'" % ls_exOver)
                l_sql.append("update pre_fee set ex_over = '', audit_id=false, audit_tim=null where ex_over='%s'" % ls_exOver)
                for i in l_sql:
                    cursorExec(i)
                l_rtn.update( {"msg": "删除成功", "error":[], "stateCod" : 202, "result": [] } )
        except Exception as e:
            l_rtn.update( {"msg": "删除失败", "error": list( (str(e.args),) ) , "stateCod" : -4 } )
    return l_rtn

def auditSumQuery(request, ldict):
    l_rtn = { }
    ls_clientid = str(ldict['ex_parm']['client_id'])
    ls_feetyp = str(ldict['ex_parm']['fee_typ'])
    ls_begin = str(ldict['ex_parm']['begin_audit_tim'])
    ls_end = str(ldict['ex_parm']['end_audit_tim'])
    # 处理参数
    ls_clientsql = " client_id > 0 " if len(ls_clientid) < 1 or int(ls_clientid) < 1 else (" client_id = " + ls_clientid)
    ls_feesql = " " if len(ls_feetyp) < 1 else (" and fee_typ = '%s' " % ls_feetyp)
    ls_timesql = ""
    if len(ls_begin) > 0 : ls_timesql += " and audit_tim > '%s' " % ls_begin
    if len(ls_end) > 0 : ls_timesql  += " and audit_tim < '%s' " % ls_end
    # 生成sql语句
    ls_sql1 = '''select s.client_id, s.fee_typ, s.ex_over,s.audit_tim,s.amount - sum(COALESCE(a.amount,0)) amount
                  from act_fee a right join
                ( select client_id, fee_typ, ex_over,audit_tim,sum(amount) amount from act_fee
            '''
    ls_sql2 = " where audit_id = true and " + ls_clientsql + ls_feesql + ls_timesql
    ls_sql3 = ''' group by client_id, fee_typ, ex_over,audit_tim) s
            on a.ex_from = s.ex_over
            group by s.client_id, s.fee_typ, s.ex_over,s.audit_tim,s.amount
        '''
    # 执行并返回。
    try:
        l_result = rawSql2JsonDict(ls_sql1 + ls_sql2 + ls_sql3)
        l_rtn.update( {"msg": "查询成功", "error":[], "stateCod" : 1, "rows": l_result } )
    except Exception as e:
        l_rtn.update( {"msg": "查询失败", "error": list( (str(e.args),) ) , "stateCod" : -1 } )
    return l_rtn

def auditDetailQuery(request,ldict):
    l_rtn = {}
    ls_exOver = str(ldict['ex_parm']['ex_over'])
    if len(ls_exOver) < 1:
        l_rtn.update( {"msg": "查询失败", "error": list( ("缺少核销参数",) ) , "stateCod" : -1 } )
        return l_rtn

    try:

        list_pre = rawSql2JsonDict("select bill_no,fee_typ,fee_cod,amount from pre_fee,contract "
                                   "where contract.id = pre_fee.contract_id"
                                   "  and ex_over = '%s'" % ls_exOver)
        list_pre.extend(rawSql2JsonDict("select bill_no,fee_typ,fee_cod,(0-amount) amount from pre_fee,contract "
                                        " where contract.id = pre_fee.contract_id"
                                        "   and ex_from = '%s'" % ls_exOver))
        list_act = rawSql2JsonDict("select client_id,fee_typ,amount,pay_type,invoice_no,check_no  from act_fee where ex_over = '%s'" % ls_exOver)
        list_act.extend(rawSql2JsonDict("select client_id,fee_typ,(0-amount) amount,pay_type,invoice_no,check_no from act_fee where ex_from = '%s'" % ls_exOver))

        l_result = { "act":list_act, "pre":list_pre }
        l_rtn.update( {"msg": "查询成功", "error":[], "stateCod" : 1, "result": l_result } )
    except Exception as e:
        l_rtn.update( {"msg": "查询失败", "error": list( (str(e.args),) ) , "stateCod" : -1 } )
    return l_rtn

def contrProFeeGen(aRequest, aDict):
    l_rtn = { }
    l_userid = aRequest.session['userid']
    ls_clientid = str(aDict["ex_parm"]["client_id"])
    ls_begid = str(aDict["ex_parm"]["begin_date"])
    ls_endid = str(aDict["ex_parm"]["end_date"])
    #ls_finid = str(aDict["ex_parm"]["financial_date"])

    ls_fee = "select f_create_protocol_fee(%s,%s,%s,%s)"
    #l_fee = cursorSelect(ls_fee, [ls_clientid,ls_begid,ls_endid,ls_finid,l_userid ])
    l_fee = cursorSelect(ls_fee, [ls_clientid,ls_begid,ls_endid,l_userid ])
    #if l_fee[0][0] < 0 :
    if l_fee[0][0] != 'SUC' :
        #l_rtn.update( {"msg": "失败", "error":[str(l_fee[0][1])], "stateCod" : -1 } )
        l_rtn.update( {"msg": "失败", "error":[str(l_fee[0][0])], "stateCod" : -1 } )
    else:
        #l_rtn.update( {"msg": "查询成功", "error":[], "stateCod" : 101 } )
        l_rtn.update( {"msg": '生成成功', "error":[], "stateCod" : 202 } )
    return l_rtn

def update_oughtfee(request, adict):
    '''  应收费用  lock_flag=true or audit_id=true or ex_feeid='E' 不能更改   '''
    l_rtn = { }
    list_PreId = []
    for i_row in  adict['rows']: #
        if i_row['op'] in ('delete', 'update', 'updatedirty'):
            list_PreId.append( i_row['id'] )
    if len(list_PreId) > 0 :
        l_count = cursorSelect("select count(*) from pre_fee where id in ( %s ) and (lock_flag=true or audit_id=true or ex_feeid='E') " % ",".join(list_PreId))
        if l_count[0][0] > 0 :
            l_rtn.update( { "msg": "失败", "error":["变更委托应付费用被锁或者已经核销"], "stateCod" : -1 } )
            return l_rtn
    l_rtn.update( json2upd(adict) )
    return l_rtn

def update_gotfee(request, adict):
    '''  应收费用  lock_flag=true or audit_id=true or ex_feeid='E'   '''
    l_rtn = { }
    list_ActId = []
    for i_row in  adict['rows']: #
        if i_row['op'] in ('delete', 'update', 'updatedirty'):
            list_ActId.append( i_row['id'] )
    if len(list_ActId) > 0 :
        l_count = cursorSelect("select count(*) from act_fee where id in ( %s ) and (audit_id=true or ex_feeid='E') " % ",".join(list_ActId))
        if l_count[0][0] > 0 :
            l_rtn.update( { "msg": "失败", "error":["变更的已收费用被锁或者已经核销"], "stateCod" : -1 } )
            return l_rtn
    l_rtn.update( json2upd(adict) )
    return l_rtn

def clientFeeDetailReport(request, adict):
    '''  客户费用明细报表   ex_parm:{ client_id:'', //客户id  fee_typ:'', //费用类型  begin_tim:'', //开始时间 end_tim:'' //截止时间 }'''
    l_rtn = { }
    ls_clientId = str(adict['ex_parm']['client_id']).strip()
    ls_feeType = str(adict['ex_parm']['fee_typ']).strip()

    ls_client_q = ("p.client_id = %s and " % ls_clientId) if len(ls_clientId) > 0 else ""
    ls_feeType_q =  ("p.fee_typ = '%s' and " % ls_feeType) if len(ls_feeType) > 0 else ""

    ls_sql = '''
        select c.bill_no,sum(case p.fee_cod when 1 then amount else 0 end) baogan,sum(case p.fee_cod when 2 then amount else 0 end) chaoqi,
        sum(case p.fee_cod when 3 then amount else 0 end) duicun,sum(case p.fee_cod when 4 then amount else 0 end) banyi,
        sum(case p.fee_cod when 5 then amount else 0 end) yanhuo,sum(case p.fee_cod when 6 then amount else 0 end) xunzheng,
        sum(case p.fee_cod when 7 then amount else 0 end) changdi,sum(case p.fee_cod when 8 then amount else 0 end) tuoche,
        sum(case p.fee_cod when 11 then amount else 0 end) zhibao,
        sum(case p.fee_cod in(1,2,3,4,5,6,7,8,11) when true then 0 else amount end) qita
        from pre_fee as p,contract as c
        where  %s  %s  and p.ex_feeid = 'O'
        and (p.fee_financial_tim between '%s' and '%s')
        and p.contract_id = c.id
        group by c.bill_no
        '''

    try:
        list_rtn = rawSql2JsonDict(ls_sql % ( ls_client_q, ls_feeType_q, str(adict['ex_parm']['begin_tim'] ), str(adict['ex_parm']['end_tim'])) )
        l_rtn.update( {"msg": "查询成功", "error":[], "stateCod" : 1, "rows": list_rtn } )
    except Exception as e:
        l_rtn.update( {"msg": "查询失败", "error": list( (str(e.args),) ) , "stateCod" : -1 } )
    return l_rtn


def getRptFeeStruct(request, adict):

    ls_rptid = str(adict["ex_parm"]["rptid"])
    l_rtn = {"msg": "成功", "stateCod": "001", "error": [], "result": [] }
    ls_sqlitem = 'select id,item_name from c_rpt_item where rpt_id = %s order by sort_no' % ls_rptid

    ls_sqlFee = ''' select c_rpt_fee.fee_id,c_fee.fee_name from c_rpt_fee,c_fee
                        where c_rpt_fee.rpt_id = %s and c_rpt_fee.item_id = %s
                       and c_rpt_fee.fee_id = c_fee.id;
               '''
    try:
        l_item = cursorSelect(ls_sqlitem)
        log(ls_sqlitem)
        l_cacheItem = []
        l_cacheFee = []
        for i_item in l_item:
            lx = ls_sqlFee % (str(ls_rptid), str(i_item[0]))   # id
            l_fee = cursorSelect( lx )
            l_cacheItem.append( {"title": i_item[1], "colspan": len(l_fee)} )   # i_item[1] -- name
            for i_fee in l_fee:
                l_cacheFee.append( {"field": str(i_fee[0]), "title": i_fee[1], "align": "right"} )
        l_rtn["result"].append(l_cacheItem)
        l_rtn["result"].append(l_cacheFee)
    except Exception as e:
        l_rtn.update( {"msg": "查询失败", "error": list( (str(e.args),) ) , "stateCod" : -1 } )
    return l_rtn
def queryRptFee(request, adict):
    '''
    1.where  p.client_id = %s and p.fee_typ = '%s'
        如果参数client_id为空 则p.client_id = %s 条件忽略
        如果参数fee_typ为空 则为p.fee_typ = '%s' 条件忽略
2. p.fee_typ 是应收的 金额取正值， 应付的 金额取负值
    '''
    l_rtn = {"msg": "成功", "stateCod": "001", "error": [], "rows": [] }
    ls_clientId = str(adict["ex_parm"]["client_id"])
    ls_feeType = str(adict["ex_parm"]["fee_typ"])
    ls_beginTim = str(adict["ex_parm"]["begin_tim"])
    ls_endTim = str(adict["ex_parm"]["end_tim"])
    ls_rptid = str(adict["ex_parm"]["rpt"])
    ls_sqlFee = '''select c_rpt_fee.fee_id,c_rpt_fee.fee_typ, c_fee.fee_name from c_rpt_fee,c_fee
                      where c_rpt_fee.rpt_id = %s and c_rpt_fee.item_id in
                      (select id from c_rpt_item where rpt_id = %s )
                      and c_rpt_fee.fee_id = c_fee.id;''' % (ls_rptid, ls_rptid)
    try:
        l_fee = cursorSelect(ls_sqlFee)
        l_cacheFeeCod = []
        l_cacheFeeSql = []
        for i_fee in l_fee:
            l_cacheFeeSql.append( (" sum(case (p.fee_cod = %s and p.fee_typ = '%s')" + ' when true then amount else 0 end) "%s" ') % (str(i_fee[0]), str(i_fee[1]), str(i_fee[0]) ) )
            l_cacheFeeCod.append(str(i_fee[0]))
        if len(l_cacheFeeCod) > 0:
            ls_client_q = ("p.client_id = %s and" % ls_clientId) if len(ls_clientId.strip()) > 0 else ""
            ls_feeType_q =  ("p.fee_typ = '%s' and" % ls_feeType) if len(ls_feeType.strip()) > 0 else ""

            ls_sqlAll = ''' select c.bill_no,%s,
                  sum(case fee_typ when 'I' then amount else 0 end) zongji_in,
                  sum(case fee_typ when 'O' then amount else 0 end) zongji_out,
                  sum(case fee_typ when 'I' then amount else 0-amount end) zongji_gain
                  from pre_fee as p,contract as c
                  where   %s %s  p.ex_feeid = 'O'
                  and (c.finish_time between '%s' and '%s')
                  and p.contract_id = c.id
                  group by c.bill_no
            ''' % ( ",".join(l_cacheFeeSql) ,  ls_client_q, ls_feeType_q, ls_beginTim, ls_endTim )
            # % ( ",".join(l_cacheFeeSql) ,  ",".join(l_cacheFeeCod), ls_client_q, ls_feeType_q, ls_beginTim, ls_endTim )

            l_result = rawSql2JsonDict(ls_sqlAll)
            l_zongji_in = sum([float(i["zongji_in"]) for i in l_result])
            l_zongji_out = sum([float(i["zongji_out"]) for i in l_result])
            l_zongji_gain = sum([float(i["zongji_gain"]) for i in l_result])
            l_rtn.update( {"msg": "查询成功", "error":[], "stateCod" : 1, "rows": l_result,
                "footer":[{"bill_no":"合计：",  "zongji_in": l_zongji_in,"zongji_out": l_zongji_out,"zongji_gain": l_zongji_gain }]
                } )
        else:
            l_rtn.update( {"msg": "没定义查询数据列。", "error": [] , "stateCod" : 0 } )
    except Exception as e:
        l_rtn.update( {"msg": "查询失败", "error": list( (str(e.args),) ) , "stateCod" : -1 } )
    return l_rtn

def initProtElemContent(request, adict):
    '''  # 协议要素内容初始化
    import yardApp.ajaxRespFee
    import zdCommon.dbhelp
    aaa = { "func": '协议要素内容初始化',
        "reqtype": 'update',
        "ex_parm": {   "id": '1'  } }
    yardApp.ajaxRespFee.initProtElemContent(aaa, aaa)
    '''
    l_rtn = {"msg": "成功", "stateCod": "001", "error": [], "rows": [] }
    l_recnam = request.session['userid']
    ls_eleId = str(adict["ex_parm"]["id"])
    ls_sqlinit = "select init_data_sql from p_fee_ele where id = %s"
    lds_rtn = cursorSelect(ls_sqlinit, [ls_eleId])
    try:
        if lds_rtn:
            ls_sub = str(lds_rtn[0][0]).replace('"',"'")
            ls_sqlIns = ''' insert into p_fee_ele_lov(ele_id, lov_cod, lov_name, rec_nam, rec_tim)
                      select '%s' as ele_id , lov_cod, lov_name, %s, now()  from
                      ( %s ) tt2
                      where lov_cod not in (select lov_cod from p_fee_ele_lov where ele_id = '%s')
                  ''' %  (ls_eleId,  l_recnam , ls_sub, ls_eleId)
            cursorExec(ls_sqlIns)
        ls_sqlrtn = "select id,ele_id,lov_cod,lov_name,remark from p_fee_ele_lov where ele_id = %s "
        l_result = rawSql2JsonDict(ls_sqlrtn, [ls_eleId])
        l_rtn.update( {"msg": "操作成功", "error":[], "stateCod" : 202, "rows": l_result } )
    except Exception as e:
        l_rtn.update( {"msg": "操作失败", "error": list( (str(e.args),) ) , "stateCod" : -1 } )
    return l_rtn

def queryProtStruct(request, adict):
    '''
    接收参数接口：{
        func: '协议模式结构查询',
        reqtype: 'query',
        ex_parm: {
            modid: 'XXX' //模式id
        }
    '''
    l_rtn = {}
    ls_modId = str(adict["ex_parm"]["modid"])
    ls_sqlfeeMod = "select * from p_fee_mod where id = %s"
    ls_sqlEle = "select * from p_fee_ele where id = %s"
    try:
        lds_feeMod = cursorDict(ls_sqlfeeMod, [ls_modId])
        if lds_feeMod:  # fee mod，仅有1个。
            l_colIndexZip = zip ( ['col_%s' % i for i in range(1,11)], range(1,11))
            i_row =  lds_feeMod[0]
            l_rtn_rows_sum = []
            for i_colzip in l_colIndexZip:
                if i_row[i_colzip[0]] :  # 对所有的有数值的col_n进行判断。ele_name     i_row[i_col[0]]是内部值B
                    lds_ele = cursorDict( ls_sqlEle , [i_row[i_colzip[0]]] )
                    if lds_ele:
                        lds_lov = " select lov_cod, lov_name from p_fee_ele_lov where ele_id = %s "
                        lds_c = cursorSelect( lds_lov, [ str(i_row[i_colzip[0]]) ]  )
                        log(" ---> " + str(i_colzip) )
                        l_rtn_rows_edit = {}
                        if lds_c:
                            l_child = []
                            for i_edit in lds_c :
                                l_child.append( { 'text': i_edit[1], 'value': i_edit[0] } )
                            l_rtn_rows_edit = {
                                'type':'combobox',
                                'options':{ 'textField': 'text',
                                            'valueField': 'value',
                                            'data': l_child}
                                }
                        else:
                            l_rtn_rows_edit = {'type': 'text'}
                        l_rtn_rows_sum.append(  {
                                'title':    lds_ele[0]["ele_name"] ,
                                'field':    'fee_ele%s' % i_colzip[1] ,  #   n为1-10
                                'align':    'right',      #  写死
                                'halign':   'center',     #  写死
                                'sortable': 'true',    #  写死
                                'editor': l_rtn_rows_edit      } )
            l_rtn = {"msg": "成功", "stateCod": "001", "error": [], "rows": l_rtn_rows_sum }
        else:
            l_rtn = {"msg": "成功，无数据", "stateCod": "001", "error": [], "rows": [] }
    except Exception as e:
        l_rtn.update( {"msg": "操作失败", "error": list( (str(e.args),) ) , "stateCod" : -1 } )
    return l_rtn

def copyProFeeRat(aRequest, aDict):
    l_rtn = { }
    l_userid = aRequest.session['userid']
    ls_sourceid = str(aDict["ex_parm"]["source_id"])
    ls_targetid = str(aDict["ex_parm"]["target_id"])

    ls_fee = "select f_copy_protocol_rat(%s,%s,%s)"
    l_fee = cursorSelect(ls_fee, [ls_sourceid,ls_targetid,l_userid ])
    #if l_fee[0][0] < 0 :
    if l_fee[0][0] != 'SUC' :
        #l_rtn.update( {"msg": "失败", "error":[str(l_fee[0][1])], "stateCod" : -1 } )
        l_rtn.update( {"msg": "失败", "error":[str(l_fee[0][0])], "stateCod" : -4 } )
    else:
        #l_rtn.update( {"msg": "查询成功", "error":[], "stateCod" : 101 } )
        l_rtn.update( {"msg": '复制成功', "error":[], "stateCod" : 202 } )
    return l_rtn
