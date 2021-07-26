import pandas as pd
import numpy as np
# import json
# import openpyxl

def get_CID(id, planilha):

    data = pd.read_excel(str(planilha))

    for loop in range(len(data.ID)):
        if int(id) == data.ID[loop]:
            return data.IDC[loop]

print(get_CID(18230430706012000,'campanhas\Campanhas - Junho 21.xlsx'))
