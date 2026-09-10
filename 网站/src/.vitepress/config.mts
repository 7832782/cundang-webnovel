import { defineConfig } from 'vitepress'
import { readdirSync, readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { volumes } from './volumes'

const here = dirname(fileURLToPath(import.meta.url))
const repoRoot = resolve(here, '..', '..', '..')

// 自动扫描章节文件，按章号排序
const RE = /^第(\d+)章([^_]*)_(.+)\.md$/
const chapters = readdirSync(resolve(here, '..'))
  .filter((f) => RE.test(f))
  .sort((a, b) => {
    const ma = a.match(RE)
    const mb = b.match(RE)
    return Number(ma[1]) - Number(mb[1]) || ma[2].localeCompare(mb[2], 'zh')
  })

const noOf = (f) => Number(f.match(RE)[1])
const itemText = (f) => {
  const m = f.match(RE)
  return '第' + m[1] + '章' + m[2] + ' ' + m[3]
}

// 正文字数：剥掉 markdown 标记后按非空白字符计
function countChars(content: string): number {
  const text = content
    .replace(/```[\s\S]*?```/g, '')
    .replace(/^\s*#{1,6}\s+.*$/gm, '')
    .replace(/^\s*>\s?/gm, '')
    .replace(/^---+\s*$/gm, '')
    .replace(/!\[([^\]]*)\]\([^)]*\)/g, '$1')
    .replace(/\[([^\]]*)\]\([^)]*\)/g, '$1')
    .replace(/\*\*([^*]+)\*\*/g, '$1')
    .replace(/\*([^*]+)\*/g, '$1')
    .replace(/`([^`]+)`/g, '$1')
  return text.replace(/\s/g, '').length
}

const cache = new Map(chapters.map((f) => [f, countChars(readFileSync(resolve(here, '..', f), 'utf-8'))]))

const volumeTotals = volumes.map((v) => ({
  name: v.name,
  from: v.from,
  to: v.to,
  total: chapters
    .filter((f) => noOf(f) >= v.from && noOf(f) <= v.to)
    .reduce((sum, f) => sum + cache.get(f)!, 0)
}))

const sidebar = volumes
  .map((v) => ({
    text: v.name + '\n' + volumeTotals.find((t) => t.from === v.from)!.total + '字',
    collapsed: false,
    items: chapters
      .filter((f) => noOf(f) >= v.from && noOf(f) <= v.to)
      .map((f) => ({
        text: itemText(f) + ' · ' + cache.get(f) + '字',
        link: '/' + f.replace(/\.md$/, '')
      }))
  }))
  .filter((g) => g.items.length > 0)

export default defineConfig({
  lang: 'zh-CN',
  title: '存档',
  description: '一百二十章长篇·全虚构',
  base: '/cundang-webnovel/',
  outDir: resolve(repoRoot, 'docs'),
  cleanUrls: true,
  head: [['link', { rel: 'icon', href: '/cundang-webnovel/favicon.svg' }]],
  themeConfig: {
    nav: [{ text: '目录', link: '/' }],
    sidebar,
    docFooter: { prev: '上一章', next: '下一章' },
    outline: false,
    search: { provider: 'local' },
    darkModeSwitchLabel: '外观',
    sidebarMenuLabel: '目录',
    returnToTopLabel: '回到顶部',
    lastUpdated: false,
    volumesWithTotal: volumeTotals,
    footer: {
      message: '全虚构作品，人物与情节均与真实个人无关。',
      copyright: '存档'
    }
  } as any
})
