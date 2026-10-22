const catalog = require('../data/catalog');
const sourceNotes = require('../data/source-notes');
const entryMap = Object.create(null), chapterMap = Object.create(null), groupMap = Object.create(null);
catalog.chapters.forEach(c => { chapterMap[c.id] = c; });
catalog.groups.forEach(g => { groupMap[g.id] = g; });
catalog.entries.forEach(e => { entryMap[e.id] = e; });
function decorate(e) {
  if (!e) return null;
  const chapter = chapterMap[e.chapterId] || {}, group = groupMap[e.groupId] || {};
  return Object.assign({}, e, {
    chapterTitle: chapter.title || '', groupName: group.name || '',
    hasSourceNote: !!sourceNotes[e.id],
    costLabel: '原文钱标签：' + e.moneyCost,
    displayNumber: String(e.number).padStart(2, '0')
  });
}
function filter(options) {
  const o = options || {};
  return catalog.entries.filter(e => (!o.groupId || e.groupId === o.groupId) && (!o.chapterId || e.chapterId === o.chapterId) && (!o.freeOnly || e.moneyCost === '0') && (!o.evidence || String(e.evidence).charAt(0) === o.evidence));
}
module.exports = {catalog,entryMap,chapterMap,groupMap,decorate,filter};
