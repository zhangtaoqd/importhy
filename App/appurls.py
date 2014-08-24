from App.ajaxr import ajaxResp

__author__ = 'zhangtao'
from django.conf.urls import patterns, url
from App.render import intfex


urlpatterns = patterns('',
    url(r'^$', intfex.index,name='index'),
    url(r'^logon/$', "App.ajaxr.ajaxRespAuth.logon",name='logon'),
    url(r'^logout/$', "App.ajaxr.ajaxRespAuth.logout",name='logout'),

    # 处理页面左边导航的功能。
    url('^dealmenureq/$', intfex.dealMenuReq,name='dealmenureq'),
    url('^dealPAjax/$', ajaxResp.dealPAjax,name='dealPAjax'),
    # 实验室
    url(r'^lab/$',"App.lab.index", name='labindex'),
    url(r'^lab/getfunc/$',"App.lab.getfunc", name='labgetfunc'),
    url(r'^lab/post/$',"App.lab.getJsonPost", name='labpost'),
    url(r'^lab/test/$',"App.lab.test", name='labtest'),
    # http://127.0.0.1:8000/importhy/lab/getfunc/?func=getJson1&&args=%22aaa%22

)

#  appurls.py --->  ajaxResp ---> function.