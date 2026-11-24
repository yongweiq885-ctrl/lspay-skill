# 立收通（LSPay）对接 Skill

让 AI 编程助手（Cursor、Claude Code 等支持 Agent Skills 的工具）按立收通协议完成支付对接：签名、统一下单、分账、快捷支付、电子账户、异步通知和上线检查。

配套 SDK：<https://github.com/yongweiq885-ctrl/lspay-SDK>

## 安装

把本仓库放到 skills 目录下，目录名保持 `lspay-integration`。

Cursor（全局）：

```bash
# macOS / Linux
git clone https://github.com/yongweiq885-ctrl/lspay-skill.git ~/.cursor/skills/lspay-integration

# Windows PowerShell
git clone https://github.com/yongweiq885-ctrl/lspay-skill.git "$env:USERPROFILE\.cursor\skills\lspay-integration"
```

只给某个项目用时，放到项目里的 `.cursor/skills/lspay-integration/`。

更新：在该目录执行 `git pull`。

## 使用

在对话里提到立收通、LSPay、支付、分账、退款、提现或电子账户时，助手会自动加载本 skill。

1. 先引导你到立收通商户控台取商户号 `mch_no`、应用 ID `app_id`、应用密钥 `md5_key`，写入环境变量或本地配置。文档和示例里的商户号不能当配置。
2. 配置完成后，可以直接说要做的功能（例如“对接微信扫码”），也可以用手动指令，如 `$lspay-wx-scan`、`$lspay-ali-scan`、`$lspay-account`。完整列表见 [SKILL.md](SKILL.md)。

## 文件

| 文件 | 内容 |
| --- | --- |
| [SKILL.md](SKILL.md) | 入口：配置流程、协议规则、场景与 `way_code`、接口速查、异步通知、上线检查 |
| [payment.md](payment.md) | 统一下单、`channel_extra`、`pay_info`、cashier 收银台、查询、退款、通知 |
| [division.md](division.md) | 实时/延时分账、交易确认、订单转账、余额支付 |
| [account.md](account.md) | 电子账户开户、业务开通/变更、余额、提现、结算 |
| [quickpay.md](quickpay.md) | 银行卡快捷支付 |
| [signing.md](signing.md) | 签名规则、测试数据、各语言最小客户端 |
| [sdk.md](sdk.md) | 官方 SDK 获取方式与用法、PHP 调试面板 |
| [test-account.md](test-account.md) | 商户配置初始化 |
| `scripts/lspay_sign.py` | 签名 / 验签调试工具（Python 3.7+，无第三方依赖） |

签名自测：

```bash
python scripts/lspay_sign.py selftest
```

## 安全

- `md5_key` 只放在服务端，不要写进代码、日志、前端或 git。
- 本仓库不包含任何真实商户凭证。

## License

[MIT](LICENSE) © 立收通
