from django.db import models

# Create your models here.
from App.models.BaseModel import BaseModel


class Client(BaseModel):
    id = models.AutoField('pk',primary_key=True)
    client_name = models.CharField('客户名称',max_length=50,unique=True)
    client_flag = models.NullBooleanField('委托方标识')
    custom_flag = models.NullBooleanField('报关行标识')
    ship_corp_flag = models.NullBooleanField('船公司标识')
    yard_flag = models.NullBooleanField('场站标识')
    port_flag = models.NullBooleanField('码头标识')
    financial_flag = models.NullBooleanField('财务往来单位标识')
    landtrans_flag = models.NullBooleanField('车队标识')
    credit_flag = models.NullBooleanField('信用证公司标识')
    protocol_id = models.ForeignKey('Protocol',blank=True,null=True,verbose_name='协议',related_name='+',db_column='protocol_id')
    def __str__(self):
        return self.client_name
    class Meta:
        db_table = 'c_client'
class CntrType(BaseModel):
    id = models.AutoField('pk',primary_key=True)
    cntr_type = models.CharField('箱型',max_length=4)
    cntr_type_name = models.CharField('箱型描述',max_length=20)
    def __str__(self):
        return self.cntr_type
    class Meta:
        db_table = 'c_cntr_type'
class Action(BaseModel):
    id = models.AutoField('pk',primary_key=True)
    action_name = models.CharField('动态名称',max_length=20)
    require_flag = models.NullBooleanField('必有标识',blank=True,null=True)
    sortno = models.SmallIntegerField('序号')
    def __str__(self):
        return self.action_name
    class Meta:
        db_table = 'c_contract_action'
class Cargo(BaseModel):
    id = models.AutoField('pk',primary_key=True)
    cargo_name = models.CharField('货物名称',max_length=20)
    def __str__(self):
        return self.cargo_name
    class Meta:
        db_table = 'c_cargo'
class CargoType(BaseModel):
    id = models.AutoField('pk',primary_key=True)
    type_name = models.CharField('货物分类名称',max_length=20)
    def __str__(self):
        return self.type_name
    class Meta:
        db_table = 'c_cargo_type'
class Place(BaseModel):
    id = models.AutoField('pk',primary_key=True)
    place_name = models.CharField('地点名称',max_length=20)
    def __str__(self):
        return self.place_name
    class Meta:
        db_table = 'c_place'
class Dispatch(BaseModel):
    id = models.AutoField('pk',primary_key=True)
    place_name = models.CharField('发货地',max_length=30)
    def __str__(self):
        return self.place_name
    class Meta:
        db_table = 'c_dispatch'
class FeeCod(BaseModel):
    id = models.AutoField('pk',primary_key=True)
    fee_name = models.CharField('费用名称',max_length=20)
    protocol_flag = models.NullBooleanField('协议费用标识')
    pair_flag = models.NullBooleanField('代付标识',blank=True,null=True)
    def __str__(self):
        return self.fee_name
    class Meta:
        db_table = 'c_fee'
class PayType(BaseModel):
    id = models.AutoField('pk',primary_key=True)
    pay_name = models.CharField('付款方式',max_length=20)
    def __str__(self):
        return self.pay_name
    class Meta:
        db_table = 'c_pay_type'
class Contract(BaseModel):
    id = models.AutoField('pk',primary_key=True)
    bill_no = models.CharField('提单号',max_length=25,unique=True)
    client_id = models.ForeignKey('Client',verbose_name='客户',limit_choices_to={'client_flag':True},related_name='+',db_column='client_id')
    #contract_type = models.ForeignKey('SysCode',verbose_name='委托类型',limit_choices_to={'fld_eng':'contract_type'},related_name='contract_type_contract',db_column='contract_type')
    #cargo_fee_type = models.ForeignKey('SysCode',verbose_name='货物费用计费类型',limit_choices_to={'fld_eng':'fee_cal_type'},related_name='cargo_fee_type_contract',db_column='cargo_fee_type')
    cargo_piece = models.IntegerField('货物件数',blank=True,null=True)
    cargo_weight = models.DecimalField('货物重量',blank=True,decimal_places=2,max_digits=13,null=True)
    cargo_volume = models.DecimalField('货物体积',blank=True,decimal_places=3,max_digits=13,null=True)
    booking_date = models.DateField('接单日期',blank=True,null=True)
    in_port_date = models.DateField('到港日期',blank=True,null=True)
    return_cntr_date = models.DateField('还箱日期',blank=True,null=True)
    custom_id = models.ForeignKey('Client',blank=True,null=True,limit_choices_to={'custom_flag':True},verbose_name='报关行',related_name='+',db_column='custom_id')
    ship_corp_id = models.ForeignKey('Client',blank=True,null=True,limit_choices_to={'ship_corp_flag':True},verbose_name='船公司',related_name='+',db_column='ship_corp_id')
    port_id = models.ForeignKey('Client',blank=True,null=True,verbose_name='码头',limit_choices_to={'port_flag':True},related_name='+',db_column='port_id')
    yard_id = models.ForeignKey('Client',blank=True,null=True,verbose_name='还箱场站',limit_choices_to={'yard_flag':True},related_name='+',db_column='yard_id')
    finish_time = models.DateTimeField('完成时间',blank=True,null=True)
    finish_flag = models.NullBooleanField('完成标识',blank=True,null=True)
    vslvoy = models.CharField('船名航次',max_length=40,blank=True,null=True)
    contract_no = models.CharField('合同号',max_length=20,blank=True,null=True)
    dispatch_place = models.ForeignKey('Dispatch',verbose_name='发货地',related_name='+',db_column='dispatch_place')
    custom_title1 = models.CharField('报关抬头1',max_length=30,blank=True,null=True)
    custom_title2 = models.CharField('报关抬头2',max_length=30,blank=True,null=True)
    landtrans_id = models.ForeignKey('Client',blank=True,null=True,verbose_name='车队',limit_choices_to={'landtrans_flag':True},related_name='+',db_column='landtrans_id')
    check_yard_id = models.ForeignKey('Client',blank=True,null=True,verbose_name='查验场站',limit_choices_to={'yard_flag':True},related_name='+',db_column='check_yard_id')
    unbox_yard_id = models.ForeignKey('Client',blank=True,null=True,verbose_name='拆箱场站',limit_choices_to={'yard_flag':True},related_name='+',db_column='unbox_yard_id')
    credit_id = models.ForeignKey('Client',blank=True,null=True,verbose_name='信用证公司',limit_choices_to={'credit_flag':True},related_name='+',db_column='credit_id')
    cargo_name = models.ForeignKey('Cargo',blank=True,null=True,verbose_name='货物',related_name='+',db_column='cargo_name')
    origin_place = models.ForeignKey('Place',blank=True,null=True,verbose_name='产地',related_name='+',db_column='origin_place')
    cargo_type = models.ForeignKey('CargoType',blank=True,null=True,verbose_name='货物分类',related_name='+',db_column='cargo_type')
    cntr_freedays = models.IntegerField('箱使天数',blank=True,null=True)
    pre_inport_date = models.DateField('预计到港',blank=True,null=True)
    def __str__(self):
        return self.bill_no
    class Meta:
        db_table = 'contract'
class ContractAction(BaseModel):
    id = models.AutoField('pk',primary_key=True)
    contract_id = models.ForeignKey('Contract',related_name='contract_contractaction',verbose_name='委托',db_column='contract_id')
    action_id = models.ForeignKey('Action',related_name='+',verbose_name='委托动态',db_column='action_id')
    finish_flag = models.NullBooleanField('完成标识',blank=True,null=True)
    finish_time = models.DateTimeField('完成时间',blank=True,null=True)
    def __str__(self):
        return self.contract_id.bill_no + '/' + self.action_id.action_name
    class Meta:
        db_table = 'contract_action'
class ContractCntr(BaseModel):
    id = models.AutoField('pk',primary_key=True)
    contract_id = models.ForeignKey('Contract',related_name='contract_contractcntr',verbose_name='委托',db_column='contract_id')
    cntr_type = models.ForeignKey('CntrType',related_name='+',verbose_name='箱型',db_column='cntr_type')
    cntr_num = models.IntegerField('箱量')
    check_num = models.IntegerField('查验箱量',blank=True,null=True)
    def __str__(self):
        return self.contract_id.bill_no + '/' + self.cntr_type + '/' + str(self.cntr_num)
    class Meta:
        db_table = 'contract_cntr'
