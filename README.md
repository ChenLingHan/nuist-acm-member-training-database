# NUIST ACM 训练开放数据

可供任何前端、分析程序或教学项目读取的静态数据集。[训练看板](https://chenlinghan.github.io/nuist-acm-training-dashboard/)是一个使用示例。

- [接口文档](API.md)：字段、完整性、读取示例、SQL 查询、版本与缓存约定。
- [数据入口](data/index.json) · [规范化完整数据 JSON](data/dataset.json) · [公开 SQLite](data/training-public.sqlite3)
- [OpenAPI 3.1](openapi.json) · [JSON Schema](dataset.schema.json) · [Python 示例](examples/read_data.py)
- 每表 JSON / JSONL、各账号所有 AC 和提交明细，见入口文件 paths / files。

CF 使用官方 API，目标上限 30 次/分钟；QOJ 登录读取并在限制时退避。洛谷由用户提供本人内存会话，先读取指定队员的个人页过题总量，再以所有队员合计最多 10 次/分钟、至少间隔 6 秒补采 AC 列表；批量通过时间补齐后常态仅检查 AC 列表，不再自动轮询 practice 页。遇验证或限制暂停。历史未补齐、字段未知会明确标记，不将空白当作零。

只发布训练元数据：姓名、年级、公开 OJ 账号、题目、提交、采集证据。不含学号、账号表、Cookie、密码、管理令牌、提交代码、原始页面、私人运行日志。SQLite 是从公开字段重新生成的文件，绝非本机数据库副本。

数据来自各 OJ，可能受可见范围、删除、重判和网络限制影响；平台题目和内容权利归原权利人。仓库未授予超出原来源的额外许可。自动合并增量并保留 Git 历史，默认每两分钟检查发布，间隔由本机管理员调整；无变化不新增提交。所有时间为 Unix 秒。

大文件采用分片或 gzip。请先读取 data/index.json，参见 API.md 的大文件读取说明。
