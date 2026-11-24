# 使用官方 lspay-sdk

官方 SDK 已封装签名、公共参数、字段校验、日志脱敏和通知解析，优先使用。

## 获取 SDK

源码仓库：<https://github.com/yongweiq885-ctrl/lspay-SDK>（MIT 协议）。目录含 `php/LsPaySdk`、`java/`、`python/lspay`、`csharp/`、`uniapp/lspay`、`go/`、`contracts/endpoints.json`。

各语言包还没有发布到 Packagist、Maven Central、PyPI、NuGet、npm，按下面的方式引用：

```bash
git clone https://github.com/yongweiq885-ctrl/lspay-SDK.git lspay-sdk
```

| 语言 | 引用方式 |
| --- | --- |
| PHP | `require_once 'lspay-sdk/php/LsPaySdk/init.php';`，或在 `composer.json` 里把 `lspay-sdk/php` 配成 `path` 仓库 |
| Java | `cd lspay-sdk/java && mvn install`，再在项目里依赖 `tech.lspay:lspay-sdk-java` |
| Python | `pip install -e lspay-sdk/python` |
| C# | 引用 `lspay-sdk/csharp/src/LsPaySdk/LsPaySdk.csproj` |
| UniApp / Node.js | `require('./lspay-sdk/uniapp/lspay')`，签名只在服务端做 |
| Go | `go.mod` 里 `replace` 到本地目录，见下方「Go 示例」 |

项目里已经拷入过 SDK 目录时，直接用现有目录，不要重复引入。

## 校验规则（与网关保持一致）

- 统一下单 `channel_extra` 必传，不传报 `channel_extra 必填`。
- `pay_data_type=cashier` 不能走普通接口调用，会直接报错，改用下方「cashier 收银台表单」。
- 商户配置为空，或还是示例占位符（`YOUR_*`、`MERCH_B_*` 等）时，示例程序和调试面板会提示“未配置商户信息”，不会带着假商户号去请求网关。
- 注册商户时三项凭证都不能为空。PHP、Java、Python、Go、C# 还会校验 `mch_no` 最长 30、`app_id` 最长 24，`notify_url`、`return_url` 必须是 128 字符以内的 HTTP(S) 地址；UniApp 只校验非空。

## 请求类与接口对照

| 接口 | 请求类 | 说明 |
| --- | --- | --- |
| `gateway/unifiedorder` | `UnifiedOrderRequest` | 下单；分账用 `UnifiedOrderChannelExtra` + `DivisionReceiver` |
| `gateway/unifiedorder` | `QuickPayApplyRequest` | 快捷支付申请 |
| `gateway/unifiedorder` | `BalancePayRequest` | 余额支付；`BalancePayChannelExtra` |
| `gateway/query` | `QueryOrderRequest` | |
| `gateway/refund` | `RefundRequest` | |
| `gateway/refund/query` | `QueryRefundRequest` | |
| `gateway/delaytrans/confirm` | `DelayTransConfirmRequest` | `pay_order_id` 与 `mch_order_no` 二选一。确认成功看 `trans_status == "S"` |
| `gateway/delaytrans/confirmrefund` | `DelayTransConfirmRefundRequest` | |
| `gateway/delaytrans/unconfirm/query` | `DelayTransUnconfirmQueryRequest` | |
| `gateway/delaytrans/createtask` | `DelayTransCreateTaskRequest` | |
| `gateway/quickpay/buckleapply` | `QuickPayBindApplyRequest` | `QuickPayBindChannelExtra` |
| `gateway/quickpay/buckleconfirm` | `QuickPayBindConfirmRequest` | `QuickPayBindConfirmChannelExtra` |
| `gateway/quickpay/smscheck` | `QuickPaySmsCheckRequest` | |
| `gateway/quickpay/payconfirm` | `QuickPayConfirmRequest` | |
| `gateway/quickpay/payunbind` | `QuickPayUnbindRequest` | `QuickPayUnbindChannelExtra` |
| `gateway/user/personapply` | `ElectronicAccountUserOpenRequest` | 自动带 `way_code=APPLY`。开户成功只看响应 `trans_status == "S"` |
| `gateway/user/personconfirm` | `ElectronicAccountBusinessOpenRequest` | 自动带 `way_code=APPLY`。开通成功看 `trans_status == "S"` |
| `gateway/user/personmodify` | `ElectronicAccountBusinessChangeRequest` | 自动带 `way_code=APPLY`。变更成功看 `trans_status == "S"` |
| `gateway/user/query` | `ElectronicAccountUserQueryRequest` | 自动带 `way_code=APPLY`。`trans_status` 只表示查询是否成功，其余是查到的资料 |
| `gateway/user/balance/query` | `BalanceQueryRequest` | |
| `gateway/user/balance/withdraw` | `ElectronicAccountBalanceWithdrawRequest` | |
| `gateway/user/balance/withdraw/single/query` | `ElectronicAccountSingleWithdrawQueryRequest` | |
| `gateway/user/balance/withdraw/query` | `ElectronicAccountBatchWithdrawQueryRequest` | |
| `gateway/user/settlement/query` | `ElectronicAccountSettlementQueryRequest` | |

每个请求类都有对应的 `XxxResponse`，提供 `isSuccessful()` / `isPaid()` 等业务判断方法。
各语言的命名风格不同（PHP/Java/JS 用 setter 链，Python 用构造参数，C# 用对象初始化器，Go 用结构体字面量），以对应语言目录下的 README 和 demo 为准。

## 调用入口

| 操作 | PHP | Java | Python | C# | JS / UniApp | Go |
| --- | --- | --- | --- | --- | --- | --- |
| 注册商户 | `LsPay::init($cfg, true, 'default')` | `LsPay.init("default", cfg)` | `LsPay.init("default", MerConfig(...))` | `new LsPayOptions().AddMerchant("default", cfg)` | `LsPay.init('default', new MerConfig({...}))` | `client, err := lspay.NewClient(cfg)` |
| 发请求 | `(new LsPayClient('default'))->postRequest($req)` | `LsPayClient.execute(req, "default")` | `LsPayClient.execute(req, "default")` | `await client.PostAsync(req)` | `await LsPayClient.execute(req, 'default')` | `client.UnifiedOrder(ctx, req)` 等同名方法 |
| 结果 | `$resp->isError()` / `getData()` | `resp.isError()` / `getData()` | `resp.is_error()` / `get_data()` | `resp.IsError` / `resp.Data` | `resp.isError()` / `getData()` | `resp.Err()` / `resp.Data()` |
| 解析通知 | `LsPayNotify::fromGlobals('default')` | `LsPayNotify.parse(map, "default")` | `LsPayNotify.parse(form)` | `LsPayNotify.Parse(form, cfg)` | `LsPayNotify.parse(params, 'default')` | `lspay.ReadNotifyForm(r)` + `client.ParseNotify(form)` |
| 通知应答 | `LsPayNotify::successResponse()` | `LsPayNotify.successResponse()` | `LsPayNotify.success_response()` | `LsPayNotify.SuccessResponse` | `LsPayNotify.successResponse()` | `lspay.NotifySuccessResponse` |
| cashier 表单 | `$client->buildCashierForm($req)` / `renderCashierForm($req)` | `LsPayClient.buildCashierForm(req)` → `form.toHtml()` | `LsPayClient.build_cashier_form(req)` → `form.to_html()` | `client.BuildCashierForm(req)` → `form.ToHtml()` | `LsPayClient.buildCashierForm(req)` → `form.toHtml()` | `client.BuildCashierForm(req)` → `form.HTML()` |

PHP 配置可以传数组、JSON 文件路径，也可以用 `LSPAY_MCH_NO` 等环境变量覆盖。多商户时每个商户注册一个 profile，回调地址按 profile 分开（不要用通知里的 `mch_no` 去选密钥）。

Go 没有全局 profile，多商户时每个商户一个 `Client`，同样按回调地址选 `Client`。`lspay.LoadConfig(path)` 读 JSON 配置并用 `LSPAY_*` 环境变量覆盖，`path` 为空时只读环境变量。

## PHP 示例

```php
use LsPaySdk\core\LsPay;
use LsPaySdk\core\LsPayClient;
use LsPaySdk\enums\PayDataTypeEnum;
use LsPaySdk\enums\WayCodeEnum;
use LsPaySdk\request\DivisionReceiver;
use LsPaySdk\request\UnifiedOrderChannelExtra;
use LsPaySdk\request\UnifiedOrderRequest;

LsPay::init([
    'mch_no' => getenv('LSPAY_MCH_NO'),
    'app_id' => getenv('LSPAY_APP_ID'),
    'md5_key' => getenv('LSPAY_MD5_KEY'),
    'notify_url' => 'https://api.example.com/lspay/notify',
], true, 'default');

$extra = (new UnifiedOrderChannelExtra())
    ->addDivisionReceiver((new DivisionReceiver('RECEIVER_ACCOUNT_NO'))->setDivAmt(10))
    ->setPayDataType(PayDataTypeEnum::CODE_IMG_URL);

$req = (new UnifiedOrderRequest())
    ->setMchOrderNo($orderNo)
    ->setWayCode(WayCodeEnum::WX_NATIVE)
    ->setAmount(100)
    ->setSubject('会员月卡')
    ->setBody('会员月卡 1 个月')
    ->setDivisionMode(1)
    ->setChannelExtra($extra);

$resp = (new LsPayClient('default'))->postRequest($req);
```

通知：

```php
$notify = \LsPaySdk\notify\LsPayNotify::fromGlobals('default');
if ($notify instanceof \LsPaySdk\notify\PaymentNotify && $notify->isSucceeded()) {
    $notify->assertOrder($orderNo, $amountFen, 'cny');
    // 用 $notify->getIdempotencyKey() 去重，事务提交后再返回
}
echo \LsPaySdk\notify\LsPayNotify::successResponse();
```

SDK 不会自动重试资金类请求；非 JSON 响应抛 `LsPayProtocolException`，网络错误抛 `LsPayNetworkException`，字段不合规抛 `LsPayValidationException`。

## cashier 收银台表单

`pay_data_type=cashier` 时用表单方法，不要用 `postRequest` / `execute` / `PostAsync`。表单方法只签名、不发请求，返回 `action`（统一下单地址）、`method`（`POST`）和已签名的全部字段。

```php
$req = (new UnifiedOrderRequest())
    ->setMchOrderNo($orderNo)
    ->setWayCode(WayCodeEnum::ALI_QR)
    ->setAmount(100)
    ->setSubject('会员月卡')
    ->setBody('会员月卡 1 个月')
    ->setChannelExtra(['pay_data_type' => PayDataTypeEnum::CASHIER]);

header('Content-Type: text/html; charset=utf-8');
echo (new LsPayClient('default'))->renderCashierForm($req); // 输出自动提交的表单，浏览器直接跳到收银台
```

`renderCashierForm()` / `toHtml()` / `to_html()` / `ToHtml()` / `HTML()` 输出的表单自带 `submit()` 脚本，作为“去支付”请求的响应返回给浏览器即可直接跳转，用户不需要再点击。前后端分离时，后端返回 `buildCashierForm()` 的结果，前端拿到后立即创建隐藏表单并 `submit()`。完整示例见 SDK 的 `php/LsPayDemo/v1/payment/create/CashierFormDemo.php`。

## PHP 调试面板

SDK 自带调试面板 `php/LsPayDemo/web/index.php`，覆盖全部接口，可以填写参数、查看签名和请求原文。

- 商户配置读 `php/LsPayDemo/config/config.json`（从 `config.example.json` 复制后填写，已被 `.gitignore` 忽略）。未配置时面板顶部提示，不会自动填入假商户号。
- 默认只允许本机访问。远程访问需设置 `LSPAY_DEBUG_PANEL_ALLOW_REMOTE=1`，建议同时设置 `LSPAY_DEBUG_PANEL_TOKEN`，访问时带 `?token=...`。
- **干跑模式**默认开启：只在本地组装、校验和签名，不请求网关，响应区显示的是“模拟响应”。干跑**不能**验证商户号、应用 ID、密钥是否正确。
- 发真实请求：在 `config.json` 里设置 `"debug_panel_allow_live": true`（或环境变量 `LSPAY_DEBUG_PANEL_ALLOW_LIVE=1`），刷新后取消勾选干跑；发送前会弹出确认框。验证凭证建议先用订单查询这类只读接口。
- 统一下单选 `cashier` 时，面板生成签名表单，需要再点“提交跳转收银台”才在新标签页打开。多这一步只是为了防止调试时误下单；商户正式接入时直接输出自动提交的表单，见上一节。

## Go 示例

目录 `lspay-sdk/go`，Go 1.18+，只依赖标准库。模块名 `lspay.tech/lspay-sdk-go` 不能直接 `go get`，先 clone 仓库，再在业务项目的 `go.mod` 里指向本地目录：

```
require lspay.tech/lspay-sdk-go v0.0.0
replace lspay.tech/lspay-sdk-go => ../lspay-sdk/go
```

```go
import lspay "lspay.tech/lspay-sdk-go"

cfg, err := lspay.LoadConfig("") // LSPAY_MCH_NO、LSPAY_APP_ID、LSPAY_MD5_KEY、LSPAY_NOTIFY_URL
if err != nil {
    return err
}
client, err := lspay.NewClient(cfg)
if err != nil {
    return err
}

resp, err := client.UnifiedOrder(ctx, &lspay.UnifiedOrderRequest{
    MchOrderNo:   orderNo,
    WayCode:      lspay.WayCodeWxNative,
    Amount:       100,
    Subject:      "会员月卡",
    Body:         "会员月卡 1 个月",
    DivisionMode: 1,
    ChannelExtra: &lspay.UnifiedOrderChannelExtra{
        PayDataType: lspay.PayDataTypeCodeImgURL,
        DivList:     []lspay.DivisionReceiver{{TransIn: "RECEIVER_ACCOUNT_NO", DivAmt: 10}},
    },
})
if err != nil {
    return err // 网络错误不要直接重试，先用同一单号调 client.QueryOrder
}
if err := resp.Err(); err != nil {
    return err
}
```

通知：

```go
form, err := lspay.ReadNotifyForm(r) // 兼容 multipart/form-data 和 urlencoded
if err != nil {
    return err
}
notify, err := client.ParseNotify(form) // 全字段验签并核对 mch_no、app_id
if err != nil {
    return err
}
if p, ok := notify.(*lspay.PaymentNotify); ok && p.IsSucceeded() {
    if err := p.AssertOrder(orderNo, amountFen, "cny"); err != nil {
        return err
    }
    // 用 p.IdempotencyKey() 去重，事务提交后再应答
}
w.Write([]byte(lspay.NotifySuccessResponse))
```

- `ChannelExtra` 接受构造器结构体、`map[string]interface{}` 或 JSON 对象字符串，走同一套校验。统一下单不传会返回 `channel_extra 必填`。
- 固定的 `way_code`（`BANK_FAST`、`APPLY`、`BALANCE_PAY` 等）由请求自动填写，不能改。
- 业务结果用响应方法判断：`IsPaid()`、`IsRefunded()`、`IsSuccessful()`、绑卡确认 `HasBinding()`。用户查询的 `IsQuerySuccessful()` 不代表开户成功。
- 错误都是 `*lspay.Error`，用 `lspay.IsKind(err, lspay.ErrKindNetwork)` 等区分 config、validation、network、protocol、sign、biz。
