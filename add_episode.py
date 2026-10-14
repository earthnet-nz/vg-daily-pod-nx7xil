#!/usr/bin/env python3
"""Usage: add_episode.py <audio file|URL> "<title>" "<description>" [--start SECONDS] [--no-push] [--date RFC822]"""
import sys, os, re, subprocess, argparse, glob, tempfile, html, email.utils, time
from xml.sax.saxutils import escape
D=os.path.dirname(os.path.abspath(__file__))
BASE="https://earthnet-nz.github.io/vg-daily-pod-nx7xil"
YTDLP=os.path.expanduser("~/.local/bin/yt-dlp")
HEAD=f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
<title>Daily Pod</title>
<link>{BASE}/</link>
<atom:link href="{BASE}/feed.xml" rel="self" type="application/rss+xml"/>
<description>A daily curated listen on AI and the people building it. Curated for Vikram.</description>
<language>en</language>
<itunes:author>Daily Pod</itunes:author>
<itunes:owner><itunes:name>Daily Pod</itunes:name></itunes:owner>
<itunes:image href="{BASE}/cover.jpg"/>
<image><url>{BASE}/cover.jpg</url><title>Daily Pod</title><link>{BASE}/</link></image>
<itunes:category text="Technology"/>
<itunes:explicit>false</itunes:explicit>
<itunes:block>Yes</itunes:block>
<itunes:type>episodic</itunes:type>
<!--ITEMS-->
</channel>
</rss>
'''
p=argparse.ArgumentParser(); p.add_argument("src"); p.add_argument("title"); p.add_argument("description")
p.add_argument("--start",type=float,default=0); p.add_argument("--no-push",action="store_true"); p.add_argument("--date")
a=p.parse_args()
src=a.src; tmp=tempfile.mkdtemp()
if re.match(r"https?://",src):
    subprocess.run([YTDLP,"-f","bestaudio/best","-o",f"{tmp}/in.%(ext)s",src],check=True)
    src=glob.glob(f"{tmp}/in.*")[0]
n=len(glob.glob(f"{D}/episodes/ep*.mp3"))+1
slug=re.sub(r"[^a-z0-9]+","-",a.title.lower()).strip("-")[:50]
name=f"ep{n:03d}-{slug}.mp3"; out=f"{D}/episodes/{name}"
os.makedirs(f"{D}/episodes",exist_ok=True)
cmd=["ffmpeg","-loglevel","error","-y"]+(["-ss",str(a.start)] if a.start else [])+["-i",src,"-vn","-ac","1","-b:a","64k",out]
subprocess.run(cmd,check=True)
size=os.path.getsize(out)
if size>95*1024*1024: sys.exit("mp3 > 95 MB; GitHub limit is 100 MB")
dur=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",out]).strip())
h,m,s=int(dur//3600),int(dur%3600//60),int(dur%60)
date=a.date or email.utils.formatdate(time.time(),usegmt=True)
item=f'''<item>
<title>{escape(a.title)}</title>
<description>{escape(a.description)}</description>
<itunes:summary>{escape(a.description)}</itunes:summary>
<enclosure url="{BASE}/episodes/{name}" length="{size}" type="audio/mpeg"/>
<guid isPermaLink="false">daily-pod-{name}</guid>
<pubDate>{date}</pubDate>
<itunes:duration>{h:02d}:{m:02d}:{s:02d}</itunes:duration>
<itunes:episode>{n}</itunes:episode>
<itunes:explicit>false</itunes:explicit>
</item>
'''
fp=f"{D}/feed.xml"
feed=open(fp).read() if os.path.exists(fp) else HEAD
feed=feed.replace("<!--ITEMS-->\n","<!--ITEMS-->\n"+item,1)
open(fp,"w").write(feed)
import xml.dom.minidom; xml.dom.minidom.parse(fp)
print("added",name,size,"bytes")
if not a.no_push:
    subprocess.run(["git","-C",D,"add","-A"],check=True)
    subprocess.run(["git","-C",D,"commit","-qm",f"Add episode {n}: {a.title}"],check=True)
    subprocess.run(["git","-C",D,"push","-q","origin","main"],check=True)
