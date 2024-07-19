#!/usr/bin/env python
# -*- coding: utf-8 -*-
# coding=utf-8
# module name: cofnet
# author: Cof-Lee
# this module uses the GPL-3.0 open source protocol
# update: 2024-07-19

"""
术语解析:
maskint    掩码数字型 ，如 24 ，子网掩码位数，           类型: int
maskbyte   掩码字节型 ，如 255.255.255.0 ，子网掩码，   类型: str
ip         ip地址称，如 10.1.1.2 ，不含掩码            类型: str
netseg     网段，如 10.1.0.0 ，不含掩码                类型: str
cidr       地址块，网段及掩码位数 ，如 10.1.0.0/16      类型: str
hostseg    主机号，一个ip地址去除网段后，剩下的部分       类型: int
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


# #################################  start of module's function  ##############################
def is_ip_addr(input_str: str) -> bool:
    """
    判断 输入字符串 是否为 ip地址，返回bool值，是则返回True，否则返回False
    """
    seg_list = input_str.split(".")
    if len(seg_list) != 4:
        return False
    if seg_list[0].isdigit():
        if 0 > int(seg_list[0]) or int(seg_list[0]) > 255:
            return False
    if seg_list[1].isdigit():
        if 0 > int(seg_list[1]) or int(seg_list[1]) > 255:
            return False
    if seg_list[2].isdigit():
        if 0 > int(seg_list[2]) or int(seg_list[2]) > 255:
            return False
    if seg_list[3].isdigit():
        if 0 > int(seg_list[3]) or int(seg_list[3]) > 255:
            return False
        else:
            return True
    else:
        return False


def is_cidr(input_str: str) -> bool:
    """
    判断 输入字符串 是否为 cidr地址块，返回bool值，是则返回True，否则返回False
    输入 "10.99.1.0/24" 输出 True
    输入 "10.99.1.1/24" 输出 False ，不是正确的cidr地址块写法，24位掩码，的最后一字节必须为0
    """
    seg_list = input_str.split(".")
    if len(seg_list) != 4:
        return False
    if seg_list[0].isdigit():
        if 0 > int(seg_list[0]) or int(seg_list[0]) > 255:
            return False
    if seg_list[1].isdigit():
        if 0 > int(seg_list[1]) or int(seg_list[1]) > 255:
            return False
    if seg_list[2].isdigit():
        if 0 > int(seg_list[2]) or int(seg_list[2]) > 255:
            return False
    if seg_list[3].isdigit():
        return False
    seg_list2 = seg_list[3].split("/")
    if len(seg_list2) == 2:
        if seg_list2[1].isdigit():
            if 0 > int(seg_list2[1]) or int(seg_list2[1]) > 32:
                return False
    else:
        return False
    seg_list3 = input_str.split("/")
    if len(seg_list3) == 2:
        seg_list4 = seg_list3[0].split(".")
        ip_mask_int = int(seg_list4[0]) << 24 | int(seg_list4[1]) << 16 | int(seg_list4[2]) << 8 | int(seg_list4[3])
        if seg_list3[1].isdigit():
            ip_mask_int_and = ip_mask_int & (0xFFFFFFFF << (32 - int(seg_list3[1])))
        else:
            return False
        if ip_mask_int != ip_mask_int_and:
            return False
    else:
        return False
    return True


def is_ip_maskint_addr(input_str: str) -> bool:
    """
    判断 输入字符串 是否为 ip/子网掩码位数 的格式，返回bool值，是则返回True，否则返回False，例：
    输入 "10.99.1.55/24" 输出 True
    输入 "10.99.1.55/255.255.255.0" 输出 False，原因是 / 后面只能接数字，不能接子网掩码byte型
    """
    ip_maskint_seg_list = input_str.split("/")
    if len(ip_maskint_seg_list) != 2:
        return False
    if not ip_maskint_seg_list[1].isdigit():
        return False
    seg_list = ip_maskint_seg_list[0].split(".")
    if len(seg_list) != 4:
        return False
    if seg_list[0].isdigit():
        if 0 > int(seg_list[0]) or int(seg_list[0]) > 255:
            return False
    if seg_list[1].isdigit():
        if 0 > int(seg_list[1]) or int(seg_list[1]) > 255:
            return False
    if seg_list[2].isdigit():
        if 0 > int(seg_list[2]) or int(seg_list[2]) > 255:
            return False
    if seg_list[3].isdigit():
        if 0 > int(seg_list[3]) or int(seg_list[3]) > 255:
            return False
        else:
            return True
    else:
        return False


def is_ip_range(input_str: str) -> bool:
    """
    判断 输入字符串 是否为 ip地址范围，返回bool值，是则返回True，否则返回False
    输入 "10.99.1.33-55" 输出 True
    输入 "10.99.1.22-10" 输出 False ，不是正确的地址范围，首ip大于了尾ip
    """
    seg_list = input_str.split(".")
    if len(seg_list) != 4:
        return False
    if seg_list[0].isdigit():
        if 0 > int(seg_list[0]) or int(seg_list[0]) > 255:
            return False
    if seg_list[1].isdigit():
        if 0 > int(seg_list[1]) or int(seg_list[1]) > 255:
            return False
    if seg_list[2].isdigit():
        if 0 > int(seg_list[2]) or int(seg_list[2]) > 255:
            return False
    if seg_list[3].isdigit():
        return False
    seg_list2 = seg_list[3].split("-")
    if len(seg_list2) == 2:
        if seg_list2[0].isdigit():
            if 0 > int(seg_list2[0]) or int(seg_list2[0]) > 255:
                return False
        if seg_list2[1].isdigit():
            if 0 > int(seg_list2[1]) or int(seg_list2[1]) > 255:
                return False
        if int(seg_list2[0]) >= int(seg_list2[1]):
            return False
        return True
    else:
        return False


def is_ip_range_2(input_str: str) -> bool:
    """
    判断 输入字符串 是否为 ip地址范围，返回bool值，是则返回True，否则返回False
    输入 "10.99.1.33-10.99.1.55" 输出 True
    输入 "10.99.1.22-10.99.1.10" 输出 False ，不是正确的地址范围，首ip大于了尾ip
    """
    input_seg = input_str.split("-")
    if len(input_seg) != 2:
        return False
    seg1_list = input_seg[0].split(".")
    seg2_list = input_seg[1].split(".")
    if len(seg1_list) != 4:
        return False
    if len(seg2_list) != 4:
        return False
    if ip_mask_to_int(input_seg[0]) > ip_mask_to_int(input_seg[1]):
        return False
    return True


def maskint_to_maskbyte(maskint: int) -> str:
    """
    将子网掩码数字型 转为 子网掩码字节型，例如：
    输入 16 输出 "255.255.0.0"
    输入 24 输出 "255.255.255.0
    """
    if maskint < 0 or maskint > 32:
        raise Exception("子网掩码数值应在[0-32]", maskint)
    mask = [0, 0, 0, 0]
    i = 0
    while maskint >= 8:
        mask[i] = 255
        i += 1
        maskint -= 8
    if i < 4:
        mask[i] = 255 - (2 ** (8 - maskint) - 1)
    mask_str_list = map(str, mask)
    return ".".join(mask_str_list)


def local__mask_seg_to_cidr(mask_seg: str) -> int:
    """
    将掩码其中一个字节的数字 转为 二进制数最开头的1的个数, 例如：
    输入 "192" 输出 2 ，即 1100 0000
    输入 "248" 输出 5 ，即 1111 1000
    输入 "255" 输出 8 ，即 1111 1111
    """
    mask_seg_1_number = 0
    mask_seg_int = int(mask_seg)
    while mask_seg_int != 0:
        mask_seg_1_number += 1
        mask_seg_int = (mask_seg_int << 1) & 0xFF
    return mask_seg_1_number


def maskbyte_to_maskint(maskbyte: str) -> int:
    """
    将子网掩码字节型 转为 子网掩码数字型，例如：
    输入 "255.255.255.0" 输出 24
    输入 "255.255.0.0"   输出 16
    """
    if not is_ip_addr(maskbyte):
        raise Exception("不是正确的子网掩码,E1", maskbyte)
    mask_seg_list = maskbyte.split(".")
    mask_seg_index = 0
    maskint = 0
    while mask_seg_list[mask_seg_index] == "255":
        maskint += 8
        mask_seg_index += 1
        if mask_seg_index == 4:
            break
    if mask_seg_index < 4 and mask_seg_list[mask_seg_index] != "":
        maskint += local__mask_seg_to_cidr(mask_seg_list[mask_seg_index])  # 依赖上面的 local_mask_seg_to_cidr()
    if maskbyte != maskint_to_maskbyte(maskint):
        raise Exception("不是正确的子网掩码,E2", maskbyte)
    return maskint


def ip_to_hex_string(ip_addresss: str) -> str:
    """
    将ip地址转为十六进制表示，例如：
    输入 "10.99.1.254" 输出 "0A6301FE"
    """
    if not is_ip_addr(ip_addresss):
        raise Exception("不是正确的ip地址,E1", ip_addresss)
    ip_hex_str_list = []
    for ip_seg in ip_addresss.split("."):
        ip_seg_int = int(ip_seg)
        # ip_hex_str_list.append(f"{ip_seg_int:0>2X}")
        ip_hex_str_list.append("{:0>2X}".format(ip_seg_int))
    return "".join(ip_hex_str_list)


def ip_mask_to_int(ip_or_mask: str) -> int:
    """
    将 ip地址或掩码byte型 转为 32 bit的数值，例如：
    输入 "255.255.255.0" 输出 4294967040
    输入 "192.168.1.1"   输出 3232235777
    """
    if not is_ip_addr(ip_or_mask):
        raise Exception("不是正确的ip地址或掩码", ip_or_mask)
    seg_list = ip_or_mask.split(".")
    ip_mask_int = int(seg_list[0]) << 24 | int(seg_list[1]) << 16 | int(seg_list[2]) << 8 | int(seg_list[3])
    return ip_mask_int


def ip_mask_to_binary_space(ip_or_mask: str) -> str:
    """
    将 ip地址或掩码byte型 转为 二进制数表示，★每8位数插入1个空格，例如：
    输入 "255.255.255.0" 输出
    输入 "192.168.1.1"   输出
    """
    if not is_ip_addr(ip_or_mask):
        raise Exception("不是正确的ip地址或掩码", ip_or_mask)
    bin_seg_list = []
    for ip_seg in ip_or_mask.split("."):
        ip_seg_int = int(ip_seg)
        # bin_seg_list.append(f"{ip_seg_int:0>8b}")
        bin_seg_list.append("{:0>8b}".format(ip_seg_int))
    return " ".join(bin_seg_list)


def get_maskint_with_space(maskint: int) -> int:
    """
    根据子网掩码位数，返回带空格时的掩码总长度，即每8位加1个空格字符
    """
    if not isinstance(maskint, int):
        raise Exception("不是正确的子风掩码位数", maskint)
    if maskint > 24:
        return maskint + 3
    elif maskint > 16:
        return maskint + 2
    elif maskint > 8:
        return maskint + 1
    else:
        return maskint


def int32_to_ip(int32: int) -> str:
    """
    将 32bit数值 转为 ipv4地址，例如:
    输入 174260481 输出 "10.99.1.1"
    """
    if int32 < 0 or int32 > 4294967295:
        raise Exception("ip地址数值应在[0-4294967295]", int32)
    ipaddress = [0, 0, 0, 0]
    ipaddress[0] = 0xFF & (int32 >> 24)
    ipaddress[1] = 0xFF & (int32 >> 16)
    ipaddress[2] = 0xFF & (int32 >> 8)
    ipaddress[3] = 0xFF & int32
    ipaddress_str_list = map(str, ipaddress)
    return ".".join(ipaddress_str_list)


def get_netseg_int(ip: str, maskintorbyte: str) -> int:
    """
    根据 子网掩码 获 取ip地址的 网段（int值），子网掩码可为int型或byte型，例如：
    输入 "10.99.1.1","24"             输出 174260480
    输入 "10.99.1.1","255.255.255.0"  输出 174260480
    """
    if not is_ip_addr(ip):
        raise Exception("不是正确的ip地址,E1", ip)
    maskintorbyte_seg = str(maskintorbyte).split(".")
    if len(maskintorbyte_seg) == 1:
        if int(maskintorbyte_seg[0]) < 0 or int(maskintorbyte_seg[0]) > 32:
            raise Exception("子网掩码数值应在[0-32]", maskintorbyte_seg)
        else:
            maskint2bin = 0xFFFFFFFF << (32 - int(maskintorbyte_seg[0]))
            return ip_mask_to_int(ip) & maskint2bin
    if len(maskintorbyte_seg) == 4:
        if not is_ip_addr(maskintorbyte):
            raise Exception("不是正确的掩码,E2", maskintorbyte)
        maskint2bin = 0xFFFFFFFF << (32 - int(maskbyte_to_maskint(maskintorbyte)))
        return ip_mask_to_int(ip) & maskint2bin
    else:
        raise Exception("不是正确的掩码,E3", maskintorbyte)


def get_netseg_byte(ip: str, maskintorbyte: str) -> str:
    """
    根据 子网掩码 获 取ip地址的 网段（byte值），子网掩码可为int型或byte型，例如：
    输入 "10.99.1.1","24"             输出 10.99.1.0
    输入 "10.99.1.1","255.255.255.0"  输出 10.99.1.0
    依赖上面的2个函数:  get_netseg_int() 以及 int32_to_ip()
    input <str,int/str> , output <str>
    """
    return int32_to_ip(get_netseg_int(ip, maskintorbyte))


def get_netseg_byte_c(cidr: str) -> str:
    """
    根据 cidr 获 取ip地址的 网段（byte值），子网掩码可为int型或byte型，例如：
    输入 "10.99.1.1/24"     输出 10.99.1.0
    依赖上面的2个函数:  get_netseg_int() 以及 int32_to_ip()
    """
    ip_mask_seg = cidr.split("/")
    return int32_to_ip(get_netseg_int(ip_mask_seg[0], ip_mask_seg[1]))


def get_hostseg_int(ip: str, maskintorbyte: str) -> int:
    """
    根据 子网掩码 获 取ip地址的 主机号（int值），子网掩码可为int型或byte型，例如：
    输入 "10.99.1.145","24"             输出 145 （主机号为第4个字节的值）
    输入 "10.99.1.145","255.255.255.0"  输出 145
    """
    if not is_ip_addr(ip):
        raise Exception("不是正确的ip地址,E1", ip)
    maskintorbyte_seg = str(maskintorbyte).split(".")
    if len(maskintorbyte_seg) == 1:
        if int(maskintorbyte_seg[0]) < 0 or int(maskintorbyte_seg[0]) > 32:
            raise Exception("子网掩码数值应在[0-32]", maskintorbyte_seg)
        else:
            maskint2bin = 0xFFFFFFFF << (32 - int(maskintorbyte_seg[0]))
            return ip_mask_to_int(ip) & ~maskint2bin
    if len(maskintorbyte_seg) == 4:
        if not is_ip_addr(maskintorbyte):
            raise Exception("不是正确的掩码,E2", maskintorbyte)
        maskint2bin = 0xFFFFFFFF << (32 - int(maskbyte_to_maskint(maskintorbyte)))
        return ip_mask_to_int(ip) & ~maskint2bin
    else:
        raise Exception("不是正确的掩码,E3", maskintorbyte)


def get_hostseg_num(maskint: int) -> int:
    """
    根据子网掩码位数获取主机号可表示的主同ip数量
    例如：24位的掩码，主机号为8位，可表示的主机ip数量为256
    """
    host_seg_num = (0xFFFFFFFF >> maskint) + 1
    return host_seg_num


def is_ip_in_cidr(ip: str, cidr: str) -> bool:
    """
    判断 ip地址 是否在 网段cidr内，此ip是否属于某网段地址块，返回bool值: True表示ip在网段内，False不在网段内
    输入 "10.99.1.1","10.99.1.0/24"  输出 True
    输入 "10.99.3.1","10.99.1.0/24"  输出 False
    """
    if not is_ip_addr(ip):
        raise Exception("不是正确的ip地址,E1", ip)
    if not is_cidr(cidr):
        raise Exception("不是正确的cidr地址块,E2", cidr)
    netseg_maskint = cidr.split("/")
    netseg = netseg_maskint[0]
    maskint = netseg_maskint[1]
    ipnetsegint = get_netseg_int(ip, maskint)
    netsegint = get_netseg_int(netseg, maskint)
    if ipnetsegint == netsegint:
        return True
    else:
        return False


def is_ip_in_net_maskbyte(ip: str, net: str, maskbyte: str) -> bool:
    """
    判断 ip地址 是否在 网段 net maskbyte内，是否属于某网段地址块，返回bool值: True表示ip在网段内，False不在网段内
    输入 "10.99.1.1","10.99.1.0","255.255.255.0"  输出 True
    输入 "10.99.3.1","10.99.1.0","255.255.255.0"  输出 False
    """
    if not is_ip_addr(ip):
        raise Exception("不是正确的ip地址,E1", ip)
    if not is_ip_addr(net):
        raise Exception("不是正确的网段,E2", net)
    if not is_ip_addr(maskbyte):
        raise Exception("不是正确的掩码,E3", maskbyte)
    ipnetsegint = get_netseg_int(ip, maskbyte)
    netsegint = get_netseg_int(net, maskbyte)
    if ipnetsegint == netsegint:
        return True
    else:
        return False


def is_ip_in_range(targetip: str, start_ip: str, end_ip: str) -> bool:
    """
    判断 ip地址 是否在 ip地址范围内，返回bool值: True表示ip在ip-range内，False不在ip-range内
    输入 "10.99.1.88","10.99.1.1","10.99.2.22"  输出 True
    输入 "10.99.1.88","10.99.1.1","10.99.1.22"  输出 False
    input <str, str, str> , output <bool>
    """
    if not is_ip_addr(targetip):
        raise Exception("不是正确的ip地址,E1", targetip)
    if not is_ip_addr(start_ip):
        raise Exception("不是正确的ip地址,E2", start_ip)
    if not is_ip_addr(end_ip):
        raise Exception("不是正确的ip地址,E3", end_ip)
    if ip_mask_to_int(end_ip) >= ip_mask_to_int(targetip) >= ip_mask_to_int(start_ip):
        return True
    else:
        return False


# #################################  end of module's function  ##############################
if __name__ == '__main__':
    print("this is cofnet.py")
