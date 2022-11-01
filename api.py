import requests

class Api:

    def __init__(self, config, logger):
        self.application_grant = config['api_credentials']['X-AgreementGrantToken']
        self.application_token = config['api_credentials']['X-AppSecretToken']
        self.base_url = "https://restapi.e-conomic.com/"
        
        self.session = requests.Session()
        self.session.headers.update(config['api_credentials'])

        self.logger = logger
    
    def getAllCustomers(self):
        self.logger.info("getAllCustomers")
        
        customers = []
        
        url = self.base_url + 'customers?pageSize=1000'

        result = self.session.get(url).json()
        customers.extend(result['collection'])

        while ('nextPage' in result['pagination']):
            next_page = result['pagination']['nextPage']
            result = self.session.get(next_page).json()

            customers.extend(result['collection'])
            
            
        
        self.logger.info(f'Found {len(customers)} customers')
        return customers
    
    def getEmployees(self):
        self.logger.info("GetEmployees")
        employees = []
        
        url = self.base_url + 'employees?pageSize=100'

        result = self.session.get(url).json()
        employees.extend(result['collection'])

        while ('nextPage' in result['pagination']):
            next_page = result['pagination']['nextPage']
            result = self.session.get(next_page).json()

            employees.extend(result['collection'])
            
            
        
        self.logger.info(f'Found {len(employees)} employees')
        return employees
        