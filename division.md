# 分账：实时分账、延时分账、余额支付

## 前置条件

每个分账接收方必须先在立收通开户，拿到用户编号 `account_no`（分账时填在 `trans_in`）。
开户流程：用户开户 → 业务开通，见 [account.md](account.md)。开户时的 `division_profit` 是该用户的默认分账比例。

## 选哪种模式

| 需求 | 模式 |
| --- | --- |
| 支付成功后立即按固定规则分钱 | 实时分账：`division_mode=1` |
| 先冻结资金，等确认收货/服务完成再分 | 延时分账：`division_mode=2`，之后调交易确认 |
| 平台内账户之间转账/付款（不走微信支付宝） | 余额支付：`way_code=BALANCE_PAY` |
| 把延时分账订单里未分配的钱转给某个电子账户 | 延时分账订单转账：`gateway/delaytrans/createtask` |

## 下单时分账（实时 / 延时）

仍调用 `gateway/unifiedorder`，参数同普通下单，另加 `division_mode` 和 `channel_extra.div_list`（模式 1、2 时必填且不能为空）。

同一套 `div_list` 也放在延时分账交易确认和退款的 `channel_extra` 里。退款时用来指定从哪些接收方退回。

`div_list` 每项：

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `trans_in` | 是 | 接收方用户编号。由商户控台或用户开户接口创建，分账时填开户返回的 `account_no` |
| `div_amt` | 否 | 分账金额（分），大于 0 的整数。不传时按该用户开户时的 `division_profit` |
| `description` | 否 | 分账说明 |

```json
{
  "div_list": [
    {"trans_in": "350873274291111", "div_amt": 10, "description": "经销商分账"},
    {"trans_in": "35087342028002222", "description": "按比例分账"}
  ],
  "pay_data_type": "code_img_url"
}
```

注意 `channel_extra` 官方限长 256 字符，接收方很多时要控制描述长度。

## 延时分账交易确认 `gateway/delaytrans/confirm`

对 `division_mode=2` 且已支付的订单分配资金。

| 参数 | 必填 | 说明 |
| --- | --- | --- |
| `pay_order_id` / `mch_order_no` | 二选一 | 原支付订单 |
| `order_id` | 是 | 商户确认流水号，String(30)，唯一 |
| `channel_extra` | 否 | `{"div_list":[{"trans_in":"…","div_amt":10,"description":"…"}]}` |

`div_list` 总额不能超过可分账金额 = 原交易金额 − 手续费（手续费按四舍五入保留两位小数，以元计算）。
可以多次确认，直到分完；当前剩余金额看订单查询的 `unconfirm_amount`。

响应 `data`：`trans_status`（`S` 成功、`F` 失败）、`confirm_order_id`、`batch_order_id`、`unconfirm_amount`、`confirmed_amount`、`err_code`、`err_msg`。
`status=200` 只表示调用成功，必须 `trans_status == "S"` 才算确认成功。必须保存响应里的确认流水号 `confirm_order_id`，交易确认退款时要用它。

## 交易确认退款 `gateway/delaytrans/confirmrefund`

把已确认分出去的金额退回商户账户。延时分账订单要给用户退款时，先调本接口，成功后再调普通退款 `gateway/refund`。

| 参数 | 必填 | 说明 |
| --- | --- | --- |
| `confirm_order_id` | 是 | 确认流水号：延时分账交易确认接口 `gateway/delaytrans/confirm` 响应返回的 `confirm_order_id`，String(30)。不是确认请求里商户传的 `order_id` |
| `confirm_refund_no` | 是 | 商户退款流水号，String(30)，唯一 |
| `channel_extra` | 否 | JSON 字符串 |

响应 `data`：`trans_status`、`confirm_order_id`、`confirm_refund_no`、`unconfirm_amount`、`confirmed_amount`、`err_code`、`err_msg`。

## 可转余额查询 `gateway/delaytrans/unconfirm/query`

无业务参数。响应 `data.unconfirm_amount`：所有延时分账订单的未分账总额（分）。

## 延时分账订单转账 `gateway/delaytrans/createtask`

从延时分账订单的未分账资金中，向一个电子账户发起转账任务。平台自动挑选订单凑够金额。

| 参数 | 必填 | 说明 |
| --- | --- | --- |
| `account_no` | 是 | 收款电子账号，String(30) |
| `account_name` | 是 | 收款人姓名，String(30) |
| `order_no` | 是 | 商户流水号，String(30)，唯一 |
| `amount` | 是 | 转账金额（分） |
| `notify_url` | 否 | 转账结果通知地址，String(64) |
| `remark` | 否 | 备注，String(256) |

同步响应 `data.status=PENDING` 只表示任务已创建，还会返回 `task_id`、`selected_orders`、`first_order_time`、`last_order_time`。

### 转账通知

`POST`，`application/x-www-form-urlencoded`，同一任务会随进度多次推送。

| 字段 | 说明 |
| --- | --- |
| `task_id`、`order_no` | 任务号、商户流水号 |
| `mch_no`、`app_id` | 核对与配置一致 |
| `target_amount`、`processed_amount`、`remaining_amount` | 目标、已处理、剩余金额（分） |
| `status` | `PENDING`、`PROCESSING`、`COMPLETED`、`FAILED`、`PARTIAL` |
| `progress` | 进度百分比，如 `65.0` |
| `completed_time` | 完成时间，未完成时为空 |
| `account_no`、`account_name`、`remark` | 收款方信息（账号已脱敏） |
| `sign` | 签名 |

没有 `sign` 或验签失败一律拒绝。所有非空字段（含未知新增字段）参与验签。最终到账金额以 `COMPLETED` 时的 `processed_amount` 为准。
幂等键建议：`task_id + status + processed_amount`（同一任务允许多次进度更新）。

## 余额支付（走 `gateway/unifiedorder`）

电子账户之间用余额付款，资金不经过微信/支付宝。

| 参数 | 值 |
| --- | --- |
| `way_code` | 固定 `BALANCE_PAY` |
| `division_mode` | 固定 `1` |
| `amount` | 订单金额（分） |
| `channel_extra` | `{"trans_out":"出款账户编号","div_list":[{"trans_in":"收款账户编号","div_amt":100}]}` |

其他必填项（`mch_order_no`、`currency`、`subject`、`body`）与普通下单相同。
余额支付中每个 `div_amt` 必填且大于 0，总和不能超过 `amount`。
响应同统一下单，`order_state=2` 表示已支付成功。

```json
{"trans_out":"350873420280024268","div_list":[{"trans_in":"3709180455068368896","div_amt":100},{"trans_in":"3681144962280062976","div_amt":200}]}
```
