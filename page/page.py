import streamlit as st
import time


class Page:
    def __init__(self, route):
        self.route_path = route

    # def get_route_path(self):
    #     return self.route_path

    def refresh_route(self):
        # st.query_params.clear()
        # st.session_state["svap_router_route"] = self.route_path
        st.query_params["page"] = self.route_path

    def route(self):
        # st.session_state["svap_router_route"] = self.route_path
        st.query_params["page"] = self.route_path
        time.sleep(0.1)  # 需要等待路由更新
        st.rerun()
        # st.experimental_rerun()

    def get_route(self):
        return self.route_path

    def write(self):
        pass
