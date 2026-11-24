---
name: lspay-wx-scan
description: 手动对接立收通微信扫码支付。输入 $lspay-wx-scan 使用。
disable-model-invocation: true
---

# 微信扫码

输入 `$lspay-wx-scan` 使用。凭证不齐时改为执行同级 `lspay-setup` 的规则并停住。

读取同级 `lspay-integration/SKILL.md` 的协议规则，以及 `payment.md` 的「统一下单」。默认间连：`way_code=WX_PUB`，扫码传 `pay_data_type`。直连 `WX_NATIVE` 必须先确认商户是直连。
