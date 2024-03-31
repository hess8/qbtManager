"""
This script is designed to ban leeches who do not upload
their files, such as '-XL0012-' aka '迅雷' in Chinese.

The API documents referred to in this URL:
https://github.com/qbittorrent/qBittorrent/wiki/Web-API-Documentation#set-application-preferences
https://github.com/qbittorrent/qBittorrent/wiki/WebUI-API-(qBittorrent-4.1)
"""
import os,sys
from urllib import request
import json
import time
import argparse
import ssl

ssl._create_default_https_context = ssl._create_unverified_context
#Disable certificate verification

def _get_url(url) -> str:
    """
    send HTTP GET request to server
    :param url: the domain name + port number + api path
    :return: result in a string.
    """
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) ' \
                 'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'

    headers = {'X-Request': 'JSON',
               'User-Agent': user_agent,
               'X-Requested-With': 'XMLHttpRequest',
               'Accept': '*/*'}

    req = request.Request(url, headers=headers)
    resp = None
    try:
        resp = request.urlopen(req)
    except Exception as e:
        print(str(e) + '\nFailed: Wrong URL or qBittorrent Web UI server not started.')
        exit(0)

    test = resp.read()
    return test.decode('ascii', 'ignore')


def _post_url(url, content):
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) ' \
                 'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'

    headers = {'User-Agent': user_agent,
               'X-Requested-With': 'XMLHttpRequest',
               'Accept': '*/*'}

    request.urlopen(request.Request(url, str.encode(content)))

def create_list(file,newlist):
    try:
        f = open(file, "rt")
        lines = f.readlines()
        for line in lines:
            newlist.append(line.strip())
        return newlist
    except Exception as e:
        print(str(e) + "\n Error reading {}".format(file))
        exit(0)

class ClientFilter:

    def __init__(self, url='localhost', port=8080, https=False, watch_all = False, unconditional=False):
        if https:
            self.url_port = "https://" + url + ":" + str(port)
        else:
            self.url_port = "http://" + url + ":" + str(port)
        self.unconditional = unconditional
        self.watch_all = watch_all
        self.torrents_to_check = {}
        self.clients_list = []
        self.countries_watch = []
        self.countries_block = []
        self.watched = []
        self.n_banned = None
        self.config_json = None
        self.clients_list = create_list('clients_to_block.txt', self.clients_list)
        self.countries_watch = create_list('countries_to_watch.txt', self.countries_watch)
        self.countries_block = create_list('countries_to_block.txt', self.countries_block)
        print('connecting to server ' + self.url_port)

    def get_torrents_to_check(self):
        server_url = self.url_port + "/api/v2/sync/maindata"
        torrents_str = _get_url(server_url)
        self.torrents_to_check = {}
        obj = json.loads(torrents_str)
        torrents = obj['torrents']
        for torrent_hash in torrents.keys():
            if torrents[torrent_hash]['num_leechs'] > 0 or self.unconditional:
                self.torrents_to_check[torrent_hash] = torrents[torrent_hash]
                
    def get_config(self):
        return json.loads(_get_url(self.url_port + "/api/v2/app/preferences"))
    
    def post_config(self,config):
        _post_url(self.url_port + "/api/v2/app/setPreferences", 'json=' + json.dumps(config))
        
    def clear_banned_ip_list(self):
        self.config_json = self.get_config()
        banned_ip_str = ''
        self.config_json['banned_IPs'] = banned_ip_str
        self.post_config(self.config_json)
        print('Cleared all banned IPs from qBittorrent')

    def output_watched(self,peer,torrent):
        time_str = time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime())
        file = os.path.split(torrent['content_path'])[1]
        progr = peer['progress'] * 100
        if progr < 25:
            progress_str = '0-25'
        elif progr < 50:
            progress_str = '25-50'
        elif progr < 75:
            progress_str = '50-75'
        else:
            progress_str = '75-100'
        watch_str = '{} {} {} {}'.format(peer['country'], file, peer['ip'], progress_str)
        if watch_str not in self.watched:
            self.watched.append(watch_str)
            wd = 20
            print('{} Watched | {} | {}% | {} | {} | {} '.format(time_str, file[:wd].ljust(wd), progress_str.rjust(6), peer['country'][:wd].ljust(wd),  peer['client'][:wd].ljust(wd), peer['ip']))
    def output_blocked_IP(self,peer):
        time_str = time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime())
        self.n_banned += 1
        print('{} Total: {} banned {} client name: {} country: {}'.format(time_str, self.n_banned, peer['ip'],
                                                                          peer['client'], peer['country']))

    def filter(self):
        """
        Get all the connected peers using torrent hash list and ban the matched peer.
        """

        self.config_json = self.get_config()
        banned_ip_str = self.config_json["banned_IPs"]
        active_torrents = json.loads(_get_url(self.url_port + "/api/v2/torrents/info?filter=active"))
        for torrent in active_torrents:
            if torrent['hash'] in self.torrents_to_check:
                peers = json.loads(self._get_peers_list(torrent['hash']))['peers']
                for ip_port in peers:
                    peer = peers[ip_port]
                    if peer['progress'] == 0: #to skip fleeting connections
                        continue
                    ip = peer['ip']
                    # if 'devel' in peer['client']:
                    #     pass
                    if self.watch_all:
                        self.output_watched(peer, torrent)
                    else:
                        for country in self.countries_watch:
                            if country in peer['country'] or peer['client'] == '':
                                self.output_watched(peer,torrent)
                    for client in self.clients_list:
                        if (client.lower() in peer['client'].lower() or client == 'Empty') and ip not in banned_ip_str:
                            banned_ip_str += '\n'
                            banned_ip_str += ip
                            self.output_blocked_IP(peer)
                    for country in self.countries_block:
                        if country in peer['country'] and ip not in banned_ip_str:
                            banned_ip_str += '\n'
                            banned_ip_str += ip
                            self.output_blocked_IP(peer)

            self.config_json['banned_IPs'] = banned_ip_str
            self.post_config(self.config_json)

    def _get_peers_list(self, torrent_hash):
        server_url = self.url_port + "/api/v2/sync/torrentPeers?rid=0&hash=" + torrent_hash
        return _get_url(server_url)

    def loop(self, filter_time_cycle=10, clear_hours=None):
        """
        Run a while true loop to ban matched ip with certain time interval.
        :param torrent_time_cycle: Time interval in sec to check the torrent list.
        :param filter_time_cycle: Time interval in sec to check the peers.
        :param clear_hours: Time interval in hours (can be decimal) to clear the banned IP list.
        :return: none
        """
        start_time = time.perf_counter()
        def t():
            return round(time.perf_counter() - start_time, 1)
        print('\nFilter time interval is {} sec'.format(filter_time_cycle))
        clear_time_cycle = None
        if clear_hours:
            clear_time_cycle = clear_hours * 3600
            if int(clear_hours) > 2: digits = 0
            elif int(clear_hours) > 1: digits = 1
            else: digits = 3
            print('clear time interval is {} hr'.format(round(clear_hours,digits)))
        if self.watch_all:
            print('\n-w is set: output a line for every peer')
        elif len(self.countries_watch) > 0:
            print('\nCountries to watch:')
            for country in self.countries_watch:
                print('\t{}'.format(country))
        if self.unconditional:
            print('\n-x is set: blocks clients regardless of leeching status')
        if len(self.clients_list) > 0:
            print('\nClient names to block:')
            for client in self.clients_list:
                print('\t{}'.format(client))
        if len(self.countries_block) > 0:
            print('\nCountries to block:')
            for country in self.countries_block:
                print('\t{}'.format(country))
        print()
        self.config_json = self.get_config()
        banned_ip_str = self.config_json["banned_IPs"]
        if banned_ip_str =='':
            self.n_banned = 0
        else:
            self.n_banned = len(banned_ip_str.split('\n'))
        if self.n_banned > 1:
            entries_str = 'entries'
            if self.n_banned == 1:
                entries_str == 'entry'
            print('\nBanned IPs list has {} {}\n'.format(self.n_banned,entries_str))
            self.config_json['banned_IPs'] = banned_ip_str

        i_cycle_clear = 0
        i_cycle_filter = 0
        while True:
            if clear_time_cycle and t() > (i_cycle_clear + 1) * clear_time_cycle:
                self.clear_banned_ip_list()
                i_cycle_clear += 1
            self.get_torrents_to_check()
            self.filter()
            i_cycle_filter += 1
            t_cycle_remaining = i_cycle_filter * filter_time_cycle - t()
            if t_cycle_remaining > 0:
                time.sleep(t_cycle_remaining)

if __name__ == '__main__':
    os.chdir(sys.path[0])
    parser = argparse.ArgumentParser(description='Ban bad peers in qBittorrent connections.',
                                     epilog='eg: python3 filter.py -u localhost -p 8080 -t 10')
    parser.add_argument('-u', default='localhost',
                        help='url of the service without \'http://\' or \'https://\'')
    parser.add_argument('-p', default=8080, type=int,
                        help='port number. Default=8080')
    parser.add_argument('-t', default=10,  type=int,
                        help='time interval between filter checks')
    parser.add_argument('-s', default=False, action="store_true",
                        help='use https protocol. Default=http')
    parser.add_argument('-c', default=None, type=float,
                        help='time interval to clear torrents list in hours (decimal OK). Default=None')
    parser.add_argument('-w', default=False, action="store_true",
                        help='watch all peers (output to sdtout)')
    parser.add_argument('-x', default=False, action="store_true",
                        help='blocks clients unconditionally regardless of leeching status')

    config = parser.parse_args()
    f = ClientFilter(url=config.u, port=config.p, https=config.s, watch_all=config.w, unconditional=config.x)
    f.loop(filter_time_cycle=config.t, clear_hours=config.c)
