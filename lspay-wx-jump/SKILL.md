---
name: lspay-wx-jump
description: 手动对接立收通自有小程序跳收银台。输入 $lspay-wx-jump 使用。
disable-model-invocation: true
---

# 小程序跳收银台

输入 `$lspay-wx-jump` 使用。凭证不齐时改为执行同级 `lspay-setup` 的规则并停住。

读取同级 `lspay-integration/payment.md` 的「微信小程序跳收银台」。`way_code=WX_LITE_JUMP`。用返回的 `pay_info.app_id` 和 `pay_info.path` 跳转。
