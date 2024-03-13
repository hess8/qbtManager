# qbtManager
A python script to manage qBittorrent downloads by blocking clients

## Features
* Block clients by name
* Blocking can be dependent on leeching


## Requirements
* `python 3.6`
* `qBittorrent 4.2.1` (GUI version and non-GUI version are both fine)

## Configuration and run
1. Open the qBittorrent **Web UI** in settings.
2. Set *IP Address* and *Port*, for example `localhost` and `8080`.
3. Set your own *Username* and *Password*.
4. Check the config box "Bypass authentication for clients on localhost" to let the script work without a password.
5. Edit `clients_to_block.txt`.  Each line is a substring of a client name you might block.
6. On the computer running qBittorrent, run the script `filter.py` with required flags `-u`, `-p`, and `-t`.  For example `python3 filter.py -u localhost -p 8080 -t 10`.

## Params
* `-u`: url of service, default=`localhost`
* `-p`: port of service, default=`8080`
* `-f`: path to a customized filter list, with each line containing a string. Default=`None`, i.e. use default filter list.
* `-t`: time interval between filter checks, default =`10`
* `-c`: optional time interval to clear "Banned IP Addresses", in hours, default=`None`
* `-s`: use https to connect webui.
* `-x`: ban clients in the filter list always, regardless of leeching status

## Clearing "Banned IP Addresses"
Over time `filter.py` will add more and more entries to "Banned IP Addresses". If it is very long it might slow down your seeding.  You can choose to clear the list through btDownloadManager. Note that the script will unconditionally clean up the list, including anything that may have been manually added before!

You can set `-c` the optional time interval between clearing to any numberof hours: `-c 24` will clear it once a day

If you want to clear the list just once, run the script `clear_once.py`.  It needs only flags `-u` and `-p`

## Using your own list of clients to the filter
Create a file with a string on each line that contains part of the name of the client you want to filter.  Or edit the sample file `my_clients_to_filter.txt` and use it.

## Credit
Much of this code is from Od1gree/btDownloadManager, which doesn't appear to be maintained. My pull requests to add features and fix bugs haven't been addressed.
