import time
import pymysql
from page.page import Page
import streamlit as st
import pandas as pd
import os
from multiprocessing import Process
import base64
from zhipuai import ZhipuAI
from page.db import DocParseTask as DBDocParseTask, get_db_connection
from page.doc_parse_compare import doc_parse_compare
import json
import time
from alibabacloud_tea_openapi.models import Config
from alibabacloud_searchplat20240529.client import Client
from alibabacloud_searchplat20240529.models import (
    CreateDocumentAnalyzeTaskRequestDocument,
    CreateDocumentAnalyzeTaskRequestOutput,
    CreateDocumentAnalyzeTaskRequest,
    CreateDocumentAnalyzeTaskResponse,
    GetDocumentAnalyzeTaskStatusRequest,
    GetDocumentAnalyzeTaskStatusResponse
)
import re


def get_project_root():
    current_file_path = os.path.abspath(__file__)
    project_root = os.path.dirname(os.path.dirname(current_file_path))
    return project_root


def update_data(task_id, status='成功'):
    conn = pymysql.connect(
        host='9.134.12.32',
        # port=3861,
        user='root',
        password='1qaz9ol.',
        database='ai_tester',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor


    )
    with conn.cursor() as connection:
        sql = f"UPDATE doc_parse SET `status` = '{status}'  WHERE id = {task_id}"
        print(sql)
        result = connection.execute(sql)
        conn.commit()

# 将Markdown中的图片替换为占位符
def replace_ali_images_with_placeholder(md_content):
    # 使用正则表达式匹配Markdown图片语法并替换为占位符
    pattern = r'!\[IMAGE](.*)'
    # 使用正则表达式查找所有匹配的图片链接
    matches = re.findall(pattern, md_content)
    updated_content = re.sub(pattern, '[image]', md_content)
    pattern = r'!\[](.*)'
    updated_content = re.sub(pattern, '[image]', updated_content)
    return updated_content


def compare_text_similarity(text1, text2):
    import Levenshtein
    text1 = replace_ali_images_with_placeholder(text1)
    text2 = replace_ali_images_with_placeholder(text2)

    return round(1 - float(Levenshtein.distance(text1, text2)) / max(len(text1), len(text2)), 3)


def call_doc_parse(local_file_path):
    config = Config(bearer_token="OS-g1h6d9g3s948p1nu1",
                    # endpoint: 配置统一的请求入口 需要去掉http://
                    endpoint="default-dm5.platform-cn-shanghai.opensearch.aliyuncs.com",
                    # 支持 protocol 配置 HTTPS/HTTP
                    protocol="http"
                    )
    client = Client(config=config)
    # 本地模式，需要额外指定file_name
    document = CreateDocumentAnalyzeTaskRequestDocument(
        content=base64.b64encode(open(local_file_path, 'rb').read()).decode(),
        file_name=os.path.basename(local_file_path)
    )

    output = CreateDocumentAnalyzeTaskRequestOutput(image_storage="url")
    request = CreateDocumentAnalyzeTaskRequest(document=document, output=output)
    # default：替换工作空间名称, ops-document-analyze-001: 服务id
    response: CreateDocumentAnalyzeTaskResponse = client.create_document_analyze_task(
        "default", "ops-document-analyze-001", request)
    task_id = response.body.result.task_id
    # print("task_id: " + task_id)
    request = GetDocumentAnalyzeTaskStatusRequest(task_id=task_id)
    while True:
        response: GetDocumentAnalyzeTaskStatusResponse = client.get_document_analyze_task_status(
            "default", "ops-document-analyze-001", request)
        status = response.body.result.status
        print("status: " + status)
        if status == "PENDING":
            time.sleep(5)
        elif status == "SUCCESS":
            data = response.body.result.data
            print(response.body)
            print("content:\n" + data.content[:20] + "\n")
            return data.content
        else:
            print(response.body.result)
            break

def call_model(task_id, output_path):
    data_dict = {'static/doc/财报.pdf':"static/doc/财报.pdf.md"}

    df = pd.DataFrame(
        columns=['file_name', 'similarity', 'model_parse_md_file_path', 'anno_parse_md_file_path'])

    for local_file_path, anno_file_path in data_dict.items():
        content = call_doc_parse(local_file_path)
        with open(output_path+'.md', 'w') as f:
            f.write(content)
        with open(anno_file_path, 'r') as f:
            anno_content = f.read()
        similarity = compare_text_similarity(anno_content, content)
        result = {
            'file_name': os.path.basename(local_file_path),
            'similarity': similarity,
            'model_parse_md_file_path': output_path+'.md',
            'anno_parse_md_file_path': anno_file_path
        }
        df.loc[len(df)] = result

    df.to_csv(output_path, index=False)
    update_data(task_id, status='Success')


def call_doc_parse_task(task_id, task_path):
    call_model(task_id, task_path)


class DocParse(Page):
    def write(self):

        conn = get_db_connection()
        db_doc_parse_task = DBDocParseTask(conn)
        df = db_doc_parse_task.get_tasks()

        # df['link'] = f'http://localhost:8501/?page=mllm_test_detail&task_id='

        df['id_str'] = df['id'].astype(str)
        df['link'] = df['id_str'].apply(lambda x: f"http://localhost:8501/?page=doc_parse_compare&task_id={x}")
        df = df.drop('id_str', axis=1)
        df['是否参与对比'] = False

        def on_click():
            task_name = st.session_state['task_name']
            output_path = f'static/doc_parse/{task_name}.csv'
            task_id = db_doc_parse_task.add_task(task_name, status='running', output_path=output_path)
            process_mllm = Process(target=call_doc_parse_task, args=(task_id, output_path))
            process_mllm.start()

        with st.popover("创建文档解析测试任务"):
            with st.form(key='doc_parse_task'):
                st.text_input('任务名称', key='task_name')
                st.form_submit_button("提交", on_click=on_click)

        st.data_editor(df, use_container_width=True, hide_index=True,
                     column_config={
                         'link': st.column_config.LinkColumn(display_text='任务详情'),
                         '是否参与对比': st.column_config.CheckboxColumn()
                     },key='doc_parse_task_df'
                     )

        compare_button = st.button('生成对比报告')

        if compare_button:
            edit_df = st.session_state['doc_parse_task_df']['edited_rows']
            # st.write(st.session_state['mllm_task'])
            ids = []
            for key, value in edit_df.items():
                ids.append(df.loc[int(key)]['id'])
            st.query_params.tasks = ids
            doc_parse_compare.route()








doc_parse = DocParse('doc_parse')
