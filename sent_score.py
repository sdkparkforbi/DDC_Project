import streamlit as st
import pandas as pd
import pymysql
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.font_manager as fm
from datetime import datetime
import os

# GitHub 저장소에 업로드된 폰트 파일 경로 설정
# font_path = os.path.join(os.path.dirname(__file__), 'NanumGothic.ttf')
font_path = "C:/Windows/Fonts/NanumGothic.ttf"
fontprop = fm.FontProperties(fname=font_path, size=10)

# .env 파일 로드
load_dotenv('db_password')

# 데이터베이스 연결 정보
db_host = '59.9.20.28'
db_user = 'user1'
db_password = os.getenv("DB_PASSWORD")
db_database = 'cuif'
charset = 'utf8'

# 조회할 도시 목록
cities = ['동두천', '양주', '포천', '연천', '가평', '의정부', '고양', '구리', '남양주', '파주']
tablens = 'sentindex'

# 각 도시의 스타일 설정
styles = {
    '동두천': {'color': 'blue', 'marker': 'o', 'linestyle': '--'},
    '양주': {'color': 'green', 'marker': 'v', 'linestyle': '--'},
    '포천': {'color': 'red', 'marker': 's', 'linestyle': '--'},
    '연천': {'color': 'purple', 'marker': 'D', 'linestyle': '--'},
    '가평': {'color': 'orange', 'marker': 'x', 'linestyle': '--'},
    '의정부': {'color': 'brown', 'marker': '^', 'linestyle': '--'},
    '고양': {'color': 'darkblue', 'marker': '*', 'linestyle': '--'},
    '구리': {'color': 'gray', 'marker': 'P', 'linestyle': '--'},
    '남양주': {'color': 'cyan', 'marker': 'H', 'linestyle': '--'},
    '파주': {'color': 'magenta', 'marker': 'X', 'linestyle': '--'}
}

# 데이터베이스에서 모든 도시의 데이터를 가져오는 함수 (캐시 사용)
@st.cache_data
def fetch_all_data():
    conn = pymysql.connect(host=db_host, user=db_user, password=db_password, database=db_database, charset=charset)
    all_data = {}
    for city in cities:
        query = f"SELECT * FROM {tablens} WHERE cname='{city}'"
        data = pd.read_sql(query, conn)
        data['date'] = pd.to_datetime(data['date'], format='%Y%m')
        all_data[city] = data
    conn.close()
    return all_data

# Streamlit 페이지 설정
st.title("다수 도시의 월별 감성 지수")
st.write("MySQL 데이터베이스에서 추출된 도시별 월별 감성 지수 및 이동 평균을 보여줍니다.")

# 전체 지자체의 이동평균 비교를 위한 그래프 생성
st.write("## 전체 지자체의 이동평균 비교")

# 모든 도시의 데이터를 가져오기
all_data = fetch_all_data()

# 전체 도시 이동평균을 비교하는 큰 그래프 생성
fig, ax = plt.subplots(figsize=(14, 8))

for city, data in all_data.items():
    # 각 도시의 이동평균을 그래프에 추가 (색상, 선 스타일, 마커 적용)
    ax.plot(data['date'], data['sentindex_ma'],
            label=city,
            color=styles[city]['color'],
            marker=styles[city]['marker'],
            linestyle=styles[city]['linestyle'])

# X축을 12개월 단위로 설정
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=12))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

# X축 레이블을 회전시켜 보기 좋게 설정
ax.tick_params(axis='x', rotation=45)

# 그래프 제목 및 축 레이블 설정
ax.set_xlabel('월', fontproperties=fontprop)
ax.set_ylabel('감성 지수 이동평균', fontproperties=fontprop)
ax.set_title('전체 지자체 감성 지수 이동평균 비교', fontproperties=fontprop, fontsize=20, fontweight='bold')

# 범례에 폰트 적용
ax.legend(prop=fontprop)

# 그래프를 Streamlit에 표시
st.pyplot(fig)

# 도시 선택 옵션 추가
st.write("## 개별 지자체 감성 지수")
selected_city = st.selectbox("도시를 선택하세요:", cities)

# 선택한 도시의 개별 그래프 표시
city_data = all_data[selected_city]

# 개별 도시의 감성 지수 및 이동평균 그래프 생성
fig, ax = plt.subplots(figsize=(10, 6))

# 원래 감성 지수 시각화
ax.plot(city_data['date'], city_data['sentindex'],
        marker=styles[selected_city]['marker'],
        label='Sentiment Index',
        color=styles[selected_city]['color'])

# 이동 평균 시각화
ax.plot(city_data['date'], city_data['sentindex_ma'],
        linestyle=styles[selected_city]['linestyle'],
        color=styles[selected_city]['color'],
        label='12-Month Moving Avg')

# X축을 12개월 단위로 설정
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=12))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

# X축 레이블을 회전시켜 보기 좋게 설정
ax.tick_params(axis='x', rotation=45)

# 그래프 제목 및 축 레이블 설정
ax.set_xlabel('월', fontproperties=fontprop)
ax.set_ylabel('감성 지수', fontproperties=fontprop)
ax.set_title(f'{selected_city} 감성 지수', fontproperties=fontprop, fontsize=20, fontweight='bold')

# 범례 추가
ax.legend(prop=fontprop)

# Streamlit을 통한 개별 도시 그래프 출력
st.pyplot(fig)
