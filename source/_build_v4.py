# -*- coding: utf-8 -*-
"""构建V4古风版：注入疆域数据 + 知识点 + 测验 + 大事记 + 引文填空 + 世界舆图。"""
import json,os,base64

WD=r'D:\WorkBuddyData\2026-11-20-17-31-34'
JS_DATA=json.load(open(WD+r'\_jiangshan_data.json',encoding='utf-8'))
OLD=json.load(open(WD+r'\_data_all.json',encoding='utf-8'))
KN=json.load(open(WD+r'\_v5_knowledge.json',encoding='utf-8'))
TERRAIN=WD+r'\_jiangshan_src\assets\terrain_relief.webp'
def _load(name):
    p=os.path.join(WD,name)
    return json.load(open(p,encoding='utf-8')) if os.path.isfile(p) else None

EVENTS=_load('_events.json')
CLOZE=_load('_cloze.json')
WORLD=_load('_world.json')

# JS 需要: eras(朝代疆域+政权) settlements landmarks rivers/lakes + quiz pitfalls + events/cloze/world
JS={
 'eras':JS_DATA['eras'],
 'settlements':JS_DATA['settlements'],
 'landmarks':JS_DATA.get('landmarks',[]),
 'rivers':JS_DATA.get('rivers',[]),
 'lakes':JS_DATA.get('lakes',[]),
 'corridors':JS_DATA.get('corridors',[]),
 'quiz':OLD['quiz'],
 'pitfalls':OLD['pitfalls'],
 'milestones':JS_DATA.get('milestones', []),
 'phases':JS_DATA.get('phases', []),
}
if EVENTS: JS['events']=EVENTS
if CLOZE: JS['cloze']=CLOZE
if WORLD: JS['world']=WORLD
WPOL=os.path.join(WD,'_world_polities.json')
if os.path.isfile(WPOL):
    JS['wpol']=json.load(open(WPOL,encoding='utf-8'))
# 朝代综述（借江山时序 DYNASTY_DATA，GPL-3.0 已授权）
MDP=WD+r'\_jiangshan_src\js\map_data.js'
if os.path.isfile(MDP):
    try:
        _mt=open(MDP,encoding='utf-8',errors='ignore').read()
        _i=_mt.find('window.DYNASTY_DATA');_j=_mt.find('=',_i);_k=_mt.find('];',_j)
        _DD=json.loads(_mt[_j+1:_k+1])
        JS['eraSummaries']={d['key']:d.get('summary','') for d in _DD if d.get('key')}
        print('eraSummaries',len(JS['eraSummaries']))
    except Exception as _e:
        print('eraSummaries skip',_e)
# 世界统一晕渲底图（V10.1：AWS Terrain Tiles DEM + 江山时序 hillshade 配方（GPL 同源已授权），
# SRTM/Copernicus 公有领域；中国与世界同一张图同一配方，风格由构造保证完全一致；
# 海面透明露纸色海，南极 lat<-56 裁除；旧 terrain_relief.webp / world_land.webp 均弃用仅存档）
WBASE=WD+r'\_dl_world\world_relief.webp'
if os.path.isfile(WBASE):
    JS['worldBase']={'src':'data:image/webp;base64,'+base64.b64encode(open(WBASE,'rb').read()).decode(),
                     'w':8192,'h':4096}

TPL=r'D:\WorkBuddyData\2026-11-20-17-31-34\_v4_template.html'
OUT=r'D:\UserData\Desktop\高中历史时空互动学习系统.html'

tpl=open(TPL,encoding='utf-8').read()
html=tpl.replace('__JS__',json.dumps(JS,ensure_ascii=False)).replace('__KN__',json.dumps(KN,ensure_ascii=False))
open(OUT,'w',encoding='utf-8').write(html)
print('WROTE',OUT,os.path.getsize(OUT)//1024,'KB')
print('朝代',len(JS['eras']),'城池',len(JS['settlements']),'山河',len(JS['landmarks']),'知识点',len(KN),
      '大事',sum(len(v) for v in (JS.get('events') or {}).values()),
      '填空',len(JS.get('cloze') or []),
      '世界锚点',len((JS.get('world') or {}).get('anchors',[])))
