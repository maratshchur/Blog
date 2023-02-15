import redis
import datetime as dt
from fastapi import FastAPI
from fastapi import Query
app = FastAPI()

r = redis.Redis(host='localhost', port=6379, db=0)


@app.post("/create")
def create_blog_post(theme: str = Query(min_length=1, max_length=50),
                     title: str = Query(min_length=1, max_length=50),
                     content: str = Query(min_length=1),
                     author: str = Query(min_length=1, max_length=50)):

    # генерируем id для поста
    post_id = r.incr("blog:current_post_id")
    time = dt.datetime.now()
    last_change_time = time.strftime("%m/%d/%Y , %H:%M:%S")
    # сохраняем данные поста в Redis

    try:
        r.hset(post_id, "Theme", theme)
        r.hset(post_id, "Title", title)
        r.hset(post_id, "Content", content)
        r.hset(post_id, "Author", author)
        r.hset(post_id, "Changed", last_change_time)
        return {"message": "Post created successfully", "post_id": post_id}

    except redis.exceptions.RedisError:
        r.decr("blog:current_post_id")
        return {"success": False, "error": "Failed to create post"}


@app.put("/update/{post_id}")
def update_blog_post(post_id: str = Query(min_length=1, max_length=40),
                     theme: str = Query(min_length=1, max_length=50),
                     title: str = Query(min_length=1, max_length=50),
                     content: str = Query(min_length=1),
                     author: str = Query(min_length=1, max_length=50)):
    # обновляем данные поста в Redis

    post = r.hgetall(post_id)
    if post:
        time = dt.datetime.now()
        last_change_time = time.strftime("%m/%d/%Y , %H:%M:%S")
        r.hset(post_id, "Theme", theme)
        r.hset(post_id, "Title", title)
        r.hset(post_id, "Content", content)
        r.hset(post_id, "Author", author)
        r.hset(post_id, "Changed", last_change_time)
        return {"message": "Post updated successfully"}

    else:
        return {"message": "Post not found"}


@app.get("/view/{post_id}")
def view_blog_post(post_id: str):
    # получаем данные поста из Redis
    post = r.hgetall(post_id)
    if post:
        return post
    else:
        return {"message": "Post not found"}


@app.delete("/delete/{post_id}")
def delete_blog_post(post_id: str):
    # удаляем пост из Redis
    post = r.hgetall(post_id)
    if post:
        r.delete(post_id)
        return {"status": "success"}
    else:
        return {"message": "Post not found"}
