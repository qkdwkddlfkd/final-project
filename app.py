from pymongo import MongoClient
from bs4 import BeautifulSoup
import requests
from flask import Flask, render_template, jsonify, request
app = Flask(__name__)


# client = MongoClient('mongodb://sampleID:samplePW@12.34.56.78', 27017)
# client = MongoClient('mongodb://qkdwkddlfkd:june7575@15.164.216.152', 27017)
client = MongoClient('localhost', 27017)
db = client.dbsparta
# HTML을 주는 부분
@app.route('/')
def home():
    return render_template('food.html')

    
# API 역할을 하는 부분

# 식약처에서 데이터 받아와서 db에 저장
@app.route('/crawl', methods=['GET'])
def crawl():
    # 1. 기존 DB에서 저장된 데이터 수 받아오기 ex) 28000 -> curr_count
    # 2. 식약처 api로 총 데이터 수 받아오기 requests (1/2) -> total count ex) 28050
    # 3. 식약처 api로 새로운 데이터 받아오기 requests (curr_count+1 / total_count) -> 100개씩 나눠서
    ##### 4. 이때마다 db.insert_one하기
    curr_count = int(db.healthnutritionfood.count())
    print(curr_count)
    URL = 'http://openapi.foodsafetykorea.go.kr/api/b7511e10cbfd4b10a763/I0030/json/1/2'
    response = requests.get(URL)
    code = response.status_code #response 안에 status_code가 저장되어있음 항상. 우린 그걸 가져온거.
    if code == 200: #200:아무 오류 없이 잘 대답이 온 것 / 500: internal server error
        total_count = response.json()['I0030']['total_count']

    for i in range(curr_count + 1, total_count, 1000):
        if total_count - i + 1 > 1000:
            remain = i+999
        else:
            remain = total_count
        
        URL = 'http://openapi.foodsafetykorea.go.kr/api/b7511e10cbfd4b10a763/I0030/json/' + i + '/' + remain
        response = requests.get(URL)
        code = response.status_code #response 안에 status_code가 저장되어있음 항상. 우린 그걸 가져온거.
        if code == 200: #200:아무 오류 없이 잘 대답이 온 것 / 500: internal server error
            datas = response.json()['I0030']['row']

            for data in datas:
                license_number = data['LCNS_NO'] 
                factory = data['BSSH_NM'] 
    #            product_report_number = data['PRDLST_REPORT_NO'] 
                product_name = data['PRDLST_NM'] 
                permission_date = data['PRMS_DT'] 
    #            shelflife = data['POG_DAYCNT']
    #            dispose = data['DISPOS'] 
    #            intake_method = data['NTK_MTHD'] 
    #            primary_functionality = data['PRIMARY_FNCLTY'] 
    #            caution = data['IFTKN_ATNT_MATR_CN'] 
    #            storage_method = data['CSTDY_MTHD']
    #            category = data['PRDLST_CDNM']
    #            standard_test = data['STDR_STND']
    #            high_low_calorie = data['HIENG_LNTRT_DVS_NM'] 
    #            production = data['PRODUCTION']
    #            child = data['CHILD_CRTFC_YN']
                product_shape = data['PRDT_SHAP_CD_NM'] 
                package = data['FRMLC_MTRQLT']
                substance = data['RAWMTRL_NM']
                substance_list = substance.split(',')
                substance_list.sort()
    #            type_of_business = data['INDUTY_CD_NM']
    #            last_update = data['LAST_UPDT_DTM'] # 최종수정일자
    
            drug = {'lecense_number': license_number, 'product_name': product_name, 'substance_list': substance_list, 
                    'package': package, 'product_shape': product_shape, 'factory': factory, 'permission_date': permission_date}

            print(drug)
            db.healthnutritionfood.insert_one(drug)

    return jsonify({'result': 'success'})


# db에서 약 정보 받아와서 클라이언트로 보내주는부분
@app.route('/drugs', methods=['GET'])
def get_drugs():
    drugs = db.healthnutritionfood.find({}, {'_id': 0})
    return jsonify({'result': 'success', 'drugs': list(drugs)})

00
if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
