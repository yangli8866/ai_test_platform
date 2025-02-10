import time
import pymysql
from page.page import Page
import streamlit as st
import pandas as pd
import os
from multiprocessing import Process
import base64
from zhipuai import ZhipuAI
from page.db import MLLMTask as DBMLLMTask, get_db_connection
from page.mllm_test_compare import mllm_test_compare
import json

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
        sql = f"UPDATE mllm SET `status` = '{status}'  WHERE id = {task_id}"
        print(sql)
        result = connection.execute(sql)
        conn.commit()


# def call_qwen(question, anwser, ground_truth):
#     from dashscope import MultiModalConversation
#     prompt = """
#     你是一位阅读理解评分老师。针对question，分析answer和ground_truth，陈述的内容和观点是一致的吗？如果是一致的，请返回1；如果不一致，请返回0。并输出原因。
#     注意：
#     -如果answer和ground_truth里有数值内容，必须保证严格相等。
#     -如果answer和ground_truth有一些关键实体名称，要保证名称要完全一致，不要错字漏字。
#     -注意在判断时，需要结合question的内容来综合判断。
#     -如果回答正确，则输出1，回答错误输出0
#     可以参考以下示例：
#     【examples】1:
#     {
#         "question": "你今天心情怎么样",
#         "answer": "我今天很开心",
#         "ground_truth": 我今天心情不错,
#         "verification": {
#             "result" : 1,
#             "result" : "两边回答的心情是一样的"
#         }
#     }
#
#     【examples】2:
#     {
#         "question": "1+1等于几",
#         "answer": "3",
#         "ground_truth": "2",
#         "verification": {
#             "result" : 0,
#             "result" : "两边的数值计算不一样"
#         }
#     }
#
#     下面是真正的问题：
#     {
#         "question": "%s",
#         "answer": "%s",
#         "ground_truth": "%s",
#     }
#
#     请按以下格式进行输出：
# {
#         "result": 0,
#         "reason": "两者核心观点不一致"
# }
#
#     """ % (question, anwser, ground_truth)
#
#     messages = [
#         {
#             "role": "user",
#             "content": [
#                 {
#                     "text": prompt
#                 }
#             ]
#         }
#     ]
#
#     response = MultiModalConversation.call(model='qwen-vl-max',
#                                            messages=messages,
#                                            api_key='sk-34f385226c2f491fb0c41692dd899e57')
#     text = response.output.choices[0].message.content[0]['text'].strip('```')
#     print(text)
#     print("11111\n")
#     verification = json.loads(text)
#     print(verification)
#     result = verification['result']
#     reason = verification['reason']
#
#     return result, reason

def cal_qwen(question, answer, ground_truth):
    from dashscope import MultiModalConversation

    prompt = """
    你是一位阅读理解评分老师。针对question，分析answer和ground_truth，陈述的内容和观点是一致的吗？如果是一致的，请返回正确；如果不一致，请返回错误。并输出原因。 
    
    【注意】：
    -如果answer和ground_truth里有数值内容，必须保证严格相等。
    -如果answer和ground_truth有一些关键实体名称，要保证名称要完全一致，不要错字漏字。
    -注意在判断时，需要结合question的内容来综合判断。
    -如果回答正确，则输出1，回答错误输出0
    可以参考以下示例：
    【examples】1:
    {
        "question": "你今天心情怎么样",
        "answer": "我今天很开心",
        "ground_truth": 我今天心情不错,
        "verification": {
            "result" : "正确",
            "result" : "两边回答的心情是一样的"
        }
    }

    【examples】2:
    {
        "question": "1+1等于几",
        "answer": "3",
        "ground_truth": "2",
        "verification": {
            "result" : "错误",
            "result" : "两边的数值计算不一样"
        }
    }

    下面是真正的问题：
    {
        "question": "%s",
        "answer": "%s",
        "ground_truth": "%s",
    }

    请严格按以下格式进行输出：
    {
            "result": "错误",
            "reason": "这里是详细的错误原因"
    }

    """ % (question, answer, ground_truth)

    messages = [
        {
            "role": "user",
            "content": [
                {
                    "text": prompt
                }
            ]
        }
    ]

    response = MultiModalConversation.call(model='qwen-vl-max',
                                           messages=messages,
                                           api_key='sk-34f385226c2f491fb0c41692dd899e57')

    print(response.output.choices[0].message.content[0]['text'])
    result = json.loads(response.output.choices[0].message.content[0]['text'])
    return result

def call_model(task_id, output_path):
    df = pd.read_excel('static/data/pic/mllm_anno.xlsx')
    df['模型答案'] = ''

    for index, row in df.iterrows():
        prefix = 'static/data/pic/'
        image_path = os.path.join(prefix, row['图片'])
        questions = row['问题']

        with open(image_path, 'rb') as img_file:
            img_base = base64.b64encode(img_file.read()).decode('utf-8')

        client = ZhipuAI(api_key="5ffdcf14622669c64487ab73392af88a.YkcYrzsq4prA0Yhm")  # 填写您自己的APIKey
        response = client.chat.completions.create(
            model="glm-4v-plus",  # 填写需要调用的模型名称
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": img_base
                            }
                        },
                        {
                            "type": "text",
                            "text": questions
                        }
                    ]
                }
            ]
        )
        answer = response.choices[0].message.content
        df.loc[index, '模型答案'] = answer
        res = cal_qwen(questions, answer, df['预期答案'])
        result = res['result']
        reason = res['reason']

        df.loc[index, '人工评分'] = result
        df.loc[index, '原因'] = reason
        df['错误类型'] = ''

        # answer = response.choices[0].message.content
        # df.loc[index, '模型答案'] = answer
        # # df['人工评分'] = ''
        # df['错误类型'] = ''
        #
        # result, reason = call_qwen(questions, answer, df['预期答案'])
        # df.loc[index, '人工评分'] = result
        # df.loc[index, '原因'] = reason

    df.to_excel(output_path, index=False)
    update_data(task_id, status='Success')




def call_mllm_task(task_id, task_path):
    call_model(task_id, task_path)


class MLLM(Page):
    def write(self):
        #task_id = st.query_params['task_id']  # 从url中获取测试任务的id
        # task_ids = st.query_params.get_all('tasks')  # 从url中获取测试任务的id
        # tasks_output = {}
        #
        # conn = get_db_connection()
        # db_task = MLLMNormalTask(conn)
        # placeholders = str([int(x) for x in task_ids])[1:-1]
        # task = db_task.get_tasks_by_ids(placeholders)


        conn = get_db_connection()
        db_mllm_task = DBMLLMTask(conn)
        df = db_mllm_task.get_tasks()

        # df['link'] = f'http://localhost:8501/?page=mllm_test_detail&task_id='

        df['id_str'] = df['id'].astype(str)
        df['link'] = df['id_str'].apply(lambda x: f"http://localhost:8501/?page=mllm_test_detail&task_id={x}")
        df = df.drop('id_str', axis=1)
        df['是否参与对比'] = False






        def on_click():
            task_name = st.session_state['task_name']
            # conn = get_db_connection()
            # db_mllm_task = DBMLLMTask(conn)
            # output_path = f'static/mllm/{task_name}.xlsx'
            # task_id = db_mllm_task.add_task(task_name, f'static/mllm/{task_name}.xlsx')
            # st.write(task_id)

            output_path = f'static/mllm/{task_name}.xlsx'
            task_id = db_mllm_task.add_task(task_name, status='running', output_path=output_path)
            process_mllm = Process(target=call_mllm_task, args=(task_id, output_path))
            process_mllm.start()

        with st.popover("创建多模态测试任务"):
            with st.form(key='mllm_test_task'):
                st.text_input('任务名称', key='task_name')
                st.form_submit_button("提交", on_click=on_click)

        st.data_editor(df, use_container_width=True, hide_index=True,
                     column_config={
                         'link': st.column_config.LinkColumn(display_text='任务详情'),
                         '是否参与对比': st.column_config.CheckboxColumn()
                     },key='mllm_task'
                     )
        # task_ids = st.query_params.get_all('tasks')  # 从url中获取测试任务的id
        # placeholders = str([int(x) for x in task_ids])[1:-1]
        # task = db_task.get_tasks_by_ids(placeholders)
        # 遍历DataFrame的每一行
        # for index, row in task.iterrows():
        #     # 提取'id'列的值，并将其作为键添加到字典中
        #     # 这里我们使用行索引作为字典的值，你也可以根据需要使用其他列的值
        #     tasks_output[row['id']] = row['output_path']

        # edit_df = st.session_state['mllm_normal_table']['edited_rows']
        # output_dict = [key for key, value in edit_df.items() if value["if_compare"]]
        # ids = result.iloc[output_dict]['id'].tolist()
        # st.query_params.tasks = ids
        #
        # mllmNormalCompareDetail.route()

        compare_button = st.button('生成对比报告')

        if compare_button:
            edit_df = st.session_state['mllm_task']['edited_rows']
            # st.write(st.session_state['mllm_task'])
            ids = []
            for key, value in edit_df.items():
                ids.append(df.loc[int(key)]['id'])
            st.query_params.tasks = ids
            mllm_test_compare.route()








mllm_test = MLLM('mllm_test')
