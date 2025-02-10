# import streamlit as st
# import pandas as pd
#
# st.header('这是一个测试平台')
# st.write('测试测试')
#
# df = pd.read_excel('static/data/pic/mllm_anno.xlsx')
# st.data_editor(df, use_container_width=True)


# import streamlit as st
# import pandas as pd
#
#
#
# # 示例数据
# data = {
#     'Name': ['Alice', 'Bob', 'Charlie', 'David'],
#     'Age': [30, 25, 35, 28],
#     'City': ['New York', 'Los Angeles', 'Chicago', 'Houston']
# }
#
# # 将数据转换为DataFrame
# df = pd.DataFrame(data)
#
# # 添加多选列
# selected_columns = st.multiselect('Select columns:', df.columns)
#
# # 显示筛选后的DataFrame
# st.dataframe(df[selected_columns])


import streamlit as st
import pandas as pd

# 创建一个示例数据框
data = {
    '列1': ['数据1', '数据2', '数据3'],
    '列2': ['数据A', '数据B', '数据Cqwe']
}
df = pd.DataFrame(data)

# 自定义 CSS 来设置行高
st.markdown(
    """
    <style>
    .stDataFrame tbody tr {
        height: 250px;  /* 你可以根据需要调整这个值 */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 显示数据框

st.dataframe(df.style.highlight_max(axis=1))



