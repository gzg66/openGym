# 二开说明（fork 分支）

> 这份仓库是 [`https://github.com/DuarteSantos8/openGym.git`](https://github.com/DuarteSantos8/openGym.git) 的二开分支。
> 上游主分支：`main` ｜ 我们的工作分支：`dev`
> 初始化日期：2026-10-20

## 一句话规则

**上游代码不改结构，我们的改动一律是薄薄一层 patch，叠在上游之上，随时能整体重放。**

## 分支布局

| 分支 | 含义 | 允许的操作 |
|---|---|---|
| `main` | 上游镜像，**永远等于** `upstream/main` | 只允许 fast-forward。**禁止直接提交**（pre-commit 会拒） |
| `dev` | 我们的 patch 层：`{上游基线} + N 个 patch 提交` | 所有二开工作都在这里 |
| `patch/NNN-xxx` | 单个 patch 的独立分支（可选，需要评审/可能推上游时用） | 从 `dev` 切出，合回后删除 |

远程：`upstream` = 原项目（只读），`origin` = 我们自己的 fork。

| 远端 | 地址 | 用途 |
|---|---|---|
| `upstream` | https://github.com/DuarteSantos8/openGym.git | 只 fetch，永不 push |
| `origin` | https://github.com/gzg66/openGym.git | 推 `main` + `dev`（真 fork，服务端已有上游对象） |

`remote.pushDefault=origin`，所以直接 `git push` 就推 fork（`main` 仍追踪 `upstream/main`，便于看落后多少）。

## 一个 patch 长什么样

```
patch(007): fix(conf): 关掉 up.grade.retry 的死循环

目的: 上游重试策略在我们的单机部署下会无限重试
上游: 不适用（私有部署假设），已报 issue #1234
边界: 仅改 config/upstream.yaml 的 3 行 + 新增 ext/retry_guard.py
```

- 编号在 `docs/fork/patches/NNN-<slug>.md`
- 编号表 `docs/fork/PATCHES.md` 是**生成文件**，由 `bash .fork/bin/fork-status.sh --ledger` 重建
- 开新 patch：`bash .fork/bin/fork-new-patch.sh <slug>`

## 日常命令

```bash
bash .fork/bin/fork-check-upstream.sh    # 上游有没有更新（cron 每天跑，退出码 10 = 有更新）
bash .fork/bin/fork-sync.sh --check      # 更新详情 + 冲突面分级
bash .fork/bin/fork-sync.sh --apply      # 真同步：rebase 重放 + range-diff 校验 + 跑测试 + 记台账
bash .fork/bin/fork-status.sh            # patch 清单、龄期、台账缺失
bash .fork/bin/fork-doctor.sh            # 薄层体检（有 FAIL 就别推）
```

## 同步上游（每月照做）

1. `fork-sync.sh --check` 看冲突面（无重叠 = 低风险，>5 文件 = 高风险）
2. 低风险直接 `--apply`；高风险先 `git branch backup/$(date +%F)` 再上
3. 冲突解法记进 [`CONFLICTS.md`](CONFLICTS.md)，同步结果记进 [`SYNC-LOG.md`](SYNC-LOG.md)
4. `fork-doctor.sh` 绿了才推：`git push origin main dev`

## 硬红线

- ❌ 在 `main` 上提交
- ❌ `git merge upstream/main` 进 `dev`（必须 rebase）
- ❌ 一个 patch 里混入格式化/重排/重命名
- ❌ 改了源码但没写 `docs/fork/patches/*.md`
- ❌ 直接改第三方 vendored 目录而不在台账里登记

## 升级大版本（上游 v1 → v3）

不要硬 rebase。做法：
1. `git switch -c next-upstream upstream/main` 冻结旧维护分支
2. 在新分支上按台账逐个 patch **重新实现**（不是重放），能删的删、能换成钩子的换
3. 全绿后 `dev` 改名归档，新分支接任

见 `SYNC-LOG.md` 里的「大版本迁移」记录。
