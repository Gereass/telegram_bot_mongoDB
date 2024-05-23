#!venv/bin/python3
import datetime, json, os, asyncio, telebot, logging
# import srez_day_work
from pymongo.mongo_client import MongoClient
from dotenv import load_dotenv
from dateutil.relativedelta import relativedelta
from telebot.async_telebot import AsyncTeleBot
from collections import OrderedDict, defaultdict
from datetime import timedelta, date


class EmptyJsonClientError(Exception):
    pass

TELEGRAM_TOKEN = 'TELEGRAM_TOKEN' #os.environ.get('TELEGRAM_TOKEN')
MONGODB_URI = 'mongodb://localhost:27017/'
COLLECTION_NAME = 'sample_collection'
DATABASE_NAME = 'test'



TYPE_GROUPS = {'month': relativedelta(months=1), 'day': relativedelta(days=1), 'hour': relativedelta(hours=1)}
EXAMPLE = """\
{
   "dt_from": "2022-09-01T00:00:00",
   "dt_upto": "2022-12-31T23:59:00",
   "group_type": "month"
}
    """

def json_response(dt_from, dt_upto, group_type):
    total_by_day_and_month = OrderedDict()
    total_by_month = OrderedDict()
    month_day_local = OrderedDict()
    day_hour_local = OrderedDict()
    month_yar_local = []
    all_day_in_month = []
    all_hour = [num for num in range(24)]
    total_by_day_and_hour = {}
    current_day = None
    current_month = None
    current_hour = None
    current_sum = 0
    
    with MongoClient(MONGODB_URI) as client:
        mydb = client["dump"]
        # mycol = mydb["workers"]
        db = client[DATABASE_NAME]
        collections = db[COLLECTION_NAME]   
        # summ = 0

        first_date = datetime.datetime.fromisoformat(dt_from)
        last_date = datetime.datetime.fromisoformat(dt_upto)

        query = {'dt': {'$gte': first_date, '$lte': last_date}}
        result = collections.find(query)

        '''-------------------------------------------'''
        def count_days_in_interval(first_date: date, last_date: date) -> dict:
            days_in_intervals = defaultdict(lambda: 0)
            current_date = first_date

            while current_date <= last_date:
                interval_tuple = (current_date.year, current_date.month)
                days_in_intervals[interval_tuple] += 1
                current_date += timedelta(days=1)

            sorted_days_in_intervals = sorted(days_in_intervals.items(), key=lambda item: (item[0][0], item[0][1]))
            return sorted_days_in_intervals

        cout_day = count_days_in_interval(first_date, last_date)
        """тут можно переделать 2 цикла на более локаничное описание"""
        for i in range(len(cout_day)):
            month_day_local[cout_day[i][0][1]] = cout_day[i][1]
            month_yar_local.append(cout_day[i][0])
        
        month_local = list(month_day_local.items())
        
        for a in month_local:
            for d in range(1, a[1]+1):
                all_day_in_month.append((a[0],d))

        if group_type == 'day':
            for record in result:
                dt = record["dt"]
                day = dt.day
                month = dt.month
                year = dt.year
                '''1--------------------------------/'''
                if month != current_month or day != current_day:
                    if current_month is not None and current_day is not None:
                        if (current_month, current_day) not in total_by_day_and_month:
                            total_by_day_and_month[(current_month, current_day)] = 0
                        total_by_day_and_month[(current_month, current_day)] += current_sum
                        current_sum = 0
                    
                    current_month = month
                    current_day = day
                current_sum += record["value"]

            if current_month is not None and current_day is not None:
                if (current_month, current_day) not in total_by_day_and_month:
                    total_by_day_and_month[(current_month, current_day)] = 0
                total_by_day_and_month[(current_month, current_day)] += current_sum

            sort_day = OrderedDict(sorted(total_by_day_and_month.items()))

            keys, values = zip(*sort_day.items())
            keys = [(k0, k1) for k0, k1 in keys]

            if len(total_by_day_and_month) != len(all_day_in_month):
                for i in all_day_in_month:
                    if i not in keys:
                        sort_day[i] = 0
                        
            final_data = OrderedDict(sorted(sort_day.items()))
            final_data=list(final_data.values())

            '''1-------------------------------------------'''
        elif group_type == 'month':
            '''2-------------------------------------------'''
            for record in result:
                dt = record["dt"]
                month = dt.month
                year = dt.year

                if month != current_month:
                    current_month = month
                
                if year != current_month:
                    current_year = year
                if (current_year, current_month) not in total_by_month:
                    total_by_month[(current_year, current_month) ] = 0
                total_by_month[(current_year, current_month) ] += record["value"]

            sort_month = OrderedDict(sorted(total_by_month.items()))

            keys_month, values = zip(*sort_month.items())
            keys_month = [(k0, k1) for k0, k1 in keys_month]

            if len(total_by_month) != len(month_yar_local):
                for i in total_by_month:
                    if i not in keys_month:
                        sort_month[i] = 0

            final_data = OrderedDict(sorted(sort_month.items()))
            final_data=list(final_data.values())
            '''2-------------------------------------------'''
        elif group_type == 'hour':
            '''3-------------------------------------------'''
            def generate_dates_range(first_date, last_date, interval):
                date_range = []
                current_date = first_date

                while current_date <= last_date:
                    date_range.append(current_date)
                    current_date += interval

                return date_range

            def format_date(date):
                return ((date.month, date.day, date.hour))

            def hours_vector_ordereddict(first_date, last_date):
                dates_range = generate_dates_range(first_date, last_date, datetime.timedelta(hours=1))
                vector = OrderedDict()

                for date in dates_range:
                    formatted_date = format_date(date)
                    vector[formatted_date] = 0

                return vector

            hours_vector_ordereddict_result = hours_vector_ordereddict(first_date, last_date)

            """//"""
            def count_days_in_interval(first_date: date, last_date: date) -> dict:
                days_in_intervals = defaultdict(lambda: 0)
                current_date = first_date

                while current_date <= last_date:
                    interval_tuple = (current_date.year, current_date.month)
                    days_in_intervals[interval_tuple] += 1
                    current_date += timedelta(days=1)

                sorted_days_in_intervals = sorted(days_in_intervals.items(), key=lambda item: (item[0][0], item[0][1]))
                return sorted_days_in_intervals

            cout_day = count_days_in_interval(first_date, last_date)

            for i in range(len(cout_day)):
                month_day_local[cout_day[i][0][1]] = cout_day[i][1]

            month_local = list(month_day_local.items())

            for a in month_local:
                for d in range(1, a[1]+1):
                    all_day_in_month.append((a[0],d))

            for i in all_day_in_month:
                for h in all_hour:
                    day_hour_local[i] = h


            for record in result:
                dt = record["dt"]
                day = dt.day
                hour = dt.hour
                month = dt.month


                if day != current_day or hour != current_hour or month != current_month:
                    if current_day is not None and current_hour is not None and current_month is not None:
                        if (current_month, current_day, current_hour) not in total_by_day_and_hour:
                            total_by_day_and_hour[(current_month, current_day, current_hour)] = 0
                        total_by_day_and_hour[(current_month, current_day, current_hour)] += current_sum
                        current_sum = 0
                    current_day = day
                    current_hour = hour
                    current_month = month

                current_sum += record["value"]

            if current_day is not None and current_hour is not None and current_month is not None:
                if (current_month, current_day, current_hour) not in total_by_day_and_hour:
                    total_by_day_and_hour[(current_month, current_day, current_hour)] = 0
                total_by_day_and_hour[(current_month, current_day, current_hour)] += current_sum

            sort_hour = OrderedDict(sorted(total_by_day_and_hour.items()))
            if len(hours_vector_ordereddict_result) != len(sort_hour):
                for i in hours_vector_ordereddict_result:
                    if i not in sort_hour:
                        sort_hour[i] = 0
                        
            final_data = OrderedDict(sorted(sort_hour.items()))
            final_data=list(final_data.values())
            '''3-------------------------------------------'''
        for doc in result:                
                summ = summ+doc['value']
        added_date = TYPE_GROUPS[group_type]

        result = {"dataset": final_data, "labels": []}

        while first_date <= last_date:
            result["labels"].append(first_date.isoformat())
            first_date += added_date

        client.close()

        return json.dumps(result)

def validate_json(query):
    try:
        js_data = json.loads(query)
        if not js_data:
            raise EmptyJsonClientError

        dt_from = js_data["dt_from"]
        dt_upto = js_data["dt_upto"]
        group_type = js_data["group_type"]

    except json.JSONDecodeError:
        return 'Not json data. For example:\n%s' % EXAMPLE
    except EmptyJsonClientError:
        return 'Empty json data. For example:\n%s' % EXAMPLE
    except KeyError:
        return 'Invalid query. For example:\n%s' % EXAMPLE
    else:
        return json_response(dt_from, dt_upto, group_type)

load_dotenv()

bot = AsyncTeleBot(TELEGRAM_TOKEN)
logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

@bot.message_handler(commands=['help', 'start'])
async def send_welcome(message):
    msg = """Hi there, I accept the request in json format and send the json response. 
Input query for example:\n%s""" % EXAMPLE
    await bot.reply_to(message, msg)


@bot.message_handler(func=lambda message: True)
async def echo_message(message):
    result = validate_json(message.text)
    await bot.reply_to(message, result)


if __name__ == '__main__':
    asyncio.run(bot.polling())