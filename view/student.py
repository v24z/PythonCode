# -*-codeing = utf-8 -*-
#@Time:2023 05 09
#@Author:Qu Linyi
#@File:student.py
#@Software: PyCharm

from django.shortcuts import render,redirect
from app01.models import User,Title,Stuapply,Uploadtime
from django import forms
from app01.utils.encrypt import md5
from datetime import date

from app01.utils.pagination import Pagination
from app01.utils.bootstrap import BootStrapModelForm
from django.core.exceptions import ValidationError

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse


class TitleModelForm(forms.ModelForm):
    title_name=forms.CharField(min_length=5,label="选题名称")
    class Meta:
        model=Title
        fields=["title_name","title_quality",
                "fit_major","work_time","work_difficulty",
                "title_source","title_introduce",
                "paper_requirement"]
        # widgets={
        #     "title_name":forms.TextInput(attrs={"class":"form-control"})·
        # }
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        #循环找到所有的插件，添加类名
        for name, field in self.fields.items():
            field.widget.attrs={'class':'form-control','placeholder':field.label,"disabled":"disabled"}


def title_list(request):
    stuID = 2      #后期集中用session中传过来的ID替换
    """"选题表"""
    data_dict = {}  # 空字典就是查询所有
    search_data = request.GET.get("q", "")
    if search_data:  # 如果传过来的search_data不为空
        data_dict["title_name__contains"] = search_data

    title_list=Title.objects.filter(**data_dict,state="通过")

    page_object = Pagination(request, title_list)
    form = TitleModelForm()

    context = {
        "title_list": page_object.page_queryset,
        "search_data": search_data,
        "page_string": page_object.html(),
        "form": form
    }


    return render(request,"stu_titleList.html",context)



#查看选题详情
def cheack_title(request,nid):
    row_object = Title.objects.filter(id=nid).first()
    if request.method == "GET":
        form = TitleModelForm(instance=row_object)  # 加上instance 即可在表单中显示数据库中的数据
        return render(request,"stu_cheacktitle.html",{"form":form})
def title_apply(request,nid):

    #stuId=Title.objects.filter(id=nid).first().id       #申请的学生id，后期用session中id替换

    """"判断是否重复申请语句待完成"""
    exist=Stuapply.objects.filter(titlename_id=nid,stuname_id=2).exists()
    if not exist:           # 该选题的申请记录不存在，则添加申请
        Stuapply.objects.create(titlename_id=nid,stuname_id=2)
        return redirect("/stu/titlelist/")
    return redirect("/stu/titlelist/")

def my_apply(request):
    stuid=request.session['info']['id']           #后期替换成session中的id
    my_apply=Stuapply.objects.filter(stuname_id=stuid).all()
    return render(request,"stu_myapply.html",{"my_apply":my_apply})



def downloadpage(request):
    title_list=Stuapply.objects.filter(stuname=request.session['info']['id'],applystate="通过")
    return render(request,"stu_downloadfile.html",{"title_list":title_list})

def download_score_page(request):
    title_list=Stuapply.objects.filter(stuname=request.session['info']['id'],applystate="通过")
    return render(request,"stu_download_score.html",{"title_list":title_list})


def uploadfile(request):
    current_date = date.today()
    queryset = Uploadtime.objects.filter(id=1, start_time__lte=current_date, end_time__gte=current_date)
    if queryset:
        title_list=Stuapply.objects.filter(stuname=request.session['info']['id'],applystate="通过")
        return render(request, "stu_upload_list.html",{"title_list":title_list})
    return redirect("/stu/titlelist/")




def article_translation_upload_page(request):
    current_date = date.today()
    queryset = Uploadtime.objects.filter(id=2, start_time__lte=current_date, end_time__gte=current_date)
    if queryset:

        title_list=Stuapply.objects.filter(stuname=request.session['info']['id'],applystate="通过")
        return render(request, "stu_upload_articletranslation_list.html",{"title_list":title_list})
    return redirect("/stu/titlelist/")



def medium_check_upload_page(request):
    current_date = date.today()
    queryset = Uploadtime.objects.filter(id=3, start_time__lte=current_date, end_time__gte=current_date)
    if queryset:
        title_list=Stuapply.objects.filter(stuname=request.session['info']['id'],applystate="通过")
        return render(request, "stu_upload_mediumcheck_list.html",{"title_list":title_list})
    return redirect("/stu/titlelist/")


def final_paper_upload_page(request):
    current_date = date.today()
    queryset = Uploadtime.objects.filter(id=4, start_time__lte=current_date, end_time__gte=current_date)
    if queryset:

        title_list=Stuapply.objects.filter(stuname=request.session['info']['id'],applystate="通过")
        return render(request, "stu_upload_finalpaper_list.html",{"title_list":title_list})
    return redirect("/stu/titlelist/")



class StuApplypload(forms.ModelForm):
    class Meta:
        model=Stuapply
        fields=["stufile"]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['stufile'].widget.clear_checkbox_label = ''  # 隐藏清除选项的标签文本
    def clean_stufile(self):
        file_field = self.cleaned_data.get('stufile')
        if not file_field:
            raise ValidationError("请选择文件后再提交")
        return file_field

def edit_upload(request, nid):
    apply=Stuapply.objects.filter(id=nid).first()
    if request.method == "GET":
        form =StuApplypload(instance=apply)
        return render(request, 'stu_upload.html', {"form": form})
    form = StuApplypload(data=request.POST, files=request.FILES, instance=apply)
    if form.is_valid():
        print(form.cleaned_data)
        form.save()
        return redirect("/stu/upload/")
    return render(request, "stu_upload.html", {"form": form})


class ArticleTranslationUpload(forms.ModelForm):
    class Meta:
        model=Stuapply
        fields=["articletranslationfile"]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['articletranslationfile'].widget.clear_checkbox_label = ''  # 隐藏清除选项的标签文本
    def clean_stufile(self):
        file_field = self.cleaned_data.get('articletranslationfile')
        if not file_field:
            raise ValidationError("请选择文件后再提交")
        return file_field


def article_translation_upload(request, nid):
    apply=Stuapply.objects.filter(id=nid).first()
    if request.method == "GET":
        form =ArticleTranslationUpload(instance=apply)
        return render(request, 'stu_upload.html', {"form": form})
    form = ArticleTranslationUpload(data=request.POST, files=request.FILES, instance=apply)
    if form.is_valid():
        print(form.cleaned_data)
        form.save()
        return redirect("/stu/uploadarticletranslation/")

class MediumCheckUpload(forms.ModelForm):
    class Meta:
        model=Stuapply
        fields=["mediumcheck"]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['mediumcheck'].widget.clear_checkbox_label = ''  # 隐藏清除选项的标签文本
    def clean_stufile(self):
        file_field = self.cleaned_data.get('mediumcheck')
        if not file_field:
            raise ValidationError("请选择文件后再提交")
        return file_field

def medium_check_upload(request, nid):
    apply=Stuapply.objects.filter(id=nid).first()
    if request.method == "GET":
        form =MediumCheckUpload(instance=apply)
        return render(request, 'stu_upload.html', {"form": form})
    form = MediumCheckUpload(data=request.POST, files=request.FILES, instance=apply)
    if form.is_valid():
        print(form.cleaned_data)
        form.save()
        return redirect("/stu/uploadmediumcheck/")
    return render(request, "stu_upload.html", {"form": form})


class FinalPaperUpload(forms.ModelForm):
    class Meta:
        model=Stuapply
        fields=["finalpaper"]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['finalpaper'].widget.clear_checkbox_label = ''  # 隐藏清除选项的标签文本
    def clean_stufile(self):
        file_field = self.cleaned_data.get('finalpaper')
        if not file_field:
            raise ValidationError("请选择文件后再提交")
        return file_field

def final_paper_upload(request, nid):
    apply=Stuapply.objects.filter(id=nid).first()
    if request.method == "GET":
        form =FinalPaperUpload(instance=apply)
        return render(request, 'stu_upload.html', {"form": form})
    form = FinalPaperUpload(data=request.POST, files=request.FILES, instance=apply)
    if form.is_valid():
        print(form.cleaned_data)
        form.save()
        return redirect("/stu/uploadfinalpaper/")


""""ajax"""

""""查看选题申请后的申请"""
def apply_title(request):
    userID=request.session['info']['id']        #后面用session中ID替换
    uid=request.GET.get("uid")
    exists = Title.objects.filter(id=uid).exists()
    if not exists:
        return JsonResponse({'status': False, 'error': "申请失败，数据不存在。"})

    apply_exist=Stuapply.objects.filter(titlename=uid,stuname=userID)   #是否申请过该选题

    if apply_exist: #重复申请
        return JsonResponse({'status': False, 'error': "已申请过该选题，请勿重复申请。"})

    Stuapply.objects.create(titlename_id=uid, stuname_id=userID)
    return JsonResponse({'status': True})




from django.core.validators import RegexValidator

class UserMyInfoModelForm(BootStrapModelForm):
    tele = forms.CharField(
        label='手机号',
        validators=[RegexValidator(r'^1[3-9]\d{9}$', '手机格式错误')],
    )
    class Meta:
        model=User
        fields=["name","age","email","tele"]

def my_information(request,nid):
    row_object=User.objects.filter(id=nid).first()
    title="我的信息"
    if request.method == "GET":
        form=UserMyInfoModelForm(instance=row_object)
        return render(request,'stu_change.html',{"form":form,"pagetitle":title})
    form=UserMyInfoModelForm(data=request.POST,instance=row_object)
    if form.is_valid():
        form.save()
        return redirect('/stu/titlelist/')
    return render(request,'stu_change.html',{'form':form,'pagetitle':title})

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
        return render(request, 'stu_change.html', {"form": form, "pagetitle": title})
    form = UserChangePasswordModelForm(data=request.POST, instance=row_object)
    if form.is_valid():
        form.save()
        return redirect('/stu/titlelist/')
    return render(request, 'stu_change.html', {'form': form, 'pagetitle': title})
