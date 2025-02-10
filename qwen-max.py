from dashscope import MultiModalConversation


prompt = """
你是一位阅读理解评分老师。针对question，分析answer和ground_truth，陈述的内容和观点是一致的吗？如果是一致的，请返回1；如果不一致，请返回0。并输出原因。 

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
        "result" : 1,
        "result" : "两边回答的心情是一样的"
    }
}

【examples】2:
{
    "question": "1+1等于几",
    "answer": "3",
    "ground_truth": "2",
    "verification": {
        "result" : 0,
        "result" : "两边的数值计算不一样"
    }
}

下面是真正的问题：
{
    "question": "%s",
    "answer": "%s",
    "ground_truth": "%s",
}

请按以下格式进行输出：
{
        "result": 0,
        "reason": "两者核心观点不一致",
}

""" % ("你的名字叫什么", "我无法回答我的名字", "frank")

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
                                                 api_key='sk-34f385226c2f491fb0c41692dd899e571')

print(response.output.choices[0].message.content[0]['text'])