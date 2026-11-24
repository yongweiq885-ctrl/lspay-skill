---
name: lspay-setup
description: 手动初始化立收通商户号、应用 ID 和应用密钥。输入 $lspay-setup 使用。
disable-model-invocation: true
---

# 初始化配置

输入 `$lspay-setup` 使用。

按同级目录 `lspay-integration/test-account.md` 创建空配置。告诉用户这三项只能在立收通商户控台的应用信息里查看。文档和示例里的商户号不能用。三项写好之前停住。写好后告诉用户配置已完成，可以发功能指令，例如 `$lspay-wx-scan`、`$lspay-ali-scan`、`$lspay-account`。
