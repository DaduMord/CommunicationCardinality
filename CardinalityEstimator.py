
###############################################################
# This work is based on the article "Sliding HyperLogLog:
# Estimating Cardinality in a Data Stream over a Sliding
# Window" by Yousra Chabchoub, Georges Hebrail; 2010
###############################################################

import argparse
from math import log2
from hashlib import sha256
import pyshark
import multiprocessing
from LFPM import *

parser = argparse.ArgumentParser(description="A program to estimate QUIC connection cardinality using sliding window \
                                             HyperLogLog method based on \"Sliding HyperLogLog: Estimating Cardinality \
                                             in a Data Stream over a Sliding Window\" by \
                                             Y. Chabchoub, G. Hebrail; 2010")

parser.add_argument("-m",
                    "--memory",
                    type=int,
                    default=1024,
                    help="amount of buckets in memory to use. this number should be a power of 2.")

parser.add_argument("-v",
                    "--verify",
                    action="store_true",
                    help="print the actual cardinality to verify correctness.")

parser.add_argument("-f",
                    "--file",
                    type=str,
                    default=None,
                    help="capture from a .pcap file instead of a live capture.")


def process_packet(timestamp: float, quic_layer) -> None:
    header_form = quic_layer.get_field_value("header_form")
    long_packet_type = quic_layer.get_field_value("long_packet_type")
    if header_form == "1" and long_packet_type == "0":  # ignore initial packets
        return

    dcid = quic_layer.get_field_value("dcid")
    if dcid is None:
        return

    dcid = dcid.replace(":", "")
    hashed_dcid = sha256(dcid.encode()).hexdigest()
    binary_hash = pad_binary_with_0(get_binary_from_hex(hashed_dcid), 256) # 256 because hash result is 32 chars
    j, rest = binary_hash[0:b], binary_hash[b:]
    leftmost = get_leftmost_1_position(rest)

    LFPMs[int(j, 2)].add_packet(PacketInformation(timestamp, leftmost))

def estimate_cardinality(duration: float) -> float:
    pass # TODO: finish

def get_leftmost_1_position(binary_str: str) -> int:  #TODO: start count at 0 or 1?
    leftmost = 0
    for char in binary_str:
        if char == "1":
            return leftmost
        else:
            leftmost += 1
    return leftmost

def pad_binary_with_0(binary_str: str, target_length: int) -> str:
    if len(binary_str) < target_length:
        return "0" * (target_length - len(binary_str)) + binary_str
    else:
        return binary_str


def get_binary_from_hex(hex_str: str) -> str:
    return bin(int(hex_str, 16)).replace("0b", "")


def is_power_of_two(n: int) -> bool:
    return (n & (n - 1) == 0) and n != 0


if __name__ == "__main__":
    args = parser.parse_args()

    if not is_power_of_two(args.memory):
        raise Exception("Please enter a number that is a power of 2 for m")

    b: int = int(log2(args.memory))
    if b > 128:
        raise Exception("Number of buckets is too large. You are using **WAY** too much memory")

    LFPMs = [LFPM() for _ in range(args.memory)]  # TODO: check that it creates different instances

    if args.file is None:
        capture = pyshark.LiveCapture(display_filter="quic")
    else:
        capture = pyshark.FileCapture(input_file=args.file, display_filter="quic")

    for packet in capture.sniff_continuously():
        process_packet(packet.sniff_timestamp, packet["quic"])


