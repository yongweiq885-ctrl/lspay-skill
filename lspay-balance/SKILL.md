---
name: lspay-balance
description: 手动对接立收通余额查询、提现和结算查询。输入 $lspay-balance 使用。
disable-model-invocation: true
---

# 余额、提现、结算

输入 `$lspay-balance` 使用。凭证不齐时改为执行同级 `lspay-setup` 的规则并停住。

读取同级 `lspay-integration/account.md` 的余额查询、余额提现、提现查询和结算记录查询。提现金额和查询结果用元字符串。余额支付见 `division.md`，指令仍用本功能时一并按该节实现。
