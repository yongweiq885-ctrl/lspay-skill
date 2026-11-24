---
name: lspay-wx-lite
description: 手动对接立收通微信小程序支付。输入 $lspay-wx-lite 使用。
disable-model-invocation: true
---

# 微信小程序

输入 `$lspay-wx-lite` 使用。凭证不齐时改为执行同级 `lspay-setup` 的规则并停住。

读取同级 `lspay-integration/payment.md` 的「微信小程序」。`way_code=WX_LITE`，`channel_extra` 必填 `openid`。`pay_info` 解析后调用 `wx.requestPayment`。
