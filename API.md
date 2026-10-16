# 静态数据接口 v2

本仓库提供无需鉴权、无需后端服务的只读文件接口，独立于展示页面。v1 大屏接口继续兼容。无 POST、服务端筛选或分页查询接口；URL 后增加 handle 等查询参数不会筛选数据，请客户端筛选。

## 地址与读取顺序

基地址：`https://raw.githubusercontent.com/ChenLingHan/nuist-acm-member-training-database/main/`

1. 读取 `data/index.json`，比较 revision；未变化时复用本地结果。
2. 按 paths 或 accounts[].path 获取文件。需要所有数据时下载 `data/dataset.json` 或 `data/training-public.sqlite3`。
3. 分文件读取完成后再次检查入口 revision；变化时重新获取。GitHub/CDN 缓存可能导致短暂混版；严格一致性应把 URL 中 main 替换为同一个 Git commit SHA。files 提供 SHA-256 和字节数（入口不自校验）。缓存不保证两分钟可见，30 次/分钟是采集上限而非数据实时性承诺。

## 文件

|路径|内容|
|---|---|
|data/index.json|兼容 schema_version=1，新增 api_version=2、revision、generated_at、paths、counts、files；账号归档列表|
|data/dashboard.json|兼容 v1：在训队员、账号、设置、去重过题、最近 100 条 AC，供现有看板使用|
|data/dataset.json|api_version=2、revision 和下面八张表的全部数据|
|data/{table}.json|api_version、revision、items（完整表，无截断）|
|data/{table}.jsonl|每行一个同表对象，UTF-8，可流式读取；空表为空文件|
|data/accounts/a*.json|单账号全部 solves、accepted_submissions、submissions、coverage，不限于最近 100 条|
|data/training-public.sqlite3|八张表 + metadata，可直接 SQL 查询；列表字段以 JSON 文本保存|

八张表：members、accounts、problems、solves、accepted_submissions、submissions、coverage、batches。当前文件只含当前启用队员及其绑定；停用或移除后的旧数据可从 Git 历史读取。编号是仓库内稳定的不透明标识，不能视为学号。

## 字段与关联

所有 *_at、from_at、to_at、history_before、latest_checkpoint 为 UTC Unix 秒（可能为小数），显示北京时间时用 Asia/Shanghai；duration / relative_time_seconds 为秒，time_ms 为毫秒，memory_bytes 为字节。空值或未出现字段代表未知/平台未提供，不代表零或无记录。可增加可选字段；破坏性变更将提升 api_version。

|表|主键 / 字段说明|
|---|---|
|members|id；name 姓名、cohort 入学年份、active=1|
|accounts|id；member_id → members.id，platform=luogu/codeforces/qoj，handle 为洛谷数字 UID 或其他平台账号；inventory_total 平台个人页去重过题总量、inventory_at 获取时间、inventory_source 原始个人页来源 URL；last_success 最近成功请求；complete=1 仅表示已读到一次可访问历史末尾；first_ac_at 已知最早 AC，first_ac_confirmed=1 才完成历史与缺题核对；cursor、cursor_unit 下次历史位置；history_before 已到达的旧时间边界；last_full_scan_at 扫描末尾时间；latest_checkpoint 最新已核对头部边界，latest_cursor 最新区间的下一位置；history_mode 表示采集方式|
|problems|(platform, problem_id)；title、difficulty、tags（已获取标签列表）、points（平台分值，可空）|
|solves|(account_id, problem_id)；member_id、platform、title、difficulty、solved_at 最早已知 AC 提交时间、observed_at 首次入库时间、source 来源。快照没有提交时间，solved_at=null|
|accepted_submissions|(account_id, submission_id)；problem_id、title、difficulty、accepted_at 已通过提交的提交时间（不是判题结束时间）、observed_at 首次入库。重复通过保留，按题去重请读 solves|
|submissions|(account_id, submission_id)；problem_id、title、difficulty、submitted_at、observed_at、verdict（AC 归一为 OK，其余保留平台结果）、verdict_text（QOJ 原始可见判定，例如 200 ✓）、language、time_ms、memory_bytes、resource_time_text/resource_memory_text（QOJ 原始可见单位文字）、code_size_text、tags、points、testset、passed_test_count、participant_type、relative_time_seconds、source。保留响应中已经取得的非 AC 提交，但旧版只收 AC，因此非 AC 历史不完整；不包含源码。未获得的扩展字段可以省略|
|coverage|account_id、from_at、to_at、checked_at、kind=history/latest；成功返回页面的时间边界，可相交。不是整月全覆盖证明，区间之间仍未知；旧日志不追溯伪造|
|batches|account_id、fetched_at、kind（snapshot/history/latest/repair/metadata/reparse）、position、returned_count 返回条数、accepted_count AC 条数、new_solves 新题、new_ac 新 AC、oldest_at/newest_at 本批边界、total_count/page_size 平台分页信息、scope_problem（定向补题时的题号，否则 null）；仅成功入库的批次摘要；reparse 为使用已存提交纠正判定，不是新增页面查询，不生成新的查询覆盖区间；无错误日志|

洛谷仅保留题号以 P、B、CF、SP、AT、UVA 开头的公开题库题目；排除 T、U 及其他前缀。UVA 属于保留范围。过题数、AC 动态、提交明细与缺失日期统计均使用此范围。旧范围主页总量在重新核对前为 null，不能拿包含私题的总数与公开题明细比较。分页返回条数、总页数和查询时间边界仍来自原始页面，可能包含已被过滤的记录，不等于收录的公开题数。batches.collection_scope=luogu_public_v1 才表示洛谷新增量按公开题过滤；legacy 表示旧口径，保留查询证据但不用于当前公开题增量统计。accounts.inventory_scope=luogu_public_v1 才表示主页计数已按公开题核对；当前训练统计请使用 solves 与 accepted_submissions。

题目难度：洛谷 0=暂无评定，1..8 为平台难度等级；CF 为原始 Rating，部分 Gym 没有 Rating；QOJ 无统一评分，使用 null。QOJ 同时识别 AC/Accepted 及带明确通过勾号的满分结果（如 25 ✓、100 ✓、200 ✓），不把单独分数当作 AC，也不假定满分必须为 100。不同平台题号不合并，同一题被不同队员通过分别计数。profile 总量与记录数可能不同：一个是去重过题，一个是包含重复通过的提交数，且采集仍可能缺失。

发现延迟：accepted_submissions.discovery_delay_seconds = observed_at − accepted_at（秒），重复采集不重置 observed_at。discovery_mode 为 routine（常态最新检查且提交发生在本机常态统计起点之后）、catch_up（最新检查发现的旧提交）、backfill（历史/定向补采）、legacy（旧记录，没有可靠采集阶段证据）。discovery_kind 为首次写入时任务类型，旧记录为空。仅 routine 且延迟非负的记录可用于统计常态发现速度；其余记录的差值仍可参考，不应混算。跨机导入保留原始 observed_at；阶段信息缺失时显示 legacy。AC 时间是提交时间，延迟包含平台判题、列表更新和排队耗时，不等于单次请求耗时；负值应视为时钟或源时间异常。

## 完整性与断点

complete 不是所有数据完整的保证，first_ac_confirmed 只针对当时可访问记录。要判断日期缺口，应比较账号 inventory_total 与 solves 中 solved_at 非空的题数，并查看 coverage / history_before。未见到记录不能推断该时间段无人训练。洛谷 history_mode=authenticated_pages：使用用户授权的本人内存会话查询指定队员的提交列表，主页过题清单与提交明细各自保存。缺失时间保持 null，待后续分页或本人导入补齐。登录凭据不在公开接口中。

CF 一次官方 API 请求获取最多 1000 条，历史向前保留 50 条重叠，提交 ID 去重；各平台最新记录默认约每 10 分钟到期检查，到期任务优先于历史补采；QOJ 逐页补采。三个平台独立预算、独立队列。洛谷主页和明细共用最多 10 次/滚动 60 秒、至少间隔 6 秒的预算；CF / QOJ 各最多 30 次、至少间隔 2 秒；收到 429 遵循 Retry-After 并降速，401/403/验证页暂停。本机管理员可以手动解除洛谷的本地冷却，仍保留限速和服务器明确指定的 Retry-After；该管理操作不属于公开只读接口。账号错误不会阻塞其他平台。此接口仅反映已取得的数据，自动补采不会虚构隐藏或不可访问记录。

## JavaScript

```js
const base = 'https://raw.githubusercontent.com/ChenLingHan/nuist-acm-member-training-database/main/';
const index = await fetch(base + 'data/index.json').then(r => { if (!r.ok) throw Error(r.status); return r.json(); });
const data = await fetch(base + index.paths.dataset).then(r => r.json());
if (data.revision !== index.revision) throw Error('数据更新中，请重试或固定 commit SHA');
const member = data.members.find(m => m.name === '陈凌寒');
const ids = new Set(data.accounts.filter(a => a.member_id === member?.id).map(a => a.id));
const records = data.accepted_submissions.filter(s => ids.has(s.account_id));
records.sort((a, b) => b.accepted_at - a.accepted_at);
console.log(records);
```

## SQLite

```sql
-- 下载公开 SQLite 后运行；获取每人近七天首次通过题数。
SELECT m.name, COUNT(*) AS solved_last_7_days
FROM solves s JOIN accounts a ON a.id=s.account_id JOIN members m ON m.id=a.member_id
WHERE s.solved_at >= unixepoch('now') - 7*86400
GROUP BY m.id ORDER BY solved_last_7_days DESC;
-- 查询某账号所有 AC，而不是大屏最近 100 条。
SELECT * FROM accepted_submissions WHERE account_id='a2' ORDER BY accepted_at DESC;
```

Python 下载及校验示例见 examples/read_data.py。GitHub Raw 支持浏览器跨域读取（受平台自身可用性及缓存影响）；大数据分析宜下载 SQLite / JSONL 并缓存，勿反复轮询全部大文件。
