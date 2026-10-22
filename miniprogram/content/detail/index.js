const details=require('../data/entries');const {catalog,decorate,chapterMap}=require('../../lib/catalog');const storage=require('../../lib/storage');
const reading=require('../../lib/reading');
const sourceNotes=require('../../data/source-notes');
Page({
 data:{entry:null,chapter:null,summary:'',notes:'',body:[],fields:[],sources:[],sourceText:'',glossary:[],isFavorite:false,error:'',storageError:'',showIntro:false,showSources:false,showGlossary:false,syncedAt:catalog.meta.syncedAt},
 onLoad(options){
  const id=String((options||{}).id||'');const d=Object.prototype.hasOwnProperty.call(details,id)?details[id]:null;if(!d){this.setData({error:'这条建议暂时找不到，回到全部建议重新选择。'});return;}
  const fields=Array.isArray(d.fields)?d.fields:[];const textOf=label=>fields.filter(f=>f.label===label).map(f=>f.text).join('\n\n');
  const chapter=chapterMap[d.chapterId]||{};
  this.setData({sourceNote:sourceNotes[id]||''});
  this.setData({entry:Object.assign({},decorate(d),{sourceUrl:d.sourceUrl,entrySourceUrl:d.entrySourceUrl}),chapter:Object.assign({},chapter,{nodes:reading.nodes(chapter.intro,chapter.introEmphasis),references:reading.references(chapter.intro,d.chapterNumber,d.id)}),summary:textOf('说人话')||d.summary,notes:textOf('备注'),sourceText:textOf('来源'),body:fields.filter(f=>['说人话','备注','来源','证据等级'].indexOf(f.label)===-1),fields:fields.map(f=>Object.assign({},f,{displayLabel:f.label==='说人话'?'解读':f.label,nodes:reading.nodes(f.text,f.emphasis),references:f.label==='来源'?[]:reading.references(f.text,d.chapterNumber,d.id)})),glossary:reading.glossary(fields.filter(f=>f.label!=='来源').map(f=>f.text).join('\n')),sources:d.sourceLinks||[],showIntro:false,showSources:false,showGlossary:false});
  wx.setNavigationBarTitle({title:'第 '+d.chapterNumber+' 章 · 建议 '+d.number});
  try{storage.visit(id);}catch(e){this.setData({storageError:'阅读记录未能保存；正文仍可正常查看。'});}
 },
 onShow(){if(!this.data.entry)return;try{this.setData({isFavorite:storage.read().favorites.indexOf(this.data.entry.id)!==-1});}catch(e){this.setData({storageError:'收藏暂时不可读取；原记录已保留。'});}},
 favorite(){if(!this.data.entry)return;try{const value=storage.toggle(this.data.entry.id);this.setData({isFavorite:value,storageError:''});wx.showToast({title:value?'已收藏':'已取消收藏',icon:'none'});}catch(e){wx.showToast({title:'保存失败，请保留原记录重试',icon:'none'});}},
 intro(){this.setData({showIntro:!this.data.showIntro});},sources(){this.setData({showSources:!this.data.showSources});},
 glossary(){this.setData({showGlossary:!this.data.showGlossary});},
 related(e){const id=e.currentTarget.dataset.id;if(!Object.prototype.hasOwnProperty.call(details,id))return;wx.navigateTo({url:'/content/detail/index?id='+encodeURIComponent(id)});},
 notes(){wx.pageScrollTo({selector:'#original-notes',duration:250});},
 copy(e){const url=e.currentTarget.dataset.url;if(typeof url!=='string'||!/^https?:\/\//i.test(url))return;wx.setClipboardData({data:url,success(){wx.showToast({title:'已复制，可在浏览器打开',icon:'none'});},fail(){wx.showToast({title:'复制失败，请稍后重试',icon:'none'});}});},
 chapter(){if(!this.data.chapter)return;getApp().globalData.libraryFilter={groupId:this.data.chapter.groupId,chapterId:this.data.chapter.id};wx.switchTab({url:'/pages/library/index'});},
 explore(){getApp().globalData.libraryFilter={};wx.switchTab({url:'/pages/library/index'});},about(){wx.navigateTo({url:'/content/about/index'});},
 onShareAppMessage(){const e=this.data.entry;return e?{title:e.title+'｜低成本生活指南',path:'/content/detail/index?id='+encodeURIComponent(e.id)}:{title:'低成本生活指南',path:'/pages/home/index'};}
});
