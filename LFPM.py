import math
import threading
from typing import Optional


class PacketInformation:  # Packet timestamp and leftmost bit
    time: float
    leftmost: int

    def __init__(self, time: float, leftmost: int):
        self.time = time
        self.leftmost = leftmost

    def __str__(self):
        return "(" + str(self.leftmost) + ", " + str(self.time) + ")"


class LFPM:  # List of Future Possible Maxima as described in the article by Chabchoub and Hebrail
    _packets: list[PacketInformation]

    def __init__(self):
        self._packets = list()

    def is_empty(self) -> bool:
        return len(self._packets) == 0

    def add_packet(self, packet: PacketInformation) -> None:
        # Add a packet according to the algorithm proposed in the article
        self._packets = list(filter(lambda info: info.leftmost > packet.leftmost, self._packets))
        self._packets.append(packet)

    def extract_highest_leftmost(self, time: float, duration: float) -> Optional[int]:
        # Extract the highest number of leftmost 1 from the LFPM for the last <duration> seconds
        # according to the rules proposed in the article
        filtered = list(filter(lambda info: float(info.time) >= (time - duration), self._packets))
        if len(filtered) == 0:
            return None
        return max(filtered, key=lambda info: info.leftmost).leftmost

    def print_status(self) -> None:
        print(len(self._packets), "packets:")
        for packet in self._packets:
            print(str(packet), end='')
        print()

    def status(self) -> str:
        # Get the status of the LFPM as a printable string

        res = str(len(self._packets)) + " packets:"
        for packet in self._packets:
            res += str(packet)
        return res


class LFPMList:  # Thread safe list of LFPMs
    _size: int
    _LFPMs: list[LFPM]
    _LFPMs_lock: threading.Lock

    def __init__(self, size: int):
        self._size = size
        self._LFPMs = [LFPM() for _ in range(self._size)]
        self._LFPMs_lock = threading.Lock()

    def get_size(self) -> int:
        return self._size

    def add_packet_for_index(self, index: int, packet: PacketInformation) -> None:
        if index >= self._size:
            raise IndexError("LFPMs list received illegal index")

        self._LFPMs_lock.acquire()
        self._LFPMs[index].add_packet(packet=packet)
        self._LFPMs_lock.release()

    def small_range_correction(self, E: float, m: int) -> float:
        # Apply Linear Counting
        # E is the current estimate
        # m is the amount of LFPMs

        V = sum(lfpm.is_empty() for lfpm in self._LFPMs)
        if V == 0:
            return E
        else:
            return m*math.log2(m/V)

    def estimate_cardinality(self, time: float, duration: Optional[float], m: int, use_src: bool, src_used: [bool]) -> int:
        # Estimate the cardinality according to the HyperLogLog algorithm
        # time is the current time
        # duration is the duration in which we want to estimate the cardinality
        # m is the amount of LFPMs
        # use_src specifies whether to use Small Range Correction
        # src_used[0] is set if Small Range Correction has been applied

        self._LFPMs_lock.acquire()
        l_duration = 9999999999  # we are using 9999999999 as a dummy time duration. This means this script will only consider packets in the last 2286 years.
        if duration is not None:
            l_duration = duration

        temp = 0.0
        for lfpm in self._LFPMs:
            rightmost = lfpm.extract_highest_leftmost(time=time, duration=l_duration)
            if rightmost is not None:
                temp += 2 ** (-1 * rightmost)

        self._LFPMs_lock.release()

        if temp == 0.0:
            return 0

        Z = temp ** (-1)
        E = alpha_m(m) * m * m * Z

        if E <= (5*m)/2 and use_src:
            src_used[0] = True
            return round(self.small_range_correction(E, m))
        return round(E)

    def print_status(self) -> None:
        self._LFPMs_lock.acquire()
        for i, lfpm in enumerate(self._LFPMs):
            print(str(i) + ": ", end='')
            print(lfpm.status())
        self._LFPMs_lock.release()

    def status(self) -> str:
        # Get the status of the LFPMs as a printable string

        self._LFPMs_lock.acquire()
        res = ""
        for i, lfpm in enumerate(self._LFPMs):
            res += str(i) + ": " + lfpm.status() + "\n"
        self._LFPMs_lock.release()
        return res


def alpha_m(m: int) -> float:  # Estimate alpha_m according to suggestion on the HyperLogLog article by
    # Flajolet, Philippe; Fusy, Éric; Gandouet, Olivier; Meunier, Frédéric (2007).

    if m == 16:
        return 0.673
    elif m == 32:
        return 0.697
    elif m == 64:
        return 0.709
    else:
        return 0.7213 / (1 + (1.079 / m))
