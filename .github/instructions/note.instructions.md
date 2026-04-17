---
description: Tạo file note khi người dùng chat "note ..."
applyTo: 'khi người dùng bắt đầu message với "note" hoặc "note ..."'
---

# Hướng dẫn tạo file Note

## Khi nào tạo file Note?
- Khi người dùng chat bắt đầu với "note" hoặc "note ..." (ví dụ: "note cấu trúc project", "note lỗi trong validation")

## Quy tắc đặt tên file Note
- **Format**: `short_title_in_english.md`
- **Ví dụ**: `project_structure.md`, `user_quiz_config.md`, `uuid_explanation.md`
- Sử dụng **tiếng Anh**, chữ thường, dấu gạch dưới thay khoảng trắng
- Tên file ngắn gọn, mô tả nội dung chính
- **Không** sử dụng tiếng Việt trong tên file

---

## Cấu trúc Header của file Note

```markdown
---
date: YYYY-MM-DD HH:mm
summary: Tóm tắt ngắn gọn nội dung note (1-2 dòng)
tags: [tag1, tag2, tag3]
type: knowledge   # knowledge | issue
---
```

**Ví dụ — Knowledge:**
```markdown
---
date: 2026-04-17 10:45
summary: Giải thích cách Markdown + KaTeX hoạt động cùng nhau trong LogicBoost
tags: [markdown, katex, rendering, frontend]
type: knowledge
---

# Markdown + LaTeX Rendering
```

**Ví dụ — Issue:**
```markdown
---
date: 2026-04-17 11:00
summary: Lỗi KaTeX không render được công thức sau khi marked.js chạy
tags: [katex, marked, bug, frontend]
type: issue
---

# KaTeX Không Render Sau marked.js
```

---

## Nội dung Note

### Ngôn ngữ
- Viết bằng **tiếng Việt**
- Giữ nguyên các thuật ngữ kỹ thuật đặc thù (Flask, Excel, rendering, validation, v.v.)

### Định dạng
- Sử dụng Markdown với heading, bullet points, code blocks
- Tóm tắt các thông tin liên quan trong cuộc hội thoại

### Mục lục (TOC)
- Nếu note có từ **3 mục (heading level 2) trở lên**, PHẢI có mục lục ở đầu file
- Mục lục nằm ngay sau header metadata
- Format:
```markdown
## Mục Lục
- [Tiêu đề](#anchor-link)
```

---

## Template theo `type`

### type: knowledge
```markdown
---
date: YYYY-MM-DD HH:mm
summary: ...
tags: [...]
type: knowledge
---

## Mục Lục (nếu có từ 3 mục trở lên)

# Tiêu đề Note

## Khái niệm
Giải thích khái niệm, định nghĩa

## Cách hoạt động
Mô tả flow, cơ chế

## Ví dụ thực tế
Code snippet hoặc ví dụ minh họa

## Liên quan
- Xem thêm: [[tên_file_note_liên_quan]]
```

### type: issue
```markdown
---
date: YYYY-MM-DD HH:mm
summary: ...
tags: [...]
type: issue
---

# Tiêu đề Issue

## Vấn đề
Mô tả vấn đề gặp phải

## Nguyên nhân
Tại sao xảy ra

## Giải pháp
Cách đã giải quyết (kèm code nếu có)

## Kết quả
✅ Đã fix / ⚠️ Workaround / ❌ Chưa giải quyết

## Liên quan
- Xem thêm: [[tên_file_note_liên_quan]]
```

---

## Cross-reference giữa các Note

Khi note có liên quan đến note khác, thêm mục **Liên quan** ở cuối file:

```markdown
## Liên quan
- Xem thêm: [[markdown_latex_rendering]]
- Xem thêm: [[database_schema]]
```

---

## Ví dụ hoàn chỉnh

### Knowledge note
```markdown
---
date: 2026-04-17 10:45
summary: Tổng hợp cách dùng Markdown + KaTeX để render câu hỏi toán học trong LogicBoost
tags: [markdown, katex, rendering, frontend]
type: knowledge
---

## Mục Lục
- [Khái niệm](#khai-niem)
- [Cách hoạt động](#cach-hoat-dong)
- [Ví dụ thực tế](#vi-du-thuc-te)

# Markdown + LaTeX Rendering

## Khái niệm
- **Markdown** (marked.js) — xử lý định dạng văn bản: in đậm, danh sách, bảng
- **LaTeX** (KaTeX) — xử lý ký hiệu và công thức toán học

## Cách hoạt động
1. marked.js render Markdown → HTML
2. KaTeX scan HTML vừa render, tìm `$...$` và `$$...$$` rồi render tiếp

## Ví dụ thực tế
\`\`\`javascript
el.innerHTML = marked.parse(content);
renderMathInElement(el, {
    delimiters: [
        { left: "$$", right: "$$", display: true },
        { left: "$",  right: "$",  display: false }
    ]
});
\`\`\`

## Liên quan
- Xem thêm: [[database_schema]]
```

### Issue note
```markdown
---
date: 2026-04-17 11:30
summary: KaTeX không render công thức vì marked.js escape ký tự $ trước
tags: [katex, marked, bug, frontend]
type: issue
---

# KaTeX Không Render Sau marked.js

## Vấn đề
Công thức `$r = 0.06$` hiển thị dạng text thô, không render thành ký hiệu toán học.

## Nguyên nhân
marked.js escape ký tự `$` thành `&dollar;` trước khi KaTeX có cơ hội xử lý.

## Giải pháp
Cấu hình marked.js để không escape `$`, sau đó mới gọi `renderMathInElement()`.

## Kết quả
✅ Đã fix

## Liên quan
- Xem thêm: [[markdown_latex_rendering]]
```

---

## Vị trí lưu file
Tất cả file note sẽ được lưu trong folder: `LogicBoost/notes/`