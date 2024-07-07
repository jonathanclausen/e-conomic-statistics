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

    if(current_date.day != config['day_of_month_to_run']):
        Logger.error(f'Can only run script on day first of month. Current date is {current_date}')
        print("Script is only run on first day of month")
        exit()

    ec_api = api.Api(config, createLogger("Api"))
    customers = ec_api.getAllCustomers()
    diff = []

    with open(DIR + "/data/customers.json", 'r') as customerFile:
        # Save old file to new file with date attached
        previousCustomers = json.load(customerFile)

        with open(DIR + "/data/customers" + str(current_date.strftime("%d-%m-%Y%H:%M:%S")) + ".json", "w") as outfile:
            json.dump(previousCustomers, outfile)
        
        # Find differences in old and new files
        for cust in customers:
            if not any(x['customerNumber'] == cust['customerNumber'] for x in previousCustomers):
                
                diff.append(cust)
        Logger.debug(f"Found {len(diff)} customer not already in json file")

    # Write new with differences to customers.json
    with open(DIR + "/data/customers.json", "w") as outfile:
        json.dump(customers, outfile)
    
    # Get employee email addresses
    employees = ec_api.getEmployees()
    # Sanitize phone numbers

    employee_acquisitions = {}
    employee_emails = {}

    for emp in employees:
        if 'phone' in emp and 'email' in emp:
            emp['phone'] = emp['phone'].replace(" ", "").replace("+45", "")
            emp['email'] = emp['email'].lower()
            emp['isActive'] = True
            employee_emails[emp['name']] = emp['email']
            employee_acquisitions[emp['name']] = []
        else:
            emp['isActive'] = False
            if 'email' in emp:
                Logger.info(f"No phone number for employee: {emp['email']}")
            elif 'name' in emp:
                Logger.info(f"No phone number or email for employee: {emp['name']}")
            else:
                Logger.info(f"No phone number, email or name found for employee")


    # attach employees to customers
    for customer in diff:
        responsible_employee_id = customer['customerGroup']['customerGroupNumber']
        responsible_employee = next((x for x in employees if x['employeeNumber'] == responsible_employee_id), None)
        
        if (not responsible_employee): 
            Logger.error(f"No employee found with id: {responsible_employee_id}")
            continue
        if (not responsible_employee['isActive']):
            Logger.info(f"Found customer for non-active employee with id: {responsible_employee_id}. Set email and phone number in e-conomics to activate employee for report.")
            continue
        
        customer['employeeName'] = responsible_employee['name']
        
        if customer['employeeName'] in employee_acquisitions:
            employee_acquisitions[customer['employeeName']].append(customer)

    rep = reporter.Reporter(config, createLogger("Reporter"))

    # Create individual emails for customers
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
    mail_result("ff@auto-mow.com", totals_html)


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
    run(dt.datetime.now())

else:
    print("Running in mode 'Test' ")
    TestMode = True
    run(dt.datetime(2024,1,1,13,22,10))