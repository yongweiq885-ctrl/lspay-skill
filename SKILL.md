---
name: lspay-integration
description: 对接立收通（LSPay，api.lspay.tech）。用户提到立收通、LSPay、lspay、支付、分账、退款、提现或电子账户时自动加载。加载后先让用户到商户控台完成商户号、应用 ID、密钥；配置完成后再选择自动对接或手动指令。手动指令有 $lspay-wx-scan、$lspay-ali-scan、$lspay-account 等。文档和示例里的商户号不能当配置。
---

# 立收通（LSPay）支付对接

## 安装后先配置，配完再选下一步

加载本 skill 后按这个顺序说，不要跳步，也不要先写支付代码。

1. 配置还没齐时，只做第一步。告诉用户：商户号 `mch_no`、应用 ID `app_id`、应用密钥 `md5_key` 要登录立收通商户控台，在应用信息里查看。按 [test-account.md](test-account.md) 创建空模板。文档、示例、签名测试数据里的商户号不能写入配置。然后停下来等用户填写。
2. 三项都已写进环境变量或本地 `config.json` 后，明确告诉用户：配置已完成，可以进行下一步。下一步可以对接微信扫码、支付宝，或电子账户等功能接口。
3. 接着让用户选择对接方式，二选一：
   - 自动：用户直接说要做的功能，例如「对接微信扫码」。按该功能实现，并遵守本文件的协议规则。
   - 手动：列出下面的指令后停住。输入对应指令使用。

| 指令 | 功能 |
| --- | --- |
| `$lspay-setup` | 重新初始化商户号、应用 ID、密钥 |
| `$lspay-wx-scan` | 微信扫码 `WX_PUB` |
| `$lspay-wx-lite` | 微信小程序 `WX_LITE` |
| `$lspay-wx-h5` | 微信 App / H5 `WX_LITE_H5` |
| `$lspay-wx-jump` | 自有小程序跳收银台 `WX_LITE_JUMP` |
| `$lspay-wx-bar` | 微信付款码 `WX_BAR` |
| `$lspay-ali-scan` | 支付宝扫码 `ALI_PUB` |
| `$lspay-ali-qr` | 支付宝外拉起收银台 `ALI_QR` |
| `$lspay-ali-h5` | 支付宝 App / H5 `ALI_LITE_H5` |
| `$lspay-ali-bar` | 支付宝付款码 `ALI_BAR` |
| `$lspay-unionpay` | 云闪付 |
| `$lspay-quickpay` | 银行卡快捷支付 |
| `$lspay-order` | 订单查询、退款、通知 |
| `$lspay-division` | 实时分账、延时分账、交易确认 |
| `$lspay-account` | 电子账户开户、业务开通、变更、查询 |
| `$lspay-balance` | 余额查询、提现、结算查询 |

## 工作流程

复制这份清单并逐项完成：

```text
- [ ] 1. 初始化商户配置
- [ ] 2. 收集对接信息
- [ ] 3. 选择实现方式（官方 SDK 或自建客户端）
- [ ] 4. 实现签名并通过测试数据
- [ ] 5. 实现业务接口
- [ ] 6. 实现异步通知
- [ ] 7. 按“上线检查”逐项核对
```

**1. 初始化商户配置**：见上一节和 [test-account.md](test-account.md)。

**2. 收集对接信息**。先读项目代码推断，推断不出来再问用户：

- 后端语言和框架；前端形态（PC 网页、H5、公众号、小程序、App、线下收银）。
- 收款场景，按下方“场景与 way_code”确定支付方式。
- 是否分账：不分账、实时分账、延时分账、余额支付。分账接收方要先开电子账户。
- 公网可访问的 `notify_url`。

**3. 选择实现方式**。优先用官方 SDK（[GitHub 仓库](https://github.com/yongweiq885-ctrl/lspay-SDK)，PHP / Java / Python / Go / C# / UniApp），见 [sdk.md](sdk.md)。项目不方便引入 SDK 时，按 [signing.md](signing.md) 的最小客户端写一个封装类（签名 + 公共参数 + POST），业务代码只调用这个类。

**4. 签名自测**。新写的签名函数必须通过 [signing.md](signing.md) 里的三组测试数据。调试工具：

```bash
python scripts/lspay_sign.py selftest
python scripts/lspay_sign.py sign --key "$LSPAY_MD5_KEY" --json params.json
python scripts/lspay_sign.py verify --key "$LSPAY_MD5_KEY" --form "<通知原文>"
```

**5. 实现业务接口**。按需读取对应参考文件：

| 需求 | 参考 |
| --- | --- |
| 下单、查询、退款、支付/退款通知 | [payment.md](payment.md) |
| 微信小程序内支付 | [payment.md](payment.md) 的「微信小程序」 |
| 微信或支付宝 App / H5 跳转收银台 | [payment.md](payment.md) 的「间连 App / H5」 |
| 自有微信小程序跳立收通收银台 | [payment.md](payment.md) 的「微信小程序跳收银台」 |
| 实时/延时分账、交易确认、转账、余额支付 | [division.md](division.md) |
| 电子账户开户、业务开通、余额、提现、结算 | [account.md](account.md) |
| 银行卡快捷支付（绑卡、短信确认） | [quickpay.md](quickpay.md) |

**6. 实现异步通知**，规则见下方“异步通知”。

**7. 上线前**按“上线检查”逐项核对。

## 协议规则（必须遵守）

- **网关**：`https://api.lspay.tech/{path}`，`POST`，`Content-Type: application/x-www-form-urlencoded;charset=utf-8`，响应为 JSON。
- **公共参数**（每个请求都带）：`mch_no`、`app_id`、`req_time`（13 位毫秒时间戳）、`version=1.0`、`sign_type=MD5`、`sign`。`md5_key` 只用于签名，不放进请求体。
- **签名**：去掉 `sign` 和空值 → 按键名 ASCII 升序 → `k=v&k=v`（不做 URL 编码）→ 末尾加 `&key={md5_key}` → MD5 → 大写。
- **`channel_extra`** 是 JSON **字符串**：先序列化一次，同一个字符串既参与签名又放进表单。统一下单**必传**，没有业务字段时至少传 `{}`，一般写明 `pay_data_type`。
- **`pay_data_type=cashier`**：网关返回收银台 HTML，不返回 JSON，不能由服务端调用接口。服务端只签名，输出自动提交的表单，浏览器直接跳到立收通收银台，用户无需再点击。见 [payment.md](payment.md) 的「cashier 收银台」。
- **金额**：下单、退款、分账、转账、余额支付都用**整数分**；提现金额和提现/结算查询结果用**元字符串**（如 `"99.99"`）。全程不用浮点数运算，元和分的换算用字符串或十进制库。
- **单号**：`mch_order_no`、`mch_refund_no`、`order_id`、`order_no` 都由商户生成，唯一，最长 30 字符。
- **响应判断**：`status == 200` 只表示接口调用成功，业务结果看 `data` 里的 `trans_status`、`order_state`、`state`。`data` 可能是对象，也可能是 JSON 字符串；开户、绑卡、余额查询等接口可能直接返回扁平业务字段。三种格式都要兼容。同步响应里的 `sign` 不需要验签。
- **电子账户**：开户、业务开通、业务变更的 `way_code` 固定 `APPLY`，成功是 `trans_status == "S"`。用户查询的 `trans_status` 和 `channel_status` 都不能用来判断开户是否成功，见 [account.md](account.md)。
- **最终状态**：以验签后的异步通知或主动查询为准，不以前端跳转或同步响应为准。
- **不自动重试资金类请求**（下单、退款、提现、转账、余额支付、交易确认）。超时或网络错误后用原单号查询结果，再决定是否用**同一单号**重试。
- **密钥只在服务端**：小程序、App、H5 前端只调用自己的后端接口，不能持有 `md5_key`，也不能直连立收通网关。

## 场景与 way_code

立收通默认开通**间连**。下面标了「直连」的代码是官方原生直连接口，接入前必须先确认商户的收单模式是直连；没确认就用对应的间连代码。

| 场景 | `way_code` | `channel_extra` | 前端拿到 `pay_info` 后 |
| --- | --- | --- | --- |
| 支付宝线上扫码（推荐，风控更少） | `ALI_PUB` | 扫码传 `pay_data_type`，间连可自动取 `buyer_id`；服务号或小程序内直接唤起仍传 `buyer_id` | 出二维码，或在支付宝内打开支付链接。支付宝外面拿到的链接不能直接拉起收银台 |
| 支付宝间连扫码，或要在支付宝外拉起收银台 | `ALI_QR` | `pay_data_type` | 出二维码，或把支付链接包成 H5。App、网页等支付宝外环境可以拉起收银台 |
| 支付宝条码，扫码枪反扫 | `ALI_BAR` | `auth_code` | 无页面，下单后查询结果 |
| 商户 App 或 H5 唤起支付宝 | `ALI_LITE_H5` | App 跳转时传 `app_schema`，值带 `://` | 只用 schema 打开返回的 `jump_url`。见 [payment.md](payment.md) 的「间连 App / H5」 |
| 支付宝直连：H5 / 电脑网站 / App / 小程序 | `ALI_H5` / `ALI_PC` / `ALI_APP` / `ALI_LITE` | 小程序传 `buyer_id` | 跳转，或交给支付宝 SDK。仅直连商户 |
| 微信间连：扫码或公众号 | `WX_PUB` | 扫码传 `pay_data_type`，间连可自动取 `openid`；公众号或微信内直接调起仍传 `openid` | 出二维码，或在微信内用支付链接 / JSAPI 调起 |
| 微信小程序内支付 | `WX_LITE` | 必填 `{"openid":"…"}`，见 [payment.md](payment.md) 的「微信小程序」 | 按该节解析 `pay_info` 并调用 `wx.requestPayment` |
| 商户 App 或 H5 唤起微信支付 | `WX_LITE_H5` | `{"pay_data_type":"pay_url"}` | `scheme_code` 无返回按钮。要回到 App，用微信原生 SDK，`path` 拼 `p={pay_order_id}&s=app`。见 [payment.md](payment.md) 的「间连 App / H5」 |
| 连锁、多门店：自有小程序跳立收通收银台 | `WX_LITE_JUMP` | `{}`，需要带用户标识时 `{"openid":"…"}`，见 [payment.md](payment.md) 的「微信小程序跳收银台」 | 用 `pay_info.app_id` 和 `pay_info.path` 跳转立收通收银台小程序 |
| 微信条码，扫码枪反扫 | `WX_BAR` | `auth_code` | 无页面，下单后查询结果 |
| 微信直连：扫码 / App | `WX_NATIVE` / `WX_APP` | 扫码传 `pay_data_type` | 出二维码，或交给微信 SDK。仅直连商户 |
| 云闪付条码，扫码枪反扫 | `YSF_BAR` | `auth_code` | 无页面，下单后查询结果 |
| 云闪付线上（小程序或扫码，推荐） | `YSF_JSAPI` | `pay_data_type`，例如 `{"pay_data_type":"pay_url"}` | 出二维码或跳转 |
| 云闪付只做扫码 | `CUP_QR` | `pay_data_type`，例如 `{"pay_data_type":"code_url"}` | 只出二维码，不要当成跳转支付 |
| 银行卡快捷，自己封装页面 | `BANK_FAST` | 见 [quickpay.md](quickpay.md) | 用返回的支付参数自己做绑卡和短信页 |
| 银行卡快捷收银台 | `BANK_FAST_JUMP` | `pay_data_type`，可加 `channel_user` | 跳转 `pay_info`。用户在立收通页面输入银行卡，银行发短信，系统自动绑卡并支付 |

所有场景都要传 `channel_extra`，上表只列出各场景需要放进去的字段。`channel_user` 来自绑卡确认接口，传入后收银台可以带出该用户已绑定的卡。`pay_data_type` 的取值和前端处理见 [payment.md](payment.md)。商户实际开通了哪些产品不确定时，让用户向立收通确认。

## 接口速查

| 接口 | path |
| --- | --- |
| 统一下单（也用于分账下单、快捷支付申请、余额支付） | `gateway/unifiedorder` |
| 订单查询 | `gateway/query` |
| 申请退款 / 退款查询 | `gateway/refund` / `gateway/refund/query` |
| 延时分账：交易确认 / 确认退款 | `gateway/delaytrans/confirm` / `gateway/delaytrans/confirmrefund` |
| 延时分账：可转余额查询 / 订单转账 | `gateway/delaytrans/unconfirm/query` / `gateway/delaytrans/createtask` |
| 快捷：绑卡申请 / 绑卡确认 / 解绑 | `gateway/quickpay/buckleapply` / `gateway/quickpay/buckleconfirm` / `gateway/quickpay/payunbind` |
| 快捷：短信校验 / 支付确认 | `gateway/quickpay/smscheck` / `gateway/quickpay/payconfirm` |
| 电子账户：开户 / 业务开通 / 业务变更 / 查询 | `gateway/user/personapply` / `personconfirm` / `personmodify` / `query`（均在 `gateway/user/` 下） |
| 余额查询 / 余额提现 | `gateway/user/balance/query` / `gateway/user/balance/withdraw` |
| 提现查询：单笔 / 批量 | `gateway/user/balance/withdraw/single/query` / `gateway/user/balance/withdraw/query` |
| 结算记录查询 | `gateway/user/settlement/query` |

## 状态值

| 字段 | 取值 |
| --- | --- |
| 支付订单 `order_state` / `state` | `0` 生成、`1` 支付中、`2` 成功、`3` 失败、`4` 已撤销、`5` 已退款、`6` 关闭 |
| 退款 `state` | `0` 生成、`1` 退款中、`2` 成功、`3` 失败、`4` 关闭 |
| `trans_status` | `S` 成功、`P` 处理中、`F` 失败 |
| 转账任务 `status` | `PENDING`、`PROCESSING`、`COMPLETED`、`FAILED`、`PARTIAL` |

## 异步通知

- 平台向 `notify_url` 发 `POST`。支付和退款通知是 `multipart/form-data`，转账通知是 `application/x-www-form-urlencoded`，都不是 JSON。下单/退款时不传 `notify_url` 就不会有通知。
- `notify_url` 不能带查询参数，不能要求登录、session 或 CSRF token。在框架里给该路由关闭 CSRF 校验（如 Laravel `VerifyCsrfToken::$except`、Django `@csrf_exempt`、Spring Security `ignoringRequestMatchers`；Go 用 gorilla/csrf 等中间件时，把通知路由注册在中间件之外）。
- **验签**：用收到的全部字段（包括未知的新字段），去掉 `sign` 和空值后签名，用常量时间比较。缺少 `sign` 或验签失败直接拒绝。
- **核对**：`mch_no`、`app_id` 与配置一致；单号、金额、币种与本地记录一致。
- **幂等**：同一通知会重复推送。用唯一键去重（支付用 `pay_order_id + event_type`，退款用 `mch_refund_no + event_type`，转账用 `task_id + status + processed_amount`），已处理过就直接返回成功。
- **应答**：数据库事务提交后，返回 HTTP 200 和纯文本 `ok`（不要带 JSON、HTML 或换行）；失败返回 `fail`，平台会在 0/10/15/20/25/30 秒重试，之后只能在后台手动补发。必须在 3 秒内应答，耗时逻辑放到队列里异步处理。
- **类型识别**：`notify_type == "refund"` 或 `event_type` 以 `refund.` 开头是退款通知；以 `payment` 开头是支付通知；带 `task_id`、`order_no`、`target_amount` 的是转账通知。
- 多商户时每个商户用独立的回调地址，按地址选密钥，不要根据通知里的 `mch_no` 选密钥。
- 前端跳转（`return_url`）只用于展示，不更新订单状态。

## 上线检查

```text
- [ ] 签名实现通过三组测试数据
- [ ] md5_key 只在服务端，从环境变量/密钥管理读取，日志中不输出
- [ ] 金额全程为整数分（提现除外），没有浮点运算
- [ ] 统一下单都传了 channel_extra；用 cashier 时输出自动提交的签名表单直接跳转收银台，服务端没有直接调用接口
- [ ] 单号唯一，有数据库唯一索引
- [ ] 通知：全字段验签 + 核对商户号/金额/单号 + 幂等 + 事务提交后返回 "ok" + 已关闭 CSRF
- [ ] 下单后有兜底：未收到通知时按订单查询补单（如定时任务查询“支付中”超过 N 分钟的订单）
- [ ] 资金类请求超时不盲目重试，先查询
- [ ] 直连代码（ALI_APP / ALI_H5 / ALI_PC / ALI_LITE / WX_APP / WX_NATIVE）已确认商户是直连收单；否则改用间连代码
- [ ] 分账：接收方已开户并完成业务开通；div_amt 总额不超过可分账金额
- [ ] 延时分账订单退款：先交易确认退款，再普通退款
- [ ] 身份证、银行卡、手机号、短信验证码在日志中脱敏
- [ ] 已用用户自己的商户号、应用 ID 和密钥走通“下单 → 支付 → 通知 → 退款 → 退款通知”
```

## 参考文件

- [signing.md](signing.md)：签名规则、测试数据，PHP / Python / Node.js / Java / C# / Go 最小客户端，各框架读取通知字段的方式
- [payment.md](payment.md)：统一下单、`channel_extra`、`pay_info` 处理、订单查询、退款、退款查询、支付与退款通知
- [division.md](division.md)：实时/延时分账、交易确认、确认退款、可转余额、订单转账及通知、余额支付
- [account.md](account.md)：电子账户开户、业务开通/变更、用户查询、余额查询、提现、结算查询
- [quickpay.md](quickpay.md)：快捷支付绑卡、支付申请、短信校验、支付确认、解绑
- [sdk.md](sdk.md)：官方 lspay-sdk（PHP / Java / Python / C# / JS / Go）获取方式、用法、cashier 收银台表单、PHP 调试面板
- [test-account.md](test-account.md)：安装后初始化配置，并引导用户获取商户号、应用 ID 和密钥
- `scripts/lspay_sign.py`：签名与验签调试工具（Python 3.7+，无第三方依赖）
