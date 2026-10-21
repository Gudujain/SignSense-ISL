// Synthetic feature vectors exercise rule wiring only; they are not captured sign data or accuracy evidence.
const test = require('node:test');
const assert = require('node:assert/strict');
require('../../src/static/js/features.js');
require('../../src/static/js/scorer.js');
const templates = require('../../src/static/data/signs.json').signs;

const sampleStates = {
  '1': {thumb:'tucked',index:'extended',middle:'curled',ring:'curled',pinky:'curled'},
  '2': {thumb:'tucked',index:'extended',middle:'extended',ring:'curled',pinky:'curled'},
  '3': {thumb:'half',index:'extended',middle:'extended',ring:'extended',pinky:'curled'},
  '4': {thumb:'tucked',index:'extended',middle:'extended',ring:'extended',pinky:'extended'},
  '5': {thumb:'out',index:'extended',middle:'extended',ring:'extended',pinky:'extended'}
};

for (const label of ['1','2','3','4','5']) {
  test(`rule scorer recognizes a synthetic matching feature vector for ${label}`, () => {
    const hand={fingers:sampleStates[label],wrist:[.5,.8,0],bbox:{minX:.2,maxX:.8,minY:.1,maxY:.9}};
    const frames=Array.from({length:15},()=>({handCount:1,hands:[hand]}));
    const result=globalThis.SignSenseScorer.scoreWindow(frames,templates.find(t=>t.label===label),templates);
    assert.equal(result.outcome,'got_it');
    assert.equal(result.candidate,label);
  });
}

test('feature extractor rejects malformed hand landmarks', () => {
  assert.equal(globalThis.SignSenseFeatures.extractHand([[0,0,0]],'Left'),null);
});

test('empty window is a system visibility case', () => {
  const result=globalThis.SignSenseScorer.scoreWindow([{handCount:0,hands:[]}],templates[0],templates);
  assert.equal(result.outcome,'not_seen');
  assert.equal(result.failure_source,'system');
});

test('stable window selector returns the requested bounded window', () => {
  const frames=Array.from({length:25},(_,i)=>({hands:[{landmarks:[[i/100,0,0]]}]}));
  assert.equal(globalThis.SignSenseScorer.chooseStableWindow(frames,15).length,15);
});
