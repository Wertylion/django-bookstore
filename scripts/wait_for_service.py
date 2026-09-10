import socket
import sys
import time


host = sys.argv[1]
port = int(sys.argv[2])
name = sys.argv[3] if len(sys.argv) > 3 else f'{host}:{port}'

for attempt in range(1, 31):
    try:
        with socket.create_connection((host, port), timeout=2):
            print(f'{name} is available')
            break
    except OSError:
        print(f'Waiting for {name} ({attempt}/30)...')
        time.sleep(1)
else:
    raise SystemExit(f'{name} is not available')
