# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个会持续记住你弱点和进步轨迹的 AI 面试训练系统，请通过vibe coding，让这个项目更加完善。目标是让原型开发更快速、迭代更轻松、开发过程更愉快。

---

## 核心机制

### 1. 个性化出题引擎

![TechSpar personalized question generation engine](images/question-generation-engine.png)

TechSpar 不从固定题库随机抽题，而是融合三层信息后生成下一轮问题：

- **Session Context**：简历、JD、知识库、最近训练记录
- **Topic Mastery**：领域掌握度、历史薄弱点、练习轨迹
- **Global Profile**：跨领域强项、弱项、思维模式、沟通风格

结果是：问题更少重复，更贴近真实短板，也更有连续性。

### 2. 训练闭环

![TechSpar training evaluation profile update loop](images/training-loop.png)

每次训练结束后，系统不会只给一句点评，而是继续向后推进：

- 逐题评估回答质量
- 提取薄弱点、强项和行为特征
- 更新领域掌握度与长期画像
- 用 **SM-2** 调度后续复习
- 把这次结果带入下一轮训练

这意味着：**每次训练都会改变下一次训练。**

### 3. 系统架构

![TechSpar system architecture overview](images/system-architecture.png)

TechSpar 不是单页 Demo，而是完整系统：

- 前端：React 19 + React Router v7 + Vite
- 后端：FastAPI + LangGraph 工作流
- 数据层：SQLite、用户隔离目录、长期画像、向量检索
- 外部服务：OpenAI 兼容 LLM、Embedding、DashScope ASR、Qiniu OSS

---

## Vibe Coding 约束规则

### 开发节奏
- **先跑通，再优化**：先用最简单的方案让功能工作，复杂的优化留到后面
- **小步快跑**：每次只做一件事，完成后再做下一件
- **快速验证**：写一点代码就测试，不要等到写了很多才发现问题
- **保留选项**：避免过早做决定，用临时方案先跑起来

### 代码习惯
- **不过度设计**：不要为了"可能的需求"写代码，只为当前需求写代码
- **删除优于修改**：能删掉的代码就不要留着，代码越少问题越少
- **命名即注释**：变量和函数名要自解释，减少不必要的注释
- **复制粘贴要小心**：复制的代码一定要改干净

### 调试策略
- **最小复现**：先找到能触发问题的最小代码示例
- **print 大法**：不确定的时候加个 console.log 比看代码更快
- **注释大法**：不确定哪行出问题就注释掉一半，二分查找
- **先猜后验证**：有个假设再去查，不要漫无目的地看代码

### 重构时机
- **重复出现三次再抽象**：不要第一次就开始抽象，等看到重复模式再说
- **性能问题出现后再优化**：不要提前优化，先让程序跑起来
- **代码难以理解时再重构**：如果能正常工作就先别动

### 项目维护
- **文档只在必要时写**：代码本身要能自解释
- **测试覆盖核心逻辑**：不是所有代码都要测试，核心业务逻辑要测
- **CI/CD 要快**：构建太慢会影响开发节奏，保持在 5 分钟以内

- **快速交付，逐步完善**：先让它工作，再优化。不要在一开始就过度设计。
- **偏好迭代而非规划**：先尝试，测试，再调整。小步快跑，快速反馈。
- **减少样板代码**：自动化重复模式。让代码生成处理繁琐的部分。
- **保持上下文**：这个扩展会保留会话上下文，支持无缝继续工作。
- **失败要可见**：错误和系统状态应该在 UI 中立即清晰显示。



## 约束规则

### Git 工作流
- 频繁小提交 —— 保持提交的原子性
- 提交信息要清晰，说明"为什么"而非"做了什么"
- 每个提交只包含一个逻辑变更

### 代码风格
- 开启 TypeScript strict 模式
- 优先使用显式类型，避免 `any`
- 命名要清晰，不要为了简短而牺牲可读性

### 错误处理
- 绝不静默吞掉错误
- 记录错误时提供足够的上下文便于调试
- 关键失败要立即展示给用户

### 安全
- 绝不提交 API key、token 或密钥
- 敏感数据使用环境变量或 VS Code 的 `SecretStorage`
- API key 应由用户配置，绝不硬编码


## 项目结构

```text
TechSpar/
├── backend/
│   ├── main.py
│   ├── auth.py
│   ├── memory.py
│   ├── vector_memory.py
│   ├── indexer.py
│   ├── spaced_repetition.py
│   ├── migrate.py
│   ├── graphs/
│   │   ├── resume_interview.py
│   │   └── topic_drill.py
│   ├── prompts/
│   └── storage/sessions.py
├── frontend/src/
│   ├── App.jsx
│   ├── contexts/AuthContext.jsx
│   ├── components/
│   ├── pages/
│   └── api/interview.js
├── data/users/{user_id}/
│   ├── profile/profile.json
│   ├── resume/
│   ├── knowledge/
│   └── topics.json
├── docker-compose.yml
├── requirements.txt
├── requirements.local-embedding.txt
└── .env.example
```

---