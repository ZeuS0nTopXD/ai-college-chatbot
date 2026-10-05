(async () => {
 const canvas=document.getElementById('neural-brain'), toggle=document.getElementById('motion-toggle');
 const gl=canvas.getContext('webgl',{alpha:true,antialias:true});
 if(!gl){canvas.replaceWith(Object.assign(document.createElement('p'),{textContent:'VSIT Â· Connected intelligence'}));toggle.hidden=true;return;}
 const vertex=`attribute vec3 position; attribute vec3 normal; uniform mat4 rotation; uniform float aspect; varying vec3 n; varying vec3 p; void main(){ vec4 q=rotation*vec4(position,1.); n=mat3(rotation)*normal; p=q.xyz; float d=3.8-q.z; gl_Position=vec4(q.x*2.5/aspect,q.y*2.5,-q.z*.1,d); }`;
 const fragment=`precision mediump float; varying vec3 n; varying vec3 p; void main(){vec3 N=normalize(n); float diffuse=max(dot(N,normalize(vec3(-.6,.9,1.))),0.); float rim=pow(1.-abs(N.z),3.); float shade=.48+.43*diffuse; gl_FragColor=vec4(vec3(shade*.96,shade*.96,shade*.92)+rim*.1,1.);}`;
 function shader(type,source){const s=gl.createShader(type);gl.shaderSource(s,source);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw Error(gl.getShaderInfoLog(s));return s;}
 const program=gl.createProgram();gl.attachShader(program,shader(gl.VERTEX_SHADER,vertex));gl.attachShader(program,shader(gl.FRAGMENT_SHADER,fragment));gl.linkProgram(program);gl.useProgram(program);
 // Imported Z-Anatomy / BodyParts3D mesh, CC BY-SA 4.0; see assets/brain/CREDITS.txt.
 let data;
 try {
  const response=await fetch('assets/brain/brain.bin');
  if(!response.ok)throw new Error('Model unavailable');
  data=new Int16Array(await response.arrayBuffer());
  if(!data.length||data.length%6)throw new Error('Invalid model');
 } catch(error) {
  canvas.replaceWith(Object.assign(document.createElement('p'),{textContent:'VSIT · Connected intelligence'}));
  toggle.hidden=true;return;
 }
 const vertexCount=data.length/6;
 const buffer=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,buffer);gl.bufferData(gl.ARRAY_BUFFER,data,gl.STATIC_DRAW);
 for(const [name,offset] of [['position',0],['normal',6]]){
  const loc=gl.getAttribLocation(program,name);gl.enableVertexAttribArray(loc);gl.vertexAttribPointer(loc,3,gl.SHORT,true,12,offset);
 }
 gl.enable(gl.DEPTH_TEST);gl.clearColor(0,0,0,0);
 const rot=gl.getUniformLocation(program,'rotation'),aspect=gl.getUniformLocation(program,'aspect');
 const pref=matchMedia('(prefers-reduced-motion: reduce)');let paused=pref.matches,visible=true,frame=0,last=0,yaw=.8,pitch=.15,drag=null;
 function draw(){const cy=Math.cos(yaw),sy=Math.sin(yaw),cx=Math.cos(pitch),sx=Math.sin(pitch);gl.uniformMatrix4fv(rot,false,new Float32Array([cy,sx*sy,-cx*sy,0,0,cx,sx,0,sy,-sx*cy,cx*cy,0,0,0,0,1]));gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);gl.drawArrays(gl.TRIANGLES,0,vertexCount);}
 function tick(time){frame=0;if(last&&!drag)yaw+=Math.min(time-last,50)*.00013;last=time;draw();if(!paused&&visible&&!document.hidden)frame=requestAnimationFrame(tick);}
 function sync(){cancelAnimationFrame(frame);last=0;document.body.classList.toggle('motion-paused',paused);toggle.textContent=paused?'Enable motion':'Pause motion';toggle.setAttribute('aria-pressed',String(paused));draw();if(!paused&&visible&&!document.hidden)frame=requestAnimationFrame(tick);}
 new ResizeObserver(()=>{const r=canvas.getBoundingClientRect(),d=Math.min(devicePixelRatio,2);canvas.width=r.width*d;canvas.height=r.height*d;gl.viewport(0,0,canvas.width,canvas.height);gl.uniform1f(aspect,r.width/r.height);draw();}).observe(canvas);
 new IntersectionObserver(e=>{visible=e[0].isIntersecting;sync();}).observe(canvas);
 canvas.style.touchAction='pan-y';canvas.style.cursor='grab';canvas.tabIndex=0;canvas.removeAttribute('aria-hidden');canvas.setAttribute('aria-label','3D brain. Drag or use arrow keys to rotate.');
 canvas.addEventListener('pointerdown',e=>{drag=[e.clientX,e.clientY];canvas.setPointerCapture(e.pointerId);});
 canvas.addEventListener('pointermove',e=>{if(!drag)return;yaw+=(e.clientX-drag[0])*.01;pitch=Math.max(-1,Math.min(1,pitch+(e.clientY-drag[1])*.01));drag=[e.clientX,e.clientY];draw();});
 for(const event of ['pointerup','pointercancel'])canvas.addEventListener(event,()=>{drag=null;});
 canvas.addEventListener('keydown',e=>{if(!e.key.startsWith('Arrow'))return;e.preventDefault();yaw+=e.key==='ArrowLeft'?-.15:e.key==='ArrowRight'?.15:0;pitch+=e.key==='ArrowUp'?-.1:e.key==='ArrowDown'?.1:0;draw();});
 toggle.addEventListener('click',()=>{paused=!paused;sync();});pref.addEventListener('change',()=>{paused=pref.matches;sync();});document.addEventListener('visibilitychange',sync);sync();
})();
