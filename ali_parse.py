import base64
import os
import time
from alibabacloud_tea_openapi.models import Config
from alibabacloud_searchplat20240529.client import Client
from alibabacloud_searchplat20240529.models import (
    CreateDocumentAnalyzeTaskRequestDocument,
    CreateDocumentAnalyzeTaskRequestOutput,
    CreateDocumentAnalyzeTaskRequest,
    CreateDocumentAnalyzeTaskResponse,
    GetDocumentAnalyzeTaskStatusRequest,
    GetDocumentAnalyzeTaskStatusResponse
)


def call_ali(local_file_path):
    config = Config(bearer_token="OS-g1h6d9g3s948p1nu1",
                    # endpoint: 配置统一的请求入口 需要去掉http://
                    endpoint="default-dm5.platform-cn-shanghai.opensearch.aliyuncs.com",
                    # 支持 protocol 配置 HTTPS/HTTP
                    protocol="http"
                    )
    client = Client(config=config)
    # 本地模式，需要额外指定file_name
    document = CreateDocumentAnalyzeTaskRequestDocument(
        content=base64.b64encode(open(local_file_path, 'rb').read()).decode(),
        file_name=os.path.basename(local_file_path)
    )

    output = CreateDocumentAnalyzeTaskRequestOutput(image_storage="url")
    request = CreateDocumentAnalyzeTaskRequest(document=document, output=output)
    # default：替换工作空间名称, ops-document-analyze-001: 服务id
    response: CreateDocumentAnalyzeTaskResponse = client.create_document_analyze_task(
        "default", "ops-document-analyze-001", request)
    task_id = response.body.result.task_id
    # print("task_id: " + task_id)
    request = GetDocumentAnalyzeTaskStatusRequest(task_id=task_id)
    while True:
        response: GetDocumentAnalyzeTaskStatusResponse = client.get_document_analyze_task_status(
            "default", "ops-document-analyze-001", request)
        status = response.body.result.status
        print("status: " + status)
        if status == "PENDING":
            time.sleep(5)
        elif status == "SUCCESS":
            data = response.body.result.data
            # usage = response.body.usage
            print(response.body)
            # print("content:\n" + data.content[:20] + "\n")
            # print("content:\n" + data.content + "\n")
            # print("page count: " + str(data.page_num))
            # print("usage: " + str(usage))
            return data.content
            # break
        else:
            print(response.body.result)
            break


content = call_ali('static/doc/财报.pdf')
print(content)