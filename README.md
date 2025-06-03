
# Trợ lý Lập trình Thông minh

Ứng dụng Flask “Trợ lý Lập trình” giúp phân tích và gợi ý sửa lỗi mã nguồn tự động, chạy trên Google Cloud Run.

---

## 1. Cấu hình `gcloud`

```bash
gcloud init
# – Chọn tài khoản Google của bạn  
# – Chọn "Enter a project ID" hoặc "Create a new project"  
# – Nhập PROJECT_ID (ví dụ ai-phan-tich-code)
````

---

## 2. Bật API cần thiết

```bash
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  --project=ai-phan-tich-code
```

---

## 3. Deploy với Buildpacks

```bash
gcloud run deploy smart-assistant ^
  --project=ai-phan-tich-code ^
  --region=us-central1 ^
  --source=. ^
  --allow-unauthenticated ^
  --set-env-vars=GEMINI_API_KEY=<..............>
```

* `--source=.`: dùng Buildpacks tự động build container từ mã Python/Flask.
* `--allow-unauthenticated`: cho phép mọi người truy cập.
* `--set-env-vars`: truyền biến môi trường `GEMINI_API_KEY`.

---

## 4. Cập nhật biến môi trường

Nếu muốn thay API key mà không redeploy toàn bộ:

```bash
gcloud run services update smart-assistant \
  --region=us-central1 \
  --set-env-vars=GEMINI_API_KEY=<NEW_GEMINI_API_KEY>
```

---

## 5. Kiểm tra biến môi trường

```bash
gcloud run services describe smart-assistant \
  --region=us-central1 \
  --format="value(spec.template.spec.containers[0].env)"
```

---

## 6. Truy cập ứng dụng

Mở URL do Cloud Run cung cấp, ví dụ:

```
https://smart-assistant-602021543026.us-central1.run.app/
```

---

## 7. Chi phí & Quy mô

Giả sử mỗi request tiêu tốn \~1 000 token (prompt + response), Gemini 1.5 Pro có giá:

* **Input**: \$1.25 / 1 000 000 token
* **Output**: \$5.00 / 1 000 000 token

→ **Tổng** ≈ \$0.00625 / request

| Users × calls        | Requests | Chi phí API (USD)          |
| -------------------- | -------- | -------------------------- |
| 100 users × 1 call   | 100      | 100 × \$0.00625 = \$0.63   |
| 100 users × 10 calls | 1 000    | 1 000 × \$0.00625 = \$6.25 |

### Ngân sách \$500 000

* Requests tối đa ≈ \$500 000 / \$0.00625 ≈ **80 000 000 requests**
* Nếu mỗi user 10 requests/tháng → hỗ trợ ≈ **8 000 000 user**

---

## 8. Tối ưu chi phí & Cấu hình đề xuất

Mặc định:

```python
generation_config = {
  "temperature": 0.2,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 20480,
}
```

**Đề xuất** để giảm chi phí:

```diff
 generation_config = {
   "temperature": 0.2,
-  "top_p": 0.95,
+  "top_p": 0.9,
   "top_k": 40,
-  "max_output_tokens": 20480,
+  "max_output_tokens": 2048,
 }
```

* Giảm `max_output_tokens` từ 20 480 → 2 048
* Hạ `top_p` từ 0.95 → 0.9

Vẫn giữ độ chi tiết đủ dùng, nhưng tiết kiệm \~90% chi phí trong worst-case.

---

## 9. Ngân sách 500 000 VND & Quy mô (50 lượt/người/tuần)

* **Chi phí/request** ≈ 0.00625 USD ≈ 150 VND
  (tỷ giá 1 USD = 24 000 VND)
* Mỗi user dùng 50 requests/tuần

```
500 000 VND / 150 VND/request ≈ 3 333 requests
3 333 requests / 50 requests/user ≈ 66 users
```

> **Kết luận**: với 500 000 VND, ngân sách đủ cho \~66 người dùng, mỗi người 50 lượt/tuần.

---

**Lưu ý chung**

* Không commit file chứa API key vào repo.
* Luôn quản lý `GEMINI_API_KEY` qua `--set-env-vars`.
* Theo dõi actual token usage (nếu có) để điều chỉnh cấu hình cho sát thực tế.

```
