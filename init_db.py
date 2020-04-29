from pymongo import MongoClient
from bs4 import BeautifulSoup
import requests

SAMPLE_DATA = [
    {'LCNS_NO': '20040020002', 'BSSH_NM': '코스맥스바이오(주)', 'PRDLST_REPORT_NO': '200400200021640',
        'PRDLST_NM': '+프리맥', 'PRMS_DT': '20150624', 'POG_DAYCNT': '제조일로부터 2년', 'DISPOS': '흑갈색의 내용물을 함유한 투명한 연질캡슐.',
        'NTK_MTHD': '1일 1회, 1회 2캡슐을 충분한 물과 함께 섭취하십시오. 1일 2회, 1회 1캡슐을 충분한 물과 함께 섭취하십시오.',
        'PRIMARY_FNCLTY': '혈중 콜레스테롤 수치 개선에 도움을 줄 수 있음.',
        'IFTKN_ATNT_MATR_CN': '임산부, 수유부, 청소년 및 어린이는 섭취를 피하십시오. 의약품 복용(심혈관 등), 혈액 응고장애가 있거나 수술예정인 사람은 전문가와 상담하십시오. 이상사례 발생 시 섭취를 중단하고 전문가와 상담하십시오. 본 제품은 섭취자의 신체상태에 따라 반응에 차이가 있을 수 있습니다. 임산부, 수유부, 질병으로 인해 치료중인 분은 섭취 전 고객센터나 구입처로 문의하십시오. 특정 성분에 알레르기 체질이신 분은 섭취 전에 반드시 원료(성분)를 확인하신 후 섭취하시기 바랍니다. 섭취량 및 섭취방법을 확인 한 후 섭취하시고, 기타 제품관련사항은 고객센터로 문의해 주십시오.',
        'CSTDY_MTHD': '', 
        'STDR_STND': '1) 성상 : 고유의 색택과 향미를 가지고 이미, 이취가 없어야 한다. 2) 총 지방족 알코올 함량 : 표시량(5.4mg/1000mg)의 80~120% 3) 납(mg/kg) : 1.0 이하 4) 총비소(mg/kg) : 1.0 이하 5) 카드뮴(mg/kg) : 0.5 이하 6) 총수은(mg/kg) : 0.5 이하 7) 아세톤(g/kg) : 불검출 8) 헥산(g/kg) : 0.005 이하 9) 대장균군 : 음성 10) 붕해시험 : 20분 이내',
        'HIENG_LNTRT_DVS_NM': '해당없음', 'PRODUCTION': '아니오', 'PRDT_SHAP_CD_NM': '캡슐',
        'FRMLC_MTRQLT': 'PTP(염화비닐수지+알루미늄호일), HDPE(고밀도폴리에틸렌), PE(폴리에틸렌), PET(폴리에틸렌테레프탈레이트), PP(폴리프로필렌), PS(폴리스틸렌), 유리, AL(알루미늄), 철.',
        'RAWMTRL_NM': '폴리코사놀-사탕수수 왁스알코올(2006-4)',
        'LAST_UPDT_DTM': '', 'PRDLST_CDNM': '', 'CHILD_CRTFC_YN': '', 'INDUTY_CD_NM': ''
        }, 
    {'LCNS_NO': '20110020001', 'BSSH_NM': '주식회사 성윤 에프엔지(F&G)', 'PRDLST_REPORT_NO': '201100200015',
        'PRDLST_NM': '6년근 고려홍삼정 PREMIUM', 'PRMS_DT': '20111209', 'POG_DAYCNT': '제조일로부터 24개월', 'DISPOS': '암갈색의 액상으로 고유의 색택과 향미를 가지며 이미·이취가 없어야 한다.',
        'NTK_MTHD': '1일 3회, 1회 1스푼(3.2g)씩 물에 녹여 섭취 하십시요.',
        'PRIMARY_FNCLTY': '①면역력 증진②피로개선③혈소판 응집 억제를 통한 혈액흐름에 도움④기억력 개선⑤항산화에 도움을 줄 수 있음',
        'IFTKN_ATNT_MATR_CN': '[홍삼제품]의약품(당뇨치료제, 혈액항응고제) 복용 시 섭취에 주의 2) 특이체질등 알레르기 체질의 경우 제품성분을 확인 후 섭취하시기 바랍니다. 3) 15세 이하의 어린이는 상기 섭취량의 절반 정도를 섭취하시요. 4) 제품 개봉 또는 섭취시에 포장재로 인한 상처를 입을수 있으니주의 하십시오.	직사광선을 피해 건조하고 서늘한 곳에서 보관한다.',
        'CSTDY_MTHD': '', 
        'STDR_STND': '① 성상 : 암갈색의 액상으로 고유의 색택과 향미를 가지며 이미·이취가 없어야 한다. ② 진세노사이드 Rg1, Rb1 및 Rg3의 합 :최종제품 - 표시량(3.840㎎/9.6g)의 80% 이상 ③ 세균수 : 1㎖ 당 3,000 CFU 이하 ④ 대장균군 : 음성',
        'HIENG_LNTRT_DVS_NM': '해당없음', 'PRODUCTION': '아니오', 'PRDT_SHAP_CD_NM': '액상',
        'FRMLC_MTRQLT': '유리, 도자기.',
        'RAWMTRL_NM': '홍삼제품',
        'LAST_UPDT_DTM': '', 'PRDLST_CDNM': '', 'CHILD_CRTFC_YN': '', 'INDUTY_CD_NM': ''}, 
    {'LCNS_NO': '20110020001', 'BSSH_NM': '하하', 'PRDLST_REPORT_NO': '201100200015',
        'PRDLST_NM': '베타A', 'PRMS_DT': '20111209', 'POG_DAYCNT': '제조일로부터 24개월', 'DISPOS': '암갈색의 액상으로 고유의 색택과 향미를 가지며 이미·이취가 없어야 한다.',
        'NTK_MTHD': '1일 3회, 1회 1스푼(3.2g)씩 물에 녹여 섭취 하십시요.',
        'PRIMARY_FNCLTY': '①면역력 증진②피로개선③혈소판 응집 억제를 통한 혈액흐름에 도움④기억력 개선⑤항산화에 도움을 줄 수 있음',
        'IFTKN_ATNT_MATR_CN': '[홍삼제품]의약품(당뇨치료제, 혈액항응고제) 복용 시 섭취에 주의 2) 특이체질등 알레르기 체질의 경우 제품성분을 확인 후 섭취하시기 바랍니다. 3) 15세 이하의 어린이는 상기 섭취량의 절반 정도를 섭취하시요. 4) 제품 개봉 또는 섭취시에 포장재로 인한 상처를 입을수 있으니주의 하십시오.	직사광선을 피해 건조하고 서늘한 곳에서 보관한다.',
        'CSTDY_MTHD': '', 
        'STDR_STND': '① 성상 : 암갈색의 액상으로 고유의 색택과 향미를 가지며 이미·이취가 없어야 한다. ② 진세노사이드 Rg1, Rb1 및 Rg3의 합 :최종제품 - 표시량(3.840㎎/9.6g)의 80% 이상 ③ 세균수 : 1㎖ 당 3,000 CFU 이하 ④ 대장균군 : 음성',
        'HIENG_LNTRT_DVS_NM': '해당없음', 'PRODUCTION': '아니오', 'PRDT_SHAP_CD_NM': '액상',
        'FRMLC_MTRQLT': '유리, 도자기.',
        'RAWMTRL_NM': '베타카로틴, 비타민A',
        'LAST_UPDT_DTM': '', 'PRDLST_CDNM': '', 'CHILD_CRTFC_YN': '', 'INDUTY_CD_NM': ''}, 
        {'LCNS_NO': 'bbb', 'BSSH_NM': 'ㅎ', 'PRDLST_REPORT_NO': '1234',
        'PRDLST_NM': '비타민A', 'PRMS_DT': '20111209', 'POG_DAYCNT': '제조일로부터 24개월', 'DISPOS': '암갈색의 액상으로 고유의 색택과 향미를 가지며 이미·이취가 없어야 한다.',
        'NTK_MTHD': '1일 3회, 1회 1스푼(3.2g)씩 물에 녹여 섭취 하십시요.',
        'PRIMARY_FNCLTY': '①면역력 증진②피로개선③혈소판 응집 억제를 통한 혈액흐름에 도움④기억력 개선⑤항산화에 도움을 줄 수 있음',
        'IFTKN_ATNT_MATR_CN': '[홍삼제품]의약품(당뇨치료제, 혈액항응고제) 복용 시 섭취에 주의 2) 특이체질등 알레르기 체질의 경우 제품성분을 확인 후 섭취하시기 바랍니다. 3) 15세 이하의 어린이는 상기 섭취량의 절반 정도를 섭취하시요. 4) 제품 개봉 또는 섭취시에 포장재로 인한 상처를 입을수 있으니주의 하십시오.	직사광선을 피해 건조하고 서늘한 곳에서 보관한다.',
        'CSTDY_MTHD': '', 
        'STDR_STND': '① 성상 : 암갈색의 액상으로 고유의 색택과 향미를 가지며 이미·이취가 없어야 한다. ② 진세노사이드 Rg1, Rb1 및 Rg3의 합 :최종제품 - 표시량(3.840㎎/9.6g)의 80% 이상 ③ 세균수 : 1㎖ 당 3,000 CFU 이하 ④ 대장균군 : 음성',
        'HIENG_LNTRT_DVS_NM': '해당없음', 'PRODUCTION': '아니오', 'PRDT_SHAP_CD_NM': '액상',
        'FRMLC_MTRQLT': '유리, 도자기.',
        'RAWMTRL_NM': '비타민A',
        'LAST_UPDT_DTM': '', 'PRDLST_CDNM': '', 'CHILD_CRTFC_YN': '', 'INDUTY_CD_NM': ''}
]


client = MongoClient('localhost', 27017) #Mongoclient를 통해서 localhost 포트 27017 코드에서 실행중인 몽고 DB와 직접 연결
db = client.dbsparta # 그중에서 dbsparta라는 db를 뽑아내서 그 안에 drugs? 라는 컬렉션을 만들어 db.healthnutritionfood.insert_one(drug)에 스크래핑 결과를 저장
db.healthnutritionfood.drop()  # mystar 콜렉션을 모두 지워줍니다.

# 식약처 api로 총 데이터 수 받아오기 ex) 28050
def get_total_count():
    URL = 'http://openapi.foodsafetykorea.go.kr/api/b7511e10cbfd4b10a763/I0030/json/1/2'
    response = requests.get(URL)
    code = response.status_code
    if code == 200: #200: 아무 오류 없이 잘 대답이 온 것
        total_count = int(response.json()['I0030']['total_count'])
    else:
        total_count = -1
    return total_count

def insert_drugs(drugs):
    for data in drugs:
        license_number = data['LCNS_NO'] 
        factory = data['BSSH_NM'] 
        product_name = data['PRDLST_NM'] 
        permission_date = data['PRMS_DT'] 
        product_shape = data['PRDT_SHAP_CD_NM'] 
        package = data['FRMLC_MTRQLT']
        substance = data['RAWMTRL_NM']
        substance_list = substance.split(',')
        for i in range(len(substance_list)):
            substance_list[i] = ''.join(substance_list[i].strip().split())
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


# 현재 db에 저장되지 않은 데이터 크롤해서 db에 넣기
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


def update_db(IS_TEST_MODE = False):
    if IS_TEST_MODE:
        insert_drugs(SAMPLE_DATA)
        return
    curr_count = int(db.healthnutritionfood.count())    # 기존 DB에 저장된 데이터 수 ex) 100
    total_count = get_total_count()     # 등록된 식약처 데이터 수 ex) 28000
    print('curr_count:', curr_count, 'total_count:', total_count)
    crawl_all_data(curr_count, total_count)

### 실행하기
IS_TEST_MODE = True
db.healthnutritionfood.drop()  # healthnutritionfood 콜렉션을 모두 지우기
update_db(IS_TEST_MODE)