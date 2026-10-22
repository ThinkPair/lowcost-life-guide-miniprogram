const a=require('miniprogram-automator'),fs=require('fs'),path=require('path');
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const out=path.resolve(process.env.LIFE_CAPTURE_DIR||path.join(__dirname,'visual-refresh'));
fs.mkdirSync(out,{recursive:true});
(async()=>{let m;for(let i=0;i<20;i++){try{m=await a.connect({wsEndpoint:process.env.WX_AUTOMATION_ENDPOINT});break;}catch(e){if(i===19)throw e;await sleep(600);}}
try{for(const [name,url,selector] of [
 ['01-home','/pages/home/index','.hero'],
 ['02-library','/pages/library/index','.group-tabs'],
 ['03-detail','/content/detail/index?id=c02-09','.detail-title'],
 ['04-saved','/pages/saved/index','.saved-tabs'],
 ['05-search','/content/search/index?q='+encodeURIComponent('租房'),'.search-count'],
 ['06-about','/content/about/index','.about-card']]){
 const p=await m.reLaunch(url);await p.waitFor(selector);await sleep(450);
 await m.screenshot({path:path.join(out,name+'.png')});
 if(name==='01-home'){await m.pageScrollTo(620);await sleep(350);await m.screenshot({path:path.join(out,'01-home-scroll.png')});}
 if(name==='03-detail'){await m.pageScrollTo(600);await sleep(350);await m.screenshot({path:path.join(out,'03-detail-scroll.png')});}
 if(name==='03-detail'||name==='06-about'){await m.pageScrollTo(99999);await sleep(350);await m.screenshot({path:path.join(out,name+'-bottom.png')});}
 }
 const home=await m.reLaunch('/pages/home/index');await home.waitFor('.hero-action');await(await home.$('.hero-action')).tap();
 let target;for(let i=0;i<30;i++){target=await m.currentPage();if(target.path==='pages/library/index')break;await sleep(200);}
 if(target.path!=='pages/library/index'||await target.data('total')!==667)throw Error('Home primary action did not open full library');
 fs.writeFileSync(path.join(out,'capture.json'),JSON.stringify({at:new Date().toISOString(),screenshots:10,pages:6,heroAction:'PASS',native:true,realPhone:false},null,2));
 await m.reLaunch('/pages/home/index');console.log('Captured 10 official simulator screenshots; home primary action passed. '+out);
}finally{await m.disconnect();}})().catch(e=>{console.error(e.stack);process.exitCode=1;});
