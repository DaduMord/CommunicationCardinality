
###############################################################
# This work is based on the article "Sliding HyperLogLog:
# Estimating Cardinality in a Data Stream over a Sliding
# Window" by Yousra Chabchoub, Georges Hebrail; 2010
###############################################################

import argparse
import os.path
import sys
import platform
import threading
import time
from typing import Tuple
from math import log2
from hashlib import sha256
import pyshark
from LFPM import *

sys_type = platform.system()  # need to check system type to know whether to use \ or /.
if sys_type == "Windows":
    dir_sign = "\\"
elif sys_type == "Linux":
    dir_sign = "/"
else:
    raise Exception("Error: Script should be run on Windows or Linux platforms only")


def get_default_log() -> str:
    return "." + dir_sign + "logs" + dir_sign + "log.txt"


class ThreadSafeSet:
    _data: set[str]
    _data_lock: threading.Lock

    def __init__(self):
        self._data = set()
        self._data_lock = threading.Lock()

    def add(self, value: str):
        self._data_lock.acquire()
        self._data.add(value)
        self._data_lock.release()

    def remove(self, value: str):
        self._data_lock.acquire()
        self._data.remove(value)
        self._data_lock.release()

    def get_len(self):
        self._data_lock.acquire()
        ret = len(self._data)
        self._data_lock.release()
        return ret


parser = argparse.ArgumentParser(description="A program to estimate QUIC connection cardinality using sliding window \
                                             HyperLogLog method based on \"Sliding HyperLogLog: Estimating Cardinality \
                                             in a Data Stream over a Sliding Window\" by \
                                             Y. Chabchoub, G. Hebrail; 2010")

parser.add_argument("-m",
                    "--memory",
                    type=int,
                    default=64,
                    help="Amount of buckets in memory to use. This number should be a power of 2 \
                         and higher or equal to 16. Defaults to 64.")

parser.add_argument("-v",
                    "--verify",
                    action="store_true",
                    help="Print the actual cardinality to verify correctness.")

parser.add_argument("-f",
                    "--file",
                    type=str,
                    default=None,
                    help="Capture from a .pcap file instead of a live capture.")

parser.add_argument("-l",
                    "--log",
                    type=str,
                    default=get_default_log(),
                    help="Path to log file in which you would like to save your output. \
                         Defaults to <current_folder>\\logs\\log.txt")


def is_power_of_two(n: int) -> bool:
    return (n & (n - 1) == 0) and n != 0


def check_m_validity(m: int) -> None:
    if not is_power_of_two(args.memory):
        raise AttributeError("Please enter a number that is a power of 2 for m")
    # TODO: should raise exception here if m is too low? Consult Eran
    if m < 16:
        raise AttributeError("Please enter a larger number for m. it should be 16 or larger.")


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

    if args.verify:
        verify_set.add(dcid)


def run_loop() -> None:
    if args.file is None:  # TODO: check this is working
        for packet in capture.sniff_continuously():
            process_packet(packet.sniff_timestamp, packet["quic"])
    else:
        for packet in capture:
            process_packet(packet.sniff_timestamp, packet["quic"])
        print("Completed File Reading")


def print_and_log(*values) -> None:
    print(*values)

    if len(values) == 0:
        log_file.write("\n")
        return

    str_to_write: str = " ".join(list( map(lambda val: str(val), values) ))
    log_file.write(str_to_write + "\n")


def small_range_warning(estimation):
    # TODO: make estimate_cardinality actually apply the small range correction and delete this
    if estimation <= 5*args.memory/2 and estimation != 0:
        print_and_log("Warning: the estimation is too low to be accurate according to HyperLogLog article")


if __name__ == "__main__":
    # file flag: -f ".\100 QUIC Connections.pcapng"
    # TODO: delete this
    args = parser.parse_args()

    check_m_validity(args.memory)

    if not os.path.exists("." + dir_sign + "logs"):
        os.makedirs("." + dir_sign + "logs")
        print("logs folder created at " + os.getcwd() + dir_sign + "logs")

    b: int = int(log2(args.memory))
    if b > 128:
        raise AttributeError("Number of buckets is too large. You are using **WAY** too much memory")

    alpha_m = alpha_m(args.memory)
    LFPMs = LFPMList(args.memory)

    start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    if args.file is None:
        capture = pyshark.LiveCapture(display_filter="quic")
    else:
        capture = pyshark.FileCapture(input_file=args.file, display_filter="quic")

    log_file = open(args.log, mode="a")
    print_and_log("\nStarting estimator on time: " + start_time + "\n\n")
    # event_log_file = open("." + dir_sign + "logs" + dir_sign + "event_log.txt", mode="a")

    # The daemon flag is set to terminate the thread when the program exits
    loop_thread = threading.Thread(target=run_loop, daemon=True)
    loop_thread.start()

    verify_set: ThreadSafeSet = ThreadSafeSet()

    start_message = "Running with arguments:\n" \
        + "\t" + "Memory Buckets (LFPMs): " + str(args.memory) + "\n" \
        + "\t" + (("Capturing from file: " + args.file + "\n\tPlease wait for the file to complete reading before exiting (for logging purposes)\n"
                   ) if args.file is not None else ("Live Capture (No Capture File)\n")) \
        + "\t" + "Log File: " + args.log + "\n" \
        + "\t" + ("Verifying the real cardinality (warning: this increases processing times)\n" if args.verify else "") \
        + "\n" \
        + "The estimator is running in the background and it takes your input for instructions.\n" \
        + "Instruction List:\n" \
        + "\t" + "To estimate the cardinality you may enter a blank input or the inputs \"estimate\", \"cardinality\".\n" \
        + "\t" + "To estimate the cardinality in the last <n> seconds enter <n> as input.\n" \
        + "\t" + "You may also enter the keyword \"status\" as input to print the current LFPMs status.\n" \
        + "\t" + "To quit the estimator enter \"exit\" or \"quit\"."
    print(start_message)

    while True:
        user_input = input()
        curr_time = time.time()
        if user_input == "exit" or user_input == "quit" or user_input == "exit/quit":
            end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            print_and_log("Stopping Estimator on time:", end_time)
            break

        elif user_input == "status":
            print("Status of the LFPMs is:")
            print(LFPMs.status())
            log_file.write("Status of the LFPMs is:")
            log_file.write(LFPMs.status())

        elif user_input == "" or user_input == "estimate" or user_input == "cardinality":
            estimation = LFPMs.estimate_cardinality(time=curr_time, duration=None, m=args.memory)
            print_and_log("Cardinality estimation is:", estimation)
            small_range_warning(estimation)
            if args.verify:
                print_and_log("Actual cardinality is:", verify_set.get_len()//2)

        else:
            try:
                input_duration = float(user_input)
            except ValueError:
                print("Please insert a valid float number or exit/quit to terminate the program")
                log_file.write("Illegal input inserted: " + user_input + '\n')
                continue

            estimation = LFPMs.estimate_cardinality(time=curr_time, duration=input_duration, m=args.memory)
            print_and_log("Current time is:", time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(curr_time)))
            print_and_log("\tand the cardinality estimation for duration", input_duration, "is:", estimation)
            small_range_warning(estimation)
            if args.verify:
                print_and_log("\tThere is currently no support for a cardinality verification with specified duration")
