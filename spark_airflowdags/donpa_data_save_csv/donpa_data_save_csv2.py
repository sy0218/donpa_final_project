from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.sql.types import DoubleType
from pyspark.sql.functions import current_timestamp, year, month, dayofmonth, hour
from pyspark.sql.functions import concat_ws, lit, to_timestamp
import requests
import os

# 파이썬 스크립트 내에서 외부 명령어를 실행하고 그 결과를 처리하는 기능
import subprocess

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
    "itemName": "무결점 조화의 결정체",
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

# 시간대 같은 항목들의 unitPrice를 평균으로 합치기
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


try:
    previous_df = spark.read.option("header", "true").csv("hdfs:///user/ubuntu/donpa_data2.csv/*.csv")
except:
    previous_df = None

if previous_df is not None:
    # now_time 컬럼을 timestamp 형식으로 변환
    previous_df = previous_df.withColumn("now_datetime", col("now_datetime").cast("timestamp"))

    # unitPrice 컬럼을 숫자 형식으로 변환
    previous_df = previous_df.withColumn("unitPrice", col("unitPrice").cast(DoubleType()))

    # 두 데이터프레임을 수직으로 합치기
    merged_df = previous_df.union(grouped_df)

    # 시간대 같은 항목들의 unitPrice를 평균으로 합치기
    merged_df = merged_df.groupBy("now_datetime", "itemName").avg("unitPrice").withColumnRenamed("avg(unitPrice)", "unitPrice")

    # 시간 순으로 정렬
    merged_df = merged_df.orderBy("now_datetime")
    
    # CSV 파일로 저장
    merged_df.write.csv("new_donpa2.csv", header=True, mode="overwrite")

    # 기존 디렉토리 삭제
    os.system("hdfs dfs -rm -r donpa_data2.csv")

    # 새로운 디렉터리 이름 변경
    os.system("hdfs dfs -mv new_donpa2.csv donpa_data2.csv")
else:
    # grouped_df로 바로 저장
    grouped_df.write.csv("donpa_data2.csv", header=True, mode="overwrite")


print("성공")

# 스파크 세션 종료
spark.stop()
