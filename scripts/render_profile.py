#!/usr/bin/env python3
"""Create GitHub-compatible SVGs with bounded, non-overlapping Moonshade layouts.

The activity cards use only GitHub's actual contribution calendar. When data is
not yet available, clearly marked pending states replace numerical statistics.
"""
from __future__ import annotations

import calendar
import datetime as dt
import html
import json
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARDS = ROOT / "cards"
DATA = ROOT / "data" / "contributions.json"
CARDS.mkdir(parents=True, exist_ok=True)

INK = "#171827"
MUTED = "#64697C"
FAINT = "#8A90A3"
LILAC = "#746DCE"
LILAC_STRONG = "#625BCD"
BLUE = "#8A9DC5"
SILVER = "#F0F2F5"
SILVER_DARK = "#E6E9F0"
STROKE = "#D9DEE8"
VIOLET = ["#E0E3ED", "#DCD9F4", "#BDB7EA", "#978BE0", "#625BCD"]


def s(v):
    return html.escape(str(v), quote=True)


def t(x, y, value, size=16, fill=INK, weight=None, family=None, cls=None, other=""):
    a = f' x="{x}" y="{y}" fill="{fill}" font-size="{size}"'
    if weight: a += f' font-weight="{weight}"'
    if family: a += f' font-family="{family}"'
    if cls: a += f' class="{cls}"'
    return f'<text{a} {other}>{s(value)}</text>'


def rect(x, y, w, h, fill, rx=0, other=""):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" {other}/>'


def svg(width, height, content, title, desc, background=True):
    base = f'''
    <svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
    <title id="title">{s(title)}</title><desc id="desc">{s(desc)}</desc>
    <defs>
      <linearGradient id="surface" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#F6F7F9"/><stop offset="1" stop-color="#ECEEF3"/></linearGradient>
      <linearGradient id="night" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#1D1E33"/><stop offset="1" stop-color="#292A47"/></linearGradient>
      <linearGradient id="twilight" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#3A385E"/><stop offset="1" stop-color="#44436C"/></linearGradient>
      <linearGradient id="dusk" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#585183"/><stop offset="1" stop-color="#68639F"/></linearGradient>
      <style><![CDATA[
      text{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif}}
      .serif{{font-family:Georgia,'Times New Roman',serif;font-style:italic}}
      @keyframes appear{{from{{opacity:0;transform:translateY(8px)}}to{{opacity:1;transform:translateY(0)}}}}
      @keyframes gleam{{0%,100%{{opacity:.55}}50%{{opacity:.86}}}}
      @keyframes grow{{from{{transform:scaleY(.12)}}to{{transform:scaleY(1)}}}}
      .fade{{animation:appear .85s ease-out both}}
      .glow{{animation:gleam 6s ease-in-out infinite}}
      .bar{{transform-box:fill-box;transform-origin:center bottom;animation:grow .8s ease-out both}}
      @media (prefers-reduced-motion:reduce){{.fade,.glow,.bar{{animation:none!important;opacity:1!important;transform:none!important}}}}
      ]]></style>
    </defs>
    {rect(1,1,width-2,height-2,'url(#surface)',22, f'stroke="{STROKE}"') if background else ''}
    {content}
    </svg>'''
    return base


def save(name, content):
    (CARDS / name).write_text(content + "\n", encoding="utf-8")


def render_hero():
    out = []
    # Subtle product-flow geometry in the right-hand column; no moons or orbits.
    out.append(rect(751, 55, 168, 225, '#E9ECF5', 20, other='stroke="#D9DDEE"'))
    out.append(t(770, 84, 'HOW I THINK', 12, LILAC, 750, other='letter-spacing="1.5"'))
    for k, (y, label) in enumerate([(110, 'Discover'), (165, 'Design'), (220, 'Deliver')]):
        out.append(rect(771, y, 126, 43, '#F7F7FA', 10, other='stroke="#D3D5E7"'))
        out.append(rect(780, y+15, 13, 13, '#776ECE', 3))
        out.append(t(803, y+28, label, 15, INK, 650))
        if k != 2:
            out.append(f'<path d="M834 {y+43} v12" stroke="{LILAC}" stroke-width="1.5" stroke-dasharray="3 3"/>')
    out.append(t(45,52,'PRODUCT THINKING / SOFTWARE ENGINEERING',14,LILAC,700,cls='fade'))
    out.append(t(43,120,'Selina',65,INK,750,cls='fade'))
    out.append(t(245,120,'Liu',65,LILAC,family='Georgia, Times New Roman, serif',cls='fade',other='font-style="italic"'))
    out.append(t(46,158,'Yen-Chun Liu  ·  Sydney, Australia  ·  UTS Master of IT',18,MUTED))
    out.append(t(46,202,'I build thoughtful software where product',22,INK,500))
    out.append(t(46,231,'and engineering meet.',22,INK,500))
    out.append(rect(46,259,398,36,'#E6E4F6',18,other='stroke="#D4D0EE"'))
    out.append(t(64,283,'DISCOVER   /   DESIGN   /   BUILD   /   TEST',13,'#4F4C7B',700))
    out.append(t(47,320,'SwiftUI  ·  Privacy-aware AI  ·  Data products',16,MUTED))
    save('hero.svg',svg(1000,344,''.join(out),'Selina Liu','Product-minded software developer working with SwiftUI, responsible AI, and data products'))


def load_contributions():
    if not DATA.is_file(): return None
    try:
        v=json.loads(DATA.read_text(encoding='utf-8'))
        days=v.get('days',[])
        parsed={}
        for d in days:
            day=dt.date.fromisoformat(d['date'])
            n=int(d['count'])
            if n<0: raise ValueError('negative count')
            parsed[day]=n
        # Fail closed on partial/unrecognised source data; avoid bogus statistics.
        if len(parsed)<330: return None
        return parsed
    except (ValueError,TypeError,KeyError,json.JSONDecodeError):
        return None


def grid_dates(data):
    # Exactly 53 weekly columns, Sunday-first, including today.
    end=max(data) if data else dt.date.today()
    week_start = end - dt.timedelta(days=(end.weekday()+1)%7)
    start = week_start - dt.timedelta(weeks=52)
    return start,end


def render_heatmap(data):
    out=[t(44,53,'Every day,',26,INK,600),t(188,53,'in moonlight',28,LILAC,family='Georgia, Times New Roman, serif',other='font-style="italic"')]
    out.append(t(955,51,'GITHUB CONTRIBUTIONS',12,FAINT,650,other='text-anchor="end" letter-spacing="2"'))
    pitch=16.45; size=12.3; gx=44; gy=87
    start,end=grid_dates(data)
    for col in range(53):
        for row in range(7):
            day=start+dt.timedelta(days=col*7+row)
            val=(data or {}).get(day,0)
            if day>end: continue
            if data:
                level=0 if val==0 else 1 if val<=2 else 2 if val<=5 else 3 if val<=10 else 4
                color=VIOLET[level]
            else:
                color='#E2E4EC'
            x=round(gx+col*pitch,2); y=gy+row*17
            out.append(rect(x,y,size,size,color,3))
    # All month annotations below the grid (grid ends at y201.3)
    last_mon=None; last_label_col=-5
    for col in range(53):
        day=start+dt.timedelta(weeks=col)
        mon=(day.year,day.month)
        if mon!=last_mon and col-last_label_col>=4:
            out.append(t(round(gx+col*pitch,2),229,calendar.month_abbr[day.month],12,MUTED))
            last_label_col=col
        last_mon=mon
    if data:
        out.append(t(47,260,'A YEAR OF WORK, ONE DAY AT A TIME',12,FAINT,650,other='letter-spacing="1.5"'))
    else:
        out.append(t(47,260,'AWAITING FIRST GITHUB ACTIVITY SYNC',12,FAINT,650,other='letter-spacing="1.5"'))
    out.append(t(795,260,'less',12,MUTED))
    for j,c in enumerate(VIOLET):
        out.append(rect(834+j*19,250,13,13,c,3))
    out.append(t(950,260,'more',12,MUTED))
    save('heatmap.svg',svg(1000,281,''.join(out),'GitHub contribution calendar','Genuine daily contribution data in Moonshade Silver colors' if data else 'Contribution calendar awaiting GitHub Actions data sync'))


def streak_stats(data):
    end=max(data)
    ordered=sorted(data)
    total=sum(data.values())
    active=sum(v>0 for v in data.values())
    busiest=max(data.values())
    longest=cur=0
    for d in ordered:
        if data[d]>0:
            cur+=1;longest=max(longest,cur)
        else:cur=0
    latest=end if data.get(end,0)>0 else end-dt.timedelta(days=1)
    cur=0
    while data.get(latest,0)>0:
        cur+=1;latest-=dt.timedelta(days=1)
    # Match screenshot's month bars, with real values only.
    months={}
    for d,v in data.items():
        key=(d.year,d.month)
        months[key]=months.get(key,0)+v
    keys=[]
    year,month=end.year,end.month
    for k in range(11,-1,-1):
        idx=year*12+(month-1)-k
        keys.append((idx//12,idx%12+1))
    monthly=[(calendar.month_abbr[m],months.get((y,m),0)) for y,m in keys]
    return dict(total=total,active=active,busiest=busiest,current=cur,longest=longest,monthly=monthly)


def render_streak(data):
    out=[t(44,44,'THE LAST 12 MONTHS ON GITHUB',12,FAINT,700,other='letter-spacing="2"')]
    if data:
        st=streak_stats(data)
        total=f"{st['total']:,}"
        out.append(t(44,113,total,55,INK,400,family='Georgia, Times New Roman, serif'))
        num_x=45+max(100,len(total)*31)
        out.append(t(num_x,113,'contributions',52,INK,family='Georgia, Times New Roman, serif',other='font-style="italic"'))
    else:
        st=None
        out.append(t(44,113,'Your',53,INK,400,family='Georgia, Times New Roman, serif'))
        out.append(t(198,113,'contribution story',48,INK,family='Georgia, Times New Roman, serif',other='font-style="italic"'))
        out.append(t(47,145,'Counts appear after the first GitHub Actions sync.',16,MUTED))
    base=278
    max_bar=max((n for _,n in st['monthly']),default=0) if st else 0
    for i in range(12):
        x=47+i*50
        val=st['monthly'][i][1] if st else 0
        h=round(113*math.sqrt(val/max_bar),1) if max_bar and val else 4
        x2=x; y=base-h
        color=LILAC_STRONG if val==max_bar and max_bar>0 else INK
        if not st: color='#D3D6E2'
        out.append(rect(x2,y,34,h,color,4,other='class="bar"'))
        lab=st['monthly'][i][0] if st else calendar.month_abbr[(i+10)%12+1]
        out.append(t(x+4,303,lab,11,MUTED))
    # Right column starts at x700, no interaction with bars ending at x631.
    out.append('<path d="M673 42 V306" stroke="#D9DEE8" stroke-width="1"/>')
    if st:
        stats=[(f"{st['current']} days",f"current streak · {st['longest']} longest"),(f"{st['active']} / {len(data)}",'days with contributions'),(str(st['busiest']),'on the busiest day')]
    else:
        stats=[('—','current streak'),('—','active days'),('—','busiest day')]
    for j,(main,sub) in enumerate(stats):
        y=100+j*90
        out.append(t(704,y,main,32,INK,400,family='Georgia, Times New Roman, serif'))
        out.append(t(705,y+24,sub,16,MUTED))
        if j<2:out.append(f'<path d="M704 {y+43} H952" stroke="#D4D8E1"/>')
    save('streak.svg',svg(1000,327,''.join(out),'GitHub yearly activity','Actual contribution totals, monthly bar chart and streak statistics' if data else 'Awaiting verified GitHub contribution data'))


def focus_card(name,num,title,lines,gradient,accent):
    out=[rect(1,1,320,200,f'url(#{gradient})',19,other='stroke="#4E526F"')]
    out.append(t(25,43,num,13,accent,700,other='letter-spacing="1"'))
    # Minimal linked squares repeat the hero's workflow motif, not the old moon symbol.
    for k, y in enumerate((27,38,49)):
        out.append(rect(276-k*9,y,12,12,'none',3,other=f'stroke="{accent}" stroke-opacity=".66"'))
    out.append(t(25,100,title,36,'#F5F6FC',750))
    for i,line in enumerate(lines):out.append(t(25,136+23*i,line,15,'#D7DAEC'))
    out.append('<path d="M25 180 H295" stroke="#777992" stroke-opacity=".65"/>')
    out.append('<path d="M278 184 L290 172 M282 172 H290 V180" fill="none" stroke="#B8B5ED" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>')
    save(name,svg(322,202,''.join(out),title,'Focus area: '+title,False))


def render_focus():
    focus_card('product.svg','01','PRODUCT',['User research to product decisions','Clear stories, practical UX'],'night','#BEAAFF')
    focus_card('engineering.svg','02','BUILD',['SwiftUI apps and maintainable code','Architecture, testing, accessibility'],'twilight','#B8CEFF')
    focus_card('data.svg','03','INSIGHT',['Privacy-aware AI and analytics','Turning evidence into decisions'],'dusk','#DFDBFF')


def project_card(name,title,tag,lines,stack,idx):
    out=[t(24,40,f'0{idx}   /   SELECTED WORK',12,LILAC,750,other='letter-spacing="1"')]
    out.append(t(24,86,title,26,INK,700))
    for i,line in enumerate(lines):out.append(t(24,117+i*22,line,15,MUTED))
    out.append('<path d="M24 175 H298" stroke="#D8DCE6"/>')
    out.append(t(24,200,stack,13,'#585D76',650))
    out.append(f'<path d="M280 202 L294 188 M285 188 H294 V197" fill="none" stroke="{LILAC}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>')
    save(name,svg(322,222,''.join(out),title,tag))


def render_projects():
    project_card('fridgefix.svg','FridgeFix','iOS recipe recommendations',['Pantry-aware meal choices,','explanations and feedback.'],'Swift  ·  SwiftUI  ·  MVVM',1)
    project_card('smarttrip.svg','SmartTrip 2.0','iOS trip planning',['Travel planning, itinerary','and local-first memories.'],'SwiftUI  ·  Core Data',2)
    project_card('research.svg','Research Dashboard','Funding analysis',['Australian university funding','analysis and live exploration.'],'Python  ·  Plotly',3)
    title=t(25,47,"What I'm",30,INK,700)+t(180,47,'building',34,LILAC,family='Georgia, Times New Roman, serif',other='font-style="italic"')
    save('title-work.svg',svg(1000,77,title,'What I am building','Featured software and data projects',True))


def main():
    data=load_contributions()
    render_hero()
    render_heatmap(data)
    render_streak(data)
    render_focus()
    render_projects()
    print(f'Rendered 10 SVG cards; real GitHub activity: {"loaded" if data else "awaiting sync"}')

if __name__=='__main__':main()
