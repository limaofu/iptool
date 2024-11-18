#!/usr/bin/env python3
# coding=utf-8
# module name: cofping
# author: Cof-Lee <cof8007@gmail.com>
# this module uses the GPL-3.0 open source protocol
# update: 2024-11-19

import array
import ctypes
import struct
import time
import socket
import random
import string
import cofnet

ICMP_TYPE_8_ECHO_REQUEST = 0x08
ICMP_TYPE_0_ECHO_RESPOND = 0x00
ICMP_TYPE_3_DESTINATION_UNREACHABLE = 3
ICMP_TYPE_11_TIME_TO_LIVE_EXCEEDED = 11


def stop_thread_silently(thread):
    """
    结束线程，如果线程里有time.sleep(n)之类的操作，则需要等待这个时长之后，才会结束此线程
    即此方法无法立即结束sleep及其他阻塞函数导致的休眼线程，得等线程获得响应时才结束它
    本函数不会抛出异常
    """
    if thread is None:
        print("cofping.stop_thread_silently: thread obj is None")
        return
    thread_id = ctypes.c_long(thread.ident)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, ctypes.py_object(SystemExit))
    # 正常结束线程时会返回数值1
    if res == 0:
        print("cofping.stop_thread_silently: invalid thread id")
    elif res == 1:
        print("cofping.stop_thread_silently: thread stopped")
    else:
        # 如果返回的值不为0，也不为1，则:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, None)
        print("cofping.stop_thread_silently: PyThreadState_SetAsyncExc failed")


class ResultOfPingOnePacket:
    def __init__(self, respond_source_ip="", respond_destination_ip=0, rtt_ms=0.0, icmp_data_size=0, ttl=0, is_success=False,
                 icmp_type=0, icmp_code=0, icmp_checksum=0x0000, icmp_id=0x0000, icmp_sequence=0x0000, icmp_data=b'',
                 received_a_respond=False, failed_info=""):
        self.respond_source_ip = respond_source_ip
        self.respond_destination_ip_int32 = respond_destination_ip
        self.rtt_ms = rtt_ms  # RTT时间，单位：毫秒
        self.icmp_data_size = icmp_data_size  # icmp数据大小，单位：字节
        self.ttl = ttl  # ip报文里的ttl
        self.is_success = is_success  # 检测是否成功，成功则置为True
        self.icmp_type = icmp_type
        self.icmp_code = icmp_code
        self.icmp_checksum = icmp_checksum
        self.icmp_id = icmp_id
        self.icmp_sequence = icmp_sequence
        self.icmp_data = icmp_data  # bytes类型数据
        self.received_a_respond = received_a_respond
        self.failed_info = failed_info  # 如果检测不成功，必须提示失败信息


class PingOnePacket:
    """
    单次ping检测，只会发送1个icmp_echo_request报文，然后等待回复
    """

    def __init__(self, target_ip="", timeout=2, size=1, ttl=128, dont_frag=False):
        self.target_ip = target_ip  # 目标ip（ipv4地址）
        self.timeout = timeout  # 超时，单位：秒
        self.size = size  # 发包数据大小，单位：字节，当整个报文长度小于mac帧长度要求时，会自动以0填充
        self.ttl = ttl
        self.dont_frag = dont_frag  # 置True时不分片，置False时分片
        self.result = ResultOfPingOnePacket()
        self.is_finished = False
        self.icmp_send_type = ICMP_TYPE_8_ECHO_REQUEST  # icmp_echo_request
        self.icmp_send_code = 0x00
        self.icmp_send_checksum = 0x0000
        self.icmp_send_id = 0xFFFF & random.randint(0, 0xFFFF)  # 为进程号，echo响应消息与echo请求消息中的id保持一致，取值随机
        self.icmp_send_sequence = 0xFFFF & random.randint(0, 0xFFFF)  # 序列号，echo响应消息与echo请求消息中的sequence保持一致，取值随机
        self.icmp_send_data = b''
        self.icmp_send_packet = b''
        self.icmp_socket = None
        self.start_time = 0.0
        self.recv_thread = None

    def start(self):
        self.icmp_send_packet = self.generate_icmp_packet()
        # 创建icmp套接字
        self.icmp_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        self.icmp_socket.settimeout(self.timeout)  # 设置socket超时时间，当收到数据包后，会重置超时时间为指定的
        self.icmp_socket.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, self.ttl)  # 设置ip报文的ttl
        if self.dont_frag:
            self.icmp_socket.setsockopt(socket.IPPROTO_IP, socket.IPV6_DONTFRAG, 2)  # 设置ip报文不分片，没有IPV4_DONTFRAG常量，这就有点坑
        self.start_time = time.time()
        try:
            self.icmp_socket.sendto(self.icmp_send_packet, (self.target_ip, 0))  # ★发送请求报文
        except OSError as err:
            self.is_finished = True
            stop_thread_silently(self.recv_thread)
            self.result.is_success = False
            self.result.failed_info = err.__str__()
            return
        self.recv_icmp_packet()  # 接收报文，阻塞型
        self.icmp_socket.close()

    @staticmethod
    def generate_icmp_checksum(packet: bytes) -> int:
        if len(packet) & 1:  # 长度的末位为1表示：长度不是2的倍数（即最后一bit不为0），则：
            packet = packet + b'\x00'  # 需要以0填充
        words = array.array('h', packet)
        checksum = 0
        for word in words:
            checksum += (word & 0xffff)
        while checksum > 0xFFFF:
            checksum = (checksum >> 16) + (checksum & 0xffff)  # checksum只能为2字节，溢出部分需要继续进行+运算，直到不溢出为止
        return (~checksum) & 0xffff  # 反回2字节校验和的反码

    def generate_icmp_packet(self) -> bytes:
        self.icmp_send_data = "".join(random.SystemRandom().choice(string.ascii_letters) for _ in range(self.size)).encode('utf8')
        # 字节序默认跟随系统，x86_64为LE小端字节序
        icmp_temp_header = struct.pack('bbHHH', self.icmp_send_type, self.icmp_send_code, self.icmp_send_checksum,
                                       self.icmp_send_id, self.icmp_send_sequence)
        icmp_temp_packet = icmp_temp_header + self.icmp_send_data
        self.icmp_send_checksum = self.generate_icmp_checksum(icmp_temp_packet)
        icmp_header = struct.pack('bbHHH', self.icmp_send_type, self.icmp_send_code, self.icmp_send_checksum,
                                  self.icmp_send_id, self.icmp_send_sequence)
        return icmp_header + self.icmp_send_data

    def recv_icmp_packet(self):
        while True:
            print(f"{self.target_ip} 开始接收回包，")
            used_time = time.time() - self.start_time
            if used_time >= self.timeout:
                print(f"PingOnePacket.recv_icmp_packet: {self.target_ip}接收超时了 {used_time}")
                self.result.is_success = False
                self.result.failed_info = "timeout"
                self.result.rtt_ms = self.timeout * 1000
                self.is_finished = True
                return
            try:
                # recv_packet, addr = self.icmp_socket.recvfrom(65535)  # ★★接收到整个ip报文，阻塞型函数
                recv_packet = self.icmp_socket.recv(65535)  # ★★接收到整个ip报文，阻塞型函数
            except Exception as e:  # 超时会报异常
                print("\nPingOnePacket.recv_icmp_packet: 接收报异常超时了", e)
                self.result.is_success = False
                self.result.failed_info = "timeout"
                self.result.rtt_ms = self.timeout * 1000
                self.is_finished = True
                return
            # 如果接收到报文了：
            rtt_s = time.time() - self.start_time
            ipv4_header = recv_packet[:20]
            icmp_header = recv_packet[20:28]
            icmp_data = recv_packet[28:]
            ipv4_struct_tuple = struct.unpack("!BBHHHBBHII", ipv4_header)
            icmp_type, icmp_code, icmp_checksum, icmp_id, icmp_sequence = struct.unpack("bbHHH", icmp_header)
            if icmp_id == self.icmp_send_id and icmp_sequence == self.icmp_send_sequence and icmp_type != ICMP_TYPE_8_ECHO_REQUEST:
                self.result.received_a_respond = True
                self.result.rtt_ms = rtt_s * 1000
                if icmp_type == ICMP_TYPE_0_ECHO_RESPOND and icmp_code == 0x00:
                    self.result.is_success = True
                else:
                    self.result.is_success = False
                    self.result.failed_info = self.generate_icmp_failed_info(icmp_type, icmp_code)
                self.result.ttl = ipv4_struct_tuple[5]
                # self.result.respond_source_ip = addr[0]  # 同 ipv4_struct_tuple[8]
                self.result.respond_source_ip = cofnet.int32_to_ip(ipv4_struct_tuple[8])
                self.result.respond_destination_ip_int32 = ipv4_struct_tuple[9]
                self.result.icmp_data_size = len(icmp_data)  # 大小为icmp数据部分的长度
                self.result.icmp_type = icmp_type
                self.result.icmp_code = icmp_code
                self.result.icmp_checkum = icmp_checksum
                self.result.icmp_id = icmp_id
                self.result.icmp_sequence = icmp_sequence
                self.result.icmp_data = icmp_data
                self.is_finished = True
                return
            elif icmp_type == ICMP_TYPE_11_TIME_TO_LIVE_EXCEEDED:  # 这种类型常见于tracepath中，由中间路由器返回的ttl超时消息
                # 它本身是icmp报文，其icmp_id和icmp_sequence为空，其数据内容为 原数据包的ip报文（含ip报文中的icmp载荷）
                carrier_ipv4_header = recv_packet[28:48]
                carrier_icmp_packet = recv_packet[48:]
                # carrier_icmp_header = recv_packet[48:56]
                # carrier_icmp_data = recv_packet[56:]
                carrier_ipv4_struct_tuple = struct.unpack("!BBHHHBBHII", carrier_ipv4_header)
                if carrier_ipv4_struct_tuple[9] == cofnet.ip_or_maskbyte_to_int(
                        self.target_ip) and carrier_icmp_packet == self.icmp_send_packet:
                    self.result.received_a_respond = True
                    self.result.rtt_ms = rtt_s * 1000
                    self.result.is_success = False
                    self.result.failed_info = self.generate_icmp_failed_info(icmp_type, icmp_code)
                    self.result.ttl = ipv4_struct_tuple[5]
                    self.result.respond_source_ip = cofnet.int32_to_ip(ipv4_struct_tuple[8])
                    self.result.respond_destination_ip_int32 = ipv4_struct_tuple[9]
                    self.result.icmp_data_size = len(icmp_data)  # 大小为icmp数据部分的长度
                    self.result.icmp_type = icmp_type
                    self.result.icmp_code = icmp_code
                    self.result.icmp_checkum = icmp_checksum
                    self.result.icmp_id = icmp_id
                    self.result.icmp_sequence = icmp_sequence
                    self.result.icmp_data = icmp_data
                    self.is_finished = True
                    return
            time_left = self.timeout - rtt_s
            if time_left > 0:
                self.icmp_socket.settimeout(time_left)

    @staticmethod
    def generate_icmp_failed_info(icmp_type, icmp_code) -> str:
        if icmp_type == ICMP_TYPE_3_DESTINATION_UNREACHABLE:  # ★终点不可达
            if icmp_code == 0:
                failed_info = f"终点不可达-->network_unreachable icmp_type={icmp_type} icmp_code={icmp_code}"
            elif icmp_code == 1:
                failed_info = f"终点不可达-->host_unreachable icmp_type={icmp_type} icmp_code={icmp_code}"
            elif icmp_code == 2:
                failed_info = f"终点不可达-->protocol_unreachable icmp_type={icmp_type} icmp_code={icmp_code}"
            elif icmp_code == 3:
                failed_info = f"终点不可达-->port_unreachable icmp_type={icmp_type} icmp_code={icmp_code}"
            elif icmp_code == 4:
                failed_info = f"终点不可达-->fragmentation_required icmp_type={icmp_type} icmp_code={icmp_code}"
            elif icmp_code == 5:
                failed_info = f"终点不可达-->source_route_failed icmp_type={icmp_type} icmp_code={icmp_code}"
            elif icmp_code == 6:
                failed_info = f"终点不可达-->network_unknown icmp_type={icmp_type} icmp_code={icmp_code}"
            elif icmp_code == 7:
                failed_info = f"终点不可达-->host_unknown icmp_type={icmp_type} icmp_code={icmp_code}"
            elif icmp_code == 8:
                failed_info = f"终点不可达-->source_host_isolated icmp_type={icmp_type} icmp_code={icmp_code}"
            elif icmp_code == 9:
                failed_info = f"终点不可达-->network_administratively_prohibited icmp_type={icmp_type} icmp_code={icmp_code}"
            elif icmp_code == 10:
                failed_info = f"终点不可达-->host_administratively_prohibited icmp_type={icmp_type} icmp_code={icmp_code}"
            elif icmp_code == 11:
                failed_info = f"终点不可达-->network_unreachable_tos icmp_type={icmp_type} icmp_code={icmp_code}"
            elif icmp_code == 12:
                failed_info = f"终点不可达-->host_unreachable_tos icmp_type={icmp_type} icmp_code={icmp_code}"
            elif icmp_code == 13:
                failed_info = f"终点不可达-->communication_administratively_prohibited icmp_type={icmp_type} icmp_code={icmp_code}"
            elif icmp_code == 14:
                failed_info = f"终点不可达-->host_precedence_violation icmp_type={icmp_type} icmp_code={icmp_code}"
            elif icmp_code == 13:
                failed_info = f"终点不可达-->precedence_cutoff icmp_type={icmp_type} icmp_code={icmp_code}"
            else:
                failed_info = f"终点不可达-->UNKNOWN_CODE icmp_type={icmp_type} icmp_code={icmp_code}"
        elif icmp_type == 4:  # ★源点不可达
            failed_info = f"源点不可达  icmp_type={icmp_type} icmp_code={icmp_code}"
        elif icmp_type == 5:  # ★路由重定向
            if icmp_code == 0:
                failed_info = f"路由重定向-->for_network  icmp_type={icmp_type} icmp_code={icmp_code}"
            elif icmp_code == 1:
                failed_info = f"路由重定向-->for_host  icmp_type={icmp_type} icmp_code={icmp_code}"
            elif icmp_code == 2:
                failed_info = f"路由重定向-->for_tos_and_network  icmp_type={icmp_type} icmp_code={icmp_code}"
            elif icmp_code == 3:
                failed_info = f"路由重定向-->for_tos_and_host  icmp_type={icmp_type} icmp_code={icmp_code}"
            else:
                failed_info = f"路由重定向-->UNKNOWN_CODE  icmp_type={icmp_type} icmp_code={icmp_code}"
        elif icmp_type == ICMP_TYPE_11_TIME_TO_LIVE_EXCEEDED:  # ★时间超时
            if icmp_code == 0:
                failed_info = f"时间超时--ttl_超时_传输过程中减为0了  icmp_type={icmp_type} icmp_code={icmp_code}"
            elif icmp_code == 1:
                failed_info = f"时间超时--分片重组超时  icmp_type={icmp_type} icmp_code={icmp_code}"
            else:
                failed_info = f"时间超时--UNKNOWN_CODE  icmp_type={icmp_type} icmp_code={icmp_code}"
        elif icmp_type == 12:  # ★IP头参数问题
            if icmp_code == 0:
                failed_info = f"IP头参数问题-->pointer_indicates_error  icmp_type={icmp_type} icmp_code={icmp_code}"
            elif icmp_code == 1:
                failed_info = f"IP头参数问题-->missing_required_option  icmp_type={icmp_type} icmp_code={icmp_code}"
            elif icmp_code == 2:
                failed_info = f"IP头参数问题-->bad_length  icmp_type={icmp_type} icmp_code={icmp_code}"
            else:
                failed_info = f"IP头参数问题-->UNKNOWN_CODE  icmp_type={icmp_type} icmp_code={icmp_code}"
        else:  # ★未知错误类型
            failed_info = f"未知错误类型  icmp_type={icmp_type} icmp_code={icmp_code}"
        return failed_info


class PingIPv6OnePacket:
    def __init__(self):
        pass


class TcpPing:
    def __init__(self):
        pass


# #################################  end of module  ##############################
if __name__ == '__main__':
    print("Hello, this is cofping.py")
