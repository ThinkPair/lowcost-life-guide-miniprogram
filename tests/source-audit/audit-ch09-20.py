"""Independent read-only audit of pinned chapters 9-20; writes only this lane's reports."""
import hashlib, html, json, re
from pathlib import Path
from urllib.parse import urljoin, quote

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'tests/source-audit'
CAT = ROOT / 'miniprogram/data/catalog.js'
DET = ROOT / 'miniprogram/content/data/entries.js'
catalog = json.JSONDecoder().raw_decode(CAT.read_text(encoding='utf-8').split('module.exports=',1)[1])[0]
details = json.JSONDecoder().raw_decode(DET.read_text(encoding='utf-8').split('var details=',1)[1])[0]
summaries = {e['id']:e for e in catalog['entries']}
chapters = {e['number']:e for e in catalog['chapters']}
required = ['成本','说人话','收益','证据等级','来源','备注']
def digest(s): return hashlib.sha256(s.encode('utf-8')).hexdigest()
def display(s,url):
    s = re.sub(r'<!--.*?-->', '',s,flags=re.S)
    s = re.sub(r'\[([^\]]+)\]\(([^\s)]+)\)',lambda m:m[1]+'（'+urljoin(url,html.unescape(m[2]))+'）',s)
    s = re.sub(r'<(https?://[^>]+)>',r'\1',s)
    s = re.sub(r'</?(?:br|p|div|span|strong|em)\b[^>]*>','',s,flags=re.I)
    s = re.sub(r'^#{1,6}\s+|^>\s?', '',s,flags=re.M)
    s = re.sub(r'\*\*([^*]+)\*\*',r'\1',s)
    s = re.sub(r'__([^_]+)__',r'\1',s)
    s = re.sub(r'`([^`]+)`',r'\1',s)
    s = html.unescape(s)
    return re.sub(r'\n{3,}','\n\n','\n'.join(x.rstrip() for x in s.splitlines())).strip()
def links(s,url):
    items=[]
    masked=list(s)
    for m in re.finditer(r'\[([^\]]+)\]\(([^\s)]+)\)',s):
        items.append((m.start(),urljoin(url,html.unescape(m[2]))))
        masked[m.start():m.end()]=' '*len(m[0])
    for m in re.finditer(r'https?://[^\s<>\]\"\'，。；、]+',''.join(masked)):
        u=m[0].rstrip(';,.，。；）')
        while u.endswith(')') and u.count(')')>u.count('('): u=u[:-1]
        items.append((m.start(),html.unescape(u)))
    return list(dict.fromkeys(u for _,u in sorted(items)))

report={'scope':{'chapters':[9,20],'upstreamCommit':catalog['meta']['upstreamCommit'],'independentMedicalLegalReview':False},'mechanical':{},'semanticReading':{'status':'pending','fields':[],'entryIds':[]},'findings':[],'chapters':[],'entries':[]}
reading=[]
for path in sorted((OUT/'upstream/book').glob('*.md')):
    n=int(path.name.split('-')[0])
    if not 9<=n<=20: continue
    text=path.read_text(encoding='utf-8-sig').replace('\r\n','\n')
    lines=text.splitlines()
    heads=[(i,re.match(r'^### (\d+)\. (.*)$',line)) for i,line in enumerate(lines)]
    heads=[(i,m) for i,m in heads if m]
    ch=chapters[n]; url=ch['sourceUrl']
    intro_start=next(i for i,s in enumerate(lines) if s.startswith('# '))+1
    intro='\n'.join(lines[intro_start:heads[0][0]]).strip()
    report['chapters'].append({'number':n,'file':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'entries':len(heads),'introMatches':display(intro,url)==ch['intro'],'introSource':intro})
    reading.append('\n'+'='*12+' CHAPTER '+str(n)+' '+ch['title']+'\nINTRO: '+ch['intro'])
    for k,(start,h) in enumerate(heads):
        end=heads[k+1][0] if k+1<len(heads) else len(lines)
        raw='\n'.join(lines[start+1:end]).strip()
        entry_id=f'c{n:02d}-{int(h[1]):02d}'
        d=details[entry_id]; e=summaries[entry_id]
        expected=[]; label=None; bucket=[]
        clean=re.sub(r'<!--.*?-->','',raw,flags=re.S).strip()
        for line in clean.splitlines():
            m=re.match(r'^- ([^：:]+)[：:]\s*(.*)$',line)
            if m:
                if label is not None:expected.append((label,'\n'.join(bucket).strip()))
                label=m[1];bucket=[m[2]]
            else:bucket.append(line)
        if label is not None:expected.append((label,'\n'.join(bucket).strip()))
        actual={f['label']:f['text'] for f in d['fields']}
        rawfields=dict(expected)
        tags=dict(re.findall(r'([^\s=]+)=([^\s]+)',re.search(r'<!--\s*成本标签[：:]\s*(.*?)\s*-->',raw,re.S)[1]))
        expected_links=links(raw,url);actual_links=[l['url'] for l in d['sourceLinks']]
        record={'id':entry_id,'sourceFile':str(path.relative_to(ROOT)),'sourceLine':start+1,'title':h[2],'rawBodySha256':digest(raw),'titleMatches':display(h[2],url)==e['title'],'summaryMatches':display(rawfields['说人话'],url)==e['summary'],'evidenceMatches':display(rawfields['证据等级'],url)==e['evidence'],'fieldOrderMatches':[x[0] for x in expected]==[f['label'] for f in d['fields']],'allSixFieldsPresent':all(f in actual for f in required),'fields':[],'sourceLinksMatch':expected_links==actual_links,'sourceLinkCount':len(expected_links),'missingLinks':[u for u in expected_links if u not in actual_links],'extraLinks':[u for u in actual_links if u not in expected_links],'tagsMatch':all(tags[t]==e[a] for t,a in [('钱','moneyCost'),('时间','timeCost'),('毅力','effort'),('收益','benefit'),('口径','metric')]),'semanticReviewed':False}
        for label,rawvalue in expected:
            normalized=display(rawvalue,url)
            actualvalue=actual.get(label,'')
            record['fields'].append({'label':label,'sourceChars':len(rawvalue),'sourceSha256':digest(rawvalue),'normalizedChars':len(normalized),'actualChars':len(actualvalue),'matches':normalized==actualvalue})
            if normalized!=actualvalue:report['findings'].append({'id':entry_id,'type':'conversionMismatch','field':label,'source':rawvalue,'expected':normalized,'actual':actualvalue})
            leftovers=re.findall(r'\*[^*\n]+\*|\[[^\]\n]+\]\([^\n]+\)|^\|.+\|$',actualvalue,re.M)
            if leftovers:report['findings'].append({'id':entry_id,'type':'markdownResidue','field':label,'snippets':leftovers})
        report['entries'].append(record)
        reading.append('\n'+entry_id+' '+h[2]+' [钱='+tags['钱']+']\n说人话：'+actual['说人话']+'\n备注：'+actual['备注'])
        # Full benefit paragraphs retained for adaptive checks without rereading all JS.
        (OUT/f'agent-ch{n:02d}-full.json').write_text(json.dumps([{'id':r['id'],'title':summaries[r['id']]['title'],'fields':details[r['id']]['fields']} for r in report['entries'] if r['id'].startswith(f'c{n:02d}-')],ensure_ascii=False,indent=2),encoding='utf-8')
    (OUT/f'agent-ch{n:02d}-reading.txt').write_text('\n'.join(reading),encoding='utf-8');reading=[]
report['mechanical']={'entries':len(report['entries']),'fields':sum(len(e['fields']) for e in report['entries']),'links':sum(e['sourceLinkCount'] for e in report['entries']),'allTitlesMatch':all(e['titleMatches'] for e in report['entries']),'allSixFieldsAndOrderMatch':all(e['allSixFieldsPresent'] and e['fieldOrderMatches'] and all(f['matches'] for f in e['fields']) for e in report['entries']),'allSummariesMatch':all(e['summaryMatches'] for e in report['entries']),'allEvidenceMatches':all(e['evidenceMatches'] for e in report['entries']),'allTagsMatch':all(e['tagsMatch'] for e in report['entries']),'allLinksMatch':all(e['sourceLinksMatch'] for e in report['entries']),'allChapterIntrosMatch':all(e['introMatches'] for e in report['chapters'])}
(OUT/'agent-ch09-20.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'mechanical':report['mechanical'],'findings':report['findings'],'chapterCounts':[{k:c[k] for k in ('number','entries')} for c in report['chapters']]},ensure_ascii=False,indent=2))
