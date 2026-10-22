"""Append actual human/model reading coverage to the frozen pre-rebuild lane report."""
import json, hashlib, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'tests/source-audit'
path=OUT/'agent-ch09-20.json'
report=json.loads(path.read_text(encoding='utf-8'))
benefit_ids=['c09-01','c09-08','c10-02','c10-15','c11-16','c12-11','c12-14','c13-20','c13-28','c13-35','c16-07','c16-09','c18-01','c18-03','c19-03','c19-05','c20-03']
report['scope']['appVersion']='0.2.0 before current fidelity fixes'
report['scope']['snapshotArchive']='tests/source-audit/before-0.2.0.zip'
report['scope']['rebuildRetested']=False
with zipfile.ZipFile(OUT/'before-0.2.0.zip') as z:
    report['scope']['snapshotFiles']=[{'path':p,'sha256':hashlib.sha256(z.read(p)).hexdigest()} for p in ['miniprogram/data/catalog.js','miniprogram/content/data/entries.js','miniprogram/lib/catalog.js','miniprogram/content/detail/index.js','miniprogram/content/detail/index.wxml']]
report['semanticReading']={'status':'completed_for_declared_fields','method':'Read every title, complete 说人话 and complete 备注, and each chapter intro from frozen extracted reading packets; extraction was mechanically checked against pinned upstream. Read 17 full related 收益 fields to resolve apparent qualifier conflicts. This is neither a complete medical/legal re-review nor a claim that every source paper or all 208 收益 paragraphs were read.','chapterIntroCount':12,'entryCount':208,'fieldsReadForAllEntries':['title','说人话','备注'],'entryIds':[e['id'] for e in report['entries']],'benefitParagraphsRead':benefit_ids,'sourcePaperChecks':0,'networkResearch':False}
byid={e['id']:e for e in report['entries']}
for e in report['entries']:
    e['semanticReviewed']=True
    e['semanticFieldsRead']=['title','说人话','备注']+(['收益'] if e['id'] in benefit_ids else [])
    e['semanticDisposition']='No additional conversion issue observed in declared reading fields; source wording retained, not independently endorsed.'

findings=[
{'findingId':'F09-20-01','severity':'P2','kind':'conversion_presentation','ids':['c16-09'],'title':'Markdown escape and broken bold delimiters remain in gene name paragraph','sourceExcerpt':'**汉族人用别嘌醇之前值得先查 HLA-B\\\\*5801**','actualExcerpt':'**汉族人用别嘌醇之前值得先查 HLA-B\\\\*5801。它是一种天生的…刚开始降尿酸反而更容易诱发发作**','effect':'Builder bold matching is interrupted by the internal star; data retains delimiters across the intervening paragraph. Detail plain() strips ** but does not remove Markdown backslash escapes. Preserve the meaningful allele-name star.','recommendation':'Render original bold spans properly and normalize escaped punctuation to visible HLA-B*5801; do not remove the star or rewrite the medical text.','status':'reported to root; root says fix in progress, not independently retested'},
{'findingId':'F09-20-02','severity':'P2','kind':'app_label_overstatement','ids':['c20-01','c20-07','c13-15','c13-23','c16-01','c14-08','c17-02'],'title':'App converts author money tag 0 into an unconditional 不花钱 badge','sourceExcerpts':{'c20-01':'不花钱。床垫要换成硬的，几百元。','c20-07':'0 元到几十元。这笔钱通常已经包含在住院生孩子的费用里，不用另外交','c13-15':'不花钱。已知有严重过敏的人自备肾上腺素笔要花钱，而且它是处方药。','c13-23':'不花钱。一瓶运动饮料几元。','c16-01':'不花钱，反而省下以后治并发症的钱。每天吃药占不了几分钟','c14-08':'不花钱。只有对方拖着不办，才需要去投诉或者起诉。真打官司就是几个月起步，律师费还要自己出','c17-02':'自己手写一份遗嘱，不花钱。找公证处公证，几百到上千元。'},'effect':'Original 0 tags coexist with actual purchase, medicine, or legal-service costs. App badge reads as a stronger promise than the documented cost paragraph.','recommendation':'Keep author-tag attribution explicit (for example 原文钱标签：0) and point to original cost; do not infer a new cost classification or change source tags.'},
{'findingId':'F09-20-03','severity':'P2','kind':'source_internal_inconsistency','ids':['c12-11'],'title':'Source heading says 起刑五年 but its body says 5年以下','sourceExcerpts':{'title':'掺了有毒有害的不看金额、起刑五年','说人话':'往食品里掺有毒有害的非食品原料，起步就是 5 年以下，不看你卖了多少钱。','收益':'判 5 年以下有期徒刑并罚钱。把人的健康搞出严重损害，或者有其他严重情节的，判 5 年以上 10 年以下并罚钱。'},'effect':'Heading and same-entry explanation point in materially different directions. This discrepancy exists in pinned upstream and was faithfully copied.','recommendation':'Retain original text, attribute it, and record a source wording query; do not silently correct a legal conclusion.'},
{'findingId':'F09-20-04','severity':'P2','kind':'source_summary_compression','ids':['c09-01','c09-08','c10-02','c10-15','c19-03','c19-05'],'title':'Original condensed headings and 说人话 omit qualifiers that remain in 收益 or 备注','sourceExcerpts':{'c09-01':['说人话：还要罚 1000 元','收益：还可以再罚 1000 元以下。情节较轻…拘留 5 日以下，或者罚 1000 元以下'], 'c09-08':['说人话：骗到 3000 元就能判 3 年以下，3 万元起判 3 到 10 年','收益：各省在下面的幅度内定本地标准。较大是 3000 元至 1 万元以上。巨大是 3 万元至 10 万元以上'], 'c10-02':['说人话：对方明确说了拒绝，你还发消息、还去等人…就是治安违法','收益：多次发送…或者采取滋扰、纠缠、跟踪等方法，干扰他人正常生活的'], 'c10-15':['说人话：分居满两年','收益：因感情不和分居满二年等情形'], 'c19-03':['说人话：合同签 1 年以内的，试用期最多 1 个月。签 1 到 3 年的最多 2 个月','收益：合同签 3 个月以上不满 1 年…签 1 年以上不满 3 年…总共不到 3 个月的合同，不许约定试用期'], 'c19-05':['标题：公司辞退你没提前 30 天通知，还要多付一个月工资','备注：这一个月只出现在劳动合同法第四十条的三种情形里']},'effect':'Qualifiers are present in app body; no parser omission found. Isolated titles and summary sections can nevertheless be read as more absolute rules.','recommendation':'Maintain original-field provenance and immediate access to the full 收益 and 备注. Source correction is separate, not within this presentation fix.'},
{'findingId':'F09-20-05','severity':'P3','kind':'source_ambiguity','ids':['c11-16'],'title':'Original 备案说不收费、实际在收钱 is ambiguous without its 收益 paragraph','sourceExcerpts':{'说人话':'备案说不收费、实际在收钱的，罚 10 万到 100 万元。','收益':'未经许可经营的，没收违法所得，并罚违法所得的 3 到 5 倍，或者罚 10 万到 100 万元。','备注':'备案成个人非经营性，实际却在收费'},'effect':'Could be read as a registration vendor charging a fee, whereas the same entry describes a commercial service registered as noncommercial. Original phrase preserved.','recommendation':'Keep original wording and full explanatory body; record author wording ambiguity, do not silently replace the conclusion.'},
{'findingId':'F09-20-06','severity':'P3','kind':'field_presentation','ids':['c09-01','c11-16','c12-11','c20-10'],'title':'Reader-facing blocks obscure original field identity','sourceExcerpts':{'originalFields':['说人话','收益','备注'],'currentDisplay':['这条建议在说什么','收益','先看适用条件与限制'],'c20-10':'TODO（待核实：调查结论。截至 2026 年 9 月 30 日…没找到纸尿裤的结论）'},'effect':'收益 is often legal penalties or supporting evidence, and 备注 includes source status, not only applicability. Not a text-fidelity loss, but the app can make the author’s provisional explanations sound like app-authored guidance.','recommendation':'Retain original names with attribution, e.g. 原文说人话／原文收益与依据／原文备注, and retain TODO and date qualifiers instead of deleting them.'},
{'findingId':'F09-20-07','severity':'P3','kind':'source_cross_reference','ids':['c20-12'],'title':'Infant choking cross-reference points to the general choking entry','sourceExcerpts':{'c20-12':'噎住了怎么办见第 13 节第 26 条（有人噎住说不出话）。','c13-26':'不满 1 岁的孩子不按肚子，改按胸口，见本节第 43 条（婴儿噎住）。'},'effect':'Both original cross-reference and redirect remain intact, but an infant-specific entry requires an extra hop through the adult/general entry. This is an upstream navigation issue, not a missing field.','recommendation':'Preserve the original cross-reference. If adding navigation aids, keep the original reference visible and label any direct link to c13-43 as editorial navigation, not substituted original text.'}
]
report['findings']=findings
for f in findings:
    for entry_id in f['ids']:
        e=byid.get(entry_id)
        if e is not None:
            e.setdefault('findingIds',[]).append(f['findingId'])
            e['semanticDisposition']='See findingIds; distinguish app presentation issue from preserved upstream wording.'
report['conclusion']={'textualFidelity':'PASS for all 208 entries after presentation-only normalization','presentation':'ISSUES_FOUND in pre-fix badge wording and Markdown escape rendering','sourceWording':'Several original summaries/titles compress or conflict with their own qualifiers; not corrected in this audit','postFixStatus':'NOT_TESTED_BY_THIS_LANE'}
path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
md='''# 第9—20章独立原文核对

范围：修复前 0.2.0，固定上游 `20718eeab32cb8506971fb71b03e66a91077be07`。不是重建后验收。

- 机械核对208条、1248个字段、534个去重条目来源链接全部通过；标题、六字段顺序和内容、摘要、作者分级、成本标签、12章导语均匹配原文。
- 逐条读完208条的标题、完整“说人话”和完整“备注”，以及12章导语。另完整读17条相关“收益”，具体ID在JSON。没有声称逐篇读来源论文或重做医疗/法律核验。
- 需要修呈现：`c16-09`的Markdown加粗和HLA-B*5801转义；作者“钱=0”被应用扩成“不花钱”的绝对标签。正文和作者标签不擅改。
- 原文本身的关键问题：`c12-11`“起刑五年”与正文“5年以下”不一致；`c09-01`“还要罚1000元”与“还可以再罚1000元以下”不同；`c19-03`试用期摘要省略小于3个月和边界限制；`c19-05`标题省略只适用三类解除的限定。均有完整原文片段，不能算成转换错误。
- 其他：保留原字段身份更清楚；`c20-10`原文TODO与核验日期必须保留；`c20-12`婴儿噎住交叉引用到普通条目是原文路径，若优化直达需标成编辑导航。

`agent-ch09-20.json`包含208条逐项覆盖记录、1248字段来源哈希、每条来源行号、原数据与展示代码快照哈希、发现及处置边界。本分工没有改应用、构建器或固定原文。
'''
(OUT/'agent-ch09-20.md').write_text(md,encoding='utf-8')
print('Finalized 208 entry audit records; 17 full related benefit paragraphs; 7 grouped findings.')
