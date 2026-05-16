#!/usr/bin/env python3
"""
将 CTF理论选拔题.md 转换为结构化的 questions.json
"""
import json
import re

INPUT_FILE = "../CTF理论选拔题.md"
OUTPUT_FILE = "questions.json"


def parse_md(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # 按章节分割，匹配 "## 一、..." 到下一个 "## " 或文件末尾
    section_pattern = re.compile(r"##\s+(.+?)\n(.*?)(?=\n##\s+|\Z)", re.DOTALL)
    sections = section_pattern.findall(content)

    all_questions = []

    for section_title, section_body in sections:
        # 只处理包含题目的章节（跳过"题目说明"、"题型汇总"等非题目章节）
        if "题目说明" in section_title or "题型汇总" in section_title or "参考答案" in section_title or "选拔赛内容" in section_title:
            continue

        # 清理章节标题，去掉 "（第 X–Y 题）"
        section_name = re.sub(r"（第\s*\d+–\d+\s*题）", "", section_title).strip()

        # 提取表格行
        lines = section_body.strip().splitlines()
        for line in lines:
            line = line.strip()
            if not line.startswith("|") or "题号" in line or "|:---:|:---" in line:
                continue

            parts = [p.strip() for p in line.split("|")]
            # 过滤空字符串
            parts = [p for p in parts if p]
            if len(parts) < 4:
                continue

            # parts 结构: [题号, 题型, 题目, 选项A, 选项B, 选项C, 选项D, 正确答案]
            q_id = parts[0]
            q_type_raw = parts[1]
            q_question = parts[2]
            q_answer = parts[-1]

            # 映射题型
            if q_type_raw == "单选":
                q_type = "single"
                options = {
                    "A": parts[3],
                    "B": parts[4],
                    "C": parts[5],
                    "D": parts[6],
                }
            elif q_type_raw == "多选":
                q_type = "multiple"
                options = {
                    "A": parts[3],
                    "B": parts[4],
                    "C": parts[5],
                    "D": parts[6],
                }
            elif q_type_raw == "判断":
                q_type = "judge"
                # 判断题选项固定为 正确/错误
                options = {
                    "A": "正确",
                    "B": "错误",
                }
                # 答案映射: 正确 -> A, 错误 -> B
                if q_answer == "正确":
                    q_answer = "A"
                elif q_answer == "错误":
                    q_answer = "B"
            elif q_type_raw == "填空":
                q_type = "fill"
                options = {}
            else:
                continue

            # 清理填空题答案中的反引号
            if q_type == "fill":
                q_answer = q_answer.strip("`").strip()

            all_questions.append({
                "id": int(q_id),
                "section": section_name,
                "type": q_type,
                "question": q_question,
                "options": options,
                "answer": q_answer,
            })

    return all_questions


def main():
    questions = parse_md(INPUT_FILE)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)
    print(f"共转换 {len(questions)} 道题目，已保存到 {OUTPUT_FILE}")

    # 统计
    stats = {}
    for q in questions:
        sec = q["section"]
        typ = q["type"]
        if sec not in stats:
            stats[sec] = {}
        stats[sec][typ] = stats[sec].get(typ, 0) + 1

    for sec, types in stats.items():
        print(f"  {sec}: {types}")


if __name__ == "__main__":
    main()
