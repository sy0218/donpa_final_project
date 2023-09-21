from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.sql.types import DoubleType
from pyspark.sql.functions import current_timestamp
from pyspark.sql.functions import year, month, dayofmonth, hour
from pyspark.sql.functions import concat_ws, lit, to_timestamp
import requests

# 스파크 세션 생성
spark = SparkSession.builder \
        .master("yarn") \
        .config("spark.sql.legacy.timeParserPolicy", "LEGACY") \
        .appName("DataProcessing") \
        .getOrCreate()

# API 엔드포인트 URL
api_url = "https://api.neople.co.kr/df/auction-sold"

# 파라미터 설정
params = {
    "itemName": "왜곡된 차원의 큐브[교환가능]",
    "wordType": "match",
    "wordShort": "false",
    "limit": 10,
    "apikey": "JUG54ELPbKttanbis2VPFNqC9LJOM7v4"
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
formatted_data = [{"soldDate": row["soldDate"], "itemName": row["itemName"], "unitPrice": row["unitPrice"]} for row in test1]

# 데이터프레임 생성
df = spark.createDataFrame(formatted_data)

# 불필요한 컬럼 제거
df = df.drop("soldDate")

# 수집한 시간 컬럼 추가
df = df.withColumn("now_time", current_timestamp())

# now_time 컬럼을 timestamp 형식으로 변환
df = df.withColumn("now_time", col("now_time").cast("timestamp"))

# unitPrice 컬럼을 숫자 형식으로 변환
df = df.withColumn("unitPrice", col("unitPrice").cast(DoubleType()))

# 시간이 같은 항목들의 unitPrice를 평균으로 합치기
grouped_df = df.groupBy(year("now_time").alias("year"),
                        month("now_time").alias("month"),
                        dayofmonth("now_time").alias("day"),
                        hour("now_time").alias("hour"),
                        "itemName").avg("unitPrice").withColumnRenamed("avg(unitPrice)", "unitPrice")

grouped_df = grouped_df.withColumn("now_datetime",
                                   to_timestamp(concat_ws("-", "year", "month", "day", "hour"), "yyyy-MM-dd-HH"))

grouped_df = grouped_df.drop("year", "month", "day", "hour")

# 원하는 순서로 컬럼 선택
grouped_df = grouped_df.select("now_datetime", "itemName", "unitPrice")

csv_path = "donpa_data9.csv"
grouped_df.write.csv(csv_path, header=True, mode="overwrite")

# 스파크 세션 종료
spark.stop()

print("데이터를 CSV 파일로 저장했습니다.")
