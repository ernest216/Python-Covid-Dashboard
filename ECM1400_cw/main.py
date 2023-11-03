import sched
import time
from covid_data_handler import schedule_covid_updates, add_covid_data, remove_update
from covid_news_handling import news_API_request, update_news, remove_news, add_news
from flask import Flask, request
from flask import render_template
from time_conver import hhmm_to_seconds, current_time_hhmm


global news
global local_location, local_7day_infections, national_location, national_7day_infections, hospital_cases, total_deaths
global update

news_data = sched.scheduler(time.time, time.sleep)
covid_data = sched.scheduler(time.time, time.sleep)
app = Flask(__name__, static_url_path='/static')


news = add_news()
local_location, local_7day_infections, national_location, national_7day_infections, hospital_cases, total_deaths = add_covid_data()


@app.route('/index')
def web():
    global update
    update = []
    update_news()
    news_title = request.args.get("notif")
    if news_title is not None:
        remove_news(news_title)
    if request.args.get('two') is not None and request.args.get('update') is not None and request.args.get(
            'update') != '':
        update.append(
        schedule_covid_updates(update_interval=request.args.get('update'), update_name=request.args.get('two')))
    update_name = request.args.get("update")
    if update_name is not None:
        remove_update(update_name)
    return render_template(
        'index.html',
        title='Daily update',
        news_articles=news[0:4],
        location=local_location,
        local_7day_infections=local_7day_infections,
        nation_location=national_location,
        national_7day_infections=national_7day_infections,
        hospital_cases=hospital_cases,
        deaths_total=total_deaths,
        updates=update,
        image='covid.jpg'
    )


if __name__ == '__main__':
    app.run()
