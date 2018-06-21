import telebot
import time
from binance.client import Client
from binance.websockets import BinanceSocketManager
import sqlite3
import datetime
import sys


class Main:
    def __init__(self, login, password, token, room, percent, timing):
        self.login = str(login)
        self.password = str(password)
        self.token = str(token)
        self.room = str(room)
        self.percent = float(percent)
        self.timing = int(timing)
        self.mytime = time.time()
        self.previous_price = None
        self.current_price = None
        self.dict_for_database = {}

    def socket_manager(self):
        with sqlite3.connect('TAdb.db') as conn:

            db = conn.cursor()
            bot = telebot.TeleBot(self.token)

            def telegram_sender():
                percent_difference_for_pep8 = str(round(((100 * (self.previous_price - self.current_price))
                                                         / self.previous_price), 2)) + '%'
                bot.send_message(self.room, 'Current Bitcoin Price is : ' + str(self.current_price) + '$' '\n' +
                                 'Previous Price is : ' + str(self.previous_price) + '$' '\n' +
                                 'The difference is : ' + percent_difference_for_pep8)
            # Proccesing messages from socket binance

            def process_message(msg):
                if msg['e'] == 'error':
                    bm.close()
                    bm.start()
                else:
                    self.current_price = float(msg['p'])
            # Counting difference in percent between previous and current price

            def counting_difference():
                if float(((100 * (self.previous_price - self.current_price)) / self.previous_price)) > self.percent:
                    return True
                else:
                    return False
            # Just database SQL

            def adding_to_database(event):
                self.dict_for_database['time'] = int(time.time())
                self.dict_for_database['price'] = str(self.current_price)
                self.dict_for_database['event'] = str(str(event) + '{}%'.format(self.percent))
                db.execute('INSERT INTO price(time, price) VALUES ("{database[time]}", "{database[price]}")'.format(
                    database=self.dict_for_database))
                db.execute('INSERT INTO event(time, event) VALUES ("{database[time]}", "{database[event]}")'.format(
                    database=self.dict_for_database))
                conn.commit()
            # creating variables for current and previous prices, then in infinity loop adding events to database and if
            # necessary send to the Telegram

            def main_res():
                while True:
                    if self.current_price is not None:
                        self.previous_price = self.current_price
                        break
                    else:
                        time.sleep(0.1)
                while True:
                    if counting_difference():
                        adding_to_database('Price changed for more than ')
                        telegram_sender()
                        self.previous_price = self.current_price
                        time.sleep(self.timing)
                    elif not counting_difference():
                        adding_to_database('Price changed less than ')
                        self.previous_price = self.current_price
                        time.sleep(self.timing)
            # Just creating sockets
            bm = BinanceSocketManager([self.login, self.password])
            bm.start_trade_socket('BTCUSDT', process_message)
            bm.start()
            main_res()
            bm.close()


a = Main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])

a.socket_manager()
