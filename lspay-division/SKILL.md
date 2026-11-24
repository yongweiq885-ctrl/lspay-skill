---
name: lspay-division
description: 手动对接立收通实时分账、延时分账和交易确认。输入 $lspay-division 使用。
disable-model-invocation: true
---

# 分账

输入 `$lspay-division` 使用。凭证不齐时改为执行同级 `lspay-setup` 的规则并停住。接收方要先完成电子账户开户和业务开通。

读取同级 `lspay-integration/division.md`。实时分账 `division_mode=1`。延时分账 `division_mode=2`，之后调用 `gateway/delaytrans/confirm`。确认成功是 `trans_status=S`。分账金额单位是分。
