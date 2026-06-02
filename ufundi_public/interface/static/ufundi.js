// ==================== ÉTOILES ====================
(function(){const c=document.getElementById('stars');if(!c)return;for(let i=0;i<60;i++){const s=document.createElement('div');s.className='star';s.style.left=Math.random()*100+'%';s.style.top=Math.random()*100+'%';s.style.setProperty('--duration',(Math.random()*3+2)+'s');s.style.animationDelay=Math.random()*3+'s';s.style.width=s.style.height=(Math.random()*3+1)+'px';c.appendChild(s);}})();

// ==================== ÉTAT GLOBAL ====================
let step1Passwords=[],step1Current=1,step1Cles=[],dailyChoice=null,pinLength=4,createdEmail='',userPrenom='',userEmail='',contacts=[];

// ==================== UTILITAIRES ====================
function toast(id,type,msg){const e=document.getElementById(id);if(!e)return;e.className=`toast ${type} show`;e.textContent=msg;setTimeout(()=>{if(e)e.classList.remove('show');},4000);}
function hideAll(){document.querySelectorAll('.screen-center,.app-layout').forEach(e=>e.classList.add('hidden'));}
function el(id){return document.getElementById(id);}
function setText(id,txt){const e=el(id);if(e)e.textContent=txt;}

function showLogin(){hideAll();const e=el('loginScreen');if(e)e.classList.remove('hidden');}
function showCreateStep1(){hideAll();const e=el('createStep1Screen');if(e)e.classList.remove('hidden');}
function showCreateStep2(){hideAll();const e=el('createStep2Screen');if(e)e.classList.remove('hidden');}
function showCreateStep3(){hideAll();const e=el('createStep3Screen');if(e)e.classList.remove('hidden');}

async function openApp(){
    hideAll();const app=el('appScreen');if(!app)return;app.classList.remove('hidden');
    setText('sidebarName',userPrenom||'---');setText('userAvatar',(userPrenom||'U')[0].toUpperCase());setText('setEmail',userEmail||'---');setText('walletBalance',Math.floor(Math.random()*1000));
    try{ufundiRAM=new UfundiVirtualRAM();await ufundiRAM.init(new Uint8Array(32));}catch(e){}
    try{await fetch('/api/smtp/start',{method:'POST'});}catch(e){}
    loadContacts();showAppView('messages');checkNotifications();setInterval(checkNotifications,5000);
}

// ==================== ÉTAPE 1 : 6 MOTS DE PASSE ====================
function validateStep1(){
    const inp=el('step1Pass');if(!inp)return;const v=inp.value;
    const rules={maj:/[A-Z]/.test(v),min:/[a-z]/.test(v),digit:/[0-9]/.test(v),special:/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(v),length:v.length>=8,unique:!step1Passwords.includes(v)};
    ['rMaj','rMin','rDigit','rSpecial','rLength','rUnique'].forEach((id,i)=>{const e=el(id);if(e)e.classList.toggle('valid',Object.values(rules)[i]);});
    const btn=el('step1Btn');if(btn)btn.disabled=!Object.values(rules).every(v=>v);
}
async function submitStep1(){
    const inp=el('step1Pass');if(!inp)return;const p=inp.value;step1Passwords.push(p);
    const dot=el(`d${step1Current}`);if(dot)dot.classList.add('filled');
    const r=await fetch('/api/generer_cle',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({password:p,typing_speed:45+step1Current*12,key_pressure:0.7})});
    const d=await r.json();
    if(d.success){step1Cles.push(d.cle);step1Current++;
        if(step1Current<=6){setText('step1Num',step1Current);inp.value='';document.querySelectorAll('#step1Rules span').forEach(s=>s.classList.remove('valid'));const btn=el('step1Btn');if(btn)btn.disabled=true;}
        else{showCreateStep2();}
    }else{toast('step1Toast','error',d.error);}
}

// ==================== ÉTAPE 2 : IDENTITÉ + MDP QUOTIDIEN ====================
function selectDaily(n){
    dailyChoice=n;
    document.querySelectorAll('#dailyChoices .btn-sm').forEach(b=>b.classList.remove('selected'));
    const e=el(`daily${n}`);if(e)e.classList.add('selected');
    checkStep2();
}
function checkStep2(){
    const prenom=el('s2Prenom'),nom=el('s2Nom'),confirm=el('s2Confirm');
    if(!prenom||!nom||!confirm)return;
    const p=prenom.value.trim(),n=nom.value.trim(),c=confirm.value;
    const mdpOk=(dailyChoice!==null)&&(c===step1Passwords[dailyChoice-1]);
    const nomOk=p.length>=2&&n.length>=2;
    const btn=el('step2Btn');
    if(btn){
        btn.disabled=!(mdpOk&&nomOk);
        if(mdpOk&&nomOk){btn.style.opacity='1';btn.style.cursor='pointer';}
        else{btn.style.opacity='0.5';btn.style.cursor='not-allowed';}
    }
}
function submitStep2(){
    const prenom=el('s2Prenom'),nom=el('s2Nom');
    if(!prenom||!nom)return;
    const p=prenom.value.trim(),n=nom.value.trim();
    if(!p||!n){toast('step2Toast','error','Prénom et nom requis');return;}
    if(dailyChoice===null){toast('step2Toast','error','Choisissez un MDP quotidien');return;}
    createdEmail=`${p.toLowerCase()}.${n.toLowerCase()}@ufundi.ai`;
    const emailEl=el('s3Email');if(emailEl)emailEl.value=createdEmail;
    showCreateStep3();
}

// ==================== ÉTAPE 3 : PIN + CRÉATION ====================
function setPinLength(n){pinLength=n;setText('pinLenLabel',n);const inp=el('s3Pin');if(inp){inp.maxLength=n;inp.value='';}const b4=el('pin4Btn'),b6=el('pin6Btn');if(b4)b4.classList.toggle('selected',n===4);if(b6)b6.classList.toggle('selected',n===6);const btn=el('step3Btn');if(btn)btn.disabled=true;document.querySelectorAll('#pinRules span').forEach(s=>s.classList.remove('valid'));}
function validatePin(){const inp=el('s3Pin');if(!inp)return;const p=inp.value;const okLen=p.length===pinLength,okUnique=new Set(p).size===p.length&&p.length===pinLength,okNum=/^\d+$/.test(p);['pinLenRule','pinUniqueRule','pinNumericRule'].forEach(id=>{const e=el(id);if(e)e.classList.toggle('valid',id==='pinLenRule'?okLen:id==='pinUniqueRule'?okUnique:okNum&&p.length>0);});const btn=el('step3Btn');if(btn)btn.disabled=!(okLen&&okUnique&&okNum);}
setPinLength(4);
async function submitStep3(){
    const inp=el('s3Pin');if(!inp)return;const pin=inp.value;const btn=el('step3Btn');if(btn){btn.disabled=true;btn.textContent='⏳...';}
    const prenom=el('s2Prenom'),nom=el('s2Nom');if(!prenom||!nom)return;const p=prenom.value.trim(),n=nom.value.trim();
    const r1=await fetch('/api/combiner_cles',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({cles:step1Cles,global_rhythm:{entre_mots:[120,95,150,80,110]}})});
    const cm=(await r1.json()).cle_unique;
    const r=await fetch('/api/creer_compte_final',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({cle_maitresse:cm,nom:n,prenom:p,mdp_6:pin,telephone:'N/A',mdp_quotidien_hash:btoa(step1Passwords[dailyChoice-1])})});
    const d=await r.json();
    if(d.success){await fetch('/api/set_daily_password',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:createdEmail,password:step1Passwords[dailyChoice-1]})});userPrenom=p;userEmail=createdEmail;try{await ufundiDB.sauvegarderCompte(createdEmail,step1Cles,new Uint8Array(32),p);await ufundiDB.sauvegarderSession(createdEmail,p);}catch(e){}openApp();}
    else{toast('step3Toast','error',d.error);if(btn){btn.disabled=false;btn.textContent='Finaliser l\'identité';}}
}

// ==================== LOGIN ====================
async function handleLogin(){const emailEl=el('loginEmail'),passEl=el('loginPass');if(!emailEl||!passEl)return;const email=emailEl.value.trim().toLowerCase(),pass=passEl.value;if(!email||!pass){toast('loginToast','error','Email et mot de passe requis');return;}try{const check=await fetch('/api/check_existence',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:email})});const cd=await check.json();if(!cd.existe){toast('loginToast','error','Ce compte n\'existe pas');return;}}catch(e){}try{const cl=await ufundiDB.chargerCompte(email);if(cl){userPrenom=cl.prenom;userEmail=email;await ufundiDB.sauvegarderSession(email,cl.prenom);openApp();return;}}catch(e){}const r=await fetch('/api/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:email,password:pass})});const d=await r.json();if(d.success){userPrenom=d.prenom;userEmail=d.email;try{await ufundiDB.sauvegarderSession(d.email,d.prenom);}catch(e){}openApp();}else{toast('loginToast','error',d.error||'Échec connexion');}}

// ==================== APPLICATION ====================
async function loadContacts(){try{const r=await fetch('/api/contacts');const d=await r.json();contacts=d.contacts||[];renderContacts();}catch(e){contacts=[];renderContacts();}}
function renderContacts(f=''){const list=el('contactList');if(!list)return;list.innerHTML=contacts.filter(c=>c.prenom.toLowerCase().includes((f||'').toLowerCase())).map(c=>`<div class="contact" onclick="openChat('${c.prenom}')"><div class="c-avatar">${c.prenom[0]}</div><div class="c-name">${c.prenom}</div></div>`).join('')||'<div style="padding:20px;color:var(--text-secondary);">Aucun contact</div>';}
function filterContacts(){renderContacts(el('searchInput')?.value||'');}
function showAppView(v){document.querySelectorAll('.app-view').forEach(e=>e.classList.add('hidden'));const view=el('view'+v.charAt(0).toUpperCase()+v.slice(1));if(view)view.classList.remove('hidden');if(v==='wallet')setText('walletBalance',Math.floor(Math.random()*1000));if(v==='messages')renderContacts();if(v==='system'&&typeof systemMessages!=='undefined')systemMessages.updateSystemTab();}

function openChat(prenom){setText('mainTitle',`💬 ${prenom}`);const content=el('mainContent');if(!content)return;content.innerHTML=`<div id="chatMessages" style="flex:1;overflow-y:auto;padding:10px;"></div><div style="display:flex;gap:10px;padding:10px;border-top:1px solid var(--border);"><input type="text" id="chatInput" placeholder="Message..." style="flex:1;padding:12px;background:rgba(0,0,0,0.3);border:1px solid var(--border);border-radius:12px;color:#fff;outline:none;" onkeypress="if(event.key==='Enter')sendMessage()"><button class="btn btn-primary" style="width:auto;padding:12px 20px;" onclick="sendMessage()">➤</button></div>`;}
async function sendMessage(){const input=el('chatInput');if(!input||!input.value.trim())return;const chat=el('chatMessages');if(chat)chat.innerHTML+=`<div class="message-bubble msg-out">${input.value}</div>`;input.value='';}

async function checkNotifications(){if(!userEmail)return;try{const r=await fetch(`/api/messages/notifications?email=${userEmail}`);const d=await r.json();if(d.notifications&&d.notifications.length>0){const badge=el('notificationBadge');if(badge){badge.classList.remove('hidden');setText('notifCount',d.notifications.length);}}}catch(e){}}

async function handleLogout(){
    try{await fetch('/api/smtp/stop',{method:'POST'});}catch(e){}
    if(typeof ufundiRAM!=='undefined'&&ufundiRAM)ufundiRAM.destroy();ufundiRAM=null;
    try{await ufundiDB.effacerSession();}catch(e){}
    if(typeof ufundiSettings!=='undefined')ufundiSettings.destroy();
    if(typeof systemMessages!=='undefined')systemMessages.destroy();
    if(typeof selfChat!=='undefined')selfChat.destroy();
    await fetch('/api/logout',{method:'POST'});
    userPrenom='';userEmail='';contacts=[];showLogin();
}
const profileBtn=el('profileBtn');if(profileBtn)profileBtn.addEventListener('click',()=>{if(confirm('Se déconnecter ?'))handleLogout();});

(async function autoLogin(){try{const s=await ufundiDB.chargerSession();if(s){userPrenom=s.prenom;userEmail=s.email;openApp();return;}}catch(e){}showLogin();})();
