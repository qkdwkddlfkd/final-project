from pymongo import MongoClient #파이썬과 몽고DB 연결
from bs4 import BeautifulSoup
import requests
from flask import Flask, render_template, jsonify, request
app = Flask(__name__)

# client = MongoClient('mongodb://sampleID:samplePW@12.34.56.78', 27017)
# client = MongoClient('mongodb://qkdwkddlfkd:june7575@15.164.216.152', 27017)
client = MongoClient('localhost', 27017) #Mongoclient를 통해서 localhost 포트 27017 코드에서 실행중인 몽고 DB와 직접 연결
db = client.dbsparta # 그중에서 dbsparta라는 db를 뽑아내서 그 안에 drugs? 라는 컬렉션을 만들어 db.healthnutritionfood.insert_one(drug)에 스크래핑 결과를 저장
# HTML을 주는 부분
@app.route('/')
def home():
    return render_template('food.html')
    
# API 역할을 하는 부분

# 식약처에서 데이터 받아와서 db에 저장
@app.route('/crawl', methods=['GET'])
def crawl():
    # 1. 기존 DB에서 저장된 데이터 수 받아오기 ex) 28000 -> curr_count
    curr_count = int(db.healthnutritionfood.count()) #int 형변환 안했더니 아래 코드에서 str문자열이라고 오류나서 정수형 변환처리함.
    print(curr_count)

    # 2. 식약처 api로 총 데이터 수 받아오기 requests (1/2) -> total count ex) 28050
    URL = 'http://openapi.foodsafetykorea.go.kr/api/b7511e10cbfd4b10a763/I0030/json/1/2'
    response = requests.get(URL) #클라이언트로부터 url 가져오기
    code = response.status_code #response 안에 status_code가 저장되어있음 항상. 우린 그걸 가져온거.
    if code == 200: #200:아무 오류 없이 잘 대답이 온 것 / 500: internal server error
        total_count = int(response.json()['I0030']['total_count'])
    elif code == 500:
        print('Internal Server Error (Code 500)')

    # 3. 식약처 api로 새로운 데이터 받아오기 requests (curr_count+1 / total_count) -> 1000개씩 나눠서
    # 4. 이때마다 db.insert_one하기
    for i in range(curr_count + 1, total_count, 1000): #range (a,b,c): a부터 b-1 까지 c 간격으로
        if total_count - i + 1 > 1000:
            remain = i+999
        else:
            remain = total_count
        
        URL = 'http://openapi.foodsafetykorea.go.kr/api/b7511e10cbfd4b10a763/I0030/json/' + str(i) + '/' + str(remain)
        response = requests.get(URL)
        code = response.status_code #response 안에 status_code가 저장되어있음 항상. 우린 그걸 가져온거.
        if code == 200: #200:아무 오류 없이 잘 대답이 온 것 / 500: internal server error
            datas = response.json()['I0030']['row']

            for data in datas:
                license_number = data['LCNS_NO'] 
                factory = data['BSSH_NM'] 
                product_name = data['PRDLST_NM'] 
                permission_date = data['PRMS_DT'] 
                product_shape = data['PRDT_SHAP_CD_NM'] 
                package = data['FRMLC_MTRQLT']
                substance = data['RAWMTRL_NM']
                substance_list = substance.split(',')
                for i in range(len(substance_list)):
                    substance_list[i] = substance_list[i].strip()
                substance_list.sort()

                last_update = data['LAST_UPDT_DTM']
                product_report_number = data['PRDLST_REPORT_NO'] 
                shelflife = data['POG_DAYCNT']
                dispose = data['DISPOS'] 
                intake_method = data['NTK_MTHD'] 
                primary_functionality = data['PRIMARY_FNCLTY'] 
                caution = data['IFTKN_ATNT_MATR_CN'] 
                storage_method = data['CSTDY_MTHD']
                category = data['PRDLST_CDNM']
                standard_test = data['STDR_STND']
                high_low_calorie = data['HIENG_LNTRT_DVS_NM'] 
                production = data['PRODUCTION']
                child = data['CHILD_CRTFC_YN']
                type_of_business = data['INDUTY_CD_NM']

            drug = {'license_number': license_number, 'product_name': product_name, 'substance_list': substance_list, 
                    'package': package, 'product_shape': product_shape, 'factory': factory, 
                    'permission_date': permission_date, 'last_update': last_update,
                    'product_report_number' : product_report_number, 'shelflife':shelflife, 'dispose': dispose,
                    'intake_method': intake_method, 'primary_functionality': primary_functionality, 'caution':caution,
                    'storage_method': storage_method, 'category':category, 'standard_test':standard_test, 'high_low_calorie':high_low_calorie,
                    'production':production, 'child':child, 'type_of_business':type_of_business
                    }

            print(drug)
            db.healthnutritionfood.insert_one(drug)

    return jsonify({'result': 'success', 'msg': '크롤링이 완료되었습니다. 최신 DB로 업데이트하려면 update를 클릭하세요'})


# db에서 약 정보 받아와서 클라이언트로 보내주는 부분 function update()
@app.route('/drugs', methods=['GET'])
def get_all_drugs():
    drugs = db.healthnutritionfood.find({}, {'_id': 0})
    return jsonify({'result': 'success', 'drugs': list(drugs)})

@app.route('/drugs/search', methods=['post'])
def search():
    print(request.form)
    selected = request.form['selected']
    drugs = list(db.healthnutritionfood.find({}, {'_id': 0}))
    found_drugs = []
    for drug in drugs:
        if all(e in drug['substance_list'] for e in selected):
            found_drugs.append(drug)
    
    if not found_drugs:
        return jsonify({'result': 'not found'})
    return jsonify({'result': 'success', 'drugs': found_drugs})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)






  
#            product_report_number = data['PRDLST_REPORT_NO'] 
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
    #            type_of_business = data['INDUTY_CD_NM']
    #            last_update = data['LAST_UPDT_DTM'] # 최종수정일자