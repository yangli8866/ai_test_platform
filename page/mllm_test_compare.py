import streamlit as st
from page.page import Page
from page.db import MLLMTask as DBMLLMTask, get_db_connection
import pandas as pd
import os


class MLLMCompareTaskDetail(Page):
    def write(self):
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

        task_id = st.query_params.get_all('tasks')
        placeholders = str([int(x) for x in task_id])[1:-1]
        st.write(f'task_id is : {placeholders}')

        conn = get_db_connection()
        db_mllm_task = DBMLLMTask(conn)
        tasks = db_mllm_task.get_tasks_by_ids(placeholders)

        task = tasks.loc[0]
        df = pd.read_excel(task.output_path)

        # 原始的df， 里面有公共的列
        df = df[['图片', '问题', '场景', '预期答案']]
        score_columns = []
        error_columns = []

        tasks_output = {}
        # 拼接每一个任务的结果。
        for index, row in tasks.iterrows():
            # 提取'id'列的值，并将其作为键添加到字典中
            # 这里我们使用行索引作为字典的值，你也可以根据需要使用其他列的值
            tasks_output[row['id']] = row['output_path']
        for index, row in tasks.iterrows():
            result = pd.read_excel(row.output_path)
            result = result[['模型答案', '人工评分', '错误类型']]
            task_name = row['name']
            result.columns = [f'{task_name}:{row["id"]}:模型答案', f'{row["id"]}:{task_name}:人工评分', f'{row["id"]}:{task_name}:错误类型']
            score_columns.append(f'{row["id"]}:{task_name}:人工评分')
            error_columns.append(f'{row["id"]}:{task_name}:错误类型')
            df = pd.concat([df, result], axis=1)

        column_config = {
                            "图片": st.column_config.ImageColumn(),
                        }
        for item in score_columns:
            column_config[item] = st.column_config.SelectboxColumn(
                                options=['正确', '错误']
                            )
        for item in error_columns:
            column_config[item] = st.column_config.SelectboxColumn(
                                options=['指令错误', '上下文错误', '幻觉']
                            )

        prefix = 'http://localhost:8501/app/static/data/pic/'
        df['图片'] = df['图片'].apply(lambda x: os.path.join(prefix, x))

        def hold_page():
            st.query_params['page'] = 'mllm_test_compare'
            st.query_params['task_id'] = task_id

        # st.write(column_config)
        st.data_editor(df, key='mllm_task_table',
                       column_config=column_config,
                       on_change=hold_page,
                       )

        def save_anno():
            edit_df = st.session_state['mllm_task_table']['edited_rows']

            output_score_dfs = {}
            # 读取所有输出文件:
            scoring_columns = [col for col in df.columns if '人工评分' in col]
            for col in scoring_columns:
                taskid = col.split(':')[0]
                output_file_path = tasks_output[int(taskid)]
                read_df = pd.read_excel(output_file_path)
                output_score_dfs[taskid] = {'df': read_df, 'path': output_file_path}

            for index, value in edit_df.items():
                for column, v in value.items():
                    st.write(column)
                    taskid = column.split(':')[0]
                    column_name = column.split(':')[2]
                    write_df = output_score_dfs.get(str(taskid))['df']
                    write_df.loc[index, column_name] = v
            for taskid, value in output_score_dfs.items():
                save_dataframe = value['df']
                save_path = value['path']
                save_dataframe.to_excel(save_path, index=False)

        def cal_mllm():
            hold_page()
            cal_df = df.groupby('场景').size().to_frame().T
            st.write(cal_df)

            # cal_df = df.groupby('人工评分').size().to_frame().T
            # cal_df.columns = ['数量']
            # cal_df['总分'] = (cal_df['基本正确'] * 6 + cal_df['完全正确'] * 10) / (
            #         cal_df['基本正确'] + cal_df['完全正确'] + cal_df['完全错误'])
            #
            # err_df = df.groupby('错误类型', dropna=True).size().to_frame().T
            # err_df['上下文错误'] = err_df['上下文错误'] / len(df)
            # err_df['指令错误'] = err_df['上下文错误'] / len(df)
            # err_df['数字计算错误'] = err_df['上下文错误'] / len(df)
            #
            # sence_df = df.groupby(['场景', '人工评分']).size()
            #
            # st.write(cal_df)
            # st.write(err_df)
            # st.write(sence_df)
            pass

        st.button('记录标注', on_click=save_anno)
        st.button('计算指标', on_click=cal_mllm)


mllm_test_compare = MLLMCompareTaskDetail('mllm_test_compare')
