const {catalog}=require('../../lib/catalog');
const sourceGuide=require('../../data/reading-guide');
const guide=Object.assign({},sourceGuide,{gradeNotes:sourceGuide.gradeNotes.map(text=>text.replace(/说人话/g,'解读'))});
Page({data:{guide,meta:Object.assign({},catalog.meta,{version:require('../../lib/version')})},copy(e){const url=e.currentTarget.dataset.url;if(!/^https?:\/\//.test(url||''))return;wx.setClipboardData({data:url,success(){wx.showToast({title:'链接已复制',icon:'none'});}});}});
