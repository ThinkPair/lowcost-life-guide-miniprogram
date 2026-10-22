from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json,re,shutil

PROJECT=Path(__file__).resolve().parents[1]
ROOT=PROJECT.parents[2]
now=datetime.now(timezone(timedelta(hours=8))).replace(microsecond=0)
epoch=now.isoformat();date='2026-10-06'
revision='2026-10-06-life-guide-native-first'
source='10_Sources/低成本生活指南小程序首版本地交付与授权-2026-10-06.md'
original='10_Sources/原始材料/低成本生活指南小程序-2026-10-06'
fact='70_Governance/事实版本/product.low_cost_life_guide.milestone-2026-10-06-native-first.md'
entry='30_输出/作品/低成本生活指南小程序/README.md'
claim='低成本生活指南原生小程序0.1.0本地候选已完成，唯一入口为30_输出/作品/低成本生活指南小程序/README.md。固定上游20718eeab32cb8506971fb71b03e66a91077be07的34章667条建议全部转换，提供8主题、全文搜索、章节与成本/作者分级筛选、逐条详情、收藏、阅读历史和来源复制；完整保留适用限制与争议文字。内容构建、独立18组测试及官方模拟器18项流程通过，模拟器实际本地存储读回与重进通过且未mock存储；不代表真实手机验收。当前使用touristappid，其他可访问聊天未检出能确认归属本项目的真实AppID，不能据此断言用户从未提供。尚未生成手机预览码、正式上传、送审或发布；不改变星图主线，不启动收费或运营排期。'
mirrors=['00_Index/当前状态总览.md','00_Index/行动闭环.md','00_Index/今日驾驶舱.md','00_Index/目标地图.md','00_Index/目标达成设计.md','00_Index/每周计划与复盘.md','00_Index/长期目标总控.md','00_Index/降噪实验室深度口播项目接手卡.md','00_Index/A股公司知识库当前入口.md']
targets=['AI_STATE.md','70_Governance/当前事实字段注册表.md','30_输出/输出总览.md']+mirrors
texts={p:(ROOT/p).read_text('utf-8-sig') for p in targets}
originals=texts.copy()
assert 'LOW_COST_LIFE_GUIDE_MILESTONE:' not in texts['AI_STATE.md'],'Already written; revise explicitly instead of duplicating.'
official=json.loads((PROJECT/'tests/official/result.json').read_text('utf-8'))
assert official['status']=='PASS' and len(official['checks'])==18
def header(kind,layer='source',privacy='private',retrieval='on_demand'):
    return f"---\ntype: {kind}\nlayer: {layer}\nstatus: active\nvalidity: current\nretrieval: {retrieval}\neffective_from: '{date}'\nrecorded_at: '{epoch}'\nupdated: '{date}'\nlast_reviewed: '{date}'\nconfidence: confirmed\nprivacy: {privacy}\nschema_version: temporal-governance-v2\n"

raw=ROOT/original
raw.mkdir(parents=True,exist_ok=True)
(raw/'用户授权原话.md').write_text(header('user_authorization_record')+f"vault_source_file: {original}/用户授权原话.md\n---\n\n# 本轮制作授权\n\n用户在已说明分类、搜索、收藏、来源查看及独立AppID边界后明确说：\n\n> 可以，我们直接做一下\n\n询问本项目AppID时，用户回复：\n\n> 你搜索一下其他对话框，我记得发过\n\n本轮按此制作本地原生候选并查找可访问聊天。没有把该授权解释为使用第三方身份或直接公开发布。原话记录由本轮对话直接整理，未补造未提供的账号材料。\n",'utf-8')
archives=[]
for file in ['HowToLiveBetter-upstream.zip','HowToLiveBetter-miniapp.zip']:
    p=raw/file;archives.append(f"| `{file}` | {p.stat().st_size} | `{hashlib.sha256(p.read_bytes()).hexdigest()}` |")
(raw/'README.md').write_text(header('external_source_bundle')+f"vault_source_file: {original}/HowToLiveBetter-upstream.zip\n---\n\n# 生活指南小程序原始证据\n\n2026-10-06从两个公开仓库按固定提交下载，保留原始ZIP；未执行上游脚本。\n\n- 原书：https://github.com/eternity4719/HowToLiveBetter/tree/20718eeab32cb8506971fb71b03e66a91077be07\n- 小程序参考：https://github.com/HuiTurn/HowToLiveBetter/tree/717135e7527025a55f283f2fba98a42a7eeca224\n- 本轮用户授权原话：[[{original}/用户授权原话]]。\n\n| 原件 | 字节 | SHA256 |\n|---|---:|---|\n"+'\n'.join(archives)+'\n\n此文件是原件伴随说明，不代替原始书稿、许可或对话证据。\n','utf-8')
(ROOT/source).write_text(header('product_acceptance_record')+f"vault_source_file: {original}/用户授权原话.md\n---\n\n# 低成本生活指南首版本地交付\n\n{claim}\n\n## 授权与范围\n\n用户直接授权原话见[[{original}/用户授权原话]]。本轮只实现阅读工具与可验证原生工程，没有将其升级为经营重心。来源ZIP及校验值见[[{original}/README]]。\n\n## 可核验证据\n\n- 产品入口：[[{entry[:-3]}]]。\n- 原始内容构建：`30_输出/作品/低成本生活指南小程序/release/content-build-report.json`，34章667条、4003字段。\n- 独立测试：`30_输出/作品/低成本生活指南小程序/tests/independent-qa.json`，18/18，隔离VM与合成数据。\n- 官方模拟器：`30_输出/作品/低成本生活指南小程序/tests/official/result.json`，18项，未模拟存储接口；对应截图在同目录。\n- 分发包：`30_输出/作品/低成本生活指南小程序/release/delivery-manifest.json`。\n\n## AppID检索边界\n\n本轮只读检查当前最近50个Codex聊天、150个归档标题、相关英语项目与项目整理记录及笔记本档案索引。未检出可确认归属生活指南的独立AppID。活动列表有范围限制，ChatGPT来源当时不可用，不能宣称已经穷尽所有历史。已知另一个项目和参考仓库的AppID均未写入本产品。\n\n## 最小验证与取舍\n\n- 优先级：用户明确选择做首版，不改星图既有经营主线。\n- 外部挑战：已有免费开源版本，本版新增价值仍需用户实用反馈；内容随政策更新；AppID与审核身份需要独立确认。\n- 最小证据：能检索一条建议、查看限制和来源、收藏后重进找到；本地模拟器证据已得到，真机未知。\n- 机会成本：本轮止于首版可用工程，未延伸账户、收费、云服务或内容运营。\n",'utf-8')
fact_header=header('fact_projection_version','governance',retrieval='default')
fact_header+=f"effective_to: null\nsupersedes: null\nsuperseded_by: null\nentity_id: product.low_cost_life_guide\nclaim_key: product.low_cost_life_guide.milestone\nclaim_value: {claim}\ncardinality: single\nsource_refs:\n- {source}\nchange_reason: 用户明确授权制作原生首版，已完成本地内容转换、独立测试和官方模拟器验证。\n"
(ROOT/fact).write_text(fact_header+'---\n\n# 生活指南原生首版里程碑\n\n'+claim+'\n','utf-8')
new_registry=f"  product.low_cost_life_guide.milestone:\n    entity_id: product.low_cost_life_guide\n    current_field: LOW_COST_LIFE_GUIDE_MILESTONE\n    cardinality: single\n    review_cycle: event_driven\n    evidence_rule: direct_user_authorization_and_local_acceptance\n    source_refs:\n    - {source}\n    evidence_scope: 本地原生首版与官方模拟器通过，真实AppID和手机预览尚待确认，未上传或发布。\n    source_review_status: verified_local_reference\n    lifecycle: active\n    projection_version_ref: {fact}\n"
texts['70_Governance/当前事实字段注册表.md']=texts['70_Governance/当前事实字段注册表.md'].replace('claims:\n','claims:\n'+new_registry,1)
texts['AI_STATE.md']=texts['AI_STATE.md'].replace('ENGLISH_TEACHER_WORKBENCH_MILESTONE:',f'LOW_COST_LIFE_GUIDE_MILESTONE: {claim}\nENGLISH_TEACHER_WORKBENCH_MILESTONE:',1)
texts['00_Index/当前状态总览.md']=texts['00_Index/当前状态总览.md'].replace('| 英语工作台 |',f'| 生活指南 | 原生0.1.0本地候选，34章667条；内容、独立18组与官方模拟器18项通过，实际模拟器收藏存储读回通过 | 本项目真实AppID尚未确认，待手机预览；未上传或发布。[[{entry[:-3]}]] |\n| 英语工作台 |',1)
actions=texts['00_Index/行动闭环.md']
waiting=f"- [ ] #waiting #工具 确认生活指南自己的小程序AppID后，生成开发预览并完成手机阅读、收藏与重进验证。[task_state:: waiting] [task_id:: life-guide-phone-preview-20261006] ^life-guide-phone-preview\n\n  - 已有：0.1.0原生工程、34章667条、独立18组及官方模拟器18项通过。待核身份只能由本项目账号证据确认；不沿用学员手记或第三方AppID。未把此项扩为上架、收费或运营。入口[[{entry[:-3]}]]。\n\n"
actions=actions.replace('## 当前推进｜已选下一步\n\n','## 当前推进｜已选下一步\n\n'+waiting,1)
done=f"- [x] #工具 按用户明确授权完成低成本生活指南0.1.0微信原生首版、本地完整内容转换和模拟器验收。[task_state:: done] [task_id:: life-guide-native-first-20261006] ✅ 2026-10-06\n\n  - 完成范围：34章667条、8主题、全文搜索与筛选、逐条详情/来源、收藏和阅读历史；独立18组及官方模拟器18项通过。手机预览、真实AppID、上传审核发布未完成。依据[[{source[:-3]}]]。\n\n"
anchor='## 完成证据｜按原发生日期\n\n'
actions=actions.replace(anchor,anchor+done,1)
texts['00_Index/行动闭环.md']=actions
index=texts['30_输出/输出总览.md']
index=index.replace('# 输出总览\n','# 输出总览\n\n## 2026-10-06 低成本生活指南小程序首版\n\n[[30_输出/作品/低成本生活指南小程序/README|原生工程与使用入口]]：34章667条，分类、全文搜索、收藏、阅读历史和来源查看；独立18组与官方模拟器18项通过。当前为测试身份本地候选，真实AppID和手机预览待核，未上传或发布。[[10_Sources/低成本生活指南小程序首版本地交付与授权-2026-10-06|授权与验收证据]]。\n',1)
texts['30_输出/输出总览.md']=index
for p in ['AI_STATE.md']+mirrors:
    t=texts[p]
    t=re.sub(r'^(state_epoch|last_synced_epoch|STATE_EPOCH):[^\n]*',lambda m:m.group(1)+": '"+epoch+"'",t,flags=re.M)
    t=re.sub(r'^(state_revision|STATE_REVISION):[^\n]*',lambda m:m.group(1)+": '"+revision+"'",t,flags=re.M)
    # Keep the existing global partial status; this local product does not certify unrelated maintenance.
    texts[p]=t
backup=ROOT/'.codex-output'/('life-guide-writeback-'+now.strftime('%Y%m%dT%H%M%S'))
for p,original_text in originals.items():
    if (ROOT/p).read_text('utf-8-sig')!=original_text:
        raise RuntimeError('Concurrent change before writeback: '+p)
for p,t in texts.items():
    dest=ROOT/p
    if dest.read_text('utf-8-sig')!=originals[p]:
        raise RuntimeError('Concurrent change during writeback: '+p)
    target=backup/p;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dest,target)
    dest.write_text(t,'utf-8')
receipt={'at':epoch,'revision':revision,'field':'LOW_COST_LIFE_GUIDE_MILESTONE','source':source,'fact':fact,'mirrors':mirrors,'scope':'Product milestone only; existing current product, task scope and priorities preserved.','globalSync':'kept existing partial','backup':str(backup.relative_to(ROOT))}
(PROJECT/'release/writeback-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(receipt,ensure_ascii=False,indent=2))
