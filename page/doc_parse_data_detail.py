import streamlit as st
from page.page import Page
from page.db import DocParseTask, get_db_connection
import pandas as pd
import json
import os
from streamlit_extras.grid import grid
from pathlib import Path
import re


def read_txt_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.readlines()


def get_anno(task):
    with open(task['anno_path'], 'r', encoding='utf-8') as f:
        # 遍历字典，找到包含搜索值的键
        anno_json = json.load(f)
        for key, value in anno_json.items():
            if os.path.basename(st.query_params['file_path']) in key:
                return value


def find_parse_directories(base_dir):
    return [d for d in Path(base_dir).iterdir() if d.is_dir()]


def get_files_with_extension(directory, extension):
    return [f for f in os.listdir(directory) if f.endswith(extension)]


def read_file(file_path):
    # content = ''
    # with open(file_path, 'r') as f:
    #     content = f.read()
    with open(file_path, 'r', encoding='utf-8') as source_file:
        lines = source_file.readlines()

    # lines_with_newline = [line + '\n' for line in lines]


    return ''.join(lines)


class DocParseDataDetail(Page):

    def write(self):
        def hold_page():
            st.query_params['page'] = 'doc_parse_data_detail'
            st.query_params['task_id'] = task_id
            st.query_params['file_name'] = file_name

        # 从数据中查询任务信息
        task_id = st.query_params['task_id']  # 从url中获取测试任务的id
        file_name = st.query_params['file_name']  # 从url中获取文件的路径
        conn = get_db_connection()
        db_task = DocParseTask(conn)
        task = db_task.get_task(task_id).iloc[0]

        task_result_df = pd.read_csv(task['output_path'])
        output_file_path = task_result_df.loc[
            task_result_df['file_name'] == file_name, ['model_parse_md_file_path', 'anno_parse_md_file_path']]
        model_parse_md_file_path = output_file_path.iloc[0]['model_parse_md_file_path']
        anno_parse_md_file_path = output_file_path.iloc[0]['anno_parse_md_file_path']


        st.caption(file_name)
        anno_content = read_file(anno_parse_md_file_path)
        model_content = read_file(model_parse_md_file_path)
        with st.expander("模型结果原文"):
            st.text_area('', model_content,height=1000, on_change=hold_page)
        with st.expander("标注文件原文"):
            st.text_area('', anno_content,height=1000, on_change=hold_page, key='anno_content')
            def update_anno():
                hold_page()
                anno_content = st.session_state['anno_content']
                # st.write(anno_content)
                with open(anno_parse_md_file_path, 'w') as f:
                    f.write(anno_content)
                st.success("标注修改成功")
            st.button('修改标注', on_click=update_anno)

        # st.button('仅显示不同点')



        model_content = model_content.replace("begin{align*}", "begin{aligned}")
        model_content = model_content.replace("end{align*}", "end{aligned}")
        st.subheader('markdown渲染结果对比')
        col1, col2 = st.columns(2)
        with col1:
            with st.container(border=True):
                st.caption('模型结果')
                st.markdown("""
<style>
.markdown-table {
    width: 1000px;  /* 设置你想要的宽度 */
    margin: 0 auto;  /* 居中显示 */
}
</style>
<div class="markdown-table">

%s

</div>
""" % model_content, unsafe_allow_html=True)
        with col2:
            with st.container(border=True):
                st.caption('预期结果')
                st.markdown(anno_content)


doc_parse_data_detail = DocParseDataDetail('doc_parse_data_detail')
