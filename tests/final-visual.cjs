const a=require('miniprogram-automator'),fs=require('fs'),path=require('path'),assert=require('assert/strict');
const out=path.join(__dirname,'official'),sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{let m;for(let i=0;i<12;i++){try{m=await a.connect({wsEndpoint:process.env.WX_AUTOMATION_ENDPOINT});break;}catch(e){if(i===11)throw e;await sleep(800);}}
try{
let p=await m.reLaunch('/pages/saved/index');await p.waitFor('.shelf-stamp');await sleep(400);await m.screenshot({path:path.join(out,'04-saved.png')});
p=await m.reLaunch('/content/about/index');await p.waitFor('.about-card');await sleep(400);await m.screenshot({path:path.join(out,'08-about.png')});
p=await m.reLaunch('/pages/home/index');await p.waitFor('.hero');assert.equal(await p.data('meta.totalEntries'),667);await sleep(400);await m.screenshot({path:path.join(out,'09-home-final.png')});
const file=path.join(out,'result.json'),r=JSON.parse(fs.readFileSync(file));r.finalPresentation={checkedAt:new Date().toISOString(),status:'PASS',changes:'Only bookshelf stamp line layout and attribution wording changed after flow checks; saved/about/home recompiled and captured.'};fs.writeFileSync(file,JSON.stringify(r,null,2));console.log('Final saved/about/home pages recompiled and captured.');
}finally{await m.disconnect();}})().catch(e=>{console.error(e);process.exitCode=1;});
