import requests
from bs4 import BeautifulSoup
import pandas as pd


class FinanceReportScraper:
    def __init__(self, companyNames ) -> None:
        self.MAIN_URL = "https://www.biznesradar.pl"
        self.TYPE_OF_DATA = {
            "profitAndLoss" : "raporty-finansowe-rachunek-zyskow-i-strat",
            "balance" : "raporty-finansowe-bilans",
            "cashFlow" : "raporty-finansowe-przeplywy-pieniezne",
        }
        self.COMPANY_NAMES = companyNames

    def _readRawTable(self, company, data_type):
        url = self.MAIN_URL + "/" + data_type + "/" + company + ",Y"
        request = requests.get(url)
        raw_page = BeautifulSoup(request.content, 'html.parser')
        return raw_page.find("table", class_="report-table")

    def _getYearsData(self, raw_report_table):
        # Get meta data years (header of table)
        years_header = raw_report_table.find("tr") # First row
        years_th = years_header.find_all("th", class_="thq h")
        years = ["".join(y.text.split()) for y in years_th ]
        return years

    def _getData(self, raw_report_table):
        data_frame = {}
        
        for tr in raw_report_table.find_all("tr", attrs={"class":"premium-row"}): #Remove premium row 
            tr.decompose()

        bold_table = raw_report_table.find_all("tr", attrs={"class":"bold"})

        for bold_data_row in bold_table:

            row_name = bold_data_row.find("td", attrs={"class":"f"}).find("strong").text

            value = []
            for bold_data_td in bold_data_row.find_all("td", attrs={"class":"h"}):
                bold_data_value = bold_data_td.find("span", attrs={"class":"value"}).find("span", attrs={"class":"pv"})
                value.append("".join(bold_data_value.text.split()))

            data_frame[row_name] = value[:-1]

        return data_frame


    def getData(self):
        raw_page = self._readRawTable(self.COMPANY_NAMES[0], 
                                      self.TYPE_OF_DATA["profitAndLoss"])
        data = {"Rok": self._getYearsData(raw_page)}
        data.update(self._getData(raw_page))
        for type in (self.TYPE_OF_DATA["balance"], self.TYPE_OF_DATA["cashFlow"]):
            raw_page = self._readRawTable(self.COMPANY_NAMES[0], type)
            data.update(self._getData(raw_page))

        return data





com = ["ORLEN"]
frs = FinanceReportScraper(com)
dict_frame = frs.getData()

df = pd.DataFrame(dict_frame)
df.to_csv(com[0]+".csv", index=False)



