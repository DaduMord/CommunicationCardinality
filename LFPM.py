
class PacketInformation:  # Packet timestamp and leftmost bit
    time: float
    leftmost: int

    def __init__(self, time: float, leftmost: int):
        self.time = time
        self.leftmost = leftmost


class LFPM:  # List of Future Possible Maxima as described in the article by Chabchoub and Hebrail
    packets: list[PacketInformation]

    def __init__(self):
        self.packets = list()

    def add_packet(self, packet: PacketInformation) -> None:
        self.packets = list(filter(lambda info: info.leftmost > packet.leftmost, self.packets))
        self.packets.append(packet)

    def extract_highest_leftmost(self, time: float, duration: float) -> int:
        filtered = list(filter(lambda info: info.time >= (time - duration), self.packets))
        return max(filtered, key=lambda info: info.leftmost).leftmost
