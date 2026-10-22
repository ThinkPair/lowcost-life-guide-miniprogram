/* Independent behavioral QA. Runs only against local app code and synthetic wx storage. */
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const root = path.resolve(__dirname, '../miniprogram');
const results = [];
const clone = value => value === undefined ? undefined : JSON.parse(JSON.stringify(value));
const same = (actual, expected, message) => assert.deepEqual(clone(actual), clone(expected), message);
function test(name, run) {
  try { run(); results.push({name, status:'pass'}); }
  catch (error) { results.push({name, status:'fail', message:error.message}); }
}
function harness(initial = '') {
  const state = {stored:clone(initial), writes:0, calls:[], readError:false, writeError:false,
    app:{globalData:{libraryFilter:null}}, timer:null, modalConfirm:true, clipboardError:false};
  const wx = {
    getStorageSync() { if (state.readError) throw Error('synthetic read failure'); return clone(state.stored); },
    setStorageSync(key, value) { state.calls.push({type:'write-attempt',key}); if (state.writeError) throw Error('synthetic write failure'); state.stored=clone(value); state.writes++; },
    navigateTo(o) { state.calls.push({type:'navigateTo',...o}); },
    switchTab(o) { state.calls.push({type:'switchTab',...o}); },
    setNavigationBarTitle(o) { state.calls.push({type:'title',...o}); },
    showToast(o) { state.calls.push({type:'toast',...o}); },
    showModal(o) { state.calls.push({type:'modal',title:o.title}); o.success({confirm:state.modalConfirm}); },
    setClipboardData(o) { state.calls.push({type:'clipboard',data:o.data}); const fn=state.clipboardError?o.fail:o.success; if(fn)fn(); }
  };
  const modules = new Map(); let registered;
  const context = vm.createContext({wx, getApp:()=>state.app, Page:o=>{registered=o;}, Component:o=>{registered=o;},
    setTimeout:fn=>{state.timer=fn;return 1;}, clearTimeout:()=>{state.timer=null;}});
  function load(relative) {
    let filename = path.resolve(root,relative); if (!path.extname(filename)) filename += '.js';
    assert.ok(filename.startsWith(root+path.sep),'module must remain in miniprogram');
    if (modules.has(filename)) return modules.get(filename).exports;
    const module={exports:{}}; modules.set(filename,module);
    const code=fs.readFileSync(filename,'utf8');
    const factory=new vm.Script('(function(require,module,exports){\n'+code+'\n})',{filename}).runInContext(context);
    factory(request=>load(path.relative(root,path.resolve(path.dirname(filename),request))),module,module.exports);
    return module.exports;
  }
  function page(relative) {
    registered=null; load(relative); assert.ok(registered,relative+' registers Page/Component');
    const instance={data:clone(registered.data||{}),properties:{},setData(patch){Object.assign(this.data,clone(patch));}};
    const methods=registered.methods||registered;
    for(const [name,value] of Object.entries(methods)) if(typeof value==='function')instance[name]=value.bind(instance);
    return instance;
  }
  return {state,load,page,context};
}
const catalog = require(path.join(root,'data/catalog.js'));
const details = require(path.join(root,'content/data/entries.js'));
const ids = catalog.entries.map(e=>e.id);
const event = (dataset={},value) => ({currentTarget:{dataset},detail:{value}});
const validState = () => ({version:1,favorites:[ids[1]],history:[ids[2],ids[1]]});

test('catalog-detail referential completeness and fields',()=>{
  assert.equal(new Set(ids).size,ids.length); assert.equal(ids.length,catalog.meta.totalEntries);
  assert.equal(catalog.chapters.length,catalog.meta.totalChapters); same(Object.keys(details).sort(),ids.slice().sort());
  const groups=new Set(catalog.groups.map(g=>g.id)); const chapters=new Map(catalog.chapters.map(c=>[c.id,c]));
  assert.equal(groups.size,catalog.groups.length); assert.equal(chapters.size,catalog.chapters.length);
  for(const chapter of catalog.chapters){assert.ok(groups.has(chapter.groupId),chapter.id); assert.equal(chapter.count,catalog.entries.filter(e=>e.chapterId===chapter.id).length,chapter.id+' count');}
  for(const entry of catalog.entries){
    const d=details[entry.id],chapter=chapters.get(entry.chapterId); assert.ok(chapter,entry.id+' chapter');
    assert.equal(chapter.groupId,entry.groupId,entry.id+' group'); assert.equal(chapter.number,entry.chapterNumber);
    for(const key of Object.keys(entry))same(d[key],entry[key],entry.id+'.'+key);
    for(const key of ['title','summary','evidence','moneyCost','timeCost','effort','benefit','metric'])assert.ok(typeof entry[key]==='string'&&entry[key].length,entry.id+'.'+key);
    const labels=d.fields.map(f=>f.label); assert.equal(new Set(labels).size,labels.length,entry.id+' field keys');
    for(const label of ['成本','说人话','收益','证据等级','来源'])assert.ok(labels.includes(label),entry.id+' missing '+label);
    for(const field of d.fields)assert.ok(typeof field.text==='string'&&field.text.trim(),entry.id+' empty '+field.label);
    assert.equal(d.sourceUrl,chapter.sourceUrl); assert.ok(d.sourceUrl.includes('/blob/'+catalog.meta.upstreamCommit+'/'),entry.id+' source must pin commit');
    for(const link of d.sourceLinks){assert.ok(['http:','https:'].includes(new URL(link.url).protocol),entry.id+' link');assert.ok(!/[\s<>]/.test(link.url),entry.id+' malformed URL '+link.url);}
    assert.equal(new Set(d.sourceLinks.map(s=>s.url)).size,d.sourceLinks.length,entry.id+' duplicate sources');
  }
});

test('fresh storage favorites persist and history is unique, newest-first, capped at 100',()=>{
  const h=harness(),s=h.load('lib/storage.js'); same(s.read(),{version:1,favorites:[],history:[]});assert.equal(h.state.writes,0);
  assert.equal(s.toggle(ids[0]),true);assert.equal(s.toggle(ids[1]),true);assert.equal(s.toggle(ids[0]),false);same(s.read().favorites,[ids[1]]);
  for(const id of ids.slice(0,105))s.visit(id);s.visit(ids[100]);const saved=s.read();assert.equal(saved.history.length,100);assert.equal(saved.history[0],ids[100]);assert.equal(new Set(saved.history).size,100);assert.ok(!saved.history.includes(ids[0]));
  s.clearHistory();same(s.read().favorites,[ids[1]]);same(s.read().history,[]);
});

test('malformed JSON and incompatible storage schema block all mutations and preserve bytes',()=>{
  const specimens=['{broken',JSON.stringify({version:2,favorites:[],history:[]}),JSON.stringify({version:1,favorites:{},history:[]}),JSON.stringify({version:1,favorites:[],history:'bad'}),JSON.stringify([])];
  for(const raw of specimens)for(const operation of ['toggle','visit','clearHistory']){
    const h=harness(raw),s=h.load('lib/storage.js');assert.throws(()=>s[operation](ids[0]),operation+' should reject malformed storage');same(h.state.stored,raw);assert.equal(h.state.writes,0);
  }
});

test('non-string storage members are recognized as corrupted instead of overwritten',()=>{
  for(const field of ['favorites','history']){
    const bad=validState();bad[field].push({id:ids[4]});const raw=JSON.stringify(bad),h=harness(raw),s=h.load('lib/storage.js');
    assert.throws(()=>s.toggle(ids[0]),field+' malformed member should block overwrite');same(h.state.stored,raw);assert.equal(h.state.writes,0);
  }
});

test('read errors and write failures propagate without loss or success UI',()=>{
  for(const operation of ['toggle','visit','clearHistory'])for(const failure of ['readError','writeError']){
    const raw=JSON.stringify(validState()),h=harness(raw),s=h.load('lib/storage.js');h.state[failure]=true;
    assert.throws(()=>s[operation](ids[0]));same(h.state.stored,raw);assert.equal(h.state.writes,0);
  }
  const h=harness(JSON.stringify(validState())),page=h.page('content/detail/index.js');page.onLoad({id:ids[0]});page.onShow();const before=h.state.stored;h.state.writeError=true;page.favorite();
  assert.equal(page.data.isFavorite,false);same(h.state.stored,before);assert.ok(h.state.calls.some(c=>c.type==='toast'&&c.title.includes('失败')));assert.ok(!h.state.calls.some(c=>c.type==='toast'&&c.title==='已收藏'));
});

test('all detail pages load with complete actionable identity and original sources',()=>{
  const h=harness(),page=h.page('content/detail/index.js');
  for(const id of ids){page.onLoad({id});assert.equal(page.data.entry.id,id,id);assert.equal(page.data.entry.title,details[id].title);assert.ok(page.data.summary,id+' summary');assert.equal(page.data.chapter.id,details[id].chapterId);same(page.data.sources,details[id].sourceLinks);assert.equal(page.data.entry.sourceUrl,details[id].sourceUrl);assert.ok(page.onShareAppMessage().path.endsWith('?id='+encodeURIComponent(id)));}
});

test('unknown and inherited-property detail IDs produce safe not-found state',()=>{
  for(const id of ['','missing-id','c99-99','__proto__','constructor','toString','hasOwnProperty']){
    const h=harness(),page=h.page('content/detail/index.js');page.onLoad({id});assert.equal(page.data.entry,null,'id='+id+' must not be a valid entry');assert.ok(page.data.error,'id='+id+' needs not-found message');assert.equal(h.state.writes,0);assert.equal(page.onShareAppMessage().path,'/pages/home/index');
  }
});

test('detail reading remains available through storage errors',()=>{
  const h=harness('{bad'),page=h.page('content/detail/index.js');page.onLoad({id:ids[0]});page.onShow();assert.equal(page.data.entry.id,ids[0]);assert.ok(page.data.storageError);assert.equal(h.state.stored,'{bad');assert.equal(h.state.writes,0);
  const saved=h.page('pages/saved/index.js');saved.onShow();assert.ok(saved.data.error);same(saved.data.rows,[]);saved.clear();assert.equal(h.state.stored,'{bad');assert.equal(h.state.writes,0);
});

test('clear history cancellation preserves records and confirmation preserves favorites',()=>{
  const h=harness(JSON.stringify(validState())),page=h.page('pages/saved/index.js');page.onShow();const before=h.state.stored;h.state.modalConfirm=false;page.clear();assert.equal(h.state.stored,before);assert.equal(h.state.writes,0);
  h.state.modalConfirm=true;page.clear();same(h.load('lib/storage.js').read().favorites,[ids[1]]);same(h.load('lib/storage.js').read().history,[]);
});

test('group/chapter filtering and every detail breadcrumb return to the exact chapter',()=>{
  const h=harness(),library=h.page('pages/library/index.js'),detail=h.page('content/detail/index.js');library.onLoad();assert.equal(library.data.total,ids.length);assert.equal(library.data.rows.length,20);
  for(const group of catalog.groups){library.group(event({id:group.id}));assert.equal(library.data.total,catalog.entries.filter(e=>e.groupId===group.id).length);assert.ok(library.data.chapterOptions.slice(1).every(c=>c.groupId===group.id));}
  for(const chapter of catalog.chapters){
    const entry=catalog.entries.find(e=>e.chapterId===chapter.id);detail.onLoad({id:entry.id});detail.chapter();library.onShow();assert.equal(h.state.app.globalData.libraryFilter,null);assert.equal(library.data.groupId,chapter.groupId);assert.equal(library.data.chapterId,chapter.id);assert.equal(library.data.chapterOptions[library.data.chapterIndex].id,chapter.id);assert.equal(library.data.total,chapter.count);assert.ok(library.data.rows.every(e=>e.chapterId===chapter.id));
  }
  library.reset();assert.equal(library.data.total,ids.length);assert.equal(library.data.chapterIndex,0);while(library.data.hasMore)library.more();assert.equal(library.data.rows.length,ids.length);assert.equal(new Set(library.data.rows.map(e=>e.id)).size,ids.length);
});

test('zero-result filters recover and home all-navigation clears prior filters',()=>{
  const h=harness(),library=h.page('pages/library/index.js'),home=h.page('pages/home/index.js');library.onLoad();library.setData({groupId:catalog.groups[0].id,chapterId:catalog.chapters[0].id,freeOnly:true,evidence:'Z'});library.refresh();assert.equal(library.data.total,0);assert.equal(library.data.hasMore,false);same(library.data.rows,[]);
  home.all();library.onShow();assert.equal(library.data.total,ids.length);assert.equal(library.data.freeOnly,false);assert.equal(library.data.evidence,'');assert.equal(library.data.chapterId,'');
});

test('not-found recovery returns to all suggestions even when library had a prior filter',()=>{
  const h=harness(),library=h.page('pages/library/index.js'),detail=h.page('content/detail/index.js');
  library.onLoad();library.group(event({id:catalog.groups[0].id}));library.free();
  detail.onLoad({id:'nonexistent-shared-entry'});detail.explore();library.onShow();
  assert.equal(library.data.total,ids.length,'回到全部建议 must reset the existing tab filters');assert.equal(library.data.groupId,'');assert.equal(library.data.freeOnly,false);
});

test('multi-word search is AND, insensitive to case, and includes original source URLs',()=>{
  const h=harness(),page=h.page('content/search/index.js');page.onLoad({q:'睡眠'});assert.ok(page.data.total>0);const single=page.data.total;page.setData({query:'睡眠 运动'});page.run();assert.ok(page.data.total>0);assert.ok(page.data.total<=single);
  while(page.data.hasMore)page.more();for(const e of page.data.rows){const text=JSON.stringify(details[e.id]).toLowerCase();assert.ok(text.includes('睡眠')&&text.includes('运动'),e.id);}
  const candidate=ids.map(id=>details[id]).find(d=>d.sourceLinks.some(l=>l.url.includes('doi.org/'))),url=candidate.sourceLinks.find(l=>l.url.includes('doi.org/')).url;
  page.setData({query:url.toUpperCase()});page.run();while(page.data.hasMore)page.more();assert.ok(page.data.rows.some(e=>e.id===candidate.id),'source URL search must find its entry');
  page.setData({query:'绝不可能出现的搜索词__qa__'});page.run();assert.equal(page.data.total,0);assert.equal(page.data.hasMore,false);page.clear();assert.equal(page.data.searchedQuery,'');same(page.data.rows,[]);
  page.input(event({},'租房'));assert.ok(h.state.timer);page.onUnload();assert.equal(h.state.timer,null);
});

test('home navigation encoded Chinese search matches direct Chinese search and decodes once',()=>{
  for(const query of ['睡眠','睡眠 运动','省钱']){
    const h=harness(),home=h.page('pages/home/index.js');home.input(event({},query));home.search();
    const url=h.state.calls.find(c=>c.type==='navigateTo').url,rawOption=url.slice(url.indexOf('?q=')+3);
    assert.equal(rawOption,encodeURIComponent(query));
    const routed=h.page('content/search/index.js');routed.onLoad({q:rawOption});
    const direct=harness().page('content/search/index.js');direct.onLoad({q:query});
    assert.equal(routed.data.query,query);assert.equal(routed.data.searchedQuery,query);assert.ok(routed.data.total>0);assert.equal(routed.data.total,direct.data.total);same(routed.data.rows,direct.data.rows);
  }
  const page=harness().page('content/search/index.js');page.onLoad({q:encodeURIComponent('%E7%9D%A1')});
  assert.equal(page.data.query,'%E7%9D%A1','encoded-looking literal input must only be decoded once');
});

test('search entry safely preserves malformed percent input',()=>{
  for(const query of ['%','abc%ZZ','%E7%9D','睡眠 50%']){
    const page=harness().page('content/search/index.js');assert.doesNotThrow(()=>page.onLoad({q:query}));
    assert.equal(page.data.query,query);assert.equal(page.data.searchedQuery,query);assert.ok(Number.isInteger(page.data.total));assert.ok(Array.isArray(page.data.rows));
  }
});

test('copy source validates scheme and shows failure feedback',()=>{
  const h=harness(),page=h.page('content/detail/index.js');page.copy(event({url:'javascript:alert(1)'}));assert.equal(h.state.calls.length,0);
  const url=details[ids[0]].sourceUrl;page.copy(event({url}));assert.ok(h.state.calls.some(c=>c.type==='clipboard'&&c.data===url));h.state.clipboardError=true;page.copy(event({url}));assert.ok(h.state.calls.some(c=>c.type==='toast'&&c.title.includes('失败')));
});

function files(directory){return fs.readdirSync(directory,{withFileTypes:true}).flatMap(entry=>entry.isDirectory()?files(path.join(directory,entry.name)):[path.join(directory,entry.name)]);}
test('all WXML event handlers resolve and registered routes have all required files',()=>{
  const config=JSON.parse(fs.readFileSync(path.join(root,'app.json'),'utf8'));
  const routes=config.pages.concat((config.subpackages||[]).flatMap(p=>p.pages.map(r=>p.root+'/'+r)));
  for(const route of routes)for(const ext of ['js','json','wxml','wxss'])assert.ok(fs.existsSync(path.join(root,route+'.'+ext)),route+'.'+ext);
  for(const filename of files(root).filter(f=>f.endsWith('.wxml'))){const h=harness(),relative=path.relative(root,filename).replace(/\.wxml$/,'.js'),page=h.page(relative),source=fs.readFileSync(filename,'utf8');for(const match of source.matchAll(/\b(?:bind|catch)(?::)?[a-zA-Z]+\s*=\s*["']([^"']+)["']/g))assert.equal(typeof page[match[1]],'function',relative+': '+match[1]);}
});

test('all app JavaScript parses without browser or Node runtime dependencies',()=>{
  const appFiles=files(root).filter(f=>f.endsWith('.js'));
  for(const filename of appFiles){const source=fs.readFileSync(filename,'utf8');new vm.Script(source,{filename});assert.ok(!/\b(?:window|document|process|Buffer)\s*[.\[]/.test(source),path.relative(root,filename)+' non-miniapp global');assert.ok(!/require\(['"](?:node:|https?:|fs['"]|path['"])/.test(source),path.relative(root,filename)+' external dependency');}
});

const sources={};for(const filename of files(root).filter(f=>/\.(js|wxml|json)$/.test(f)))sources[path.relative(root,filename).replace(/\\/g,'/')]=crypto.createHash('sha256').update(fs.readFileSync(filename)).digest('hex');
const report={generatedAt:new Date().toISOString(),runtime:process.version,method:'Node VM with synthetic WeChat API and synthetic storage; no live device, personal data, or remote code',totals:{entries:ids.length,chapters:catalog.chapters.length,groups:catalog.groups.length,tests:results.length,passed:results.filter(r=>r.status==='pass').length,failed:results.filter(r=>r.status==='fail').length},results,limitations:['No official WeChat compiler, native WXML rendering, or device JSCore validation in this independent lane.','No independent medical/legal/financial verification of upstream content.'],sourceSHA256:sources};
fs.writeFileSync(path.join(__dirname,'independent-qa.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({totals:report.totals,failures:results.filter(r=>r.status==='fail')},null,2));
process.exitCode=report.totals.failed?1:0;
