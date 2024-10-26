import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os

# GitHub 저장소에 업로드된 폰트 파일 경로 설정
font_path = os.path.join(os.path.dirname(__file__), 'NanumGothic.ttf')
# font_path = "C:/Windows/Fonts/NanumGothic.ttf"
fontprop = fm.FontProperties(fname=font_path, size=10)

# 특정 기간과 지역에 대한 API 호출 함수 정의 (데이터 캐싱 추가)
@st.cache_data
def fetch_population_data():
    regions = [
        "41250", "41630", "41650", "41800", "41820", "41150", "41280", "41310", "41360", "41480"
    ]
    start_date = '200801'
    end_date = '202408'
    monthly_list = pd.date_range(start="2008-01", end="2024-08", freq='M').strftime('%Y%m').tolist()
    filtered_monthly_list = [month for month in monthly_list if month.endswith('01') and (int(month[:4]) - 2008) % 5 == 0]

    all_data = []

    for region in regions:
        for month in filtered_monthly_list:
            month1 = str(int(month) + 411)
            url_page = (f"https://kosis.kr/openapi/Param/statisticsParameterData.do?"
                        f"method=getList&"
                        f"apiKey=ODZlMTM0NGEyYWFlNmRmNzhmMmJhZDRkN2I2OWRmOGE=&"
                        f"itmId=T2+T3+T4+&"
                        f"objL1={region}+&"
                        f"objL2=ALL&objL3=&objL4=&objL5=&objL6=&objL7=&objL8=&"
                        f"format=json&"
                        f"jsonVD=Y&"
                        f"prdSe=M&"
                        f"startPrdDe={month}&"
                        f"endPrdDe={month1}&"
                        f"orgId=101&"
                        f"tblId=DT_1B04006")

            response = requests.get(url_page)
            json_data = response.json()

            if 'err' not in json_data:
                data = pd.DataFrame({
                    '연도': [datetime.strptime(f"{x['PRD_DE']}01", '%Y%m%d').strftime('%Y%m') for x in json_data],
                    '시군구': [x['C1_NM'] for x in json_data],
                    '연령별': [x['C2_NM'] for x in json_data],
                    '성별': [x['ITM_NM'] for x in json_data],
                    '인구수': [float(x['DT']) for x in json_data]
                })
                all_data.append(data)

    df_final = pd.concat(all_data, ignore_index=True)
    return df_final

# 데이터 가져오기
df_final = fetch_population_data()

# 데이터 필터링
df_filtered = df_final[df_final['연령별'] != '계']

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
ax2.set_xticklabels(tick_positions, rotation=45, fontsize=8, fontproperties=fontprop)

# Streamlit을 통한 두 번째 그래프 출력
st.pyplot(fig2)
