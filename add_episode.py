#!/usr/bin/env python3
"""Usage: add_episode.py <audio file|URL> "<title>" "<description>" [--start SECONDS] [--image FILE|URL] [--no-push] [--date RFC822]
Artwork: --image wins; otherwise a URL source auto-fetches its thumbnail; otherwise falls back to cover-milkyway.jpg (the show cover).
Art is made 3000x3000 RGB JPG (blurred fill + centred thumbnail) in episodes/epNNN-*.jpg."""
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
<description>A daily curated listen on AI and the people building it. Curated for Vikram. Cover: ESO/Yuri Beletsky, CC BY 4.0.</description>
<language>en</language>
<itunes:author>Daily Pod</itunes:author>
<itunes:owner><itunes:name>Daily Pod</itunes:name><itunes:email>vikramgorur@gmail.com</itunes:email></itunes:owner>
<itunes:image href="{BASE}/cover-milkyway.jpg"/>
<image><url>{BASE}/cover-milkyway.jpg</url><title>Daily Pod</title><link>{BASE}/</link></image>
<itunes:category text="Technology"/>
<itunes:explicit>false</itunes:explicit>
<itunes:block>Yes</itunes:block>
<itunes:type>episodic</itunes:type>
<!--ITEMS-->
</channel>
</rss>
'''
p=argparse.ArgumentParser(); p.add_argument("src"); p.add_argument("title"); p.add_argument("description")
p.add_argument("--start",type=float,default=0); p.add_argument("--no-push",action="store_true"); p.add_argument("--date"); p.add_argument("--image")
a=p.parse_args()
def make_art(img_in,out):
    vf=("[0:v]split[a][b];[a]scale=3000:3000:force_original_aspect_ratio=increase,crop=3000:3000,boxblur=40:5,eq=brightness=-0.15[bg];"
        "[b]scale=3000:3000:force_original_aspect_ratio=decrease[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,format=yuvj420p")
    subprocess.run(["ffmpeg","-loglevel","error","-y","-i",img_in,"-filter_complex",vf,"-frames:v","1","-q:v","2",out+".tmp.jpg"],check=True)
    from PIL import Image
    Image.open(out+".tmp.jpg").convert("RGB").save(out,"JPEG",quality=82,optimize=True,progressive=False,dpi=(72,72)); os.remove(out+".tmp.jpg")
def embed_art(mp3,jpg):
    from PIL import Image
    small=mp3+".cover.jpg"; Image.open(jpg).resize((1400,1400)).save(small,"JPEG",quality=85,dpi=(72,72))
    tmpo=mp3+".tmp.mp3"
    subprocess.run(["ffmpeg","-loglevel","error","-y","-i",mp3,"-i",small,"-map","0:a","-map","1:0","-c","copy","-id3v2_version","3",
        "-metadata:s:v","title=Album cover","-metadata:s:v","comment=Cover (front)","-disposition:v","attached_pic",tmpo],check=True)
    os.replace(tmpo,mp3); os.remove(small)
def fetch_img(u,tmp):
    if re.match(r"https?://.*\.(jpe?g|png|webp)(\?|$)",u,re.I):
        f=f"{tmp}/img"; subprocess.run(["curl","-sfL","-o",f,u],check=True); return f
    subprocess.run([YTDLP,"-q","--skip-download","--write-thumbnail","--convert-thumbnails","jpg","-o",f"{tmp}/thumb",u],check=True)
    return glob.glob(f"{tmp}/thumb*.jpg")[0]
src=a.src; tmp=tempfile.mkdtemp(); url_src=src if re.match(r"https?://",src) else None
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
img_src=a.image or url_src
art_tag=f'<itunes:image href="{BASE}/cover-milkyway.jpg"/>'
if img_src:
    try:
        f=fetch_img(img_src,tmp) if re.match(r"https?://",img_src) else img_src
        art=name[:-4]+"-art.jpg"; make_art(f,f"{D}/episodes/{art}")
        art_tag=f'<itunes:image href="{BASE}/episodes/{art}"/>'
    except Exception as e: print("artwork failed, using cover-milkyway.jpg:",e); art=None
else: art=None
# ID3 art embedding disabled: broke Apple Podcasts follow (see commit history)
size=os.path.getsize(out)
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
{art_tag}
<itunes:explicit>false</itunes:explicit>
</item>
'''
fp=f"{D}/feed.xml"
feed=open(fp).read() if os.path.exists(fp) else HEAD
feed=feed.replace("<!--ITEMS-->\n","<!--ITEMS-->\n"+item,1)
open(fp,"w").write(feed)
open(f"{D}/feed2.xml","w").write(feed.replace('/feed.xml" rel="self"','/feed2.xml" rel="self"'))
import xml.dom.minidom; xml.dom.minidom.parse(fp)
print("added",name,size,"bytes")
if not a.no_push:
    subprocess.run(["git","-C",D,"add","-A"],check=True)
    subprocess.run(["git","-C",D,"commit","-qm",f"Add episode {n}: {a.title}"],check=True)
    subprocess.run(["git","-C",D,"push","-q","origin","main"],check=True)
