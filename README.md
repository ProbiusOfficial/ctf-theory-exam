# Hello CTF Theory Exam

> 🚩 A containerized online theory exam platform for CTF competitions.  
> Built for [hello-ctf.com](https://hello-ctf.com) and compatible with mainstream CTF platforms.

[简体中文](#功能特性) | [English](#features)

---

## 功能特性

- **智能组题**：从 8 大知识模块中随机抽取，每位选手试卷各不相同
- **全题型支持**：单选题、多选题、判断题、填空题一站式兼容
- **后端权威计时**：60 分钟倒计时，超时自动交卷，前端无法篡改
- **防篡改校验**：HMAC-SHA256 分数校验值 + 独立校验脚本
- **FLAG 自动发放**：交卷后自动展示 FLAG，完美对接 CTF 平台判题
- **交卷锁死**：一旦交卷，该实例立即锁死，防止重复答题
- **单容器自包含**：零外部依赖，一个镜像就是一个完整考场

## 分值规划

| 题型 | 数量 | 分值 | 小计 | 说明 |
|:---|:---:|:---:|:---:|:---|
| 单选题 | 24 | 2.0 | 48 | 答对得分，答错零分 |
| 多选题 / 判断题 | 8 | 4.0 | 32 | 全对满分，漏选半分，错选零分 |
| 填空题 | 8 | 2.5 | 20 | 支持多个正确答案（`/` 分隔） |
| **合计** | **40** | - | **100** | |

## 快速开始

### 构建镜像

```bash
git clone https://github.com/yourname/hello-ctf-theory.git
cd hello-ctf-theory
docker build -t hello-ctf-theory .
```

### 启动实例

```bash
# 本地测试
docker run -d -p 5000:5000 hello-ctf-theory

# CTF 平台动态部署（传入动态 FLAG）
docker run -d -p 5001:5000 -e FLAG="flag{hello_ctf_theory_xxxx}" hello-ctf-theory
```

### 环境变量

| 变量 | 默认值 | 说明 |
|:---|:---|:---|
| `FLAG` | `flag{TEST_Dynamic_FLAG}` | 选手答完题后获得的 FLAG |
| `DASFLAG` | - | 兼容 DASCTF 平台动态 FLAG |
| `GZCTF_FLAG` | - | 兼容 GZCTF 平台动态 FLAG |
| `SECRET_KEY` | 内置默认值 | Session 与 HMAC 密钥，生产环境建议修改 |
| `EXAM_DURATION` | `3600` | 考试时长（秒） |

## 项目结构

```
hello-ctf-theory/
├── app.py                  # Flask 主应用
├── config.py               # 应用配置
├── models.py               # SQLite 数据模型
├── utils.py                # 组题、判分、HMAC 校验
├── md_to_json.py           # Markdown 题库转 JSON 工具
├── verify_score.py         # 分数真实性校验脚本
├── docker-entrypoint.sh    # 容器入口（FLAG 注入 + 启动）
├── questions.json          # 题库数据（140 题）
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── templates/              # HTML 模板
│   ├── index.html
│   ├── exam.html
│   ├── result.html
│   ├── locked.html
│   └── admin.html
└── static/css/
    └── style.css
```

## 使用流程

1. **开始考试**：访问实例地址，输入姓名/队伍名
2. **答题**：顶部倒计时实时显示，答案自动保存（刷新不丢失）
3. **交卷**：支持手动交卷或超时自动交卷
4. **获取 FLAG**：结果页展示得分、用时、校验值与 **FLAG**
5. **提交 FLAG**：将 FLAG 提交至 CTF 平台完成挑战

## 分数校验

独立脚本验证分数真实性（防止选手本地篡改截图）：

```bash
python verify_score.py <校验值> <分数> <用时(秒)> <选手姓名>

# 示例
python verify_score.py abc123 86.5 2340 Alice
```

## 自定义题库

1. 将你的 Markdown 格式题库放入项目根目录
2. 参照 `CTF理论选拔题.md` 的表格格式编写
3. 运行转换脚本：

```bash
python md_to_json.py
```

4. 重新构建镜像即可

## 兼容性

| CTF 平台 | 支持状态 | 说明 |
|:---|:---:|:---|
| [hello-ctf.com](https://hello-ctf.com) | ✅ | 原生适配 |
| DASCTF | ✅ | 支持 `DASFLAG` 动态注入 |
| GZCTF | ✅ | 支持 `GZCTF_FLAG` 动态注入 |
| 其他 Docker-based 平台 | ✅ | 标准单容器镜像，通用部署 |

## 开源协议

[MIT License](LICENSE)

---

## Features

- **Smart Exam Generation**: Randomly draws from 8 knowledge modules, each player gets a unique paper
- **Full Question Type Support**: Single-choice, multiple-choice, true/false, fill-in-the-blank
- **Server-side Timing**: 60-minute countdown with auto-submission; frontend cannot tamper
- **Anti-tamper Verification**: HMAC-SHA256 score token + standalone verification script
- **Dynamic FLAG**: Automatically displays FLAG after submission, integrates with CTF platforms
- **Instance Lockdown**: Once submitted, the container is locked; no re-examination possible
- **Self-contained Single Container**: Zero external dependencies

## Quick Start

```bash
docker build -t hello-ctf-theory .
docker run -d -p 5000:5000 -e FLAG="flag{hello_ctf_theory_xxxx}" hello-ctf-theory
```

## Acknowledgments

Crafted with ❤️ for the CTF community.  
Official companion project of [hello-ctf.com](https://hello-ctf.com)
