# 签名算法与最小客户端

## 签名规则

1. 去掉 `sign` 字段。
2. 去掉值为 `''` 或 `null` 的字段（`0` 要保留）。
3. 剩余字段按参数名 ASCII 升序排序。
4. 拼成 `k1=v1&k2=v2`，**值不做 URL 编码**；对象/数组值先序列化为紧凑 JSON。
5. 末尾追加 `&key={md5_key}`。
6. 对整串（UTF-8）做 MD5，转大写。

`md5_key` 只参与签名，不放进请求体。

### 防止签名错误

- `channel_extra` 先序列化**一次**得到字符串，同一个字符串既用于签名、又放进表单。不要让签名函数和 HTTP 库各自序列化。
- 不要用 `http_build_query` / `URLSearchParams` 生成签名原串（它们会做 URL 编码）。HTTP 请求体可以正常 URL 编码。
- 金额等数字转字符串时用整数形式（`100`，不要用 `100.0`）；不要传布尔值。
- 对方说“签名失败”时，打印签名原串（打码 key）比对，或用 `python scripts/lspay_sign.py sign --key K --json params.json` 生成正确签名对照。

### 测试数据

密钥 `JT2025_DEMO_SECRET_KEY`：

| 输入 | 期望 sign |
| --- | --- |
| `{"a":"1","b":"2"}` | `CD9D772610FCC1396431811A0189F50E` |
| `{"a":"1","b":"","c":"2","d":null,"e":"3","sign":"X"}` | `6E864E0A8CEB3D618BBD9FAE88A049E1` |
| 统一下单完整参数（见下） | `E728465DB08DF8D8672D8C39FE2FC294` |

统一下单完整参数：

```json
{"mch_no":"839305812000286","app_id":"A0001","way_code":"WX_PUB","amount":"100","currency":"cny","subject":"测试商品","body":"支付测试","notify_url":"https://www.lspay.tech/lspay/notify","return_url":"https://www.lspay.tech/success","channel_extra":"{\"pay_data_type\": \"code_img_url\"}","req_time":"1779958002449","version":"1.0","sign_type":"MD5","mch_order_no":"0019770760423138"}
```

新写的签名实现必须先通过这三组数据再接业务。

## 最小客户端

每个实现都包含：签名、验签、发送请求（自动注入公共参数）。请求统一为
`POST https://api.lspay.tech/{path}`，`Content-Type: application/x-www-form-urlencoded;charset=utf-8`，响应为 JSON。
网络超时建议连接 10 秒、读取 30 秒。

下面是最小骨架，接进项目时在发送前补两条校验：

- 统一下单 `gateway/unifiedorder` 的 `channel_extra` 为空就拒绝发送。
- `channel_extra.pay_data_type == "cashier"` 时不发送，改为只注入公共参数并签名，输出自动提交的表单，见 [payment.md](payment.md) 的「cashier 收银台」。所以把“注入公共参数 + 签名”单独做成一个函数，发送和生成表单都调用它。

### PHP (7.4+)

```php
final class LsPayClient
{
    private string $mchNo; private string $appId; private string $key;
    private string $gateway;

    public function __construct(string $mchNo, string $appId, string $md5Key, string $gateway = 'https://api.lspay.tech/')
    {
        $this->mchNo = $mchNo; $this->appId = $appId; $this->key = $md5Key;
        $this->gateway = rtrim($gateway, '/') . '/';
    }

    public static function sign(array $data, string $key): string
    {
        unset($data['sign']);
        $filtered = [];
        foreach ($data as $k => $v) {
            if ($v === '' || $v === null) continue;
            if (is_array($v) || is_object($v)) {
                $v = json_encode($v, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
            }
            $filtered[$k] = (string)$v;
        }
        ksort($filtered, SORT_STRING);
        $buf = '';
        foreach ($filtered as $k => $v) $buf .= $k . '=' . $v . '&';
        return strtoupper(md5($buf . 'key=' . $key));
    }

    public static function verify(array $data, string $key): bool
    {
        return !empty($data['sign'])
            && hash_equals(self::sign($data, $key), strtoupper((string)$data['sign']));
    }

    /** @return array 解码后的完整响应 {status,msg,data,...} */
    public function post(string $path, array $params): array
    {
        foreach ($params as $k => $v) {
            if (is_array($v) || is_object($v)) {
                $params[$k] = json_encode($v, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
            }
        }
        $params = array_merge($params, [
            'mch_no' => $this->mchNo, 'app_id' => $this->appId,
            'req_time' => (string)(int)floor(microtime(true) * 1000),
            'version' => '1.0', 'sign_type' => 'MD5',
        ]);
        $params['sign'] = self::sign($params, $this->key);

        $ch = curl_init($this->gateway . ltrim($path, '/'));
        curl_setopt_array($ch, [
            CURLOPT_POST => true,
            CURLOPT_POSTFIELDS => http_build_query($params),
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_CONNECTTIMEOUT => 10,
            CURLOPT_TIMEOUT => 30,
            CURLOPT_HTTPHEADER => ['Content-Type: application/x-www-form-urlencoded;charset=utf-8'],
        ]);
        $body = curl_exec($ch);
        $err = curl_error($ch);
        $code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        if ($body === false || $code !== 200) {
            throw new RuntimeException("LSPay HTTP error: $code $err");
        }
        $resp = json_decode($body, true);
        if (!is_array($resp)) throw new RuntimeException('LSPay 响应不是 JSON');
        if (isset($resp['data']) && is_string($resp['data'])) {
            $decoded = json_decode($resp['data'], true);
            if (is_array($decoded)) $resp['data'] = $decoded;
        }
        return $resp;
    }
}
```

### Python (3.7+，依赖 `requests`)

```python
import hashlib, hmac, json, time
import requests

class LsPayClient:
    def __init__(self, mch_no, app_id, md5_key, gateway="https://api.lspay.tech/"):
        self.mch_no, self.app_id, self.key = mch_no, app_id, md5_key
        self.gateway = gateway.rstrip("/") + "/"

    @staticmethod
    def _value(v):
        if isinstance(v, (dict, list)):
            return json.dumps(v, ensure_ascii=False, separators=(",", ":"))
        return str(v)

    @classmethod
    def sign(cls, data, key):
        parts = [f"{k}={cls._value(data[k])}" for k in sorted(data)
                 if k != "sign" and data[k] is not None and data[k] != ""]
        raw = "&".join(parts + [f"key={key}"])
        return hashlib.md5(raw.encode("utf-8")).hexdigest().upper()

    @classmethod
    def verify(cls, data, key):
        received = str(data.get("sign") or "")
        return bool(received) and hmac.compare_digest(cls.sign(data, key), received.upper())

    def post(self, path, params):
        body = {k: self._value(v) for k, v in params.items() if v is not None}
        body.update(mch_no=self.mch_no, app_id=self.app_id,
                    req_time=str(int(time.time() * 1000)), version="1.0", sign_type="MD5")
        body["sign"] = self.sign(body, self.key)
        r = requests.post(self.gateway + path.lstrip("/"), data=body, timeout=(10, 30))
        r.raise_for_status()
        resp = r.json()
        if isinstance(resp.get("data"), str):
            try:
                resp["data"] = json.loads(resp["data"])
            except ValueError:
                pass
        return resp
```

### Node.js (18+，内置 fetch；TypeScript 可直接加类型)

```js
const crypto = require('crypto');

class LsPayClient {
  constructor(mchNo, appId, md5Key, gateway = 'https://api.lspay.tech/') {
    Object.assign(this, { mchNo, appId, key: md5Key, gateway: gateway.replace(/\/+$/, '') + '/' });
  }

  static value(v) {
    return typeof v === 'object' ? JSON.stringify(v) : String(v);
  }

  static sign(data, key) {
    const raw = Object.keys(data).sort()
      .filter((k) => k !== 'sign' && data[k] !== '' && data[k] !== null && data[k] !== undefined)
      .map((k) => `${k}=${LsPayClient.value(data[k])}`)
      .concat(`key=${key}`).join('&');
    return crypto.createHash('md5').update(raw, 'utf8').digest('hex').toUpperCase();
  }

  static verify(data, key) {
    if (!data.sign) return false;
    const a = Buffer.from(LsPayClient.sign(data, key));
    const b = Buffer.from(String(data.sign).toUpperCase());
    return a.length === b.length && crypto.timingSafeEqual(a, b);
  }

  async post(path, params) {
    const body = {};
    for (const [k, v] of Object.entries(params)) if (v !== null && v !== undefined) body[k] = LsPayClient.value(v);
    Object.assign(body, {
      mch_no: this.mchNo, app_id: this.appId, req_time: String(Date.now()), version: '1.0', sign_type: 'MD5',
    });
    body.sign = LsPayClient.sign(body, this.key);
    const res = await fetch(this.gateway + path.replace(/^\/+/, ''), {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8' },
      body: new URLSearchParams(body).toString(),
      signal: AbortSignal.timeout(30000),
    });
    if (!res.ok) throw new Error(`LSPay HTTP ${res.status}`);
    const resp = await res.json();
    if (typeof resp.data === 'string') { try { resp.data = JSON.parse(resp.data); } catch (_) {} }
    return resp;
  }
}

module.exports = { LsPayClient };
```

### Java (8+，JSON 解析用项目已有的库)

```java
import java.io.*;
import java.net.*;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.*;

public final class LsPayClient {
    private final String mchNo, appId, key, gateway;

    public LsPayClient(String mchNo, String appId, String md5Key, String gateway) {
        this.mchNo = mchNo; this.appId = appId; this.key = md5Key;
        this.gateway = gateway.replaceAll("/+$", "") + "/";
    }

    /** 值必须已是字符串；channel_extra 先自行序列化为紧凑 JSON 字符串。 */
    public static String sign(Map<String, String> data, String key) {
        StringBuilder sb = new StringBuilder();
        for (Map.Entry<String, String> e : new TreeMap<>(data).entrySet()) {
            String v = e.getValue();
            if ("sign".equals(e.getKey()) || v == null || v.isEmpty()) continue;
            sb.append(e.getKey()).append('=').append(v).append('&');
        }
        sb.append("key=").append(key);
        try {
            byte[] d = MessageDigest.getInstance("MD5").digest(sb.toString().getBytes(StandardCharsets.UTF_8));
            StringBuilder hex = new StringBuilder();
            for (byte b : d) hex.append(String.format("%02X", b));
            return hex.toString();
        } catch (Exception ex) { throw new IllegalStateException(ex); }
    }

    public static boolean verify(Map<String, String> data, String key) {
        String s = data.get("sign");
        return s != null && !s.isEmpty() && MessageDigest.isEqual(
            sign(data, key).getBytes(StandardCharsets.UTF_8),
            s.toUpperCase().getBytes(StandardCharsets.UTF_8));
    }

    /** 返回响应 JSON 原文，由调用方解析。 */
    public String post(String path, Map<String, String> params) throws IOException {
        Map<String, String> body = new HashMap<>(params);
        body.put("mch_no", mchNo); body.put("app_id", appId);
        body.put("req_time", String.valueOf(System.currentTimeMillis()));
        body.put("version", "1.0"); body.put("sign_type", "MD5");
        body.put("sign", sign(body, key));

        StringBuilder form = new StringBuilder();
        for (Map.Entry<String, String> e : body.entrySet()) {
            if (e.getValue() == null) continue;
            if (form.length() > 0) form.append('&');
            form.append(URLEncoder.encode(e.getKey(), "UTF-8")).append('=')
                .append(URLEncoder.encode(e.getValue(), "UTF-8"));
        }
        HttpURLConnection conn = (HttpURLConnection) new URL(gateway + path.replaceAll("^/+", "")).openConnection();
        conn.setRequestMethod("POST");
        conn.setConnectTimeout(10000); conn.setReadTimeout(30000);
        conn.setDoOutput(true);
        conn.setRequestProperty("Content-Type", "application/x-www-form-urlencoded;charset=utf-8");
        try (OutputStream os = conn.getOutputStream()) { os.write(form.toString().getBytes(StandardCharsets.UTF_8)); }
        if (conn.getResponseCode() != 200) throw new IOException("LSPay HTTP " + conn.getResponseCode());
        try (InputStream in = conn.getInputStream(); ByteArrayOutputStream out = new ByteArrayOutputStream()) {
            byte[] buf = new byte[4096]; int n;
            while ((n = in.read(buf)) > 0) out.write(buf, 0, n);
            return new String(out.toByteArray(), StandardCharsets.UTF_8);
        }
    }
}
```

### C# (.NET 6+)

```csharp
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;

public sealed class LsPayClient
{
    private readonly HttpClient _http;
    private readonly string _mchNo, _appId, _key, _gateway;

    public LsPayClient(HttpClient http, string mchNo, string appId, string md5Key, string gateway = "https://api.lspay.tech/")
    {
        _http = http; _mchNo = mchNo; _appId = appId; _key = md5Key;
        _gateway = gateway.TrimEnd('/') + "/";
    }

    /// 值必须已是字符串；channel_extra 先自行序列化为紧凑 JSON 字符串。
    public static string Sign(IReadOnlyDictionary<string, string?> data, string key)
    {
        var parts = data
            .Where(p => p.Key != "sign" && !string.IsNullOrEmpty(p.Value))
            .OrderBy(p => p.Key, StringComparer.Ordinal)
            .Select(p => p.Key + "=" + p.Value);
        var raw = string.Join("&", parts.Append("key=" + key));
        return Convert.ToHexString(MD5.HashData(Encoding.UTF8.GetBytes(raw)));
    }

    public static bool Verify(IReadOnlyDictionary<string, string?> data, string key)
    {
        if (!data.TryGetValue("sign", out var s) || string.IsNullOrEmpty(s)) return false;
        return CryptographicOperations.FixedTimeEquals(
            Encoding.UTF8.GetBytes(Sign(data, key)), Encoding.UTF8.GetBytes(s.ToUpperInvariant()));
    }

    public async Task<JsonDocument> PostAsync(string path, IDictionary<string, string?> parameters, CancellationToken ct = default)
    {
        var body = new Dictionary<string, string?>(parameters)
        {
            ["mch_no"] = _mchNo, ["app_id"] = _appId,
            ["req_time"] = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds().ToString(),
            ["version"] = "1.0", ["sign_type"] = "MD5",
        };
        body["sign"] = Sign(body, _key);
        var form = new FormUrlEncodedContent(body.Where(p => p.Value != null)
            .Select(p => new KeyValuePair<string, string>(p.Key, p.Value!)));
        using var resp = await _http.PostAsync(_gateway + path.TrimStart('/'), form, ct);
        resp.EnsureSuccessStatusCode();
        return JsonDocument.Parse(await resp.Content.ReadAsStringAsync(ct));
    }
}
```

### Go (1.18+，仅标准库)

```go
package lspay

import (
	"bytes"
	"context"
	"crypto/md5"
	"crypto/subtle"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"sort"
	"strconv"
	"strings"
	"time"
)

type Client struct {
	MchNo, AppID, MD5Key string
	Gateway              string       // 默认 https://api.lspay.tech/
	HTTP                 *http.Client // 默认 30 秒超时
}

// Sign 的值必须已是字符串；channel_extra 先自行序列化为 JSON 字符串。
func Sign(data map[string]string, key string) string {
	keys := make([]string, 0, len(data))
	for k, v := range data {
		if k != "sign" && v != "" {
			keys = append(keys, k)
		}
	}
	sort.Strings(keys)
	var b strings.Builder
	for _, k := range keys {
		b.WriteString(k + "=" + data[k] + "&")
	}
	b.WriteString("key=" + key)
	sum := md5.Sum([]byte(b.String()))
	return strings.ToUpper(hex.EncodeToString(sum[:]))
}

func Verify(data map[string]string, key string) bool {
	s := data["sign"]
	return s != "" && subtle.ConstantTimeCompare([]byte(Sign(data, key)), []byte(strings.ToUpper(s))) == 1
}

// Post 返回解码后的完整响应 {status,msg,data,...}。数字是 json.Number，data 为 JSON 字符串时已展开。
func (c *Client) Post(ctx context.Context, path string, params map[string]string) (map[string]any, error) {
	body := map[string]string{}
	for k, v := range params {
		if v != "" {
			body[k] = v
		}
	}
	body["mch_no"], body["app_id"] = c.MchNo, c.AppID
	body["req_time"] = strconv.FormatInt(time.Now().UnixNano()/int64(time.Millisecond), 10)
	body["version"], body["sign_type"] = "1.0", "MD5"
	body["sign"] = Sign(body, c.MD5Key)

	form := url.Values{}
	for k, v := range body {
		form.Set(k, v)
	}
	gateway := c.Gateway
	if gateway == "" {
		gateway = "https://api.lspay.tech/"
	}
	endpoint := strings.TrimRight(gateway, "/") + "/" + strings.TrimLeft(path, "/")
	req, err := http.NewRequestWithContext(ctx, http.MethodPost, endpoint, strings.NewReader(form.Encode()))
	if err != nil {
		return nil, err
	}
	req.Header.Set("Content-Type", "application/x-www-form-urlencoded;charset=utf-8")
	hc := c.HTTP
	if hc == nil {
		hc = &http.Client{Timeout: 30 * time.Second}
	}
	resp, err := hc.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	raw, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}
	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("LSPay HTTP %d", resp.StatusCode)
	}
	out, err := decodeObject(raw)
	if err != nil {
		return nil, fmt.Errorf("LSPay 响应不是 JSON 对象: %w", err)
	}
	if s, ok := out["data"].(string); ok {
		if d, err := decodeObject([]byte(s)); err == nil {
			out["data"] = d
		}
	}
	return out, nil
}

func decodeObject(raw []byte) (map[string]any, error) {
	dec := json.NewDecoder(bytes.NewReader(raw))
	dec.UseNumber()
	var m map[string]any
	if err := dec.Decode(&m); err != nil {
		return nil, err
	}
	if m == nil {
		return nil, fmt.Errorf("不是 JSON 对象")
	}
	return m, nil
}
```

Go 解析响应必须用 `UseNumber()`。默认解码成 `float64` 后，金额和 `order_state` 容易被当成浮点数处理。

`data` 字段可能是 JSON 对象，也可能是 JSON 字符串，C#/Java 调用方解析时两种都要处理（上面的 PHP、Python、Node.js、Go 客户端已展开）。

## 通知验签

通知验签用**收到的全部表单字段**（不要只挑已知字段，平台会新增字段），调用上面的 `verify`。
框架里的取值方式：

| 框架 | 取全部表单字段 |
| --- | --- |
| 原生 PHP | `$_POST` |
| Laravel | `$request->post()` |
| ThinkPHP | `$this->request->post()` |
| Flask | `request.form.to_dict()` |
| Django | `request.POST.dict()` |
| FastAPI | `dict(await request.form())` |
| Express | `multer().none()` 处理 multipart，`express.urlencoded()` 处理 urlencoded，然后读 `req.body` |
| Spring | `@RequestParam Map<String,String> params`（multipart 和 urlencoded 都可用） |
| ASP.NET Core | `Request.Form.ToDictionary(x => x.Key, x => (string?)x.Value.ToString())` |
| Go net/http | multipart 先 `r.ParseMultipartForm(1 << 20)` 再读 `r.MultipartForm.Value`；urlencoded 先 `r.ParseForm()` 再读 `r.PostForm`。每个键取 `v[0]` 组成 `map[string]string` |
| Gin | 同 net/http，用 `c.Request`；或 `c.MultipartForm()` / `c.Request.PostForm` |
