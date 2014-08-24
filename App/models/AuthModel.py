__author__ = 'zhangtao'

from django.db import models
from App.models.BaseModel import BaseModel

class SysCode(BaseModel):
    id = models.AutoField('pk',primary_key=True)
    fld_eng = models.CharField('英文字段名',max_length=20)
    fld_chi = models.CharField('中文字段名',max_length=30)
    cod_name = models.CharField('值名称',max_length=20)
    fld_ext1 = models.CharField('字段扩展值1',blank=True,max_length=20,null=True)
    fld_ext2 = models.CharField('字段扩展值2',blank=True,max_length=20,null=True)
    seq = models.SmallIntegerField('序号')
    def __str__(self):
        return self.fld_chi + ':' + self.cod_name
    class Meta:
        db_table = 'sys_code'
class SysMenu(BaseModel):
    id = models.AutoField('pk',primary_key=True)
    menuname = models.CharField('功能名称',max_length=50)
    menushowname = models.CharField('功能显示名称',max_length=50)
    parent_id = models.ForeignKey('SysMenu',limit_choices_to={'parent_id':0},related_name='+',verbose_name='父功能',db_column='parent_id')
    sortno = models.SmallIntegerField('序号',blank=True,null=True)
    sys_flag = models.NullBooleanField('系统功能标识',blank=True,null=True)
    def __str__(self):
        return self.menushowname
    class Meta:
        db_table = 'sys_menu'
class SysFunc(BaseModel):
    id = models.AutoField('pk',primary_key=True)
    funcname = models.CharField('权限名称',max_length=50)
    ref_tables = models.CharField('涉及表',max_length=100,blank=True,null=True)
    def __str__(self):
        return self.funcname
    class Meta:
        db_table = 'sys_func'
class SysMenuFunc(BaseModel):
    id = models.AutoField('pk',primary_key=True)
    menu_id = models.ForeignKey('SysMenu',verbose_name='功能',related_name='+',db_column='menu_id')
    func_id = models.ForeignKey('SysFunc',verbose_name='权限',related_name='+',db_column='func_id')
    def __str__(self):
        return self.menu_id.menuname + '/' + self.func_id.funcname
    class Meta:
        db_table = 'sys_menu_func'
class User(BaseModel):
    id = models.AutoField('pk',primary_key=True)
    username = models.CharField('用户',max_length=10)
    password = models.CharField('密码',max_length=40)
    lock = models.NullBooleanField('锁住',blank=True,null=True)
    def __str__(self):
        return self.username
    class Meta:
        db_table = 's_user'
class Post(BaseModel):
    id = models.AutoField('pk',primary_key=True)
    postname = models.CharField('岗位名称',max_length=20)
    def __str__(self):
        return self.postname
    class Meta:
        db_table = 's_post'
class PostUser(BaseModel):
    id = models.AutoField('pk',primary_key=True)
    post_id = models.ForeignKey('Post',verbose_name='岗位',related_name='+',db_column='post_id')
    user_id = models.ForeignKey('User',verbose_name='用户',related_name='+',db_column='user_id')
    def __str__(self):
        return self.post_id.postname + '/' + self.user_id.username
    class Meta:
        db_table = 's_postuser'

class PostMenu(BaseModel):
    id = models.AutoField('pk',primary_key=True)
    post_id = models.ForeignKey('Post',verbose_name='岗位',related_name='+',db_column='post_id')
    menu_id = models.ForeignKey('SysMenu',verbose_name='功能',related_name='+',db_column='menu_id')
    active = models.NullBooleanField('显示',blank=True,null=True)
    def __str__(self):
        return self.post_id.postname + '/' + self.menu_id.menuname
    class Meta:
        db_table = 's_postmenu'
class PostMenuFunc(BaseModel):
    id = models.AutoField('pk',primary_key=True)
    post_id = models.ForeignKey('Post',verbose_name='岗位',related_name='+',db_column='post_id')
    menu_id = models.ForeignKey('SysMenu',verbose_name='功能',related_name='+',db_column='menu_id')
    func_id = models.ForeignKey('SysFunc',verbose_name='权限',related_name='+',db_column='func_id')
    def __str__(self):
        return self.post_id.postname + '/' + self.menu_id.menuname + '/' + self.func_id.funcname
    class Meta:
        db_table = 's_postmenufunc'
