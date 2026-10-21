/* Browser-only, scale-normalized hand feature extraction. No camera pixels leave this file. */
(function (root) {
  const FINGERS = ['thumb', 'index', 'middle', 'ring', 'pinky'];
  const CHAINS = { index: [5, 6, 8], middle: [9, 10, 12], ring: [13, 14, 16], pinky: [17, 18, 20] };
  const point = (p) => [Number(p.x ?? p[0]), Number(p.y ?? p[1]), Number(p.z ?? p[2] ?? 0)];
  const distance = (a, b) => Math.hypot(a[0]-b[0], a[1]-b[1], a[2]-b[2]);
  const angle = (a,b,c) => {
    const u=a.map((v,i)=>v-b[i]), w=c.map((v,i)=>v-b[i]);
    const d=Math.hypot(...u)*Math.hypot(...w);
    if (!d) return 0;
    return Math.acos(Math.max(-1,Math.min(1,u.reduce((s,v,i)=>s+v*w[i],0)/d)))*180/Math.PI;
  };
  function extractHand(landmarks, handedness='unknown') {
    if (!Array.isArray(landmarks) || landmarks.length !== 21) return null;
    const p=landmarks.map(point), scale=Math.max(distance(p[0],p[9]),1e-5), states={};
    for (const [name, chain] of Object.entries(CHAINS)) {
      const a=angle(p[chain[0]],p[chain[1]],p[chain[2]]);
      states[name]=a>=155?'extended':a<125?'curled':'half';
    }
    const thumbSpread=distance(p[4],p[5])/scale;
    const thumbAcross=distance(p[4],p[9])/scale;
    states.thumb=thumbSpread>.95?'out':thumbAcross<.48?'across':thumbSpread<.55?'tucked':'half';
    const v1=p[5].map((v,i)=>v-p[0][i]), v2=p[17].map((v,i)=>v-p[0][i]);
    const normal=[v1[1]*v2[2]-v1[2]*v2[1],v1[2]*v2[0]-v1[0]*v2[2],v1[0]*v2[1]-v1[1]*v2[0]];
    const norm=Math.hypot(...normal)||1, nz=(handedness==='Left'?-1:1)*normal[2]/norm;
    const palmOrientation=nz>.72?'camera':nz<-.72?'away':Math.abs(nz)<.32?'side':'angled';
    return { landmarks:p, handedness, fingers:states, palmOrientation, scale,
      wrist:p[0], center:p[9], bbox:{minX:Math.min(...p.map(v=>v[0])),maxX:Math.max(...p.map(v=>v[0])),minY:Math.min(...p.map(v=>v[1])),maxY:Math.max(...p.map(v=>v[1]))} };
  }
  function extractFrame(hands=[]) {
    const extracted=hands.map(h=>extractHand(h.landmarks,h.handedness)).filter(Boolean).slice(0,2);
    let interHandDistance=null;
    if(extracted.length===2) interHandDistance=distance(extracted[0].wrist,extracted[1].wrist)/((extracted[0].scale+extracted[1].scale)/2);
    return {handCount:extracted.length,hands:extracted,interHandDistance};
  }
  root.SignSenseFeatures={FINGERS,extractHand,extractFrame,distance};
})(globalThis);
