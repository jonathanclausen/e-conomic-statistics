import api
import reporter
import sys
import os
import json
import logging
import datetime as dt

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from smtplib import SMTP_SSL as SMTP 
from email.mime.application import MIMEApplication
from os.path import basename

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

    diff = []

    with open(DIR + "/data/customers.json", 'r') as customerFile:
        previousCustomers = json.load(customerFile)

        
        
        for cust in customers:
            if not any(x['customerNumber'] == cust['customerNumber'] for x in previousCustomers):
                
                diff.append(cust)
        Logger.debug(f"Found {len(diff)} customer not already in json file")

    with open(DIR + "/data/customers.json", "w") as outfile:
        json.dump(customers, outfile)

    # Handle the differences and save the the new file.
    
    employees = ec_api.getEmployees()



    for customer in diff:
        responsible_employee_id = customer['customerGroup']['customerGroupNumber']
        responsible_employee = next((x for x in employees if x['employeeNumber'] == responsible_employee_id), None)
        
        if (not responsible_employee): Logger.Error(f"Could not find employee with id {responsible_employee_id}")

        customer['employeeName'] = responsible_employee['name']
        customer['employeeEmail'] = responsible_employee['email']

    employee_acquisitions = {emp['name']: [] for emp in employees }
    employee_emails = {emp['name']: emp['email'] for emp in employees }

    for customer in diff:
        
        if customer['employeeName'] in employee_acquisitions:
            employee_acquisitions[customer['employeeName']].append(customer)
        else: 
            Logger.error(f"Could not find employee {customer}")

    rep = reporter.Reporter(config, createLogger("Reporter"))

    for name,customers in employee_acquisitions.items():
        html = rep.build_html(customers,name, current_date)
        
        
        # Send html as email
        mail_result(employee_emails[name], html)

    # Creating totals email
    
    totals_list = []
    counts = {}
    for name,customers in employee_acquisitions.items():
        totals_list.extend(customers)
        counts[name] = len(customers)

    totals_list.sort(key=lambda x: x['employeeName'])
    totals_html = rep.build_html(totals_list, "All", current_date, counts)
    f = open("demo.html", "w")
    f.write(totals_html)
    f.close()

    # Save new file with date in title, so we save history
    # with open(DIR + "/data/customers.json", "w") as outfile:
    #     json.dump(customers, outfile)


def mail_result(recipient, body):

    if TestMode: recipient = "wordpress@concensur.dk"

    SMTPserver = 'smtp.simply.com'
    sender =     'Customer Report <reports@concensur.dk>'
    destination = recipient

    USERNAME = config['smtp_username']
    PASSWORD = config['smtp_password']
    

    subject="Customer Report"

    try:
        msg = MIMEMultipart()
        msg['Subject']= subject
        msg['From']   = sender # some SMTP servers will do this automatically, not all
        msg.add_header('reply-to', "wordpress@concensur.dk")

        msg.attach(MIMEText(body, 'html'))

        conn = SMTP(SMTPserver)
        conn.set_debuglevel(False)
        conn.login(USERNAME, PASSWORD)
        
        try:
            conn.sendmail(sender, destination, msg.as_string())
        finally:
            conn.quit()

    except Exception as e:
        sys.exit( "mail failed; %s" % e ) # give an error message




if( len(sys.argv) > 1 and sys.argv[1] == "live"):
    print("Running in mode 'Live' ")
    run(dt.datetime.now)

else:
    print("Running in mode 'Test' ")
    TestMode = True
    run(dt.datetime(2022,10,1))