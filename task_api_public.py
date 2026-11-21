from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
import sqlite3

app = FastAPI()

DB_FILE = "tasks.db"

conn = sqlite3.connect(DB_FILE)
conn.execute("CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, time TEXT, done INTEGER)")
conn.commit()
conn.close()

class TaskIn(BaseModel):
    title: str
    time: str

# 公開用のダミーデータ
tasks = [
    {"id": 1, "title": "確認A", "time": "08:00", "done": False},
    {"id": 2, "title": "設定A", "time": "08:00", "done": False},
    {"id": 3, "title": "送信A", "time": "08:40", "done": False},
    {"id": 4, "title": "記帳A", "time": "08:40", "done": False},
    {"id": 5, "title": "受け取りA", "time": "11:00", "done": False},
    {"id": 6, "title": "メールチェックA", "time": "11:30", "done": False},
    {"id": 7, "title": "システムチェックA", "time": "11:30", "done": False},
    {"id": 8, "title": "システムチェックB", "time": "11:30", "done": False},
    {"id": 9, "title": "システムチェックC", "time": "11:30", "done": False},
    {"id": 10, "title": "システムチェックD", "time": "11:30", "done": False},
    {"id": 11, "title": "システムチェックE", "time": "11:30", "done": False},
    {"id": 12, "title": "システムチェックF", "time": "11:30", "done": False},
    {"id": 13, "title": "遠隔管理A", "time": "11:30", "done": False},
    {"id": 14, "title": "部屋チェックA", "time": "11:30", "done": False},
    {"id": 15, "title": "記帳B", "time": "11:30", "done": False},
    {"id": 16, "title": "機器再起動A", "time": "11:50", "done": False},
    {"id": 17, "title": "巡回A", "time": "15:00", "done": False},
    {"id": 18, "title": "回収A", "time": "15:00", "done": False},
    {"id": 19, "title": "設定B", "time": "18:00", "done": False},
    {"id": 20, "title": "温度チェックA", "time": "毎時", "done": False},
    {"id": 21, "title": "メールチェックB", "time": "毎時", "done": False},
    {"id": 22, "title": "監視チェックA", "time": "毎時", "done": False},
    {"id": 23, "title": "メールチェックC", "time": "毎時", "done": False},
    {"id": 24, "title": "容量チェックA", "time": "8・13・16時", "done": False},
    {"id": 25, "title": "メールチェックD", "time": "8・13・16時", "done": False},
    {"id": 26, "title": "連絡チェックA", "time": "8・13・16時", "done": False},
]

conn = sqlite3.connect(DB_FILE)
count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
if count == 0:
    for m in tasks:
        conn.execute("INSERT INTO tasks (title, time, done) VALUES (?, ?, 0)", (m["title"], m["time"]))
    conn.commit()
conn.close()

@app.get("/tasks")           #タスク一覧/時間検索
def get_tasks(time: str = None):
    conn = sqlite3.connect(DB_FILE)
    rows = conn.execute("SELECT id, title, time, done FROM tasks").fetchall()
    conn.close()
    result = []        
    for row in rows:
        if time is None or row[2] == time:
            result.append({"id": row[0], "title": row[1], "time": row[2], "done": bool(row[3])})
    return {"tasks": result}

@app.post("/tasks")           #タスク追加
def add_tasks(new_task: TaskIn):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.execute("INSERT INTO tasks (title, time, done) VALUES (?, ?, 0)", (new_task.title, new_task.time))
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return {"id": new_id, "title": new_task.title, "time": new_task.time, "done": False}

@app.get("/tasks/{num}")           #タスク検索
def select_num_tasks(num: int):
    conn = sqlite3.connect(DB_FILE)
    select = conn.execute("SELECT * FROM tasks WHERE id = ?", (num,)).fetchone()
    conn.close()
    if select is None:
        raise HTTPException(status_code=404, detail='そのタスクは見つかりません')
    return {"id": select[0], "title": select[1], "time": select[2], "done": bool(select[3])}

@app.put("/tasks/{num}/done")           #タスク完了
def done_task(num: int):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.execute("UPDATE tasks SET done = 1 WHERE id = ?", (num,))
    conn.commit()
    conn.close()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail='そのタスクは見つかりません')
    return {"message": "完了にしました"}

@app.put("/tasks/{num}/undo")           #タスク未完了
def reset_task(num: int):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.execute("UPDATE tasks SET done = 0 WHERE id = ?", (num,))
    conn.commit()
    conn.close()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail='そのタスクは見つかりません')
    return {"message": "完了を取り消しました"}

@app.put("/tasks/reset")                   #タスクリセット
def reset_all_task():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.execute("UPDATE tasks SET done = 0")
    conn.commit()
    conn.close()
    return {"message": f"{cur.rowcount}件のタスクを未完了にしました"}

@app.delete("/tasks/{num}/del")           #タスク削除
def del_task(num: int):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.execute("DELETE FROM tasks WHERE id = ?", (num,))
    conn.commit()
    conn.close()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail='そのタスクは見つかりません')
    return {"message": "タスクを削除しました"}
