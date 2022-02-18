import os, traceback
from time import strftime, localtime, time, mktime
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

from src.libraries.arcapi import *
from src.libraries.arcsql import *

img = os.path.join(os.path.dirname('src/static'), 'arcimg')
chardir = os.path.join(img, 'char')
pttdir = os.path.join(img, 'ptt')
rankdir = os.path.join(img, 'rank')
songdir = os.path.join(img, 'song')
diffdir = os.path.join(img, 'diff')

Exo_Regular = os.path.join(img, 'font', 'Exo-Regular.ttf')
GeosansLight = os.path.join(img, 'font', 'GeosansLight.ttf')

diffdict = {
    '0' : ['pst', 'past'],
    '1' : ['prs', 'present'],
    '2' : ['ftr', 'future'],
    '3' : ['byd', 'beyond']
}

class datatext:
    #L=X轴，T=Y轴，size=字体大小，fontpath=字体文件，
    def __init__(self, L, T, size, text, path, anchor = 'lt'):
        self.L = L
        self.T = T
        self.text = str(text)
        self.path = path
        self.font = ImageFont.truetype(self.path, size)
        self.anchor = anchor

def write_text(image, font, text='text', pos=(0, 0), color=(255, 255, 255, 255), anchor='lt'):
    rgba_image = image
    text_overlay = Image.new('RGBA', rgba_image.size, (255, 255, 255, 0))
    image_draw = ImageDraw.Draw(text_overlay)
    image_draw.text(pos, text, font=font, fill=color, anchor=anchor)
    return Image.alpha_composite(rgba_image, text_overlay)

def draw_text(image, class_text: datatext, color=(255, 255, 255, 255)):
    font = class_text.font
    text = class_text.text
    anchor = class_text.anchor
    return write_text(image, font, text, (class_text.L, class_text.T), color, anchor)

def open_img(img):
    with open(img, 'rb') as f:
        im = Image.open(f).convert('RGBA')
    return im

def pttbg(ptt: int) -> str:
    if ptt == -1:
        return 'rating_off.png'
    ptt /= 100
    if ptt < 3:
        name = 'rating_0.png'
    elif ptt < 7:
        name = 'rating_1.png'
    elif ptt < 10:
        name = 'rating_2.png'
    elif  ptt < 11:
        name = 'rating_3.png'
    elif  ptt < 12:
        name = 'rating_4.png'
    elif  ptt < 12.5:
        name = 'rating_5.png'
    else:
        name = 'rating_6.png'
    return name

def isrank(score: int) -> str:
    if score < 8600000:
        rank = 'D'
    elif score < 8900000:
        rank = 'C'
    elif score < 9200000:
        rank = 'B'
    elif score < 9500000:
        rank = 'A'
    elif score < 9800000:
        rank = 'AA'
    elif score < 9900000:
        rank = 'EX'
    else:
        rank = 'EX+'
    return rank

def calc_rating(songrating: float = 0, rating: float = 0, score: int = 0) -> str:
    if score and (rating or songrating):
        if songrating:
            if score >= 10000000:
                result = songrating + 2
            elif score >= 9800000:
                result = songrating + 1 + (score - 9800000) / 200000
            else:
                result = songrating + (score - 9500000) / 300000
            msg = f'Rating: {result}'
        else:
            if score >= 10000000:
                result = rating - 2
            elif score >= 9800000:
                result = rating - 1 - (score - 9800000) / 200000
            else:
                result = rating - (score - 9500000) / 300000
            msg = f'Song Rating: {result}'
    else:
        r = songrating - rating
        if r == -2:
            result = 1000
        elif r > -2:
            result = (rating - songrating - 1 + 980 / 20) * 20
        else:
            result = (rating - songrating + 950 / 30) * 30
        msg = f'Score: {result}'
    return msg

def sql_diff(diff):
    if diff == 0:
        sql_diff = 'pst'
    elif diff == 1:
        sql_diff = 'prs'
    elif diff == 2:
        sql_diff = 'ftr'
    else:
        sql_diff = 'byd'
    return sql_diff

def playtime(date):
    timearray = localtime(date / 1000)
    datetime = strftime('%Y-%m-%d %H:%M:%S', timearray)
    return datetime

def timediff(date):
    now = mktime(datetime.now().timetuple())
    time_diff = (now - date / 1000) / 86400
    return time_diff

async def draw_info(arcid: int) -> str:
    try:
        best30sum = 0
        alldata = await arcb30(arcid)
        if not isinstance(alldata, list):
            return alldata
        arcname = alldata[0]['data']['name']
        character = alldata[0]['data']['character']
        is_char_uncapped = alldata[0]['data']['is_char_uncapped']
        is_char_uncapped_override = alldata[0]['data']['is_char_uncapped_override']
        icon_name = f'{character}u_icon.png' if is_char_uncapped ^ is_char_uncapped_override else f'{character}_icon.png'
        userrating = alldata[0]['data']['rating']
        scorelist = alldata[1:]
        scorelist.sort(key = lambda v: v['data'][0]['rating'], reverse=True)
        for i in range(30) if len(scorelist) >= 30 else range(len(scorelist)):
            best30sum += scorelist[i]['data'][0]['rating']
        
        b30 = best30sum / 30
        r10 = (userrating / 100 - b30 * 0.75) / 0.25
        #------------------------------------------------
        # 图片整理
        icon = os.path.join(chardir, icon_name)
        ptt = os.path.join(pttdir, pttbg(userrating))
        # 新建底图
        bg = os.path.join(img, 'b30_bg.png')
        im = Image.new('RGBA', (1800, 3000))
        b30_bg = open_img(bg)
        im.alpha_composite(b30_bg)
        # 角色
        icon_bg = open_img(icon).resize((250, 250))
        im.alpha_composite(icon_bg, (175, 275))
        # ptt背景
        ptt_bg = open_img(ptt).resize((150, 150))
        im.alpha_composite(ptt_bg, (300, 400))
        # ptt
        w_ptt = datatext(375, 475, 45, userrating / 100 if userrating != -1 else '--', Exo_Regular, anchor='mm')
        im = draw_text(im, w_ptt)
        # arcname
        w_arcname = datatext(455, 400, 85, arcname, GeosansLight, anchor='lb')
        im = draw_text(im, w_arcname)
        # arcid
        w_arcid = datatext(480, 475, 60, f'ID:{arcid}', Exo_Regular, anchor='lb')
        im = draw_text(im, w_arcid)
        # r10
        w_r10 = datatext(1100, 400, 60, f'Recent 10: {r10:.3f}', Exo_Regular, anchor='lb')
        im = draw_text(im, w_r10)
        # b30
        w_b30 = datatext(1100, 425, 60, f'Best 30: {b30:.3f}', Exo_Regular)
        im = draw_text(im, w_b30)
        # 30个成绩
        bg_y = 580
        for num, i in enumerate(scorelist):
            if num == 30:
                break
            # 横3竖10
            if num % 3 == 0:
                bg_y += 240 if num != 0 else 0
                bg_x = 30
            else:
                bg_x += 600

            data = i['data'][0]
            # 歌曲信息
            songid = data['song_id']
            difficulty = data['difficulty']
            # 成绩整理
            song_rating = data['constant']
            score = data['score']
            sp_count = data['shiny_perfect_count']
            p_count = data['perfect_count']
            far_count = data['near_count']
            lost_count = data['miss_count']
            health = data['health']
            play_time = data['time_played']
            rating = data['rating']
            # 图片整理
            score30 = os.path.join(img, 'b30_score_bg.png')
            rank = os.path.join(rankdir, f'grade_{isrank(score).lower()}.png' if health != -1 else 'grade_f.png')
            songbg = os.path.join(songdir, songid, 'base.jpg')
            diffbg = os.path.join(diffdir, diffdict[str(difficulty)][0].upper() + '.png')
            newbg = os.path.join(img, 'new.png')
            # 底图
            score30_bg = open_img(score30)
            im.alpha_composite(score30_bg, (10 + bg_x, bg_y))
            # 曲图
            song_bg = open_img(songbg).resize((190, 190))
            im.alpha_composite(song_bg, (35 + bg_x, 5 + bg_y))
            # 难度
            diff_bg = open_img(diffbg).resize((72, 72))
            im.alpha_composite(diff_bg, (161 + bg_x, bg_y - 3))
            # rank
            rank_bg = open_img(rank).resize((135, 65))
            im.alpha_composite(rank_bg, (395 + bg_x, 95 + bg_y))
            # songrating
            w_songrating = datatext(223 + bg_x, 12 + bg_y, 20, f'{song_rating:.1f}', Exo_Regular, anchor='rt')
            im = draw_text(im, w_songrating)
            # #
            w_rank = datatext(480 + bg_x, bg_y, 45, f'#{num + 1}', Exo_Regular, anchor='lm')
            im = draw_text(im, w_rank)
            # 分数
            w_score = datatext(235 + bg_x, 15 + bg_y, 55, f'{score:,}', GeosansLight)
            im = draw_text(im, w_score)
            # PURE 
            w_PURE = datatext(235 + bg_x, 75 + bg_y, 30, 'PURE', GeosansLight)
            im = draw_text(im, w_PURE)
            w_p_count = datatext(335 + bg_x, 75 + bg_y, 30, p_count, GeosansLight)
            im = draw_text(im, w_p_count)
            w_sp_count = datatext(400 + bg_x, 75 + bg_y, 20, f'+{sp_count}', GeosansLight)
            im = draw_text(im, w_sp_count)
            # FAR
            w_FAR = datatext(235 + bg_x, 105 + bg_y, 30, 'FAR', GeosansLight)
            im = draw_text(im, w_FAR)
            w_far_count = datatext(335 + bg_x, 105 + bg_y, 30, far_count, GeosansLight)
            im = draw_text(im, w_far_count)
            # LOST
            w_LOST = datatext(235 + bg_x, 135 + bg_y, 30, 'LOST', GeosansLight)
            im = draw_text(im, w_LOST)
            w_lost_count = datatext(335 + bg_x, 135 + bg_y, 30, lost_count, GeosansLight)
            im = draw_text(im, w_lost_count)
            # Rating
            w_Rating = datatext(235 + bg_x, 170 + bg_y, 30, 'Rating:', GeosansLight)
            im = draw_text(im, w_Rating)
            w_u_rating = datatext(335 + bg_x, 170 + bg_y, 30, f'{rating:.3f}', GeosansLight)
            im = draw_text(im, w_u_rating)
            # time
            game_time = playtime(play_time)
            w_time = datatext(280 + bg_x, 210 + bg_y, 30, game_time, Exo_Regular, anchor='mm')
            im = draw_text(im, w_time)
            # new
            if timediff(play_time) <= 7:
                new_bg = open_img(newbg)
                im.alpha_composite(new_bg, (bg_x - 23, bg_y))
        # save
        outputiamge_path = os.path.join(img, 'out', f'{arcid}.png')
        im.save(outputiamge_path)
        msg = f'[CQ:image,file=file:///{outputiamge_path}]'
        return msg
    except Exception as e:
        return f'Error {type(e)}'

async def draw_score(user_id, est: bool = False) -> str:
    try:
        # 获取用户名
        asql = arcsql()
        if est:
            scoreinfo = await arcb30(user_id, est)
            if isinstance(scoreinfo, str):
                return scoreinfo
            userinfo = scoreinfo['data']
            arcid = user_id
        else:
            arcid, email, pwd = asql.get_bind_user(user_id)
            scoreinfo = await get_web_api(email, pwd)
            if isinstance(scoreinfo, str):
                return scoreinfo
            friends = scoreinfo['value']['friends']
            for n, i in enumerate(friends):
                if user_id == i['user_id']:
                    userinfo = friends[n]
                    break

        arcname = userinfo['name']
        userrating = userinfo['rating'] / 100 if userinfo['rating'] != -1 else '--'
        recentscore = userinfo['recent_score'][0]
        songid = recentscore['song_id']
        difficulty = recentscore['difficulty']

        # 歌曲信息
        songinfo = asql.song_info(songid, sql_diff(difficulty))
        title = songinfo[1] if songinfo[1] else songinfo[0]
        artist = songinfo[2]
        songrating = songinfo[3] / 10
        # 整理赋值
        songbg = os.path.join(songdir, songid, 'base.jpg' if difficulty != 3 else '3.jpg')
        score = recentscore['score']
        sp_count = recentscore['shiny_perfect_count']
        p_count = recentscore['perfect_count']
        far_count = recentscore['near_count']
        miss_count = recentscore['miss_count']
        health = recentscore['health']
        play_time = recentscore['time_played']
        rating = recentscore['rating']

        msg = f'''
[CQ:image,file=file:///{songbg}]
Player: {arcname}
Rating: {userrating}
Code: {arcid}
PlayTime: {playtime(play_time)}
---------------------------------
Song: {title}
Artist: {artist}
Difficulty: {diffdict[str(difficulty)][0].upper()} | SongRating: {songrating}
---------------------------------
Score: {score:,}
Rank: {'F' if health == -1 else isrank(score)} | Rating: {rating:.2f}
Pure: {p_count} (+{sp_count})
Far: {far_count}
Lost: {miss_count}'''
        return msg
    except Exception as e:
        return f'Error {type(e)}'

async def bindinfo(qqid, arcid, arcname) -> str:
    asql = arcsql()
    asql.insert_temp_user(qqid, arcid, arcname.lower())
    return f'▾ Kiba Arc - Bind\n用户 {arcid} 已成功绑定QQ {qqid}，现可使用 <arcinfo> 指令查询B30成绩和 <arcre:> 指令使用 est 查分器查询最近，<arcre> 指令需等待管理员确认是否为好友才能使用'

async def newbind() -> str:
    try:
        asql = arcsql()
        bind_id, email, password = asql.get_not_full_email()
        info = await get_web_api(email, password)
        friend = info['value']['friends']
        for m in friend:
            arcname = m['name']
            user_id = m['user_id']
            name = asql.get_user_name(user_id)
            if name:
                continue
            arasql.insert_user(arcname.lower(), user_id, bind_id)
            return f'▾ Kiba Arc - Newbind\n添加成功。'
    except Exception as e:
        return f'▿ Kiba Arc - Newbind\n添加失败。请检查在服务器端数据库是否手动添加了查询用账号的数据？如没有添加，请手动添加。\n[Exception Occurred]\n{e}'