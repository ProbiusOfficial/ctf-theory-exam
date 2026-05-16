import os

SECRET_KEY = os.environ.get("SECRET_KEY", "ctf-theory-exam-2026-secret-key-change-me")
EXAM_DURATION = 3600  # 1小时 = 3600秒

# 分值配置
SCORE_SINGLE = 2.0      # 单选每题分值
SCORE_MULTIPLE = 4.0    # 多选每题分值（全对满分，漏选半分，错选0分）
SCORE_FILL = 2.5        # 填空每题分值

# 组题配置
SECTIONS_PER_EXAM = {
    "single": 3,    # 每章节抽3道单选
    "multiple": 1,  # 每章节抽1道多选
    "fill": 1,      # 每章节抽1道填空
}

DATABASE_PATH = os.environ.get("DATABASE_PATH", "/app/data/exam.db")
QUESTIONS_PATH = os.environ.get("QUESTIONS_PATH", "/app/questions.json")
