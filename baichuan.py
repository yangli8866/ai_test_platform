import requests
import json

API_KEY='sk-880eb54ab32d5908d5a784265fa194e11'
url = "https://api.baichuan-ai.com/v1/assistants"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}



prompt = f"""
你是一位阅读理解评分老师。针对question，分析answer和ground_truth，陈述的内容和观点是一致的吗？如果是一致的，请返回1；如果不一致，请返回0。
注意：
-如果answer和ground_truth里有数值内容，必须保证严格相等。
-如果anser和ground_truth有一些关键实体名称，要保证名称要完全一致，不要错字漏字。
-注意在判断时，需要结合question的内容来综合判断。
-如果回答正确，则输出1，回答错误输出0
可以参考以下示例：
【示例】1:
question: 你今天心情怎么样？
answer: 我今天很开心
ground_truth: 我今天心情不错
verification: 1
【示例】2:
question: 3+1等于几？
answer: 3
ground_truth: 4
verification: 0

下面是真正的问题：
question: {'图片中有多少个人'}
answer:{'5个'}
ground_truth:{'6个'}

"""

data = {
    "instructions": prompt,
    "name": "Math Tutor",
    # "tools": [{"type": "code_interpreter"}],
    "model": "Baichuan4"
}

response = requests.post(url, headers=headers, data=json.dumps(data))

print(response.status_code)
print(response.json())