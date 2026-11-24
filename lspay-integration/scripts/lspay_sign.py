#!/usr/bin/env python3
"""立收通 (LSPay) MD5 签名 / 验签调试工具，仅依赖 Python 3.7+ 标准库。

用法:
  python lspay_sign.py selftest
  python lspay_sign.py sign   --key MD5_KEY --json params.json
  python lspay_sign.py sign   --key MD5_KEY --form "mch_no=1&app_id=2&amount=100"
  python lspay_sign.py verify --key MD5_KEY --form "<urlencoded 通知原文>"
  python lspay_sign.py verify --key MD5_KEY --json notify.json

--json 可传文件路径，也可传 "-" 从标准输入读取。
sign 会打印参与签名的原串（末尾 key 已打码），便于和对方日志逐字比对。
"""
import argparse
import hashlib
import hmac
import json
import sys
from urllib.parse import parse_qsl

VECTORS = [
    ("minimal", {"a": "1", "b": "2"}, "CD9D772610FCC1396431811A0189F50E"),
    (
        "with_empty_and_null",
        {"a": "1", "b": "", "c": "2", "d": None, "e": "3", "sign": "WILL_BE_IGNORED"},
        "6E864E0A8CEB3D618BBD9FAE88A049E1",
    ),
    (
        "unified_order_full",
        {
            "mch_no": "839305812000286",
            "app_id": "A0001",
            "way_code": "WX_PUB",
            "amount": "100",
            "currency": "cny",
            "subject": "测试商品",
            "body": "支付测试",
            "notify_url": "https://www.lspay.tech/lspay/notify",
            "return_url": "https://www.lspay.tech/success",
            "channel_extra": "{\"pay_data_type\": \"code_img_url\"}",
            "req_time": "1779958002449",
            "version": "1.0",
            "sign_type": "MD5",
            "mch_order_no": "0019770760423138",
        },
        "E728465DB08DF8D8672D8C39FE2FC294",
    ),
]
VECTOR_KEY = "JT2025_DEMO_SECRET_KEY"


def to_sign_value(value):
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def sign_string(params, key):
    parts = []
    for k in sorted(params):
        v = params[k]
        if k == "sign" or v is None or v == "":
            continue
        parts.append("%s=%s" % (k, to_sign_value(v)))
    return "&".join(parts + ["key=" + key])


def sign(params, key):
    return hashlib.md5(sign_string(params, key).encode("utf-8")).hexdigest().upper()


def verify(params, key):
    received = str(params.get("sign") or "")
    return bool(received) and hmac.compare_digest(sign(params, key), received.upper())


def load_params(args):
    if args.form is not None:
        return dict(parse_qsl(args.form, keep_blank_values=True))
    if args.json is not None:
        raw = sys.stdin.read() if args.json == "-" else open(args.json, encoding="utf-8").read()
        data = json.loads(raw)
        if not isinstance(data, dict):
            sys.exit("JSON 必须是对象")
        return data
    sys.exit("需要 --json 或 --form")


def cmd_selftest(_args):
    ok = True
    for name, data, expect in VECTORS:
        got = sign(data, VECTOR_KEY)
        passed = got == expect
        ok &= passed
        print("%-22s %s  got=%s expect=%s" % (name, "PASS" if passed else "FAIL", got, expect))
    sys.exit(0 if ok else 1)


def cmd_sign(args):
    params = load_params(args)
    masked = sign_string(params, args.key)[: -len(args.key)] + "***"
    print("sign_string:", masked)
    print("sign:", sign(params, args.key))


def cmd_verify(args):
    params = load_params(args)
    expect = sign(params, args.key)
    received = str(params.get("sign") or "")
    print("received:", received or "(缺少 sign)")
    print("expected:", expect)
    passed = verify(params, args.key)
    print("PASS" if passed else "FAIL")
    sys.exit(0 if passed else 1)


def main():
    parser = argparse.ArgumentParser(description="立收通 MD5 签名调试工具")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selftest").set_defaults(func=cmd_selftest)
    for name, func in (("sign", cmd_sign), ("verify", cmd_verify)):
        p = sub.add_parser(name)
        p.add_argument("--key", required=True, help="商户应用密钥 md5_key")
        p.add_argument("--json", help="JSON 文件路径，或 - 表示标准输入")
        p.add_argument("--form", help="x-www-form-urlencoded 原文")
        p.set_defaults(func=func)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
