import logging
import os
import random
import sys
import time

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from sqlalchemy import create_engine  
from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base  
from sqlalchemy.orm import sessionmaker


db_string = "I don't want show may db link, sorry"

db = create_engine(db_string)  
base = declarative_base()

class Username(base):  
    __tablename__ = 'usernames'

    username = Column(String, primary_key=True)
    amount = Column(Integer)
    
Session = sessionmaker(db)
session = Session()

base.metadata.create_all(db)

# Enabling logging
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

# Getting mode, so we could define run function for local and Heroku setup
mode = os.getenv("MODE")
TOKEN = os.getenv("TOKEN")
if mode == "dev":
    def run(updater):
        updater.start_polling()
elif mode == "prod":
    def run(updater):
        PORT = int(os.environ.get("PORT", "8443"))
        HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
        updater.start_webhook(listen="0.0.0.0",
                              port=PORT,
                              url_path=TOKEN)
        updater.bot.set_webhook("https://{}.herokuapp.com/{}".format(HEROKU_APP_NAME, TOKEN))
else:
    logger.error("No MODE specified!")
    sys.exit(1)


def is_row(username):
    global session
    return session.query(Username).filter_by(username=username).scalar() is not None

def create_row(username, amount):
    global session
    row = Username(username=username, amount=amount)
    session.add(row)  
    session.commit()

def update_row(username, amount):
    global session
    row = session.query(Username).filter_by(username=username).first()
    row.amount = amount
    session.commit()

def start_handler(bot, update):
    # Creating a handler-function for /start command 
    logger.info("User {} started bot".format(update.effective_user["id"]))
    print(update.message.from_user.username)
    update.message.reply_text("Привет, Андрей!\nНу как ты там?")
    time.sleep(2.4)
    update.message.reply_text("Андрю")
    time.sleep(1)
    update.message.reply_text("ша")
    time.sleep(1.5)
    update.message.reply_text("Сколько бабла ты у меня спиздил?")


def random_handler(bot, update):
    # Creating a handler-function for /random command
    number = random.randint(0, 10)
    logger.info("User {} randomed number {}".format(update.effective_user["id"], number))
    update.message.reply_text("Random number: {}".format(number))

def text_handler(bot, update):

    message = update.message.text

    if message.lower() == "алло":

        start_handler(bot, update)

    elif message.isdigit():

        number = int(message)

        if number <= 100:
            update.message.reply_text("Это мало, пшёл на хуй!")
        elif number > 100 and number <= 10000:
            update.message.reply_text("Заебись так спиздил!")
        else:
            update.message.reply_text("Это пиздец дохуя!")
        
        username = update.message.from_user.username

        if is_row(username):
            update_row(username, number)
            print('update', number)
        else:
            create_row(username, number)
            print('create', number)
        
        time.sleep(1)
        update.message.reply_text("Я не пойду к ментам...")

    else:

        update.message.reply_text("Пиши число, сука!")


if __name__ == '__main__':
    logger.info("Starting bot")
    updater = Updater(TOKEN)

    updater.dispatcher.add_handler(CommandHandler("start", start_handler))
    updater.dispatcher.add_handler(CommandHandler("random", random_handler))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, text_handler))

    run(updater)
