import requests
from bs4 import BeautifulSoup
import re
import pymysql

# MySQL 연결 설정
conn = pymysql.connect(
    host='10.233.18.183',  # 호스트명
    user='root',    # 데이터베이스 사용자명
    password='1234',  # 데이터베이스 암호
    db='donpa_item',      # 데이터베이스 이름
    port = 3306
)

# 커서 생성
cursor = conn.cursor()

eve_img = []
eve_text = []
eve_date = []
eve_herf = []

# 검색 결과 페이지 URL
url = "https://df.nexon.com/community/news/event/list"

# HTTP GET 요청
response = requests.get(url)

# 응답 데이터 파싱
soup = BeautifulSoup(response.text, "html.parser")

# 이벤트 img 셀렉터
selector_img = "#wrap > section.content.news > article.board_eventlist > ul > li > img"
# 이벤트 b 셀렉터
selector_text = "#wrap > section.content.news > article.board_eventlist > ul > li > b"
# 이벤트 날짜 span 셀렉터
selector_date = "#wrap > section.content.news > article.board_eventlist > ul > li > span"
# 이벤트 링크가 포함된 li 태그들 선택
selector_href = "#wrap > section.content.news > article.board_eventlist > ul > li"

# 선택자에 해당하는 요소들을 모두 찾음
event_img = soup.select(selector_img)
# URL에 프로토콜을 추가하여 출력
for img in event_img:
    src = img.get('src')
    if src.startswith('//'):
        src = 'https:' + src
    eve_img.append(src)
    
 # 선택자에 해당하는 요소들을 모두 찾음
event_text = soup.select(selector_text)
# 각 링크의 텍스트만 추출하여 리스트에 저장
event_text = [link.get_text(strip=True) for link in event_text]
# 결과 출력
for text in event_text:
    eve_text.append(text)



# 선택자에 해당하는 요소들을 모두 찾음
event_dates = soup.select(selector_date)
# 결과 출력
for span in event_dates:
    date_text = span.text.strip().replace('\n', '').strip().replace(' ','')  # span 태그 안의 텍스트>에서 공백 및 줄바꿈 제거
    eve_date.append(date_text)



event_href = soup.select(selector_href)

# 결과 출력
for li in event_href:
    if li.get("data-no"):
        event_url = f"http://df.nexon.com/community/news/event/{li.get('data-no')}?categoryType=0"
        eve_herf.append(event_url)

    else:
        li = li.get("onclick")

        if 'window.location.href' in li:
            # 정규 표현식을 사용하여 값을 추출합니다.
            li = re.findall(r"'(.*?)';", li)

            eve_herf.append("https://df.nexon.com"+''.join(li))
        elif 'neople.openCouponPop()' in li:
            li = "https://df.nexon.com/community/news/event/list"
            eve_herf.append(li)

        elif 'window.open' in li:
            # 정규 표현식을 사용하여 URL 추출
            li = re.search(r"https://[a-zA-Z0-9./-]+", li).group()
            eve_herf.append(li)
 
 # 테이블 초기화 (기존 데이터 삭제)
truncate_sql = "TRUNCATE TABLE donpa_event"
cursor.execute(truncate_sql)


# 데이터베이스에 데이터 삽입
for i in range(len(eve_img)):
    img = eve_img[i]
    text = eve_text[i]
    date = eve_date[i]
    herf = eve_herf[i]

    sql = "INSERT INTO donpa_event (img, text, date, herf) VALUES (%s, %s, %s, %s)"
    cursor.execute(sql, (img, text, date, herf))

# 변경사항 커밋
conn.commit()

# 연결 종료
conn.close()
