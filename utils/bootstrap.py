# -*-codeing = utf-8 -*-
#@Time:2023 05 10
#@Author:Qu Linyi
#@File:bootstrap.py
#@Software: PyCharm

from django import forms

class BootStrap:
    bootstrap_exclude_fields=[]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 循环ModelForm中的所有字段，给每个字段的插件设置
        for name, field in self.fields.items():
            # 字段中有属性，保留原来的属性，没有属性，才增加。
            if name in self.bootstrap_exclude_fields:
                continue
            if field.widget.attrs:
                field.widget.attrs["class"] = "form-control"
                field.widget.attrs["placeholder"] = field.label
            else:
                field.widget.attrs = {
                    "class": "form-control",
                    "placeholder": field.label
                }




class BootStrapModelForm(BootStrap,forms.ModelForm):
    pass
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     # 循环ModelForm中的所有字段，给每个字段的插件设置
    #     for name, field in self.fields.items():
    #         # 字段中有属性，保留原来的属性，没有属性，才增加。
    #         if field.widget.attrs:
    #             field.widget.attrs["class"] = "form-control"
    #             field.widget.attrs["placeholder"] = field.label
    #         else:
    #             field.widget.attrs = {
    #                 "class": "form-control",
    #                 "placeholder": field.label
    #             }


class BootStrapForm(BootStrap,forms.Form):
    pass
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     # 循环ModelForm中的所有字段，给每个字段的插件设置
    #     for name, field in self.fields.items():
    #         # 字段中有属性，保留原来的属性，没有属性，才增加。
    #         if field.widget.attrs:
    #             field.widget.attrs["class"] = "form-control"
    #             field.widget.attrs["placeholder"] = field.label
    #         else:
    #             field.widget.attrs = {
    #                 "class": "form-control",
    #                 "placeholder": field.label
    #             }