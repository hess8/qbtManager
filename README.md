# qbtManager
A python script to manage qBittorrent downloads.  Blocks IP addresses by client name or country, and checks leeching.

## Features
* Block IP addresses based on country and/or client name
* Blocking can be dependent on leeching

## Requirements
* `python 3.6`
* `qBittorrent 4.2.1` (GUI version and non-GUI version are both fine)

## Configuration and run
1. Open the qBittorrent **Web UI** in settings.
2. Set *IP Address* and *Port*, for example `localhost` and `8080`.
3. Set your own *Username* and *Password*.
4. Check the config box "Bypass authentication for clients on localhost" to let the script work without a password.
5. Edit `clients_to_block.txt`, which contains some client names.  Each line is a substring of a client name you might block. Case insensitive. Remove names if you don't want them blocked, and add your own.  If the word "Empty" is in the file, all peers that have no client name will be blocked.
6. If you add countries to `countries_to_watch.txt`, the output will show the ip address, country, client name and file downloaded. Each line is a substring of the name (or entire name) of a country you might block. Case sensitive.
7. To block by country, add to `countries_to_block.txt`.   If you don't want to block by country, the file should be empty.
8. On the computer running qBittorrent, run the script `filter.py` with required flags `-u` and `-p`.  For example `python3 filter.py -u localhost -p 8080`.

## Params
* `-u`: url of service, default=`localhost`
* `-p`: port of service, default=`8080`
* `-t`: time interval between filter checks, default =`10` seconds.
* `-c`: optional time interval to clear "Banned IP Addresses", in hours, default=`None`.
* `-s`: use https to connect webui.
* `-w`: watch all peers (outputs a line to stdout: file, country, client name, IP address)
* `-x`: ban clients in the client and country lists always, regardless of leeching status

## Clearing "Banned IP Addresses" list
Over time `filter.py` will add more and more entries to "Banned IP Addresses". If it is very long it might slow down your seeding.  You can choose to clear the list through btDownloadManager. Note that the script will unconditionally clean up the list, including anything that may have been manually added before!

You can set `-c` the optional time interval between clearing to any numberof hours: `-c 24` will clear it once a day

If you want to clear the list once, run the script `clear_once.py`.  It needs only the flags `-u` and `-p`

## Credit
This is further development of Od1gree/btDownloadManager, which doesn't appear to be maintained.
