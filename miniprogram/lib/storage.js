const {entryMap} = require('./catalog');
const KEY = 'low-cost-life-guide.v1';
function normalize(raw) {
  if (raw === '' || raw === undefined || raw === null) return {version:1,favorites:[],history:[]};
  const data = typeof raw === 'string' ? JSON.parse(raw) : raw;
  if (!data || data.version !== 1 || !Array.isArray(data.favorites) || !Array.isArray(data.history)) throw Error('本地记录格式异常，原记录已保留');
  if (data.favorites.some(id=>typeof id!=='string') || data.history.some(id=>typeof id!=='string')) throw Error('本地记录格式异常，原记录已保留');
  const clean = list => list.filter((id,i) => typeof id === 'string' && entryMap[id] && list.indexOf(id) === i);
  return {version:1,favorites:clean(data.favorites),history:clean(data.history).slice(0,100)};
}
function read() { return normalize(wx.getStorageSync(KEY)); }
function save(state) { wx.setStorageSync(KEY,JSON.stringify(normalize(state))); }
function toggle(id) {
  if (!entryMap[id]) throw Error('没有找到这条建议');
  const state = read(), exists = state.favorites.indexOf(id) !== -1;
  state.favorites = exists ? state.favorites.filter(x=>x!==id) : [id].concat(state.favorites);
  save(state); return !exists;
}
function visit(id) {
  if (!entryMap[id]) return;
  const state=read(); state.history=[id].concat(state.history.filter(x=>x!==id)).slice(0,100); save(state);
}
function clearHistory() { const state=read(); state.history=[]; save(state); }
module.exports={KEY,normalize,read,toggle,visit,clearHistory};
