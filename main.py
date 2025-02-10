import streamlit as st
from page.page import Page
from page.mllm_task import mllm_test
from page.mllm_task_detail import mllm_test_detail
from page.mllm_test_compare import mllm_test_compare
from page.doc_parse import doc_parse
from page.doc_parse_compare import doc_parse_compare
from page.doc_parse_data_detail import doc_parse_data_detail


class MultiApp:
    """ 整个平台的主页面，所有子页面需要按照它的标准进行初始化. 每个子页面对象都要集成page.page中的Page父类
    Usage:
        app = MultiApp()
        app.add_xiaoguo_app("项目管理", project)
        app.run()
    """

    def __init__(self):
        self.apps = []
        self.extra_apps = []
        self.buttons_status = []

    def add_xiaoguo_app(self, title, page):
        """ 这里定义的页面会显示在侧边导航栏
        Parameters
        ----------
        page:
            页面对象，该对象需要继承page.page中的Page父类
        title:
            显示在侧边导航栏的名字
        """
        self.apps.append({
            "title": title,
            "page": page,
        })

    def add_extra_app(self, page):
        """ 这里定义的页面不会显示在侧边导航栏
        Parameters
        ----------
        page:
            页面对象， 该页面不会显示在侧边导航栏
        """
        self.extra_apps.append({
            "page": page,
        })

    def run(self):
        """
        负责主页面显示的函数，主要通过以下步骤：
        1. 定义侧边导航栏架构。
        2. 获取当前url中是否已经设定了page参数，如果有page参数则并遍历已注册的所有页面对象并导航到对应的页面那种， 如果没有则直接显示默认首页
        """

        # ratio的回调函数, 负责设置url并导航到对应子页面
        def change_route():
            app = st.session_state['app_key']  # 获取当前被选中的页面
            app['page'].refresh_route()  # 要重置一下url中的参数

        # 获取当前URL中是否已经带了page参数， page参数决定了应该显示哪个子页面.
        route = st.query_params.get('page')
        default_page = 0
        if route:
            for a in self.apps:
                pa: Page = a['page']
                print(pa.get_route())
                if route == pa.get_route():
                    default_page = self.apps.index(a)

        # step 1: 定义侧边导航栏架构
        st.sidebar.title("任务导航")
        with st.sidebar.expander("效果测试管理", expanded=True):
            app = st.radio(
                '',
                self.apps,
                format_func=lambda app: app['title'],
                on_change=change_route,
                key="app_key",
                index=default_page,
            )
        url = 'http://localhost:8501/'
        st.markdown(f'<a href="{url}" target="_self">{"返回首页"}</a>', unsafe_allow_html=True)
        if route:
            for a in self.apps:
                pa: Page = a['page']
                if route == pa.get_route():
                    pa.write()
            for a in self.extra_apps:
                pa: Page = a['page']
                if route == pa.get_route():
                    pa.write()
        else:
            app['page'].refresh_route()
            app['page'].write()


st.set_page_config(layout='wide')
app = MultiApp()
# 开始注册效果测试侧边栏
app.add_xiaoguo_app("多模态", mllm_test)
app.add_xiaoguo_app("文档解析", doc_parse)
# app.add_extra_app(doc_split_detail)


app.add_extra_app(mllm_test_detail)
app.add_extra_app(mllm_test_compare)
app.add_extra_app(doc_parse_compare)
app.add_extra_app(doc_parse_data_detail)
app.run()



# def write1():
#     st.write(111)
# def write2():
#     st.write(222)
# def write3():
#     st.write(333)
#
# click1 = st.button('click1')
# click2 = st.button('click2')
# click3 = st.button('click3')
# if click1:
#     write1()
# if click2:
#     write2()
# if click3:
#     write3()



