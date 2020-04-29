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
    
def get_total_count():
    URL = 'http://openapi.foodsafetykorea.go.kr/api/b7511e10cbfd4b10a763/I0030/json/1/2'
    response = requests.get(URL)
    code = response.status_code
    if code == 200: #200: 아무 오류 없이 잘 대답이 온 것
        try:
            total_count = int(response.json()['I0030']['total_count'])
        except:
            total_count = -1
    else:
        total_count = -1
    return total_count

def crawl_all_data(curr_count, total_count):
    # 식약처 api로 새로운 데이터 받아오기 requests (curr_count+1 / total_count) -> 1000개씩 나눠서
    for i in range(curr_count + 1, total_count + 1, 1000): #range (a,b,c): a부터 b-1 까지 c 간격으로
        if total_count - i + 1 > 1000:
            remain = i+999
        else:
            remain = total_count

        URL = 'http://openapi.foodsafetykorea.go.kr/api/b7511e10cbfd4b10a763/I0030/json/' + str(i) + '/' + str(remain)
        response = requests.get(URL)
        code = response.status_code #response 안에 status_code가 저장되어있음 항상. 우린 그걸 가져온거.
        if code == 200: #200:아무 오류 없이 잘 대답이 온 것 / 500: internal server error
            drugs = response.json()['I0030']['row']
            insert_drugs(drugs)

# API 역할을 하는 부분

# 식약처 api로 총 데이터 수 받아오기
@app.route('/api/total_count', methods=['GET'])
def total_count():
    return str(get_total_count())

# 식약처에서 데이터 받아와서 db에 저장
@app.route('/api/update', methods=['GET'])
def update():
    curr_count = int(db.healthnutritionfood.count())    # 기존 DB에 저장된 데이터 수 ex) 100
    total_count = get_total_count()     # 등록된 식약처 데이터 수 ex) 28000
    print('curr_count:', curr_count, 'total_count:', total_count)
    if total_count == -1:
        return jsonify({'result': 'fail', 'curr_count': curr_count, 'total_count': total_count})
    crawl_all_data(curr_count, total_count)
    return jsonify({'result': 'success', 'msg': '크롤링이 완료되었습니다. 최신 DB로 업데이트하려면 update를 클릭하세요'})

# db에서 약 정보 받아와서 클라이언트로 보내주는 부분 function update()
@app.route('/api/drugs', methods=['GET'])
def get_all_drugs():
    drugs = db.healthnutritionfood.find({}, {'_id': 0})
    return jsonify({'result': 'success', 'drugs': list(drugs)})

# substance_list가 selected에서 값이 true인 영양소들을 모두 갖고 있는지 확인하는 함수
# e.g. selected = {'비타민A': 'true', '베타카로틴': 'false'} 인 경우,
# 비타민A가 substance_list 안에 있을 경우 True, 없으면 False
def contains_all_nut(selected, substance_list):
    for key, value in selected.items():
        if value == 'true': # 선택한 영양소에 대해서
            if not key in substance_list:   # 만약 없으면
                print(key, substance_list)
                return False
    return True # 만약 중간에 없는게 없이 잘 끝났으면 다 있는거

@app.route('/api/search', methods=['post'])
def search():
    selected = request.form.to_dict()
    drugs = list(db.healthnutritionfood.find({}, {'_id': 0}))
    found_drugs = []
    for drug in drugs:
        if contains_all_nut(selected, drug['substance_list']):
            found_drugs.append(drug)
    
    if not found_drugs:
        return jsonify({'result': 'not found'})
    return jsonify({'result': 'success', 'drugs': found_drugs})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)