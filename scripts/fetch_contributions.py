#!/usr/bin/env python3
"""Fetch public GitHub contribution calendar. Failure leaves existing data intact."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.request import Request,urlopen
import json,datetime,re

class Calendar(HTMLParser):
    def __init__(self):
        super().__init__();self.days={}
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        # GitHub contribution calendar has used both <td> and <tool-tip> elements;
        # parse only elements bearing actual dates + a numeric count.
        day=a.get('data-date') or a.get('date')
        count=a.get('data-count') or a.get('data-contribution-count')
        if not day or count is None:return
        try:
            datetime.date.fromisoformat(day)
            n=int(count)
            if n>=0:self.days[day]=n
        except ValueError:pass

url='https://github.com/users/ycl2001/contributions'
req=Request(url,headers={'User-Agent':'GitHub-Profile-Card-Generator/1.0','Accept':'text/html'})
with urlopen(req,timeout=20) as resp:html=resp.read().decode('utf-8','replace')
p=Calendar();p.feed(html)
if len(p.days)<100:
    # GitHub sometimes exposes data through aria-labels instead of data-count;
    # abort rather than publish fabricated or incomplete statistics.
    raise RuntimeError(f'Contribution markup not recognised ({len(p.days)} dated cells); kept previous data')
path=Path(__file__).resolve().parents[1]/'data'/'contributions.json'
path.parent.mkdir(parents=True,exist_ok=True)
path.write_text(json.dumps({'source':url,'fetched_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'days':[{'date':k,'count':v} for k,v in sorted(p.days.items())]},indent=2)+'\n')
print('Captured',len(p.days),'public GitHub contribution days')
