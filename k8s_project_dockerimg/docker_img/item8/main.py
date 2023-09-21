import pandas as pd
import pymysql
from pymongo import MongoClient
from sklearn.preprocessing import StandardScaler
import numpy as np

# 레이어를 선형으로 쌓아 순차적으로 연결하여 모델을 만드는 방식
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

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

date_df = pd.read_sql(query, connection)

# 연결 종료
connection.close()

# MongoDB 연결 설정
client = MongoClient("mongodb://3.38.178.84:27017/")
db = client["donpa"]  # 데이터베이스명
collection = db["donpa_data7"]  # 컬렉션명

# 컬렉션 데이터 조회
data = collection.find()

# 데이터프레임으로 변환
df = pd.DataFrame(data)

# _id 컬럼은 제거해주자
df = df.drop(columns="_id") 


# object타입의 데이터 datetime타입으로 변경하는 코드
df['now_datetime'] = pd.to_datetime(df['now_datetime'])
# 시간까지만 잘라내기
df['now_datetime'] = df['now_datetime'].dt.strftime("%Y-%m-%d %H:%M")
# now_datetime 다시 datetime타입으로 변경하는 코드
df['now_datetime'] = pd.to_datetime(df['now_datetime'])

# unitPrice 컬럼 float타입으로 변경
df['unitPrice'] = df['unitPrice'].astype('float')

#soldDate 컬럼 인덱스로 변경
df.set_index('now_datetime', inplace=True)

# itemName컬럼은 사용하지 안을거임
item_name = df.iloc[0,0] # 지우기전 아이템 이름 저장해주자
df = df.drop(columns= 'itemName')
df = df.reset_index(drop=False)

# 피처 엔지니어링
# 30분 이평선
ma3 = df['unitPrice'].rolling(window=3).mean()
df.insert(len(df.columns), 'ma3', ma3)

# 기존 데이터가 있다면 NaN에 이동평균선 값을 채워넣어주는 방법
# 기존 데이터가 없다면 NaN에 0 값을 채워줘야 함
df = df.fillna(0)

# unitPrice 컬럼 float타입으로 변경
df['unitPrice'] = df['unitPrice'].astype('float')

# sell, buy컬럼을 합쳐주기 위해 date컬럼 생성
df['date'] = pd.to_datetime(df['now_datetime']).dt.strftime('%Y%m%d')

# sell, buy컬럼 붙여주자!!
df = df.merge(date_df, left_on='date', right_on='date', how='left')

# sell, buy값이 널값이면 가장 최근의 sell, buy값으로 대체해주자
null_check = df['sell'].isnull().sum()
if null_check != 0:
    # date_df의 맨 마지막 값을 가져와서 NaN 값을 채우기
    last_date_df_row = date_df.iloc[-1]
    df['sell'].fillna(last_date_df_row['sell'], inplace=True)
    df['buy'].fillna(last_date_df_row['buy'], inplace=True)

# 붙여주고 date는 이제 필요없으므로 drop시켜줌
df.drop(columns = 'date', inplace=True)

# 이전가격 변수에 저장해 두기
before_now = df.iloc[-1,1]
before_one = df.iloc[-2,1]
before_two = df.iloc[-3,1]
before_three = df.iloc[-4,1]
before_four = df.iloc[-5,1]
before_five = df.iloc[-6,1]
before_six = df.iloc[-7,1]
before_seven = df.iloc[-8,1]
before_eight = df.iloc[-9,1]
before_nine = df.iloc[-10,1]
before_ten = df.iloc[-11,1]

# 실제 값
original_open = df['unitPrice'].values
# 날짜 값
dates = pd.to_datetime(df['now_datetime'])

# 사용할 컬럼만 가져오기
cols = list(df)[1:]

# 데이터타입 float로 변경
df = df[cols].astype(float)

# standardscaler스케일링
scaler = StandardScaler()
scaler = scaler.fit(df)
df_scaler = scaler.transform(df)

# 학습용, 테스트 9대1로 나눔
n_train = int(0.9*df_scaler.shape[0]) # 90퍼 비율
train_data_scaled = df_scaler[:n_train] # train 데이터
train_dates = dates[:n_train] # train 날짜

test_data_scaled = df_scaler[n_train:] # test 데이터
test_dates = dates[n_train:] # test 날짜

# 직전 24개의 데이터를 기반으로 10분뒤 가격을 예측하는 것을 목표
# 데이터 구조를 lstm의 입력과 출력에 맞게 바꿔주자
pred_days = 1
seq_len = 24
input_dim = 4

X_train = []
Y_train = []
X_test = []
Y_test = []

for i in range(seq_len, n_train-pred_days +1):
    X_train.append(train_data_scaled[i - seq_len:i, 0:train_data_scaled.shape[1]])
    Y_train.append(train_data_scaled[i + pred_days - 1:i + pred_days, 0])

for i in range(seq_len, len(test_data_scaled)-pred_days +1):
    X_test.append(test_data_scaled[i - seq_len:i, 0:test_data_scaled.shape[1]])
    Y_test.append(test_data_scaled[i + pred_days - 1:i + pred_days, 0])

X_train, Y_train = np.array(X_train), np.array(Y_train)
X_test, Y_test = np.array(X_test), np.array(Y_test)

# lstm모델
model = Sequential()
model.add(LSTM(64, input_shape=(X_train.shape[1], X_train.shape[2]), # (seq length, input dimension)
               return_sequences=True))
model.add(LSTM(32, return_sequences=False))
model.add(Dense(Y_train.shape[1]))

# 모델 피팅
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.losses import Huber
from tensorflow.keras.callbacks import EarlyStopping

# specify your learning rate
learning_rate = 0.01
# create an Adam optimizer with the specified learning rate
optimizer = Adam(learning_rate=learning_rate)
# compile your model using the custom optimizer
model.compile(optimizer=optimizer, loss=Huber(), metrics=['mse'])
earlystopping = EarlyStopping(monitor='val_loss', patience=5)

# 모델 피팅
history = model.fit(X_train, Y_train, epochs=100, batch_size=32,
                    validation_split=0.1, verbose=1, callbacks = [earlystopping])


# 마지막 데이터에 대한 예측을 위한 입력 데이터 준비
last_input = df_scaler[-seq_len:]
# 하나만 예측하므로 배치크기는 1
last_input = last_input.reshape(1, seq_len, input_dim)
# 10분 뒤의 unitPrice 예측
predicted_unitPrice = model.predict(last_input)
# 스케일링을 원래 데이터 범위로 되돌리기
predicted_unitPrice = scaler.inverse_transform(np.array([[predicted_unitPrice[0][0], 0, 0, 0]]))[0][0]

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

# item_img, item_name, price 컬럼 값 설정
item_name = item_name  # 변수 값
item_img = "https://img-api.neople.co.kr/df/items/84ce25912570c6b244e90259a58091bf"
price = predicted_unitPrice

# 쿼리 생성
update_query = f"""
    UPDATE donpa_item1
    SET price = {price}, item_img = '{item_img}', before_now = {before_now}, before_one = {before_one}, before_two = {before_two}, before_three = {before_three}, before_four = {before_four}, before_five = {before_five}, before_six = {before_six}, before_seven = {before_seven}, before_eight = {before_eight}, before_nine = {before_nine}, before_ten = {before_ten}
    WHERE item_name = '{item_name}'
"""

insert_query = f"""
    INSERT INTO donpa_item1 (item_name, item_img, before_now, before_one, before_two, before_three, before_four, before_five, before_six, before_seven, before_eight, before_nine, before_ten, price)
    VALUES ('{item_name}', '{item_img}', {before_now}, {before_one}, {before_two}, {before_three}, {before_four}, {before_five}, {before_six}, {before_seven}, {before_eight}, {before_nine}, {before_ten}, {price})
"""

# 데이터베이스 작업 수행
try:
    with connection.cursor() as cursor:
        cursor.execute(update_query)  # item_name 값이 있는 경우 업데이트 시도
        if cursor.rowcount == 0:
            cursor.execute(insert_query)  # item_name 값이 없는 경우 새로운 행 추가
    connection.commit()  # 변경 내용을 커밋
except Exception as e:
    connection.rollback()  # 에러가 발생한 경우 롤백

# 연결 종료
connection.close()
