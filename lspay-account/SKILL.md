---
name: lspay-account
description: 手动对接立收通电子账户开户、业务开通、变更和查询。输入 $lspay-account 使用。
disable-model-invocation: true
---

# 电子账户

输入 `$lspay-account` 使用。凭证不齐时改为执行同级 `lspay-setup` 的规则并停住。

读取同级 `lspay-integration/account.md`。开户、业务开通、业务变更的 `way_code` 固定 `APPLY`，成功是 `trans_status=S`。用户查询的 `trans_status` 只表示查询是否成功，不能用来判断开户是否成功。
