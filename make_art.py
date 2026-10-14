from PIL import Image, ImageDraw, ImageFont
S=3000; im=Image.new("RGB",(S,S)); d=ImageDraw.Draw(im)
for y in range(S):
    t=y/S; d.line([(0,y),(S,y)],fill=(int(20+60*t),int(24+10*t),int(70+90*t)))
for i,r in enumerate([1100,850,600]):
    d.ellipse([S/2-r,1150-r*0.6,S/2+r,1150+r*0.6],outline=(120+40*i,200,255),width=18)
for k in range(-6,7):
    h=abs(160-abs(k)*22)+40; x=S/2+k*90; d.rounded_rectangle([x-25,1150-h,x+25,1150+h],12,fill=(255,255,255))
F="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; F2="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
def c(txt,f,y,col):
    w=d.textlength(txt,font=f); d.text(((S-w)/2,y),txt,font=f,fill=col)
c("Daily Pod",ImageFont.truetype(F,400),1900,(255,255,255))
c("Curated for Vikram",ImageFont.truetype(F2,170),2400,(170,215,255))
im.save("cover.jpg",quality=85,optimize=True)
