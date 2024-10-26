import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import streamlit as st
import matplotlib.font_manager as fm

# GitHub 저장소에 업로드된 폰트 파일 경로 설정
font_path = os.path.join(os.path.dirname(__file__), 'NanumGothic.ttf')
# font_path = "C:/Windows/Fonts/NanumGothic.ttf"
fontprop = fm.FontProperties(fname=font_path, size=10)

# Streamlit 앱 제목
st.title("경기북부 관광객 데이터 분석")

# y축 숫자 포맷팅 함수
def y_fmt(x, _):
    return f'{int(x):,}'  # 천 단위로 쉼표 추가

@st.cache_data
def load_and_preprocess_data():
    # 관광객수 데이터 불러오기 및 전처리
    tourist_df = pd.read_excel('경기북부_관광객.xlsx')

    # 'signguNm' 열에서 '고양시'가 포함된 모든 값을 '고양시'로 변경
    tourist_df.loc[tourist_df['signguNm'].str.contains('고양시'), 'signguNm'] = '고양시'

    # 'baseYmd'를 datetime 형식으로 변환 및 월 단위로 변환
    tourist_df['baseYmd'] = pd.to_datetime(tourist_df['baseYmd'], format='%Y%m%d')
    tourist_df['month'] = tourist_df['baseYmd'].dt.to_period('M')

    # 2024년 9월 데이터 제외
    tourist_df = tourist_df[tourist_df['baseYmd'] < '2024-09-01']

    # 데이터 그룹화: 각 지역별 데이터 미리 그룹화
    grouped_total = tourist_df.groupby(['signguNm', 'month']).agg({'touNum': 'sum'}).reset_index()
    grouped_individual = tourist_df.groupby(['signguNm', 'month', 'touDivNm']).agg({'touNum': 'sum'}).reset_index()
    grouped_foreigner = tourist_df[tourist_df['touDivNm'] == '외국인(c)'].groupby(['signguNm', 'month']).agg({'touNum': 'sum'}).reset_index()

    return grouped_total, grouped_individual, grouped_foreigner

# 데이터 로드 및 전처리
grouped_total, grouped_individual, grouped_foreigner = load_and_preprocess_data()

# 시군구 선택 옵션
regions = grouped_total['signguNm'].unique()
selected_region = st.selectbox("시각화할 시군구를 선택하세요:", regions)

# 특정 지역의 월 단위 방문자 총합 추이
@st.cache_resource
def plot_total_trend_for_selected_region(region_data, region_name):
    fig, ax = plt.subplots(figsize=(10, 6))
    months = region_data['month'].astype(str)
    tou_nums = region_data['touNum']
    ax.plot(months, tou_nums, marker='o', label=f'{region_name} 전체 합계', color='blue')
    ax.set_title(f'{region_name}(2019.10 ~ 2024.08) 월별 방문자 총합 추이', fontproperties=fontprop)
    ax.set_xlabel('년월', fontproperties=fontprop)
    ax.set_ylabel('방문자 수', fontproperties=fontprop)
    ax.yaxis.set_major_formatter(FuncFormatter(y_fmt))
    ax.set_xticks(range(0, len(months), 3))
    ax.set_xticklabels(months[::3], rotation=45, fontproperties=fontprop)
    ax.legend(prop=fontprop)
    ax.grid(True)
    st.pyplot(fig)

# 특정 지역의 월 단위 방문자 유형별 추이
@st.cache_resource
def plot_individual_trend_for_selected_region(region_data, region_name):
    fig, ax = plt.subplots(figsize=(10, 6))
    for tou_type in ['현지인(a)', '외지인(b)', '외국인(c)']:
        type_data = region_data[region_data['touDivNm'] == tou_type]
        months = type_data['month'].astype(str)
        tou_nums = type_data['touNum']
        ax.plot(months, tou_nums, marker='o', label=f'{tou_type}')
    ax.set_title(f'{region_name}(2019.10 ~ 2024.08) 월별 방문자 유형별 추이', fontproperties=fontprop)
    ax.set_xlabel('년월', fontproperties=fontprop)
    ax.set_ylabel('방문자 수', fontproperties=fontprop)
    ax.yaxis.set_major_formatter(FuncFormatter(y_fmt))
    ax.set_xticks(range(0, len(months), 3))
    ax.set_xticklabels(months[::3], rotation=45, fontproperties=fontprop)
    ax.legend(prop=fontprop)
    ax.grid(True)
    st.pyplot(fig)

# 특정 지역의 외국인 방문자 추이
@st.cache_resource
def plot_foreigner_trend_for_selected_region(region_data, region_name):
    fig, ax = plt.subplots(figsize=(10, 6))
    months = region_data['month'].astype(str)
    tou_nums = region_data['touNum']
    ax.plot(months, tou_nums, marker='o', label=f'{region_name} 외국인 방문자 수', color='green')
    ax.set_title(f'{region_name}(2019.10 ~ 2024.08) 외국인 방문자 추이', fontproperties=fontprop)
    ax.set_xlabel('년월', fontproperties=fontprop)
    ax.set_ylabel('외국인 방문자 수', fontproperties=fontprop)
    ax.yaxis.set_major_formatter(FuncFormatter(y_fmt))
    ax.set_xticks(range(0, len(months), 3))
    ax.set_xticklabels(months[::3], rotation=45, fontproperties=fontprop)
    ax.legend(prop=fontprop)
    ax.grid(True)
    st.pyplot(fig)

# 선택된 지역의 데이터 필터링
selected_region_total = grouped_total[grouped_total['signguNm'] == selected_region]
selected_region_individual = grouped_individual[grouped_individual['signguNm'] == selected_region]
selected_region_foreigner = grouped_foreigner[grouped_foreigner['signguNm'] == selected_region]

# 그래프 출력
st.header(f"{selected_region}의 월 단위 방문자 총합 추이")
plot_total_trend_for_selected_region(selected_region_total, selected_region)

st.header(f"{selected_region}의 월 단위 방문자 유형별 추이")
plot_individual_trend_for_selected_region(selected_region_individual, selected_region)

st.header(f"{selected_region}의 외국인 방문자 추이")
plot_foreigner_trend_for_selected_region(selected_region_foreigner, selected_region)
