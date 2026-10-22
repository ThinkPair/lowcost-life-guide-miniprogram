const {catalog,decorate,entryMap}=require('../../lib/catalog');
const storage=require('../../lib/storage');
Page({
  data:{meta:catalog.meta,groups:catalog.groups,query:'',recent:null,featured:[],savedCount:0,storageError:''},
  onLoad(){
    const picks=catalog.entries.filter(e=>[3,4,5,20].indexOf(e.chapterNumber)!==-1 && e.moneyCost==='0');
    this.setData({featured:(picks.length?picks:catalog.entries).slice(0,3).map(decorate)});
  },
  onShow(){try{const s=storage.read();this.setData({savedCount:s.favorites.length,recent:decorate(entryMap[s.history[0]]),storageError:''});}catch(e){this.setData({storageError:'本地记录暂时无法读取，阅读仍可使用。'});}},
  input(e){this.setData({query:e.detail.value});},
  search(){wx.navigateTo({url:'/content/search/index?q='+encodeURIComponent(this.data.query.trim())});},
  quickSearch(e){wx.navigateTo({url:'/content/search/index?q='+encodeURIComponent(e.currentTarget.dataset.q)});},
  group(e){getApp().globalData.libraryFilter={groupId:e.currentTarget.dataset.id};wx.switchTab({url:'/pages/library/index'});},
  all(){getApp().globalData.libraryFilter={};wx.switchTab({url:'/pages/library/index'});},
  saved(){wx.switchTab({url:'/pages/saved/index'});},
  recent(){if(this.data.recent)wx.navigateTo({url:'/content/detail/index?id='+encodeURIComponent(this.data.recent.id)});},
  about(){wx.navigateTo({url:'/content/about/index'});},
  onShareAppMessage(){return {title:'低成本生活指南｜更少的成本，更好的日常',path:'/pages/home/index'};}
});
