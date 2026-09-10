// 把 正文/ 下的章节同步到 src/（平铺），并清空输出目录 docs/
import { cpSync, rmSync, mkdirSync, readdirSync, statSync, writeFileSync } from 'node:fs'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url))
const repo = join(here, '..')
const src = join(here, 'src')
const book = join(repo, '正文')
const out = join(repo, 'docs')

// 1. 清空上一次的章节源文件与站点输出
for (const f of readdirSync(src)) {
  if (/^第\d+章.*\.md$/.test(f)) rmSync(join(src, f), { force: true })
}
rmSync(out, { recursive: true, force: true })
mkdirSync(out, { recursive: true })

// 2. 正文按章号平铺复制
const walk = (dir) =>
  readdirSync(dir).flatMap((name) => {
    const p = join(dir, name)
    return statSync(p).isDirectory() ? walk(p) : [p]
  })

const chapters = walk(book).filter((p) => p.endsWith('.md'))
const noOf = (p) => Number(p.match(/第(\d+)章/)?.[1] ?? 0)
chapters.sort((a, b) => noOf(a) - noOf(b) || a.localeCompare(b, 'zh'))

for (const p of chapters) cpSync(p, join(src, p.split(/[\\/]/).pop()))

// 3. 章节文件若引用了图片，一并带进 public/图片
const imgFrom = join(book, '图片')
const imgTo = join(src, 'public', '图片')
try {
  rmSync(imgTo, { recursive: true, force: true })
  if (statSync(imgFrom).isDirectory()) cpSync(imgFrom, imgTo, { recursive: true })
} catch {
  /* 没有图片目录就跳过 */
}

writeFileSync(
  join(here, '.last-sync'),
  new Date().toISOString() + '\t' + chapters.length + ' 章\n'
)
console.log('已同步 ' + chapters.length + ' 章到 src/，docs/ 已清空待构建')
