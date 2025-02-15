import streamlit as st
import pandas as pd
import pymysql
import requests
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
import matplotlib.dates as mdates
import time

# GitHub 저장소에 업로드된 폰트 파일 경로 설정
font_path = os.path.join(os.path.dirname(__file__), 'NanumGothic.ttf')
# font_path = "C:/Windows/Fonts/NanumGothic.ttf"
fontprop = fm.FontProperties(fname=font_path, size=10)

# 데이터베이스 연결 정보
db_host = '59.9.20.28'
db_user = 'user1'
db_password = 'user1!!'
db_database = 'cuif'
charset = 'utf8'

# 조회할 도시 목록
cities = ['동두천시', '양주시', '포천시', '연천군', '가평군', '의정부시', '고양시', '구리시', '남양주시', '파주시']
tablens = 'population'

@st.cache_data
def fetch_all_data():
    conn = pymysql.connect(host=db_host, user=db_user, password=db_password, database=db_database, charset=charset)
    all_data = []
    for city in cities:
        query = f"SELECT * FROM {tablens} WHERE 시군구='{city}'"
        df = pd.read_sql(query, conn)
        all_data.append(df)

    # 모든 데이터프레임을 하나로 합치기
    final_df = pd.concat(all_data, ignore_index=True)
    return final_df

df_final = fetch_all_data()

# 데이터 필터링
df_filtered = df_final[(df_final['연령별'] != '계') & (df_final['성별'] != '총인구수')]

# 연령 그룹화 함수 정의
def group_age(row):
    if row == '100세 이상':
        return '75-99'
    else:
        age = int(row.replace('세', ''))
        if age < 15:
            return '00-14'
        elif 15 <= age <= 24:
            return '15-24'
        elif 25 <= age <= 34:
            return '25-34'
        elif 35 <= age <= 44:
            return '35-44'
        elif 45 <= age <= 54:
            return '45-54'
        elif 55 <= age <= 64:
            return '55-64'
        elif 65 <= age <= 74:
            return '65-74'
        else:
            return '75-99'

# 연령 그룹화 적용
df_filtered['연령그룹'] = df_filtered['연령별'].apply(group_age)

# Streamlit 페이지 설정
st.title("지역별 인구수 시각화")
st.write("KOSIS 데이터를 활용하여 특정 지역의 인구 변화를 시각화합니다.")

# 지역별 목록 추출 및 선택
regions = df_filtered['시군구'].unique()
selected_region = st.selectbox("시각화할 지역을 선택하세요:", regions)

# 첫 번째 그래프: 연령 그룹별 인구 변화
fig1, ax1 = plt.subplots(figsize=(10, 6))

# 지역별 데이터 필터링 및 그룹화
df_region = df_filtered[df_filtered['시군구'] == selected_region]
df_grouped = df_region.groupby(['연도', '연령그룹'])['인구수'].sum().reset_index()

# 연령 그룹별로 선 그리기
age_groups = df_grouped['연령그룹'].unique()
line_styles = ['-', '--', '-.', ':']
for j, age_group in enumerate(age_groups):
    age_group_data = df_grouped[df_grouped['연령그룹'] == age_group]
    line_style = line_styles[j % len(line_styles)]
    ax1.plot(age_group_data['연도'], age_group_data['인구수'], label=age_group, linestyle=line_style, linewidth=2 + (j % 3))

# 그래프 제목 및 축 레이블 설정
ax1.set_title(f'{selected_region} - 연령 그룹별 인구 변화', fontproperties=fontprop, fontsize=16)
ax1.set_xlabel('YearMonth', fontproperties=fontprop, fontsize=12)
ax1.set_ylabel('Population', fontproperties=fontprop, fontsize=12)
ax1.legend(loc='upper left', bbox_to_anchor=(1, 1))

# X축 레이블 설정 (3년 간격)
tick_positions = df_grouped['연도'].unique()[::36]
ax1.set_xticks(tick_positions)
ax1.set_xticklabels(tick_positions, rotation=0, fontproperties=fontprop)

# Streamlit을 통한 첫 번째 그래프 출력
st.header(f"{selected_region}의 연령대별 인구 변화 추이")
st.pyplot(fig1)

# 두 번째 그래프: 전체 인구 변화 (월별 전체 합계)
fig2, ax2 = plt.subplots(figsize=(10, 6))

# 연도별 인구수 합계 계산
df_total_population = df_region.groupby('연도')['인구수'].sum().reset_index()

# 전체 인구 변화를 선 그래프로 표시
ax2.plot(df_total_population['연도'], df_total_population['인구수'], marker='o', linestyle='-', markersize=3, linewidth=1.5)
ax2.set_title(f"{selected_region}의 인구 변화", fontproperties=fontprop, fontsize=16)
ax2.set_xlabel('YearMonth', fontproperties=fontprop, fontsize=12)
ax2.set_ylabel('Population', fontproperties=fontprop, fontsize=12)

# X축 레이블 간격 설정 (3년 간격)
tick_positions = df_total_population['연도'].unique()[::36]
ax2.set_xticks(tick_positions)
ax2.set_xticklabels(tick_positions, rotation=0, fontsize=8, fontproperties=fontprop)

# Streamlit을 통한 두 번째 그래프 출력
st.header(f"{selected_region}의 인구 변화 추이")
st.pyplot(fig2)
