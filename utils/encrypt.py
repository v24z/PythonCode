# -*-codeing = utf-8 -*-
#@Time:2023 05 15
#@Author:Qu Linyi
#@File:encrypt.py
#@Software: PyCharm

import hashlib
from django.conf import settings#直接用django中随机生成的秘钥，不在自己写盐
def md5(data_string):
    # 盐换成django自生成的密钥
    obj=hashlib.md5(settings.SECRET_KEY.encode('utf-8'))
    obj.update(data_string.encode('utf-8'))
    return obj.hexdigest()