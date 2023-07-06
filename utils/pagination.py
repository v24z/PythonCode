# -*-codeing = utf-8 -*-
#@Time:2023 05 09
#@Author:Qu Linyi
#@File:pagination.py
#@Software: PyCharm

from django.utils.safestring import mark_safe
class Pagination(object):
    def __init__(self,request,queryset,page_size=10,page_param='page',plus = 5):
        """
        :param request:     请求的对象
        :param queryset:    符合条件的数据（根据这个数据进行分页处理）
        :param page_size:   每页显示多少数据
        :param page_param:  在URL中传递的获取分页的参数 例如： /pretty/list/?page=12
        :param plus:        显示当前页的 前或后几页（根据页码）
        """

        import copy
        from django.http.request import QueryDict
        query_dict = copy.deepcopy(request.GET)
        query_dict._mutable = True
        self.query_dict=query_dict

        self.page_parm=page_param


        page = request.GET.get('page', "1")
        # 判断是否是十进制的数
        if page.isdecimal():
            page=int(page)
        else:
            page=1
        self.page=page
        self.page_size=page_size
        # 1 根据用户想要访问的页码，计算出起止位置
        self.start = (page - 1) * page_size
        self.end = page * page_size
        self.page_queryset=queryset[self.start: self.end]

        total_count = queryset.count()

        # 数据总条数
        # divmod(num1,num2) 结果 （商，余数）
        total_page_count, div = divmod(total_count, page_size)
        if div:
            total_page_count += 1
        self.total_page_count=total_page_count
        self.plus=plus

    def html(self):
        # 计算出，显示当前页的 前5页、后5页
        # start_page=0
        # end_page=0

        if self.total_page_count <= 2 * self.plus + 1:
            # 数据库数据比较少，没有达到11页
            start_page = 1
            end_page = self.total_page_count
        else:
            # 数据库数据比较多，大于11页
            # 当前页<5时
            if self.page <= self.plus:
                start_page = 1
                end_page = 2 * self.plus + 1
            else:
                # 当前页大于5
                """
                直接在stat = page - plus if page - plus>=1 else 1
                start_page = page - plus if page - plus > 0 else 1
                end_page = start_page + plus * 2 if start_page + plus * 2 < total_page else total_page
                """
                if (self.page + self.plus) > self.total_page_count:
                    start_page = self.total_page_count - 2 * self.plus
                    end_page = self.total_page_count
                else:
                    start_page = self.page - self.plus
                    end_page = self.page + self.plus

        # 页码
        page_str_list = []
        # 首页

        self.query_dict.setlist(self.page_parm, [1])
        # print(self.query_dict.urlencode())
        page_str_list.append('<li class="active"><a href="?{}">首页</a></li>'.format(self.query_dict.urlencode()))

        # 上一页
        if self.page > 1:
            self.query_dict.setlist(self.page_parm, [self.page - 1])
            prev = '<li class="active"><a href="?{}">上一页</a></li>'.format(self.query_dict.urlencode())
            page_str_list.append(prev)
        else:
            self.query_dict.setlist(self.page_parm, [1])
            prev = '<li class="active"><a href="?{}">上一页</a></li>'.format(self.query_dict.urlencode())
            page_str_list.append(prev)

        # 分页页面
        # for i in range(1,total_page_count+1):
        for i in range(start_page, end_page + 1):
            self.query_dict.setlist(self.page_parm, [i])
            if i == self.page:
                ele = '<li class="active"><a href="?{}">{}</a></li>'.format(self.query_dict.urlencode(), i)
            else:
                ele = '<li><a href="?{}">{}</a></li>'.format(self.query_dict.urlencode(), i)
            page_str_list.append(ele)

        # 下一页
        if self.page < self.total_page_count:
            self.query_dict.setlist(self.page_parm, [self.page + 1])
            prev = '<li class="active"><a href="?{}">下一页</a></li>'.format(self.query_dict.urlencode())
            page_str_list.append(prev)
        else:
            self.query_dict.setlist(self.page_parm, [self.total_page_count])
            prev = '<li class="active"><a href="?{}">下一页</a></li>'.format(self.query_dict.urlencode())
            page_str_list.append(prev)
        # 尾页
        self.query_dict.setlist(self.page_parm, [self.total_page_count])
        page_str_list.append('<li class="active"><a href="?{}">尾页</a></li>'.format(self.query_dict.urlencode()))


        page_string = mark_safe(''.join(page_str_list))
        """
            <li><a href="?page=2">2</a></li>
            <li><a href="?page=3">3</a></li> 
        """
        return page_string