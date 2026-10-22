Component({properties:{entry:{type:Object,value:null}},methods:{open(){const e=this.properties.entry;if(e)wx.navigateTo({url:'/content/detail/index?id='+encodeURIComponent(e.id)});}}});
