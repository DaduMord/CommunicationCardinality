
import threading
import os
import time


def run_QUIC(conn_num: int = 1) -> None:
    for _ in range(conn_num):  # Change this command to how you run your QUIC client
        os.system("cd C:\\Technion\\CommunicationCardinality\\aioquic & \
                  python examples/http3_client.py --ca-certs tests/pycacert.pem https://localhost:4433/10")


def run_server() -> None:
    os.system('cmd /c "cd C:\\Technion\\CommunicationCardinality\\aioquic & \
                  python examples/http3_server.py --certificate tests/ssl_cert.pem --private-key tests/ssl_key.pem"')


if __name__ == "__main__":

    # server_thread = threading.Thread(target=run_server(), daemon=True)
    # server_thread.start()

    # Number of connections is going to be thread_num * conns_per_thread.
    # Increase thread_num with care and be careful not to exceed your machine capabilities.
    # A thread_num of 10-15 should be a safe choice.
    # Make sure to have an active server before running the script.

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
