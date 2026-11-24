---
name: lspay-ali-bar
description: 手动对接立收通支付宝付款码。输入 $lspay-ali-bar 使用。
disable-model-invocation: true
---

# 支付宝付款码

输入 `$lspay-ali-bar` 使用。凭证不齐时改为执行同级 `lspay-setup` 的规则并停住。

读取同级 `lspay-integration/payment.md` 的「统一下单」。`way_code=ALI_BAR`，`channel_extra` 必填 `auth_code`。下单后用订单查询确认结果。
