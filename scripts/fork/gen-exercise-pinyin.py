#!/usr/bin/env python3
"""重建 frontend/src/lib/exercise-pinyin.json（二开 patch(001) 的拼音首字母索引）。

上游每次更新动作库（把新的中文名加进 frontend/src/exercise-names/zh.js）后跑一次：

    pip install --user pypinyin          # 只在生成时需要，不是运行时依赖
    python3 scripts/fork/gen-exercise-pinyin.py

然后 `git add frontend/src/lib/exercise-pinyin.json`，作为 patch(001) 的后续修正提交。

为什么只存首字母：全拼会让这个文件从 ~97KB 涨到 ~253KB，而它是打进主包的
（语言包是懒加载，这个不是）。首字母串走既有的子串匹配，够用。
"""
import json
import re
import sys
from pathlib import Path

try:
    from pypinyin import lazy_pinyin
except ImportError:
    sys.exit("缺少 pypinyin：pip install --user pypinyin")

ROOT = Path(__file__).resolve().parents[2]
NAMES = ROOT / "frontend/src/exercise-names/zh.js"
OUT = ROOT / "frontend/src/lib/exercise-pinyin.json"
CJK = re.compile(r"[\u3400-\u9fff]")


def initials(name: str) -> str:
    out = []
    for ch in name:
        if CJK.match(ch):
            out.append(lazy_pinyin(ch)[0][0].lower())
        elif ch.isalnum():
            out.append(ch.lower())
    return "".join(out)


def _load_names(raw: str) -> dict:
    """解析动作名 JSON；文件被上游改格式时给出可读错误，而不是抛栈。"""
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        sys.exit(f"{NAMES.name} 里的 JSON 解析失败（上游可能改了生成格式）: {e}")
    if not isinstance(data, dict) or not data:
        sys.exit(f"{NAMES.name} 解析出来的不是非空对象，拒绝覆盖索引")
    return data


def main() -> None:
    src = NAMES.read_text(encoding="utf-8")
    m = re.search(r"export default (\{.*\})", src, re.S)
    if not m:
        sys.exit(f"解析失败：{NAMES} 里没找到 `export default {{...}}`")
    names = _load_names(m.group(1))
    data = {k: initials(v) for k, v in names.items() if initials(v)}
    OUT.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"{len(data)} 条 -> {OUT.relative_to(ROOT)} ({OUT.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
