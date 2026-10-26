# Supreme-inspired FastAPI frontend

A lightweight, dependency-free frontend inspired by the supplied screenshot: black canvas, centered red wordmark, compact monospace menu, muted social icons, and a minimal page view. It is an original implementation inspired by the reference rather than an official Supreme site.

## Run it

1. Start your FastAPI backend, for example:
   ```bash
   uvicorn src.main:app --reload
   ```
2. Make sure CORS allows the frontend origin. For the command below, that is `http://localhost:5500` and `http://127.0.0.1:5500`.
3. In this folder, run:
   ```bash
   python3 -m http.server 5500
   ```
4. Open `http://localhost:5500`.
5. If your API is not at `http://127.0.0.1:8000`, click the faint `+` in the lower-right corner and set the API base URL.

## API integration

- `POST /setup_database`: database setup button in Page Tools.
- `POST /add_page`: create a page.
- `GET /get_page?page_id=...`: open/load one page.
- `GET /get_current`: populate News, preview/lookbook filtering, and Random.
- `GET /about` and `GET /contact`: render those endpoint responses.
- `PATCH /patch?page_id=...`: update a page.

The frontend assumes page fields are named `page_id`, `title`, and `main_text`, and that `AddPage_scheme` / `Page_Update_scheme` accept `title` and `main_text`. If your schemas differ, change the JSON/query payload in `app.js` to match. The `shop`, `stores`, and mailing-list entries are placeholders because the provided backend has no endpoints for those features.
