from bs4 import BeautifulSoup
import requests
import pymysql

# MySQL 연결 설정
conn = pymysql.connect(
    host='10.233.18.183',  # 호스트명
    user='root',    # 데이터베이스 사용자명
    password='1234',  # 데이터베이스 암호
    db='donpa_item',      # 데이터베이스 이름
    port=3306
)

# 커서 생성
cursor = conn.cursor()

date_list = []
sell_list = []
buy_list = []

# 검색 결과 페이지 URL
url = "http://dnfnow.xyz/invest"

headers = {
     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
}

response = requests.get(url, headers=headers)

# 응답 데이터 파싱
soup = BeautifulSoup(response.text, "html.parser")

# 뉴스 타이틀, 링크 선택자
selector = "#week > script:nth-child(3)"
# 선택자에 해당하는 요소들을 모두 찾음
script_element = soup.select_one(selector)

# 원하는 JavaScript 코드 부분 추출
javascript_code = script_element.text
javascript_code = javascript_code.split('data')

date = javascript_code[1].split(' labels: [ ')[1].split(', ],\n ')[0].split(',')
# 공백 및 작은 따옴표 제거 후 출력
for i in date:
    cleaned_date = i.strip().strip("'")
    date_list.append(cleaned_date)

sell = javascript_code[3].split(': [ ')[1].split(', ]')[0].split(',')
# 공백 및 작은 따옴표 제거 후 출력
for i in sell:
    cleaned_sell = i.strip().strip("'")
    sell_list.append(float(cleaned_sell))

buy = javascript_code[4].split(': [ ')[1].split(', ]')[0].split(',')
# 공백 및 작은 따옴표 제거 후 출력
for i in buy:
    cleaned_buy = i.strip().strip("'")
    buy_list.append(float(cleaned_buy))

# 데이터베이스에 데이터 삽입 또는 업데이트
for i in range(len(date_list)):
    date = date_list[i]
    sell = sell_list[i]
    buy = buy_list[i]

    # 날짜가 이미 존재하는지 확인
    cursor.execute("SELECT COUNT(*) FROM goldprice WHERE date = %s", (date,))
    result = cursor.fetchone()

    if result[0] == 0:
        # 날짜가 존재하지 않으면 데이터 삽입
        sql = "INSERT INTO goldprice (date, sell, buy) VALUES (%s, %s, %s)"
        cursor.execute(sql, (date, sell, buy))
    else:
        # 날짜가 존재하면 데이터 업데이트 (오버라이팅)
        sql = "UPDATE goldprice SET sell = %s, buy = %s WHERE date = %s"
        cursor.execute(sql, (sell, buy, date))

# 변경사항 커밋
conn.commit()

# 연결 종료
conn.close()
