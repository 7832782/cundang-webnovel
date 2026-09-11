import re, glob, os, sys, statistics

# 全书体检：字数 / 段落并段达标 / 连续台词 / 串线 / 错字
# 用法：python 工具/audit.py           —— 全书
#       python 工具/audit.py 66 116    —— 只看指定章

D = re.compile(r'^(她说|我说|他说|她说：|我说：)')
BAN = ['有我没我', '二十圈', '纸星星', '海盐糖', '随身听', '平安结', '书签',
       '枇杷', '橘子汽水', '未回也是回', '明目张胆', '薄荷水', '明信片',
       '《答案》', '烧掉', '烧了那', '烧稿']
TYPO = ['拄', '兵袋', '胋', '隔璧', '一遗', '三遗', '两遗', 'foreign',
        'effort', ' she ', '搚', '规频', '包东纸', '三摠', '扮把', '纸中']

want = {int(a) for a in sys.argv[1:] if a.isdigit()}
MODE = 'plan' if '--plan' in sys.argv else 'check'
if MODE == 'plan':
    want = set()

# “剧本行”：短（≤28字）且以她说/我说/他说开头 = 一句占一屏。
# 并段后以“她说”开头的长段不算剧本行，它是正常叙述。
D2 = re.compile(r'^(她说|我说|他说)')


def script_run(t):
    best = r = 0
    for x in t.split('\n'):
        x = x.strip()
        if not x or x.startswith('# '):
            continue
        if D2.match(x) and len(x) <= 28:
            r += 1
            best = max(best, r)
        else:
            r = 0
    return best
if MODE == 'plan':
    rows = []
    for p in sorted(glob.glob('正文/**/*.md', recursive=True),
                    key=lambda x: int(re.search(r'\d+', os.path.basename(x)).group())):
        ch = int(re.match(r'第(\d+)章_', os.path.basename(p)).group(1))
        t = open(p, encoding='utf-8').read()
        L = [x.strip() for x in t.split('\n') if x.strip() and not x.startswith('# ')]
        r = bb = 0
        for x in L:
            if D2.match(x) and len(x) <= 28:
                r += 1
                bb = max(bb, r)
            else:
                r = 0
        rows.append((ch, statistics.median([len(x) for x in L]), bb))
    need = [x for x in rows if x[1] < 40 or x[2] > 6]
    ts = {113, 114, 115, 116, 117}
    hard = [x for x in need if x[0] in ts or x[1] <= 16 or x[2] >= 20]
    rest = [x for x in need if x not in hard]
    print(f'待处理 {len(need)}/120 章；其中硬骨头 {len(hard)}，其余 {len(rest)}')
    print('已达标的章：', [x[0] for x in rows if x not in need])
    print()
    print('硬骨头（章号 / 中位数 / 最长连续台词）：')
    for ch, m, b in hard:
        print(f'  {ch:>3}  {m:>5}  {b:>3}')
    sys.exit(0)

files = []
for p in sorted(glob.glob('正文/**/*.md', recursive=True)):
    m = re.match(r'第(\d+)章_', os.path.basename(p))
    if m and (not want or int(m.group(1)) in want):
        files.append(p)

tot = 0
meds = []
worst_run = 0
low = []
prob = []
rows = []

for p in files:
    ch = int(re.match(r'第(\d+)章_', os.path.basename(p)).group(1))
    t = open(p, encoding='utf-8').read()
    n = len(re.sub(r'\s', '', t))
    tot += n
    L = [len(x.strip()) for x in t.split('\n') if x.strip() and not x.startswith('# ')]
    med = statistics.median(L)
    meds.append(med)
    if n < 2000:
        low.append((ch, n))
    best = script_run(t)
    worst_run = max(worst_run, best)
    rows.append((ch, n, med, best))
    if best > 0:
        prob.append((ch, '剧本行', best))
    floor = 22 if ch in (113, 114, 115, 116, 117) else 30
    if med < floor:
        prob.append((ch, f'段落仍偏碎(下限{floor})', med))
    for b in BAN:
        if b in t:
            prob.append((ch, '串线:' + b, t.count(b)))
    for b in TYPO:
        if b in t:
            prob.append((ch, '错字:' + b, t.count(b)))

print(f'扫描 {len(files)} 章  总字 {tot}  段落中位数均值 {round(statistics.median(meds),1)}')
if want:
    print('章 / 字数 / 段落中位数 / 剧本行：')
    for ch, n, med, b in rows:
        print(f'  ch{ch:>3}  {n:>5}  {med:>6}  {b:>3}')
if low:
    print('低于2000字:', low)
print('全书最长连续台词段:', worst_run)
if prob:
    print('--- 问题 ---')
    for ch, kind, v in prob:
        print(f'  ch{ch:>3} {kind} {v}')
else:
    print('全部达标')
