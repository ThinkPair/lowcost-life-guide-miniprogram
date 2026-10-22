from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]
mini=root/'miniprogram'
app=json.loads((mini/'app.json').read_text('utf-8'))
app['window'].update(navigationBarBackgroundColor='#FAF6EF',backgroundColor='#FAF6EF')
app['tabBar'].update(color='#7D6F60',selectedColor='#C2530C',backgroundColor='#FFFDF9')
(mini/'app.json').write_text(json.dumps(app,ensure_ascii=False,indent=2)+'\n','utf-8')
replacements={
 'pages/library/index.wxml':{'A SMALL GUIDE TO EVERYDAY LIFE':'按需要查找 · 共 34 章','把问题，逐个解开。':'找到适合你的办法','按需要翻阅，不必从头读到尾。':'按主题、章节和成本，选一条开始。'},
 'pages/saved/index.wxml':{'YOUR LITTLE BOOKSHELF':'我的生活书签','有用的，留在这里。':'有用的建议，随手可查','<view>READ</view><view>KEEP</view><view>LIVE</view>':'<view>留给</view><view>自己</view>'},
 'content/search/index.wxml':{'FIND YOUR NEXT SMALL STEP':'标题、原文与出处都能搜','你想了解什么？':'搜一个生活问题','#8B9588':'#93877A'},
 'content/detail/index.wxml':{'NOTE {{entry.chapterNumber}}.{{entry.displayNumber}}':'生活笔记 · {{entry.chapterNumber}}.{{entry.displayNumber}}'},
 'content/about/index.wxml':{'A GUIDE, NOT A TO-DO LIST':'一份可以慢慢读的生活指南'},
}
for name,mapping in replacements.items():
 p=mini/name;s=p.read_text('utf-8')
 for old,new in mapping.items():s=s.replace(old,new)
 p.write_text(s,'utf-8')
package=json.loads((root/'package.json').read_text('utf-8'));package['version']='0.2.0'
(root/'package.json').write_text(json.dumps(package,ensure_ascii=False,indent=2)+'\n','utf-8')
# Keep original content snapshot intact. Product UI version lives separately.
(mini/'lib/version.js').write_text("module.exports = '0.2.0';\n",'utf-8')
p=mini/'content/about/index.js';s=p.read_text('utf-8')
s=s.replace('meta:catalog.meta','meta:Object.assign({},catalog.meta,{version:require(\'../../lib/version\')})')
p.write_text(s,'utf-8')
print('Native navigation palette, page labels and UI version updated.')
