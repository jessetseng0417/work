# 1. 安裝字體 (以思源黑體為例)
!apt-get -qy install fonts-nanum

# 2. 重新整理 Matplotlib 的字體快取 (這步很重要)
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 手動清除快取，確保系統抓到新字體
!rm -rf ~/.cache/matplotlib

# 3. 設定字體路徑
# 安裝後的 fonts-nanum 預設路徑在 /usr/share/fonts/truetype/nanum/
# 我們選擇其中的 NanumBarunGothic 作為顯示字體
path = '/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf'
fontprop = fm.FontProperties(fname=path)

# 4. 全域設定：讓 Matplotlib 預設使用該字體
plt.rc('font', family='NanumBarunGothic')
mpl.rcParams['axes.unicode_minus'] = False # 修正負號顯示問題

print("字體安裝完成，請執行下方的 ROI 計算程式碼。")

import ipywidgets as widgets
from IPython.display import display, HTML, clear_output
import matplotlib.pyplot as plt

# 1. 產業基準數據 (已換算為 TWD, 匯率基準 1:32)
industry_data = {
    "石油煉化 (Refinery)": 64000,
    "沖壓廠 (Stamping)": 56000,
    "核能電廠 (Nuclear)": 32512,
    "一般工業平均 (Average)": 26880
}

# 2. 建立互動元件
style = {'description_width': 'initial'}
industry_select = widgets.Dropdown(options=industry_data.keys(), value='石油煉化 (Refinery)', description='選擇產業別:', style=style)
sample_slider = widgets.IntSlider(value=100, min=10, max=500, step=10, description='每月樣品數:', style=style)

lab_fee_input = widgets.IntText(value=1600, description='委外分析單價(TWD):', style=style)
price_input = widgets.IntText(value=4800000, description='儀器售價(TWD):', style=style)
op_cost_input = widgets.IntText(value=640000, description='年度維護費(TWD):', style=style)

# 自定義按鈕樣式 (使用 #026E9A)
btn = widgets.Button(
    description="計算 ROI 並生成簡報圖表", 
    layout=widgets.Layout(width='350px', height='50px'),
)
btn.style.button_color = '#026E9A'
btn.style.font_weight = 'bold'

output = widgets.Output()

# 3. 計算與繪圖邏輯
def calculate_roi(b):
    with output:
        clear_output()
        # 獲取數值
        risk_per_sample = industry_data[industry_select.value]
        monthly_qty = sample_slider.value
        lab_fee = lab_fee_input.value
        capex = price_input.value
        opex = op_cost_input.value
        
        # 計算
        annual_qty = monthly_qty * 12
        annual_benefit = (risk_per_sample + lab_fee) * annual_qty
        first_year_profit = annual_benefit - (capex + opex)
        
        denominator = (annual_benefit - opex)
        payback_months = (capex / denominator) * 12 if denominator > 0 else float('inf')
        
        # 顯示結果文字 (使用指定色票)
        display(HTML(f"""
            <div style="background-color: #FFFFFF; padding: 25px; border-radius: 12px; border: 2px solid #026E9A; border-left: 15px solid #78BC42; color: #333333; font-family: 'PingFang TC', sans-serif;">
                <h2 style="color: #026E9A; margin-top: 0;">📊 專案分析報告：{industry_select.value}</h2>
                <p style="font-size: 18px; border-bottom: 1px solid #EEEEEE; padding-bottom: 10px;">
                    年度總收益 (避險+節省): <b style="color: #026E9A;">NT$ {annual_benefit:,.0f}</b>
                </p>
                <p style="font-size: 18px;">
                    第一年預估淨損益: <b style="color: {'#78BC42' if first_year_profit >= 0 else '#E74C3C'};">NT$ {first_year_profit:,.0f}</b>
                </p>
                <div style="background-color: #f9f9f9; padding: 15px; border-radius: 8px; margin-top: 15px;">
                    <p style="font-size: 28px; margin: 0; color: #333333;">
                        預估回收期: <b style="color: #5B2E85;">{payback_months:.1f} 個月</b>
                    </p>
                </div>
                <p style="font-size: 12px; color: #777777; margin-top: 15px;">註：以上數據基於 Spectro Scientific Bootcamp 實績統計。</p>
            </div>
        """))
        
        # 繪製累積成本圖 (視覺色票同步)
        years = [0, 1, 2, 3, 4, 5]
        outsource_total = [y * (annual_qty * lab_fee) for y in years]
        spectro_total = [capex + (y * opex) for y in years]
        
        plt.figure(figsize=(11, 5), facecolor='#FFFFFF')
        plt.plot(years, outsource_total, label='持續委外分析累積成本', marker='o', color='#333333', linestyle='--', alpha=0.6)
        plt.plot(years, spectro_total, label='導入 Spectro 現場化累積成本', marker='s', color='#026E9A', linewidth=4)
        
        # 著色獲利區間 (使用 #78BC42)
        plt.fill_between(years, outsource_total, spectro_total, 
                         where=([s < o for s, o in zip(spectro_total, outsource_total)]), 
                         color='#78BC42', alpha=0.2, label='預期獲利區間')
        
        plt.title('總持有成本分析 (TCO Projection)', fontsize=16, color='#026E9A', fontweight='bold')
        plt.xlabel('年份 (Years)', color='#333333')
        plt.ylabel('累積支出 (TWD)', color='#333333')
        plt.legend(loc='upper left', frameon=True)
        plt.grid(True, linestyle=':', alpha=0.5)
        plt.ticklabel_format(style='plain', axis='y')
        plt.show()

btn.on_click(calculate_roi)

# 4. 顯示初始介面
display(HTML("<h1 style='color: #026E9A; border-bottom: 3px solid #78BC42; padding-bottom: 10px;'>Spectro Scientific ROI 分析儀</h1>"))
display(widgets.VBox([industry_select, sample_slider, lab_fee_input, price_input, op_cost_input, btn]))
display(output)
