
import unittest
from LFPM import *


class LFPMTest(unittest.TestCase):

    # def test_add_packet_removes_old_packets(self):
    #     lfpm = LFPM(self.W)
    #     lfpm.add_packet(PacketInformation(1.0, 6))
    #     lfpm.add_packet(PacketInformation(1.5, 5))
    #     lfpm.add_packet(PacketInformation(2.0, 4))
    #     lfpm.add_packet(PacketInformation(100.0, 3))
    #
    #     assert(len(lfpm.packets) == 4)
    #
    #     lfpm.add_packet(PacketInformation(10**6 + 50.0, 2))
    #
    #     assert(len(lfpm.packets) == 2)

    def test_add_packet_removes_low_leftmost_packets(self):
        lfpm = LFPM()
        lfpm.add_packet(PacketInformation(1.0, 6))
        lfpm.add_packet(PacketInformation(1.5, 4))
        lfpm.add_packet(PacketInformation(3.0, 3))

        assert (len(lfpm.packets) == 3)

        lfpm.add_packet(PacketInformation(4.0, 5))

        assert(len(lfpm.packets) == 2)

    def test_extract_returns_packets(self):
        lfpm = LFPM()
        lfpm.add_packet(PacketInformation(10.0, 4))
        lfpm.add_packet(PacketInformation(15.0, 2))
        lfpm.add_packet(PacketInformation(20.0, 1))

        assert lfpm.extract_highest_leftmost(20, 11) == 4
        assert lfpm.extract_highest_leftmost(20, 21) == 4
        assert lfpm.extract_highest_leftmost(20, 6) == 2
        assert lfpm.extract_highest_leftmost(20, 3) == 1
        assert lfpm.extract_highest_leftmost(16, 3) == 2
        assert lfpm.extract_highest_leftmost(16, 7) == 4
