---
name: lspay-order
description: 手动对接立收通订单查询、退款和异步通知。输入 $lspay-order 使用。
disable-model-invocation: true
---

# 订单查询、退款、通知

输入 `$lspay-order` 使用。凭证不齐时改为执行同级 `lspay-setup` 的规则并停住。

读取同级 `lspay-integration/payment.md` 的「订单查询」「申请退款」「退款查询」「支付通知」「退款通知」，以及 `SKILL.md` 的「异步通知」。`status=200` 只表示调用成功。支付成功看通知验签后的 `state=2`。
