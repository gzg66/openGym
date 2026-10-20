import { describe, it, expect, beforeAll } from 'vitest'
import { matchExercise, exOr } from './exercises.js'
import { _setLangState } from './i18n-core.js'
import zh from '../locales/zh.js'
import zhNames from '../exercise-names/zh.js'

// 二开 patch(001): 中文界面下用拼音首字母找动作。
// 中文输入法下打 "wt" 比打 "卧推" 快，也比切输入法省事。
// 这条能力上游没有，且完全靠新增数据 + 搜索语料拼接实现，不改上游任何逻辑。
const BENCH = exOr('1173') // 杠铃上斜宽反握卧推
const SQUAT = exOr('1004') // 弹力带深蹲

describe('拼音首字母搜索（中文界面）', () => {
  beforeAll(() => {
    _setLangState('zh', zh, null, zhNames)
  })

  it('用中文名首字母命中动作', () => {
    expect(BENCH.n).toBeTruthy()
    expect(matchExercise(BENCH, 'wt')).toBe(true) // …卧推
    expect(matchExercise(SQUAT, 'sd')).toBe(true) // …深蹲
  })

  it('用整串首字母命中动作', () => {
    // 杠铃上斜宽反握卧推 -> glsxkfwwt
    expect(matchExercise(BENCH, 'glsxkfwwt')).toBe(true)
    expect(matchExercise(BENCH, 'glsxkfwwt.')).toBe(false) // 多余字符不该命中
  })

  it('中文原名仍然有效', () => {
    expect(matchExercise(BENCH, '卧推')).toBe(true)
  })

  it('英文查询不受影响', () => {
    expect(matchExercise(BENCH, 'bench')).toBe(true)
  })

  it('不相关查询不误报', () => {
    expect(matchExercise(BENCH, 'zzzq')).toBe(false)
  })
})

describe('拼音首字母搜索（英文界面）', () => {
  it('英文界面下不额外引入拼音匹配', () => {
    _setLangState('en', null, null, null)
    expect(matchExercise(BENCH, 'wt')).toBe(false)
    _setLangState('zh', zh, null, zhNames) // 还原，避免影响同文件其他用例
  })
})
