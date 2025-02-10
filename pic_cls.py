import cv2
import numpy as np

# yolov3下载地址：
# 网络结构文件：https://github.com/pjreddie/darknet/blob/master/cfg/yolov3.cfg
# 模型(权重)文件：https://pjreddie.com/media/files/yolov3.weights
# 80个类别标签的文本文件：https://raw.githubusercontent.com/pjreddie/darknet/master/data/coco.names

net = cv2.dnn.readNet('yolov3.weights', 'yolov3.cfg')
# 加载类别标签
classes = []
# with open('coco.names', 'r') as f:
#     classes = [line.strip() for line in f.readlines()]

datas = []
with open('static/pic_cls/labels.txt', 'r') as f:
    for line in f:
        datas.append(list(line.strip('\n').split(' ')))
print(datas)

TP = 0
FN = 0
FP = 0
TN = 0

for image in datas:
    path = image[0]
    label_y = int(image[1])
    frame = cv2.imread(path)
    height, width, _ = frame.shape
    # 构建输入图像
    blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (416, 416), swapRB=True, crop=False)

    # 设置输入层和输出层
    net.setInput(blob)
    output_layers = net.getUnconnectedOutLayersNames()

    # 前向传播，模型推理
    outputs = net.forward(output_layers)

    # 解析输出
    boxes = []
    confidences = []
    class_ids = []
    for output in outputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5 and class_id == 0:  # 只检测人类
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)
                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)
    # 非极大值抑制
    indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

    y = 0
    # # 判断是否存在人类
    if len(boxes) > 0:
        y = 1
        print('There is a human in the image.')
    else:
        y = 0
        print('There is no human in the image.')
    if label_y == 1 and y == 1:
        TP += 1
    elif label_y == 1 and y == 0:
        FN += 1
    elif label_y == 0 and y == 1:
        FP += 1
    elif label_y == 0 and y == 0:
        TN += 1

recall = TP / (TP + FN)
precision = TP / (TP + FP)

print("recall: " + str(recall))
print("precision: " + str(precision))



#
# from sklearn.metrics import confusion_matrix
# import pandas as pd
#
# # 创建一个字典，其中包含'label'和'answer'的键，以及相应的数据
# data = {
#     'label': ['fig_other', 'fig_data', 'fig_mind', 'fig_proc','fig_other', 'fig_data', 'fig_mind', 'fig_proc', 'fig_other'],  # 示例标签
#     'answer': ['fig_data', 'fig_data', 'fig_other', 'fig_proc','fig_proc', 'fig_proc', 'fig_mind', 'fig_proc', 'fig_other']         # 示例答案
# }
#
# # 使用字典创建DataFrame
# df = pd.DataFrame(data)
#
#
# # 计算混淆矩阵
# cm = confusion_matrix(df['label'], df['answer'],
#                               labels=['fig_other', 'fig_data', 'fig_mind', 'fig_proc'])
#
# # 定义分类标签
# labels = ['fig_other', 'fig_data', 'fig_mind', 'fig_proc']
#
# # 计算每个分类的召回率和精确率
# recall = {}
# precision = {}
# for i, label in enumerate(labels):
#             recall[label] = round(cm[i, i] / cm[:, i].sum(), 4)
#             precision[label] = round(cm[i, i] / cm[i, :].sum(), 4)
#
# # 找出每个分类的badcase
# badcases = {}
# for i, label in enumerate(labels):
#     badcases[label] = df[(df['label'] == label) & (df['answer'] != label)]
#
# print(recall)
# print(precision)
# print('下面是badcase')
# for key, value in badcases.items():
#     print(key)
#     print(value)

