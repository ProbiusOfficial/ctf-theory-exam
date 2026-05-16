#!/usr/bin/env python3
"""
分数校验脚本
用法: python verify_score.py <校验值> <分数> <用时(秒)> <选手姓名>
示例: python verify_score.py abc123 86.5 2340 张三
"""
import sys
import hmac
import hashlib
import base64

# 必须与容器内的 SECRET_KEY 一致
DEFAULT_SECRET = "ctf-theory-exam-2026-secret-key-change-me"


def verify_token(token, score, time_spent, player_name, secret=DEFAULT_SECRET):
    payload = f"{score}|{time_spent}|{player_name}"
    sig = hmac.new(
        secret.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    expected = base64.urlsafe_b64encode(sig).decode("utf-8").rstrip("=")
    return hmac.compare_digest(token, expected)


def main():
    if len(sys.argv) < 5:
        print("用法: python verify_score.py <校验值> <分数> <用时(秒)> <选手姓名>")
        print("示例: python verify_score.py abc123 86.5 2340 张三")
        sys.exit(1)

    token = sys.argv[1]
    score = sys.argv[2]
    time_spent = sys.argv[3]
    player_name = sys.argv[4]

    # 支持传入自定义密钥（第5个参数）
    secret = sys.argv[5] if len(sys.argv) > 5 else DEFAULT_SECRET

    ok = verify_token(token, score, time_spent, player_name, secret)

    print("=" * 50)
    print("分数校验结果")
    print("=" * 50)
    print(f"选手姓名 : {player_name}")
    print(f"分数     : {score}")
    print(f"用时(秒) : {time_spent}")
    print(f"校验值   : {token}")
    print("-" * 50)
    if ok:
        print("✅ 校验通过：分数真实有效，未被篡改。")
    else:
        print("❌ 校验失败：分数可能已被篡改，或信息输入有误。")
    print("=" * 50)


if __name__ == "__main__":
    main()
