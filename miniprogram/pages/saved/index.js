const {entryMap,decorate}=require('../../lib/catalog');const storage=require('../../lib/storage');
Page({data:{mode:'favorites',rows:[],favoritesCount:0,historyCount:0,error:''},onShow(){this.refresh();},
 refresh(){try{const s=storage.read();this.setData({rows:s[this.data.mode].map(id=>decorate(entryMap[id])).filter(Boolean),favoritesCount:s.favorites.length,historyCount:s.history.length,error:''});}catch(e){this.setData({error:'记录暂时无法读取，原数据仍保留。请勿清理微信缓存。',rows:[]});}},
 mode(e){this.setData({mode:e.currentTarget.dataset.mode});this.refresh();},
 explore(){getApp().globalData.libraryFilter={};wx.switchTab({url:'/pages/library/index'});},
 clear(){wx.showModal({title:'清空阅读足迹？',content:'只清空阅读历史，已收藏的建议会保留。',confirmText:'清空历史',success:r=>{if(r.confirm){try{storage.clearHistory();this.refresh();}catch(e){wx.showToast({title:'清空失败，原记录已保留',icon:'none'});}}}});},
 about(){wx.navigateTo({url:'/content/about/index'});}
});
