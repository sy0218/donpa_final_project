from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.sql.types import DoubleType
import requests

# 스파크 세션 생성
spark = SparkSession.builder \
        .master("yarn") \
        .appName("aabataProcessing") \
        .getOrCreate()

# API 엔드포인트 URL
api_url = "https://api.neople.co.kr/df/avatar-market/sold"

# 파라미터 설정
params = {
        "limit": 50,
        "q": 'avatarSet:true,avatarRarity:레어',
        "apikey": "Q3A8yWb7Un1oXuM7uC5nIRV6zzGL23YP"
}

# GET 요청 보내기
response = requests.get(api_url, params=params)

# 응답 데이터 확인
if response.status_code == 200:
    data = response.json()
    # 데이터 처리 및 출력
    #print(data)
else:
    print("API 요청 실패:", response.status_code)

test1 = data.get("rows")

# 필요한 필드만 추출하여 저장할 리스트
extracted_data = []

for item in test1:
    title = item['title']
    jobname = item['jobName']
    price = item['price']
    ava_rit = item['avatarRarity']
    emblem = item['emblem']['name']
    soldDate = item['soldDate']

    extracted_data.append({'title': title, 'price': price, 'ava_rit': ava_rit, 'jobname': jobname,
                           'emblem': emblem, 'soldDate': soldDate})

# 데이터 프레임 생성
df = spark.createDataFrame(extracted_data)

# 원하는 순서로 컬럼 선택
df = df.select('soldDate', 'title', 'ava_rit', 'jobname', 'emblem', 'price')

# 중복 레코드 제거
df = df.dropDuplicates()

# soldDate 컬럼을 기준으로 정렬
df = df.orderBy("soldDate")

# csv파일로 저장
csv_path = "donpa_aabata_rare.csv"
df.write.csv(csv_path, header=True, mode="overwrite")

# 스파크 세션 종료
spark.stop()

print("데이터를 csv파일로 저장했습니다")
