# -*- coding: utf-8 -*-
import sys,urllib2,re,json,xbmc,xbmcplugin, xbmcgui,gzip,StringIO,urllib,xbmcaddon,time

plugin_url = sys.argv[0]
handle = int(sys.argv[1])
userAgent = 'Opera/9.80 (Android 2.3.4; Linux; Opera Mobi/build-1107180945; U; en-GB) Presto/2.8.149 Version/11.10'


__addon__ = xbmcaddon.Addon()
__addonname__ = __addon__.getAddonInfo("name")

def log(txt):
    message = "%s: %s" % (__addonname__, unicode(txt).encode('utf-8'))
    print(message)

def getParams():
    param = []
    paramstring = sys.argv[2]
    if len(paramstring) >= 2:
        params = sys.argv[2]
        cleanedparams = params.replace('?', '')
        if (params[len(params) - 1] == '/'):
            params = params[0:len(params) - 2]
        pairsofparams = cleanedparams.split('&')
        param = {}
        for i in range(len(pairsofparams)):
            splitparams = {}
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]
    return param

def getHttpData(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', userAgent)
    req.add_header("Referer","http://m.kugou.com")
    response = urllib2.urlopen(req)
    httpdata = response.read()
    return httpdata

#显示 酷狗FM 的相应的专辑
def index(page):
    #获得酷狗Fm列表 json
    totalPages = 4
    currpage = int(page)
    url = "http://m.kugou.com/app/i/fmList.php?pageindex="+str(page)+"&pagesize=20"
    reqStr = getHttpData(url)
    reqJson = json.loads(reqStr)
    for i in reqJson['data']:
        li = xbmcgui.ListItem(unicode(i['fmname']).encode('utf-8'))
        li.setInfo(type="Music",infoLabels={"Title":unicode(i['fmname']).encode('utf-8')})  
        url = plugin_url+"?act=list&fmid="+str(i['fmid'])
        xbmcplugin.addDirectoryItem(handle, url, li, True)
    #设置分页
    if currpage > 1:
        prevLi = xbmcgui.ListItem('上一页 【[COLOR FF00FF00]'+str(currpage-1)+'[/COLOR]/[COLOR FFFF0000]'+str(totalPages)+'[/COLOR]】')
        u = plugin_url+ "?act=index&page="+str(currpage-1)
        xbmcplugin.addDirectoryItem(handle, u, prevLi, True)
    if currpage < totalPages:
        nextLi = xbmcgui.ListItem('下一页 【[COLOR FF00FF00]'+str(currpage+1)+'[/COLOR]/[COLOR FFFF0000]'+str(totalPages)+'[/COLOR]】')
        u = plugin_url+ "?act=index&page="+str(currpage+1)
        xbmcplugin.addDirectoryItem(handle, u, nextLi, True)
    xbmcplugin.endOfDirectory(handle)
#获得相应电台的歌曲的列表
def getPlayList(fmid):
    listitemAll = xbmcgui.ListItem('播放当前专辑所有歌曲')
    listitemAll.setInfo(type="Music",infoLabels={ "Title":"播放当前专辑所有歌曲"})
    listUrl = plugin_url+"?act=playList&fmid="+str(fmid)
    xbmcplugin.addDirectoryItem(handle, listUrl, listitemAll, False)
    #只选取前80首歌(可以查询的歌曲相当的多！！！)  返回的是相应的json
    listUrl = "http://m.kugou.com/app/i/fmSongs.php?fmid="+str(fmid)+"&offset=0&size=80"
    listStr = getHttpData(listUrl)
    listJson = json.loads(listStr)
    songs = listJson['data'][0]['songs']
    #判断songs是否存在
    if songs:
        for song in songs:
            listitem=xbmcgui.ListItem(song['name'])
            listitem.setInfo(type="Music",infoLabels={ "Title": song['name'],})
            url = plugin_url+"?act=play&title="+str(song['name'].encode('utf-8'))+"&playUrl="+urllib.quote_plus(getSongInfo(song['hash']))
            xbmcplugin.addDirectoryItem(handle, url, listitem, False)
        xbmcplugin.endOfDirectory(handle)
    



#播放当前Fm列表里的歌曲
def playList(fmid):
    #只选取前80首歌(可以查询的歌曲相当的多！！！)  返回的是相应的json
    listUrl = "http://m.kugou.com/app/i/fmSongs.php?fmid="+str(fmid)+"&offset=0&size=80"
    listStr = getHttpData(listUrl)
    listJson = json.loads(listStr)
    playlist = xbmc.PlayList(0)
    playlist.clear()
    for song in listJson['data'][0]['songs']:
        listitem=xbmcgui.ListItem(song['name'])
        listitem.setInfo(type="Music",infoLabels={ "Title": song['name']})
        playlist.add(getSongInfo(song['hash']), listitem)
    xbmc.Player().play(playlist)

#根据歌手获得相应的信息
def getSinger(title):
    singerList = title.split('-')
    if (singerList[0]).strip():
        timestamp  = time.time()*1000
        singerUrl = "http://m.kugou.com/app/i/getSingerHead_new.php?singerName="+urllib.quote(singerList[0])+"&size=52&d="+str(timestamp)
        singerInfo = getHttpData(singerUrl)
        return singerInfo
    

#根据hash 获得mp3的相应信息
def getSongInfo(hashId):
    songUrl = "http://m.kugou.com/app/i/getSongInfo.php?hash="+str(hashId)+"&cmd=playInfo"
    songStr =  getHttpData(songUrl)
    songJson = json.loads(songStr)
    return songJson['url']

#播放音乐
def play(mp3path,title):
    playlist = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)  #xbmc.PLAYLIST_MUSIC 表示 audio   也可直接用 0
    playlist.clear() #中止播放列表
    xbmc.Player().stop()
    listitem=xbmcgui.ListItem(title)
    listitem.setInfo(type="Music",infoLabels={ "Title": title,})
    xbmc.Player().play(mp3path,listitem)
    #playlist.add(mp3path, listitem)    
    #xbmc.Player().play(playlist)

params = getParams()
try:
    act = params['act']
except :
    act = 'index'
try:
    fmid = params["fmid"]
except :
    pass
try:
    page = params["page"]
except:
    page = 1
try:
    title = params['title']
except:
    pass
try:
    playUrl = urllib.unquote_plus(params['playUrl'])
except:
    pass

if act == 'index':
    index(page)
if act == 'list':
    getPlayList(fmid)
if act == 'playList':
    playList(fmid)
if act == 'play':
    play(playUrl,title)
