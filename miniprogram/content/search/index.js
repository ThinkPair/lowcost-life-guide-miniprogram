const details=require('../data/entries');const {catalog,decorate,chapterMap}=require('../../lib/catalog');
const searchable=catalog.entries.map(e=>({entry:e,text:[e.title,e.summary,(chapterMap[e.chapterId]||{}).title].concat((details[e.id].fields||[]).map(f=>f.text)).join(' ').toLowerCase()}));
function search(query){const terms=String(query||'').trim().toLowerCase().split(/\s+/).filter(Boolean);if(!terms.length)return [];return searchable.filter(row=>terms.every(t=>row.text.indexOf(t)!==-1)).map(row=>row.entry);}
Page({data:{query:'',searchedQuery:'',rows:[],total:0,hasMore:false,hot:['睡眠','租房','省钱','社保','手机','拖延','运动','工作']},
 onLoad(options){let q=String((options||{}).q||'');try{q=decodeURIComponent(q);}catch(e){}this.setData({query:q.slice(0,80)});this.run();},
 input(e){this.setData({query:e.detail.value});clearTimeout(this._timer);this._timer=setTimeout(()=>this.run(),260);},
 run(){clearTimeout(this._timer);const q=this.data.query.trim();this._list=search(q);this._limit=20;this.setData({searchedQuery:q});this.showRows();},
 showRows(){this.setData({rows:this._list.slice(0,this._limit).map(decorate),total:this._list.length,hasMore:this._limit<this._list.length});},
 hot(e){this.setData({query:e.currentTarget.dataset.q});this.run();},clear(){this.setData({query:''});this.run();},
 more(){if(this.data.hasMore){this._limit+=20;this.showRows();}},onReachBottom(){this.more();},onUnload(){clearTimeout(this._timer);}
});
