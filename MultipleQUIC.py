
import threading
import os
import time


def run_QUIC(conn_num: int = 1):
    for _ in range(conn_num):
        os.system("cd C:\\Technion\\CommunicationCardinality\\aioquic & \
                  python examples/http3_client.py \
                --ca-certs tests/pycacert.pem https://localhost:4433/10")


if __name__ == "__main__":

    # Number of connections is going to be thread_num * conns_per_thread.
    # Increase thread_num with care and be careful not to exceed your machine capabilities.
    # A thread_num of 10-15 should be a safe choice.

    thread_num = 10
    conns_per_thread = 10
    threads = [threading.Thread(target=run_QUIC, args=(conns_per_thread, )) for _ in range(thread_num)]

    start = time.time()
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    end = time.time()

    print("elapsed time is:", end - start)
