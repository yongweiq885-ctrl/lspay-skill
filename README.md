# 立收通（LSPay）对接 Skill

让 AI 编程助手（Cursor、Claude Code 等支持 Agent Skills 的工具）按立收通协议完成支付对接：签名、统一下单、分账、快捷支付、电子账户、异步通知和上线检查。本 skill 只依赖协议文档，不依赖任何 SDK。

需要现成的多语言 SDK，见 <https://github.com/yongweiq885-ctrl/lspay-SDK>。

## 目录结构

```text
lspay-integration/   主 skill：协议规则、各业务参考文档、签名调试脚本
lspay-setup/         $lspay-setup 等 16 个手动指令，都依赖同级的 lspay-integration
lspay-wx-scan/
...
```

## 安装

把仓库里的 `lspay-integration` 和全部 `lspay-*` 文件夹复制到 skills 目录，文件夹名保持不变、并列放置。指令文件夹依赖同级的 `lspay-integration`，不要单独复制。

Cursor（全局）：

```bash
# macOS / Linux
git clone https://github.com/yongweiq885-ctrl/lspay-skill.git
mkdir -p ~/.cursor/skills
cp -R lspay-skill/lspay-* ~/.cursor/skills/
```

```powershell
# Windows PowerShell
git clone https://github.com/yongweiq885-ctrl/lspay-skill.git
New-Item -ItemType Directory -Force "$env:USERPROFILE\.cursor\skills" | Out-Null
Copy-Item lspay-skill\lspay-* "$env:USERPROFILE\.cursor\skills\" -Recurse -Force
```

只给某个项目用时，把同样这些文件夹复制到项目里的 `.cursor/skills/`。

不用 git 时，在 GitHub 页面点 Code → Download ZIP，解压后同样复制 `lspay-*` 文件夹。

更新：在 clone 出来的 `lspay-skill` 目录执行 `git pull`，再执行一次上面的复制命令覆盖旧文件。

## 使用

在对话里提到立收通、LSPay、支付、分账、退款、提现或电子账户时，助手会自动加载本 skill。

1. 先引导你到立收通商户控台取商户号 `mch_no`、应用 ID `app_id`、应用密钥 `md5_key`，写入环境变量或本地配置。文档和示例里的商户号不能当配置。
2. 配置完成后，可以直接说要做的功能（例如“对接微信扫码”），也可以输入手动指令：

| 指令 | 功能 |
| --- | --- |
| `$lspay-setup` | 配置商户号、应用 ID 与应用密钥 |
| `$lspay-wx-scan` | 微信扫码及公众号支付 |
| `$lspay-wx-lite` | 微信小程序支付 |
| `$lspay-wx-h5` | 微信 App / H5 支付 |
| `$lspay-wx-jump` | 自有小程序跳转立收通收银台 |
| `$lspay-wx-bar` | 微信付款码 |
| `$lspay-ali-scan` | 支付宝扫码 |
| `$lspay-ali-qr` | 支付宝外拉起收银台 |
| `$lspay-ali-h5` | 支付宝 App / H5 支付 |
| `$lspay-ali-bar` | 支付宝付款码 |
| `$lspay-unionpay` | 云闪付 |
| `$lspay-quickpay` | 银行卡快捷支付 |
| `$lspay-order` | 订单查询、退款与异步通知 |
| `$lspay-division` | 实时分账、延时分账与交易确认 |
| `$lspay-account` | 电子账户开户、业务开通、变更与查询 |
| `$lspay-balance` | 余额查询、提现与结算查询 |

## 主 skill 文件

| 文件 | 内容 |
| --- | --- |
| [SKILL.md](lspay-integration/SKILL.md) | 入口：配置流程、协议规则、场景与 `way_code`、接口速查、异步通知、上线检查 |
| [payment.md](lspay-integration/payment.md) | 统一下单、`channel_extra`、`pay_info`、cashier 收银台、查询、退款、通知 |
| [division.md](lspay-integration/division.md) | 实时/延时分账、交易确认、订单转账、余额支付 |
| [account.md](lspay-integration/account.md) | 电子账户开户、业务开通/变更、余额、提现、结算 |
| [quickpay.md](lspay-integration/quickpay.md) | 银行卡快捷支付 |
| [signing.md](lspay-integration/signing.md) | 签名规则、测试数据、各语言最小客户端 |
| [test-account.md](lspay-integration/test-account.md) | 商户配置初始化 |
| `lspay-integration/scripts/lspay_sign.py` | 签名 / 验签调试工具（Python 3.7+，无第三方依赖） |

签名自测：

```bash
python lspay-integration/scripts/lspay_sign.py selftest
```

## 安全

- `md5_key` 只放在服务端，不要写进代码、日志、前端或 git。
- 本仓库不包含任何真实商户凭证。

## License

[MIT](LICENSE) © 立收通
