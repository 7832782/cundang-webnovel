import DefaultTheme from 'vitepress/theme'
import { h } from 'vue'
import { useData } from 'vitepress'
import { volumeOf } from '../volumes'
import './custom.css'

// 自定义布局：每章正文上方显示所属卷（卷名一行，卷总字数一行）
const Layout = {
  setup() {
    const { page, theme } = useData()
    return () => {
      const m = page.value.relativePath.match(/^第(\d+)章([^_]*)_/)
      const vol = m ? volumeOf(Number(m[1])) : undefined
      const volInfo = vol
        ? ((theme.value as any).volumesWithTotal ?? []).find(
            (t: { from: number }) => t.from === vol.from
          )
        : undefined
      return h(DefaultTheme.Layout, null, {
        'doc-before': () =>
          vol
            ? h('div', { class: 'volume-badge' }, [
                h('div', { class: 'volume-name' }, vol.name),
                volInfo
                  ? h('div', { class: 'volume-total' }, volInfo.total + '字')
                  : null
              ])
            : null
      })
    }
  }
}

export default {
  ...DefaultTheme,
  Layout
}
