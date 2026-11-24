---
name: lspay-unionpay
description: 手动对接立收通云闪付。输入 $lspay-unionpay 使用。
disable-model-invocation: true
---

# 云闪付

输入 `$lspay-unionpay` 使用。凭证不齐时改为执行同级 `lspay-setup` 的规则并停住。

读取同级 `lspay-integration/SKILL.md` 的「场景与 way_code」。线上用 `YSF_JSAPI`。只出二维码用 `CUP_QR`。付款码用 `YSF_BAR`，并传 `auth_code`。
