from pathlib import Path
from datetime import datetime, timezone, timedelta
import json, re, shutil

p=Path(__file__).resolve().parents[1];root=p.parents[2]
now=datetime.now(timezone(timedelta(hours=8))).replace(microsecond=0);epoch=now.isoformat();date=now.date().isoformat();revision=date+'-life-guide-content-audit'
source='10_Sources/生活指南原文逐条核对与修正-2026-10-06.md'
raw='10_Sources/原始材料/低成本生活指南小程序-2026-10-06/内容核对反馈原话.md'
prior='70_Governance/事实版本/product.low_cost_life_guide.milestone-2026-10-06-visual-refresh.md'
fact='70_Governance/事实版本/product.low_cost_life_guide.milestone-2026-10-06-content-audit.md'
entry='30_输出/作品/低成本生活指南小程序/README'
report='30_输出/作品/低成本生活指南小程序/原文逐条核对与修正报告'
claim='低成本生活指南原生小程序0.2.1本地候选已完成，唯一入口为30_输出/作品/低成本生活指南小程序/README.md。按用户要求对照固定原文，34章667条4003字段逐项比对通过；667条标题、说人话及备注逐条阅读。修复摘要截断、费用标签过度概括、栏目重命名重排及两处Markdown转义，补原书41术语、分级分档、原文加粗与条目引用；4处原文内部差异加独立核对提示，其他原文疑点留报告，未重审全部外部医学法律事实。18组回归、独立667页呈现复核、官方18项原流程及13项阅读流程和关于页补验通过，收藏格式保留。使用touristappid，真实AppID和手机验收待完成；未上传、送审或发布，用户视觉认可仍待反馈，不改变星图主线。'
mirrors=['00_Index/当前状态总览.md','00_Index/行动闭环.md','00_Index/今日驾驶舱.md','00_Index/目标地图.md','00_Index/目标达成设计.md','00_Index/每周计划与复盘.md','00_Index/长期目标总控.md','00_Index/降噪实验室深度口播项目接手卡.md','00_Index/A股公司知识库当前入口.md']
names=['AI_STATE.md','70_Governance/当前事实字段注册表.md','30_输出/输出总览.md',prior]+mirrors
originals={n:(root/n).read_text('utf-8-sig') for n in names};texts=originals.copy()
assert not (root/fact).exists()
assert json.loads((p/'release/delivery-manifest.json').read_text('utf8'))['version']=='0.2.1'
assert json.loads((p/'tests/source-audit/all-entry-verification.json').read_text('utf8'))['status']=='PASS'
assert json.loads((p/'tests/source-audit/presentation-independent.json').read_text('utf8'))['mechanicalStatus']=='PASS'
assert json.loads((p/'tests/source-audit/official-reading.json').read_text('utf8'))['status']=='PASS'
assert json.loads((p/'tests/source-audit/about-supplement.json').read_text('utf8'))['status']=='PASS'
def header(kind,layer='source',retrieval='on_demand'):
 return f"---\ntype: {kind}\nlayer: {layer}\nstatus: active\nvalidity: current\nretrieval: {retrieval}\neffective_from: '{epoch}'\nrecorded_at: '{epoch}'\nupdated: '{date}'\nlast_reviewed: '{date}'\nconfidence: confirmed\nprivacy: private\nschema_version: temporal-governance-v2\n"
new={raw:header('user_feedback_record')+f'vault_source_file: {raw}\n---\n\n# 内容核对反馈原话\n\n> 你检查一下小程序的每条具体内容和项目对应原文，为啥我觉得有的表述不太清晰呢，注意原文表述\n\n2026-10-06当前对话直接授权逐条对照和阅读修正；不构成发布授权。\n'}
new[source]=header('product_acceptance_record')+f'vault_source_file: {raw}\n---\n\n# 生活指南原文逐条核对与修正\n\n{claim}\n\n用户原话见[[{raw[:-3]}]]。完整范围、原文疑点、修正和逐条回执索引见[[{report}]]；工程入口[[{entry}]]。原始ZIP和固定SHA仍使用原证据包，未替换原件。新候选保留原作者正文和数字，编辑提示与原文区分。\n\n## 验收边界\n\n667条六字段为机械全检，667条标题/说人话/备注为逐条阅读，部分收益段为定向复核；未冒称667份外部文献与法条事实全部验证。官方模拟器和Node独立检查分开记录，真实手机未验收。完整工程包及源码/证据哈希见项目release/delivery-manifest.json。\n'
new[fact]=header('fact_projection_version','governance','default')+f'effective_to: null\nsupersedes: {prior}\nsuperseded_by: null\nentity_id: product.low_cost_life_guide\nclaim_key: product.low_cost_life_guide.milestone\nclaim_value: {claim}\ncardinality: single\nsource_refs:\n- {source}\nchange_reason: 用户要求逐条对照原文并修正不清楚的呈现，已完成0.2.1本地内容核对候选。\n---\n\n# 生活指南0.2.1原文核对候选里程碑\n\n{claim}\n'
t=texts[prior]
for k,v in {'status':'archived','validity':'superseded','retrieval':'on_demand','effective_to':f"'{epoch}'",'superseded_by':fact}.items():t=re.sub('^'+k+r':[^\n]*',k+': '+v,t,count=1,flags=re.M)
texts[prior]=t
r=texts['70_Governance/当前事实字段注册表.md'];start=r.index('  product.low_cost_life_guide.milestone:');m=re.search(r'\n  [^ \n][^\n]*:\n',r[start+1:]);end=start+1+m.start() if m else r.index('\n---',start)
block=r[start:end].replace(prior,fact).replace('10_Sources/生活指南橙色界面重制与验收-2026-10-06.md',source)
assert fact in block
block=re.sub(r'    evidence_scope:.*','    evidence_scope: 0.2.1原文忠实性与阅读修正候选，667条4003字段及模拟器通过；外部事实未全审，AppID及手机验收待完成，未发布。',block)
texts['70_Governance/当前事实字段注册表.md']=r[:start]+block+r[end:]
texts['AI_STATE.md']=re.sub(r'^LOW_COST_LIFE_GUIDE_MILESTONE:.*','LOW_COST_LIFE_GUIDE_MILESTONE: '+claim,texts['AI_STATE.md'],count=1,flags=re.M)
texts['00_Index/当前状态总览.md']=re.sub(r'^\| 生活指南 \|.*',f'| 生活指南 | 原生0.2.1内容核对候选；667条4003字段完整对照，修复摘要/费用/栏目/转义并补原书阅读说明，4处原文差异独立标注 | 原文外部事实未全审；真实AppID、手机验收及用户视觉反馈待完成，未上传或发布。[[{entry}]] |',texts['00_Index/当前状态总览.md'],count=1,flags=re.M)
a=texts['00_Index/行动闭环.md'];a=a.replace('已有：0.2.0橙色视觉候选、34章667条、独立18组及官方模拟器18项通过；待用户审美反馈。','已有：0.2.1原文核对候选、34章667条4003字段对照通过，18组回归与13项阅读流程通过；原文疑点留报告，待手机及用户反馈。',1)
anchor='## 完成证据｜按原发生日期\n\n';assert anchor in a
a=a.replace(anchor,anchor+f'- [x] #工具 完成生活指南667条与原文逐条核对及0.2.1阅读修正。[task_state:: done] [task_id:: life-guide-content-audit-20261006] ✅ 2026-10-06\n\n  - 4003字段全检、667条标题/说人话/备注逐条阅读，修正呈现并保留作者正文；原文内部问题独立列出，未冒称外部事实全审，未发布。依据[[{source[:-3]}]]。\n\n',1);texts['00_Index/行动闭环.md']=a
t=texts['30_输出/输出总览.md'];t=t.replace('## 2026-10-06 生活指南0.2.0界面重制','## 2026-10-06 生活指南0.2.0界面重制（历史阶段）',1)
t=t.replace('# 输出总览\n',f'# 输出总览\n\n## 2026-10-06 生活指南0.2.1原文核对\n\n[[{entry}|当前工程入口]]；[[{report}|逐条核对与修正报告]]。667条完整对照和阅读修正通过，原文自身疑点单列，未上传发布。\n',1);texts['30_输出/输出总览.md']=t
for n in ['AI_STATE.md']+mirrors:
 t=texts[n];t=re.sub(r'^(state_epoch|last_synced_epoch|STATE_EPOCH):[^\n]*',lambda m:m[1]+": '"+epoch+"'",t,flags=re.M);t=re.sub(r'^(state_revision|STATE_REVISION):[^\n]*',lambda m:m[1]+": '"+revision+"'",t,flags=re.M);texts[n]=t
for n,old in originals.items():assert (root/n).read_text('utf-8-sig')==old,'Concurrent write '+n
backup=root/'.codex-output'/('life-guide-content-writeback-'+now.strftime('%Y%m%dT%H%M%S'))
for n,t in new.items():assert not(root/n).exists();(root/n).write_text(t,'utf8')
for n,t in texts.items():
 assert(root/n).read_text('utf-8-sig')==originals[n],'Concurrent write '+n
 dest=backup/n;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/n,dest);(root/n).write_text(t,'utf8')
(p/'release/content-writeback-receipt.json').write_text(json.dumps({'epoch':epoch,'revision':revision,'source':source,'fact':fact,'backup':str(backup.relative_to(root)),'globalSync':'pre-existing partial preserved'},ensure_ascii=False,indent=2),'utf8')
print('0.2.1 milestone and mirrors written: '+epoch)
