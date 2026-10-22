from pathlib import Path
from datetime import datetime,timezone,timedelta
import re,json,shutil

project=Path(__file__).resolve().parents[1]
root=project.parents[2]
now=datetime.now(timezone(timedelta(hours=8))).replace(microsecond=0)
epoch=now.isoformat();date='2026-10-06';revision='2026-10-06-life-guide-visual-refresh'
source='10_Sources/生活指南橙色界面重制与验收-2026-10-06.md'
raw='10_Sources/原始材料/低成本生活指南小程序-2026-10-06/界面修改反馈原话.md'
fact='70_Governance/事实版本/product.low_cost_life_guide.milestone-2026-10-06-visual-refresh.md'
prior='70_Governance/事实版本/product.low_cost_life_guide.milestone-2026-10-06-native-first.md'
entry='30_输出/作品/低成本生活指南小程序/README'
claim='低成本生活指南原生小程序0.2.0视觉候选已完成，唯一入口为30_输出/作品/低成本生活指南小程序/README.md。按用户要求参考生意有谱实际截图重做暖白底、深色正文、橙色操作与细边框；首页八主题改为两行图标，列表、搜索、阅读、收藏和关于页同步。34章667条原文及本地存储格式保持一致，署名和许可保留；独立18组与官方模拟器18项流程通过，六页面实看和独立视觉复核完成，用户审美验收仍待反馈。使用touristappid，生活指南真实AppID或是否替换现有项目身份尚待用户确认；没有生成手机预览码、上传、送审或发布，不改变星图主线。'
mirrors=['00_Index/当前状态总览.md','00_Index/行动闭环.md','00_Index/今日驾驶舱.md','00_Index/目标地图.md','00_Index/目标达成设计.md','00_Index/每周计划与复盘.md','00_Index/长期目标总控.md','00_Index/降噪实验室深度口播项目接手卡.md','00_Index/A股公司知识库当前入口.md']
targets=['AI_STATE.md','70_Governance/当前事实字段注册表.md','30_输出/输出总览.md',prior]+mirrors
texts={p:(root/p).read_text('utf-8-sig') for p in targets};originals=texts.copy()
assert fact not in texts['70_Governance/当前事实字段注册表.md'],'Already written'
assert json.loads((project/'tests/official/result.json').read_text('utf-8'))['status']=='PASS'
assert json.loads((project/'tests/independent-qa.json').read_text('utf-8'))['totals']['failed']==0
assert json.loads((project/'release/visual-review.json').read_text('utf-8'))['status']=='PASS'
assert json.loads((project/'release/delivery-manifest.json').read_text('utf-8'))['version']=='0.2.0'
def header(kind,layer='source',retrieval='on_demand'):
 return f"---\ntype: {kind}\nlayer: {layer}\nstatus: active\nvalidity: current\nretrieval: {retrieval}\neffective_from: '{epoch}'\nrecorded_at: '{epoch}'\nupdated: '{date}'\nlast_reviewed: '{date}'\nconfidence: confirmed\nprivacy: private\nschema_version: temporal-governance-v2\n"
new={}
new[raw]=header('user_feedback_record')+f"vault_source_file: {raw}\n---\n\n# 界面修改反馈原话\n\n> 配色修改改一下，你这审美我是真的看不下去啊，至少要不低于生意有谱那个项目的ui设计啊\n\n本条直接记录2026-10-06当前对话用户原话；不据此认定用户已接受新配色，也不改变AppID与发布授权状态。\n"
new[source]=header('product_acceptance_record')+f"vault_source_file: {raw}\n---\n\n# 生活指南橙色界面重制\n\n{claim}\n\n## 原始反馈和参考\n\n用户反馈见[[{raw[:-3]}]]。经资料路径映射定位并实看本机 `D:/个人资料与项目/02_工作资产与参赛/生意有谱-界面截图/01-问题看板.png` 与 `03-新话题-开场气泡.png`。取用页面背景#FAF6EF、卡片#FFFDF9、边框#E8DDC9、橙色#C2530C，以及清晰层级、少量阴影和紧凑入口；未读取或修改该项目业务。\n\n## 已交付\n\n- 工程与说明：[[{entry}]]，版本0.2.0；旧0.1.0工程ZIP保留。\n- 官方流程：`30_输出/作品/低成本生活指南小程序/tests/official/result.json`。\n- 独立检查：`30_输出/作品/低成本生活指南小程序/tests/independent-qa.json`。\n- 新版六页面与滚动截图：`30_输出/作品/低成本生活指南小程序/tests/visual-refresh/`。\n- 视觉复核与范围：`30_输出/作品/低成本生活指南小程序/release/visual-review.json`。\n- 工程包与校验值：`30_输出/作品/低成本生活指南小程序/release/delivery-manifest.json`。\n\n只验证实现与截图，无真实手机验收；设计是否满意由用户本人判断，未把Agent通过写成用户认可。正文来源与版权边界沿此前说明。\n"
new[fact]=header('fact_projection_version','governance','default')+f"effective_to: null\nsupersedes: {prior}\nsuperseded_by: null\nentity_id: product.low_cost_life_guide\nclaim_key: product.low_cost_life_guide.milestone\nclaim_value: {claim}\ncardinality: single\nsource_refs:\n- {source}\nchange_reason: 用户要求配色与UI至少对齐生意有谱，已按实际截图重做并验收本地实现。\n---\n\n# 生活指南0.2.0视觉候选里程碑\n\n{claim}\n"
t=texts[prior]
for key,value in {'status':'archived','validity':'superseded','retrieval':'on_demand','effective_to':f"'{epoch}'",'superseded_by':fact}.items():
 t=re.sub(r'^'+key+r':[^\n]*',key+': '+value,t,count=1,flags=re.M)
texts[prior]=t
registry=texts['70_Governance/当前事实字段注册表.md']
start=registry.index('  product.low_cost_life_guide.milestone:');end=registry.find('\n  ',start+len('  product.low_cost_life_guide.milestone:'))
# A block ends at the next exactly two-space claim, not its nested properties.
match=re.search(r'\n  [^ \n][^\n]*:\n',registry[start+1:])
end=start+1+match.start() if match else registry.index('\n---',start)
block=registry[start:end].replace(prior,fact).replace('10_Sources/低成本生活指南小程序首版本地交付与授权-2026-10-06.md',source)
block=re.sub(r'    evidence_scope:.*','    evidence_scope: 0.2.0橙色视觉候选及模拟器通过，用户审美反馈与手机预览待核，未上传或发布。',block)
texts['70_Governance/当前事实字段注册表.md']=registry[:start]+block+registry[end:]
texts['AI_STATE.md']=re.sub(r'^LOW_COST_LIFE_GUIDE_MILESTONE:.*','LOW_COST_LIFE_GUIDE_MILESTONE: '+claim,texts['AI_STATE.md'],count=1,flags=re.M)
texts['00_Index/当前状态总览.md']=re.sub(r'^\| 生活指南 \|.*',f'| 生活指南 | 原生0.2.0橙色视觉候选，参照生意有谱重做首页与全页样式；34章667条，独立18组和官方18项通过 | 用户视觉反馈与本项目AppID待确认，未手机验收、上传或发布。[[{entry}]] |',texts['00_Index/当前状态总览.md'],count=1,flags=re.M)
actions=texts['00_Index/行动闭环.md']
actions=actions.replace('已有：0.1.0原生工程、34章667条、独立18组及官方模拟器18项通过。','已有：0.2.0橙色视觉候选、34章667条、独立18组及官方模拟器18项通过；待用户审美反馈。',1)
done=f'- [x] #工具 按用户反馈参考生意有谱重做生活指南0.2.0配色和全页UI，完成模拟器与独立视觉复核。[task_state:: done] [task_id:: life-guide-ui-refresh-20261006] ✅ 2026-10-06\n\n  - 暖白、深色文字、橙色操作及八主题图标；全文/收藏逻辑保留，18组独立与18项官方流程通过。实现完成不等于用户审美认可；未手机预览或发布。依据[[{source[:-3]}]]。\n\n'
anchor='## 完成证据｜按原发生日期\n\n';assert anchor in actions
texts['00_Index/行动闭环.md']=actions.replace(anchor,anchor+done,1)
index=texts['30_输出/输出总览.md'];anchor='# 输出总览\n'
texts['30_输出/输出总览.md']=index.replace(anchor,anchor+f'\n## 2026-10-06 生活指南0.2.0界面重制\n\n[[{entry}|新版工程与使用入口]]：参考生意有谱改为暖白与橙色、八主题图标入口及统一阅读卡片。实现与模拟器通过，用户审美反馈和手机预览待核。[[{source[:-3]}|原始反馈与验收]]。\n',1)
for name in ['AI_STATE.md']+mirrors:
 t=texts[name]
 t=re.sub(r'^(state_epoch|last_synced_epoch|STATE_EPOCH):[^\n]*',lambda m:m.group(1)+": '"+epoch+"'",t,flags=re.M)
 t=re.sub(r'^(state_revision|STATE_REVISION):[^\n]*',lambda m:m.group(1)+": '"+revision+"'",t,flags=re.M)
 texts[name]=t
for name,old in originals.items():
 assert (root/name).read_text('utf-8-sig')==old,'Concurrent update: '+name
backup=root/'.codex-output'/('life-guide-visual-writeback-'+now.strftime('%Y%m%dT%H%M%S'))
for name,content in new.items():
 assert not (root/name).exists(),'Evidence already exists: '+name
 (root/name).write_text(content,'utf-8')
for name,content in texts.items():
 assert (root/name).read_text('utf-8-sig')==originals[name],'Concurrent update: '+name
 target=backup/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/name,target)
 (root/name).write_text(content,'utf-8')
(project/'release/visual-writeback-receipt.json').write_text(json.dumps({'epoch':epoch,'revision':revision,'source':source,'fact':fact,'prior':prior,'backup':str(backup.relative_to(root)),'userVisualAcceptance':'pending','globalSync':'pre-existing partial preserved'},ensure_ascii=False,indent=2)+'\n','utf-8')
print('0.2.0 current milestone and all mirrors written at '+epoch)
