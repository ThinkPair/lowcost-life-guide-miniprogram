const a=require('miniprogram-automator');
const assert=require('node:assert/strict');const fs=require('node:fs');const path=require('node:path');
const root=path.resolve(__dirname,'..'),out=path.join(__dirname,'official');fs.mkdirSync(out,{recursive:true});
const {catalog}=require('../miniprogram/lib/catalog');
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const checks=[],errors=[];let m;
const pass=s=>{checks.push(s);console.log('PASS',s);};
async function until(fn){for(let i=0;i<45;i++){if(await fn())return;await sleep(250);}throw Error('UI wait timed out');}
async function shot(name){await sleep(450);await m.screenshot({path:path.join(out,name+'.png')});}
(async()=>{
 for(let i=0;i<12;i++){try{m=await a.connect({wsEndpoint:process.env.WX_AUTOMATION_ENDPOINT||'ws://127.0.0.1:9431'});break;}catch(e){if(i===11)throw e;await sleep(800);}}m.on('exception',e=>errors.push(e));
 let p=await m.reLaunch('/pages/home/index');await p.waitFor('.hero');await shot('01-home');
 assert.equal(await p.data('meta.totalEntries'),667);assert.equal((await p.$$('.group-item')).length,8);pass('首页展示完整条目数与八个主题');
 await (await p.$$('.group-item'))[2].tap();await until(async()=>{p=await m.currentPage();return p.path==='pages/library/index';});
 assert.equal(await p.data('groupId'),'money');assert.equal(await p.data('total'),catalog.entries.filter(e=>e.groupId==='money').length);pass('真实点击主题进入对应分类');
 await (await p.$('.free-filter')).tap();assert.ok((await p.data('rows')).every(e=>e.moneyCost==='0'));pass('不花钱筛选只包含原文钱=0条目');
 await shot('02-library');
 const first=(await p.data('rows'))[0];await p.waitFor('.entry-host');await (await (await p.$('.entry-host')).$('.entry-card')).tap();
 await until(async()=>{p=await m.currentPage();return p.path==='content/detail/index';});await p.waitFor('.detail-title');
 assert.equal(await p.data('entry.id'),first.id);assert.ok(await p.data('notes'));assert.ok((await p.data('body')).some(f=>f.label==='成本'));pass('建议可打开，适用限制与成本可读');
 await shot('03-detail');
 const wasSaved=await p.data('isFavorite');await (await p.$('.save-button')).tap();await until(async()=>await p.data('isFavorite')===!wasSaved);pass('详情收藏按钮状态随保存结果更新');
 if(wasSaved){await(await p.$('.save-button')).tap();await until(async()=>await p.data('isFavorite')===true);}
 p=await m.switchTab('/pages/saved/index');await p.waitFor('.saved-tabs');assert.ok((await p.data('rows')).some(e=>e.id===first.id));await shot('04-saved');pass('收藏页可读回实际模拟器存储');
 p=await m.reLaunch('/content/detail/index?id='+first.id);await p.waitFor('.detail-title');assert.equal(await p.data('isFavorite'),true);pass('重进页面仍保留收藏，未使用存储mock');
 await (await p.$('.breadcrumb')).tap();await until(async()=>{p=await m.currentPage();return p.path==='pages/library/index';});assert.equal(await p.data('chapterId'),first.chapterId);assert.ok((await p.data('rows')).every(e=>e.chapterId===first.chapterId));pass('详情章节入口准确返回单章筛选');
 p=await m.navigateTo('/content/search/index?q='+encodeURIComponent('租房'));await p.waitFor('.search-count');assert.ok(await p.data('total'));await shot('05-search');pass('搜索租房命中原文');
 const input=await p.$('input');await input.input('zz_no_match_987');await until(async()=>await p.data('searchedQuery')==='zz_no_match_987');assert.equal(await p.data('total'),0);await shot('06-empty-search');pass('搜索无结果提供恢复入口');
 await (await p.$('.secondary-button')).tap();await until(async()=>await p.data('searchedQuery')==='');pass('清除查询返回搜索起点');
 await input.input('睡眠 风险');await until(async()=>await p.data('searchedQuery')==='睡眠 风险');assert.ok(await p.data('total'));pass('全文多关键词检索可用');
 p=await m.reLaunch('/content/detail/index?id=c02-09');await p.waitFor('.detail-title');await (await p.$('.source-block .fold-heading')).tap();await until(async()=>await p.data('showSources'));assert.ok((await p.data('sources')).length);await m.pageScrollTo(1800);await shot('07-sources');pass('条目完整出处与可复制原文入口可展开');
 p=await m.reLaunch('/content/about/index');await p.waitFor('.about-card');await shot('08-about');pass('来源署名、作者分级与本地存储说明可访问');
 p=await m.reLaunch('/content/detail/index?id=unknown');await p.waitFor('.empty');assert.ok(await p.data('error'));pass('陌生分享参数有明确错误与返回路径');
 p=await m.switchTab('/pages/library/index');await p.callMethod('reset');assert.equal(await p.data('rows.length'),20);await p.callMethod('more');assert.equal(await p.data('rows.length'),40);pass('长列表分页可加载，不一次渲染667条');
 await p.callMethod('evidence',{currentTarget:{dataset:{value:'A'}}});assert.equal(await p.data('total'),catalog.entries.filter(e=>e.evidence.charAt(0)==='A').length);pass('证据筛选保留带争议的A级条目');
 p=await m.reLaunch('/pages/home/index');await p.waitFor('.hero');await shot('09-home-final');
 assert.equal(errors.length,0);pass('本轮官方模拟器流程无捕获运行错误');
})().then(()=>{fs.writeFileSync(path.join(out,'result.json'),JSON.stringify({status:'PASS',at:new Date().toISOString(),checks,errors,appId:'touristappid',storage:'actual simulator wx local storage; no storage mocks',realPhone:'not_tested',previewGenerated:false,uploaded:false,published:false},null,2));}).catch(e=>{console.error(e.stack);fs.writeFileSync(path.join(out,'result.json'),JSON.stringify({status:'FAIL',checks,errors,error:e.stack},null,2));process.exitCode=1;}).finally(async()=>{if(m)await m.disconnect();});
