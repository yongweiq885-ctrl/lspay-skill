# 快捷支付（银行卡）

商户需先开通快捷支付业务。有两种接入方式：

| 方式 | `way_code` | 说明 |
| --- | --- | --- |
| API 模式 | `BANK_FAST` | 下单后拿到支付参数，商户自己封装到任意支付场景，并自己做绑卡、短信确认页面 |
| 收银台模式 | `BANK_FAST_JUMP` | 直接返回或跳转立收通快捷支付页。用户在页面输入银行卡，银行发短信，系统自动完成绑卡和支付。适合要快速接入的商户 |

银行卡号、身份证、手机号、短信验证码、`channel_card_id` **只能在服务端处理，日志里必须脱敏**。

## API 模式流程

```text
首次：绑卡申请（银行发短信）→ 绑卡确认（提交验证码）→ 保存 channel_user + channel_card_id
支付：支付申请（银行发短信）→ [可选] 短信校验 → 支付确认（提交验证码）→ 等支付通知
解约：解绑
```

API 模式下所有接口的 `way_code` 都固定为 `BANK_FAST`。

## 绑卡申请 `gateway/quickpay/buckleapply`

| 参数 | 必填 | 说明 |
| --- | --- | --- |
| `order_id` | 是 | 商户请求流水号，String(30)，绑卡确认时要复用 |
| `way_code` | 是 | `BANK_FAST` |
| `client_ip` | 否 | |
| `channel_extra` | 是 | 四要素，见下 |

`channel_extra`：

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `mch_user_id` | 是 | 商户系统里的用户编号 |
| `cert_type` | 是 | 仅支持 `00`，身份证 |
| `card_id` | 是 | 银行卡号 |
| `card_name` | 是 | 开户姓名 |
| `cert_id` | 是 | 身份证号 |
| `cert_validity_type` | 是 | `1` 长期、`0` 非长期 |
| `cert_begin_date` | 是 | `yyyyMMdd`，可传预设默认值 |
| `cert_end_date` | 非长期时填 | `yyyyMMdd` |
| `card_mp` | 是 | 银行预留手机号 |
| `dc_type` | 是 | `D` 借记卡、`C` 信用卡、`S` 准贷记、`U` 未知 |
| `vip_code` | 信用卡 | CVV2，为空时不传 |
| `expiration` | 信用卡 | 卡有效期 `MMYY`，为空时不传 |

响应：`trans_status`、`trans_id`、`order_id`、`resp_desc`。成功后银行给预留手机号发验证码。

## 绑卡确认 `gateway/quickpay/buckleconfirm`

| 参数 | 必填 | 说明 |
| --- | --- | --- |
| `order_id` | 是 | 与绑卡申请相同 |
| `way_code` | 是 | `BANK_FAST` |
| `verify_code` | 是 | 短信验证码（示例为 6 位数字） |
| `channel_extra` | 是 | `mch_user_id`、`cert_type`、`card_id`、`card_name`、`cert_id`、`card_mp`、`dc_type`，与申请时一致 |

响应：`trans_status`、`channel_user`、`channel_card_id`、`resp_desc`。
只有 `trans_status == "S"` 且 `channel_card_id` 非空时才算绑卡成功，保存 `channel_user` 与 `channel_card_id`（与本地用户、卡关联）。

## 支付申请（走 `gateway/unifiedorder`）

参数同统一下单（见 [payment.md](payment.md)），另外：

- `way_code=BANK_FAST`
- `channel_extra={"channel_user":"…","channel_card_id":"…"}`（均必填）
- 可同时设置 `division_mode` 做分账

响应 `data`：`pay_order_id`、`mch_order_no`、`trans_status`、`order_state`、`err_code`、`err_msg`。
`trans_status == "P"` 表示已受理、银行已发短信，不是失败。

## 短信校验（可选）`gateway/quickpay/smscheck`

预校验验证码，避免等到确认时才发现错误。成功后仍要调支付确认。

参数：`way_code=BANK_FAST`、`pay_order_id` / `mch_order_no` 二选一、`verify_code`（6 位数字）、可选 `client_ip`。
响应 `data`：`trans_status`、`err_msg`。

## 支付确认 `gateway/quickpay/payconfirm`

参数同短信校验。
响应 `data`：`trans_status`（`S` 成功、`P` 验证中、`F` 失败）、`err_msg`。
最终结果以支付通知（`state=2`）或订单查询为准；`P` 时等通知或轮询订单查询。

## 解绑 `gateway/quickpay/payunbind`

| 参数 | 必填 | 说明 |
| --- | --- | --- |
| `order_id` | 是 | 请求流水号 |
| `way_code` | 是 | `BANK_FAST` |
| `channel_extra` | 是 | `{"mch_user_id":"…","channel_card_id":"…"}` |

响应：`trans_status`、`order_id`、`resp_desc`。成功后删除本地保存的绑卡信息。

## 收银台模式 `BANK_FAST_JUMP`（走 `gateway/unifiedorder`）

商户不需要自己做绑卡、短信确认页面，用户在收银台页面上完成绑卡和支付。

参数同统一下单（见 [payment.md](payment.md)），另外：

- `way_code=BANK_FAST_JUMP`
- `channel_extra`（必传，统一下单要求；里面的字段都可选，一般至少写 `pay_data_type`）：

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `channel_user` | 否 | 用户 ID，由绑卡确认接口返回。传了才能在收银台里显示该用户已绑定的银行卡；不传则用户每次都要重新填卡 |
| `pay_data_type` | 否 | `pay_url` 返回支付链接；`cashier` 时由浏览器提交签名表单到收银台，服务端不能直接调用，见 [payment.md](payment.md) 的「cashier 收银台」 |

`channel_user` 只由绑卡确认接口 `gateway/quickpay/buckleconfirm` 返回；收银台支付的下单响应和支付通知里都没有这个字段。
要让收银台带出已绑定的卡，先用绑卡申请 + 绑卡确认接口为用户绑卡，把返回的 `channel_user` 与本地用户关联保存，下单时带上；没有就不传。

```text
way_code=BANK_FAST_JUMP
amount=100
currency=cny
subject=快捷支付测试
body=储蓄卡快捷支付测试
notify_url=https://api.example.com/lspay/notify
return_url=https://www.example.com/pay/result
channel_extra={"channel_user":"6666000180287572","pay_data_type":"pay_url"}
```

响应 `data`：`pay_order_id`、`mch_order_no`、`trans_status`、`order_state`（下单后通常为 `1` 支付中）、`pay_info`（收银台链接）、`err_code`、`err_msg`。
前端跳转 `pay_info`；支付结果以支付通知或订单查询为准，`return_url` 只用于展示。
