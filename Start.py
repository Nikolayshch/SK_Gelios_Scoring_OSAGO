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

gamma_fit   = h2o.load_model(log.path_Model_Gamma)
poisson_fit = h2o.load_model(log.path_Model_Poisson)

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

def DriverAge(DriverAge):

    if DriverAge < 18:
        DriverAge = 18
    elif DriverAge > 80:
        DriverAge = 80
    return DriverAge

def DriverExp(DriverExp):

    if DriverExp < 0:
        DriverExp = 0
    elif DriverExp > 30:
        DriverExp = 30
    return DriverExp

def f_Power(Power):

    if pd.isnull(Power):
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

#19.04.2019 Истрелов А.А. ++
#добавление типа филиала, создание справочника номеров типов филиала + мэппинг
def TypeFilial(data_Risk_Osago):

    # Создаем словарь типов филиала

    dict_TypeFilial_Int = {
        None: 5, 'Е-Гарантия': 1, 'Единый агент РСА': 2, 'Е-ОСАГО': 3, 'ККК': 4, 'Москва': 5, 'Регионы': 6,
        'Токсичные': 7}

    # Мапируем данные на словарь типов филиалов TypeFilial_Int
    data_Risk_Osago['TypeFilial_Int'] = data_Risk_Osago['ТипФилиала'].map(dict_TypeFilial_Int)

    # Создаем справочник типов филиалов TypeFilial - spr_TypeFilial
    spr_TypeFilial = data_Risk_Osago.groupby(['TypeFilial_Int']).sum()[['GPW_RSBU', 'ClaimCountPol_DB', 'Count']]

    # Добавляем частоту в справочник типов филиалов TypeFilial
    spr_TypeFilial['Reg_freq'] = spr_TypeFilial['ClaimCountPol_DB'] / spr_TypeFilial['Count']

    # Создаем номера для словаря типов филиалов TypeFilial
    keys_TypeFilial = []
    values_TypeFilial = []

    for i in enumerate(spr_TypeFilial.sort_values('Reg_freq', ascending=False).index.values):
        keys_TypeFilial.append(i[1])
        values_TypeFilial.append(float(i[0]))

    # Создаем словарь типов филиалов TypeFilial
    dict_TypeFilial = dict(zip(keys_TypeFilial, values_TypeFilial))

    # Мапируем данные на словарь типов филиалов TypeFilial
    data_Risk_Osago['TypeFilial_Num'] = data_Risk_Osago['TypeFilial_Int'].map(dict_TypeFilial)

    return data_Risk_Osago

@app.route('/save_quote_db', methods=['POST'])
def save_quote_db():

        try:

            nowDate = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S.%f")

            json_input = request.json
            json_str   = json.dumps(json_input)

            json_ = json_input

            avtoKod = json_input['AvtoKodJSON']

            Count_Fine_Speed  = 0 # Количество штрафов при превышении скорости
            Group_Amout_Speed = 0 # Сумма штрафов при превышении скорости
            allFine           = 0 # Все остальные штрафы
            allAmountFine     = 0 # Сумма по всем остальным штрафам
            Premium           = json_input['Premium'] # Премия

            RegNumber             = json_input["RegNumber"]
            VIN                   = json_input["VIN"]
            InsurerClientType     = json_input["InsurerClientType"]
            DriverMinAge          = json_input["DriverMinAge"]
            DriverMinAge_2        = json_input["DriverMinAge"] ** 2
            DriverMinExperience   = json_input["DriverMinExperience"]
            DriverMinExperience_2 = json_input["DriverMinExperience"] ** 2
            IsTaxi                = json_input["IsTaxi"]

            if type(IsTaxi) != type(bool):
                IsTaxi = False

            CoefKM                = json_input["CoefKM"]
            Coef_KP               = json_input["CoefKP"]
            Coef_KS               = json_input["CoefKS"]
            CoefKBM               = json_input["CoefKBM"]
            FIASGroup_Sum_Num     = int(json_input["FIASGroup"])
            DriverUnlimit         = json_input["DriverUnlimit"]
            EnginePower_Autocod   = f_Power(json_input["EnginePower"])
            VehicleAge            = f_Vehicle_Age(json_input["IssueYear"])
            IsProlongation        = json_input["IsProlongation"]
            InsurerGender         = json_input["InsurerGender"]
            BKI_scoreNumber_1_Num = float(1)
            OwnerKLADRCode_Num    = f_get_region_num(json_input["OwnerKLADRCode"])
            FIASGroup_Num         = float(json_input["FIASGroup"])
            TSCategory_Num        = float(json_input["TSCategory"])
            IsMSK                 = json_input["IsMSK"]
            IsEGARANT             = json_input["IsEGARANT"]
            IsEOSAGO              = json_input["IsEOSAGO"]
            PrevPolicyNumber      = json_input["PrevPolicyNumber"]
            BKIJSON               = json_input["BKIJSON"]

            if not pd.isnull(BKIJSON):
                if "ScoreNumber" in BKIJSON:
                    BKI_scoreNumber_1_Num = float(BKIJSON['ScoreNumber'])

            if IsEGARANT:
                TypeFilial_Num = 0
            elif IsEOSAGO:
                TypeFilial_Num = 1
            elif IsMSK:
                TypeFilial_Num = 3
            else:
                TypeFilial_Num = 2

            if InsurerGender == 0:
                GenderM = 0
                GenderW = 1
            else:
                GenderM = 1
                GenderW = 0

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
                                   Count_Fine_Speed += 1
                                   Group_Amout_Speed += itemsValue[key]['total']
                                   break

                               if key == 'amount' and payAllFine:
                                   allFine += 1
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

            if not IsTaxi:

                df = pd.DataFrame({'InsurerClientType': [InsurerClientType],
                               'DriverMinAge':          [DriverMinAge],
                               'DriverMinAge_2':        [DriverMinAge_2],
                               'DriverMinExperience':   [DriverMinExperience],
                               'DriverMinExperience_2': [DriverMinExperience_2],
                               'Coef_KP':               [Coef_KP],
                               'Coef_KS':               [Coef_KS],
                               'CoefKBM':               [CoefKBM],
                               'FIASGroup_Sum_Num':     [FIASGroup_Sum_Num],
                               'DriverUnlimitNum':      [DriverUnlimitNum],
                               'EnginePower_Autocod':   [EnginePower_Autocod],
                               'VehicleAge':            [VehicleAge],
                               'OldPolicy_Num':         [OldPolicy_Num],
                               'OldClaimSumPol_Num':    [OldClaimSumPol_Num],
                               'BKI_scoreNumber_1_Num': [BKI_scoreNumber_1_Num],
                               'OwnerKLADRCode_Num':    [OwnerKLADRCode_Num],
                               'FIASGroup_Num':         [FIASGroup_Num],
                               'TSCategory_Num':        [TSCategory_Num],
                               'TypeFilial_Num':        [TypeFilial_Num],
                               'GenderM':               [GenderM],
                               'GenderW':               [GenderW],
                               'Taxi':                  [Taxi]
                               })

                hf = h2o.H2OFrame(df)

                print('Predict Gamma......')
                predictGamma = gamma_fit.predict(hf)
                ValueGamma = predictGamma.as_data_frame()['predict'][0]
                print(ValueGamma)

                print('Predict Poisson......')
                predictPoisson = poisson_fit.predict(hf)
                ValuePoisson = predictPoisson.as_data_frame()['predict'][0]
                print(ValuePoisson)

                MeanLoss = ValueGamma * ValuePoisson / Premium

                print('MeanLoss:' + str(MeanLoss))

                json_.update({'PredictGamma': ValueGamma})
                json_.update({'PredictPoisson': ValuePoisson})
                json_.update({'MeanLoss': MeanLoss})

            json_.update({'FineAvtoKod':    Count_Fine_Speed})
            json_.update({'amountFineKod':  Group_Amout_Speed})
            json_.update({'allFine':        allFine})
            json_.update({'allAmountFine':  allAmountFine})

            print(' ')
            print('<************************** ' + str(nowDate) + ' ********************************************>')
            pprint.pprint(json_)
            print('<**********************************************************************************************>')

            with open('D:\\OsagoQuotes\\db_log_port_5978\\' + nowDate + '-OsagoQuote.json', 'w') as outfile:
                json.dump(json_, outfile)

            outfile.close()

            return json_str

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