# -*- coding: utf-8 -*-
"""Sinh lộ trình 4 tháng JLPT N5→N3 (theo giáo trình できる日本語 / JPD của FPT) + TOEIC 550→800.
Chạy:  python tools/build_data.py && python tools/tao_lich.py  [YYYY-MM-DD ngày bắt đầu, mặc định 2026-11-30]
Kết quả ghi ra thư mục gốc của lộ trình."""
import csv, json, sys, datetime as dt
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlencode
from data import N5_GRAMMAR, N3_GRAMMAR, TOEIC_GRAMMAR
from dekiru_grammar import SHOCHUKYU, CHUKYU

ROOT = Path(__file__).resolve().parent.parent
START = dt.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else dt.date(2026, 11, 30)
WEEKS = 17
DAYS = [START + dt.timedelta(d) for d in range(WEEKS * 7)]
# Ngày nghỉ nhẹ: Tết dương lịch + Tết Nguyên đán 2027 (mùng 1 = 06/02/2027)
LIGHT = {dt.date(2027, 1, 1)} | {dt.date(2027, 2, 4) + dt.timedelta(i) for i in range(6)}
THU = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ nhật"]

def week_of(d): return (d - START).days // 7 + 1

def phase(w):
    if w <= 3: return 1
    if w <= 11: return 2
    if w <= 16: return 3
    return 4

PHASE_NAME = {1: "GĐ1 · Ôn 初級 1–11 + học nốt bài 12–15 (N5) + nền TOEIC",
              2: "GĐ2 · 初中級 sách vàng bài 1–15 (N4) + TOEIC Nghe",
              3: "GĐ3 · 中級 sách xanh bài 1–5 + ngữ pháp N3 + TOEIC Đọc (Part 7)",
              4: "GĐ4 · Tổng ôn + thi thử"}

def is_study_weekday(d): return d.weekday() < 5 and d not in LIGHT

def split(items, n):
    """Chia đều list items vào n ngày."""
    out, k = [], 0
    for i in range(n):
        size = len(items) * (i + 1) // n - len(items) * i // n
        out.append(items[k:k + size]); k += size
    return out

# ---- Tiếng Nhật theo Dekiru: từ vựng + kanji lấy từ tools/build/items.json (sinh bởi build_data.py) ----
ITEMS = json.load(open(ROOT / "tools" / "build" / "items.json", encoding="utf-8"))
COUNT = defaultdict(lambda: {"w": 0, "k": 0})
for it in ITEMS:
    COUNT[(it["d"], it["l"])][it["t"]] += 1
DECK_NAME = {"S": "初級", "SC": "初中級", "C": "中級"}
BOOK = {"S": "sách đỏ", "SC": "sách vàng", "C": "sách xanh"}

def link(**q): return "on-tu.html#/" + ("learn?" + urlencode(q) if q else "review")

def study_days(w0, w1): return [d for d in DAYS if w0 <= week_of(d) <= w1 and is_study_weekday(d)]

def lesson_plan(deck, lessons, days, per_lesson_grammar):
    """Chia các bài vào số ngày học theo tỷ lệ khối lượng; mỗi ngày nhận 1 đoạn từ mới + kanji + ngữ pháp."""
    wt = {l: COUNT[(deck, l)]["w"] + COUNT[(deck, l)]["k"] for l in lessons}
    tot = sum(wt.values()); alloc = {}; acc = 0; k = 0
    for i, l in enumerate(lessons):
        acc += wt[l]
        end = round(acc / tot * len(days)) if i < len(lessons) - 1 else len(days)
        end = max(end, k + 1); alloc[l] = days[k:end]; k = end
    plan = {}
    for l, ds in alloc.items():
        nw, nk, n = COUNT[(deck, l)]["w"], COUNT[(deck, l)]["k"], len(ds)
        g = split(per_lesson_grammar.get(l, []), n)
        for i, d in enumerate(ds):
            plan[d] = dict(deck=deck, lesson=l, part=(i + 1, n), w=(nw * i // n, nw * (i + 1) // n),
                           k=(nk * i // n, nk * (i + 1) // n), grammar=g[i])
    return plan

plan_jp = {}
# Tuần 1: ôn lại sách đỏ bài 1–11 (đã học ở JPD113–133) + kanji N5 còn thiếu + ôn ngữ pháp N5
W1 = study_days(1, 1)
for d, ls, g in zip(W1, [(1, 2), (3, 4), (5, 6, 7), (8, 9), (10, 11)], split(list(enumerate(N5_GRAMMAR, 1)), len(W1))):
    plan_jp[d] = dict(review=ls, extra0=(d == W1[0]), n5=g)
# Tuần 2–3: sách đỏ bài 12–15 (học mới)
plan_jp.update(lesson_plan("S", [12, 13, 14, 15], study_days(2, 3), {}))
# Tuần 4–11: sách vàng 初中級 bài 1–15 (JPD216 + JPD226)
plan_jp.update(lesson_plan("SC", list(range(1, 16)), study_days(4, 11), SHOCHUKYU))
# Tuần 12–16: sách xanh 中級 bài 1–5 (JPD316) + ngữ pháp N3 tổng hợp
D3 = study_days(12, 16)
plan_jp.update(lesson_plan("C", [1, 2, 3, 4, 5], D3, CHUKYU))
for d, g in zip(D3, split(list(enumerate(N3_GRAMMAR, 1)), len(D3))):
    plan_jp[d]["n3"] = g

toeic_wd = [d for d in DAYS if is_study_weekday(d)]
toeic_idx = {d: i for i, d in enumerate(toeic_wd)}

# Đề TOEIC full: chẩn đoán + mốc tháng + hằng tuần GĐ4
FULL_TEST_WEEKS = {1: "Đề chẩn đoán (ETS 2024 – Test 1)", 5: "ETS 2024 – Test 2", 9: "ETS 2024 – Test 3",
                   13: "ETS 2024 – Test 4", 14: "ETS 2024 – Test 5", 15: "ETS 2025 – Test 1",
                   16: "ETS 2025 – Test 2", 17: "ETS 2025 – Test 3"}

def T(cat, text, mins, href=None):
    t = {"cat": cat, "text": text, "min": mins}
    if href: t["link"] = href
    return t

SRS = "Ôn tập SRS (web ôn từ): làm hết thẻ đến hạn"

def jp_weekday(d, j, p):
    tasks = [T("JP", SRS, 15, link())]
    if "review" in j:
        for l in j["review"]:
            c = COUNT[("S", l)]
            tasks.append(T("JP", f"Ôn lại 初級 bài {l}: {c['w']} từ" + (f" + {c['k']} kanji" if c['k'] else "") +
                           " — xem lại danh sách rồi làm trắc nghiệm", 15, link(d="S", l=l)))
        if j["extra0"] and COUNT[("S", 0)]["k"]:
            tasks.append(T("JP", f"Kanji N5 bổ sung: {COUNT[('S', 0)]['k']} chữ số đếm chưa có trong sách đỏ (二三四…百千万) — học + trắc nghiệm",
                           15, link(d="S", l=0)))
        gl = "; ".join(f"#{i} {g[0]}" for i, g in j["n5"])
        tasks.append(T("JP", f"Ôn ngữ pháp N5 (file 01): {gl} — che nghĩa, tự nói nghĩa + đặt 1 câu", 30))
    else:
        dk, l, (pi, pn) = j["deck"], j["lesson"], j["part"]
        tag = f"{DECK_NAME[dk]} bài {l}" + (f" ({pi}/{pn})" if pn > 1 else "")
        a, b = j["w"]
        if b > a:
            tasks.append(T("JP", f"Từ mới {tag}: từ {a + 1}–{b} ({b - a} từ) — tự học theo cách của bạn rồi làm trắc nghiệm", 30,
                           link(d=dk, l=l, t="w", a=a, b=b)))
        ka, kb = j["k"]
        if kb > ka:
            tasks.append(T("JP", f"Kanji {tag}: {kb - ka} chữ (Hán Việt, On/Kun, từ ghép) — viết tay + trắc nghiệm", 20,
                           link(d=dk, l=l, t="k", a=ka, b=kb)))
        if j["grammar"]:
            gl = "; ".join(f"{pat} ({m})" for pat, m in j["grammar"])
            tasks.append(T("JP", f"Ngữ pháp {tag}: {gl} — đọc phần 文法 trong {BOOK[dk]} + slide FLM, chép ví dụ, tự đặt 3 câu", 35))
        elif dk == "S" and pi == 1:
            tasks.append(T("JP", f"Ngữ pháp 初級 bài {l}: đọc phần 文法 trong sách đỏ, làm bài tập cuối bài", 35))
        elif dk == "S":
            tasks.append(T("JP", f"Luyện 初級 bài {l}: hội thoại (会話) + bài tập trong sách, nghe CD bài {l}", 30))
        if "n3" in j:
            gl = "; ".join(f"#{i} {g[0]}" for i, g in j["n3"])
            tasks.append(T("JP", f"Ngữ pháp N3 bổ sung (file 01): {gl} — đọc ví dụ, tự đặt 2 câu/mẫu", 25))
    listen = {1: "NHK World 'Easy Japanese' 1 bài (nghe 2 lần, nhại theo)",
              2: "Nghe CD bài đang học (sách vàng) + shadowing hội thoại 10 phút",
              3: "Choukai N3: 5 câu (Shin Kanzen Master / đề mẫu) + nghe lại script"}[p]
    read = {1: "Đọc 1 truyện Tadoku level 0–1 (tadoku.org, miễn phí)",
            2: "Đọc 1 bài NHK News Web Easy, tra từ mới bằng Mazii",
            3: "Dokkai: bài đọc trong sách xanh hoặc 1 đoạn N3 (Shin Kanzen Master Dokkai), bấm giờ"}[p]
    return tasks + [T("JP", listen, 15), T("JP", read, 15)]

def build_day(d):
    w, p = week_of(d), phase(week_of(d))
    tasks, note = [], ""
    if d in LIGHT:
        note = "Ngày nghỉ nhẹ (Tết) — giữ nhịp, không học mới"
        tasks += [T("JP", "Ôn tập SRS (web ôn từ): chỉ ôn thẻ đến hạn, không học từ mới", 20, link()),
                  T("EN", "Nghe thụ động 20 phút: podcast/BBC 6 Minute English hoặc phim có phụ đề Anh", 20)]
        return tasks, note

    wd = d.weekday()
    if wd < 5 and d not in plan_jp:  # GĐ4: tổng ôn, không học mới
        n = d.weekday()
        a, b = n * 20 + 1, min(n * 20 + 20, len(N3_GRAMMAR))
        tasks += [T("JP", SRS, 25, link()),
                  T("JP", f"Ôn lại từ + kanji 中級 bài {n + 1} (sách xanh): làm lại trắc nghiệm cả bài", 20, link(d="C", l=n + 1)),
                  T("JP", f"Tổng ôn ngữ pháp N3 #{a}–{b} (file 01): che nghĩa, tự nói nghĩa + đặt câu; đánh dấu mẫu còn yếu", 40),
                  T("JP", "Đề luyện từng phần N3: 1 phần Moji-Goi hoặc Bunpou (luân phiên), chấm điểm và chữa", 30),
                  T("JP", "Choukai N3: 1 phần đề thi thử + nghe lại script", 20),
                  T("EN", "Chữa lại đề thứ 7: viết lý do sai từng câu vào sổ lỗi", 30),
                  T("EN", "Luyện phần yếu nhất (theo sổ lỗi): 30–40 câu", 35),
                  T("EN", "Part 5: 30 câu bấm giờ 8 phút", 15)]
        return tasks, note
    if wd < 5:
        tasks += jp_weekday(d, plan_jp[d], p)
        # ---------- TOEIC ----------
        i = toeic_idx[d]
        topic = TOEIC_GRAMMAR[i % len(TOEIC_GRAMMAR)]
        if i < 50:
            tasks.append(T("EN", f"600 Essential Words for the TOEIC — Lesson {i + 1} (12 từ) → ghi sổ / Anki", 15))
        else:
            tasks.append(T("EN", "Ôn từ TOEIC + ghi 10 từ mới lấy từ đề đã làm vào sổ từ", 15))
        if p == 1:
            part = "Part 1: 6–10 tranh" if w <= 2 else "Part 2: 25 câu"
            tasks += [T("EN", f"Ngữ pháp Part 5: {topic[0]} — {topic[1]} Làm 15 câu đúng chủ điểm", 30),
                      T("EN", f"Nghe {part} + chép chính tả 10 phút các câu sai", 30)]
        elif p == 2:
            tasks += [T("EN", f"Part 5: 30 câu bấm giờ 10 phút (ôn lần 2 chủ điểm: {topic[0]})", 20),
                      T("EN", "Part 3/4: 4 đoạn (12 câu) → đọc script, shadowing 1 đoạn 10 phút", 35),
                      T("EN", "Part 6: 2 đoạn (8 câu), ghi lại từ nối/collocation", 15)]
        else:
            p7 = "Part 7 đoạn đơn: 2–3 bài (10 câu)" if w <= 13 else "Part 7 đoạn kép/ba: 1–2 bộ (10 câu)"
            tasks += [T("EN", "Part 5: 30 câu bấm giờ 9 phút", 15),
                      T("EN", f"{p7}, bấm giờ ≈ 1 phút/câu, phân tích câu sai", 35),
                      T("EN", "Nghe Part 3/4: 1 set 13 câu + shadowing 10 phút", 25)]
        # Nhắc mốc quan trọng
        if d == dt.date(2027, 2, 22):
            tasks.append(T("ADMIN", "Đăng ký thi TOEIC (IIG Việt Nam) cho đợt cuối tháng 3/đầu tháng 4/2027", 10))
        if d == dt.date(2027, 3, 1):
            tasks.append(T("ADMIN", "Kiểm tra lịch đăng ký JLPT tháng 7/2027 (thường mở khoảng tháng 3) tại đơn vị tổ chức ở thành phố bạn", 10))
    elif wd == 5:  # Thứ 7: ngày kiểm tra
        if w in FULL_TEST_WEEKS:
            tasks.append(T("EN", f"TOEIC FULL TEST 200 câu / 120 phút: {FULL_TEST_WEEKS[w]} — ghi điểm vào bảng tiến độ", 130))
        elif p == 3:
            tasks.append(T("EN", "TOEIC half test (Part 1–7, 100 câu / 60 phút) + chấm điểm", 70))
        else:
            tasks.append(T("EN", "TOEIC mini test: Part 2 (25 câu) + Part 5 (30 câu) + Part 3 (13 câu)", 50))
        if w in (3, 11):
            tasks.append(T("JP", f"Thi thử JLPT {'N5' if w == 3 else 'N4'}: đề mẫu chính thức trên jlpt.jp (Moji-Goi, Bunpou-Dokkai, Choukai)", 120))
        elif w in (16, 17):
            tasks.append(T("JP", "Thi thử JLPT N3 trọn bộ (140 phút): đề mẫu jlpt.jp / Shin Kanzen Master đề thi thử", 140))
        else:
            tasks.append(T("JP", "Kiểm tra tuần: tự viết lại các mẫu ngữ pháp của tuần + làm lại bài tập trong sách / đề kiểm tra trên FLM", 40))
            tasks.append(T("JP", SRS, 20, link()))
    else:  # Chủ nhật: ôn tập
        tasks += [T("JP", SRS + " (dọn sạch trước tuần mới)", 25, link()),
                  T("JP", "Ôn kanji tuần: viết lại theo trí nhớ, đánh dấu chữ sai", 20),
                  T("JP", "Xem 1 tập anime/drama có phụ đề Nhật (hoặc YouTube: Comprehensible Japanese)", 25),
                  T("EN", "Đọc lại sổ lỗi sai TOEIC của tuần + làm lại các câu sai", 30),
                  T("EN", "Nghe giải trí 20 phút: podcast/TED bằng tiếng Anh", 20),
                  T("ADMIN", "Đánh giá tuần: tick hoàn thành, ghi điểm thi thử, điều chỉnh tuần sau", 10)]
    return tasks, note

rows = []
for d in DAYS:
    tasks, note = build_day(d)
    for i, t in enumerate(tasks):  # gắn mã task để web ôn từ tự đánh dấu xong
        if "link" in t:
            t["link"] += ("&" if "?" in t["link"] else "?") + "task=" + d.isoformat() + "%23" + str(i)
    rows.append(dict(date=d.isoformat(), thu=THU[d.weekday()], week=week_of(d),
                     phase=PHASE_NAME[phase(week_of(d))], note=note, tasks=tasks,
                     total=sum(t["min"] for t in tasks)))

# ---------- Markdown lịch ----------
CAT = {"JP": "🇯🇵", "EN": "🇬🇧", "ADMIN": "📌"}
md = [f"# Lịch học hằng ngày — 4 tháng ({DAYS[0]:%d/%m/%Y} → {DAYS[-1]:%d/%m/%Y})\n",
      "> Đánh dấu `[x]` khi xong. Bản tương tác có lưu tiến độ: mở **tracker.html** bằng trình duyệt.\n",
      "> Thời lượng ngày thường ≈ 3,5 giờ (Nhật ~2h, Anh ~1,5h). Thiếu thời gian thì ưu tiên: Ôn tập SRS → Từ mới → Ngữ pháp → TOEIC Part 5/nghe.\n",
      "> Tiếng Nhật theo できる日本語: sách đỏ 初級 (JPD113–133) → sách vàng 初中級 (JPD216–226) → sách xanh 中級 bài 1–5 (JPD316). Task có 🔗 mở trang **on-tu.html** đúng đoạn từ cần học.\n"]
cur_w = 0
for r in rows:
    if r["week"] != cur_w:
        cur_w = r["week"]
        md.append(f"\n## Tuần {cur_w} — {r['phase']}\n")
    head = f"### {r['thu']} {dt.date.fromisoformat(r['date']):%d/%m/%Y}  ·  ~{r['total']} phút"
    md.append(head + (f"  ·  _{r['note']}_" if r["note"] else ""))
    for t in r["tasks"]:
        md.append(f"- [ ] {CAT[t['cat']]} {t['text']} _({t['min']}′)_" + (f" [🔗]({t['link']})" if t.get("link") else ""))
    md.append("")
(ROOT / "03_Lich-hoc-hang-ngay-4-thang.md").write_text("\n".join(md), encoding="utf-8")

# ---------- CSV (mở bằng Excel / Google Sheets) ----------
with open(ROOT / "lich-hoc.csv", "w", newline="", encoding="utf-8-sig") as f:
    wr = csv.writer(f)
    wr.writerow(["Ngày", "Thứ", "Tuần", "Giai đoạn", "Loại", "Nhiệm vụ", "Phút", "Xong?"])
    for r in rows:
        for t in r["tasks"]:
            wr.writerow([r["date"], r["thu"], r["week"], r["phase"], t["cat"], t["text"], t["min"], ""])

# ---------- Kiến thức tiếng Nhật ----------
from data import N4_GRAMMAR
def gram_table(title, items):
    out = [f"\n### {title} ({len(items)} mẫu)\n", "| # | Mẫu | Nghĩa / cách dùng | Ví dụ |", "|---|---|---|---|"]
    out += [f"| {i} | {a} | {b} | {c} |" for i, (a, b, c) in enumerate(items, 1)]
    return "\n".join(out)
def dekiru_table(title, d):
    out = [f"\n### {title}\n", "| Bài | Mẫu | Nghĩa / cách dùng |", "|---|---|---|"]
    out += [f"| {l} | {p} | {m} |" for l in sorted(d) for p, m in d[l]]
    return "\n".join(out)
head = (ROOT / "tools" / "jp_header.md").read_text(encoding="utf-8")
jp = (head + "\n## 6. Ngữ pháp theo bài Dekiru (khớp task hằng ngày)\n"
      + dekiru_table("初中級 — sách vàng (JPD216 bài 1–7, JPD226 bài 8–15; tên mẫu theo bảng buổi học FLM)", SHOCHUKYU)
      + dekiru_table("中級 — sách xanh bài 1–5 (JPD316, theo slide 文法説明 trên FLM)", CHUKYU)
      + "\n\n## 7. Danh sách ngữ pháp JLPT tổng hợp (số # khớp với lịch học hằng ngày)\n"
      + gram_table("N5", N5_GRAMMAR) + gram_table("N4", N4_GRAMMAR) + gram_table("N3", N3_GRAMMAR) + "\n")
(ROOT / "01_Kien-thuc-tieng-Nhat-N5-N4-N3.md").write_text(jp, encoding="utf-8")

# ---------- Tracker HTML ----------
tpl = (ROOT / "tools" / "tracker_template.html").read_text(encoding="utf-8")
(ROOT / "tracker.html").write_text(tpl.replace("/*__DATA__*/[]", json.dumps(rows, ensure_ascii=False)), encoding="utf-8")

n_tasks = sum(len(r["tasks"]) for r in rows)
print(f"OK: {len(rows)} ngày, {n_tasks} task, {DAYS[0]} -> {DAYS[-1]}")
for dk in ("S", "SC", "C"):
    ds = sorted(d for d, j in plan_jp.items() if j.get("deck") == dk)
    if ds: print(dk, ds[0], "->", ds[-1], len(ds), "ngày")
