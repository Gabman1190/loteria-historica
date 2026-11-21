"""Lotería Histórica - servidor multijugador. Ejecutar: pip install -r requirements.txt && uvicorn server:app --host 0.0.0.0 --port 8000"""
import asyncio, json, random, secrets, string, time
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse

ROOT=Path(__file__).parent
CONCEPTS=json.loads((ROOT/'concepts.json').read_text(encoding='utf8'))
BY_ID={c['id']:c for c in CONCEPTS}
CATEGORIES={}
for c in CONCEPTS:CATEGORIES.setdefault(c['category'],[]).append(c['id'])
print('Categorías:', {k:len(v) for k,v in CATEGORIES.items()})
app=FastAPI(title='Lotería Histórica')
ROOMS={}
MAX_TEAMS=8
DURATION=30
LOCKOUT=5
MAX_ROUNDS=35

def code():return ''.join(secrets.choice(string.ascii_uppercase+string.digits) for _ in range(6))
def token():return secrets.token_urlsafe(24)
def board():
    # 3 Totalitarismos, 3 Guerra Fría, 2 Chile inicial, 1 AL, 2 dictadura, 1 transición.
    groups=[3,3,2,1,2,1]
    assert len(CATEGORIES)==6, 'Se esperan seis categorías'
    ids=[]
    for (cat,items),n in zip(CATEGORIES.items(),groups):ids+=random.sample(items,n)
    random.shuffle(ids)
    return ids

def public(room,role,team=None):
    now=time.monotonic()
    teams=[{'id':t['id'],'name':t['name'],'score':len(t['won']),'online':bool(t['ws'])} for t in room['teams']]
    teams.sort(key=lambda x:(-x['score'],x['id']))
    data={'type':'state','code':room['code'],'phase':room['phase'],'round':room['round'],'maxRounds':MAX_ROUNDS,'seconds':max(0,int(room['deadline']-now+0.999)) if room['phase']=='active' else 0,'teams':teams,'result':room['result'],'winner':room['winner'],'message':room['message']}
    if room['current'] is not None:
        c=BY_ID[room['current']]
        data['clue']=c['clues'][room['clueIndex']]
        if room['phase']!='active' and role=='teacher':data['answer']=c['name']
        if room['phase']=='result':data['answer']=c['name']
    if role=='student' and team:
        data['you']=team['id'];data['board']=[{'id':i,'name':BY_ID[i]['name'],'won':i in team['won']} for i in team['board']]
        data['lockedFor']=max(0,int(team['lockedUntil']-now+0.999))
        data['canAnswer']=room['phase']=='active' and now>=team['lockedUntil'] and not team['submitted']
    return data

async def send(ws,payload):
    try:await ws.send_json(payload)
    except Exception:pass

async def broadcast(room):
    if room['teacher']:await send(room['teacher'],public(room,'teacher'))
    for team in room['teams']:
        if team['ws']:await send(team['ws'],public(room,'student',team))

async def finish(room,reason='timeout',winner=None):
    if room['phase']!='active':return
    room['phase']='result'
    room['result']={'reason':reason,'team':winner['name'] if winner else None,'answer':BY_ID[room['current']]['name']}
    if winner and len(winner['won'])==12:
        room['phase']='finished';room['winner']=winner['name']
    await broadcast(room)

async def countdown(room,round_number):
    while room['phase']=='active' and room['round']==round_number:
        await asyncio.sleep(.5)
        if time.monotonic()>=room['deadline']:
            async with room['lock']:
                if room['phase']=='active' and room['round']==round_number:await finish(room)
            break
        await broadcast(room)

def choose_clue(room):
    eligible={i for t in room['teams'] for i in t['board'] if i not in t['won']}
    if not eligible:return None
    # Prefer concepts not recently seen and clues not used yet; never a concept absent from all boards.
    counts={i:sum(i in t['board'] and i not in t['won'] for t in room['teams']) for i in eligible}
    choices=sorted(eligible,key=lambda i:(room['used'].get(i,0),-counts[i],random.random()))
    return choices[0]

async def handle_teacher(room,ws,body):
    action=body.get('action')
    async with room['lock']:
        if action=='start':
            if room['phase']=='active':return
            if room['phase']=='finished':return
            if room['round']>=MAX_ROUNDS:
                room['phase']='finished';room['winner']=winner_text(room);await broadcast(room);return
            i=choose_clue(room)
            if i is None:room['phase']='finished';room['winner']=winner_text(room);await broadcast(room);return
            room['round']+=1;room['current']=i;room['clueIndex']=room['used'].get(i,0)%len(BY_ID[i]['clues'])
            room['used'][i]=room['used'].get(i,0)+1
            room['deadline']=time.monotonic()+DURATION
            room['phase']='active';room['result']=None;room['message']=''
            for t in room['teams']:t['submitted']=False;t['lockedUntil']=0
            asyncio.create_task(countdown(room,room['round']))
        elif action=='close' and room['phase']=='active':await finish(room,'manual')
        elif action=='end':room['phase']='finished';room['winner']=winner_text(room)
        elif action=='reset':
            room['phase']='lobby';room['round']=0;room['current']=None;room['result']=None;room['winner']=None;room['used']={};room['message']=''
            for t in room['teams']:t['board']=board();t['won']=set();t['submitted']=False;t['lockedUntil']=0
        await broadcast(room)

def winner_text(room):
    if not room['teams']:return 'Sin equipos'
    best=max(len(t['won']) for t in room['teams'])
    winners=[t['name'] for t in room['teams'] if len(t['won'])==best]
    return ', '.join(winners) + (' (empate: requiere desempate)' if len(winners)>1 else '')

async def handle_answer(room,team,body):
    async with room['lock']:
        now=time.monotonic()
        if room['phase']!='active' or now>=room['deadline'] or team['submitted'] or now<team['lockedUntil']:return
        try:i=int(body.get('concept'))
        except (TypeError,ValueError):return
        if i not in team['board'] or i in team['won']:return
        if i==room['current']:
            team['won'].add(i);team['submitted']=True
            await finish(room,'correct',team)
        else:
            team['lockedUntil']=now+LOCKOUT
            room['message']=f"{team['name']} recibió una penalización de 5 segundos"
            await broadcast(room)

@app.get('/')
async def home():return FileResponse(ROOT/'multijugador.html')
@app.get('/health')
async def health():return {'ok':True,'rooms':len(ROOMS)}

@app.websocket('/ws')
async def websocket(ws:WebSocket):
    await ws.accept();room=None;role=None;team=None
    try:
        hello=await ws.receive_json()
        mode=hello.get('mode')
        if mode=='create':
            roomcode=code()
            while roomcode in ROOMS:roomcode=code()
            room={'code':roomcode,'secret':token(),'teacher':ws,'teams':[],'phase':'lobby','round':0,'current':None,'clueIndex':0,'deadline':0,'used':{},'result':None,'winner':None,'message':'','lock':asyncio.Lock()}
            ROOMS[roomcode]=room;role='teacher'
            await send(ws,{'type':'credentials','code':roomcode,'secret':room['secret'],'role':'teacher'})
        elif mode=='teacher':
            room=ROOMS.get(str(hello.get('code','')).upper())
            if not room or hello.get('secret')!=room['secret']:await send(ws,{'type':'error','message':'Código o credencial de profesor incorrectos'});return
            if room['teacher'] and room['teacher'] is not ws:await room['teacher'].close(code=4001)
            room['teacher']=ws;role='teacher'
            await send(ws,{'type':'credentials','code':room['code'],'secret':room['secret'],'role':'teacher'})
        elif mode=='join':
            room=ROOMS.get(str(hello.get('code','')).upper())
            if not room:await send(ws,{'type':'error','message':'Sala no encontrada'});return
            key=hello.get('token');team=next((t for t in room['teams'] if t['token']==key),None) if key else None
            if team:
                if team['ws'] and team['ws'] is not ws:await team['ws'].close(code=4001)
                team['ws']=ws
            else:
                if room['phase']!='lobby' or len(room['teams'])>=MAX_TEAMS:await send(ws,{'type':'error','message':'Sala cerrada o completa'});return
                name=str(hello.get('name','')).strip()[:26]
                if not name:name=f'Equipo {len(room["teams"])+1}'
                if any(t['name'].casefold()==name.casefold() for t in room['teams']):await send(ws,{'type':'error','message':'Ese nombre ya está ocupado'});return
                team={'id':len(room['teams'])+1,'name':name,'token':token(),'ws':ws,'board':board(),'won':set(),'submitted':False,'lockedUntil':0}
                room['teams'].append(team)
            role='student';await send(ws,{'type':'credentials','code':room['code'],'token':team['token'],'role':'student'})
        else:await send(ws,{'type':'error','message':'Acceso inválido'});return
        await broadcast(room)
        while True:
            body=await ws.receive_json()
            if role=='teacher':await handle_teacher(room,ws,body)
            elif body.get('action')=='answer':await handle_answer(room,team,body)
    except (WebSocketDisconnect,RuntimeError):pass
    finally:
        if room:
            if role=='teacher' and room['teacher'] is ws:room['teacher']=None
            if role=='student' and team and team['ws'] is ws:team['ws']=None
            await broadcast(room)
