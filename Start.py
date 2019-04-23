#ver. model 0.24

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

#from waitress import serve

now = datetime.datetime.now()

app = Flask(__name__)
api = Api(app)

# опробуем подключение к рабочему столу

server = log.server
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

#h2o.init(nthreads = 6)  # Start an H2O cluster with nthreads = num cores on your machine

#gamma_fit   = h2o.load_model("D:\\OsagoProject\\Model\\GLM_model_python_gamma") #"D:\\OsagoProject\\Models-h2o\\GLM_model_python_1551464873895_38")
#poisson_fit = h2o.load_model("D:\\OsagoProject\\Model\\GLM_model_python_poisson")

#print(type(gamma_fit))

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

def Power_Transform(Power):

    Power = int(Power/10)
    return Power

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

@app.route('/save_quote_db', methods=['POST'])
def save_quote_db():

        try:

            nowDate = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S.%f")

            json_input = request.json
            json_str   = json.dumps(json_input)

            json_ = json_input

            avtoKod = json_input['AvtoKodJSON']

            fineKod = 0 # Количество штрафов при превышении скорости
            amountFineKod = 0 # Сумма штрафов при превышении скорости

            allFine = 0 # Все остальные штрафы
            allAmountFine = 0 # Сумма по всем остальным штрафам

            if type(avtoKod) == dict:

                isTaxi   = avtoKod['taxi']['used_in_taxi']
                itemsKod = avtoKod['fines']['items'] # type = list

                for itemsValue in itemsKod:

                    payFine = False
                    payAllFine = False

                    for key in itemsValue:

                        if key == 'article':

                            if itemsValue[key]['code'] == '12.9Ч.2':

                                fineKod += 1
                                payFine = True

                            else:

                                allFine += 1
                                payAllFine = True

                            continue

                        else:

                            allFine += 1
                            payAllFine = True

                            continue

                        if key == 'amount' and payFine:
                            amountFineKod += itemsValue[key]['total']
                            continue

                        if key == 'amount' and payAllFine:
                            allAmountFine += itemsValue[key]['total']
                            continue

            json_.update({'FineAvtoKod': fineKod})
            json_.update({'amountFineKod': amountFineKod})
            json_.update({'allFine': allFine})
            json_.update({'allAmountFine': allAmountFine})

            print(' ')
            print('<************************** ' + str(nowDate) + ' ********************************************>')
            print(json_)
            print('<**********************************************************************************************>')

            Premium = json_input["Premium"]
            InsSum = json_input["InsSum"]
            PolicyId = json_input["PolicyId"]
            InsurerClientType = json_input["InsurerClientType"]
            InsurerBirthDate = json_input["InsurerBirthDate"]
            InsurerDocumentType = json_input["InsurerDocumentType"]
            InsurerGender = json_input["InsurerGender"]
            InsurerTitle = json_input["InsurerTitle"]
            InsurerPhone = json_input["InsurerPhone"]
            DriverMinAge = json_input["DriverMinAge"]
            SellerIKP = json_input["SellerIKP"]
            AgentIKP = json_input["AgentIKP"]
            VIN = json_input["VIN"]
            EnginePower = json_input["EnginePower"]
            IssueYear = json_input["IssueYear"]
            TSCategory = json_input["TSCategory"]
            RegNumber = json_input["RegNumber"]
            BodyNumber = json_input["BodyNumber"]
            CoefKM = json_input["CoefKM"]
            CoefKP = json_input["CoefKP"]
            IsTaxi = json_input["IsTaxi"]
            CoefKO = json_input["CoefKO"]
            CoefKBM = json_input["CoefKBM"]
            CoefKVC = json_input["CoefKVC"]
            CoefKT = json_input["CoefKT"]
            BaseRate = json_input["BaseRate"]
            CoefKN = json_input["CoefKN"]
            CoefKPR = json_input["CoefKPR"]
            SeatsNumberTo16 = json_input["SeatsNumberTo16"]
            MaxWeightTo16 = json_input["MaxWeightTo16"]
            CoefKS = json_input["CoefKS"]
            IsForeignCountry = json_input["IsForeignCountry"]
            OwnerKLADRCode = json_input["OwnerKLADRCode"]
            FIASGroup = json_input["FIASGroup"]
            InsuranceTerm = json_input["InsuranceTerm"]
            IsProlongation = json_input["IsProlongation"]
            SavingHour = json_input["SavingHour"]
            DateStartAndSavingDateDiff = json_input["DateStartAndSavingDateDiff"]
            IsElectronic = json_input["IsElectronic"]
            DriverMinExperience = json_input["DriverMinExperience"]

            '''
            print(Premium)
            print(InsSum)
            print(PolicyId)
            print(InsurerClientType)
            print(InsurerBirthDate)
            print(InsurerDocumentType)
            print(InsurerGender)
            print(InsurerTitle)
            print(InsurerPhone)
            print(DriverMinAge)
            print(SellerIKP)
            print(AgentIKP)
            print(VIN)
            print(EnginePower)
            print(IssueYear)
            print(TSCategory)
            print(RegNumber)
            print(BodyNumber)
            print(CoefKM)
            print(CoefKP)
            print(IsTaxi)
            print(CoefKO)
            print(CoefKBM)
            print(CoefKVC)
            print(CoefKT)
            print(BaseRate)
            print(CoefKN)
            print(CoefKPR)
            print(SeatsNumberTo16)
            print(MaxWeightTo16)
            print(CoefKS)
            print(IsForeignCountry)
            print(OwnerKLADRCode)
            print(FIASGroup)
            print(InsuranceTerm)
            print(IsProlongation)
            print(SavingHour)
            print(DateStartAndSavingDateDiff)
            print(IsElectronic)
            print(DriverMinExperience)
            '''
            # print(json_)

            # json_dict = json.loads(json_dict_str)

            # print(json_dict_str)
            # print(json_["Premium"])
            # print(json_["InsSum"])

            datetime_txt = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S.%f")

            with open('D:\\OsagoQuotes\\db_log_port_5978\\' + nowDate + '-OsagoQuote.json', 'w') as outfile:
                json.dump(json_, outfile)

            outfile.close()

            return json_str

        except:

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