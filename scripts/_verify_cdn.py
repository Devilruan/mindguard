# -*- coding: utf-8 -*-
import sys; sys.stdout.reconfigure(encoding='utf-8')
import requests

for path in ['/my-records', '/resources']:
    html = requests.get('http://localhost:8000' + path, timeout=5).text
    print(path + ' 含app容器=' + str('id="app"' in html) + ' 含CDN=' + str('jsdelivr' in html))

# 字体资源
r = requests.get('http://localhost:8000/static/css/vendor/fonts/bootstrap-icons.woff2', timeout=5)
print('字体: ' + str(r.status_code) + ' (' + str(len(r.content)) + 'B)')