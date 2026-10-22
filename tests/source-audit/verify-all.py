"""Independent source-to-display audit; never imports the production builder."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, html, json, re, zipfile
from urllib.parse import urljoin

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SRC = HERE / 'upstream'
sha = lambda b: hashlib.sha256(b).hexdigest()

def module(text, begin, end):
    return json.loads(text.split(begin, 1)[1].split(end, 1)[0])

catalog = module((ROOT/'miniprogram/data/catalog.js').read_text('utf8'), 'module.exports=', ';\n')
details = module((ROOT/'miniprogram/content/data/entries.js').read_text('utf8'), 'var details=', ';\nvar chapters=')
entries = {e['id']: e for e in catalog['entries']}
with zipfile.ZipFile(HERE/'before-0.2.0.zip') as z:
    before = module(z.read('miniprogram/content/data/entries.js').decode('utf8'), 'var details=', ';\nvar chapters=')

def display(raw, url):
    s = re.sub(r'<!--.*?-->', '', raw, flags=re.S)
    s = re.sub(r'\[([^\]]+)\]\(([^\s)]+)\)', lambda m:m[1]+'（'+urljoin(url,m[2])+'）',s)
    s = re.sub(r'<(https?://[^>]+)>', lambda m:m[1],s)
    s = s.replace('**','')
    s = re.sub(r'\\([\\`*{}\[\]()#+\-.!_>])',lambda m:m[1],s)
    s = re.sub(r'^#{1,6}\s+', '', s, flags=re.M)
    return re.sub(r'\n{3,}', '\n\n', '\n'.join(l.rstrip() for l in html.unescape(s).splitlines())).strip()

records, errors, changes, chapters = [], [], [], []
for f in sorted((SRC/'book').glob('*.md')):
    num = int(f.name[:2]); c = next(c for c in catalog['chapters'] if c['number']==num)
    text = f.read_text('utf-8-sig'); lines = text.splitlines()
    starts = [(i,re.fullmatch(r'### (\d+)\. (.+)',line)) for i,line in enumerate(lines)]
    starts = [(i,m) for i,m in starts if m]
    title_line = next(i for i,l in enumerate(lines) if l.startswith('# '))
    assert display('\n'.join(lines[title_line+1:starts[0][0]]),c['sourceUrl']) == c['intro'], f.name+' intro'
    assert c['count']==len(starts)
    chapters.append({'file':f.name,'sha256':sha(f.read_bytes()),'entries':len(starts),'introMatch':True})
    for idx,(start,m) in enumerate(starts):
        stop=starts[idx+1][0] if idx+1<len(starts) else len(lines)
        id=f'c{num:02d}-{int(m[1]):02d}'; current=details[id]; meta=entries[id]
        blocks=[]; label=None; buf=[]; in_comment=False
        for line in lines[start+1:stop]:
            if line.startswith('<!--'):
                in_comment='-->' not in line; continue
            if in_comment:
                if '-->' in line:in_comment=False
                continue
            match=re.match(r'^- ([^：]+)：(.*)$',line)
            if match or line.startswith('## '):
                if label:blocks.append((label,'\n'.join(buf).strip()))
                label=match[1] if match else '章节附记';buf=[match[2]] if match else [line]
            elif label:buf.append(line)
            elif line.strip():raise AssertionError(id+' unaccounted line '+line)
        if label:blocks.append((label,'\n'.join(buf).strip()))
        expected=[{'label':k,'text':display(v,c['sourceUrl'])} for k,v in blocks]
        actual=[{'label':v['label'],'text':v['text']} for v in current['fields']]
        issues=[]
        if actual!=expected:issues.append('field text or order differs')
        if meta['title']!=display(m[2],c['sourceUrl']):issues.append('title differs')
        if meta['summary']!=next(v['text'] for v in expected if v['label']=='说人话'):issues.append('summary differs')
        if meta['evidence']!=next(v['text'] for v in expected if v['label']=='证据等级'):issues.append('grade differs')
        if current['entrySourceUrl']!=c['sourceUrl']+f'#L{start+1}':issues.append('source anchor differs')
        for old,new in zip(before[id]['fields'],current['fields']):
            if old['text']!=new['text']:changes.append({'id':id,'field':new['label'],'before':old['text'],'after':new['text']})
        record={'id':id,'sourceLine':start+1,'fields':len(blocks),'match':not issues,'issues':issues,'rawBodySHA256':sha('\n'.join(lines[start:stop]).encode()),'displaySHA256':sha(json.dumps(actual,ensure_ascii=False).encode())}
        records.append(record);errors.extend([id+': '+x for x in issues])

assert len(records)==667 and len(chapters)==34
assert sum(r['fields'] for r in records)==4003
assert [(c['id'],c['field']) for c in changes]==[('c06-19','备注'),('c16-09','备注')], 'Unexpected prose change'
assert all('HLA-B*5801' in c['after'] and '\\*' not in c['after'] and '**' not in c['after'] for c in changes)
assert not errors, errors
guide=module((ROOT/'miniprogram/data/reading-guide.js').read_text('utf8'),'module.exports=',';\n')
readme=(SRC/'README.md').read_text('utf8')
for item in guide['glossary']+guide['grades']:
    assert '| '+item['term']+' | '+item['text']+' |' in readme,item['term']
assert len(guide['glossary'])==41 and len(guide['grades'])==3
report={'status':'PASS','at':datetime.now(timezone.utc).isoformat(),'method':'Independent line-state parser against the pinned upstream Markdown. Full field/order/title/summary/grade/chapter-intro comparison; no medical/legal/financial fact verification.','totals':{'chapters':34,'entries':667,'fields':4003,'glossaryTerms':41,'gradeDefinitions':3,'unexpectedDifferences':0,'formattingFixes':len(changes)},'chapters':chapters,'entries':records,'formattingFixes':changes}
(HERE/'all-entry-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf8')
print(json.dumps({'status':'PASS','totals':report['totals']},ensure_ascii=False))
