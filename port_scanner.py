# ==========================
# Python Port Scanner
# ==========================
# Author: Altoid
# Fast, clean, multi-threaded port scanner with CLI arguments, colored output, and file export.

import socket
import threading
from queue import Queue
from datetime import datetime
import argparse

# --------------------------
# Configuration
# --------------------------
THREADS = 120
TIMEOUT = 1

# --------------------------
# Colors (ANSI)
# --------------------------
class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    CYAN = "\033[96m"
    RESET = "\033[0m"

# --------------------------
# Banner
# --------------------------
def print_banner():
    print(f"""
{Colors.CYAN}
=====================================
        PORT SCANNER v1.0
=====================================
{Colors.RESET}
    """)

# --------------------------
# Scan Function
# --------------------------
def scan_port(ip, port, results):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(TIMEOUT)
        result = sock.connect_ex((ip, port))

        if result == 0:
            try:
                service = socket.getservbyport(port)
            except:
                service = "unknown"

            print(f"{Colors.GREEN}[OPEN]{Colors.RESET} Port {port} ({service})")
            results.append((port, service))

        sock.close()
    except:
        pass

# --------------------------
# Worker Thread
# --------------------------
def worker(ip, queue, results):
    while not queue.empty():
        port = queue.get()
        scan_port(ip, port, results)
        queue.task_done()

# --------------------------
# Main Scanner
# --------------------------
def port_scanner(ip, start_port, end_port):
    queue = Queue()
    results = []

    for port in range(start_port, end_port + 1):
        queue.put(port)

    threads = []
    for _ in range(THREADS):
        t = threading.Thread(target=worker, args=(ip, queue, results))
        t.daemon = True
        t.start()
        threads.append(t)

    queue.join()
    return sorted(results)

# --------------------------
# Save Results
# --------------------------
def save_results(results, filename):
    with open(filename, "w") as f:
        for port, service in results:
            f.write(f"{port},{service}\n")

# --------------------------
# Argument Parsing
# --------------------------
def parse_args():
    parser = argparse.ArgumentParser(description="Fast Python Port Scanner")
    parser.add_argument("-t", "--target", required=True, help="Target IP or domain")
    parser.add_argument("-p", "--ports", default="1-1000", help="Port range (e.g. 1-1000)")
    parser.add_argument("-o", "--output", help="Save results to file")
    return parser.parse_args()

# --------------------------
# Entry Point
# --------------------------
def main():
    print_banner()
    args = parse_args()

    try:
        ip = socket.gethostbyname(args.target)
    except socket.gaierror:
        print(f"{Colors.RED}Invalid target{Colors.RESET}")
        return

    try:
        start_port, end_port = map(int, args.ports.split("-"))
    except:
        print(f"{Colors.RED}Invalid port range{Colors.RESET}")
        return

    print(f"\nScanning {ip} ({args.target}) from {start_port} to {end_port}\n")

    start_time = datetime.now()
    results = port_scanner(ip, start_port, end_port)

    print("\n" + "-" * 40)
    print(f"Scan finished in {datetime.now() - start_time}")
    print(f"Open ports: {len(results)}")
    print("-" * 40)

    if args.output:
        save_results(results, args.output)
        print(f"Results saved to {args.output}")


if __name__ == "__main__":
    main()

