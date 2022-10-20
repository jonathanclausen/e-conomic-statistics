import requests

class Api:

    def __init__(self, config):
        self.application_grant = config['api_credentials']['X-AgreementGrantToken']
        self.application_token = config['api_credentials']['X-AppSecretToken']
        self.base_url = "https://restapi.e-conomic.com/"
        
        self.session = requests.Session()
        self.session.headers.update(config['api_credentials'])
    
    def getAllCustomers(self):
        customers = {}

        url = self.base_url + 'customers'

        customers = self.session.get(url).json()
        print(customers)
        