# patch 001: pinyin-search

- 开单: 2026-10-20
- 状态: 待评审
- 能不能不改源码做到？**不能**。上游 18 个语言包 + 中文动作名/说明都已完整（2258 键同步、
  中文搜索 `卧推` 命中 54 条），但没有「拼音输入」这条路：中文名只有汉字，英文名只有英文。
- 为什么上游不会接受 / 该不该推上游: **可以尝试推上游**（通用增益，非私有部署假设）。
  先在我们的 patch 层跑稳，再挑时机提 PR；合并后本 patch 用 `git rebase --skip` 撤掉。
- 触及的上游文件: `frontend/src/lib/exercises.js`（3 处：1 行 import + 1 个 CJK 常量 + `corpusOf` 里 2 行）
- 新增文件（放我们自己的扩展目录）:
  - `frontend/src/lib/exercise-pinyin.json` — 5632 条动作名的拼音首字母，离线生成（97KB 原始 / 35KB gzip）
  - `frontend/src/lib/pinyin-search.test.js` — 6 条用例
- 上游同类实现/已有 PR: 无（`git log --grep=i18n` 只查到语言包维护相关提交）
- 回滚方式: 单独 revert 本 patch 即可（新增文件 + 3 处小改，无耦合）
- 验证:
  - [x] `npx vitest run src/lib/pinyin-search.test.js` → 6/6 通过
  - [x] 全量 `npx vitest run` → 5063 passed / **3 failed**；这三个
        （`sheets.workout-detail`、`lib/demoSeed`、`lib/workout-at`）是**基线既有失败**：
        UTC+8 环境下按 UTC 假设写的日期断言。已用 `git stash -u` 在干净树上复现，与本 patch 无关。
  - [x] web 镜像重建 → 产物 `assets/exercises-*.js` 内含 `glsxkfwwt`（chunk 1164KB raw / 187KB gzip；
        本 patch 占 +97KB raw / +35KB gzip）
  - [x] 容器 `opengym-fork/web:local` 起来后 `http://127.0.0.1:8080` → 200
  - [ ] `bash .fork/bin/fork-sync.sh --apply` 后仍通过（下次上游同步时确认）
  - [ ] 手工验证：中文界面搜索框输入 `wt` / `sd` / `glsxkfwwt`（等使用者在手机上确认）

## 目的（一句话，写给人看，不是写给编译器看）

中文界面下，手机输入法打拼音比切输入法打汉字快；用拼音首字母就能找到动作，不用记英文名。

## 改动要点

- `corpusOf()` 构建搜索语料时，**仅当动作名含中日韩字符**才追加该动作的拼音首字母串。
  英文界面下名字是英文，`CJK.test(name)` 为 false → 不引入无谓匹配（有测试固定这一条）。
- 索引按 `EXDB` 的 id 生成，自定义动作没有索引 → 自动跳过，不影响用户自建动作。
- 首字母串走既有的子串匹配通道（`entry.s.includes(tok)`），因此 `wt` 命中 `…卧推`、
  `glsxkfwwt` 命中整名；不需要改搜索算法本身。
- 语料缓存按 `getVersion()`（setLang 时自增）失效，切语言后自动重建。

## 数据怎么来的（可重现）

生成脚本随 patch 一起入库：`scripts/fork/gen-exercise-pinyin.py`

```bash
pip install --user pypinyin                      # 只在生成时需要，不是运行时依赖
python3 scripts/fork/gen-exercise-pinyin.py      # 读 zh.js → 写 frontend/src/lib/exercise-pinyin.json
```

- 逐字取 `lazy_pinyin(ch)[0][0]`；非中日韩的字母数字保留，其余丢弃 → `{"1173":"glsxkfwwt", ...}`
- 脚本产物与已提交索引逐字节一致（已验证），因此可安全重跑
- 坏输入（上游改了 `zh.js` 的生成格式）会以退出码 1 报可读错误，不会覆盖索引
- 只存首字母不存全拼：全拼会让文件从 97KB 涨到 253KB，而它是打进主包的（语言包是懒加载）

## 风险 / 以后要盯的地方

- **主包 +35KB(gzip)**。如果以后首屏预算紧，可以把 JSON 改成动态 import，搜索框聚焦时再加载。
- 上游客服 `exercise-names` 由 `scripts/catalogue/build.mjs` 生成；上游更新动作库后，
  新的动作在本索引里缺失（回退到原有的中文/英文匹配，不影响正确性）。**同步上游后需要重跑生成脚本**补齐。
- 多音字：`lazy_pinyin` 取默认读音，个别动作名可能取错（如「单」dan/shan）。不影响可用性，命中失败时可改查英文/中文。
