import api
import sys
import os
import json
import logging
import datetime as dt


TestMode = False
DIR = os.path.dirname(os.path.realpath(__file__)) + "/"


def createLogger(name):
    log_dir = DIR + 'logs'
    if not os.path.exists(log_dir):
       os.makedirs(log_dir)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(log_dir + '/e-conomic-statistics.log')
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)

    return logger


Logger = createLogger("Run")


f = open(DIR + 'config.json')
config = json.load(f)
f.close()

Logger.debug("Got configuration")




def run(current_date):

    if(current_date.day != 1):
        Logger.error(f'Can only run script on first of month. Current date is {current_date}')
        print("Script is only run on first day of month")
        exit()



    ec_api = api.Api(config, createLogger("Api"))
    customers = ec_api.getAllCustomers()

    # with open(DIR + "/data/customers.json", "w") as outfile:
    #     json.dump(customers, outfile)

    with open(DIR + "/data/customers.json", 'r') as customerFile:
        previousCustomers = json.load(customerFile)

        diff = []
        
        for cust in customers:
            if not any(x['customerNumber'] == cust['customerNumber'] for x in previousCustomers):
                print("hello");
                diff.append(cust)
        Logger.debug(f"Found {len(diff)} customer not already in json file")


    # Handle the differences and save the the new file.
        


if( len(sys.argv) > 1 and sys.argv[1] == "test"):
    print("Running in mode 'Test' ")
    TestMode = True
else:
    print("Running in mode 'Live'")


run(dt.datetime(2022,10,1))