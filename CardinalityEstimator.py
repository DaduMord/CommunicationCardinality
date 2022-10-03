
###############################################################
# This work is based on the article "Sliding HyperLogLog:
# Estimating Cardinality in a Data Stream over a Sliding
# Window" by Yousra Chabchoub, Georges Hebrail; 2010
###############################################################

import argparse
import sys
import time
from math import log2
from hashlib import sha256
import pyshark
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


def is_power_of_two(n: int) -> bool:
    return (n & (n - 1) == 0) and n != 0


def get_leftmost_1_position(binary_str: str) -> int:  # TODO: start count at 0 or 1? consult Eran
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
    binary_hash = pad_binary_with_0(get_binary_from_hex(hashed_dcid), 256)  # 256 because hash result is 32 chars
    j, rest = binary_hash[0:b], binary_hash[b:]
    leftmost = get_leftmost_1_position(rest)

    information = PacketInformation(timestamp, leftmost)
    LFPMs.add_packet_for_index(int(j, 2), information)


def run_loop() -> None:
    for packet in capture.sniff_continuously():
        process_packet(packet.sniff_timestamp, packet["quic"])


if __name__ == "__main__":
    args = parser.parse_args()

    if not is_power_of_two(args.memory):
        raise Exception("Please enter a number that is a power of 2 for m")

    b: int = int(log2(args.memory))
    if b > 128:
        raise Exception("Number of buckets is too large. You are using **WAY** too much memory")

    alpha_m = alpha_m(args.memory)
    LFPMs = LFPMList(b)

    if args.file is None:
        capture = pyshark.LiveCapture(display_filter="quic")
    else:
        capture = pyshark.FileCapture(input_file=args.file, display_filter="quic")

    loop_thread = threading.Thread(target=run_loop)  # TODO: does this need capture as an argument?
    loop_thread.daemon = True  # This is set to terminate the thread when the program exits
    loop_thread.start()

    while True:
        user_input = input()
        if user_input == "exit" or user_input == "quit" or user_input == "exit/quit":
            sys.exit()
        else:
            try:
                input_duration = float(user_input)
            except ValueError:
                print("Please insert a valid float number or exit/quit to terminate the program")
                continue

            estimation = LFPMs.estimate_cardinality(time=time.time(), duration=input_duration, m=args.memory)  # TODO: check that time is ok here
            print("Cardinality estimation is:", estimation)




