import streamlit as st
from page.page import Page
from page.db import DocParseTask as DBDocParseTask, get_db_connection
import pandas as pd
import os


class DocParseCompare(Page):
    def write(self):

        task_ids = st.query_params.get_all('tasks')
        placeholders = str([int(x) for x in task_ids])[1:-1]
        st.write(f'task_id is : {placeholders}')

        conn = get_db_connection()
        db_doc_parse_task = DBDocParseTask(conn)
        tasks = db_doc_parse_task.get_tasks_by_ids(placeholders)

        task = tasks.loc[0]
        df = pd.read_csv(task.output_path)
        details_names = []

        # 原始的df， 里面有公共的列
        df = df[['file_name', 'anno_parse_md_file_path']]
        # 拼接每一个任务的结果。
        for index, row in tasks.iterrows():
            task_name = row['name']
            task_id = row['id']
            result = pd.read_csv(row['output_path'])
            result[f'{task_name}_相似度'] = result['similarity']
            # result[f'{task_name}_详情'] = 'http://localhost:8501?page=doc_parse_detail&id='
            result = result.assign(
                详情=lambda
                    x: 'http://localhost:8501?page=doc_parse_data_detail&task_id=' + str(
                    task_id) + '&file_name=' + result['file_name'])
            result.rename(columns={'详情': f'{task_name}_详情'}, inplace=True)
            df = pd.merge(df, result, on='file_name', how='outer')
            details_names.append(f'{task_name}_详情')

        config = {}
        for n in details_names:
            config[n] = st.column_config.LinkColumn()
        st.dataframe(df, column_config=config)






doc_parse_compare = DocParseCompare('doc_parse_compare')
