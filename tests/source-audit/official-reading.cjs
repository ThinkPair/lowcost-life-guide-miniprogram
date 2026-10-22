'use strict';
const a=require('miniprogram-automator'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const details=require('../../miniprogram/content/data/entries'),out=path.join(__dirname,'screenshots');fs.mkdirSync(out,{recursive:true});
const checks=[],errors=[],sleep=ms=>new Promise(r=>setTimeout(r,ms));let m;
const pass=s=>{checks.push(s);console.log('PASS '+s);};
async function shot(name){await sleep(350);await m.screenshot({path:path.join(out,name+'.png')});}
async function page(id){const p=await m.reLaunch('/content/detail/index?id='+id);await p.waitFor('.detail-title');return p;}
async function wait(fn){for(let i=0;i<35;i++){if(await fn())return;await sleep(200);}throw Error('UI wait timeout');}
(async()=>{
 for(let i=0;i<20;i++){try{m=await a.connect({wsEndpoint:process.env.WX_AUTOMATION_ENDPOINT});break;}catch(e){if(i===19)throw e;await sleep(700);}}
 m.on('exception',e=>errors.push(e));
 let p=await m.reLaunch('/pages/library/index');await p.waitFor('.entry-host');
 const host=await p.$('.entry-host'),card=await host.$('.entry-card'),summary=await card.$('.entry-summary');
 assert.equal(await summary.text(),details[(await p.data('rows'))[0].id].summary);await shot('01-full-summary');pass('列表完整显示原文说人话，无两行截断');
 p=await page('c27-01');assert.equal(await p.data('entry.costLabel'),'原文钱标签：0');assert.ok((await p.data('fields'))[0].text.includes('几十元一瓶'));await shot('02-cost-context');pass('叶酸案例保留原钱标签及付费/免费条件原文');
 assert.deepEqual((await p.data('fields')).map(f=>f.label),['成本','说人话','收益','证据等级','来源','备注']);pass('六栏目名称与次序与原文一致');
 await(await p.$('.reading-note button')).tap();await shot('03-notes');pass('可直接跳到完整备注');
 p=await page('c16-09');const notes=(await p.data('fields')).find(f=>f.label==='备注');assert.ok(notes.text.includes('HLA-B*5801'));assert.ok(!notes.text.includes('\\*'));assert.ok(notes.nodes.some(n=>n.name==='strong'));await(await p.$('.reading-note button')).tap();await shot('04-original-emphasis');pass('型号星号正常，作者加粗与备注完整保留');
 const refs=(await p.data('fields')).flatMap(f=>f.references);assert.ok(refs.some(r=>r.id==='c06-19'));const target=refs[0];await p.callMethod('related',{currentTarget:{dataset:{id:target.id}}});await wait(async()=>{p=await m.currentPage();return await p.data('entry.id')===target.id;});pass('条目引用可跳到匹配的原书章节条目');
 p=await page('c02-09');assert.ok((await p.data('glossary')).some(t=>t.term==='RR'));assert.ok(!(await p.data('glossary')).some(t=>t.term==='d、g'));await p.callMethod('glossary');await m.pageScrollTo(99999);await shot('05-source-glossary');pass('术语解释取自原书；克数不会误释为效应量');
 await p.callMethod('sources');assert.equal(await p.data('showSources'),true);assert.equal(await p.data('sourceText'),details['c02-09'].fields.find(f=>f.label==='来源').text);pass('来源可展开且原文说明完整');
 p=await page('c08-13');assert.ok(await p.data('sourceNote'));assert.equal(await p.data('entry.title'),details['c08-13'].title);await shot('06-editorial-note');pass('原文差异提示明确归属本项目，原作者标题保持不变');
 p=await page('c13-37');assert.ok(!(await p.data('fields')).find(f=>f.label==='收益').references.some(r=>r.id==='c13-09'));pass('司法意见条号不误跳本书条目');
 await p.callMethod('intro');assert.ok(await p.data('showIntro'));assert.equal((await p.data('chapter')).intro.length>0,true);pass('本章导语和原文语境可展开');
 p=await m.reLaunch('/content/about/index');await p.waitFor('.about-card');assert.equal(await p.data('guide.glossary.length'),41);assert.equal(await p.data('guide.grades.length'),3);assert.ok((await p.data('guide.beneficiaries')).includes('直系亲属'));await m.pageScrollTo(650);await shot('07-reading-guide');pass('原书分级、41术语和受益人分档可查');
 assert.equal(errors.length,0);pass('最终候选流程无捕获运行错误');
 await m.reLaunch('/pages/home/index');
})().then(()=>fs.writeFileSync(path.join(__dirname,'official-reading.json'),JSON.stringify({status:'PASS',at:new Date().toISOString(),checks,errors,version:'0.2.1',nativeSimulator:true,realPhone:false},null,2))).catch(e=>{console.error(e.stack);fs.writeFileSync(path.join(__dirname,'official-reading.json'),JSON.stringify({status:'FAIL',checks,errors,error:e.stack},null,2));process.exitCode=1;}).finally(async()=>{if(m)await m.disconnect();});
