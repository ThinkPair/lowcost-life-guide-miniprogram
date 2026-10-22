const guide=require('../data/reading-guide');
const {entryMap}=require('./catalog');
function nodes(text,emphasis){
  const value=String(text||''),marks=(emphasis||[]).filter(mark=>Number.isInteger(mark.start)&&Number.isInteger(mark.end)&&mark.start>=0&&mark.end>mark.start&&mark.end<=value.length).slice();
  marks.sort((a,b)=>a.start-b.start);let cursor=0;const result=[];
  marks.forEach(mark=>{if(mark.start<cursor)return;if(mark.start>cursor)result.push({type:'text',text:value.slice(cursor,mark.start)});result.push({name:'strong',attrs:{style:'font-weight:650;color:#29241F'},children:[{type:'text',text:value.slice(mark.start,mark.end)}]});cursor=mark.end;});
  if(cursor<value.length)result.push({type:'text',text:value.slice(cursor)});
  return result;
}
function references(text,chapterNumber,currentId){
  const value=String(text||''),result=[],seen={};
  const pattern=/(?:第\s*(\d+)\s*[节章]\s*第|本[节章]\s*第|见\s*第)\s*(\d+(?:\s*[、，]\s*\d+)*)\s*条/g;
  let match;while((match=pattern.exec(value))){if(match[0].indexOf('见')===0&&value[match.index-1]==='意')continue;const chapter=Number(match[1]||chapterNumber);match[2].split(/[、，]/).forEach(number=>{const id='c'+String(chapter).padStart(2,'0')+'-'+String(Number(number)).padStart(2,'0'),entry=entryMap[id];if(entry&&id!==currentId&&!seen[id]){seen[id]=true;result.push({id,title:entry.title,location:'第 '+chapter+' 节 · 第 '+Number(number)+' 条'});}});}
  return result;
}
function glossary(text){
  return guide.glossary.filter(item=>item.term.split('、').some(term=>{
    // Single-letter symbols may be units or locally defined variables. Keep
    // their original definitions in the full glossary; do not auto-label them.
    if(term==='d'||term==='g'||term==='r')return false;
    if(/^[A-Za-z0-9%. ]+$/.test(term)){const escaped=term.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');return new RegExp('(^|[^A-Za-z])'+escaped+'(?=$|[^A-Za-z])').test(text);}
    return text.indexOf(term)!==-1;
  }));
}
module.exports={nodes,references,glossary,guide};
