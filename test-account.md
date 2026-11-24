# 初始化商户配置

配置完成前不要请求立收通网关，也不要写入任何默认商户号、应用 ID 或密钥。

## 哪些不是可用配置

- `接口文档`、README、支付通知示例里的 `mch_no`、`app_id`
- 签名测试数据里的商户号，例如 `839305812000286`
- `config.example.json` 里的 `YOUR_MERCHANT_NO`、`YOUR_APP_ID`、`YOUR_MD5_KEY`
- `config_merchant_b.example.json` 里的 `MERCH_B_MCH_NO`、`MERCH_B_APP_ID`、`MERCH_B_MD5_KEY`
- 旧版示例代码里的 `your_mch_no`、`your_app_id`、`your_md5_key` 等默认值

## 哪些才算已配置

只认下面三类，而且三项都必须非空：

1. 环境变量 `LSPAY_MCH_NO`、`LSPAY_APP_ID`、`LSPAY_MD5_KEY`
2. 用户本机已经填写的服务端配置，例如 `config.json`、`.env`
3. 用户在当前对话里明确发来的商户号、应用 ID 和密钥

有任何一项为空，就创建空模板并停下来，等用户从商户控台取回后再继续。不要从文档里挑一个商户号凑齐。

## 初始化模板

在服务端创建本地配置，三项留空。不要把填好的配置提交进仓库。

```bash
LSPAY_MCH_NO=
LSPAY_APP_ID=
LSPAY_MD5_KEY=
```

使用官方 SDK 时，也可以写成：

```json
{
  "mch_no": "",
  "app_id": "",
  "md5_key": "",
  "notify_url": "",
  "return_url": ""
}
```

PHP Demo 的配置模板在 `lspay-sdk/php/LsPayDemo/config/config.example.json`，里面是占位值。复制为 `config.json` 后在本机填写，`config.json` 已被 `.gitignore` 忽略。多商户时再从 `config_merchant_b.example.json` 复制出 `config_merchant_b.json`。

配置为空或仍是占位值时，SDK 示例程序会报“未配置商户信息，请先配置环境变量 LSPAY_MCH_NO、LSPAY_APP_ID、LSPAY_MD5_KEY”，PHP 调试面板会在顶部提示。看到这类提示就回到本节，让用户补齐配置，不要改用文档里的商户号。

`config.json` 里的 `"debug_panel_allow_live"` 只控制 PHP 调试面板能否发真实请求，默认 `false`，与 SDK 本身无关。

## 凭证与配置项对照

| 配置项 | 环境变量 | 说明 |
| --- | --- | --- |
| 商户号 | `LSPAY_MCH_NO` | 请求字段 `mch_no` |
| 应用 ID | `LSPAY_APP_ID` | 请求字段 `app_id` |
| 应用密钥 | `LSPAY_MD5_KEY` | 只用于签名，对应 `md5_key`，不放进请求体 |

控台里找不到应用时，让用户联系立收通开通应用后再继续。不要替用户生成这三项。

用户把三项发给对话后：

- 写入上面的本地配置或环境变量。
- `md5_key` 只放服务端。小程序、App、H5 不能保存密钥，也不能直连网关。
- 不要把密钥写进代码、日志、前端包或 git。
