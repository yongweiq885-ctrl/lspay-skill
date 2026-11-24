---
name: lspay-ali-scan
description: 手动对接立收通支付宝扫码支付。输入 $lspay-ali-scan 使用。
disable-model-invocation: true
---

# 支付宝扫码

输入 `$lspay-ali-scan` 使用。凭证不齐时改为执行同级 `lspay-setup` 的规则并停住。

读取同级 `lspay-integration/payment.md` 的「统一下单」。默认间连：`way_code=ALI_PUB`，扫码传 `pay_data_type`。直连 `ALI_H5`、`ALI_PC`、`ALI_APP`、`ALI_LITE` 必须先确认商户是直连。
