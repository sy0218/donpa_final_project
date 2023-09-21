import pandas as pd
import pymysql
from pymongo import MongoClient
from sklearn.preprocessing import StandardScaler
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib
from sklearn.preprocessing import OneHotEncoder
import xgboost as xgb
import argparse

# 연결 정보 설정
host = "10.233.18.183"
port = 3306
database = "donpa_item"
user = "root"
password = "1234"

# 연결
connection = pymysql.connect(
    host=host,
    port=port,
    user=user,
    password=password,
    database=database
)

# SQL 쿼리
query = "SELECT * FROM goldprice"
# 데이터프레임으로 변환
date_df = pd.read_sql(query, connection)
# 연결 종료
connection.close


# MongoDB 연결 설정
client = MongoClient("mongodb://3.38.178.84:27017/")
db = client["donpa"]  # 데이터베이스명
collection = db["donpa_aabata_rare"]  # 컬렉션명

# 컬렉션 데이터 조회
data = collection.find()

# 데이터프레임으로 변환
df = pd.DataFrame(data)

# _id 컬럼은 제거해주자
df = df.drop(columns="_id") 

df['price'] = df['price'].astype('float')

df['soldDate'] = df['soldDate'].str.replace('-','')

# sell, buy컬럼 붙여주자!!
df = df.merge(date_df, left_on='soldDate', right_on='date', how='left')

# sell, buy값이 널값이면 가장 최근의 sell, buy값으로 대체해주자
null_check = df['sell'].isnull().sum()
if null_check != 0:
    # date_df의 맨 마지막 값을 가져와서 NaN 값을 채우기
    last_date_df_row = date_df.iloc[-1]
    df['sell'].fillna(last_date_df_row['sell'], inplace=True)
    df['buy'].fillna(last_date_df_row['buy'], inplace=True)

# date컬럼 삭제해주자
df.drop(columns = 'date', inplace=True)
df['soldDate'] = pd.to_datetime(df['soldDate'])

# 년 컬럼 추가
df['year'] = df['soldDate'].dt.year

# 월 컬럼 추가
df['month'] = df['soldDate'].dt.month

# 일 컬럼 추가
df['day'] = df['soldDate'].dt.day

# 요일 컬럼 추가해주자
df['day_name'] = df['soldDate'].dt.day_name()

# 필요 없는 컬럼 삭제
df.drop(columns = 'soldDate', inplace=True)
# ava_rit도 어차피다 레어이니까 삭제
df.drop(columns = 'ava_rit', inplace=True)

# 타겟 컬러 맨뒤로 보내기
price_column = df.pop('price')
df['price'] = price_column

title_data = df['title'].drop_duplicates()
jobname_data = df['jobname'].drop_duplicates()
emblem_data = df['emblem'].drop_duplicates()

# 장고 select 목록 테이블에 넣어주는 코드
import pymysql
# 연결 정보 설정
host = "10.233.18.183"
port = 3306
database = "donpa_item"
user = "root"
password = "1234"

# 연결
connection = pymysql.connect(
    host=host,
    port=port,
    user=user,
    password=password,
    database=database
)

try:
    # 커서 생성
    cursor = connection.cursor()

    # 데이터 입력 (존재하지 않는 데이터만 입력)
    for item in title_data:
        sql = f"INSERT INTO input_list (title) SELECT '{item}' FROM DUAL WHERE NOT EXISTS (SELECT * FROM input_list WHERE title = '{item}')"
        cursor.execute(sql)

    for item in jobname_data:
        sql = f"INSERT INTO input_list (jobname) SELECT '{item}' FROM DUAL WHERE NOT EXISTS (SELECT * FROM input_list WHERE jobname = '{item}')"
        cursor.execute(sql)

    for item in emblem_data:
        sql = f"INSERT INTO input_list (emblem) SELECT '{item}' FROM DUAL WHERE NOT EXISTS (SELECT * FROM input_list WHERE emblem = '{item}')"
        cursor.execute(sql)

    # 커밋
    connection.commit()
except Exception as e:
    # 에러 발생 시 롤백
    connection.rollback()
    print(f"데이터 입력 중 오류 발생: {str(e)}")
finally:
    # 연결 종료
    connection.close()

X_train = df.drop(columns = 'price')
y_train = df['price']


X_train, X_validation, Y_train, Y_validation = train_test_split(X_train,y_train, test_size=0.2, random_state=1)
X_train.reset_index(drop=True, inplace=True)
X_validation.reset_index(drop=True, inplace=True)

obj_col = X_train.select_dtypes(include='object').columns

sds = StandardScaler()
sds.fit(X_train.drop(columns = obj_col))

X_train_sc = sds.transform(X_train.drop(columns = obj_col))
X_train_sc = pd.DataFrame(X_train_sc, columns = X_train.drop(columns = obj_col).columns)

X_validation_sc = sds.transform(X_validation.drop(columns = obj_col))
X_validation_sc = pd.DataFrame(X_validation_sc, columns = X_validation.drop(columns = obj_col).columns)


# object 타입 컬럼 붙여주기
for i in obj_col:
    X_train_sc[i] = X_train[i]
    X_validation_sc[i] = X_validation[i]
# 스케일러 객체 저장
joblib.dump(sds, '/home/jovyan/scaler/scaler.pkl')


# OneHotEncoder 객체 생성
encoder = OneHotEncoder()

X_full = pd.concat([X_train_sc, X_validation_sc])

# 범주형 열만 선택
obj_df = X_full.select_dtypes(include='object')

# 숫자형 열만 선택
no_obj_df = X_full.select_dtypes(exclude='object')

# 범주형 열을 원핫 인코딩
encoded_features = encoder.fit_transform(obj_df)

# 인코딩된 결과를 데이터프레임으로 변환
encoded_df = pd.DataFrame(encoded_features.toarray(), columns=encoder.get_feature_names(obj_df.columns))

# 인코딩된 범주형 열과 숫자형 열을 합침
X_train_sc_ec = pd.concat([no_obj_df[:len(X_train_sc)] , encoded_df[:len(X_train_sc)]], axis = 1)
X_validation_sc_ec = pd.concat([no_obj_df[len(X_train_sc):] , encoded_df[len(X_train_sc):].reset_index(drop=True)], axis = 1)

# 인코딩 객체 저장
joblib.dump(encoder, '/home/jovyan/encoder/encoder.pkl')

import re

# 데이터프레임의 컬럼 이름에서 특수 문자를 제거하고 변경할 새로운 컬럼 이름 리스트 생성
new_columns = []
for old_column in X_train_sc_ec.columns:
    new_column = re.sub(r'[^\w\s]', '', old_column)  # 특수 문자 제거
    new_columns.append(new_column)

# 컬럼 이름을 새로운 이름으로 설정
X_train_sc_ec.columns = new_columns
X_validation_sc_ec.columns = new_columns

X_train_sc_ec.to_csv('/home/jovyan/csv/X_train_sc_ec.csv', index=False)
X_validation_sc_ec.to_csv('/home/jovyan/csv/X_validation_sc_ec.csv', index=False)
Y_train.to_csv('/home/jovyan/csv/Y_train.csv', index=False)
Y_validation.to_csv('/home/jovyan/csv/Y_validation.csv', index=False)

parser = argparse.ArgumentParser()
parser.add_argument('--learning_rate', required=False, type=float, default=0.1)
parser.add_argument('--n_estimators', required=False, type=int, default=100)
parser.add_argument('--max_depth', required=False, type=int, default=5)

args = parser.parse_args()


xgb_model = xgb.XGBRegressor(random_state=10,
                            learning_rate=args.learning_rate,
                            n_estimators=args.n_estimators,
                            max_depth=args.max_depth
                            )
xgb_model.fit(X_train_sc_ec, Y_train)

# 모델을 파일로 저장
joblib.dump(xgb_model, '/home/jovyan/model/model.pkl')

# 검증 데이터 예측
pred_validation = xgb_model.predict(X_validation_sc_ec)

# 성능평가
from sklearn.metrics import mean_absolute_error
mae_validation = mean_absolute_error(Y_validation, pred_validation)
print("mae_validation="+str(mae_validation))
