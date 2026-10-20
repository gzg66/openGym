# patch 002: branch-layout

- 开单: 2026-10-20
- 状态: 已合入
- 能不能不改源码做到？**不适用**（工作流改动，不动产品代码）
- 为什么上游不会接受: 纯本地 fork 工作流，与上游无关
- 触及的上游文件: 无（只改 `.fork/config` 和 `docs/fork/`）
- 回滚方式: revert 本 patch 后把分支名改回来（`git branch -m main dev; git branch -m upstream-mirror main`）
- 验证:
  - [x] `fork-doctor` 绿（镜像 `upstream-mirror` == `upstream/main`）
  - [x] `fork-sync --apply` 在产品型布局下可用（skill selftest 场景 D）
  - [x] 重跑 `fork-init.sh` 不重置分支名、不新增提交（skill selftest 场景 D）

## 目的

把「上游镜像 / 我们的产品线」两条分支的名字换过来：`main` 承载产品线，`upstream-mirror` 承载上游镜像。

## 为什么（这是本 patch 的全部价值）

原布局（`main`=镜像、`dev`=patch 层）适合**会向上游提 PR** 的 fork：干净历史方便开 PR，`git diff main` 永远等于我们改了什么。

但本 fork 是**自用产品**，不打算给上游提 PR（openGym 上游无外部协作入口，我们的定制也是产品级）。
于是 A 布局的收益为 0，代价却很实在：

- fork 首页显示 `main`（镜像），访客和我们自己都看不到改动
- 每天在自己的产品上写「不要动 main」
- `dev` 这个名字没有任何语义

B 布局（`main`=产品线、`upstream-mirror`=镜像）保留全部校验能力：

| 判据 | 两种布局是否都成立 |
|---|---|
| 镜像必须等于 `upstream/main` | ✅（`fork-doctor` 检查镜像分支） |
| `git diff 镜像` = 我们改了什么 | ✅ |
| patch 层可整体重放 | ✅ |

判据的依据在 skill 的 `references/layout-and-sync.md`。

## 改动要点

- 分支重命名：`main → upstream-mirror`（镜像），`dev → main`（产品线）
- `.fork/config`：`MIRROR_BRANCH=upstream-mirror`、`INTEGRATION_BRANCH=main`
- `git config fork.mirrorBranch/integrationBranch` 同步（hooks shim 靠它拦镜像分支提交）
- `docs/fork/README.md` 分支表与红线按新布局重写；`docs/fork/DEPLOY.md` 同步
- 远端：推 `main` + `upstream-mirror`，删除旧的 `dev`

## 风险 / 以后要盯的地方

- 备份分支 `backup/pre-branch-rename-*`、`backup/dev-*` 还留着，确认无误后可删
- 布局一旦确定就别再改：每次改名都在改写历史，别人的本地副本都要重来
