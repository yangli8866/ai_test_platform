import streamlit as st
from sqlalchemy import text


def get_db_connection():
    conn = st.connection(
        "mysql",
        type="sql",
        url="mysql://root:1qaz9ol.@9.134.12.32:3306/ai_tester?charset=utf8mb4",
        ttl=360,
        autocommit=True
    )
    return conn


class MLLMTask:
    def __init__(self, conn):
        self.conn = conn

    def get_tasks(self):
        sql = 'SELECT * FROM mllm ORDER BY id DESC'
        result = self.conn.query(sql, ttl=0)
        return result

    def add_task(self, name, output_path, status='运行中'):
        sql = f"INSERT INTO mllm(name,output_path, status) values('{name}', '{output_path}', '{status}')"
        result = self.conn.session.execute(text(sql))
        return result.lastrowid

    def get_task(self, task_id):
        sql = f'SELECT * FROM mllm WHERE id = {task_id} '
        result = self.conn.query(sql, ttl=0)
        return result

    def set_task_cal(self, task_id, pic_recall, pic_precision, pic_acc, average_score):
        sql = f"UPDATE mllm_ppl_task SET `pic_recall` = '{pic_recall}', `pic_precision` = '{pic_precision}', `pic_acc` = '{pic_acc}'  , `average_score` = '{average_score}'  WHERE id = {task_id}"
        result = self.conn.session.execute(text(sql))

    def get_tasks_by_ids(self, task_ids):
        sql = f'SELECT * FROM mllm  WHERE id in ({task_ids}) '
        result = self.conn.query(sql, ttl=0)
        return result


class DocParseTask:
    def __init__(self, conn):
        self.conn = conn

    def get_tasks(self):
        sql = 'SELECT * FROM doc_parse ORDER BY id DESC'
        result = self.conn.query(sql, ttl=0)
        return result

    def add_task(self, name, output_path, status='运行中'):
        sql = f"INSERT INTO doc_parse(name,output_path, status) values('{name}', '{output_path}', '{status}')"
        result = self.conn.session.execute(text(sql))
        return result.lastrowid

    def get_task(self, task_id):
        sql = f'SELECT * FROM doc_parse WHERE id = {task_id} '
        result = self.conn.query(sql, ttl=0)
        return result

    def set_task_cal(self, task_id, pic_recall, pic_precision, pic_acc, average_score):
        sql = f"UPDATE doc_parse SET `pic_recall` = '{pic_recall}', `pic_precision` = '{pic_precision}', `pic_acc` = '{pic_acc}'  , `average_score` = '{average_score}'  WHERE id = {task_id}"
        result = self.conn.session.execute(text(sql))

    def get_tasks_by_ids(self, task_ids):
        sql = f'SELECT * FROM doc_parse  WHERE id in ({task_ids}) '
        result = self.conn.query(sql, ttl=0)
        return result