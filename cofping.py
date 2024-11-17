#!/usr/bin/env python
# -*- coding: utf-8 -*-
# coding=utf-8
# module name: cofping
# author: Cof-Lee <cof8007@gmail.com>
# this module uses the GPL-3.0 open source protocol
# update: 2024-11-18

import array
import ctypes
import struct
import time
import socket
import random
import string

ICMP_ECHO_REQUEST_TYPE_ID = 0x08
ICMP_ECHO_RESPOND_TYPE_ID = 0x00


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


class ResultOfPingOnePackage:
    def __init__(self, respond_source_ip="", respond_destination_ip=0, rtt_ms=0.0, icmp_data_size=0, ttl=0, is_success=False,
                 icmp_type=0, icmp_code=0, icmp_checksum=0x0000, icmp_id=0x0000, icmp_sequence=0x0000,
                 icmp_data=b'', failed_info=""):
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
        self.failed_info = failed_info  # 如果检测不成功，必须提示失败信息


class PingOnePackage:
    """
    单次ping检测，只会发送1个icmp_echo_request报文，然后等待回复
    """

    def __init__(self, target_ip="", timeout=2, size=1, df=False):
        self.target_ip = target_ip  # 目标ip（ipv4地址）
        self.timeout = timeout  # 超时，单位：秒
        self.size = size  # 发包数据大小，单位：字节，当整个报文长度小于mac帧长度要求时，会自动以0填充
        self.df = df  # 置True时不分片，置False时分片
        self.result = ResultOfPingOnePackage()
        self.is_finished = False
        self.icmp_send_type = ICMP_ECHO_REQUEST_TYPE_ID  # icmp_echo_request
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
        self.icmp_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname("icmp"))
        self.icmp_socket.settimeout(self.timeout)
        self.start_time = time.time()
        try:
            self.icmp_socket.sendto(self.icmp_send_packet, (self.target_ip, 0))  # 每次发送完报文后，此icmp_socket就变了
        except OSError as err:
            self.is_finished = True
            stop_thread_silently(self.recv_thread)
            self.result.is_success = False
            self.result.failed_info = err.__str__()
            return
        self.recv_icmp_packet()  # 阻塞型
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
                print(f"PingOnePackage.recv_icmp_packet: {self.target_ip}接收超时了 {used_time}")
                self.result.is_success = False
                self.result.failed_info = "timeout"
                self.result.rtt_ms = self.timeout * 1000
                self.is_finished = True
                return
            try:
                recv_packet, addr = self.icmp_socket.recvfrom(65535)  # 接收到整个ip报文，阻塞型函数
            except Exception as e:  # 超时会报异常
                print("\nPingOnePackage.recv_icmp_packet: 接收报异常超时了", e)
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
            icmp_type, icmp_code, icmp_checksum, icmp_id, icmp_sequence = struct.unpack("bbHHH", icmp_header)
            if icmp_id == self.icmp_send_id and icmp_sequence == self.icmp_send_sequence and icmp_type != ICMP_ECHO_REQUEST_TYPE_ID:
                self.result.rtt_ms = rtt_s * 1000
                ipv4_struct_tuple = struct.unpack("!BBHHHBBHII", ipv4_header)
                if icmp_type == ICMP_ECHO_RESPOND_TYPE_ID and icmp_code == 0x00:
                    self.result.is_success = True
                else:
                    self.result.is_success = False
                    self.result.failed_info = self.generate_icmp_failed_info(icmp_type, icmp_code)

                self.result.ttl = ipv4_struct_tuple[5]
                self.result.respond_source_ip = addr[0]
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
        return "failed type_code: " + icmp_type + " " + icmp_code


class Ping6:
    def __init__(self):
        pass


class TcpPing:
    def __init__(self):
        pass
