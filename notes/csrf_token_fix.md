---
date: 2026-04-20 14:30
summary: CSRF Token là gì, cách render đúng, và tại sao token an toàn dù bị F12 inspect
tags: [csrf, security, flask-wtf, token, html, form, bảo-mật]
type: knowledge
---

## Mục Lục
- [CSRF Token là gì](#csrf-token-là-gì)
- [Vấn đề CSRF](#vấn-đề-csrf)
- [Giải pháp: Token liên kết với Session](#giải-pháp-token-liên-kết-với-session)
- [Cách render đúng vs sai](#cách-render-đúng-vs-sai)
- [Tại sao Token an toàn dù F12 lấy được](#tại-sao-token-an-toàn-dù-f12-lấy-được)
- [Issue: Text lạ "Username or main"](#issue-text-lạ-username-or-main)

---

# CSRF Token: Giải thích & Fix

## CSRF Token là gì

**CSRF** = **Cross-Site Request Forgery** (Giả mạo yêu cầu xuyên trang)

CSRF Token là một chuỗi ngẫu nhiên được server tạo ra để bảo vệ form POST khỏi tấn công CSRF. Token được lưu trên **server-side (session)** và được embed vào **form client-side**.

---

## Vấn đề CSRF

### Scenario tấn công
```
1. User A đã login vào bank.com (session còn 30 phút)
2. User A bỏ browser mở, truy cập link lạ → evilthing.com
3. evilthing.com chứa code ẩn:
   <form action="https://bank.com/transfer" method="POST">
       <input name="to_account" value="hacker123">
       <input name="amount" value="1,000,000">
   </form>
   <script>document.forms[0].submit();</script>

4. Browser tự động submit form (vì User A vẫn login bank.com!)
5. Tiền của User A bị chuyển tới hacker mà User A không biết
```

### Tại sao có thể xảy ra?
- Hacker không cần password, vì browser của User A **vẫn giữ session/cookie của bank.com**
- Browser tự động gửi cookie khi submit form tới cùng domain
- Server không có cách để phân biệt request từ **User A trực tiếp** hay từ **hacker gửi qua evilthing.com**

---

## Giải pháp: Token liên kết với Session

Flask-WTF implements CSRF protection bằng cách:

1. **Server generate random token** khi user truy cập form page
2. **Lưu token vào session** (server-side, chỉ server biết)
3. **Embed token vào form HTML** (client-side, public)
4. **Khi user submit form** → gửi token + session_id lên server
5. **Server kiểm tra cùng lúc:**
   - Token từ form == Token từ session?
   - Hợp lệ → xử lý request
   - Không → 403 Forbidden

### Key insight: 2-Layer Protection

```
Layer 1 - Session:
  User A: session_A = { csrf_token: "aaa111" }
  Hacker: session_H = { csrf_token: "bbb222" }

Layer 2 - Form Token:
  User A's form: <input name="csrf_token" value="aaa111">
  Hacker's form: <input name="csrf_token" value="bbb222">

Khi User A submit:
  ✅ session_A khớp với token aaa111 → accept

Khi Hacker cố submit qua form giả mạo:
  ❌ session_H không khớp với token aaa111 → reject
```

---

## Cách render đúng vs sai

### ✅ ĐÚNG - Hidden Input

```html
<form method="POST" action="/auth/login">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
    <input type="text" name="username">
    <input type="password" name="password">
    <button type="submit">Login</button>
</form>
```

**Kết quả:**
- Token ẩn, không hiển thị trên trang
- Layout không bị ảnh hưởng
- Form hoạt động bình thường

### ❌ SAI - Render thành Text Thô

```html
<form method="POST" action="/auth/login">
    {{ csrf_token() }}
    
    <input type="text" name="username">
    <input type="password" name="password">
</form>
```

**Kết quả HTML:**
```html
ImNjOTZlNzlmYTc3NmUyYTA5ZTVmMTNiYTYwNjU0N2Y4Yzg5ZmRkODQi.aeUL_g.JqQAYV3VMeRlKP3RWok-cqi-mHI

<input type="text" name="username">
<input type="password" name="password">
```

**Vấn đề:**
- Token dài (100+ ký tự) render thành text trên trang
- Làm layout bị sai, text elements bị wrap/cắt kỳ lạ
- "Email is required" → cắt thành "main" ⚠️

---

## Tại sao Token an toàn dù F12 lấy được

### Câu hỏi: Nếu hacker F12 inspect code và lấy được CSRF token, có giả mạo được login không?

**Câu trả lời:** ❌ **KHÔNG!** Dù lấy được token cũng không dùng được vì:

### Bảo mật 2 lớp (2-Layer Defense)

```
User A đăng nhập LogicBoost:
1. Server create session_A
2. Lưu token vào session_A['csrf_token'] = "token_aaa111"
3. Form HTML: <input name="csrf_token" value="token_aaa111">
4. User A submit → gửi session_id_A + token_aaa111

Hacker F12 lấy token_aaa111:
1. Tạo form giả mạo với token_aaa111
2. Submit qua evilthing.com
3. Browser của hacker gửi:
   - Không có session_id_A (vì hacker không login)
   - Có token_aaa111 (lấy từ F12)
4. Server kiểm tra:
   - ❌ Session của hacker ≠ session_A
   - ❌ csrf_token_aaa111 KHÔNG khớp với hacker's session
   - Reject! 403 Forbidden
```

### Tại sao hacker không có session của User A?

```
1. Session lưu trên SERVER (server-side, không public)
2. Session được identify bằng session_id cookie
3. Cookie được lưu trong BROWSER của User A (chỉ browser này biết)
4. Hacker không có browser của User A
5. → Hacker KHÔNG CÓ session_id của User A
6. → Hacker KHÔNG CÓ session của User A
7. → Dù có token cũng không dùng được!
```

### Same-Origin Policy (SOP)

```
Browser security:
- logicboost.com trang: CÓ THỂ gửi cookie/session tới logicboost.com
- evilthing.com trang: KHÔNG THỂ đọc được cookie của logicboost.com

Kết quả: Hacker form trên evilthing.com KHÔNG THỂ gửi session của User A tới logicboost.com
```

### So sánh: Hidden Input vs Visible Text

| Loại | Hacker lấy được? | An toàn? | Ưu điểm |
|------|-----------------|---------|---------|
| **Hidden Input** ✅ | YES (F12) | ✅ YES | Token ẩn, layout đẹp |
| **Visible Text** ❌ | YES (nhìn thấy) | ✅ YES | Cách bảo vệ giống nhau |

**Cả 2 đều an toàn, nhưng hidden input tốt hơn vì:**
- ✅ Token không hiển thị (UX tốt)
- ✅ Layout không bị break
- ✅ Semantic HTML đúng cách

---

## Issue: Text lạ "Username or main"

### Root cause
`{{ csrf_token() }}` render text thô CSRF token vào HTML, khiến:
- Layout bị break
- Form label text bị cắt/wrap kỳ lạ
- "Username or Email" → nhìn như "Username or main"

### Fix applied
Đã fix tất cả form trong project:

**Files modified:**
- `app/templates/auth/login.html`
- `app/templates/auth/register.html`
- `app/templates/auth/change_password.html`
- `app/templates/auth/profile.html`
- `app/templates/admin/user_form.html`
- `app/templates/admin/user_detail.html` (3 forms)

**Change:**
```html
<!-- Before -->
{{ csrf_token() }}

<!-- After -->
<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
```

**Status:** ✅ Fixed and tested

---

## Recap

| Khía cạnh | Chi tiết |
|----------|---------|
| **CSRF Token là** | Random string, server generate để bảo vệ form POST |
| **Dùng để** | Ngăn CSRF attack (hacker giả mạo request từ domain khác) |
| **Bảo mật bằng** | Token + Session (2-layer defense) |
| **Render đúng** | `<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">` |
| **Render sai** | `{{ csrf_token() }}` (text thô) |
| **F12 inspect được?** | YES, nhưng token chỉ hợp lệ với domain **chính chủ** |
| **An toàn không?** | ✅ YES, Same-Origin Policy + Session protection |

---

## Liên quan
- Xem thêm: [[flask_wtf_security]]
- Xem thêm: [[authentication_rbac]]
