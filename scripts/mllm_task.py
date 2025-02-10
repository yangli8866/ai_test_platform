import pandas as pd
import os
import base64
from zhipuai import ZhipuAI


def get_project_root():
    current_file_path = os.path.abspath(__file__)
    project_root = os.path.dirname(os.path.dirname(current_file_path))
    return project_root


def call_mllm(img_path):
    with open(img_path, 'rb') as img_file:
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
                        "text": "请描述这个图片"
                    }
                ]
            }
        ]
    )
    return response


if __name__ == "__main__":
    df = pd.read_excel(os.path.join(get_project_root(), 'static/data/pic/mllm_anno.xlsx'))

    df['打分'] = ''
    df['错误类型'] = ''
    df['模型输出'] = ''

    for row in df.itertuples(index=True):
        # print(f"Index: {row.图片}")
        img_path = os.path.join(get_project_root(), f'static/data/pic/{row.图片}')
        res = call_mllm(img_path)
        answer = res.choices[0].message.content
        df.loc[row.Index, '模型输出'] = answer
        print(answer)
        break

    print(df)
