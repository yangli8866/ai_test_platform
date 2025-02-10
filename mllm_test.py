import base64
from zhipuai import ZhipuAI

img_path = "static/data/pic/1.jpg"
with open(img_path, 'rb') as img_file:
    img_base = base64.b64encode(img_file.read()).decode('utf-8')

client = ZhipuAI(api_key="5ffdcf14622669c64487ab73392af88a.YkcYrzsq4prA0Yhm1")  # 填写您自己的APIKey
response = client.chat.completions.create(
    model="glm-4v-plus",  # 填写需要调用的模型名称
    messages=[
        {
            "role": "user", # user , system, assitants(助手)
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": img_base
                    }
                },
                {
                    "type": "text",
                    "text": "请问图片中有多少人"
                }
            ]
        }
    ]
)
print(response.choices[0].message)
