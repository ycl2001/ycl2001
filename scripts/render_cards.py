#!/usr/bin/env python3
"""Render self-contained, GitHub-safe animated SVG profile cards (no dependencies)."""
from pathlib import Path
import html, os, json, datetime, calendar
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'cards'; OUT.mkdir(exist_ok=True)
STATIC=os.getenv('STATIC')=='1'
INK='#e5e7f0'; MUTED='#a5acc5'; BG='#10101b'; PANEL='#191a2b'; STROKE='#41425c'; VIOLET='#9e91fa'; SILVER='#cbd2e9'; BLUE='#91bee7'

def esc(s):return html.escape(str(s),quote=True)
def svg(w,h,inside):
    anim='' if STATIC else '''
    @keyframes appear{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:translateY(0)}}
    @keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-5px)}}
    @keyframes breathe{0%,100%{opacity:.42}50%{opacity:.9}}
    @keyframes draw{from{stroke-dashoffset:500}to{stroke-dashoffset:0}}
    @keyframes grow{from{transform:scaleY(.08)}to{transform:scaleY(1)}}
    .fade{opacity:0;animation:appear .8s cubic-bezier(.2,.7,.2,1) forwards}
    .float{animation:float 6s ease-in-out infinite}
    .breathe{animation:breathe 4s ease-in-out infinite}
    .line{stroke-dasharray:500;animation:draw 2.2s ease forwards}
    .bar{transform-box:fill-box;transform-origin:center bottom;animation:grow .8s ease-out both}
    @media(prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;opacity:1!important;transform:none!important}}
    '''
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img"><defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#16172a"/><stop offset="1" stop-color="#0c0d17"/></linearGradient><linearGradient id="shine" x1="0" y1="0" x2="1" y2="0"><stop stop-color="#d8def8"/><stop offset=".6" stop-color="#9889ef"/><stop offset="1" stop-color="#8bbce7"/></linearGradient><style><![CDATA[
    text{{font-family: -apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif}}
    {anim}
    ]]></style></defs>{inside}</svg>'''
def panel(w,h):return f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="22" fill="url(#bg)" stroke="{STROKE}" stroke-opacity=".8"/>'
def txt(x,y,s,size=18,color=INK,weight=400,cls='',extra=''):return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}" class="{cls}" {extra}>{esc(s)}</text>'
def write(name,body): (OUT/name).write_text(body,encoding='utf-8')

# Hero: moonshade visual language; animated halo and architecture diagram.
w,h=1000,345
p=[panel(w,h),'<circle cx="845" cy="155" r="120" fill="none" stroke="#6665ad" stroke-width="1.4" opacity=".55"/>','<circle cx="845" cy="155" r="94" fill="none" stroke="#a49be7" opacity=".6" stroke-dasharray="4 7"/>','<circle cx="845" cy="155" r="68" fill="#2f3053"/>','<circle cx="864" cy="143" r="64" fill="#151629"/>', '<path d="M785 257 Q845 280 908 255" fill="none" stroke="#a99ef4" stroke-width="2" class="line"/>', '<circle cx="845" cy="155" r="130" fill="none" stroke="#7775b6" stroke-dasharray="1 15" opacity=".45" class="breathe"/>']
p += [txt(46,57,'PRODUCT THINKING  /  SOFTWARE ENGINEERING',14,VIOLET,700,'fade', 'style="animation-delay:.05s"'),txt(46,124,"Hi, I'm Selina.",59,INK,750,'fade','style="animation-delay:.15s"'),txt(48,171,'Yen-Chun Liu  ·  Sydney, Australia',19,SILVER,450,'fade','style="animation-delay:.30s"'),txt(48,224,'I turn complex problems into thoughtful, testable software.',21,INK,450,'fade','style="animation-delay:.43s"'),txt(48,264,'SwiftUI   /   Privacy-aware AI   /   Data products',17,MUTED,450,'fade','style="animation-delay:.55s"'),'<rect x="46" y="290" width="313" height="33" rx="16" fill="#27273e" stroke="#535273"/>',txt(63,312,'DISCOVER  /  DESIGN  /  BUILD  /  TEST',12,SILVER,650)]
write('hero.svg',svg(w,h,''.join(p)))

def focus_card(slug,num,title,subtitle,detail,accent,delay):
 w,h=318,237
 p=[panel(w,h),f'<circle cx="263" cy="56" r="39" fill="none" stroke="{accent}" stroke-width="1.3" opacity=".55" class="float"/>',f'<circle cx="263" cy="56" r="25" fill="{accent}" opacity=".12"/>',txt(24,49,num,15,accent,700),txt(24,103,title,34,INK,700,'fade',f'style="animation-delay:{delay}s"'),txt(24,140,subtitle,17,SILVER),txt(24,176,detail,14,MUTED),f'<path d="M24 203 H284" stroke="{accent}" stroke-opacity=".6"/>',txt(264,221,'+',21,accent,600)]
 write(slug+'.svg',svg(w,h,''.join(p)))
focus_card('product','01','PRODUCT','Discovery to delivery','Research · requirements · UX',VIOLET,.15)
focus_card('engineering','02','BUILD','Apple-platform software','Swift · SwiftUI · testing',BLUE,.25)
focus_card('data','03','INSIGHT','Responsible decisions','Privacy · analytics · AI',SILVER,.35)

def repo(slug,tag,title,lines,stack,accent):
 w,h=1000,205;p=[panel(w,h),f'<rect x="25" y="25" width="6" height="155" rx="3" fill="{accent}"/>',txt(52,51,tag.upper(),13,accent,700),txt(52,93,title,32,INK,700,'fade','style="animation-delay:.14s"')]
 for i,line in enumerate(lines):p.append(txt(52,124+27*i,line,18,SILVER))
 p.extend([txt(52,182,stack,13,MUTED,550),'<path d="M895 80 L950 80 L950 135" fill="none" stroke="#67688b" stroke-width="2" class="line"/>',txt(937,165,'+',32,accent,600)])
 write(slug+'.svg',svg(w,h,''.join(p)))
repo('reporting','macOS · Product engineering','Project Reporting Builder',['Transform project updates and metrics into reusable reports,','with native export, accessible cards and local history.'],'SwiftUI  ·  Swift Testing  ·  XCTest',VIOLET)
repo('smarttrip','iOS · Travel workflows','SmartTrip 2.0',['A local-first travel planner connecting saved places, itineraries,','and memories through a modular SwiftUI architecture.'],'SwiftUI  ·  Core Data  ·  MapKit',BLUE)
repo('research','Data · Visualisation','Research Block Grant Dashboard',['Explore Australian university funding trends with a transparent,','reproducible interactive dashboard.'],'Python  ·  JavaScript  ·  Plotly',SILVER)

# Activity SVG uses only true sourced contribution counts when data exists.
path=ROOT/'data'/'contributions.json'
if path.exists():
 try: days=json.loads(path.read_text())['days']
 except Exception:days=[]
else:days=[]
# Filter date/value pairs, never invent activity.
valid=[]
for d in days:
 try:
  date=datetime.date.fromisoformat(d['date']); n=int(d['count']); assert n>=0
  valid.append((date,n))
 except (ValueError,KeyError,AssertionError,TypeError):pass
valid=sorted(dict(valid).items())
w,h=1000,260;p=[panel(w,h),txt(38,47,'CONTRIBUTION ACTIVITY',15,VIOLET,700),txt(38,84,'A year of building',30,INK,700)]
if valid:
 last=valid[-1][0];start=datetime.date(last.year,last.month,1)
 months=[]
 for off in range(11,-1,-1):
  yy=start.year+(start.month-1-off)//12; mm=(start.month-1-off)%12+1
  months.append((yy,mm))
 totals={(y,m):sum(n for d,n in valid if (d.year,d.month)==(y,m)) for y,m in months}
 highest=max(totals.values()) or 1
 for i,(key,value) in enumerate(totals.items()):
  x=43+i*77; bh=round(value/highest*84)
  p.extend([f'<rect class="bar" style="animation-delay:{i*.075:.2f}s" x="{x}" y="{203-bh}" width="38" height="{max(bh,2)}" rx="5" fill="{VIOLET if value==highest else BLUE}" opacity=".9"/>',txt(x,224,calendar.month_abbr[key[1]],13,MUTED),txt(x,194-bh,str(value),11,SILVER)])
 p.append(txt(652,80,f'{sum(n for _,n in valid):,} contributions in the loaded period',15,SILVER))
else:
 p.extend([txt(39,130,'Live activity lives on GitHub. No estimated counts or synthetic data.',19,SILVER),txt(39,167,'Run the included GitHub Action to populate monthly bars with real activity.',16,MUTED),'<path d="M42 205 H956" stroke="#474967" stroke-dasharray="8 8"/>'])
write('activity.svg',svg(w,h,''.join(p)))
print('Rendered',len(list(OUT.glob('*.svg'))),'SVG cards', 'with activity' if valid else '(activity data pending)')
