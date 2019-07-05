#ver. model 0.25

from flask import Flask, request, jsonify
from flask_restful import reqparse, abort, Api, Resource
import json
import h2o
import sys
import traceback
import pandas as pd
import pyodbc
import datetime
import LogFile as log
import pprint

now = datetime.datetime.now()

app = Flask(__name__)
api = Api(app)

# опробуем подключение к рабочему столу

server   = log.server
database = log.database
username = log.username
password = log.password

print('Connect...')
print('SERVER = ' + server)
print('DATABASE = ' + database)
print('UID = ' + username)
print(' ')

cnxn   = pyodbc.connect('DRIVER={SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
cursor = cnxn.cursor()

h2o.init(nthreads = 6)  # Start an H2O cluster with nthreads = num cores on your machine

print(log.path_Model_Gamma)
gamma_fit   = h2o.load_model(log.path_Model_Gamma)

print(log.path_Model_Poisson)
poisson_fit = h2o.load_model(log.path_Model_Poisson)

printstatus = log.printstatus
jsonaddstatus = log.jsonaddstatus

def transform(input_data):

    model_data = input_data
    return model_data

def score(model_data):

    new_data  = json.loads(model_data)
    h2oFrame  = h2o.H2OFrame()
    new_frame = h2oFrame.from_python(new_data)

    print(new_frame)

    prediction = model.predict(new_frame)

    print(prediction)

    result = prediction.as_data_frame()['predict'][0]

    answer = {
        'score': result
    }

    return json.dumps(answer)

def YearReleaseCar(CarYear):

    try:
        Year = int(CarYear)
    except:
        Year = 2015

    if Year < 1980:
       Year = 1980

    numYears = now.year - Year

    numYears += 1

    return numYears

def polinomizer(data, f1, n=2):

    for i in range (2, n+1):
        data[f1 + '_' + str(n)] = data[f1] ** i

    return(data)

def DriverAgeExp(DriverAge,DriverExp):

    if DriverAge < 18:
        DriverAge = 18
    elif DriverAge > 80:
        DriverAge = 80
    if DriverExp < 0:
        DriverExp = 0
    elif DriverExp > 30:
        DriverExp = 30
    if DriverAge-DriverExp < 18:
        DriverAge = None
        DriverExp = None

    return DriverAge, DriverExp

def f_DriverAge(DriverAge):

    if DriverAge < 18:
        DriverAge = 18
    elif DriverAge > 80:
        DriverAge = 80
    else:
        DriverAge = DriverAge
    return DriverAge

def f_DriverExp(DriverExp):

    if DriverExp < 0:
        DriverExp = 0
    elif DriverExp > 30:
        DriverExp = 30
    else:
        DriverExp = DriverExp
    return DriverExp

def f_Power(Power):

    if pd.isnull(Power):
        Power = None
    elif Power > 500:
        Power = None
    else:
        Power = round(Power/10, 0)
    return Power

def f_Vehicle_Age(IssueYear):

    if 2019 - IssueYear >= 20:
        Vehicle_Age = 20
    else:
        Vehicle_Age = 2019 - IssueYear
    return Vehicle_Age

def f_get_region_num(Kladr):

    region_num = Kladr[0:2]

    if region_num == 'No':
        region_num = 0
    elif region_num == '':
        region_num = 0
    else:
        region_num = int(region_num)
    return region_num

def f_BKI(Score):
    if pd.isnull(Score):
        Score = 20 - round(949/50, 0)
    else:
        Score = 20 - round(Score/50, 0)
    return Score

def map_for_dict_TypeFilial(TypeFilial_Int, TypeDict):

    if TypeDict == 'Num':
        dictionary = {0: 0.0, 3: 1.0, 1: 2.0, 2: 3.0}
        res = dictionary.get(TypeFilial_Int)
        if res == None:
            res = 3.0

    elif TypeDict == 'Sum':
        dictionary = {0: 1.0, 1: 2.0, 2: 3.0, 3: 4.0}
        res = dictionary.get(TypeFilial_Int)
        if res == None:
            res = 3.0
    else:
        res = TypeFilial_Int
    return res

def map_for_dict_FIASGroup(FIASGroup_Int, TypeDict):
    if TypeDict == 'Num':

        dictionary = {6: 0.0, 5: 1.0, 0: 2.0, 4: 3.0, 3: 4.0, 1: 5.0, 2: 6.0}
        res = dictionary.get(FIASGroup_Int)
        if res == None:
            res = 2.0

    elif TypeDict == 'Sum':
        dictionary = {5: 0.0, 0: 1.0, 2: 2.0, 4: 3.0, 3: 4.0, 1: 5.0, 6: 6.0}
        res = dictionary.get(FIASGroup_Int)
        if res == None:
            res = 1.0
    else:
        res = FIASGroup_Int

    return res

def map_for_dict_OwnerKLADR(OwnerKLADR_Int, TypeDict):
    if TypeDict == 'Num':
        dictionary = {53: 0.0, 83: 1.0, 44: 2.0, 70: 3.0, 73: 4.0, 58: 5.0, 74: 6.0, 52: 7.0, 30: 8.0, 20: 9.0,
                      55: 10.0, 15: 11.0, 62: 12.0, 16: 13.0, 18: 14.0, 32: 15.0, 5: 16.0, 37: 17.0, 33: 18.0,
                      29: 19.0, 6: 20.0, 2: 21.0, 48: 22.0, 46: 23.0, 13: 24.0, 51: 25.0, 45: 26.0, 36: 27.0,
                      43: 28.0, 71: 29.0, 78: 30.0, 89: 31.0, 63: 32.0, 7: 33.0, 57: 34.0, 77: 35.0, 34: 36.0,
                      59: 37.0, 86: 38.0, 66: 39.0, 56: 40.0, 12: 41.0, 50: 42.0, 24: 43.0, 42: 44.0, 65: 45.0,
                      49: 46.0, 69: 47.0, 3: 48.0, 11: 49.0, 0: 50.0, 19: 51.0,  67: 52.0, 91: 53.0, 38: 54.0,
                      23: 55.0, 39: 56.0, 27: 57.0, 72: 58.0, 76: 59.0, 47: 60.0, 60: 61.0, 31: 62.0, 25: 63.0,
                      22: 64.0, 54: 65.0, 41: 66.0, 61: 67.0, 87: 68.0, 68: 69.0, 79: 70.0, 40: 71.0, 28: 72.0,
                      64: 73.0, 17: 74.0, 8: 75.0, 35: 76.0, 26: 77.0, 4: 78.0, 92: 79.0, 14: 80.0, 75: 81.0,
                      1: 82.0, 10: 83.0, 21: 84.0, 9: 85.0, 99: 86.0}

        res = dictionary.get(OwnerKLADR_Int)
        if res == None:
            res = 0.0

    elif TypeDict == 'Sum':
        dictionary = {74: 0.0, 59: 1.0, 73: 2.0, 66: 3.0, 71: 4.0, 63: 5.0, 15: 6.0, 37: 7.0, 48: 8.0, 67: 9.0,
                    45: 10.0, 7: 11.0, 60: 12.0, 43: 13.0, 61: 14.0, 3: 15.0, 44: 16.0, 76: 17.0, 20: 18.0,
                    23: 19.0, 16: 20.0, 51: 21.0, 41: 22.0, 13: 23.0, 28: 24.0, 72: 25.0, 53: 26.0, 52: 27.0,
                    8: 28.0, 40: 29.0, 4: 30.0, 26: 31.0, 42: 32.0, 34: 33.0, 55: 34.0, 29: 35.0, 2: 36.0,
                    12: 37.0, 62: 38.0, 17: 39.0, 49: 40.0, 25: 41.0, 27: 42.0, 5: 43.0, 79: 44.0, 54: 45.0,
                    57: 46.0, 22: 47.0, 77: 48.0, 14: 49.0, 75: 50.0, 50: 51.0, 65: 52.0, 0: 53.0, 64: 54.0,
                    70: 55.0, 38: 56.0, 30: 57.0, 24: 58.0, 19: 59.0, 69: 60.0, 78: 61.0, 86: 62.0, 87: 63.0,
                    89: 64.0, 18: 65.0, 91: 66.0, 33: 67.0, 32: 68.0, 56: 69.0, 6: 70.0, 1: 71.0, 58: 72.0,
                    11: 73.0, 36: 74.0, 31: 75.0, 92: 76.0, 68: 77.0, 46: 78.0, 47: 79.0, 83: 80.0, 39: 81.0,
                    35: 82.0, 9: 83.0, 10: 84.0, 21: 85.0, 99: 86.0}

        res = dictionary.get(OwnerKLADR_Int)
        if res == None:
            res = 0.0
    else:
        res = OwnerKLADR_Int

    return res

def map_for_dict_TSCategory(TSCategory_Int, TypeDict):
    if TypeDict == 'Num':
        dictionary = {7: 0.0, 4: 1.0, 3: 2.0, 2: 3.0, 8: 4.0, 10: 5.0, 5: 6.0, 1: 7.0, 6: 8.0, 9: 9.0}
        res = dictionary.get(TSCategory_Int)
        if res == None:
            res = 3.0

    elif TypeDict == 'Sum':
        dictionary = {3: 0.0, 5: 1.0, 2: 2.0, 4: 3.0, 1: 4.0, 8: 5.0, 10: 6.0, 7: 7.0, 6: 8.0, 9: 9.0}
        res = dictionary.get(TSCategory_Int)
        if res == None:
            res = 2.0
    else:
        res = TSCategory_Int

    return res

@app.route('/save_quote_db', methods=['POST'])
def save_quote_db():

        try:

            nowDateStart = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S.%f")

            print(' ')
            print('<************************** ' + str(nowDateStart) + ' ********************************************>')
            json_input = request.json
            json_str   = json.dumps(json_input)

            json_ = json_input

            PredictSegment = ""

            avtoKod = json_input['AvtoKodJSON']

            Count_Fine_Speed  = 0 # Количество штрафов при превышении скорости
            Group_Amout_Speed = 0 # Сумма штрафов при превышении скорости
            allFine           = 0 # Все остальные штрафы
            allAmountFine     = 0 # Сумма по всем остальным штрафам
            Premium           = json_input['Premium'] # Премия

            RegNumber             = json_input["RegNumber"]
            VIN                   = json_input["VIN"]
            InsurerClientType     = json_input["InsurerClientType"]
            DriverMinAge          = f_DriverAge(json_input["DriverMinAge"])
            DriverMinAge_2        = DriverMinAge ** 2
            DriverMinExperience   = f_DriverExp(json_input["DriverMinExperience"])
            DriverMinExperience_2 = DriverMinExperience ** 2
            IsTaxi                = json_input["IsTaxi"]
            InsurerTitle          = json_input["InsurerTitle"]

            if type(IsTaxi) != type(bool):
                IsTaxi = False

            CoefKM                = json_input["CoefKM"]
            Coef_KP               = json_input["CoefKP"]
            Coef_KS               = json_input["CoefKS"]
            CoefKBM               = json_input["CoefKBM"]
            DriverUnlimit         = json_input["DriverUnlimit"]
            EnginePower_Autocod   = f_Power(json_input["EnginePower"])
            VehicleAge            = f_Vehicle_Age(json_input["IssueYear"])
            IsProlongation        = json_input["IsProlongation"]
            InsurerGender         = json_input["InsurerGender"]
            BKI_scoreNumber_1_Num = float(1)

            OwnerKLADR_Int        = f_get_region_num(json_input["OwnerKLADRCode"])
            FIASGroup_Int         = float(json_input["FIASGroup"])
            TSCategory_Int        = float(json_input["TSCategory"])

            IsMSK                 = json_input["IsMSK"]
            IsEGARANT             = json_input["IsEGARANT"]
            IsEOSAGO              = json_input["IsEOSAGO"]
            SellerIKP = json_input["SellerIKP"]

            PrevPolicyNumber      = json_input["PrevPolicyNumber"]
            BKIJSON               = json_input["BKIJSON"]
            Commission            = json_input['Commission']
            IsRefusal             = False # Отказ клиенту
            MeanLoss              = 0 # Средний убыток

            if not pd.isnull(BKIJSON):
                if "ScoreNumber" in BKIJSON:
                    BKI_scoreNumber_1_Num = f_BKI(float(BKIJSON['ScoreNumber']))

            if IsEGARANT:
                TypeFilial_Int = 0
            #elif IsEOSAGO:     признак IsEOSAGO соответствует коду продукта, в модели нас интересует канал продаж
            #                    - через сайт, это признак SellerIKP = 01788
            elif SellerIKP == '01788':
                TypeFilial_Int = 1
            elif IsMSK:
                TypeFilial_Int = 3
            else:
                TypeFilial_Int = 2

            TypeFilial_Num = map_for_dict_TypeFilial(TypeFilial_Int, 'Num')
            TypeFilial_Sum_Num = map_for_dict_TypeFilial(TypeFilial_Int, 'Sum')

            OwnerKLADR_Num = map_for_dict_OwnerKLADR(OwnerKLADR_Int, 'Num')
            OwnerKLADR_Sum_Num = map_for_dict_OwnerKLADR(OwnerKLADR_Int, 'Sum')

            FIASGroup_Num = map_for_dict_FIASGroup(FIASGroup_Int, 'Num')
            FIASGroup_Sum_Num = map_for_dict_FIASGroup(FIASGroup_Int, 'Sum')

            TSCategory_Num = map_for_dict_TSCategory(TSCategory_Int, 'Num')
            TSCategory_Sum_Num = map_for_dict_TSCategory(TSCategory_Int, 'Sum')

            # 19.06.2019 Истрелов А.А. --

            if InsurerGender == 0:
                GenderM = 0
                GenderW = 1
            elif InsurerGender == 1:
                GenderM = 1
                GenderW = 0
            else:
                try:
                    lenInsurerTitle = len(InsurerTitle)
                    if InsurerTitle[lenInsurerTitle-2:].upper() == 'ИЧ' or InsurerTitle[lenInsurerTitle-4:].upper() == 'ОГЛЫ':
                        GenderM = 1
                        GenderW = 0
                    elif InsurerTitle[lenInsurerTitle-2:].upper() == 'НА' or InsurerTitle[lenInsurerTitle-4:].upper() == 'КЫЗЫ':
                        GenderM = 0
                        GenderW = 1
                    else:
                        GenderM = 0
                        GenderW = 0
                except:
                    GenderM = 0
                    GenderW = 0

            # 19.06.2019 Истрелов А.А. --

            if InsurerClientType == 2:
                GenderM = 0
                GenderW = 0

            if DriverUnlimit == True:
                DriverUnlimitNum = float(1)
            else:
                DriverUnlimitNum = float(0)

            if type(avtoKod) == dict:

               if 'taxi' in avtoKod:

                   if 'used_in_taxi' in avtoKod['taxi']:
                        IsTaxi = avtoKod['taxi']['used_in_taxi']

               if 'fines' in avtoKod:

                   if 'items' in avtoKod['fines']:

                       itemsKod = avtoKod['fines']['items']

                       for itemsValue in itemsKod:

                           payFine = False
                           payAllFine = False

                           for key in itemsValue:

                               if key == 'article':

                                   if itemsValue[key]['code'] == '12.9Ч.2':

                                       payFine = True

                                   else:

                                       payAllFine = True

                               else:

                                   payAllFine = True

                               if key == 'amount' and payFine:
                                   Count_Fine_Speed  += 1
                                   Group_Amout_Speed += itemsValue[key]['total']
                                   break

                               if key == 'amount' and payAllFine:
                                   allFine       += 1
                                   allAmountFine += itemsValue[key]['total']
                                   break

            Taxi = 1 if IsTaxi else 0

            if not pd.isnull(PrevPolicyNumber):

                OldPolicy_Num      = 0
                OldClaimSumPol_Num = 0

                TextRequest = ("""SELECT
                                SUM(ClaimSum) AS ClaimSum,
                                SUM(ClaimCount) AS ClaimCount
                                FROM ClaimDate
                                WHERE PolicyID = ?""")

                try:

                    query = cursor.execute(TextRequest, PrevPolicyNumber)
                    row   = query.fetchone()

                    while row:

                        if not pd.isnull(row.ClaimCount):

                            OldPolicy_Num      += int(row.ClaimCount)
                            OldClaimSumPol_Num += int(row.ClaimSum)

                        row = query.fetchone()

                except:

                    OldPolicy_Num = 0
                    OldClaimSumPol_Num = 0


            else:

                OldPolicy_Num      = 0
                OldClaimSumPol_Num = 0

            if DriverMinAge == 0:
                DriverUnlimit = True
                DriverUnlimitNum = 1
                json_.update({'DriverUnlimit': DriverUnlimit})

            if not IsTaxi and not DriverUnlimit:

                nowDate = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S.%f")
                #print('time start predict', str(nowDate))
                json_.update({'TimeStart': nowDateStart})
                json_.update({'TimeStartPredict': nowDate})

                df = pd.DataFrame({
                                'InsurerClientType':     [InsurerClientType],
                                'DriverMinAge':          [DriverMinAge],
                                'DriverMinAge_2':        [DriverMinAge_2],
                                'DriverMinExperience':   [DriverMinExperience],
                                'DriverMinExperience_2': [DriverMinExperience_2],
                                'Coef_KP':               [Coef_KP],
                                'Coef_KS':               [Coef_KS],
                                'CoefKBM':               [CoefKBM],
                                'DriverUnlimitNum':      [DriverUnlimitNum],
                                'EnginePower+Autocod':   [EnginePower_Autocod],
                                'VehicleAge':            [VehicleAge],
                                'OldPolicy_Num':         [OldPolicy_Num],
                                'OldClaimSumPol_Num':    [OldClaimSumPol_Num],
                                'BKI_scoreNumber_1_Num': [BKI_scoreNumber_1_Num],
                                'GenderM':               [GenderM],
                                'GenderW':               [GenderW],
                                'Taxi':                  [Taxi],
                                'FIASGroup_Sum_Num':     [FIASGroup_Sum_Num],
                                'OwnerKLADR_Sum_Num':    [OwnerKLADR_Sum_Num],
                                'TSCategory_Sum_Num':    [TSCategory_Sum_Num],
                                'TypeFilial_Sum_Num':    [TypeFilial_Sum_Num],
                                'Count_Fine_Speed':      [Count_Fine_Speed],
                                'Group_Amout_Speed':     [Group_Amout_Speed],
                                'FIASGroup_Num':         [FIASGroup_Num],
                                'OwnerKLADR_Num':        [OwnerKLADR_Num],
                                'TSCategory_Num':        [TSCategory_Num],
                                'TypeFilial_Num':        [TypeFilial_Num]
                               })

                hf = h2o.H2OFrame(df)

                #print('Predict Gamma......')
                predictGamma = gamma_fit.predict(hf)
                ValueGamma   = predictGamma.as_data_frame()['predict'][0]

                print('ValueGamma ', ValueGamma)

                #print('Predict Poisson......')

                predictPoisson = poisson_fit.predict(hf)
                ValuePoisson  = predictPoisson.as_data_frame()['predict'][0]

                nowDate = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S.%f")
                #print('time end predict', str(nowDate))
                json_.update({'TimeEndPredict': nowDate})

                print('ValuePoisson ', ValuePoisson)

                MeanLoss = (ValueGamma * ValuePoisson + Commission) / Premium
                MeanLoss = int(MeanLoss * 100)

                if MeanLoss > 95:
                    IsRefusal = True

                print('MeanLoss:' + str(MeanLoss))

                json_.update({'PredictGamma': ValueGamma})
                json_.update({'PredictPoisson': ValuePoisson})
                json_.update({'MeanLoss': MeanLoss})

                if printstatus == 1:
                    print('расчет начало')
                    print('InsurerClientType',      InsurerClientType)
                    print('DriverMinAge',           DriverMinAge)
                    print('DriverMinAge_2',         DriverMinAge_2)
                    print('DriverMinAge_2**2',      DriverMinAge ** 2)
                    print('DriverMinExperience',    DriverMinExperience)
                    print('DriverMinExperience_2',  DriverMinExperience_2)
                    print('DriverMinExperience_2 ** 2',  DriverMinExperience**2)
                    print('EnginePower+Autocod',    EnginePower_Autocod)
                    print('Coef_KP',                Coef_KP)
                    print('Coef_KS',                Coef_KS)
                    print('CoefKBM',                CoefKBM)
                    print('DriverUnlimitNum',       DriverUnlimitNum)
                    print('EnginePower_Autocod',    EnginePower_Autocod)
                    print('VehicleAge',             VehicleAge)

                    print('OldPolicy_Num', OldPolicy_Num)
                    print('OldClaimSumPol_Num', OldClaimSumPol_Num)
                    print('BKI_scoreNumber_1_Num', BKI_scoreNumber_1_Num)
                    print('Count_Fine_Speed', Count_Fine_Speed)
                    print('Group_Amout_Speed', Group_Amout_Speed)

                    print('GenderM', GenderM)
                    print('GenderW', GenderW)
                    print('Taxi', Taxi)

                    print('FIASGroup_Num',      FIASGroup_Num)
                    print('FIASGroup_Sum_Num',  FIASGroup_Sum_Num)
                    print('FIASGroup_Int',      FIASGroup_Int)

                    print('OwnerKLADR_Num',     OwnerKLADR_Num)
                    print('OwnerKLADR_Sum_Num', OwnerKLADR_Sum_Num)
                    print('OwnerKLADR_Int',     OwnerKLADR_Int)

                    print('TSCategory_Num',     TSCategory_Num)
                    print('TSCategory_Sum_Num', TSCategory_Sum_Num)
                    print('TSCategory_Int',     TSCategory_Int)

                    print('TypeFilial_Num',     TypeFilial_Num)
                    print('TypeFilial_Sum_Num', TypeFilial_Sum_Num)
                    print('TypeFilial_Int',     TypeFilial_Int)

                    print('расчет конец')

            else:
                IsRefusal = True

            if IsRefusal:
                # 11.06.2019 Истрелов А.А. ++
                if MeanLoss > 199:
                    PredictSegment = "Запретительный"
                # 11.06.2019 Истрелов А.А. --
                else:
                    PredictSegment = "Рисковый"
            else:
                PredictSegment = "Целевой-2"

            json_.update({'FineAvtoKod':    Count_Fine_Speed})
            json_.update({'amountFineKod':  Group_Amout_Speed})
            json_.update({'allFine':        allFine})
            json_.update({'allAmountFine':  allAmountFine})
            json_.update({'IsRefusal':      IsRefusal})
            json_.update({'PredictSegment': PredictSegment})

            # 19.06.2019 Истрелов А.А. ++
            json_.update({'GenderM': GenderM})
            json_.update({'GenderW': GenderW})
            # 19.06.2019 Истрелов А.А. --

            #print(' ')
            #print('<************************** ' + str(nowDate) + ' ********************************************>')
            #pprint.pprint(json_)

            nowDate = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S.%f")
            json_.update({'TimeEnd': nowDate})

            if jsonaddstatus ==1:
                json_.update({'DriverUnlimitNum':       DriverUnlimitNum})
                json_.update({'EnginePower_Autocod':    EnginePower_Autocod})
                json_.update({'VehicleAge':             VehicleAge})
                json_.update({'OldPolicy_Num':          OldPolicy_Num})
                json_.update({'OldClaimSumPol_Num':     OldClaimSumPol_Num})
                json_.update({'BKI_scoreNumber_1_Num':  BKI_scoreNumber_1_Num})
                json_.update({'FIASGroup_Sum_Num':      FIASGroup_Sum_Num})
                json_.update({'OwnerKLADR_Sum_Num':     OwnerKLADR_Sum_Num})
                json_.update({'TSCategory_Sum_Num':     TSCategory_Sum_Num})
                json_.update({'TypeFilial_Sum_Num':     TypeFilial_Sum_Num})
                json_.update({'Count_Fine_Speed':       Count_Fine_Speed})
                json_.update({'Group_Amout_Speed':      Group_Amout_Speed})
                json_.update({'FIASGroup_Num':          FIASGroup_Num})
                json_.update({'OwnerKLADR_Num':         OwnerKLADR_Num})
                json_.update({'TSCategory_Num':         TSCategory_Num})
                json_.update({'TypeFilial_Num':         TypeFilial_Num})

            with open('D:\\OsagoQuotes\\db_log_port_5978\\' + nowDate + '-OsagoQuote.json', 'w') as outfile:
                json.dump(json_, outfile)

            outfile.close()

            json_segment = {'PredictSegment': PredictSegment, 'Score': MeanLoss}

            pprint.pprint(json_segment)


            nowDate = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S.%f")
            print('Time end: ',  str(nowDate))

            print('<**********************************************************************************************>')

            return json.dumps(json_segment) #json_str



        except:

            print("ERROR")

            now = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S.%f")

            with open('D:\\OsagoQuotes\\db\\'+now+'-Except.json', 'w') as outfile:
                json.dump(json_, outfile)

            outfile.close()

            return jsonify({'trace': traceback.format_exc()})

if __name__ == '__main__':

    try:
        port = int(sys.argv[1]) # This is for a command-line input
    except:
        port = 5978 #2402 # If you don't provide any port the port will be set to 12345

    '''
    # keep for sklearn models
    lr = joblib.load("Models\\model.pkl") # Load "model.pkl"
    print ('Model loaded')
    model_columns = joblib.load("Models\\model_columns.pkl") # Load "model_columns.pkl"
    print ('Model columns loaded')
    '''
    #serve(app, host='172.31.16.122', port=port)

    app.run(host='172.31.16.122', port=port, debug=False)

#'172.31.16.122'

'''
проверяем роуты
'''

#------------------------------------------------------

@app.route("/get_input/")
def get_input_r():

    return get_input()

@app.route("/get_answer/")
def get_answer_r():

    return get_answer()

@app.route("/predict_test/")
def predict_test():

    return score(get_input())

@app.route('/predict', methods=['POST'])
def predict():

    if 1==1:

        try:

            json_ = json.dumps(request.json)
            print(json_)

            prediction = score(json_)

            return prediction

        except:
            return jsonify({'trace': traceback.format_exc()})
    else:

        print ('Train the model first')
        return ('No model here to use')

@app.route('/save_quote', methods=['POST'])
def save_quote():

        try:

            json_ = json.dumps(request.json)

            now = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S.%f")

            with open('D:\\OsagoQuotes\\'+now+'-OsagoQuote.json', 'w') as outfile:
                json.dump(json_, outfile)

            outfile.close()

            return json_

        except:

            now = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S.%f")

            with open('D:\\OsagoQuotes\\'+now+'-Except.json', 'w') as outfile:
                json.dump(json_, outfile)

            outfile.close()

            return jsonify({'trace': traceback.format_exc()})


def get_input():

    input={
              'DriverMinAge': 42,
              'DriverMinExperience': 15,
              'ClaimCountPol': 0,
              'DAgeExp': 331,
              'DriverMinAge_2': 1764,
              'DriverMinExperience_2': 225,
              'RegionNum': 49,
              'DriverUnlimit_Num': 0,
              'EnginePower': 12,
              'Taxi': 0,
              'issueyear_num': 11,
              'issueyear_num_2': 121,
              'MM_Num': 411,
              'Seg_Num': 14,
              'InsurerClientType_Num': 0,
              'CoefKBM': 0.75,
              'TSCat_Num':9,
              'OwnerKLADRCode_Num': 38,
              'KL_Num': 44,
              'Reg_Doc_Kl_Num': 1,
              'CoefKBM_2': 0.5625,
              'Count': 1
    }

    return  json.dumps(input)

def get_answer():

    answer = {
        'score':0.0283197967289844
    }

    return  json.dumps(answer)

'''
#-------------------------------------------------------

TODOS = {
    'param1': {'task': 'build an API'},
    'param2': {'task': '?????'},
    'param3': {'task': 'profit!'},
}


def abort_if_todo_doesnt_exist(todo_id):
    if todo_id not in TODOS:
        abort(404, message="Todo {} doesn't exist".format(todo_id))

parser = reqparse.RequestParser()
parser.add_argument('task')


# Todo
# shows a single todo item and lets you delete a todo item
class Todo(Resource):
    def get(self, todo_id):
        abort_if_todo_doesnt_exist(todo_id)
        return TODOS[todo_id]

    def delete(self, todo_id):
        abort_if_todo_doesnt_exist(todo_id)
        del TODOS[todo_id]
        return '', 204

    def put(self, todo_id):
        args = parser.parse_args()
        task = {'task': args['task']}
        #predict task
        TODOS[todo_id] = task
        return task, 201


# TodoList
# shows a list of all todos, and lets you POST to add new tasks
class TodoList(Resource):
    def get(self):
        return TODOS

    def post(self):
        args = parser.parse_args()
        todo_id = int(max(TODOS.keys()).lstrip('todo')) + 1
        todo_id = 'todo%i' % todo_id
        TODOS[todo_id] = {'task': args['task']}
        return TODOS[todo_id], 201

##
## Actually setup the Api resource routing here

## проверяем ресурсы

api.add_resource(TodoList, '/todos')
api.add_resource(Todo, '/todos/<todo_id>')


if __name__ == '__main__':
    app.run(debug=True, port=2402)
'''