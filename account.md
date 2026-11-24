# 电子账户：开户、业务开通、查询、余额、提现、结算

电子账户是分账接收方、余额支付双方的前提。顺序：用户开户 → 业务开通 → （可选）业务变更。
这些接口涉及身份证、银行卡、手机号，**只能在服务端调用，日志里必须脱敏**。

部分接口的响应可能不带 `status/data` 外层，而是直接返回业务字段（如 `{"trans_status":"S","account_no":"…"}`），解析时两种格式都要兼容。
开户、业务开通、业务变更的 `way_code` 都固定 `APPLY`，`trans_status`：`S` 成功、`P` 处理中、`F` 失败。
用户查询的 `trans_status` 只表示这次查询是否成功，见下方「用户查询」。

## 用户开户 `gateway/user/personapply`

| 参数 | 必填 | 说明 |
| --- | --- | --- |
| `way_code` | 是 | 固定 `APPLY` |
| `order_id` | 是 | 商户请求流水号，String(30)，唯一 |
| `account_name` | 是 | 个人填姓名，企业/个体户填企业名称，String(30) |
| `account_type` | 是 | `1` 个人、`2` 企业、`3` 个体户 |
| `relation_type` | 是 | `SERVICE_PROVIDER`、`STORE`、`STAFF`、`STORE_OWNER`、`PARTNER`、`HEADQUARTER`、`BRAND`、`DISTRIBUTOR`、`USER`、`SUPPLIER`、`CUSTOM` |
| `relation_type_name` | `CUSTOM` 时必填 | 类型描述 |
| `account_alias` | 是 | 账号别名 |
| `division_profit` | 是 | 分账比例字符串，`"0.0410"` 表示 4.10%；只做转账/余额支付时填 `"0"` |
| `client_ip` | 否 | |
| `channel_extra` | 是 | 个人传 `user_info`，企业/个体户传 `mer_info` |

`user_info`（个人）：

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `cert_type` | 是 | 默认 `00`，身份证 |
| `name` | 是 | 姓名 |
| `cert_no` | 是 | 身份证号 |
| `cert_validity_type` | 是 | `1` 长期、`0` 非长期 |
| `cert_begin_date` | 是 | `yyyyMMdd` |
| `cert_end_date` | 非长期时填 | `yyyyMMdd` |
| `mobile_no` | 是 | 手机号 |
| `email` | 是 | 邮箱，可传固定默认值 |

```json
{"user_info":{"cert_type":"00","name":"陈大海","cert_no":"610621198404070414","cert_validity_type":"0","cert_begin_date":"20170731","cert_end_date":"20370731","mobile_no":"13324502901","email":"123@qq.com"}}
```

官方允许证件有效期传预设值简化流程，如起始日 `20250110`、到期日 `20991231`。

`mer_info`（企业/个体户）：`reg_name`、`short_name`、`license_code`、`license_validity_type`、`license_begin_date`、
`license_end_date`（非长期必填）、`reg_prov_id`、`reg_area_id`、`reg_district_id`（省市区编码）、`reg_detail`、
`legal_name`、`legal_cert_type`（默认 `00` 身份证）、`legal_cert_no`、`legal_cert_validity_type`、`legal_cert_begin_date`、
`legal_cert_end_date`（非长期必填）、`contact_name`、`contact_mobile`，除标注外均必填。

开户、业务开通、业务变更的 `channel_extra` 可以超过 256 字符，官方 SDK 放宽到 2048。

响应：`trans_status`、`account_no`（用户编号，保存下来）、`resp_desc`。开户成功是 `trans_status == "S"`。

## 业务开通 `gateway/user/personconfirm`

请求固定 `way_code=APPLY`（SDK 自动带上）。开通成功是 `trans_status == "S"`。

| 参数 | 必填 | 说明 |
| --- | --- | --- |
| `order_id` | 是 | 请求流水号 |
| `account_no` | 是 | 开户返回的用户编号 |
| `client_ip` | 否 | |
| `channel_extra` | 是 | 含 `card_info`、`settle_config`、`cash_config` |

`card_info`：

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `card_type` | 是 | `0` 对公、`1` 对私、`2` 对私非法人。个人用户不支持 `2` |
| `card_name`、`card_no` | 是 | 户名、卡号 |
| `prov_id`、`area_id` | 是 | 开户行省、市编码 |
| `bank_code` | 对公必填 | 银行号 |
| `branch_code` / `branch_name` | 对公二选一 | 联行号 / 支行名 |
| `cert_type`、`cert_no`、`cert_validity_type`、`cert_begin_date`、`cert_end_date` | 对私必填（长期时无到期日） | 持卡人证件。`cert_type` 默认 `00` 身份证 |
| `mp` | 是 | 手机号 |

`settle_config`：`settle_cycle`（`D1` 自然日、`T1` 工作日）、`settle_status`（`1` 开启、`2` 关闭）。

`cash_config`（数组，至少一条）：`cash_type`（`D0` 实时到账、`D1` 隔天到账、`T1` 隔天工作日到账、`DM` 历史资金实时到账）、`switch_state`（`1` 开启、`2` 关闭）、`out_fee_flag`（`1` 商户承担、`2` 用户承担）。

```json
{"card_info":{"card_type":"1","card_name":"陈大海","card_no":"0206014170008888","prov_id":"100000","area_id":"110000","cert_type":"00","cert_no":"610621198404070414","cert_validity_type":"0","cert_begin_date":"20170731","cert_end_date":"20370731","mp":"13324502901"},"settle_config":{"settle_cycle":"D1","settle_status":1},"cash_config":[{"cash_type":"D1","switch_state":1,"out_fee_flag":1}]}
```

响应：`trans_status`、`account_no`、`resp_desc`。成功后该账户可参与分账、余额支付。

## 业务变更 `gateway/user/personmodify`

请求固定 `way_code=APPLY`（SDK 自动带上）。变更成功是 `trans_status == "S"`。
参数同业务开通，但 `card_info` 只有 `card_type`、`card_name`、`card_no` 三项。响应字段为 `trans_status`、`account_no`、`resp_desc`。

## 用户查询 `gateway/user/query`

请求：`way_code=APPLY`（SDK 自动带上）、`account_no`，可选 `client_ip`。
这个接口只返回查询状态和查到的资料，不返回开户结果：`trans_status` 是查询状态（`S` 查询成功、`P` 处理中、`F` 查询失败）。
查到的资料有 `account_no`、`account_name`、`account_type`、`relation_type`、`relation_type_name`、`division_profit`、`resp_desc`。`resp_desc` 可以为 `null`。
`channel_status` 也在查询资料里：`0` 待入驻、`1` 成功、`2` 失败，可能是数字也可能是字符串。SDK 的 `isOnboarded()` / `is_onboarded()` / `IsOnboarded` 只表示该字段为 `1`，不能用来判断开户是否成功。
`channel_extra` 可能是对象，也可能是 JSON 字符串。对象里有 `user_info`、`card_info`、`settle_config`、`cash_config`，以及同级 `settle_cycle`。
查询结果的 `settle_config` 会多出 `min_amt`、`remained_amt`；`cash_config` 可能没有 `out_fee_flag`；`card_type` 可能是数字。这些字段只用于展示，不能原样提交到业务开通或业务变更。

## 余额查询 `gateway/user/balance/query`

请求：`way_code=BALANCE_QUERY`、`order_id`（请求流水号）、`account_no`，可选 `client_ip`。
响应：`acct_type`、`acct_stat`（`N` 正常、`C` 关闭、`F` 冻结、`D` 销户）、`balance_amt`、`avl_balance`、`frz_bal`、`dm_amt`（金额为字符串）。

## 余额提现 `gateway/user/balance/withdraw`

请求：`way_code=BALANCE_WITHDRAW`、`order_id`（唯一，后续查询要用）、`account_no`、`withdraw_amount`（**元**，字符串，如 `"99.99"`）。
响应 `data`：`status`（`success` 或 `succeess` 都表示已受理；`succeess` 是平台定义的值，不是笔误）、`err_msg`。
失败示例：`{"status":400,"msg":"渠道侧:暂未开通取现权限","data":[]}`（失败时 `data` 可能是空数组）。

## 单笔提现查询 `gateway/user/balance/withdraw/single/query`

请求：`way_code=WITHDRAW_SINGLE_QUERY`、`account_no`、`withdraw_date`（`yyyyMMdd`）、`order_id`（原提现流水号）。
响应 `data`：`withdraw_date`、`order_id`、`cash_amt`、`fee_amt`（元）、`trans_status`（`pending`、`failed`、`succeeded`）、`trans_desc`、`status`、`err_msg`。

## 批量提现查询 `gateway/user/balance/withdraw/query`

请求：`way_code=WITHDRAW_QUERY`、`account_no`、`begin_date`、`end_date`（跨度小于 3 天）、可选 `page_size`（默认 10，建议 ≤ 100）、`page_num`（从 1 开始）。
响应：分页信息在 `data`（`count`、`page_size`、`page_num`、`status`），**记录列表在 `data.data`**。
每条记录：`settle_date`、`card_no`、`card_name`、`bank_name`、`batch_trans_type`、`cash_amt`、`fee_amt`、`fee_flag`、`org_req_date`、`order_id`、`trans_status`、`remark`、`trans_desc`。

## 结算记录查询 `gateway/user/settlement/query`

请求：`way_code=SETTLE_QUERY`、`order_id`、`account_no`、`begin_date`、`end_date`（跨度 ≤ 30 天）、可选 `page_size`、`page_num`。
响应 `data`：`trans_id`、`trans_date`、`settle_cycle`、`card_no`、`card_name`、`bank_code`、`trans_amt`、`fee_amt`（元）、
`trans_stat`（`I` 处理中、`F` 失败、`S` 成功）、`settle_type`（`0` 对公、`1` 对私法人、`2` 对私非法人、`3` 虚拟户）、`settle_abstract`、`settle_batch_no`、`settle_desc`。
