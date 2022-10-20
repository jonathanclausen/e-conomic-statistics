import api
import sys
import os
import json
import logging
import datetime as dt


TestMode = False
DIR = os.path.dirname(os.path.realpath(__file__)) + "/"


def setup_logging():
    log_dir = DIR + 'logs'
    if not os.path.exists(log_dir):
       os.makedirs(log_dir)

    logging.basicConfig(filename= log_dir + '/e-conomic-statistics.log', filemode='a', format='%(name)s - %(levelname)s - %(message)s')

setup_logging()


f = open(DIR + 'config.json')
config = json.load(f)
f.close()


def run(current_date):

    if(current_date.day != 1):
        logging.error('Watch out!')
        print("Script is only run on first day of month")
        exit()


    ec_api = api.Api(config)
    customers = ec_api.getAllCustomers()





if( len(sys.argv) > 1 and sys.argv[1] == "test"):
    print("Running in mode 'Test' ")
    TestMode = True
else:
    print("Running in mode 'Live'")


run(dt.datetime(2022,10,1))