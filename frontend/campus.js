(() => {
    const canvas = document.getElementById('neural-brain');
    const context = canvas.getContext('2d');
    const toggle = document.getElementById('motion-toggle');
    const preference = matchMedia('(prefers-reduced-motion: reduce)');
    let paused = preference.matches, visible = true, frame = 0, phase = 0, last = 0;
    let width = 1, height = 1, pointer = 0;
    // Joined cerebral hemispheres: rounded lobes, cortical folds and central fissure.
    const outline = new Path2D('M 0 -72 C -10 -94 -38 -98 -53 -82 C -78 -88 -97 -69 -98 -51 C -121 -43 -130 -17 -116 2 C -132 23 -116 52 -95 53 C -91 77 -65 84 -47 71 C -28 87 -5 72 0 55 Z');
    const folds = [
        'M -53 -82 C -39 -69 -65 -57 -54 -43 C -44 -32 -25 -48 -18 -32',
        'M -98 -51 C -83 -58 -68 -44 -77 -31 C -89 -17 -65 -9 -55 -18',
        'M -116 2 C -98 -8 -84 5 -92 20 C -97 35 -76 41 -65 29',
        'M -95 53 C -76 51 -73 67 -58 58 C -44 51 -59 34 -43 26',
        'M -47 71 C -31 59 -39 45 -22 42 C -7 39 -12 23 -23 18',
        'M -18 -70 C -35 -68 -23 -52 -32 -43',
        'M -57 -18 C -39 -26 -46 -4 -30 -3 C -16 -3 -17 11 -23 18',
        'M -104 -27 C -108 -12 -91 -17 -86 -8',
        'M -65 29 C -53 17 -73 6 -59 -1',
        'M -13 -22 C -5 -12 -18 -4 -11 8',
    ].map(path => new Path2D(path));
    function draw() {
        context.clearRect(0, 0, width, height);
        const angle = Math.sin(phase * .35) * .08 + pointer * .18;
        const scale = Math.min(width / 310, height / 250);
        context.save();
        context.translate(width/2, height/2 + 5);
        context.rotate(-.08 + angle);
        context.scale(scale, scale);
        // A shallow offset supplies volume without turning the lobes into separate organs.
        for (const side of [-1,1]) {
            context.save(); context.scale(side,1);
            context.translate(-2,0);
            context.save();context.translate(3,6);
            context.fillStyle='#d4d4cf';context.fill(outline);context.restore();
            const surface=context.createLinearGradient(-120,-80,0,65);
            surface.addColorStop(0,'#fffefa');surface.addColorStop(1,'#e9e9e3');
            context.fillStyle=surface;context.strokeStyle='#242424';context.lineWidth=1.8;
            context.fill(outline);context.stroke(outline);
            context.strokeStyle='#575751';context.lineWidth=1.6;
            context.lineCap='round';folds.forEach(path=>context.stroke(path));
            [[-53,-43],[-77,-31],[-92,20],[-43,26],[-23,18],[-30,-3]].forEach(([x,y],i)=>{
                const pulse=(Math.sin(phase*2-i)+1)/2;
                context.beginPath();context.arc(x,y,3+pulse*4,0,Math.PI*2);
                context.fillStyle=`rgba(25,25,25,${.04+pulse*.09})`;context.fill();
                context.beginPath();context.arc(x,y,2,0,Math.PI*2);
                context.fillStyle='#242424';context.fill();
            });
            context.restore();
        }
        context.restore();
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
