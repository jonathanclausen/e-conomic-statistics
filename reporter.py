
import datetime as dt

class Reporter:
    
    def __init__(self, config, logger):
        self.logger = logger

    def build_html(self, customers, user, date, counts = {}):
        self.logger.info(f"building report for {user}")
        # Determine the first day of the current month
        first_day_of_current_month = date.replace(day=1)

        # Calculate the last day of the previous month
        last_day_of_previous_month = first_day_of_current_month - dt.timedelta(days=1)
        html = """
        <!doctype html><html lang="en">
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>New Customers</title>
            <style>
                body{
                    font-family: arial, sans-serif;}
                table {
                    font-family: arial, sans-serif;
                    border-collapse: collapse;
                    width: 100%;
                }

                td, th {
                    border: 1px solid #dddddd;
                    text-align: left;
                    padding: 8px;
                }

                tr:nth-child(even) {
                    background-color: #dddddd;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Customers registered in """+ last_day_of_previous_month.strftime("%B %Y") + """</h1>
                
                <p>Report for """ + user + """</p>
                <small>Report generated at: """ + str(date.strftime("%d-%m-%Y %H:%M:%S")) + """ </small>
                <br>
                <p>Total new customers in """ +last_day_of_previous_month.strftime("%B %Y") + """: """+ str(len(customers))+"""</p>

        """

        html += """
            <div>
                <h3>Totals</h3>
            """
        if counts:
            html += self.createCountsTable(counts)
            html += "<br><br>"
        html += self.createCustomerTable(customers)
        html += "</div>"
        html += """
            </div>
            
            </body>
        </html>
        """


        return html
    
    def createCustomerTable(self, customers):

        html = """
        <table class="table">
            <thead>
                <tr>
                <th scope="col">Number</th>
                <th scope="col">Name</th>
                <th scope="col">Employee</th>
                </tr>
            </thead>
            <tbody>"""
        for customer in customers:
            html += """
            <tr>
                <td>""" + str(customer['customerNumber']) + """</td>
                <td>""" + customer['name'] + """</td>
                <td>""" + customer['employeeName'] + """</td>
            </tr>"""
        html += """
        </tbody>
        </table>"""
        return html

    def createCountsTable(self, counts):
        if not counts:
            return
        
        html = """
        <table class="table">
            <thead>
                <tr>
                <th scope="col">Employee</th>
                <th scope="col"># of new customers</th>
                </tr>
            </thead>
            <tbody>"""
        for name,count in counts.items():
            html += """
            <tr>
                <td>""" + name + """</td>
                <td>""" + str(count) + """</td>
            </tr>"""
        html += """
        </tbody>
        </table>"""
        return html


