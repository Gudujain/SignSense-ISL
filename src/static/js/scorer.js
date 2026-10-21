/* Temporal consensus and transparent rules. Internal score is never shown as probability. */
(function (root) {
  const FINGERS=['thumb','index','middle','ring','pinky'];
  const thumbMatch=(expected,actual)=>expected==='curled'?['tucked','across','curled'].includes(actual):expected==='extended'?['out','extended'].includes(actual):expected===actual;
  function majority(values) {
    const counts=new Map(); values.filter(v=>v!=null).forEach(v=>counts.set(v,(counts.get(v)||0)+1));
    return [...counts].sort((a,b)=>b[1]-a[1])[0]?.[0] ?? null;
  }
  function chooseStableWindow(frames,size=15) {
    if(frames.length<=size)return frames.slice();
    let best=frames.slice(0,size),bestJitter=Infinity;
    for(let start=0;start<=frames.length-size;start++){
      const window=frames.slice(start,start+size);let jitter=0,steps=0;
      for(let i=1;i<window.length;i++){
        const a=window[i-1]?.hands||[],b=window[i]?.hands||[];
        if(a.length!==b.length){jitter+=2;steps++;continue;}
        for(let h=0;h<a.length;h++){
          const p=a[h].landmarks?.[0],q=b[h].landmarks?.[0];
          if(p&&q){jitter+=Math.hypot(p[0]-q[0],p[1]-q[1],p[2]-q[2]);steps++;}
        }
      }
      const score=steps?jitter/steps:Infinity;
      if(score<bestJitter){bestJitter=score;best=window;}
    }
    return best;
  }
  function classifyCandidate(frames,templates) {
    const first=frames.find(f=>f?.hands?.length)?.hands?.[0]; if(!first)return null;
    let best=null,bestErrors=Infinity;
    for(const t of templates.filter(x=>x.handCount===1 && x.hands?.[0]?.fingers)) {
      let errors=0,compared=0;
      for(const finger of FINGERS){const expected=t.hands[0].fingers[finger];if(expected==='unknown')continue;compared++;if(finger==='thumb'?!thumbMatch(expected,first.fingers[finger]):expected!==first.fingers[finger])errors++;}
      if(compared && errors<bestErrors){best=t.label;bestErrors=errors;}
    }
    return bestErrors===0?best:null;
  }
  function scoreWindow(frames,template,templates=[]) {
    const usable=frames.filter(f=>f&&Number.isFinite(f.handCount));
    if(!usable.length || usable.every(f=>f.handCount===0)) return {outcome:'not_seen',failure_source:'system',perFingerErrors:[],hint:'We could not see a hand. Check your camera setup and try again.',confidence:0,candidate:null,stableFrames:0};
    const expectedHands=template?.handCount ?? 1;
    const handCounts=usable.map(f=>f.handCount), modeHands=Number(majority(handCounts))||0;
    const observed=usable.filter(f=>f.handCount>0);
    const errors=[];
    if(modeHands!==expectedHands) errors.push({hand:'both',finger:null,expected:expectedHands,observed:modeHands,reason:'hand_count'});
    const required=template?.hands||[];
    for(let h=0;h<Math.min(expectedHands,modeHands);h++) {
      const hand=observed.map(f=>f.hands[h]).filter(Boolean); if(!hand.length)continue;
      const role=required[h]||{}, expected=role.fingers||{};
      for(const finger of FINGERS){const want=expected[finger];if(!want||want==='unknown')continue;
        const got=majority(hand.map(x=>x.fingers?.[finger]));
        if(got && !(finger==='thumb'?thumbMatch(want,got):want===got)) errors.push({hand:role.role||String(h+1),finger,expected:want,observed:got});
      }
    }
    const candidate=classifyCandidate(usable,templates);
    const stableFrames=Math.max(0,usable.length-1);
    const constraints=required.reduce((n,h)=>n+Object.values(h.fingers||{}).filter(v=>v&&v!=='unknown').length,0);
    let outcome='try_again',hint='Watch the steps again, then try once more.';
    if(errors.length===1 && errors[0].finger){outcome='almost';hint=`Check your ${errors[0].finger} against the reference.`;}
    else if(errors.length===0 && constraints>0 && candidate===String(template.label)){outcome='got_it';hint='Your hand shape matched the reference cues.';}
    else if(errors.length===0 && constraints===0){outcome='try_again';hint='This sign needs reviewed hand cues before it can be checked.';}
    else if(errors.length>0 && errors[0].reason==='hand_count')hint=expectedHands===2?'Show both hands inside the guide.':'Keep one hand in view for this reference.';
    const agreement=observed.length?observed.filter(f=>f.handCount===modeHands).length/usable.length:0;
    const confidence=usable.length?Math.max(0,Math.min(1,agreement*(1-errors.length/Math.max(1,constraints+errors.length)))):0;
    return {outcome,failure_source:'learner',perFingerErrors:errors,hint,confidence,candidate,stableFrames,handCount:modeHands};
  }
  root.SignSenseScorer={scoreWindow,classifyCandidate,majority,chooseStableWindow};
})(globalThis);
