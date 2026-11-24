# 收款：统一下单、查询、退款、通知

下表中 “公共参数” 指 `mch_no`、`app_id`、`req_time`、`version=1.0`、`sign_type=MD5`、`sign`，由客户端自动注入。
`String(30)` 表示最长 30 字符。

## 统一下单 `gateway/unifiedorder`

| 参数 | 必填 | 类型 | 说明 |
| --- | --- | --- | --- |
| `mch_order_no` | 是 | String(30) | 商户订单号，全局唯一 |
| `way_code` | 是 | String(30) | 支付方式，见 SKILL.md 场景表 |
| `amount` | 是 | int | 金额，**分** |
| `currency` | 是 | String(3) | 固定 `cny` |
| `subject` | 是 | String(64) | 商品标题 |
| `body` | 是 | String(256) | 商品描述 |
| `client_ip` | 否 | String(32) | 用户 IPv4 |
| `notify_url` | 否 | String(128) | 异步通知地址。**不传就不会回调** |
| `return_url` | 否 | String(128) | 支付后同步跳转地址 |
| `expired_time` | 否 | int | 订单有效期（秒），默认 7200 |
| `channel_extra` | 是 | String(256) | JSON 字符串，见下。官方 SDK 不传时直接报 `channel_extra 必填` |
| `division_mode` | 否 | int | `0` 不分账（默认）、`1` 实时分账、`2` 延时分账。见 [division.md](division.md) |
| `ext_param` | 否 | String(512) | 商户自定义，回调原样返回 |
| `polling_mode` | 否 | int | 通道轮询：`0` 关闭（默认）、`1` 自然轮询、`2` 权重轮询、`3` 防断链轮询 |

### channel_extra

| way_code | 必填字段 | 示例 |
| --- | --- | --- |
| `WX_LITE` | `openid`，见下方「微信小程序」 | `{"openid":"oUpF8uMuAJO_M2pxb1Q9zNjWeS6o"}` |
| `WX_PUB` 在公众号或微信内支付 | `openid` | `{"openid":"o6BcIwvSiRpfS8e_UyfQNrYuk2LI"}` |
| `ALI_LITE`；`ALI_PUB` 在服务号或支付宝小程序内唤起 | `buyer_id` | `{"buyer_id":"2088702585070844"}` |
| `WX_PUB`、`ALI_PUB`、`ALI_QR`、`WX_NATIVE`、`CUP_QR` 的扫码 | `pay_data_type` | `{"pay_data_type":"code_img_url"}` |
| `WX_BAR`、`ALI_BAR`、`YSF_BAR` | `auth_code`（用户付款码） | `{"auth_code":"134567890123456789"}` |
| `BANK_FAST` | `channel_user`、`channel_card_id` | 见 [quickpay.md](quickpay.md) |
| `BANK_FAST_JUMP` | 无。`channel_user` 可选，用于带出已绑定的卡 | `{"channel_user":"6666000180287572","pay_data_type":"pay_url"}` |
| 分账订单 | `div_list` | 见 [division.md](division.md) |

`pay_data_type` 与 `openid`、`buyer_id`、`auth_code` 同级。不传时接口默认返回 `pay_url`。

上表没有必填字段的支付方式也要传 `channel_extra`：至少传 `{}`，一般直接写明想要的返回类型，例如 `{"pay_data_type":"pay_url"}`。

间连模式下只要传了 `pay_data_type`，接口可以自动获取 `buyer_id` 和 `openid`，商户不必自己收集。直连，或在微信、支付宝客户端内直接调起原生支付时，仍按上表传 `openid` 或 `buyer_id`。

### 示例请求体（签名前）

```text
mch_order_no=ORD202610150001
way_code=WX_PUB
amount=100
currency=cny
subject=会员月卡
body=会员月卡 1 个月
notify_url=https://api.example.com/lspay/notify
channel_extra={"pay_data_type":"code_img_url"}
```

### 响应 `data`

| 字段 | 说明 |
| --- | --- |
| `pay_order_id` | 平台订单号 |
| `mch_order_no` | 商户订单号 |
| `trans_status` | `S` 受理成功、`P` 处理中、`F` 失败 |
| `order_state` | 订单状态（见 SKILL.md 状态表），下单后通常是 `1` 支付中 |
| `pay_data_type` | `pay_info` 的类型 |
| `pay_info` | 发起支付所需数据 |
| `err_code` / `err_msg` | 上游渠道错误 |

### 按 pay_data_type 处理 pay_info

| pay_data_type | 前端处理 |
| --- | --- |
| `pay_url` | 跳转或打开该链接 |
| `cashier` | 立收通统一收银台。**不能由服务端调用接口**，见下方「cashier 收银台」 |
| `code_url` | 用二维码库把内容渲染成二维码 |
| `code_img_url` | 二维码图片地址，直接用 `<img>` 显示 |
| `wxapp`，以及 `WX_LITE` 的 `pay_info` | 微信原生支付参数。公众号用 `WeixinJSBridge.invoke('getBrandWCPayRequest', …)`，小程序见下方「微信小程序」，App 交给微信 SDK |
| `aliapp` / `ysfapp` | 交给支付宝 / 云闪付 App SDK |
| `none` | 无需前端操作（如付款码支付），直接查询结果 |

付款码（`*_BAR`）、快捷支付等场景下单即可能直接成功（`order_state=2`）；其余场景等通知或轮询订单查询。

### cashier 收银台

`pay_data_type=cashier` 时网关直接返回收银台 HTML 页面，不返回 JSON。服务端用 cURL / HTTP 客户端调用会拿到 HTML，按 JSON 解析必然失败（报“响应不是合法 JSON 对象”）。

正确做法：用户在商户页面点“去支付”后，商户服务端返回一个**自动提交**的表单，浏览器直接跳到立收通收银台，用户不需要再点任何按钮。

1. 服务端照常组装统一下单参数，`channel_extra` 写 `{"pay_data_type":"cashier"}`，注入公共参数并签名，**服务端不发请求**。
2. 把签名后的全部字段输出成隐藏表单，`action` 为 `https://api.lspay.tech/gateway/unifiedorder`，`method="POST"`，页面加载后立即用脚本 `submit()`，浏览器随即跳转到收银台。
3. 支付结果仍以异步通知或订单查询为准。

```html
<form id="lspayCashierForm" method="POST" action="https://api.lspay.tech/gateway/unifiedorder">
  <input type="hidden" name="mch_no" value="…">
  <!-- 其余已签名字段，含 channel_extra 和 sign -->
</form>
<script>document.getElementById('lspayCashierForm').submit();</script>
```

前后端分离时，后端只返回 `action` 和已签名字段，前端拿到后立即创建同样的隐藏表单并 `submit()`，同样不需要用户再点一次。

官方 SDK 已封装，见 [sdk.md](sdk.md) 的「cashier 收银台表单」；普通接口调用发 cashier 会直接报错。自建客户端时，把“签名”和“发送”拆成两个函数，表单与接口调用共用同一个签名函数。

SDK 调试面板里需要再点一次“提交跳转收银台”，只是为了防止调试时误下单，正式接入不要照抄这个交互。

签名后的字段里含 `sign`，但不含 `md5_key`，可以交给浏览器。不要把 `md5_key` 输出到页面。

## 微信小程序

对接微信小程序内原生支付时按本节执行，不要改成扫码或公众号流程。

- 仍调用 `gateway/unifiedorder`，`way_code` 固定 `WX_LITE`。签名、金额（分）、`notify_url`、分账模式与统一下单相同。
- `channel_extra` 必填：`{"openid":"…"}`。
- 成功响应的 `data.pay_info` 是 JSON 字符串。先解析，再把 `timeStamp`、`nonceStr`、`package`、`signType`、`paySign` 原样传给 `wx.requestPayment`。`signType` 用解析结果（示例为 `RSA`），不要写死 `MD5`。
- 下单后通常 `order_state=1`（支付中）、`trans_status=S`，支付结果以通知或订单查询为准。

## 间连 App / H5

用立收通小程序收银台，在商户 App 或 H5 里唤起支付宝、微信。不要和直连的 `ALI_APP`、`WX_APP` 混用。返回按钮带回来的参数只给前端参考，支付结果以服务端查询或异步通知为准。

### 支付宝 `ALI_LITE_H5`

- App 只能用 schema 打开下单返回的 `jump_url`。
- 下单入参 `app_schema` 必须带 `://`，例如 `myapp://`。iOS `Info.plist` 和 Android `android:scheme` 注册的 scheme 不要带 `://`。
- `jump_url` 形如 `alipays://platformapi/startapp?...&page=pages/cashier/cashier?p%3D{订单号}%26s%3Dapp`。
- Android 若要在当前页收结果，Activity 用 `singleTop`，在 `onNewIntent()` 里处理。

### 微信 `WX_LITE_H5`

- 仍调用 `gateway/unifiedorder`。`channel_extra` 传 `{"pay_data_type":"pay_url"}` 即可。
- `pay_info` 若是字符串，先按 JSON 解析。字段有 `gh_id`、`path`、`scheme_code`、`pay_url`、`to_lite_url`。
- **scheme_code**：iOS `openURL` 或 Android `ACTION_VIEW` 直接打开。结果页没有返回按钮，不能回到 App。
- **微信原生 SDK**：结果页有返回按钮。SDK 的 appid 用微信开放平台 appid，不是小程序 appid。返回的 `path` 没有参数，拼成 `pages/cashier/cashier?p={pay_order_id}&s=app`。`p` 是订单号，`s=app` 固定。漏了 `p` 会报 `pre_order_id 不可为空`；appid 填错会报 `bad_param`。
- 回到 App 的参数有 `trans_amt`、`req_seq_id`、`source`（固定 `app`；schema 打开时无效）、`errcode`（仅支付宝）、`errmsg`（微信错误原因）。不能当作最终支付结果。
- 苹果系统容易被微信风控拦住，只建议安卓。

## 微信小程序跳收银台

商户自有微信小程序跳到立收通收银台小程序时按本节执行。这是 `WX_LITE_JUMP`，不是小程序内原生支付的 `WX_LITE`，也不是 App / H5 的 `WX_LITE_H5`。

- 仍调用 `gateway/unifiedorder`，`way_code` 固定 `WX_LITE_JUMP`。
- `channel_extra` 必传，没有用户标识时传 `{}`，需要带用户标识时传 `{"openid":"…"}`。
- 响应 `data.pay_info` 是对象，若收到字符串先按 JSON 解析。字段为 `app_id`、`path`（如 `pages/cashier/cashier`）、`scheme_code`。
- 商户小程序用 `app_id` 和 `path` 跳转立收通收银台。
- 下单后通常 `order_state=0`、`trans_status=P`，支付结果以异步通知或订单查询为准。

## 订单查询 `gateway/query`

请求：`pay_order_id` 或 `mch_order_no` 二选一。

响应 `data` 主要字段：

| 字段 | 说明 |
| --- | --- |
| `pay_order_id`、`mch_order_no`、`way_code` | 订单标识 |
| `amount`、`currency` | 金额（分） |
| `state` | 订单状态 |
| `channel_order_no` | 微信/支付宝侧单号 |
| `ext_param` | 原样返回 |
| `add_time`、`success_time` | 10 位秒级时间戳 |
| `mch_fee_amount` | 手续费（分） |
| `division_mode`、`division_state` | 分账模式；分账状态 `0` 未分账、`1` 等待分账、`2` 分账中、`3` 已结束 |
| `unconfirm_amount`、`confirmed_amount` | 延时分账未确认/已确认金额（分） |
| `fund_freeze_stat` | `FREEZE` / `UNFREEZE` |

找不到订单时返回 `{"status":400,"msg":"订单不存在"}`。

## 申请退款 `gateway/refund`

| 参数 | 必填 | 说明 |
| --- | --- | --- |
| `pay_order_id` / `mch_order_no` | 二选一 | 原支付订单 |
| `mch_refund_no` | 是 | 商户退款单号，String(30)，唯一。同一笔退款重试时复用同一个单号 |
| `refund_amount` | 是 | 退款金额（分），不超过可退金额，可部分退款 |
| `currency` | 是 | `cny` |
| `refund_reason` | 是 | String(64) |
| `client_ip`、`notify_url`、`channel_extra`、`ext_param` | 否 | `notify_url` 不传就不会有退款通知。已分账订单退款时，`channel_extra` 可传 `div_list`，见 [division.md](division.md) |

响应 `data`：`refund_order_id`（立收通退款订单号，保存下来供退款查询使用）、`mch_refund_no`、`pay_amount`、`refund_amount`、`state`（`0` 生成、`1` 退款中、`2` 成功、`3` 失败、`4` 关闭）、`channel_order_no`、`err_code`、`err_msg`。

延时分账订单在交易确认之后退款：要先调交易确认退款，再调本接口，见 [division.md](division.md)。

## 退款查询 `gateway/refund/query`

| 参数 | 必填 | 说明 |
| --- | --- | --- |
| `order_refund_id` | 二选一（推荐） | 退款订单号，由立收通生成，即申请退款响应中的 `refund_order_id` |
| `mch_refund_no` | 二选一 | 商户退款单号，由商户生成 |

一般传 `order_refund_id`。申请退款时请求超时、没拿到 `refund_order_id`，再用 `mch_refund_no` 查询。

响应 `data`：`order_refund_id`、`pay_order_id`、`mch_refund_no`、`pay_amount`、`refund_amount`、`currency`、`state`、
`channel_order_no`、`ext_param`、`add_time`、`success_time`（10 位秒级时间戳）、`err_code`、`err_msg`。

## 支付通知

平台向下单时的 `notify_url` 发送 `POST`，`multipart/form-data`。触发时机为订单支付成功。

```text
notify_type=payment.succeeded
event_type=payment.succeeded
pay_order_id=8835508652407259136
mch_no=YOUR_MCH_NO
app_id=YOUR_APP_ID
mch_order_no=229471099691303119
way_code=WX_PUB
amount=100
currency=cny
state=2
client_ip=117.141.171.91
subject=测试商品
body=支付测试
channel_order_no=4500000482202609275453104271
ext_param=
add_time=1790487185
success_time=1790487200
req_time=1790487185050
sign=8930D06A44EE05DAB5E0477E0C1AD289
```

判定支付成功：验签通过 且 `state == 2` 且（`event_type` 为空或等于 `payment.succeeded`）。
同时核对 `mch_no`、`app_id` 与配置一致，`mch_order_no`、`amount`、`currency` 与本地订单一致。
幂等键建议：`pay_order_id + event_type`。

## 退款通知

平台向退款请求的 `notify_url` 发送 `POST`，`multipart/form-data`，退款成功或失败都会通知。

```text
notify_type=refund
event_type=refund.succeeded
pay_order_id=8835508652407259136
mch_no=YOUR_MCH_NO
app_id=YOUR_APP_ID
mch_refund_no=REFUND12345678901
way_code=WX_PUB
pay_amount=100
refund_amount=100
currency=cny
state=2
ext_param=
add_time=2026-09-27 13:40:08
success_time=2026-09-27 13:40:08
req_time=1790487608
sign=DA8B99DF2062FA744F38F941E7F3BB02
```

`state`：`2` 成功、`3` 失败、`4` 关闭；退款通知的时间字段是 `yyyy-MM-dd HH:mm:ss`。
核对 `mch_refund_no`、`refund_amount` 与本地退款记录一致。幂等键建议：`mch_refund_no + event_type`。

## 回调处理骨架（伪代码）

```text
handle_notify(request):
    params = 全部表单字段
    if not verify(params, md5_key):              return 400 "fail"
    if params.mch_no/app_id 与配置不一致:         return 400 "fail"
    type = refund if notify_type == "refund" or event_type 以 "refund." 开头
           payment if notify_type/event_type 以 "payment" 开头
           transfer if 存在 task_id、order_no、target_amount
    开启事务:
        按单号查本地记录并加行锁
        已处理过（幂等键已存在） → 提交事务，return "ok"
        核对金额/币种/单号，不一致 → 回滚，记录告警，return "fail"
        更新状态，写入幂等键
    提交事务
    return 200 纯文本 "ok"
```
