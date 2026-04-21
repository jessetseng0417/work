import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import plotly.graph_objects as go

# --- 1. 中文字體設定 ---
# 針對 Streamlit Cloud (Linux) 的字體路徑
font_path = '/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf'
try:
    # 載入字體
    fe = fm.FontEntry(fname=font_path, name='NanumBarunGothic')
    fm.fontManager.ttflist.insert(0, fe)
    plt.rcParams['font.family'] = fe.name
except:
    # 如果路徑不對，則嘗試全域尋找已安裝字體
    plt.rcParams['font.family'] = 'NanumBarunGothic'

plt.rcParams['axes.unicode_minus'] = False # 修正負號顯示問題

# --- 2. 核心色票設定 ---
C_DEEP_BLUE = "#026E9A"
C_GREEN = "#78BC42"
C_PURPLE = "#5B2E85"
C_DARK_GREY = "#333333"
C_WHITE = "#FFFFFF"

# --- 3. 產業基準數據 ---
industry_data = {
    "石油煉化 (Refinery)": 64000,
    "沖壓廠 (Stamping)": 56000,
    "核能電廠 (Nuclear)": 32512,
    "一般工業平均 (Average)": 26880
}

# --- 4. 介面與輸入 ---
st.set_page_config(page_title="Spectro ROI 分析儀", layout="wide")

# 套用自定義樣式
st.markdown(f"""
    <style>
    .main {{ background-color: {C_WHITE}; }}
    h1 {{ color: {C_DEEP_BLUE}; border-bottom: 3px solid {C_GREEN}; padding-bottom: 10px; }}
    .stMetric {{ background-color: #F8F9FA; padding: 15px; border-radius: 10px; border-left: 5px solid {C_GREEN}; }}
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Spectro Scientific ROI 分析儀")

with st.sidebar:
    st.header("專案參數輸入")
    selected_industry = st.selectbox("選擇產業別:", list(industry_data.keys()))
    monthly_samples = st.slider("每月樣品數:", 10, 500, 100)
    lab_fee = st.number_input("委外分析單價 (TWD):", value=1600)
    capex = st.number_input("儀器售價 (TWD):", value=4800000)
    opex = st.number_input("年度維護費 (TWD):", value=640000)

# --- 5. 計算邏輯 ---
risk_per_sample = industry_data[selected_industry]
annual_qty = monthly_samples * 12
annual_benefit = (risk_per_sample + lab_fee) * annual_qty
first_year_profit = annual_benefit - (capex + opex)

denominator = (annual_benefit - opex)
payback_months = (capex / denominator) * 12 if denominator > 0 else 0

# --- 6. 視覺化結果 ---
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("年度總收益 (避險+節省)", f"NT$ {annual_benefit:,.0f}")
with col2:
    color_style = "normal" if first_year_profit >= 0 else "inverse"
    st.metric("第一年預估淨損益", f"NT$ {first_year_profit:,.0f}", delta_color=color_style)
with col3:
    st.markdown(f"""
        <div style="text-align:center; padding:10px; background-color:{C_WHITE}; border:2px solid {C_PURPLE}; border-radius:10px;">
            <p style="color:{C_DARK_GREY}; margin:0;">預估回收期</p>
            <h2 style="color:{C_PURPLE}; margin:0;">{payback_months:.1f} 個月</h2>
        </div>
    """, unsafe_allow_html=True)

# --- 7. TCO 趨勢圖 (使用 Plotly 以獲得更好的 Web 互動感) ---
years = [0, 1, 2, 3, 4, 5]
outsource_total = [y * (annual_qty * lab_fee) for y in years]
spectro_total = [capex + (y * opex) for y in years]

fig = go.Figure()
fig.add_trace(go.Scatter(x=years, y=outsource_total, name='持續委外分析累積成本', 
                         line=dict(color=C_DARK_GREY, dash='dash')))
fig.add_trace(go.Scatter(x=years, y=spectro_total, name='導入 Spectro 現場化累積成本', 
                         line=dict(color=C_DEEP_BLUE, width=4)))

# 獲利區間填色
fig.add_trace(go.Scatter(
    x=years, y=outsource_total,
    fill=None, mode='lines', line_color='rgba(0,0,0,0)', showlegend=False
))
fig.add_trace(go.Scatter(
    x=years, y=spectro_total,
    fill='tonexty', mode='lines', line_color='rgba(0,0,0,0)',
    fillcolor='rgba(120, 188, 66, 0.2)', name='預期獲利區間'
))

fig.update_layout(
    title=f"<b>總持有成本分析 (TCO) - {selected_industry}</b>",
    title_font_color=C_DEEP_BLUE,
    xaxis_title="年份 (Years)",
    yaxis_title="累積支出 (TWD)",
    template="plotly_white",
    hovermode="x unified"
)

st.plotly_chart(fig, use_container_width=True)

st.caption("註：避險價值數據基於 Spectro Scientific Bootcamp 實績統計。匯率基準 1:32。")
