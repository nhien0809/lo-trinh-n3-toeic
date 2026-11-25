# -*- coding: utf-8 -*-
"""Gộp từ vựng + Kanji Dekiru thành web/data.js cho trang ôn từ.
Nguồn (tools/sources):
  shokyu_vocab.json       初級 bài 1–15, nghĩa Việt (đối chiếu "New words list", repo Shiraori13/dekiru-nihongo)
  shokyu_kanji_chars.json Hán Việt + nghĩa Việt cho chữ trong 初級 (KANJIDIC2/EDRDG CC BY-SA, repo trên)
  shochukyu_vocab.json    初中級 bài 1–15 (repo rifatjp2002-art) + nghĩa Việt ở vocab_shochukyu_vi.tsv
  kanji_flm.json          Kanji theo bài từ slide FLM: JPD216 (初中級 1–7), JPD226 (8–15), JPD316 (中級 1–5)
  chukyu_vocab.json       中級 1–5: từ ghép trong slide Kanji JPD316, cách đọc kiểm bằng JMdict + nghĩa ở vocab_chukyu_vi.tsv
Chạy: python tools/build_data.py"""
import json, os, re
from collections import Counter

T = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(T, 'sources')
ROOT = os.path.dirname(T)
load = lambda n: json.load(open(os.path.join(SRC, n), encoding='utf-8'))

def tsv(name):
    out = {}
    for line in open(os.path.join(T, name), encoding='utf-8'):
        if line.startswith('#') or not line.strip():
            continue
        p = line.rstrip('\n').split('\t')
        out[p[0]] = p[1:]
    return out

KATA = re.compile(r'^[゠-ヿー・ 〜~A-Za-z0-9]+$')
N5 = list("安一飲右雨駅円火花下何会外学間気九休魚金空月見言古五後午語校口行高国今左三山四子耳時七車社手週十出書女小少上食新人水生西先千川前足多大男中長天店電土東道読南二日入年買白八半百父分聞母北木本毎万名目友来立六話")
NUM_EX = {"一": [("一つ", "ひとつ")], "二": [("二つ", "ふたつ"), ("二人", "ふたり")], "三": [("三つ", "みっつ"), ("三月", "さんがつ")],
          "四": [("四つ", "よっつ"), ("四月", "しがつ")], "五": [("五つ", "いつつ"), ("五月", "ごがつ")], "六": [("六つ", "むっつ"), ("六月", "ろくがつ")],
          "七": [("七つ", "ななつ"), ("七月", "しちがつ")], "八": [("八つ", "やっつ"), ("八百屋", "やおや")], "九": [("九つ", "ここのつ"), ("九月", "くがつ")],
          "十": [("十日", "とおか"), ("十分", "じゅっぷん")], "百": [("百円", "ひゃくえん"), ("三百", "さんびゃく")], "千": [("千円", "せんえん"), ("三千", "さんぜん")],
          "万": [("一万円", "いちまんえん"), ("万一", "まんいち")]}

KC = load('shokyu_kanji_chars.json')
KD = load('kanjidic_subset.json')
KMV = tsv('kanji_meaning_vi.tsv')

items, seen = [], set()
def add(it):
    key = it['id']
    if key in seen:
        return False
    seen.add(key); items.append(it); return True

def wid(jp, kana): return 'w:' + jp + '|' + kana

def kinfo(ch, hv=None):
    """Hán Việt, nghĩa, On, Kun cho 1 chữ."""
    k = KC.get(ch, {}); m = KMV.get(ch); d = KD.get(ch, {})
    hv = hv or (', '.join(k['hv']).upper() if k.get('hv') else (m[0].upper() if m else ''))
    vi = (m[1] if m else '') or k.get('meaning', '') or ', '.join(d.get('en', []))
    on = k.get('on') or d.get('on', []); kun = k.get('kun') or d.get('kun', [])
    return hv, vi, '・'.join(on[:3]), '、'.join(kun[:3])

# ---------- 初級 (sách đỏ) ----------
S = load('shokyu_vocab.json')
first = {}
for w in S:
    for ch in w['k']:
        if '一' <= ch <= '鿿' and ch not in first:
            first[ch] = w['l']
for i, w in enumerate(S):
    kana = w['h'] or w['k']
    add(dict(id=wid(w['k'], kana), d='S', l=w['l'], t='w', jp=w['k'], kana=kana if kana != w['k'] else '', vi=w['m']))
for ch in N5:
    hv, vi, on, kun = kinfo(ch)
    ex = NUM_EX.get(ch) or [(w['k'], w['h']) for w in S if ch in w['k']][:3]
    add(dict(id='k:' + ch, d='S', l=first.get(ch, 0), t='k', jp=ch, hv=hv, vi=vi, on=on, kun=kun,
             ex=[list(e) for e in ex], sup=ch not in first))
# Kanji trường dạy theo slide FLM (JPD133: bài 8–11), ngoài bộ N5
for l, chars in load('kanji_shokyu_flm.json').items():
    if l.startswith('_'):
        continue
    for ch in chars:
        hv, vi, on, kun = kinfo(ch)
        ex = [[w['k'], w['h']] for w in S if ch in w['k']][:3]
        if ch == '起':  # không có trong bộ dữ liệu KANJIDIC rút gọn
            on, kun, ex = 'キ', 'お.きる、お.こす', [['起きます', 'おきます'], ['起床', 'きしょう']]
        add(dict(id='k:' + ch, d='S', l=int(l), t='k', jp=ch, hv=hv, vi=vi, on=on, kun=kun, ex=ex, src='FLM JPD133'))

# ---------- 初中級 (sách vàng) ----------
VI = tsv('vocab_shochukyu_vi.tsv')
for w in load('shochukyu_vocab.json'):
    vi, *fix = VI[w['id']]
    kana = fix[0] if fix and fix[0] else w['h']
    jp = w['k']
    if KATA.match(jp): kana = ''
    add(dict(id=wid(jp, kana), d='SC', l=w['l'], t='w', jp=jp, kana=kana, vi=vi))

FL = load('kanji_flm.json')
def flm_kanji(course, deck):
    for o in sorted([o for o in FL if o['course'] == course], key=lambda o: o['lesson']):
        hv, vi, on, kun = kinfo(o['kanji'], o['hv'])
        add(dict(id='k:' + o['kanji'], d=deck, l=o['lesson'], t='k', jp=o['kanji'], hv=hv, vi=vi,
                 on=o['on'].replace(' ', '・') or on, kun=o['kun'].replace(' ', '、') or kun,
                 ex=[[w['w'], w['r']] for w in o['words']][:3], src='FLM ' + course))
flm_kanji('JPD216', 'SC'); flm_kanji('JPD226', 'SC')

# ---------- 中級 (sách xanh) bài 1–5 ----------
CV = tsv('vocab_chukyu_vi.tsv')
for w in load('chukyu_vocab.json'):
    if w['k'] in CV:
        add(dict(id=wid(w['k'], w['h']), d='C', l=w['l'], t='w', jp=w['k'], kana=w['h'], vi=CV[w['k']][0]))
flm_kanji('JPD316', 'C')

# ---------- Chỉ viết kanji khi đã học chữ đó ----------
# Kanji coi là "đã học" tại (sách, bài) = mọi chữ Kanji của các bài trước + bài hiện tại (theo thứ tự đỏ → vàng → xanh),
# cộng 12 chữ số N5 bổ sung. Từ có chữ chưa học (hoặc không có trong chương trình) -> viết toàn bộ bằng kana
# (từ ngoại lai vốn đã là katakana). Cách viết kanji gốc giữ ở trường 'full'.
RANK = {'S': 0, 'SC': 1, 'C': 2}
IS_K = lambda c: '一' <= c <= '鿿'
kpos = {i['jp']: (RANK[i['d']], i['l']) for i in items if i['t'] == 'k'}
conv, nokana = Counter(), []
for it in items:
    if it['t'] != 'w' or not any(IS_K(c) for c in it['jp']):
        continue
    here = (RANK[it['d']], it['l'])
    if all(c in kpos and kpos[c] <= here for c in it['jp'] if IS_K(c)):
        continue
    if not it['kana']:
        nokana.append(it['jp']); continue
    it['full'] = it['jp']; it['jp'] = it['kana']; it['kana'] = ''
    conv[it['d']] += 1

DECKS = {'S': '初級 (sách đỏ)', 'SC': '初中級 (sách vàng)', 'C': '中級 (sách xanh)'}
os.makedirs(os.path.join(ROOT, 'web'), exist_ok=True)
with open(os.path.join(ROOT, 'web', 'data.js'), 'w', encoding='utf-8') as f:
    f.write('// Sinh bởi tools/build_data.py — đừng sửa tay\n')
    f.write('window.DEKIRU=' + json.dumps(dict(decks=DECKS, items=items), ensure_ascii=False, separators=(',', ':')) + ';\n')
os.makedirs(os.path.join(T, 'build'), exist_ok=True)
json.dump(items, open(os.path.join(T, 'build', 'items.json'), 'w', encoding='utf-8'), ensure_ascii=False)

print('Từ đổi về kana (có kanji chưa học):', dict(conv), '| thiếu cách đọc, giữ kanji:', nokana)
print('items', len(items), Counter((i['d'], i['t']) for i in items))
print('N5 kanji bổ sung:', ''.join(i['jp'] for i in items if i.get('sup')))
print('kanji thiếu nghĩa:', ''.join(i['jp'] for i in items if i['t'] == 'k' and not i['vi']))
