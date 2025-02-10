import pandas as pd
import streamlit as st
from utils import dataframe_agent

# 创建一个函数对图表绘制逻辑进行封装
def create_chart(input_data, chart_type):
    df_data = pd.DataFrame(input_data["data"], columns=input_data["columns"])# 把数据由列表转化成dataframe数据类型
    df_data.set_index(input_data["columns"][0], inplace=True)# 设置dataframe的索引。inplace=True可以实际改变这个df_data
    # 索引会被用来表示图表的横轴，因此在这里把第一个列设置为索引
    if chart_type == "bar":
        st.bar_chart(df_data)
    elif chart_type == "line":
        st.line_chart(df_data)
    elif chart_type == "scatter":
        st.scatter_chart(df_data)

st.title("💡 CSV数据分析智能工具")

with st.sidebar:
    openai_api_key = st.text_input("请输入OpenAI API密钥：", type="password")
    st.markdown("[获取OpenAI API key](https://platform.openai.com/account/api-keys)")

data = st.file_uploader("上传你的数据文件（CSV格式）：", type="csv")
if data:
    st.session_state["df"] = pd.read_csv(data)
    with st.expander("原始数据"):
        st.dataframe(st.session_state["df"])# streamlit展示dataframe的现成组件

query = st.text_area("请输入你关于以上表格的问题，或数据提取请求，或可视化要求（支持散点图、折线图、条形图）：", disabled=not data)
button = st.button("生成回答")

if button and not openai_api_key:
    st.info("请输入你的OpenAI API密钥")
if button and "df" not in st.session_state:
    st.info("请先上传数据文件")
if button and openai_api_key and "df" in st.session_state:
    with st.spinner("AI正在思考中，请稍等..."):
        response_dict = dataframe_agent(openai_api_key, st.session_state["df"], query)
        if "answer" in response_dict:
            st.write(response_dict["answer"])
        if "table" in response_dict:
            st.table(pd.DataFrame(response_dict["table"]["data"],
                                  columns=response_dict["table"]["columns"]))
            # 第一个参数是表格里的内容，接受dataframe作为参数。所以我们要提取的是响应里面data键对应的值
            # pd.DataFrame(）把数据由列表转化成dataframe数据类型
            # 第二个参数是columns，参数赋值为表示列名的列表
        if "bar" in response_dict:
            create_chart(response_dict["bar"], "bar")
        if "line" in response_dict:
            create_chart(response_dict["line"], "line")
        if "scatter" in response_dict:# 散点图
            create_chart(response_dict["scatter"], "scatter")
