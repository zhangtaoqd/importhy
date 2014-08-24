__author__ = 'zhangtao'
from django.db import models
from App.models.BaseModel import BaseModel

class PreFee(BaseModel):
    id = models.AutoField('pk',primary_key=True)
    contract_id = models.ForeignKey('Contract',related_name='contract_prefee',verbose_name='委托',db_column='contract_id')
    fee_typ = models.CharField('费用类型',max_length=1,choices=(('I','应收'),('O','应付')))
    fee_cod = models.ForeignKey('FeeCod',related_name='+',verbose_name='费用名称',db_column='fee_cod')
    client_id = models.ForeignKey('Client',related_name='+',limit_choices_to={'financial_flag':True},verbose_name='客户',db_column='client_id')
    amount = models.DecimalField('金额',blank=True,null=True,max_digits=10,decimal_places=2)
    fee_tim = models.DateTimeField('费用时间')
    fee_financial_tim = models.DateTimeField('财务统计时间')
    lock_flag = models.NullBooleanField('锁定',blank=True,null=True)
    ex_feeid = models.CharField('生成方式',max_length=1,choices=(('O','原生'),('E','拆分')))
    ex_from = models.CharField('来源号',max_length=36,blank=True,null=True)
    ex_over = models.CharField('完结号',max_length=36,blank=True,null=True)
    audit_id =  models.NullBooleanField('核销',blank=True,null=True)
    audit_tim = models.DateTimeField('核销时间')
    currency_cod = models.CharField('货币',max_length=3,choices=(('RMB','人民币'),('USD','美元')))
    create_flag = models.CharField('费用产生方式',max_length=1,choices=(('M','手工录入'),('P','协议生成')))
    def __str__(self):
        return self.contract_id.bill_no + '/' + self.fee_typ + '/' + self.fee_cod.fee_name + '/' + self.client_id.client_name + '/' + str(self.amount)
    class Meta:
        db_table = 'pre_fee'
class ActFee(BaseModel):
    id = models.AutoField('pk',primary_key=True)
    client_id = models.ForeignKey('Client',related_name='+',limit_choices_to={'financial_flag':True},verbose_name='客户',db_column='client_id')
    fee_typ = models.CharField('费用类型',max_length=1,choices=(('I','已收'),('O','已付')))
    amount = models.DecimalField('金额',blank=True,null=True,max_digits=10,decimal_places=2)
    invoice_no = models.CharField('发票号',max_length=30,blank=True,null=True)
    check_no = models.CharField('支票号',max_length=30,blank=True,null=True)
    accept_no = models.CharField('承兑号',max_length=30,blank=True,null=True)
    pay_type = models.ForeignKey('PayType',related_name='+',verbose_name='付费类型',db_column='pay_type')
    fee_tim = models.DateTimeField('付费时间')
    ex_feeid = models.CharField('生成标记',max_length=1,choices=(('O','原生'),('E','拆分')))
    ex_from = models.CharField('来源号',max_length=36,blank=True,null=True)
    ex_over = models.CharField('完结号',max_length=36,blank=True,null=True)
    audit_id =  models.NullBooleanField('核销',blank=True,null=True)
    audit_tim = models.DateTimeField('核销时间')
    currency_cod = models.CharField('货币',max_length=3,choices=(('RMB','人民币'),('USD','美元')))
    def __str__(self):
        return self.client_id.client_name + '/' + self.fee_typ + '/' + self.pay_type.pay_name + '/' + str(self.amount)
    class Meta:
        db_table = 'act_fee'
class FilterHead(BaseModel):
    id = models.AutoField('pk',primary_key=True)
    datagrid = models.CharField('datagrid名称',max_length=100)
    filter_type = models.CharField('查询类型',max_length=1,choices=(('G','全局'),('P','个人')))
    filter_owner = models.ForeignKey('User',related_name='+',verbose_name='查询人员',db_column='filter_owner')
    filter_name = models.CharField('查询名称',max_length=50)
    def __str__(self):
        return self.filter_name
    class Meta:
        db_table = 's_filter_head'
class FilterBody(BaseModel):
    id = models.AutoField('pk',primary_key=True)
    filter_id = models.ForeignKey('FilterHead',related_name='+',verbose_name='查询头',db_column='filter_id')
    content_type = models.CharField('查询内容类型',max_length=1,choices=(('W','where条件'),('S','排序条件'),('C','字段列表')))
    content_col = models.CharField('查询字段名',max_length=30)
    content_condition = models.CharField('查询条件',max_length=10,blank=True,null=True)
    content_value = models.CharField('查询值',max_length=50,blank=True,null=True)
    value_text = models.CharField('字面值',max_length=100,blank=True,null=True)
    display_value = models.CharField('显示值',max_length=100,blank=True,null=True)
    class Meta:
        db_table = 's_filter_body'
class Rpt(BaseModel):
    id = models.AutoField('pk',primary_key=True)
    rpt_name = models.CharField('报表名称',max_length=30)
    def __str__(self):
        return self.rpt_name
    class Meta:
        db_table = 'c_rpt'
class RptItem(BaseModel):
    id = models.AutoField('pk',primary_key=True)
    item_name = models.CharField('报表项目名称',max_length=30)
    rpt_id = models.ForeignKey('Rpt',related_name='+',verbose_name='报表id',db_column='rpt_id')
    sort_no = models.IntegerField('序号',blank=True,null=True)
    def __str__(self):
        return self.item_name
    class Meta:
        db_table = 'c_rpt_item'
class RptItemFee(BaseModel):
    id = models.AutoField('pk',primary_key=True)
    rpt_id = models.ForeignKey('Rpt',related_name='+',verbose_name='报表id',db_column='rpt_id')
    item_id = models.ForeignKey('RptItem',related_name='+',verbose_name='报表项目id',db_column='item_id')
    fee_id = models.ForeignKey('FeeCod',related_name='+',verbose_name='费用id',db_column='fee_id')
    fee_typ = models.CharField('费用类型',max_length=1,choices=(('I','应收'),('O','应付')))
    class Meta:
        db_table = 'c_rpt_fee'
class Protocol(BaseModel):
    id = models.AutoField('pk',primary_key=True)
    protocol_name = models.CharField('协议名称',max_length=50,unique=True)
    write_date = models.DateField('签订日期',blank=True,null=True)
    validate_date = models.DateField('有效日期',blank=True,null=True)
    def __str__(self):
        return self.protocol_name
    class Meta:
        db_table = 'p_protocol'
class FeeEle(BaseModel):
    id = models.AutoField('pk',primary_key=True)
    ele_name = models.CharField('要素名称',max_length=30)
    init_data_sql = models.CharField('要素初始化sql语句',max_length=100,blank=True,null=True)
    def __str__(self):
        return self.ele_name
    class Meta:
        db_table = 'p_fee_ele'
class FeeEleLov(BaseModel):
    id = models.AutoField('pk',primary_key=True)
    ele_id = models.ForeignKey('FeeEle',verbose_name='要素',related_name='+',db_column='ele_id')
    lov_cod = models.CharField('要素内容代码',max_length=10)
    lov_name = models.CharField('要素内容名称',max_length=20)
    def __str__(self):
        return self.lov_name
    class Meta:
        db_table = 'p_fee_ele_lov'

class FeeMod(BaseModel):
    id = models.AutoField('pk',primary_key=True)
    mod_name = models.CharField('计费模式名称',max_length=20)
    col_1 = models.ForeignKey('FeeEle',verbose_name='要素1',related_name='+',db_column='col_1',blank=True,null=True)
    col_2 = models.ForeignKey('FeeEle',verbose_name='要素2',related_name='+',db_column='col_2',blank=True,null=True)
    col_3 = models.ForeignKey('FeeEle',verbose_name='要素3',related_name='+',db_column='col_3',blank=True,null=True)
    col_4 = models.ForeignKey('FeeEle',verbose_name='要素4',related_name='+',db_column='col_4',blank=True,null=True)
    col_5 = models.ForeignKey('FeeEle',verbose_name='要素5',related_name='+',db_column='col_5',blank=True,null=True)
    col_6 = models.ForeignKey('FeeEle',verbose_name='要素6',related_name='+',db_column='col_6',blank=True,null=True)
    col_7 = models.ForeignKey('FeeEle',verbose_name='要素7',related_name='+',db_column='col_7',blank=True,null=True)
    col_8 = models.ForeignKey('FeeEle',verbose_name='要素8',related_name='+',db_column='col_8',blank=True,null=True)
    col_9 = models.ForeignKey('FeeEle',verbose_name='要素9',related_name='+',db_column='col_9',blank=True,null=True)
    col_10 = models.ForeignKey('FeeEle',verbose_name='要素10',related_name='+',db_column='col_10',blank=True,null=True)
    mod_descript = models.CharField('模式描述',max_length=500,blank=True,null=True)
    deal_process = models.CharField('模式绑定存储过程',max_length=50,blank=True,null=True)
    def __str__(self):
        return self.mod_name
    class Meta:
        db_table = 'p_fee_mod'
class ProtocolMod(BaseModel):
    id = models.AutoField('pk',primary_key=True)
    protocol_id = models.ForeignKey('Protocol',verbose_name='协议',related_name='+',db_column='protocol_id')
    fee_id = models.ForeignKey('FeeCod',verbose_name='费用名称',related_name='+',db_column='fee_id')
    mod_id = models.ForeignKey('FeeMod',verbose_name='模式',related_name='+',db_column='mod_id')
    sort_no = models.IntegerField('序号',blank=True,null=True)
    active_flag = models.NullBooleanField('激活')
    class Meta:
        db_table = 'p_protocol_fee_mod'
class ProtocolFeeRat(BaseModel):
    id = models.AutoField('pk',primary_key=True)
    protocol_id = models.ForeignKey('Protocol',verbose_name='协议',related_name='+',db_column='protocol_id')
    fee_id = models.ForeignKey('FeeCod',verbose_name='费用名称',related_name='+',db_column='fee_id')
    mod_id = models.ForeignKey('FeeMod',verbose_name='模式',related_name='+',db_column='mod_id')
    fee_ele1 = models.CharField('要素1',max_length=10,blank=True,null=True)
    fee_ele2 = models.CharField('要素2',max_length=10,blank=True,null=True)
    fee_ele3 = models.CharField('要素3',max_length=10,blank=True,null=True)
    fee_ele4 = models.CharField('要素4',max_length=10,blank=True,null=True)
    fee_ele5 = models.CharField('要素5',max_length=10,blank=True,null=True)
    fee_ele6 = models.CharField('要素6',max_length=10,blank=True,null=True)
    fee_ele7 = models.CharField('要素7',max_length=10,blank=True,null=True)
    fee_ele8 = models.CharField('要素8',max_length=10,blank=True,null=True)
    fee_ele9 = models.CharField('要素9',max_length=10,blank=True,null=True)
    fee_ele10 = models.CharField('要素10',max_length=10,blank=True,null=True)
    fee_rat = models.DecimalField('费率',max_digits=8,decimal_places=2,blank=True,null=True)
    discount_rat = models.DecimalField('折扣金额',max_digits=8,decimal_places=2,blank=True,null=True)
    class Meta:
        db_table = 'p_protocol_rat'
