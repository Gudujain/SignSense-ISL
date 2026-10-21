/* Frames are sent only to the local Flask app for in-memory hand tracking. */
(function(root){
  async function create(video){
    const ready=await fetch('/api/hand-tracker/ready');
    if(!ready.ok){
      let detail='The local hand tracker could not start.';
      try{detail=(await ready.json()).error||detail;}catch(_){}
      throw new Error(detail);
    }
    const canvas=document.createElement('canvas');
    canvas.width=640;canvas.height=480;
    const context=canvas.getContext('2d',{alpha:false});
    let timestamp=0;
    return {async detect(){
      if(!video?.videoWidth)return {hands:[],timestamp:performance.now()};
      const ratio=Math.min(canvas.width/video.videoWidth,canvas.height/video.videoHeight);
      const width=Math.max(2,Math.round(video.videoWidth*ratio));
      const height=Math.max(2,Math.round(video.videoHeight*ratio));
      context.fillStyle='#000';context.fillRect(0,0,canvas.width,canvas.height);
      context.drawImage(video,(canvas.width-width)/2,(canvas.height-height)/2,width,height);
      const response=await fetch('/api/hand-tracker/frame',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({image:canvas.toDataURL('image/jpeg',.72)})});
      if(!response.ok)throw new Error(`Local hand tracker returned ${response.status}`);
      const result=await response.json();
      timestamp=performance.now();
      return {hands:Array.isArray(result.hands)?result.hands:[],timestamp};
    },close(){}};
  }
  root.SignSenseTracker={create,version:'mediapipe-python-local-hand-landmarker'};
})(globalThis);
