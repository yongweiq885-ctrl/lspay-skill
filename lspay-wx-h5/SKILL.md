---
name: lspay-wx-h5
description: 手动对接立收通微信 App 或 H5 支付。输入 $lspay-wx-h5 使用。
disable-model-invocation: true
---

# 微信 App / H5

输入 `$lspay-wx-h5` 使用。凭证不齐时改为执行同级 `lspay-setup` 的规则并停住。

读取同级 `lspay-integration/payment.md` 的「间连 App / H5」。`way_code=WX_LITE_H5`。回到 App 时路径使用 `p={pay_order_id}&s=app`。
