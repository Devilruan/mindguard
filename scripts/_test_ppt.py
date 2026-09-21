import sys, time
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE

print('imports ok')

prs = Presentation()
prs.slide_width = Inches(13.33)
prs.slide_height = Inches(7.5)

C_NAVY = RGBColor(0x1A,0x3A,0x5C)
C_TEAL = RGBColor(0x1C,0x7A,0x6E)

# 简化：只做封面 + 一张简单图 + 结束页，测试能不能保存
s = prs.slides.add_slide(prs.slide_layouts[6])

# 深蓝矩形
shp = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(5.5), Inches(7.5))
shp.fill.solid(); shp.fill.fore_color.rgb = C_NAVY; shp.line.fill.background()
print('1 rect ok')

# 文本框
tb = s.shapes.add_textbox(Inches(0.7), Inches(2.6), Inches(4.8), Inches(1.2))
tf = tb.text_frame; tf.word_wrap = True
tf.paragraphs[0].add_run().text = '测试标题'
print('2 textbox ok')

# 图表
chart_data = CategoryChartData()
chart_data.categories = ['A', 'B']
chart_data.add_series('S1', (10, 20))
chart_data.add_series('S2', (15, 18))
chart = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED,
    Inches(7), Inches(4), Inches(5.5), Inches(3), chart_data).chart
chart.has_title = True
chart.chart_title.text_frame.text = '对比图'
print('3 chart ok')

out = r'h:\2026AIC·算法创新赛\源码_restored\docs\_test.pptx'
prs.save(out)
print(f'✅ saved: {out}')
