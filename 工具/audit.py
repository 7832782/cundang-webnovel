import re, glob, os, sys, statistics

# 全书体检：字数 / 段落并段达标 / 连续台词 / 串线 / 错字
# 用法：python 工具/audit.py           —— 全书
#       python 工具/audit.py 66 116    —— 只看指定章

D = re.compile(r'^(她说|我说|他说|她说：|我说：)')
BAN = ['有我没我', '二十圈', '纸星星', '海盐糖', '随身听', '平安结', '书签',
       '枇杷', '橘子汽水', '未回也是回', '明目张胆', '薄荷水', '明信片',
       '《答案》', '烧掉', '烧了那', '烧稿']
TYPO = ['拄', '兵袋', '胋', '隔璧', '一遗', '三遗', '两遗', 'foreign',
        'effort', ' she ', '搚', '规频', '包东纸', '三摠', '扮把']

want = {int(a) for a in sys.argv[1:]}

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
    r = best = 0
    for x in [y.strip() for y in t.split('\n') if y.strip() and not y.startswith('# ')]:
        if D.match(x):
            r += 1
            best = max(best, r)
        else:
            r = 0
    worst_run = max(worst_run, best)
    if best > 6:
        prob.append((ch, '连续台词', best))
    if med < 25:
        prob.append((ch, '段落仍偏碎', med))
    for b in BAN:
        if b in t:
            prob.append((ch, '串线:' + b, t.count(b)))
    for b in TYPO:
        if b in t:
            prob.append((ch, '错字:' + b, t.count(b)))

print(f'扫描 {len(files)} 章  总字 {tot}  段落中位数均值 {round(statistics.median(meds),1)}')
if low:
    print('低于2000字:', low)
print('全书最长连续台词段:', worst_run)
if prob:
    print('--- 问题 ---')
    for ch, kind, v in prob:
        print(f'  ch{ch:>3} {kind} {v}')
else:
    print('全部达标')
