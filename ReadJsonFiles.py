import pandas as pd
import json
import os
#from openpyxl.workbook import Workbook

def readJson():

    df = pd.DataFrame(columns = ['Policy_ID'])

    path = 'D:\OsagoQuotes\db_log_port_5978'

    lenCetalog  = len(os.listdir(path))
    error_count = 0

    for fileName in os.listdir(path):

        with open(path + "\\" + fileName, "r") as read_file:

            try:
                data_json = json.load(read_file)

                PolicyID = data_json['PolicyId']
                df.loc[len(df)] = PolicyID
                print(str(lenCetalog) + " Policy id " + PolicyID)

                lenCetalog -= 1

            except:

                error_count += 1
                continue

    df.to_excel("D:\OsagoProject\Model" + "\\" + 'list_policy.xlsx')

    print('ERRORS: ' + str(error_count))

if __name__ == '__main__':
    readJson()

