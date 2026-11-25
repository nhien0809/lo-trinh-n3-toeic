# Lộ trình 4 tháng: JLPT N5 → N3 (giáo trình できる日本語) + TOEIC 550 → 800+

**Thời gian:** 30/11/2026 → 28/03/2027 (17 tuần, nghỉ nhẹ Tết dương lịch và Tết Nguyên đán 04–09/02/2027)

| File | Dùng để |
|---|---|
| `tracker.html` | **Mở hằng ngày** (nhấp đúp, mở bằng Chrome/Edge): tick task, % tiến độ, chuỗi ngày, điểm thi thử. Task từ vựng/kanji có nút **Học ▸** / **Ôn ▸** nhảy sang trang ôn từ |
| `on-tu.html` | **Web ôn từ**: danh sách từ + kanji theo bài Dekiru, trắc nghiệm 4 đáp án, lặp lại ngắt quãng kiểu Anki (SM-2). Làm ≥80% thì task trong tracker tự được tick |
| `01_Kien-thuc-tieng-Nhat-N5-N4-N3.md` | Cấu trúc đề JLPT, giáo trình theo môn JPD, **ngữ pháp từng bài sách vàng / sách xanh**, 239 mẫu ngữ pháp JLPT N5–N3 |
| `02_Kien-thuc-TOEIC-800.md` | Cấu trúc đề, mẹo từng Part, 20 chủ điểm ngữ pháp, phương pháp nghe/đọc, mốc điểm |
| `03_Lich-hoc-hang-ngay-4-thang.md` | Toàn bộ lịch dạng checklist để in hoặc đọc |
| `lich-hoc.csv` | Lịch dạng bảng, mở bằng Excel/Google Sheets |
| `web/` | Dữ liệu từ vựng (`data.js`), giao diện chung, nền động three.js (`bg.js`) |
| `tools/` | Script + dữ liệu nguồn. Xem mục "Sinh lại" bên dưới |

> Tiến độ (tick task, thẻ ôn từ) lưu trong trình duyệt. Luôn mở bằng **cùng một trình duyệt**, và thỉnh thoảng bấm **Xuất file sao lưu** ở trang ôn từ.

## Tiếng Nhật theo giáo trình trường (FLM)
| Tuần | Nội dung | Môn tương ứng |
|---|---|---|
| 1 | Ôn lại sách đỏ 初級 bài 1–11 (trắc nghiệm cả bài, kanji theo slide JPD113–133 + 30 kanji N5 bổ sung) + ôn ngữ pháp N5 | JPD113–133 (đã học) |
| 2–3 | Sách đỏ bài 12–15: 202 từ mới | — |
| 4–11 | Sách vàng 初中級 bài 1–15: 934 từ + 162 kanji, ngữ pháp theo bảng buổi học FLM | JPD216, JPD226 |
| 12–16 | Sách xanh 中級 bài 1–5: 249 từ + 82 kanji, ngữ pháp từ slide 文法説明 + 100 mẫu N3 tổng hợp | JPD316 |
| 17 | Tổng ôn, thi thử N3 | |

## Nhịp một tuần
- **Thứ 2–6 (~3,5 giờ):** Nhật ~2 giờ (ôn SRS 15′, từ mới 30′, kanji 20′, ngữ pháp 35′, nghe 15′, đọc 15′) + TOEIC ~1,5 giờ.
- **Thứ 7:** thi thử TOEIC (mini / half / full) + kiểm tra tuần tiếng Nhật.
- **Chủ nhật (~2 giờ):** dọn thẻ SRS, sổ lỗi sai, xem phim, đánh giá tuần.

**Mốc thi:** TOEIC cuối tháng 3/đầu tháng 4/2027 (nhắc đăng ký ngày 22/02) · JLPT N3 kỳ tháng 7/2027 (nhắc kiểm tra đăng ký ngày 01/03) · thi thử N5 tuần 3, N4 tuần 11, N3 tuần 16–17.

## Sinh lại
```
python tools/build_data.py      # tools/sources + *.tsv  ->  web/data.js
python tools/tao_lich.py        # lịch -> tracker.html, 03_..., lich-hoc.csv, 01_...
node tools/web/build_bg.mjs     # (cần esbuild) three.js trong Downloads -> web/bg.js
```
Đổi ngày bắt đầu: `python tools/tao_lich.py 2026-12-07`. Sửa nghĩa tiếng Việt trong `tools/vocab_*_vi.tsv`, `tools/kanji_meaning_vi.tsv`, rồi chạy lại hai lệnh đầu.

## Nguồn dữ liệu
- Từ vựng 初級: repo GitHub Shiraori13/dekiru-nihongo. Từ vựng 初中級: repo của rifatjp2002-art, nghĩa tiếng Việt dịch bổ sung.
- Kanji theo bài + ngữ pháp sách vàng/xanh: slide JPD216/226/316 và bảng buổi học trên FLM (flm.fpt.edu.vn).
- Từ vựng 中級 bài 1–5: lấy từ các từ ghép trong slide Kanji JPD316. Cách đọc kiểm tra bằng JMdict/KANJIDIC2 (EDRDG, CC BY-SA 4.0).
- Nền động: three.js (MIT).
