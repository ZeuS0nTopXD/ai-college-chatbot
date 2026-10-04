(() => {
    const toggle = document.getElementById('motion-toggle');
    const art = document.querySelector('.campus-art');
    const stage = document.querySelector('.sculpture-stage');
    const preference = matchMedia('(prefers-reduced-motion: reduce)');
    let paused = preference.matches;
    const update = () => {
        document.body.classList.toggle('motion-paused', paused);
        toggle.textContent = paused ? 'Enable motion' : 'Pause motion';
        toggle.setAttribute('aria-pressed', String(paused));
        stage.style.setProperty('--tilt-x', '0deg');
        stage.style.setProperty('--tilt-y', '0deg');
    };
    toggle.addEventListener('click', () => { paused = !paused; update(); });
    preference.addEventListener('change', () => { paused = preference.matches; update(); });
    art.addEventListener('pointermove', event => {
        if (paused || preference.matches || event.pointerType === 'touch') return;
        const box = art.getBoundingClientRect();
        stage.style.setProperty('--tilt-y', `${((event.clientX-box.left)/box.width-.5)*24}deg`);
        stage.style.setProperty('--tilt-x', `${((event.clientY-box.top)/box.height-.5)*-16}deg`);
    });
    art.addEventListener('pointerleave', () => { stage.style.setProperty('--tilt-x','0deg'); stage.style.setProperty('--tilt-y','0deg'); });
    update();
})();
