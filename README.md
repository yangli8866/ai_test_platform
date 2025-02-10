这是简易自动标注平台
含有多模态大模型和普通大模型 的 标注、自动标注、结果diff等功能

- 主要使用框架：pandas、streamlit
- 模型为：qwen、zhipu

前置工作：

mysql
安装启动：
```
docker run --name some-mysql -e MYSQL_ROOT_PASSWORD=1qaz9ol. -p 3306:3306  -d mysql:5.5
docker exec -it some-mysql bash
mysql -h localhost -u root -p
```

创建表
```
create database ai_tester;
CREATE TABLE mllm (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    output_path VARCHAR(255),
    status VARCHAR(50)
);

CREATE TABLE doc_parse (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    output_path VARCHAR(255),
    status VARCHAR(50)
);
```

