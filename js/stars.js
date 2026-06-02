(function(){
    var c = document.getElementById('stars');
    for(var i=0; i<80; i++){
        var s = document.createElement('div');
        s.className = 'star';
        s.style.left = Math.random()*100+'%';
        s.style.top = Math.random()*100+'%';
        s.style.setProperty('--d', (Math.random()*3+2)+'s');
        s.style.animationDelay = Math.random()*3+'s';
        s.style.width = s.style.height = (Math.random()*2+1)+'px';
        c.appendChild(s);
    }
})();
