const {catalog,filter,decorate}=require('../../lib/catalog');
Page({
 data:{groups:catalog.groups,chapters:catalog.chapters,groupId:'',chapterId:'',chapterIndex:0,chapterOptions:[{id:'',title:'全部章节'}].concat(catalog.chapters),freeOnly:false,evidence:'',rows:[],total:0,hasMore:false},
 onLoad(){this.refresh();},
 onShow(){const f=getApp().globalData.libraryFilter;if(f){getApp().globalData.libraryFilter=null;this.setData({groupId:f.groupId||'',freeOnly:false,evidence:''});this.resetChapters();if(f.chapterId){const n=this.data.chapterOptions.findIndex(c=>c.id===f.chapterId);if(n>0)this.setData({chapterId:f.chapterId,chapterIndex:n});}this.refresh();}},
 resetChapters(){const chapters=catalog.chapters.filter(c=>!this.data.groupId||c.groupId===this.data.groupId);this.setData({chapterOptions:[{id:'',title:'全部章节'}].concat(chapters),chapterIndex:0,chapterId:''});},
 group(e){this.setData({groupId:e.currentTarget.dataset.id||''});this.resetChapters();this.refresh();},
 chapter(e){const n=Number(e.detail.value);const c=this.data.chapterOptions[n];this.setData({chapterId:c?c.id:'',chapterIndex:n});this.refresh();},
 free(){this.setData({freeOnly:!this.data.freeOnly});this.refresh();},
 evidence(e){const v=e.currentTarget.dataset.value;this.setData({evidence:this.data.evidence===v?'':v});this.refresh();},
 refresh(){this._list=filter(this.data);this._limit=20;this.showRows();},
 showRows(){this.setData({rows:this._list.slice(0,this._limit).map(decorate),total:this._list.length,hasMore:this._limit<this._list.length});},
 onReachBottom(){this.more();},more(){if(this.data.hasMore){this._limit+=20;this.showRows();}},
 reset(){this.setData({groupId:'',chapterId:'',freeOnly:false,evidence:''});this.resetChapters();this.refresh();},
 search(){wx.navigateTo({url:'/content/search/index'});},about(){wx.navigateTo({url:'/content/about/index'});}
});
