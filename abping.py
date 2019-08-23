import argparse
import concurrent.futures
import datetime
import ipaddress
import socket
import struct


ICMP_ECHO = 0x08
ICMP_ECHO_REPLY = 0x00
CODE = 0x00
CKSUM = 0x0000
ID = 0x0000
SEQ_NO = 0x0000
PING_RETRY = 3


class AbPing(object):

    def __init__(self, code=CODE, icmp_id=ID, seq_no=SEQ_NO):
        self.code = code
        self.icmp_id = icmp_id
        self.seq_no = seq_no
        self.sock = self._get_socket()

    def __del__(self):
        self._fin_socket()

    def _get_socket(self):
        sock = (
            socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        )
        sock.settimeout(2)
        return sock

    def _fin_socket(self):
        self.sock.close()

    def _get_payload_hex_sum_value_for_cksum(self, payload):
        payload_hex = payload.encode().hex()
        if (len(payload_hex)/2) % 2 != 0:
            payload_hex = payload_hex + '00'
        sum = 0
        for i in range(0, len(payload_hex), 4):
            sum = sum + int(payload_hex[i:i+4], 16)
        return sum

    def _get_cksum(self, icmp_type, payload):
        cksum = CKSUM
        type_code = (icmp_type << 8) | self.code
        payload_hex_sum_value = (
            self._get_payload_hex_sum_value_for_cksum(payload)
        )
        tmp = (
            type_code + self.icmp_id + self.seq_no + payload_hex_sum_value
        )
        overflow = (tmp & ~0xFFFF)
        tmp_add = (overflow & ~0xFFFF) >> 16
        cksum = (tmp + tmp_add - overflow) ^ 0xFFFF
        return cksum

    def _get_icmp_header(self, icmp_type, payload):
        cksum = self._get_cksum(icmp_type, payload)
        icmp_header = (
            struct.pack('!BBHHH', icmp_type, self.code, cksum,
                        self.icmp_id, self.seq_no)
        )
        return icmp_header

    def _get_packet(self, icmp_header, payload):
        return (
            icmp_header + payload.encode()
        )

    def _calc_recv_data_result_val(self, result):
        for result_key, result_val in result.items():
            if type(result_val) is str:
                result[result_key] = hex(int(result_val, 16))
                continue

            val_for_calc = 0x00
            shift_val = (len(result_val)-1) * 8
            for val in result_val:
                val = int(val, 16) << shift_val
                val_for_calc = val_for_calc | val
                shift_val = shift_val - 8
            result[result_key] = hex(val_for_calc)

        return result

    def _analyze_ping_recv_data(self, recv_data):
        recv_data_tmp = [hex(val) for val in recv_data]
        result = {
            # ip header
            'version_headerlength': recv_data_tmp[0],
            'df_field': recv_data_tmp[1],
            'total_length': recv_data_tmp[2:4],
            'ip_identification': recv_data_tmp[4:6],
            'flags': recv_data_tmp[6:8],
            'time_to_live': recv_data_tmp[8],
            'protocol': recv_data_tmp[9],
            'ip_checksum': recv_data_tmp[10:12],
            'source_ip': recv_data_tmp[12:16],
            'destination_ip': recv_data_tmp[16:20],
            # icmp packet
            'type': recv_data_tmp[20],
            'code': recv_data_tmp[21],
            'icmp_checksum': recv_data_tmp[22:24],
            'icmp_identification': recv_data_tmp[24:26],
            'sequence_number': recv_data_tmp[26:28],
            'data': recv_data_tmp[28:]
        }
        result = self._calc_recv_data_result_val(result)
        return result

    def _get_ipaddress(self, host):
        return socket.gethostbyname(host)

    def send_ping(self, dest_host, payload, retry=0):
        dest_ip = self._get_ipaddress(dest_host)

        # send echo request
        icmp_type = ICMP_ECHO
        icmp_header = self._get_icmp_header(icmp_type, payload)
        packet = self._get_packet(icmp_header, payload)
        while packet:
            sent_bytes = self.sock.sendto(packet, (dest_ip, 0))
            packet = packet[sent_bytes:]

        recv_data = None
        try:
            recv_data = self.sock.recv(4096)
        except socket.timeout:
            recv_data = None

        if recv_data is not None:
            recv_data = self._analyze_ping_recv_data(recv_data)
        elif recv_data is None:
            if retry < PING_RETRY:
                retry += 1
                self.send_ping(dest_host, payload, retry)

        return recv_data

    def concurrent_send_ping(self, target_host_list, payload):
        workers = 254
        result_list = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) \
                as executor:
            futures = ([
                executor.submit(self.send_ping, str(target_ip), payload)
                for target_ip in target_host_list
            ])
            for future in concurrent.futures.as_completed(futures):
                result_list.append(future.result())
        return result_list

    def _is_echo_reply(self, recv_data):
        if recv_data is not None and recv_data['code'] == '0x0':
            return True
        else:
            return False

    def _get_echo_reply_ok_dict(self, result_list):
        echo_reply_ok_dict = {}
        for result in result_list:
            if self._is_echo_reply(result):
                echo_reply_ok_dict[str(ipaddress.IPv4Address(
                    int(result['source_ip'], 16)))] = result
        return echo_reply_ok_dict

    def ping_check(self, target_host_list, payload='Hello'):
        target_host_list = tuple(target_host_list)
        result_list = self.concurrent_send_ping(target_host_list, payload)
        echo_reply_ok_dict = self._get_echo_reply_ok_dict(result_list)
        ping_check_result = {}
        for target_host in target_host_list:
            target_host = str(target_host)
            target_ip = socket.gethostbyname(target_host)
            if str(target_ip) in echo_reply_ok_dict:
                ping_check_result[target_host] = echo_reply_ok_dict[target_ip]
            else:
                ping_check_result[target_host] = None
        return ping_check_result

    def ping_check_network(self, cidr, payload='Hello'):
        target_host_list = ipaddress.IPv4Network(cidr).hosts()
        return self.ping_check(target_host_list)

    def ping_check_hostsfile(self, hostsfile, payload='Hello'):
        target_host_list = []
        with open(hostsfile, mode='r') as hostsfile:
            for line in hostsfile.read().splitlines():
                target_host_list.append(line)
        return self.ping_check(target_host_list)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--host', metavar='"hostname" or "ipaddress"', nargs='*', type=str
    )
    parser.add_argument(
        '--network', metavar='"network address (cidr)"', nargs='*',  type=str
    )
    parser.add_argument(
        '--hostsfile', metavar='"hostsfile"', nargs='*', type=str
    )
    parser.add_argument(
        '-v', '--verbose', action='store_true'
    )
    parser.add_argument(
        '--ok', action='store_true'
    )
    parser.add_argument(
        '--ng', action='store_true'
    )
    args = parser.parse_args()
    return args


def get_reform_ip_header(recv_data):
    ip_header = {
        'version': int(recv_data['version_headerlength'], 16) >> 4,
        'header_length': int(recv_data['version_headerlength'], 16) & 0x0f,
        'df_field': recv_data['df_field'],
        'total_length': int(recv_data['total_length'], 16),
        'identification': recv_data['ip_identification'],
        'flags': recv_data['flags'],
        'time_to_live': int(recv_data['time_to_live'], 16),
        'protocol': int(recv_data['protocol'], 16),
        'header_checksum': recv_data['ip_checksum'],
        'source': (
            str(ipaddress.IPv4Address(int(recv_data['source_ip'], 16)))
        ),
        'destination': (
            str(ipaddress.IPv4Address(int(recv_data['destination_ip'], 16)))
        )
    }
    return ip_header


def get_str_from_hex(hex_data):
    hex_data = hex_data.lstrip('0x')
    str_datas = ''
    for num in range(0, len(hex_data), 2):
        str_data = chr(int(hex_data[num:num+2], 16))
        str_datas = str_datas + str_data
    return str_datas


def get_reform_icmp_packet(recv_data):
    icmp_packet = {
        'type': int(recv_data['type'], 16),
        'code': int(recv_data['code'], 16),
        'header_checksum': recv_data['icmp_checksum'],
        'identification': recv_data['icmp_identification'],
        'sequence_number': int(recv_data['sequence_number'], 16),
        'data': get_str_from_hex(recv_data['data'])
    }
    return icmp_packet


def print_ping_result(result, verbose=False, ok_only=False, ng_only=False):
    if ok_only:
        print('OK List')
    if ng_only:
        print('NG list')

    for host, recv_data in result.items():
        if ok_only and recv_data is not None:
            print('{0:30s}: OK'.format(host))
            continue
        elif ok_only:
            continue

        if ng_only and recv_data is None:
            print('{0:30s}: NG .....'.format(host))
            continue
        elif ng_only:
            continue

        if recv_data is not None and verbose:
            print('\n{0:30s}: OK'.format(host))
            print('echo reply ip header ', end='')
            print(get_reform_ip_header(recv_data))
            print('echo reply icmp packet ', end='')
            print(get_reform_icmp_packet(recv_data))
            print()
        elif recv_data is not None:
            print('{0:30s}: OK'.format(host))
        else:
            print('{0:30s}: NG .....'.format(host))


def print_result_summary(result, time_start, time_end):
    print()
    print('************************* RESULT SUMMARY *************************')
    checked_host_number = 0
    ok_host_number = 0
    ng_host_number = 0
    for host, recv_data in result.items():
        if recv_data is not None:
            ok_host_number += 1
        else:
            ng_host_number += 1
    checked_host_number = ok_host_number + ng_host_number
    print('TIME : \n{0} - {1}'.format(time_start, time_end))
    print()
    print('CHECKED ALL HOST : {0}'.format(checked_host_number))
    print('OK  HOST  NUMBER : {0}'.format(ok_host_number))
    print('NG  HOST  NUMBER : {0}'.format(ng_host_number))
    print('******************************************************************')
    print()


def main():
    time_start = datetime.datetime.now()
    abping = AbPing()

    args = get_args()
    other_option_list = (args.verbose, args.ok, args.ng)
    all_result = {}
    if args.host is not None:
        print(
            '\n-------------- ping {0}: check the host --------------'
            .format(datetime.datetime.now())
        )
        result = abping.ping_check(args.host)
        all_result.update(result)
        print_ping_result(result, *other_option_list)

    if args.network is not None:
        for network in args.network:
            print(
                '\n-- ping {0}: check the host in {1} ---'
                .format(datetime.datetime.now(), network)
            )
            result = abping.ping_check_network(network)
            all_result.update(result)
            print_ping_result(result, *other_option_list)

    if args.hostsfile is not None:
        for hostsfile in args.hostsfile:
            print(
                '\n-- ping {0}: check the host in {1} ---'
                .format(datetime.datetime.now(), hostsfile)
            )
            result = abping.ping_check_hostsfile(hostsfile)
            all_result.update(result)
            print_ping_result(result, *other_option_list)
    print()

    del abping

    time_end = datetime.datetime.now()
    print_result_summary(all_result, time_start, time_end)


if __name__ == '__main__':
    main()
