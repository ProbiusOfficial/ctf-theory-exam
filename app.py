import json
import time
import os
from flask import Flask, render_template, request, session, redirect, url_for, jsonify, Response
from config import SECRET_KEY, EXAM_DURATION
from models import init_db, save_result, get_all_results, get_result_by_token, has_any_result
from utils import load_questions, generate_exam, calculate_score, generate_token, verify_token

app = Flask(__name__)
app.secret_key = SECRET_KEY

# 启动时初始化数据库
init_db()
QUESTIONS = load_questions()
QUESTION_MAP = {q["id"]: q for q in QUESTIONS}

# 读取 FLAG（优先从 /flag 文件读取，否则从环境变量，最后 fallback）
FLAG = "flag{TEST_Dynamic_FLAG}"
if os.path.exists("/flag"):
    try:
        with open("/flag", "r", encoding="utf-8") as f:
            FLAG = f.read().strip()
    except Exception:
        pass
else:
    FLAG = os.environ.get("DASFLAG") or os.environ.get("FLAG") or os.environ.get("GZCTF_FLAG") or FLAG


def get_exam_questions(exam_ids):
    """根据 ID 列表恢复完整题目（含顺序和题号）"""
    exam = []
    for idx, qid in enumerate(exam_ids, start=1):
        q = QUESTION_MAP.get(qid)
        if q:
            q = dict(q)  # 复制，避免修改原数据
            q["exam_idx"] = idx
            exam.append(q)
    return exam


@app.route("/")
def index():
    # 已交卷则锁死首页
    if has_any_result():
        return render_template("locked.html")
    return render_template("index.html")


@app.route("/start", methods=["POST"])
def start():
    # 已交卷则禁止重新开始
    if has_any_result():
        return render_template("locked.html"), 403

    player_name = request.form.get("player_name", "").strip()
    if not player_name:
        return redirect(url_for("index"))

    # 生成试卷，session 中只存轻量化的 ID 列表
    _, exam_ids = generate_exam(QUESTIONS)

    session["player_name"] = player_name
    session["start_time"] = time.time()
    session["exam_ids"] = exam_ids
    session["submitted"] = False

    return redirect(url_for("exam_page"))


@app.route("/exam")
def exam_page():
    if "exam_ids" not in session:
        return redirect(url_for("index"))
    if session.get("submitted"):
        return redirect(url_for("result"))

    exam = get_exam_questions(session["exam_ids"])
    elapsed = time.time() - session["start_time"]
    remaining = max(0, int(EXAM_DURATION - elapsed))

    return render_template("exam.html", exam=exam, remaining=remaining, duration=EXAM_DURATION)


@app.route("/api/time", methods=["POST"])
def api_time():
    """返回剩余时间和是否已超时"""
    if "start_time" not in session:
        return jsonify({"remaining": 0, "expired": True})

    elapsed = time.time() - session["start_time"]
    remaining = max(0, int(EXAM_DURATION - elapsed))
    expired = remaining <= 0

    return jsonify({"remaining": remaining, "expired": expired})


@app.route("/submit", methods=["POST"])
def submit():
    if "exam_ids" not in session or session.get("submitted"):
        return redirect(url_for("result"))

    exam = get_exam_questions(session["exam_ids"])
    answers = {}
    for q in exam:
        qid = str(q["id"])
        # 单选/填空是单个值，多选是列表
        if q["type"] in ("multiple", "judge"):
            vals = request.form.getlist(f"q_{qid}")
            answers[qid] = "".join(sorted(vals))
        else:
            answers[qid] = request.form.get(f"q_{qid}", "").strip()

    # 判分
    score, details = calculate_score(exam, answers)
    elapsed = time.time() - session["start_time"]
    time_spent = int(min(elapsed, EXAM_DURATION))

    # 计算满分
    max_score = len([q for q in exam if q["type"] == "single"]) * 2.0 + \
                len([q for q in exam if q["type"] in ("multiple", "judge")]) * 4.0 + \
                len([q for q in exam if q["type"] == "fill"]) * 2.5

    token = generate_token(score, time_spent, session["player_name"])

    # 保存到数据库
    save_result(
        player_name=session["player_name"],
        score=score,
        max_score=max_score,
        time_spent=time_spent,
        answers=answers,
        exam_questions=exam,
        token=token,
    )

    session["submitted"] = True
    session["token"] = token

    return redirect(url_for("result"))


@app.route("/result")
def result():
    if not session.get("submitted"):
        return redirect(url_for("index"))

    token = session.get("token")
    result_data = get_result_by_token(token)
    if not result_data:
        return "未找到考试记录", 404

    # 从数据库恢复 details
    exam = result_data["exam_questions"]
    answers = result_data["answers"]
    _, details = calculate_score(exam, answers)

    return render_template(
        "result.html",
        player_name=result_data["player_name"],
        score=result_data["score"],
        max_score=result_data["max_score"],
        time_spent=result_data["time_spent"],
        token=token,
        details=details,
        flag=FLAG,
    )


@app.route("/admin")
def admin():
    results = get_all_results()
    return render_template("admin.html", results=results)


@app.route("/api/export")
def api_export():
    """导出 CSV 报告"""
    results = get_all_results()
    import csv
    import io

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["选手姓名", "得分", "满分", "用时(秒)", "用时(分:秒)", "校验值", "提交时间"])

    for r in results:
        m, s = divmod(r["time_spent"], 60)
        writer.writerow([
            r["player_name"],
            r["score"],
            r["max_score"],
            r["time_spent"],
            f"{m:02d}:{s:02d}",
            r["token"],
            r["created_at"],
        ])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=exam_results.csv"},
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
