(() => {
    const canvas = document.getElementById('neural-brain');
    const context = canvas.getContext('2d');
    const toggle = document.getElementById('motion-toggle');
    const preference = matchMedia('(prefers-reduced-motion: reduce)');
    let paused = preference.matches, visible = true, frame = 0, phase = 0, last = 0;
    let width = 1, height = 1, pointer = 0;
    const points = [], edges = [];
    // Two separated, folded ellipsoidal hemispheres in real 3D coordinates.
    for (const side of [-1, 1]) {
        const start = points.length;
        for (let ring = 0; ring < 15; ring++) {
            const latitude = .14 + ring / 14 * (Math.PI - .28);
            for (let j = 0; j < 26; j++) {
                const longitude = j / 26 * Math.PI * 2;
                const fold = 1 + .075 * Math.sin(longitude * 6 + latitude * 8);
                points.push({
                    x: side * (40 + 37 * Math.sin(latitude) * Math.cos(longitude) * fold),
                    y: -12 + 94 * Math.cos(latitude) * fold,
                    z: 66 * Math.sin(latitude) * Math.sin(longitude) * fold,
                });
                const index = points.length - 1;
                if (j) edges.push([index - 1, index]);
                if (ring) edges.push([index - 26, index]);
                if (j === 25) edges.push([index, index - 25]);
            }
        }
    }
    function draw() {
        context.clearRect(0, 0, width, height);
        const rotation = Math.sin(phase * .3) * .6 + pointer + .25;
        const scale = Math.min(width / 250, height / 260);
        const projected = points.map(p => {
            const x = p.x * Math.cos(rotation) + p.z * Math.sin(rotation);
            const z = -p.x * Math.sin(rotation) + p.z * Math.cos(rotation);
            const perspective = 480 / (480 - z);
            return {x: width/2 + x * scale * perspective, y: height/2 + p.y * scale * perspective, z};
        });
        edges.forEach(([a,b]) => {
            const p = projected[a], q = projected[b];
            context.strokeStyle = `rgba(20,20,20,${.08 + (p.z + 80)/160 * .32})`;
            context.lineWidth = .65;
            context.beginPath();context.moveTo(p.x,p.y);context.lineTo(q.x,q.y);context.stroke();
        });
        projected.forEach((p,i) => {
            if (i % 11) return;
            const pulse = (Math.sin(phase * 2 - i * .15) + 1)/2;
            context.fillStyle = `rgba(15,15,15,${.35 + pulse*.65})`;
            context.beginPath();context.arc(p.x,p.y,1 + pulse*1.5,0,Math.PI*2);context.fill();
        });
    }
    function tick(time) {
        frame = 0;
        if (last) phase += Math.min((time-last)/1000,.05);
        last = time; draw();
        if (!paused && visible && !document.hidden) frame = requestAnimationFrame(tick);
    }
    function sync() {
        cancelAnimationFrame(frame);frame = 0;last = 0;
        document.body.classList.toggle('motion-paused',paused);
        toggle.textContent = paused ? 'Enable motion' : 'Pause motion';
        toggle.setAttribute('aria-pressed',String(paused));draw();
        if (!paused && visible && !document.hidden) frame=requestAnimationFrame(tick);
    }
    new ResizeObserver(() => {
        const box=canvas.getBoundingClientRect();width=box.width;height=box.height;
        const ratio=Math.min(devicePixelRatio || 1,2);
        canvas.width=width*ratio;canvas.height=height*ratio;
        context.setTransform(ratio,0,0,ratio,0,0);draw();
    }).observe(canvas);
    new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;sync();}).observe(canvas);
    toggle.addEventListener('click',()=>{paused=!paused;sync();});
    preference.addEventListener('change',()=>{paused=preference.matches;sync();});
    document.addEventListener('visibilitychange',sync);
    canvas.addEventListener('pointermove',event=>{
        if(paused || event.pointerType==='touch')return;
        const box=canvas.getBoundingClientRect();pointer=((event.clientX-box.left)/box.width-.5)*.6;
    });
    canvas.addEventListener('pointerleave',()=>{pointer=0;});sync();
})();
