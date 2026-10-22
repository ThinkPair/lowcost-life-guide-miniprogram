from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, zipfile

ROOT=Path(__file__).resolve().parents[1]
MINI=ROOT/'miniprogram'
OUT=ROOT/'release'
OUT.mkdir(exist_ok=True)
version=json.loads((ROOT/'package.json').read_text('utf-8'))['version']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
independent=json.loads((ROOT/'tests/independent-qa.json').read_text('utf-8'))
official=json.loads((ROOT/'tests/official/result.json').read_text('utf-8'))
content=json.loads((OUT/'content-build-report.json').read_text('utf-8'))
assert independent['totals']['failed']==0 and official['status']=='PASS' and content['status']=='PASS'
files=[p for p in MINI.rglob('*') if p.is_file() and p.name!='project.private.config.json']
main_size=sum(p.stat().st_size for p in files if 'content' not in p.relative_to(MINI).parts[:1])
content_size=sum(p.stat().st_size for p in files if p.relative_to(MINI).parts[0]=='content')
assert main_size<2*1024*1024 and content_size<2*1024*1024, 'Package exceeds 2MiB source budget'
config=json.loads((MINI/'project.config.json').read_text('utf-8'))
assert config['appid']=='touristappid', 'Publishing identity must be reviewed separately'
readme='''# 低成本生活指南 · 微信小程序 {version}

本包是可导入微信开发者工具的原生小程序工程，包含8个主题、34章、667条建议，支持离线阅读、全文搜索、组合筛选、收藏、最近阅读和来源复制。

0.2.1更新：667条与原文逐项对照；列表摘要完整显示，恢复原文栏目与顺序，修复两处Markdown转义，保留作者加粗，费用改为原文标签。加入原书术语/分档说明、条目引用导航、4处独立原文差异提示。收藏数据格式保持一致。

## 打开工程

1. 解压本包。
2. 使用微信开发者工具导入 `miniprogram` 目录，或在Windows中运行 `打开微信开发版.ps1`。
3. 工程当前使用 `touristappid` 测试身份，可进行本地开发。手机扫码预览前须在开发者工具中确认并填入本项目自己的AppID。

首版已完成18组独立测试和18项官方模拟器流程验证；真实手机尚未验收，未生成手机预览码，未正式上传、送审或发布。

## 使用

从“指南”选择主题，或从搜索找到具体问题。“全部”可按主题、章节、原文钱标签为0及作者分级筛选。标签不承诺全过程免费，具体成本以正文为准。详情保留原文栏目、适用限制和争议文字，可展开来源并复制链接。收藏与最近100条阅读记录只保存在当前设备；清理缓存、删除小程序或换设备可能丢失记录。

本版没有账号、后台、支付、云同步或外部AI请求。作者分级沿用原书，内容转换完整性已核对，未逐条重新验证医学、法律或金融结论。

## 来源与许可

正文：eternity4719 / HowToLiveBetter，固定提交20718eeab32cb8506971fb71b03e66a91077be07，2026-10-06获取。
https://github.com/eternity4719/HowToLiveBetter/tree/20718eeab32cb8506971fb71b03e66a91077be07

阅读与收藏结构参考：HuiTurn / HowToLiveBetter，固定提交717135e7527025a55f283f2fba98a42a7eeca224。
https://github.com/HuiTurn/HowToLiveBetter/tree/717135e7527025a55f283f2fba98a42a7eeca224

本版重新制作页面、逐条索引和主题导航；未使用参考作者的图片、品牌身份或AppID。内容使用CC BY 4.0，全文见 `licenses/CC-BY-4.0.txt`。署名、来源、许可和修改说明也保留在“关于”页面。
'''
readme=readme.replace('{version}',version)
package=OUT/('低成本生活指南-微信小程序-'+version+'.zip')
with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(files):z.write(p,'miniprogram/'+p.relative_to(MINI).as_posix())
    z.writestr('README.md',readme)
    for p in [ROOT/'打开微信开发版.ps1',ROOT/'licenses/CC-BY-4.0.txt']:
        z.write(p,p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(package) as z: assert z.testzip() is None
manifest={
 'version':version,'status':'local_native_candidate','createdAt':datetime.now(timezone.utc).isoformat(),
 'package':package.name,'sha256':sha(package),'zipBytes':package.stat().st_size,
 'sourceBytes':{'main':main_size,'contentSubpackage':content_size},
 'content':content['totals'],'upstreamCommit':content['upstreamCommit'],
 'independentChecks':independent['totals'],'officialChecks':len(official['checks']),
 'appId':config['appid'],'officialSimulator':'passed','realPhone':'not_verified',
 'previewQr':None,'upload':False,'audit':False,'published':False,
 'sourceFiles':{p.relative_to(MINI).as_posix():sha(p) for p in sorted(files)},
 'evidenceFiles':{p.relative_to(ROOT).as_posix():sha(p) for p in [ROOT/'tests/independent-qa.json',ROOT/'tests/official/result.json',OUT/'content-build-report.json']},
 'notes':['Source sizes are conservative local byte totals, not a WeChat upload receipt.','Official simulator storage was exercised without mocking storage APIs. Real phone remains unverified.']
}
if (OUT/'visual-review.json').exists():
    visual=json.loads((OUT/'visual-review.json').read_text('utf-8'))
    assert visual['status']=='PASS'
    manifest['visualReview']={'status':'PASS','baselineVersion':'0.2.0','scope':'prior six-page visual baseline; current reading changes have separate source-audit evidence','userAcceptance':visual['userAcceptance'],'pages':len(visual['pages'])}
    for p in [OUT/'visual-review.json',ROOT/'tests/visual-refresh/capture.json']:
        manifest['evidenceFiles'][p.relative_to(ROOT).as_posix()]=sha(p)
if version=='0.2.1':
    audit_paths=['all-entry-verification.json','presentation-independent.json','official-reading.json','about-supplement.json','agent-ch01-08.json','agent-ch09-20.json','agent-ch21-34.json']
    for filename in audit_paths:
        p=ROOT/'tests/source-audit'/filename
        data=json.loads(p.read_text('utf-8'))
        if filename in audit_paths[:4]:assert data.get('status',data.get('mechanicalStatus'))=='PASS',filename
        manifest['evidenceFiles'][p.relative_to(ROOT).as_posix()]=sha(p)
    manifest['contentReview']={'entriesCompared':667,'fieldsCompared':4003,'titleSummaryCaveatRead':667,'glossaryTerms':41,'editorialNotices':4,'externalFactReview':False,'officialReadingChecks':13,'aboutSupplement':'PASS'}
(OUT/'delivery-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps({k:v for k,v in manifest.items() if k not in ['sourceFiles','evidenceFiles','content']},ensure_ascii=False,indent=2))
