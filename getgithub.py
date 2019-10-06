import os

urls = [
    # 'https://raw.githubusercontent.com/solenskiner/search-plugins/master/nova3/engines/academictorrents.py',
    #         'https://raw.githubusercontent.com/hannsen/qbittorrent_search_plugins/master/ali213.py',
    #         'https://github.com/nindogo/qbtSearchScripts/raw/master/anidex.py',
    #         'https://raw.githubusercontent.com/hannsen/qbittorrent_search_plugins/master/threedm.py',
    #         'https://raw.githubusercontent.com/lima66/Torrents_Plugin/master/btetree.py',
    #         'https://raw.githubusercontent.com/MaurizioRicci/qBittorrent_search_engine/master/cinecalidad.py',
    #         'https://raw.githubusercontent.com/davy39/qbfrench/master/cpasbien.py',
    #         'https://raw.githubusercontent.com/MaurizioRicci/qBittorrent_search_engine/master/cpasbien.py',
    'https://raw.githubusercontent.com/hannsen/qbittorrent_search_plugins/master/demonoid.py',
    'https://github.com/xyauhideto/DMHY_qBittorrent_search_plugin/raw/master/dmhyorg.py',
    'https://raw.githubusercontent.com/MaurizioRicci/qBittorrent_search_engine/master/ettv.py',
    'https://raw.githubusercontent.com/MaurizioRicci/qBittorrent_search_engine/master/extratorrent.py',
    'https://raw.githubusercontent.com/MaurizioRicci/qBittorrent_search_engine/master/foxcili.py',
    'https://raw.githubusercontent.com/MaurizioRicci/qBittorrent_search_engine/master/horriblesubs.py',
    'https://raw.githubusercontent.com/MaurizioRicci/qBittorrent_search_engine/master/corsaroblu.py',
    'https://raw.githubusercontent.com/MaurizioRicci/qBittorrent_search_engine/master/corsaronero.py',
    'https://github.com/dandag/qBittorrent_search_engine/blob/master/corsarored.py',
    'https://raw.githubusercontent.com/MaurizioRicci/qBittorrent_search_engine/master/kickass_torrent.py',
    'https://raw.githubusercontent.com/MadeOfMagicAndWires/qBit-plugins/6074a7cccb90dfd5c81b7eaddd3138adec7f3377/engines/linuxtracker.py',
    'https://raw.githubusercontent.com/nindogo/qbtSearchScripts/master/magnetdl.py',
    'https://raw.githubusercontent.com/MaurizioRicci/qBittorrent_search_engine/master/mejor.py',
    'https://raw.githubusercontent.com/4chenz/pantsu-plugin/master/pantsu.py',
    'https://raw.githubusercontent.com/MadeOfMagicAndWires/qBit-plugins/master/engines/nyaapantsu.py',
    'https://raw.githubusercontent.com/MadeOfMagicAndWires/qBit-plugins/master/engines/nyaasi.py',
    'https://raw.githubusercontent.com/Pireo/hello-world/master/rockbox.py',
    'https://raw.githubusercontent.com/Pireo/hello-world/master/rutor.py',
    'https://gist.githubusercontent.com/kernc/67c939c57edb7dd057b3abf9f159598a/raw/09c0099fc8cd8bd2326e5881a8f77c2dffb8e16b/skytorrents.py',
    'https://raw.githubusercontent.com/hannsen/qbittorrent_search_plugins/master/smallgames.py',
    'https://raw.githubusercontent.com/gitDew/qbittorrent-snowfl-search-plugin/master/snowfl.py',
    'https://raw.githubusercontent.com/MaurizioRicci/qBittorrent_search_engine/master/solotorrent.py',
    'https://raw.githubusercontent.com/phuongtailtranminh/qBittorrent-Nyaa-Search-Plugin/master/nyaa.py',
    'https://raw.githubusercontent.com/4chenz/pantsu-plugin/master/sukebei.py',
    'https://raw.githubusercontent.com/ngosang/qBittorrent-plugins/master/sumotorrent/sumotorrent.py',
    'https://raw.githubusercontent.com/BrunoReX/qBittorrent-Search-Plugin-TokyoToshokan/master/tokyotoshokan.py',
    'https://raw.githubusercontent.com/CravateRouge/qBittorrentSearchPlugins/master/torrent9.py',
    'https://raw.githubusercontent.com/MaurizioRicci/qBittorrent_search_engine/master/torrentfunk.py',
    'https://raw.githubusercontent.com/nindogo/qbtSearchScripts/master/torrentgalaxy.py',
    'https://raw.githubusercontent.com/MaurizioRicci/qBittorrent_search_engine/master/torrentproject.py',
    'https://raw.githubusercontent.com/nindogo/qbtSearchScripts/master/uniondht.py',
    'https://raw.githubusercontent.com/nindogo/qbtSearchScripts/master/yourbittorrent.py',
    'https://raw.githubusercontent.com/khensolomon/leyts/master/yts.py',
    'https://raw.githubusercontent.com/MaurizioRicci/qBittorrent_search_engine/master/yts_am.py']
import urllib.request

i = 8
for url in urls:
    # print(url.rfind('/'))
    # print(url[url.rfind('/') + 1:])
    os.rename(str(i) + '.py', url[url.rfind('/') + 1:])
    # f = open(str(i) + '.py', 'wb')
    # f.flush()
    # f.close()
    i += 1
    # print(i)
