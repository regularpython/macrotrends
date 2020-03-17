import RequestBot
import re
from bs4 import BeautifulSoup
import demjson
import pandas as pd
from datetime import datetime
import os
import concurrent.futures
import local_env

class MacroTrends(RequestBot.Bot):
    def __init__(self):
        pass

    def get_macrotrends_json_data(self, record):
        today = datetime.now().strftime('%m-%d-%Y')
        if self.response:
            jsoup = BeautifulSoup(self.response.content)
            data = re.search(r"var\s+originalData.*", str(jsoup), re.DOTALL | re.MULTILINE | re.VERBOSE)
            if data:
                data = data.group(0).split('\n')[0].replace('var originalData = ', '').strip().strip(';')
                data = demjson.decode(data)
                row_data = []
                for k in data:

                    for key, value in k.items():
                        if key in ['field_name', 'popup_icon']:
                            continue
                        dummy_dict = dict()
                        dummy_dict['parameter'] = BeautifulSoup(k.get('field_name')).text
                        dummy_dict['date'] = key
                        dummy_dict['value'] = value
                        dummy_dict['Ticker'] = record.get('Ticker')
                        dummy_dict['Company'] = record.get('Company')
                        dummy_dict['Type'] = record.get('statement')
                        dummy_dict['Financial Type'] = record.get('freq')
                        dummy_dict['Created Date'] = today
                        row_data.append(dummy_dict)

                return row_data

def load_data(company):
    today = datetime.now().strftime('%m-%d-%Y')
    folder_path = local_env.output_path + today
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    print(company)
    final_data = []
    for statement in ['income-statement', 'balance-sheet', 'cash-flow-statement', 'financial-ratios']:
        for freq in ['A', 'Q']:
            url = f'https://www.macrotrends.net/stocks/charts/{company["Ticker"]}/{company["Company"]}/{statement}?freq={freq}'
            print(url)
            mt = MacroTrends()
            mt.scrper_url = url
            mt.load_response_get()
            company['statement'] = statement
            company['freq'] = freq
            results = mt.get_macrotrends_json_data(company)
            if results:
                final_data.extend(results)

    if final_data:
        pd.DataFrame(final_data).to_csv(
            f'{folder_path}\\{today}-{company["Ticker"]}-{company["Company"]}-macrotrends data.csv', index=False)

    return company["Ticker"]


if __name__ == '__main__':
    companies = pd.read_csv('companies_list.csv').to_dict(orient='records')

    import time

    time_start = time.perf_counter()

    # for company in companies:
    #     load_data(company)



    # We can use a with statement to ensure threads are cleaned up promptly
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # Start the load operations and mark each future with its URL
        future_to_url = {executor.submit(load_data, company): company for company in companies}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                companie_name = future.result()
            except Exception as exc:
                print('%r generated an exception: %s' % (url, exc))
            else:
                print(companie_name, 'Downloaded.')

    time_elapsed = (time.perf_counter() - time_start)
    print("%5.1f secs" % (time_elapsed))

