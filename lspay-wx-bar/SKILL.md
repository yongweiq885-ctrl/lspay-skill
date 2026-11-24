---
name: lspay-wx-bar
description: 手动对接立收通微信付款码。输入 $lspay-wx-bar 使用。
disable-model-invocation: true
---

# 微信付款码

输入 `$lspay-wx-bar` 使用。凭证不齐时改为执行同级 `lspay-setup` 的规则并停住。

读取同级 `lspay-integration/payment.md` 的「统一下单」。`way_code=WX_BAR`，`channel_extra` 必填 `auth_code`。下单后用订单查询确认结果。
