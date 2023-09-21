import requests
from bs4 import BeautifulSoup
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

# 크롤링 코드 작성
photo_list = []
title_list = []
link_list = []

# 검색 결과 페이지 URL
url = "https://search.naver.com/search.naver?where=news&query=%EB%8D%98%ED%8C%8C&sm=tab_opt&sort=1&photo=1&field=0&pd=0&ds=&de=&docid=&related=0&mynews=0&office_type=0&office_section_code=0&news_office_checked=&nso=so%3Add%2Cp%3Aall&is_sug_officeid=0&office_category=0&service_area=0"

# HTTP GET 요청
response = requests.get(url)

# 응답 데이터 파싱
soup = BeautifulSoup(response.text, "html.parser")

select_num = 1
while select_num<=10:
    # 이미지 선택자
    selector = f"#sp_nws{select_num} > div > a > img"
    # 선택자에 해당하는 이미지 요소를 찾음
    image = soup.select_one(selector)
    # 각 링크의 href 속성값을 출력
    photo = image.get("data-lazysrc")
    photo_list.append(photo)
    select_num+=1

# 뉴스 타이틀, 링크 선택자
selector = "#main_pack > section.sc_new.sp_nnews._prs_nws > div > div.group_news > ul > li> div > div > a"
# 선택자에 해당하는 요소들을 모두 찾음
title_link = soup.select(selector)

# 각 타이틀,링크 속성값을 출력
for link in title_link:
    title = link.get("title")
    href = link.get("href")
    title_list.append(title)
    link_list.append(href)
    
# 테이블 초기화 (기존 데이터 삭제)
truncate_sql = "TRUNCATE TABLE donpa_news"
cursor.execute(truncate_sql)


# 데이터베이스에 데이터 삽입
for i in range(len(photo_list)):
    photo = photo_list[i]
    title = title_list[i]
    link = link_list[i]

    sql = "INSERT INTO donpa_news (photo, title, link) VALUES (%s, %s, %s)"
    cursor.execute(sql, (photo, title, link))

# 변경사항 커밋
conn.commit()

# 연결 종료
conn.close()
