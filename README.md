# abping

Fast Ping tool. Use it in network and server management.
Currently, the following contents are implemented,
but please let me know if there are any other functions you would like to add.

## Installation

None

## Usage

    usage: abping.py [-h]

                     [--host ["hostname" or "ipaddress" ["hostname" or "ipaddress" ...]]]
                     [--network ["network address cidr)" ["network address (cidr" ...]]]
                     [--hostsfile ["hostsfile" ["hostsfile" ...]]] [-v] [--ok]
                     [--ng]

    optional arguments:
    -h, --help show this help message and exit
    --host ["hostname" or "ipaddress" ["hostname" or "ipaddress" ...]]
    --network ["network address (cidr)" ["network address (cidr)" ...]]
    --hostsfile ["hostsfile" ["hostsfile" ...]]
    -v, --verbose
    --ok
    --ng

## Usage example

    > python .\abping.py --host 192.168.56.101 192.168.56.105

    -------------- ping 2019-08-23 21:09:41.705192: check the host --------------
    192.168.56.101                : NG .....
    192.168.56.105                : OK


    ************************* RESULT SUMMARY *************************
    TIME :
    2019-08-23 21:09:41.699971 - 2019-08-23 21:09:43.756688

    CHECKED ALL HOST : 2
    OK  HOST  NUMBER : 1
    NG  HOST  NUMBER : 1
    ******************************************************************


    > python .\abping.py --network 192.168.56.96/28

    -- ping 2019-08-23 21:10:49.217195: check the host in 192.168.56.96/28 ---
    192.168.56.97                 : NG .....
    192.168.56.98                 : NG .....
    192.168.56.99                 : NG .....
    192.168.56.100                : OK
    192.168.56.101                : NG .....
    192.168.56.102                : NG .....
    192.168.56.103                : NG .....
    192.168.56.104                : NG .....
    192.168.56.105                : OK
    192.168.56.106                : NG .....
    192.168.56.107                : NG .....
    192.168.56.108                : NG .....
    192.168.56.109                : NG .....
    192.168.56.110                : NG .....


    ************************* RESULT SUMMARY *************************
    TIME :
    2019-08-23 21:10:49.214267 - 2019-08-23 21:10:52.140614

    CHECKED ALL HOST : 14
    OK  HOST  NUMBER : 2
    NG  HOST  NUMBER : 12
    ******************************************************************


    > python .\abping.py --hostsfile .\sample.hostlist

    -- ping 2019-08-23 21:11:54.251142: check the host in .\sample.hostlist ---
    192.168.56.100                : OK
    192.168.56.101                : NG .....
    192.168.56.105                : OK
    github.co.jp                  : OK


    ************************* RESULT SUMMARY *************************
    TIME :
    2019-08-23 21:11:54.248213 - 2019-08-23 21:11:56.276756

    CHECKED ALL HOST : 4
    OK  HOST  NUMBER : 3
    NG  HOST  NUMBER : 1
    ******************************************************************


    > python .\abping.py --host 192.168.56.101 192.168.56.105 --verbose

    -------------- ping 2019-08-23 21:14:06.353185: check the host --------------
    192.168.56.101                : NG .....

    192.168.56.105                : OK
    echo reply ip header {'version': 4, 'header_length': 5, 'df_field': '0x0', 'total_length': 33, 'identification': '0xdcfe', 'flags': '0x0', 'time_to_live': 64, 'protocol': 1, 'header_checksum': '0xac21', 'source': '192.168.56.105', 'destination': '192.168.56.2'}
    echo reply icmp packet {'type': 0, 'code': 0, 'header_checksum': '0xdc2d', 'identification': '0x0', 'sequence_number': 0, 'data': 'Hello'}



    ************************* RESULT SUMMARY *************************
    TIME :
    2019-08-23 21:14:06.349283 - 2019-08-23 21:14:08.377765

    CHECKED ALL HOST : 2
    OK  HOST  NUMBER : 1
    NG  HOST  NUMBER : 1
    ******************************************************************



    > python .\abping.py --network 192.168.56.96/28 --ok

    -- ping 2019-08-23 21:12:48.359762: check the host in 192.168.56.96/28 ---
    OK List
    192.168.56.100                : OK
    192.168.56.105                : OK


    ************************* RESULT SUMMARY *************************
    TIME :
    2019-08-23 21:12:48.355859 - 2019-08-23 21:12:56.391890

    CHECKED ALL HOST : 14
    OK  HOST  NUMBER : 2
    NG  HOST  NUMBER : 12
    ******************************************************************


    > python .\abping.py --network 192.168.56.96/28 --ng

    -- ping 2019-08-23 21:13:19.417237: check the host in 192.168.56.96/28 ---
    NG list
    192.168.56.97                 : NG .....
    192.168.56.98                 : NG .....
    192.168.56.99                 : NG .....
    192.168.56.101                : NG .....
    192.168.56.102                : NG .....
    192.168.56.103                : NG .....
    192.168.56.104                : NG .....
    192.168.56.106                : NG .....
    192.168.56.107                : NG .....
    192.168.56.108                : NG .....
    192.168.56.109                : NG .....
    192.168.56.110                : NG .....


    ************************* RESULT SUMMARY *************************
    TIME :
    2019-08-23 21:13:19.413333 - 2019-08-23 21:13:27.471299

    CHECKED ALL HOST : 14
    OK  HOST  NUMBER : 2
    NG  HOST  NUMBER : 12
    ******************************************************************



    > python .\abping.py --host 192.168.56.101 192.168.56.105 www.github.co.jp --network 192.168.56.96/29 192.168.56.104/29 --hostsfile .\sample.hostlist

    -------------- ping 2019-08-23 21:15:36.463410: check the host --------------
    192.168.56.101                : NG .....
    192.168.56.105                : OK
    www.github.co.jp              : OK

    -- ping 2019-08-23 21:15:38.488316: check the host in 192.168.56.96/29 ---
    192.168.56.97                 : NG .....
    192.168.56.98                 : NG .....
    192.168.56.99                 : NG .....
    192.168.56.100                : OK
    192.168.56.101                : NG .....
    192.168.56.102                : NG .....

    -- ping 2019-08-23 21:15:46.572983: check the host in 192.168.56.104/29 ---
    192.168.56.105                : OK
    192.168.56.106                : NG .....
    192.168.56.107                : NG .....
    192.168.56.108                : NG .....
    192.168.56.109                : NG .....
    192.168.56.110                : NG .....

    -- ping 2019-08-23 21:15:54.593839: check the host in .\sample.hostlist ---
    192.168.56.100                : OK
    192.168.56.101                : NG .....
    192.168.56.105                : OK
    github.co.jp                  : OK


    ************************* RESULT SUMMARY *************************
    TIME :
    2019-08-23 21:15:36.458532 - 2019-08-23 21:15:56.633074

    CHECKED ALL HOST : 14
    OK  HOST  NUMBER : 4
    NG  HOST  NUMBER : 10
    ******************************************************************

## Requirement

python 3.6 or more

## Author

[abwo](https://github.com/abwo)
