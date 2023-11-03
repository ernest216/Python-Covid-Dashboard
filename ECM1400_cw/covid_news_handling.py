import sched
import time
import requests
from flask import request
from time_conver import hhmm_to_seconds, current_time_hhmm
import json 

global news

def read_config():
    f = open('config.json', "r")
    data = json.loads(f.read())
    api_key = data['news_api']
    return api_key

news_data = sched.scheduler(time.time, time.sleep)


def news_API_request(covid_terms="Covid COVID-19 coronavirus"):
    base_url = "https://newsapi.org/v2/everything?"
    api_key = read_config()
    keywords = "Covid&COVID-19&coronavirus&"
    language = "en&"
    sort = "publishedAt&"
    url = base_url + "qInTitle=" + keywords + "sortBy=" + sort + "language=" + language + "apiKey=" + api_key
    r = requests.get(url)
    return r.json()


def update_news():
    update_time = request.args.get("update")
    if update_time is not None:
        update_time_sec = hhmm_to_seconds(update_time)
        current_time_sec = hhmm_to_seconds(current_time_hhmm())
        update_interval = update_time_sec - current_time_sec
        text_field = request.args.get("news")
        if text_field == "news":
            sche_update_news(update_interval)


def add_news():
    global news
    news = []
    data = news_API_request()
    articles = data["articles"]
    title = []
    content = []
    for n in articles:
        title.append(n["title"])
        content.append(n["content"])
    for i in range(len(title)):
        news.append({
            "title": title[i],
            "content": content[i]
        })
    return news


def remove_news(news_title):
    global news
    for n in news:
        if n["title"] == news_title:
            news.remove(n)


def sche_update_news(update_interval):
    repeat_field = request.args.get("repeat")
    news_data.enter(update_interval, 1, add_news)
    if repeat_field == "repeat":
        news_data.enter(update_interval, 2, lambda: sche_update_news(24 * 60 * 60))
    news_data.run(blocking=False)