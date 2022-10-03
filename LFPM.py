
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
        self._packets = list(filter(lambda info: info.leftmost > packet.leftmost, self._packets))
        self._packets.append(packet)

    def extract_highest_leftmost(self, time: float, duration: float) -> Optional[int]:
        filtered = list(filter(lambda info: float(info.time) >= (time - duration), self._packets))
        if len(filtered) == 0:
            return None
        return max(filtered, key=lambda info: info.leftmost).leftmost

    def print_status(self) -> None:
        print(len(self._packets), "packets:")
        for packet in self._packets:
            print(str(packet), end='')
        print()


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

    def estimate_cardinality(self, time: float, duration: Optional[float], m: int) -> float:
        self._LFPMs_lock.acquire()
        l_duration = 9999999999 # we are using 9999999999 as a dummy time duration. This means this script will only consider packets in the last 2286 years.
        if duration is not None:
            l_duration = duration

        temp = 0.0
        for lfpm in self._LFPMs:
            rightmost = lfpm.extract_highest_leftmost(time=time, duration=l_duration)
            if rightmost is not None:
                temp += 2 ** (-1 * rightmost)

        if temp == 0.0:
            return 0.0

        Z = temp ** (-1)

        self._LFPMs_lock.release()
        return alpha_m(m) * m * m * Z

    def print_status(self) -> None:
        self._LFPMs_lock.acquire()
        for i, lfpm in enumerate(self._LFPMs):
            print(str(i) + ": ", end='')
            lfpm.print_status()
        self._LFPMs_lock.release()


def alpha_m(m: int) -> float:  # Estimate alpha_m according to suggestion on the HyperLogLog article by
    # Flajolet, Philippe; Fusy, Éric; Gandouet, Olivier; Meunier, Frédéric (2007).
    if m < 16:
        # TODO: check this and maybe move it to the start of the main. Consult Eran
        raise Exception("This algorithm does not work well with m < 16. Consider using a different algorithm.")
    if m == 16:
        return 0.673
    if m == 32:
        return 0.697
    if m == 64:
        return 0.709
    else:
        return 0.7213 / (1 + (1.079 / m))
