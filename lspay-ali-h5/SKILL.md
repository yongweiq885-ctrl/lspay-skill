---
name: lspay-ali-h5
description: 手动对接立收通支付宝 App 或 H5 支付。输入 $lspay-ali-h5 使用。
disable-model-invocation: true
---

# 支付宝 App / H5

输入 `$lspay-ali-h5` 使用。凭证不齐时改为执行同级 `lspay-setup` 的规则并停住。

读取同级 `lspay-integration/payment.md` 的「间连 App / H5」。`way_code=ALI_LITE_H5`。App 跳转时 `app_schema` 要带 `://`，用返回的 `jump_url` 打开。
