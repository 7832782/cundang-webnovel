// 分卷定义：改这里即可调整卷名与边界，正文不用动
export interface Volume {
  name: string
  from: number
  to: number
}

export const volumes: Volume[] = [
  { name: '第一卷 · 雪花', from: 1, to: 20 },
  { name: '第二卷 · 重连', from: 21, to: 40 },
  { name: '第三卷 · 双影', from: 41, to: 60 },
  { name: '第四卷 · 深夜', from: 61, to: 80 },
  { name: '第五卷 · 时差', from: 81, to: 100 },
  { name: '第六卷 · 存档', from: 101, to: 120 }
]

export function volumeOf(chapterNo: number): Volume | undefined {
  return volumes.find((v) => chapterNo >= v.from && chapterNo <= v.to)
}
