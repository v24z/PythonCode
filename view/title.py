# -*-codeing = utf-8 -*-
#@Time:2023 05 09
#@Author:Qu Linyi
#@File:title.py
#@Software: PyCharm

from django.shortcuts import render,redirect,HttpResponse
from app01.models import Title,User,Stuapply
from django import forms
from app01.utils.pagination import Pagination
from app01.utils.bootstrap import BootStrapModelForm

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from app01.utils.encrypt import md5
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator


# def title_list (request):
#     title_list=Title.objects.all()
#     return render(request,"title_list.html",{"title_list":title_list})
#选题基本信息
class TitleModelForm(forms.ModelForm):
    title_name=forms.CharField(min_length=5,label="选题名称")
    #state=forms.CharField(disabled=True)
    #advice=forms.CharField(disabled=True)
    class Meta:
        model=Title
        fields=["title_name","title_quality",
                "fit_major","work_time","work_difficulty",
                "title_source","title_introduce",
                "paper_requirement"]
        widgets={
            "title_introduce":forms.Textarea(attrs={'cols': 50, 'rows': 5, 'resize': 'none'}),
            "paper_requirement": forms.Textarea(attrs={'cols': 50, 'rows': 5, 'resize': 'none'})
        }
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        #循环找到所有的插件，添加类名
        for name, field in self.fields.items():
            # if name=="state":
            #     field.widget.attrs = {'class': 'form-control', 'placeholder': field.label,'value':"待审核"}
            # if name=="title_introduce" or name=="paper_requirement":
            #     field.widget.attrs = {'class':'form-control','placeholder':field.label,'cols': 10}
            field.widget.attrs={'class':'form-control','placeholder':field.label}

def title_list(request):
    #userID=1            #后期集中用session中传过来的ID替换
    userID=request.session['info']['id']
    """"选题表"""
    data_dict={}            #空字典就是查询所有
    search_data=request.GET.get("q","")
    if search_data:   #如果传过来的search_data不为空
        data_dict["title_name__contains"]=search_data

    title_list=Title.objects.filter(**data_dict,teacher=userID);
    page_object=Pagination(request,title_list)
    form=TitleModelForm()
    context={
        "title_list": page_object.page_queryset,
        "search_data": search_data,
        "page_string":page_object.html(),
        "form":form
    }
    #return render(request,'title_list.html', {"title_list":title_list,"search_data":search_data})
    return render(request,'title_list.html', context)


# def title_add_mf(request):
#     if request.method == "GET":
#         form=TitleModelForm()
#         row=Title.objects.filter(id=1).first()
#         print(row)
#         return render(request,'title_add_mf.html',{"form":form})
#     #数据校验
#     form=TitleModelForm(data=request.POST)
#     if form.is_valid():
#         """"添加额外数据，后期用session中存储的id替换"""
#         form.instance.teacher=User.objects.get(id=request.session['info']['id'])
#         form.save()
#         #print(form.cleaned_data)
#         return redirect('/title/list/')
#     return render(request,'title_add_mf.html',{"form":form})

# """"待删除"""
# def title_delete(request,nid):
#     """"删除选题"""
#     #获取id
#     #nid=request.GET.get('nid')
#     Title.objects.filter(id=nid).delete()
#     return redirect("/title/list/")
""""待删除"""
# def title_edit(request,nid):
#     """"编辑用户"""
#     row_object=Title.objects.filter(id=nid).first()
#     if request.method == "GET":
#         #根据ID获取要编辑的那一行数据
#         form=TitleModelForm(instance=row_object)#加上instance 即可在表单中显示数据库中的数据
#         return render(request,"title_edit.html",{"form":form})
#
#     #告诉modelForm是更新数据，不是新增数据
#     form=TitleModelForm(data=request.POST,instance=row_object)
#     if form.is_valid():
#         form.save()
#         return redirect('/title/list/')
#     return render(request, "title_edit.html", {"form": form})

def title_review(request):
    myID=request.session['info']['id']  #后期换成session中的id
    form = TitleModelForm()
    myTitleIDList=Title.objects.filter(teacher=myID)
    print(myTitleIDList)
    title_list=Stuapply.objects.filter(titlename__in=myTitleIDList)
    page_object = Pagination(request, title_list)
    context = {
        "title_list": page_object.page_queryset,
        "page_string": page_object.html(),
        "form": form
    }

    return render(request,"title_review.html",context)


# def approve_stu_request(request,nid):
#     """此处应检查该学生是否已经有通过的选题"""
#     Stuapply.objects.filter(id=nid).update(applystate="通过")
#     return redirect("/title/review/")

def negative_stu_request(request,nid):
    Stuapply.objects.filter(id=nid).update(applystate="拒绝")
    return redirect("/title/review/")

def approve_stu(request):
    uid=request.GET.get("uid")
    stuid=request.GET.get("stuid")
    exist_approve=Stuapply.objects.filter(stuname=stuid).exclude(id=uid)
    if exist_approve:
        return JsonResponse({'status': False,'error':"该学生已有通过审核选题，已自动帮您拒绝"})
    Stuapply.objects.filter(id=uid).update(applystate="通过")
    return JsonResponse({'status': True})

def approve(request):
    uid=request.GET.get("uid")
    Stuapply.objects.filter(id=uid).update(applystate="拒绝")

    return JsonResponse({'status': True})

# def title_downloadfile(request):
#     return render(request,"title_downloadfile.html")


""""ajax"""


"""新建选题（ajax请求）"""
@csrf_exempt
def title_add(request):
    form=TitleModelForm(data=request.POST)
    if form.is_valid():
        form.instance.teacher=User.objects.get(id=request.session['info']['id'])
        form.instance.state='待审核'
        form.instance.advice='无'
        form.save()
        return JsonResponse({"status":True,})

    return JsonResponse({"status":False,'error':form.errors})

def delete_title(request):
    uid = request.GET.get("uid")
    print(uid)
    """校验数据是否存在"""
    exists = Title.objects.filter(id=uid,state="待审核" or "拒绝").exists()
    if not exists:
        return JsonResponse({'status': False, 'error': "删除失败，数据不存在或者权限不够。"})
    Title.objects.filter(id=uid).delete()
    return JsonResponse({'status': True})


def title_detail(request):
    uid = request.GET.get("uid")
    row_dict = Title.objects.filter(id=uid).values().first()  # 此时结果直接为字典
    if not row_dict:
        return JsonResponse({'status': False, 'error': "选题不存在。"})

    # 获得的对象无法直接 JSON 序列化返回
    print(row_dict)
    result = {
        'status': True,
        'data': row_dict
    }
    return JsonResponse(result)

@csrf_exempt
def edit_title(request):
    uid = request.GET.get("uid")
    row_object = Title.objects.filter(id=uid,state="待审核" or "拒绝").first()
    if not row_object:
        return JsonResponse({'status': False, 'tips': "编辑选题失败，数据不存在或权限不够,刷新重试。"})
    # 表单验证
    form = TitleModelForm(data=request.POST, instance=row_object)
    if form.is_valid():
        form.instance.state = '待审核'
        form.save()
        return JsonResponse({'status': True})
    return JsonResponse({'status': False, 'error': form.errors})

def table_show(request):
    return  render(request,"title_showtable.html")

def get_pie_data(reqeust):
    waitapprovenum = Title.objects.filter(teacher_id=reqeust.session['info']['id'],state="待审核").count()
    approvenum = Title.objects.filter(teacher_id=reqeust.session['info']['id'],state="通过").count()
    defusenum = Title.objects.filter(teacher_id=reqeust.session['info']['id'],state="拒绝").count()
    db_data = [
        {"value": waitapprovenum, "name": '待审核'},
        {"value": approvenum, "name": '已通过'},
        {"value": defusenum, "name": '拒绝'}
    ]
    result = {
        'status': True,
        'data': db_data
    }
    return JsonResponse(result)

def get_stuapply_pie_data(reqeust):
    title_id=Title.objects.filter(teacher_id=reqeust.session['info']['id']).values("id")
    title_lis=[]    #选题ID列表
    for i in title_id:
        title_lis.append(i['id'])
    waitapprovenum = Stuapply.objects.filter(titlename__in=title_lis,applystate="待审核").count()
    approvenum = Stuapply.objects.filter(titlename__in=title_lis, applystate="通过").count()
    defusenum = Stuapply.objects.filter(titlename__in=title_lis, applystate="拒绝").count()

    db_data = [
        {"value": waitapprovenum, "name": '待审核'},
        {"value": approvenum, "name": '已通过'},
        {"value": defusenum, "name": '拒绝'}
    ]
    result = {
        'status': True,
        'data': db_data
    }
    return JsonResponse(result)


class TitleUpload(forms.ModelForm):
    class Meta:
        model=Title
        fields = ["file"]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['file'].widget.clear_checkbox_label = ''  # 隐藏清除选项的标签文本
    def clean_file(self):
        file_field = self.cleaned_data.get('file')
        if not file_field:
            raise ValidationError("请选择文件后再提交")
        return file_field
#test上传
def upload(request):
    userID = request.session['info']['id']
    data_dict={}            #空字典就是查询所有
    search_data=request.GET.get("q","")
    if search_data:   #如果传过来的search_data不为空
        data_dict["title_name__contains"]=search_data

    title_list=Title.objects.filter(**data_dict,teacher=userID,state="通过")
    page_object=Pagination(request,title_list)

    context={
        "title_list": page_object.page_queryset,
        "search_data": search_data,
        "page_string":page_object.html(),
    }


    return  render(request, "title_upload_list.html", context)

def edit_upload(request,nid):
    title = Title.objects.filter(id=nid).first()
    if request.method == "GET":
        form = TitleUpload(instance=title)
        return render(request, 'title_upload.html', {"form": form})
    form = TitleUpload(data=request.POST, files=request.FILES, instance=title)
    if form.is_valid():
        print(form.cleaned_data)
        form.save()
        return redirect("/title/upload/")
    return render(request, "title_upload.html", {"form": form})



def upload_score_list(request):
    titleID = Title.objects.filter(teacher=request.session['info']['id']).values('id')
    titleID_lis = []  # 选题ID列表
    for i in titleID:
        titleID_lis.append(i['id'])
    download_list = Stuapply.objects.filter(titlename__in=titleID_lis, applystate="通过")
    page_object = Pagination(request, download_list)

    context = {
        "title_list": page_object.page_queryset,
        "page_string": page_object.html(),

    }
    return render(request,"title_upload_score_list.html",context)

class ScoreUpload(forms.ModelForm):
    class Meta:
        model=Stuapply
        fields=["score"]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['score'].widget.clear_checkbox_label = ''  # 隐藏清除选项的标签文本

    def clean_score(self):
        file_field = self.cleaned_data.get('score')
        if not file_field:
            raise ValidationError("请选择文件后再提交")
        return file_field

def upload_score(request,nid):
    apply = Stuapply.objects.filter(id=nid).first()
    if request.method == "GET":
        form = ScoreUpload(instance=apply)
        return render(request, 'title_upload.html',{"form": form})
    form = ScoreUpload(data=request.POST, files=request.FILES, instance=apply)
    if form.is_valid():
        print(form.cleaned_data)
        form.save()
        return redirect("/title/uploadscore/")
    return render(request, "title_upload.html", {"form": form})


def downloadpage(request):
    titleID=Title.objects.filter(teacher=request.session['info']['id']).values('id')
    titleID_lis = []  # 选题ID列表
    for i in titleID:
        titleID_lis.append(i['id'])
    download_list=Stuapply.objects.filter(titlename__in=titleID_lis, applystate="通过")
    page_object=Pagination(request,download_list)


    context={
        "title_list": page_object.page_queryset,
        "page_string": page_object.html(),

    }
    return render(request,"title_downloadfile.html",context)

def article_translation_downloadpage(request):
    titleID=Title.objects.filter(teacher=request.session['info']['id']).values('id')
    titleID_lis = []  # 选题ID列表
    for i in titleID:
        titleID_lis.append(i['id'])
    download_list=Stuapply.objects.filter(titlename__in=titleID_lis, applystate="通过")
    page_object=Pagination(request,download_list)

    context={
        "title_list": page_object.page_queryset,
        "page_string": page_object.html(),

    }


    return render(request,"title_download_articletranslation.html",context)

def medium_check_downloadpage(request):
    titleID=Title.objects.filter(teacher=request.session['info']['id']).values('id')
    titleID_lis = []  # 选题ID列表
    for i in titleID:
        titleID_lis.append(i['id'])
    download_list=Stuapply.objects.filter(titlename__in=titleID_lis, applystate="通过")

    page_object=Pagination(request,download_list)

    context={
        "title_list": page_object.page_queryset,
        "page_string": page_object.html(),

    }

    return render(request,"title_download_mediumcheck.html",context)


def final_paper_downloadpage(request):
    titleID=Title.objects.filter(teacher=request.session['info']['id']).values('id')
    titleID_lis = []  # 选题ID列表
    for i in titleID:
        titleID_lis.append(i['id'])
    download_list=Stuapply.objects.filter(titlename__in=titleID_lis, applystate="通过")

    page_object=Pagination(request,download_list)

    context={
        "title_list": page_object.page_queryset,
        "page_string": page_object.html(),

    }


    return render(request,"title_download_finalpaper.html",context)




class UserMyInfoModelForm(BootStrapModelForm):
    tele = forms.CharField(
        label='手机号',
        validators=[RegexValidator(r'^1[3-9]\d{9}$', '手机格式错误')],
    )
    class Meta:
        model=User
        fields=["name","age","email","tele"]
        # widgets={
        #     "name":forms.TextInput(attrs={'style': 'width: 200px;'})
        # }

def my_information(request,nid):
    row_object=User.objects.filter(id=nid).first()
    title="我的信息"
    if request.method == "GET":
        form=UserMyInfoModelForm(instance=row_object)
        return render(request,'title_change.html',{"form":form,"pagetitle":title})
    form=UserMyInfoModelForm(data=request.POST,instance=row_object)
    if form.is_valid():
        form.save()
        return redirect('/title/tableshow/')
    return render(request,'title_change.html',{'form':form,'pagetitle':title})

class UserChangePasswordModelForm(BootStrapModelForm):
    password_now=forms.CharField(
        label="当前密码",
        widget=forms.PasswordInput(render_value=False)
    )
    confirm_password = forms.CharField(
            label="确认密码",
            widget=forms.PasswordInput(render_value=True)
        )
    class Meta:
        model=User
        fields=['password_now','password','confirm_password']
        widgets = {
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
    def clean_password_now(self):
        pwd = self.cleaned_data.get('password_now')
        md5_pwd = md5(pwd)
        # 去数据库校验当前密码和新输入的密码是否一致
        exists = User.objects.filter(id=self.instance.pk, password=md5_pwd).exists()
        if not exists:
            raise ValidationError('密码错误')

def change_password(request,nid):
    row_object = User.objects.filter(id=nid).first()
    title = "修改密码"
    if request.method == "GET":
        form = UserChangePasswordModelForm()
        return render(request, 'title_change.html', {"form": form, "pagetitle": title})
    form = UserChangePasswordModelForm(data=request.POST, instance=row_object)
    if form.is_valid():
        form.save()
        return redirect('/title/tableshow/')
    return render(request, 'title_change.html', {'form': form, 'pagetitle': title})

