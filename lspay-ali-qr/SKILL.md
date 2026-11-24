---
name: lspay-ali-qr
description: 手动对接立收通支付宝外拉起收银台。输入 $lspay-ali-qr 使用。
disable-model-invocation: true
---

# 支付宝外收银台

输入 `$lspay-ali-qr` 使用。凭证不齐时改为执行同级 `lspay-setup` 的规则并停住。

读取同级 `lspay-integration/payment.md` 的「统一下单」。`way_code=ALI_QR`，传 `pay_data_type`。用于支付宝外拉起收银台。
