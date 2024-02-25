import datetime
import sqlite3
import random
import string
import os
from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

DATABASE_FILE = "identifier.sqlite"
templates = Jinja2Templates(directory="templates")

app = FastAPI()

static_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "static")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
                        SELECT * FROM url_logs
                ''')
        urls = cursor.fetchall()
    return templates.TemplateResponse(name="index.html", context={"request": request, "urls": urls}
                                      )


@app.post("/shorten")
async def generate_url(request: Request, url: str = Form(...)):
    try:
        unique_key = create_unique_key()
        unique_id = unique_key
        time = datetime.datetime.now()
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                            INSERT INTO url_logs (og_url, key, creation_time, redirects)
                            VALUES (?, ?, ?, ?)
                    ''', (url, unique_key, str(time), 0))
            conn.commit()

        return templates.TemplateResponse(
            name="success.html", context={"request": request, "short_url": str(request.base_url) + f"{unique_key}"}
        )
    except sqlite3.Error as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail="Failed to shorten URL")


@app.get("/{key}", response_class=HTMLResponse)
def redirect_to_site(key: str, request: Request):
    data = (key,)
    query = "SELECT og_url FROM url_logs WHERE key=?;"
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(query, data)
        result = cursor.fetchone()

    if result:
        redirect_url = str(result[0])
        response = RedirectResponse(redirect_url, status_code=301)
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            query = "UPDATE url_logs SET redirects=redirects+1 WHERE key=?;"
            cursor.execute(query, data)
            conn.commit()
        return response
    else:
        return templates.TemplateResponse(name="site_not_found.html", status_code=404, context={"request": request})


# Helper functions
def create_unique_key():
    key = ""
    while len(key) <= 5:
        curr_char = random.choice(string.digits + string.ascii_letters)
        key = key + curr_char
    if check_key_exists(key):
        return create_unique_key()
    return key


def check_key_exists(column_value):
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT EXISTS (SELECT 1 FROM url_logs WHERE key = ?) AS entry_exists', (column_value,))
        result = cursor.fetchone()[0]
    return bool(result)
