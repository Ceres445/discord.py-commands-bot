import os
from dotenv import load_dotenv
import datetime


def load_vars():
    """Load heroku/ qovery/ local environment variables"""
    try:
        print(os.environ.get('DATABASE_URL'), os.environ.get('TOKEN'), os.environ.get('TZ'))
        postgres = os.environ['DATABASE_URL']
        token = os.environ['TOKEN']
        print("time is ", datetime.datetime.now())
        print('loaded heroku env variables')
    except KeyError:
        try:
            postgres = os.environ['QOVERY_DATABASE_BOT_CONNECTION_URI']
            token = os.environ['token']
            print('loaded qovery variables')
        except KeyError:
            load_dotenv()
            print('loaded local dotenv file')
            token = os.environ['TOKEN']
    return postgres, token
