import re, glob, os, sys

# 时差校验器 —— 配合 设定/09_时距与账目基准表.md 使用
# 局限：句中只写"十点"不带"晚上/下午"时会按上午算，产生假报；输出需人工分返。

OFFSET = {}
for a, b, o in [(1, 55, 0), (56, 61, 7), (62, 63, 8), (64, 66, 7), (67, 69, 7),
                (70, 71, 8), (72, 77, 7), (78, 83, 7), (84, 88, 8),
                (89, 95, 7), (96, 107, 0), (108, 120, 8)]:
    for ch in range(a, b + 1):
        OFFSET[ch] = o

CN = {'零': 0, '一': 1, '两': 2, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6,
      '七': 7, '八': 8, '九': 9, '十': 10, '十一': 11, '十二': 12}
PMD = re.compile(r'(早上|上午|中午|下午|傍晚|夜里|晚上|凌晨|深夜|后半夜)?'
                 r'([零一二两三四五六七八九十]{1,3})点(半|[零一二三四五六七八九十]{1,3}分?)?')
# 只在"同一个逗号小句内"配对，避免抓到叙述里游离的"她那边"
SEG = re.compile(r'(我这边|这边|她那边|她那边的|那边)[^，。；！？]{0,12}?'
                 r'(?:早|上|中|下|傍|夜|晚|凌|深|后)?[零一二两三四五六七八九十]{0,3}点?[零一二两三四五六七八九十]{0,3}')

def nums(s):
    out = []
    for m in PMD.finditer(s):
        per, hh = m.group(1), CN.get(m.group(2))
        if hh is None:
            continue
        h = hh % 12
        if hh == 12:
            h = 0 if per in ('夜里', '凌晨', '深夜', '后半夜') else 12
        elif per in ('下午', '傍晚', '晚上'):
            h += 12
        mi = 30 if m.group(3) == '半' else 0
        out.append((h * 60 + mi) % 1440)
    return out

bad = 0
for p in sorted(glob.glob('正文/**/*.md', recursive=True)):
    ch = int(re.search(r'\d+', os.path.basename(p)).group())
    off = OFFSET.get(ch, 0)
    for i, line in enumerate(open(p, encoding='utf-8'), 1):
        s = line.strip()
        if not s or s.startswith('# ') or '这边' not in s or '那边' not in s:
            continue
        for seg in re.split(r'[，。；！？]', s):
            a = re.search(r'(我这边|这边)(.{0,12})', seg)
            b = re.search(r'(她那边|她那边的|那边)(.{0,12})', seg)
            if not (a and b):
                continue
            m1, m2 = nums(a.group(2)), nums(b.group(2))
            if not m1 or not m2:
                continue
            if off == 0:
                if m1[0] != m2[0]:
                    print(f'  [国内章写出钟点差] ch{ch} L{i}: {s[:60]}')
                    bad += 1
            else:
                d = (m1[0] - m2[0]) % 1440 / 60
                if min(abs(d - off), abs(d - off - 24), abs(d - off + 24)) > 1.0:
                    print(f'  [偏移不符 ch{ch} 应−{off}h 实−{d:.0f}h] L{i}: {s[:60]}')
                    bad += 1
print(f'待核 {bad} 处（含假报，需人工分返）')
