#!/usr/bin/env python3
"""像素风办公室 1600x650 — 6部门+走廊+丰富墙面"""
import struct, zlib, os, math, random

random.seed(42)
W, H = 1600, 650

def rgb(r,g,b): return (r,g,b)
def mix(c1,c2,t): return tuple(int(c1[i]*(1-t)+c2[i]*t) for i in range(3))
def darken(c,f=0.8): return tuple(max(0,int(v*f)) for v in c)
def lighten(c,f=1.2): return tuple(min(255,int(v*f)) for v in c)

# 墙壁
WALL_BASE=rgb(58,56,72); WALL_LIGHT=rgb(72,70,90); WALL_ACCENT=rgb(80,78,100)
BASEBOARD=rgb(75,62,48); BASEBOARD_HI=rgb(90,75,58)
# 地板
FLOOR_A=rgb(62,52,42); FLOOR_B=rgb(58,48,38); FLOOR_C=rgb(55,45,36); FLOOR_GRAIN=rgb(50,40,32)
# 走廊地板
HALL_A=rgb(70,65,58); HALL_B=rgb(65,60,53); HALL_LINE=rgb(85,78,65)
# 家具
DESK_TOP=rgb(155,105,55); DESK_SIDE=rgb(125,82,42); DESK_LEG=rgb(95,65,35)
MON_BODY=rgb(35,35,42); MON_BEZEL=rgb(25,25,30)
CHAIR_SEAT=rgb(55,55,68); CHAIR_WHEEL=rgb(35,35,38)
SOFA_BODY=rgb(85,75,95); SOFA_DARK=rgb(65,55,75); SOFA_CUSH=rgb(105,95,115)
TEA_TOP=rgb(135,95,50); TEA_LEG=rgb(105,72,38)
PLANT_TRUNK=rgb(90,60,35); PLANT_DARK=rgb(28,95,38); PLANT_MID=rgb(42,125,52); PLANT_LIGHT=rgb(58,155,68)
POT_BODY=rgb(155,95,55); POT_RIM=rgb(175,115,68)
SHELF_BG=rgb(115,75,42); SHELF_FR=rgb(85,55,30); SHELF_BD=rgb(100,65,35)
BOOK_COLORS=[rgb(195,55,55),rgb(55,55,195),rgb(55,170,55),rgb(195,175,35),rgb(175,55,175),rgb(55,155,175),rgb(195,120,55)]
BOARD_BG=rgb(242,240,228); BOARD_FR=rgb(85,68,48)
WIN_FRAME=rgb(65,65,80); WIN_SILL=rgb(80,80,95); SKY_TOP=rgb(100,150,210); SKY_BOT=rgb(160,200,240); CLOUD=rgb(220,232,245)
DIV_A=rgb(95,92,108); DIV_B=rgb(85,82,98); DIV_POST=rgb(70,68,82)
LABEL_C=rgb(160,155,145); TRASH_BODY=rgb(90,90,95); TRASH_RIM=rgb(105,105,110)
AC_BODY=rgb(230,228,222); AC_VENT=rgb(195,192,185); AC_DARK=rgb(170,168,162)
CLOCK_FACE=rgb(245,242,235); CLOCK_FR=rgb(85,65,45); CLOCK_HAND=rgb(30,30,30)

pixels=[(0,0,0)]*(W*H)
def put(x,y,c):
    if 0<=x<W and 0<=y<H: pixels[y*W+x]=c
def rect(x1,y1,x2,y2,c):
    for yy in range(max(0,y1),min(H,y2)):
        for xx in range(max(0,x1),min(W,x2)): pixels[yy*W+xx]=c
def rect_outline(x1,y1,x2,y2,c,t=1):
    rect(x1,y1,x2,y1+t,c); rect(x1,y2-t,x2,y2,c); rect(x1,y1,x1+t,y2,c); rect(x2-t,y1,x2,y2,c)
def circle_fill(cx,cy,r,c):
    for yy in range(cy-r,cy+r+1):
        for xx in range(cx-r,cx+r+1):
            if (xx-cx)**2+(yy-cy)**2<=r*r: put(xx,yy,c)
def ellipse_fill(cx,cy,rx,ry,c):
    if rx<=0 or ry<=0: return
    for yy in range(cy-ry,cy+ry+1):
        for xx in range(cx-rx,cx+rx+1):
            if ((xx-cx)/rx)**2+((yy-cy)/ry)**2<=1: put(xx,yy,c)


# ============ 布局参数 ============
WALL_H = 140  # 墙高(更高=更多墙面装饰空间)
COL_W = 470; ROW_H = 220
HALL_W = 30   # 走廊宽度
COL_X = [15, 15+COL_W+HALL_W, 15+2*(COL_W+HALL_W)]  # 15, 515, 1015
ROW_Y = [WALL_H+8, WALL_H+8+ROW_H+HALL_W]  # 148, 398

DEPTS = {
    'info': (0,0, rgb(55,62,72),rgb(50,57,67), rgb(62,58,72),rgb(57,53,67)),
    'dev':  (1,0, rgb(52,52,65),rgb(48,48,60), rgb(58,52,62),rgb(53,47,57)),
    'test': (2,0, rgb(60,55,65),rgb(55,50,60), rgb(65,58,62),rgb(60,53,57)),
    'fin':  (0,1, rgb(62,52,55),rgb(57,47,50), rgb(68,55,58),rgb(63,50,53)),
    'plan': (1,1, rgb(55,60,52),rgb(50,55,47), rgb(60,62,55),rgb(55,57,50)),
    'cmd':  (2,1, rgb(48,48,55),rgb(43,43,50), rgb(55,48,52),rgb(50,43,47)),
}
SCR_COLORS = {
    'info':rgb(80,130,190),'dev':rgb(45,160,100),'test':rgb(60,180,160),
    'fin':rgb(200,80,80),'plan':rgb(130,120,200),'cmd':rgb(200,160,60),
}

# ============ 1. 墙壁(渐变+砖纹+踢脚线) ============
for y in range(WALL_H):
    t = y/WALL_H
    for x in range(W):
        base = mix(WALL_BASE, WALL_LIGHT, t)
        by = y//24
        if y%24==0 or (x+(by%2)*24)%48==0: base=darken(base,0.92)
        # 墙面微妙色差
        if (x//200)%2==0: base=mix(base,WALL_ACCENT,0.05)
        pixels[y*W+x]=base
# 踢脚线(三层)
rect(0,WALL_H-10,W,WALL_H-6,darken(BASEBOARD,0.9))
rect(0,WALL_H-6,W,WALL_H,BASEBOARD)
rect(0,WALL_H-8,W,WALL_H-6,BASEBOARD_HI)
rect(0,WALL_H,W,WALL_H+3,darken(BASEBOARD,0.65))

# ============ 2. 木地板 ============
for y in range(WALL_H+3,H):
    for x in range(W):
        plank=x//64
        grain=math.sin(y*0.3+plank*17)*0.5+math.sin(x*0.05+plank*7)*0.3
        base=[FLOOR_A,FLOOR_B,FLOOR_C][plank%3]
        if abs(grain)>0.6: base=FLOOR_GRAIN
        if x%64<1: base=darken(FLOOR_GRAIN,0.8)
        pixels[y*W+x]=base

# ============ 3. 走廊(带地砖花纹+引导线) ============
# 垂直走廊
for cx_start in [COL_X[1]-HALL_W, COL_X[2]-HALL_W]:
    for y in range(WALL_H+3,H):
        for x in range(cx_start,cx_start+HALL_W):
            tx=(x-cx_start)//16; ty=(y-WALL_H)//16
            c=HALL_A if (tx+ty)%2==0 else HALL_B
            pixels[y*W+x]=c
    # 中线引导
    mx=cx_start+HALL_W//2
    for y in range(WALL_H+10,H-5,8):
        rect(mx-1,y,mx+1,y+4,HALL_LINE)

# 水平走廊
hy_start = ROW_Y[0]+ROW_H
for y in range(hy_start,hy_start+HALL_W):
    for x in range(15,W-15):
        tx=(x-15)//16; ty=(y-hy_start)//16
        c=HALL_A if (tx+ty)%2==0 else HALL_B
        pixels[y*W+x]=c
# 水平中线
my=hy_start+HALL_W//2
for x in range(20,W-20,8):
    rect(x,my-1,x+4,my+1,HALL_LINE)

# ============ 4. 部门区域地板(每个部门独特风格) ============
def floor_info(x, y, ox, oy):
    """情报室: 深蓝灰六边形瓷砖"""
    dx, dy = x-ox, y-oy
    hx = dx // 20; hy = dy // 18
    off = 10 if hy%2 else 0
    cx = (dx+off) % 20; cy = dy % 18
    edge = cx < 1 or cy < 1 or (cx+cy < 5) or (cx-cy > 15) or (cy-cx > 15)
    if edge: return rgb(40,50,62)
    return rgb(50,60,75) if (hx+hy)%2==0 else rgb(45,55,68)

def floor_dev(x, y, ox, oy):
    """开发区: 深色工业水泥+绿色LED条纹"""
    dx, dy = x-ox, y-oy
    base = rgb(48,48,55)
    if dy % 40 < 2: return rgb(40,120,70)  # 绿色LED地灯线
    noise = math.sin(dx*0.15+dy*0.08)*0.3
    if noise > 0.15: base = rgb(52,52,60)
    elif noise < -0.15: base = rgb(44,44,50)
    if dx % 60 < 1: base = darken(base, 0.85)
    return base

def floor_test(x, y, ox, oy):
    """测试区: 浅灰白实验室瓷砖+蓝色十字标记"""
    dx, dy = x-ox, y-oy
    tx, ty = dx//32, dy//32
    cx, cy = dx%32, dy%32
    if cx < 1 or cy < 1: return rgb(55,60,65)
    # 每隔几块放蓝色十字
    if (tx+ty)%5==0 and ((abs(cx-16)<2 and 8<cy<24) or (abs(cy-16)<2 and 8<cx<24)):
        return rgb(50,120,140)
    return rgb(58,62,68) if (tx+ty)%2==0 else rgb(54,58,64)

def floor_fin(x, y, ox, oy):
    """金融区: 深红木纹地板"""
    dx, dy = x-ox, y-oy
    plank = dx // 48
    grain = math.sin(dy*0.25+plank*13)*0.4+math.sin(dx*0.04+plank*5)*0.3
    base = rgb(72,42,35) if plank%2==0 else rgb(65,38,30)
    if abs(grain) > 0.5: base = rgb(58,32,25)
    if dx%48 < 1: base = rgb(50,28,22)
    return base

def floor_plan(x, y, ox, oy):
    """策划产品: 彩色拼接地毯"""
    dx, dy = x-ox, y-oy
    bx, by = dx//36, dy//36
    colors = [rgb(55,68,52),rgb(52,58,68),rgb(68,55,58),rgb(58,62,52),rgb(62,52,65),rgb(52,65,60)]
    base = colors[(bx*3+by*7)%len(colors)]
    # 地毯纹理
    if (dx+dy)%6 < 1: base = lighten(base, 1.08)
    if dx%36 < 1 or dy%36 < 1: base = darken(base, 0.88)
    return base

def floor_cmd(x, y, ox, oy):
    """指挥中心: 黑色大理石+金色纹路"""
    dx, dy = x-ox, y-oy
    base = rgb(35,33,38)
    vein = math.sin(dx*0.06+dy*0.04)*0.5+math.cos(dx*0.03-dy*0.06)*0.3
    if vein > 0.4: base = rgb(45,42,48)
    elif vein > 0.2: base = rgb(40,38,43)
    # 金色纹路
    gold = math.sin(dx*0.12+dy*0.08)*math.cos(dx*0.05-dy*0.1)
    if gold > 0.7: base = mix(base, rgb(90,75,40), 0.3)
    # 大理石光泽
    if (dx+dy*3)%67 < 2: base = lighten(base, 1.15)
    return base

FLOOR_FUNCS = {'info':floor_info,'dev':floor_dev,'test':floor_test,'fin':floor_fin,'plan':floor_plan,'cmd':floor_cmd}

# 休闲区地板风格
def rest_info(x, y, ox, oy):
    """情报室休闲: 暖木地板"""
    dx = x-ox; plank = dx//40
    base = rgb(72,58,45) if plank%2==0 else rgb(68,54,42)
    grain = math.sin((y-oy)*0.2+plank*11)*0.3
    if abs(grain)>0.2: base = rgb(62,50,38)
    return base

def rest_dev(x, y, ox, oy):
    """开发区休闲: 深色地毯"""
    dx, dy = x-ox, y-oy
    base = rgb(45,42,55)
    if (dx+dy)%4 < 1: base = rgb(50,47,60)
    return base

def rest_test(x, y, ox, oy):
    """测试区休闲: 竹地板"""
    dx = x-ox
    base = rgb(75,68,48) if (dx//12)%2==0 else rgb(70,64,44)
    return base

def rest_fin(x, y, ox, oy):
    """金融区休闲: 深色皮革纹"""
    dx, dy = x-ox, y-oy
    base = rgb(55,38,30)
    if math.sin(dx*0.2)*math.cos(dy*0.2) > 0.3: base = rgb(60,42,34)
    return base

def rest_plan(x, y, ox, oy):
    """策划休闲: 草绿地毯"""
    dx, dy = x-ox, y-oy
    base = rgb(48,62,42)
    if (dx+dy)%5 < 1: base = rgb(52,68,46)
    return base

def rest_cmd(x, y, ox, oy):
    """指挥中心休闲: 金色大理石(后面会被覆盖)"""
    return rgb(55,48,35)

REST_FUNCS = {'info':rest_info,'dev':rest_dev,'test':rest_test,'fin':rest_fin,'plan':rest_plan,'cmd':rest_cmd}

for dname,(col,row,of_a,of_b,re_a,re_b) in DEPTS.items():
    zx=COL_X[col]; zy=ROW_Y[row]
    # 办公区
    ox1,oy1=zx,zy; ox2=zx+int(COL_W*0.58); oy2=zy+ROW_H
    ff = FLOOR_FUNCS.get(dname, floor_info)
    for y in range(oy1,oy2):
        for x in range(ox1,ox2):
            pixels[y*W+x] = ff(x, y, ox1, oy1)
    rect_outline(ox1-1,oy1-1,ox2+1,oy2+1,darken(of_b,0.65),1)
    # 休闲区
    rx1=zx+int(COL_W*0.6); ry1=zy; rx2=zx+COL_W; ry2=zy+ROW_H
    rf = REST_FUNCS.get(dname, rest_info)
    for y in range(ry1,ry2):
        for x in range(rx1,rx2):
            pixels[y*W+x] = rf(x, y, rx1, ry1)
    rect_outline(rx1-1,ry1-1,rx2+1,ry2+1,darken(re_b,0.65),1)
    # 分隔线
    sx=zx+int(COL_W*0.59)
    for y in range(zy,zy+ROW_H):
        if (y//8)%2==0: put(sx,y,DIV_A)
        else: put(sx,y,DIV_B)


# ============ 5. 墙面装饰(窗户/空调/时钟/画/海报) ============
# --- 窗户(每列一个大窗) ---
for ci, cx in enumerate(COL_X):
    wx = cx + 100
    wy = 18
    ww, wh = 120, 80
    # 窗框
    rect(wx-3, wy-3, wx+ww+3, wy+wh+3, WIN_FRAME)
    rect(wx-1, wy-1, wx+ww+1, wy+wh+1, WIN_SILL)
    # 天空渐变
    for y in range(wy, wy+wh):
        t = (y-wy)/wh
        c = mix(SKY_TOP, SKY_BOT, t)
        for x in range(wx, wx+ww):
            pixels[y*W+x] = c
    # 云朵
    for ccx, ccy, cr in [(wx+25,wy+20,12),(wx+35,wy+16,10),(wx+80,wy+35,14),(wx+90,wy+30,10)]:
        ellipse_fill(ccx, ccy, cr, int(cr*0.6), CLOUD)
    # 窗格(十字)
    rect(wx+ww//2-1, wy, wx+ww//2+1, wy+wh, WIN_FRAME)
    rect(wx, wy+wh//2-1, wx+ww, wy+wh//2+1, WIN_FRAME)
    # 窗台
    rect(wx-5, wy+wh+1, wx+ww+5, wy+wh+6, WIN_SILL)
    rect(wx-5, wy+wh+6, wx+ww+5, wy+wh+8, darken(WIN_SILL,0.8))

    # 第二个窗(右侧)
    wx2 = cx + COL_W - 180
    rect(wx2-3, wy-3, wx2+ww+3, wy+wh+3, WIN_FRAME)
    rect(wx2-1, wy-1, wx2+ww+1, wy+wh+1, WIN_SILL)
    for y in range(wy, wy+wh):
        t = (y-wy)/wh
        c = mix(SKY_TOP, SKY_BOT, t)
        for x in range(wx2, wx2+ww):
            pixels[y*W+x] = c
    for ccx, ccy, cr in [(wx2+30,wy+25,11),(wx2+45,wy+18,13),(wx2+75,wy+40,10)]:
        ellipse_fill(ccx, ccy, cr, int(cr*0.6), CLOUD)
    rect(wx2+ww//2-1, wy, wx2+ww//2+1, wy+wh, WIN_FRAME)
    rect(wx2, wy+wh//2-1, wx2+ww, wy+wh//2+1, WIN_FRAME)
    rect(wx2-5, wy+wh+1, wx2+ww+5, wy+wh+6, WIN_SILL)
    rect(wx2-5, wy+wh+6, wx2+ww+5, wy+wh+8, darken(WIN_SILL,0.8))

# --- 空调(每列墙上方) ---
for ci, cx in enumerate(COL_X):
    ax = cx + COL_W//2 - 30
    ay = 5
    rect(ax, ay, ax+60, ay+14, AC_BODY)
    rect(ax+2, ay+6, ax+58, ay+8, AC_VENT)
    rect(ax+2, ay+9, ax+58, ay+11, AC_VENT)
    rect(ax+2, ay+12, ax+58, ay+13, AC_DARK)
    # LED灯
    put(ax+54, ay+3, rgb(50,200,50))
    rect_outline(ax, ay, ax+60, ay+14, darken(AC_BODY,0.85), 1)

# --- 时钟(中间列墙上) ---
clk_cx, clk_cy = COL_X[1]+COL_W//2, 50
circle_fill(clk_cx, clk_cy, 16, CLOCK_FACE)
circle_fill(clk_cx, clk_cy, 14, lighten(CLOCK_FACE,1.02))
rect_outline(clk_cx-16, clk_cy-16, clk_cx+16, clk_cy+16, CLOCK_FR, 2)
# 刻度
for i in range(12):
    a = i*math.pi/6
    ix = int(clk_cx + math.cos(a)*12)
    iy = int(clk_cy + math.sin(a)*12)
    put(ix, iy, CLOCK_HAND)
# 时针分针
for dx in range(-5,1): put(clk_cx+dx, clk_cy, CLOCK_HAND)
for dy in range(-8,1): put(clk_cx, clk_cy+dy, CLOCK_HAND)
circle_fill(clk_cx, clk_cy, 2, rgb(180,50,50))

# --- 墙面画/海报 ---
# 情报室: 世界地图
mx, my = COL_X[0]+260, 30
rect(mx, my, mx+50, my+32, rgb(30,60,90))
rect_outline(mx-1, my-1, mx+51, my+33, rgb(100,80,55), 2)
# 简易大陆轮廓
for px, py in [(mx+10,my+10),(mx+12,my+12),(mx+14,my+10),(mx+25,my+8),(mx+28,my+10),(mx+30,my+14),(mx+35,my+18),(mx+38,my+20),(mx+15,my+22),(mx+40,my+12)]:
    ellipse_fill(px, py, 3, 2, rgb(60,140,80))

# 开发区: 代码海报
px, py = COL_X[1]+260, 30
rect(px, py, px+45, py+30, rgb(25,25,35))
rect_outline(px-1, py-1, px+46, py+31, rgb(80,80,100), 1)
for i, c in enumerate([rgb(100,200,100),rgb(200,150,80),rgb(100,150,220),rgb(200,100,100)]):
    rect(px+4, py+4+i*6, px+4+random.randint(15,38), py+6+i*6, c)

# 测试区: 绿色通过标志
tx, ty = COL_X[2]+260, 30
rect(tx, ty, tx+40, ty+30, rgb(30,50,30))
rect_outline(tx-1, ty-1, tx+41, ty+31, rgb(60,80,50), 1)
circle_fill(tx+20, ty+15, 10, rgb(50,150,50))
# 对勾
for d in range(8):
    put(tx+14+d, ty+16+d if d<4 else ty+22-d, rgb(220,255,220))


# ============ 5b. 部门办公家具(工位+显示器+椅子) ============
def draw_desk(x, y):
    """画一个小工位: 桌面+显示器+椅子"""
    # 桌面
    rect(x, y, x+32, y+4, DESK_TOP)
    rect(x, y+4, x+32, y+6, DESK_SIDE)
    # 桌腿
    rect(x+2, y+6, x+4, y+14, DESK_LEG)
    rect(x+28, y+6, x+30, y+14, DESK_LEG)
    # 显示器
    rect(x+10, y-12, x+24, y-1, MON_BODY)
    rect(x+11, y-11, x+23, y-2, rgb(40,60,80))  # 屏幕
    rect(x+15, y-1, x+19, y, MON_BEZEL)  # 支架
    # 椅子
    rect(x+12, y+16, x+22, y+20, CHAIR_SEAT)
    rect(x+16, y+20, x+18, y+24, darken(CHAIR_SEAT,0.8))
    circle_fill(x+13, y+24, 2, CHAIR_WHEEL)
    circle_fill(x+21, y+24, 2, CHAIR_WHEEL)

# 每个部门办公区放2-3个工位
for dname,(col,row,_,_,_,_) in DEPTS.items():
    zx = COL_X[col]; zy = ROW_Y[row]
    ox1 = zx + 20; oy1 = zy + 40
    draw_desk(ox1, oy1)
    draw_desk(ox1+80, oy1)
    if dname in ('dev','cmd','info'):
        draw_desk(ox1+160, oy1)
    # 第二排工位
    draw_desk(ox1+40, oy1+70)
    draw_desk(ox1+120, oy1+70)


# ============ 5c. 部门休闲区家具(各有特色) ============

def draw_sofa(x, y, color=SOFA_BODY):
    """小沙发"""
    dark = darken(color, 0.75)
    cush = lighten(color, 1.2)
    rect(x, y, x+36, y+14, color)
    rect(x, y+2, x+4, y+14, dark)   # 左扶手
    rect(x+32, y+2, x+36, y+14, dark)  # 右扶手
    rect(x+5, y+2, x+17, y+8, cush)  # 左垫
    rect(x+19, y+2, x+31, y+8, cush)  # 右垫
    rect(x+2, y+14, x+6, y+16, darken(color,0.6))  # 腿
    rect(x+30, y+14, x+34, y+16, darken(color,0.6))

def draw_coffee_table(x, y):
    rect(x, y, x+24, y+3, TEA_TOP)
    rect(x+2, y+3, x+4, y+10, TEA_LEG)
    rect(x+20, y+3, x+22, y+10, TEA_LEG)

def draw_plant(x, y):
    """盆栽"""
    rect(x-4, y, x+4, y+8, POT_BODY)
    rect(x-5, y, x+5, y+2, POT_RIM)
    ellipse_fill(x, y-6, 7, 6, PLANT_MID)
    ellipse_fill(x-3, y-8, 4, 4, PLANT_DARK)
    ellipse_fill(x+3, y-8, 4, 4, PLANT_LIGHT)
    rect(x-1, y-2, x+1, y, PLANT_TRUNK)

def draw_bookshelf(x, y, w=30, h=40):
    rect(x, y, x+w, y+h, SHELF_BG)
    rect_outline(x, y, x+w, y+h, SHELF_FR, 1)
    # 3层
    for si in range(3):
        sy = y + 3 + si*13
        rect(x+1, sy+10, x+w-1, sy+12, SHELF_BD)
        bx = x+3
        for _ in range(random.randint(3,5)):
            bw = random.randint(3,6)
            bh = random.randint(7,10)
            bc = random.choice(BOOK_COLORS)
            rect(bx, sy+10-bh, bx+bw, sy+10, bc)
            bx += bw+1
            if bx > x+w-5: break

# --- 情报室休闲区: 咖啡角+地球仪+杂志架 ---
rx, ry = COL_X[0]+int(COL_W*0.62), ROW_Y[0]+20
# 咖啡桌+杯子
draw_coffee_table(rx+10, ry+60)
rect(rx+18, ry+55, rx+24, ry+60, rgb(200,200,200))  # 咖啡杯
rect(rx+19, ry+53, rx+23, ry+55, rgb(120,70,30))  # 咖啡
# 地球仪
circle_fill(rx+80, ry+30, 12, rgb(50,100,160))
ellipse_fill(rx+80, ry+30, 12, 3, rgb(60,140,80))  # 大陆带
rect(rx+79, ry+42, rx+81, ry+50, rgb(100,80,50))  # 支架
rect(rx+74, ry+50, rx+86, ry+52, rgb(100,80,50))
# 杂志架
draw_bookshelf(rx+120, ry+10, 28, 50)
# 小沙发
draw_sofa(rx+30, ry+100, rgb(70,90,110))
draw_plant(rx+5, ry+110)

# --- 开发区休闲区: 懒人沙发+街机+零食柜 ---
rx, ry = COL_X[1]+int(COL_W*0.62), ROW_Y[0]+20
# 懒人沙发(大豆袋)
ellipse_fill(rx+25, ry+90, 18, 12, rgb(80,75,110))
ellipse_fill(rx+25, ry+85, 15, 8, rgb(100,95,130))
# 街机
rect(rx+70, ry+10, rx+95, ry+60, rgb(40,40,55))
rect(rx+73, ry+14, rx+92, ry+38, rgb(20,80,60))  # 屏幕
rect(rx+78, ry+42, rx+87, ry+48, rgb(60,60,70))  # 控制面板
circle_fill(rx+81, ry+45, 2, rgb(220,50,50))  # 红按钮
circle_fill(rx+86, ry+45, 2, rgb(50,50,220))  # 蓝按钮
# 零食柜
rect(rx+110, ry+20, rx+140, ry+70, rgb(180,160,120))
rect_outline(rx+110, ry+20, rx+140, ry+70, rgb(140,120,80), 1)
for si in range(3):
    sy = ry+25+si*15
    rect(rx+112, sy, rx+138, sy+2, rgb(160,140,100))
    for sx in range(rx+114, rx+136, 6):
        c = random.choice([rgb(220,60,60),rgb(60,60,220),rgb(60,180,60),rgb(220,180,40)])
        rect(sx, sy-8, sx+4, sy, c)
draw_plant(rx+150, ry+80)

# --- 测试区休闲区: 鱼缸+冥想垫+书架 ---
rx, ry = COL_X[2]+int(COL_W*0.62), ROW_Y[0]+20
# 鱼缸
rect(rx+10, ry+20, rx+55, ry+55, rgb(140,200,230))
rect_outline(rx+10, ry+20, rx+55, ry+55, rgb(80,80,90), 2)
# 鱼
ellipse_fill(rx+25, ry+35, 4, 2, rgb(255,120,50))
ellipse_fill(rx+40, ry+42, 3, 2, rgb(50,120,255))
# 水草
for gx in [rx+18, rx+32, rx+45]:
    for gy in range(ry+45, ry+54):
        put(gx, gy, rgb(30,120,50))
        put(gx+1, gy, rgb(40,140,60))
# 冥想垫
ellipse_fill(rx+90, ry+90, 16, 8, rgb(120,80,140))
ellipse_fill(rx+90, ry+88, 14, 6, rgb(140,100,160))
# 书架
draw_bookshelf(rx+120, ry+10, 30, 50)
draw_plant(rx+5, ry+100)


# --- 金融区休闲区: 皮沙发+红酒架+雪茄盒 ---
rx, ry = COL_X[0]+int(COL_W*0.62), ROW_Y[1]+20
# 皮沙发(深棕)
draw_sofa(rx+20, ry+80, rgb(100,60,35))
# 红酒架
rect(rx+100, ry+10, rx+140, ry+65, rgb(80,45,25))
rect_outline(rx+100, ry+10, rx+140, ry+65, rgb(60,35,18), 1)
for si in range(4):
    sy = ry+15+si*12
    rect(rx+102, sy, rx+138, sy+2, rgb(70,40,22))
    for sx in range(rx+104, rx+136, 8):
        # 酒瓶
        rect(sx, sy-8, sx+3, sy, rgb(50,20,30))
        circle_fill(sx+1, sy-9, 2, rgb(60,25,35))
# 雪茄盒
rect(rx+30, ry+50, rx+60, ry+60, rgb(90,50,25))
rect_outline(rx+30, ry+50, rx+60, ry+60, rgb(120,70,35), 1)
rect(rx+32, ry+52, rx+58, ry+54, rgb(200,170,80))  # 金色条
# 茶几
draw_coffee_table(rx+40, ry+65)
draw_plant(rx+5, ry+100)

# --- 策划产品休闲区: 彩色沙发+思维导图白板+乐高 ---
rx, ry = COL_X[1]+int(COL_W*0.62), ROW_Y[1]+20
# 彩色沙发
draw_sofa(rx+20, ry+80, rgb(90,130,80))
# 白板(思维导图)
rect(rx+10, ry+5, rx+80, ry+50, BOARD_BG)
rect_outline(rx+10, ry+5, rx+80, ry+50, BOARD_FR, 2)
# 思维导图线条
center_bx, center_by = rx+45, ry+27
circle_fill(center_bx, center_by, 5, rgb(220,80,80))
for angle_i, c in enumerate([rgb(80,150,220),rgb(80,200,80),rgb(220,180,50),rgb(180,80,200)]):
    a = angle_i*math.pi/2 + math.pi/4
    ex = int(center_bx + math.cos(a)*20)
    ey = int(center_by + math.sin(a)*12)
    # 连线
    steps = 20
    for s in range(steps):
        t = s/steps
        lx = int(center_bx*(1-t)+ex*t)
        ly = int(center_by*(1-t)+ey*t)
        put(lx, ly, rgb(100,100,100))
    circle_fill(ex, ey, 3, c)
# 乐高积木堆
for bx in range(rx+100, rx+140, 8):
    for by_off in range(0, random.randint(2,4)):
        bc = random.choice([rgb(220,50,50),rgb(50,50,220),rgb(50,180,50),rgb(220,200,50)])
        rect(bx, ry+60-by_off*8, bx+7, ry+67-by_off*8, bc)
        # 凸点
        rect(bx+1, ry+58-by_off*8, bx+3, ry+60-by_off*8, lighten(bc,1.2))
        rect(bx+4, ry+58-by_off*8, bx+6, ry+60-by_off*8, lighten(bc,1.2))
draw_plant(rx+150, ry+90)

# --- 指挥中心休闲区: 金色大理石+宝座+奖杯柜+三联大屏+旗帜 ---
rx, ry = COL_X[2]+int(COL_W*0.62), ROW_Y[1]+20
# 金色大理石地板(覆盖休闲区)
rx1 = COL_X[2]+int(COL_W*0.6); ry1 = ROW_Y[1]
rx2 = COL_X[2]+COL_W; ry2 = ROW_Y[1]+ROW_H
for y in range(ry1, ry2):
    for x in range(rx1, rx2):
        base = rgb(55,48,35)
        vein = math.sin(x*0.08+y*0.05)*0.5+math.cos(x*0.03-y*0.07)*0.3
        if vein > 0.4: base = rgb(70,60,40)
        elif vein > 0.2: base = rgb(62,54,38)
        # 金色微光
        if (x+y)%47 < 2: base = rgb(85,75,50)
        pixels[y*W+x] = base
# 红毯(中间)
carpet_cx = (rx1+rx2)//2
for y in range(ry1+10, ry2-10):
    for x in range(carpet_cx-25, carpet_cx+25):
        if 0<=x<W and 0<=y<H:
            base = rgb(140,30,30)
            if abs(x-carpet_cx) > 20: base = rgb(160,40,40)
            if abs(x-carpet_cx) < 3: base = rgb(170,50,50)  # 中线
            # 金边
            if abs(x-(carpet_cx-24)) < 2 or abs(x-(carpet_cx+24)) < 2:
                base = rgb(180,150,60)
            pixels[y*W+x] = base

# 宝座
tx, ty = carpet_cx-12, ry1+60
rect(tx, ty, tx+24, ty+20, rgb(120,30,30))  # 座面
rect(tx-4, ty-30, tx+28, ty, rgb(140,35,35))  # 靠背
rect(tx+8, ty-35, tx+16, ty-30, rgb(180,150,60))  # 顶部金饰
rect(tx-4, ty-30, tx+28, ty-28, rgb(180,150,60))  # 金边
rect(tx-4, ty, tx-1, ty+20, rgb(100,25,25))  # 左扶手
rect(tx+25, ty, tx+28, ty+20, rgb(100,25,25))  # 右扶手
# 宝石
circle_fill(tx+12, ty-25, 3, rgb(50,50,200))
circle_fill(tx+5, ty-20, 2, rgb(200,50,50))
circle_fill(tx+19, ty-20, 2, rgb(50,200,50))

# 奖杯柜
tcx = rx1+15
rect(tcx, ry1+20, tcx+35, ry1+80, rgb(60,45,30))
rect_outline(tcx, ry1+20, tcx+35, ry1+80, rgb(80,60,40), 1)
for si in range(3):
    sy = ry1+25+si*18
    rect(tcx+2, sy+14, tcx+33, sy+16, rgb(70,55,35))
    # 奖杯
    trophy_x = tcx+10+si*5
    rect(trophy_x, sy+4, trophy_x+6, sy+14, rgb(200,170,50))
    rect(trophy_x-2, sy+2, trophy_x+8, sy+5, rgb(220,190,60))
    rect(trophy_x+1, sy+12, trophy_x+5, sy+14, rgb(180,150,40))

# 三联大屏
scr_y = ry1+100
for si in range(3):
    sx = rx1+20+si*50
    rect(sx, scr_y, sx+42, scr_y+28, MON_BODY)
    rect(sx+2, scr_y+2, sx+40, scr_y+24, rgb(20,40,60))
    # 数据线条
    for li in range(4):
        lc = random.choice([rgb(50,200,100),rgb(200,80,80),rgb(80,150,220)])
        rect(sx+4, scr_y+5+li*5, sx+4+random.randint(10,34), scr_y+7+li*5, lc)
    rect(sx+18, scr_y+28, sx+24, scr_y+32, MON_BEZEL)

# 旗帜(左右各一)
for fx, mirror in [(rx1+8, False), (rx2-12, True)]:
    # 旗杆
    rect(fx, ry1+10, fx+2, ry1+90, rgb(180,150,60))
    circle_fill(fx+1, ry1+8, 3, rgb(200,170,70))
    # 旗面
    if not mirror:
        for fy in range(ry1+12, ry1+40):
            fw = int(20 - abs(fy-(ry1+26))*0.3)
            for ffx in range(fx+3, fx+3+fw):
                pixels[fy*W+ffx] = rgb(180,40,40)
    else:
        for fy in range(ry1+12, ry1+40):
            fw = int(20 - abs(fy-(ry1+26))*0.3)
            for ffx in range(fx-fw, fx):
                if 0<=ffx<W: pixels[fy*W+ffx] = rgb(180,40,40)


# ============ 6. 走廊装饰(盆栽/垃圾桶/指示牌/长椅) ============
# 垂直走廊装饰
for cx_start in [COL_X[1]-HALL_W, COL_X[2]-HALL_W]:
    mx = cx_start + HALL_W//2
    # 盆栽(上下各一)
    draw_plant(mx, ROW_Y[0]+30)
    draw_plant(mx, ROW_Y[1]+ROW_H-20)
    # 垃圾桶
    tbx, tby = mx-5, ROW_Y[0]+ROW_H-30
    rect(tbx, tby, tbx+10, tby+14, TRASH_BODY)
    rect(tbx-1, tby, tbx+11, tby+3, TRASH_RIM)

# 水平走廊装饰
hy_start2 = ROW_Y[0]+ROW_H
hmy = hy_start2 + HALL_W//2
# 指示牌
for sx, label_c in [(COL_X[0]+COL_W//2, rgb(80,130,190)), (COL_X[1]+COL_W//2, rgb(130,120,200)), (COL_X[2]+COL_W//2, rgb(200,160,60))]:
    rect(sx-12, hmy-8, sx+12, hmy+2, rgb(50,50,60))
    rect(sx-10, hmy-6, sx+10, hmy, label_c)
    rect(sx-1, hmy+2, sx+1, hmy+8, rgb(80,80,85))

# 长椅(水平走廊两端)
for bx in [30, W-70]:
    rect(bx, hmy-4, bx+40, hmy+2, rgb(120,80,45))
    rect(bx+3, hmy+2, bx+7, hmy+8, rgb(90,60,35))
    rect(bx+33, hmy+2, bx+37, hmy+8, rgb(90,60,35))


# ============ 7. 区域标签 ============
DEPT_LABELS = {
    'info': '📰 情报室',
    'dev':  '💻 开发区',
    'test': '🧪 测试区',
    'fin':  '🏦 金融区',
    'plan': '📋 策划产品',
    'cmd':  '🗡️ 指挥中心',
}
# 标签绘制在墙面底部(踢脚线上方)
for dname,(col,row,_,_,_,_) in DEPTS.items():
    lx = COL_X[col] + 10
    ly = WALL_H - 18
    if row == 1:
        ly = ROW_Y[1] - 12  # 下排标签在走廊上方
    # 标签背景
    rect(lx, ly, lx+80, ly+10, rgb(40,38,52))
    rect_outline(lx, ly, lx+80, ly+10, rgb(60,58,72), 1)
    # 简单像素文字太复杂，用色块标识
    dept_c = SCR_COLORS.get(dname, rgb(150,150,150))
    rect(lx+2, ly+2, lx+8, ly+8, dept_c)
    # 小横线装饰
    rect(lx+12, ly+4, lx+70, ly+6, lighten(dept_c, 1.3))


# ============ 8. 写 PNG ============
def write_png(path):
    def chunk(ctype, data):
        c = ctype + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)
    raw = b''
    for y in range(H):
        raw += b'\x00'
        for x in range(W):
            r, g, b = pixels[y*W+x]
            raw += struct.pack('BBB', r, g, b)
    sig = b'\x89PNG\r\n\x1a\n'
    ihdr = struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0)
    compressed = zlib.compress(raw, 9)
    with open(path, 'wb') as f:
        f.write(sig)
        f.write(chunk(b'IHDR', ihdr))
        f.write(chunk(b'IDAT', compressed))
        f.write(chunk(b'IEND', b''))
    print(f"✅ {path}  ({W}x{H}, {os.path.getsize(path)//1024}KB)")

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend", "office_bg.png")
write_png(out)
