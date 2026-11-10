#!/usr/bin/env python3
"""Read genuine public GitHub contribution data using GitHub GraphQL.

Requires GITHUB_TOKEN from GitHub Actions. No invented activity numbers.
"""
import datetime as dt
import json
import os
import urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TOKEN=os.environ.get('GITHUB_TOKEN')
if not TOKEN:
    raise SystemExit('GITHUB_TOKEN not provided; refusing to create fictional activity')

query='''query($login: String!){user(login: $login){contributionsCollection{contributionCalendar{totalContributions weeks{contributionDays{date contributionCount contributionLevel}}}}}}'''
body=json.dumps({'query':query,'variables':{'login':'ycl2001'}}).encode('utf-8')
req=urllib.request.Request('https://api.github.com/graphql',data=body,headers={
    'Authorization':'Bearer '+TOKEN,'User-Agent':'Moonshade-GitHub-Profile','Accept':'application/vnd.github+json','Content-Type':'application/json'},method='POST')
with urllib.request.urlopen(req,timeout=25) as resp:
    payload=json.load(resp)
if payload.get('errors'):
    raise SystemExit('GitHub GraphQL returned errors: '+str(payload['errors']))
cal=payload.get('data',{}).get('user',{}).get('contributionsCollection',{}).get('contributionCalendar',{})
weeks=cal.get('weeks') or []
days=[{'date':d['date'],'count':int(d['contributionCount']),'level':d['contributionLevel']} for w in weeks for d in w['contributionDays']]
if len(days)<330 or any(d['count']<0 for d in days):
    raise SystemExit('Incomplete GitHub response; retained existing cards')
# Guard against invalid/partial payload rather than publishing incorrect stats.
if sum(d['count'] for d in days)!=cal.get('totalContributions'):
    raise SystemExit('Contribution count mismatch; refusing to overwrite cards')
path=ROOT/'data'/'contributions.json';path.parent.mkdir(parents=True,exist_ok=True)
path.write_text(json.dumps({'source':'GitHub GraphQL contributionCalendar','fetched_at':dt.datetime.now(dt.timezone.utc).isoformat(),'days':days},indent=2)+'\n',encoding='utf-8')
print(f"Verified {len(days)} daily records, {cal['totalContributions']} contributions")
