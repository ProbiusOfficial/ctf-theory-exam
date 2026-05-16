import json
import random
import hmac
import hashlib
import base64
from config import (
    SECRET_KEY,
    SCORE_SINGLE,
    SCORE_MULTIPLE,
    SCORE_FILL,
    SECTIONS_PER_EXAM,
    QUESTIONS_PATH,
)


def load_questions():
    with open(QUESTIONS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_exam(questions):
    """
    从每个章节中按规则抽题：
    - 3 单选
    - 1 多选（将判断题也纳入多选池，因为判断只有2个选项，和多选逻辑一致）
    - 1 填空
    """
    # 按章节分组
    sections = {}
    for q in questions:
        sec = q["section"]
        if sec not in sections:
            sections[sec] = {"single": [], "multiple": [], "fill": []}
        if q["type"] == "single":
            sections[sec]["single"].append(q)
        elif q["type"] in ("multiple", "judge"):
            # 判断题前端表现为2选项多选，逻辑一致
            sections[sec]["multiple"].append(q)
        elif q["type"] == "fill":
            sections[sec]["fill"].append(q)

    exam = []
    for sec_name, pool in sections.items():
        # 单选
        singles = random.sample(pool["single"], SECTIONS_PER_EXAM["single"])
        # 多选（含判断）
        multis = random.sample(pool["multiple"], SECTIONS_PER_EXAM["multiple"])
        # 填空
        fills = random.sample(pool["fill"], SECTIONS_PER_EXAM["fill"])
        exam.extend(singles + multis + fills)

    # 打乱顺序，但保留题号用于展示
    random.shuffle(exam)
    exam_ids = []
    for idx, q in enumerate(exam, start=1):
        q["exam_idx"] = idx
        exam_ids.append(q["id"])

    return exam, exam_ids


def calculate_score(exam_questions, answers):
    """
    判分逻辑
    answers: dict[str, str] 键为题目原始id，值为用户答案
    返回: (score, detail_list)
    """
    score = 0.0
    details = []

    for q in exam_questions:
        qid = str(q["id"])
        user_ans = answers.get(qid, "")
        correct_ans = q["answer"]
        q_type = q["type"]

        detail = {
            "exam_idx": q.get("exam_idx", 0),
            "id": q["id"],
            "section": q["section"],
            "type": q_type,
            "question": q["question"],
            "options": q.get("options", {}),
            "user_answer": user_ans,
            "correct_answer": correct_ans,
            "is_correct": False,
            "got_score": 0.0,
            "full_score": 0.0,
        }

        if q_type == "single":
            detail["full_score"] = SCORE_SINGLE
            if user_ans and user_ans.upper() == correct_ans.upper():
                detail["is_correct"] = True
                detail["got_score"] = SCORE_SINGLE
                score += SCORE_SINGLE

        elif q_type in ("multiple", "judge"):
            detail["full_score"] = SCORE_MULTIPLE
            if not user_ans:
                # 空答得0分
                pass
            else:
                user_set = set(user_ans.upper())
                correct_set = set(correct_ans.upper())
                if user_set == correct_set:
                    detail["is_correct"] = True
                    detail["got_score"] = SCORE_MULTIPLE
                    score += SCORE_MULTIPLE
                elif user_set < correct_set:
                    # 漏选：答了的部分都是对的，但少了
                    detail["got_score"] = SCORE_MULTIPLE / 2
                    score += SCORE_MULTIPLE / 2
                else:
                    # 错选（包含错误选项）
                    pass

        elif q_type == "fill":
            detail["full_score"] = SCORE_FILL
            if user_ans and user_ans.strip():
                # 填空支持多个正确答案，用 / 分隔
                corrects = [a.strip().lower() for a in correct_ans.split("/")]
                if user_ans.strip().lower() in corrects:
                    detail["is_correct"] = True
                    detail["got_score"] = SCORE_FILL
                    score += SCORE_FILL

        details.append(detail)

    return round(score, 2), details


def generate_token(score, time_spent, player_name):
    """生成防篡改校验值"""
    payload = f"{score}|{time_spent}|{player_name}"
    sig = hmac.new(
        SECRET_KEY.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    token = base64.urlsafe_b64encode(sig).decode("utf-8").rstrip("=")
    return token


def verify_token(token, score, time_spent, player_name):
    """校验 token 是否匹配"""
    expected = generate_token(score, time_spent, player_name)
    return hmac.compare_digest(token, expected)
