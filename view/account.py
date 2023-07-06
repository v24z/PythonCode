# -*-codeing = utf-8 -*-
#@Time:2023 05 15
#@Author:Qu Linyi
#@File:account.py
#@Software: PyCharm
from django import forms
from django.urls import reverse
from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.core.validators import ValidationError
from io import BytesIO


from app01.models import User
from app01.utils.pagination import Pagination
from app01.utils.bootstrap import BootStrapForm,BootStrapModelForm
from app01.utils.encrypt import md5
from app01.utils.code import check_code

class LoginForm(BootStrapForm):
    # 手写字段
    id=forms.CharField(
        label='用户名',
        widget=forms.TextInput,
        required=True           #不得为空
         )
    password=forms.CharField(
        label='密码',
        widget=forms.PasswordInput(render_value=True),
        required=True
    )
    # 生成验证码输入框
    code = forms.CharField(
        label='验证码',
        widget=forms.TextInput(),
        required=True
    )
    def clean_password(self):
        pwd=self.cleaned_data.get('password')
        return md5(pwd)


def login(request):
    if request.method == 'GET':
        form=LoginForm()
        return render(request,'login.html',{'form':form})
    form=LoginForm(data=request.POST)
    if form.is_valid():#获取到输入的数据，进行校验
        """{'id': '1', 'password': '123','code':'xx'}"""
        # 为了方便后面账号密码验证，拿到验证码同时，剔除验证码
        user_input_code = form.cleaned_data.pop('code')
        code = request.session.get('img_code', '')  # 可能已经60s超时，获取不到则置空
        if code.upper() != user_input_code.upper():#统一变大写比较
            form.add_error('code','验证码错误')
            return render(request,'login.html',{'form':form})


        # 去数据库校验用户名和密码是否正确，获取用户对象
        ###  form.cleaned_data 内容是字典,字段名字等的内容和表一致
        admin_object = User.objects.filter(**form.cleaned_data).first()
        """登录失败"""
        if not admin_object:
            form.add_error('password','用户名或密码错误')   #错误信息
            return render(request,'login.html',{'form':form})
        """id和密码正确"""
        # 网站生成随机字符串，写到用户浏览器的cookie中 再写入到session中

        request.session["info"] = \
            {'id': admin_object.id,                          #id
             'name': admin_object.name,                      #姓名
             'password':admin_object.password,               #密码
             'identity':admin_object.get_identity_display()  #身份
             }
        # 登陆成功重新设置session过期时间为7天
        request.session.set_expiry(60 * 60 * 24 * 7)
        """根据身份不同  跳转不同页面  待完成"""
        if request.session["info"]["identity"] == "管理员":

            return redirect('/admin/table/')
        elif request.session["info"]["identity"] == "教师":
            return redirect('/title/tableshow/')
        else:
            return redirect('/stu/titlelist/')


    return render(request,'login.html',{'form':form})

def image_code(request):
    """生成图片验证码"""

    # 调用pillow函数，生成图片
    img,code_string=check_code()
    print(code_string)
    # 创建文件存入内存，不用再读取文件夹
    stream=BytesIO()
    img.save(stream,'png')

    # 写入到自己的cookie中（以便后续验证）
    request.session['img_code']=code_string
    # 给session设置60s超时
    request.session.set_expiry(60)

    return HttpResponse(stream.getvalue())

def logout(request):
    """注销"""
    request.session.clear()
    return redirect('/login/')



class UserModelForm(BootStrapModelForm):
    confirm_password=forms.CharField(
        label="确认密码",
        widget=forms.PasswordInput(render_value=True)
    )
    class Meta:
        model=User
        fields=['name','identity','age','password','confirm_password']
        widgets={
            'password':forms.PasswordInput(render_value=True)
            #'password': forms.PasswordInput(render_value=True)  确认密码错误后不会清空该输入框
        }
    def clean_password(self):
        pwd=self.cleaned_data.get('password')
        return md5(pwd)
    def clean_confirm_password(self):
        confirm_password=md5(self.cleaned_data.get('confirm_password'))
        password=self.cleaned_data.get('password')
        if confirm_password!=password:
            raise ValidationError("密码不一致")  #抛出异常
        #此字段返回的值可以保存到数据库，可在此处对数据进行额外处理
        return confirm_password                 #form.cleaned_data中的值  {'name':‘张三’,'confirm_password':'xxx'}
    #钩子返回加密过的密码

def my_information(request,nid):

    return HttpResponse("还是那就看")

