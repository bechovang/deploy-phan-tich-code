````markdown
# Hướng dẫn Deploy “Trợ lý Lập trình” lên Google Cloud Run

## 1. Cấu hình gcloud và chọn dự án
```bash
gcloud init
# – Chọn cấu hình mới hoặc re-init
# – Chọn tài khoản Google của bạn
# – Chọn “Enter a project ID” hoặc “Create a new project”
# – Nhập PROJECT_ID (ví dụ ai-phan-tich-code)
````

## 2. Bật các API cần thiết

```bash
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  --project=ai-phan-tich-code
```

## 3. Deploy ứng dụng bằng Buildpacks

```bash
gcloud run deploy smart-assistant \
  --project=ai-phan-tich-code \
  --region=us-central1 \
  --source=. \
  --allow-unauthenticated \
  --set-env-vars=GEMINI_API_KEY=<YOUR_GEMINI_API_KEY>
```

* `--source=.`: dùng Buildpacks để tự build container từ code Python/Flask.
* `--allow-unauthenticated`: cho phép bất kỳ ai truy cập.
* `--set-env-vars=GEMINI_API_KEY=...`: truyền API key vào container.

## 4. Cập nhật biến môi trường (nếu cần)

```bash
gcloud run services update smart-assistant \
  --region=us-central1 \
  --set-env-vars=GEMINI_API_KEY=<NEW_GEMINI_API_KEY>
```

Chỉ thay đổi key mà không phải redeploy toàn bộ.

## 5. Kiểm tra biến môi trường hiện tại

```bash
gcloud run services describe smart-assistant \
  --region=us-central1 \
  --format="value(spec.template.spec.containers[0].env)"
```

## 6. Truy cập ứng dụng

Mở URL do Cloud Run cung cấp (ví dụ):

```
https://smart-assistant-602021543026.us-central1.run.app/
```

---

**Ghi chú:**

* Không commit file `.env` chứa key vào repo.
* Luôn dùng `--set-env-vars` để truyền `GEMINI_API_KEY`.
* Nếu cần tùy chỉnh sâu hơn, có thể bổ sung Dockerfile và dùng `gcloud builds submit` + `gcloud run deploy --image`.

```
```
