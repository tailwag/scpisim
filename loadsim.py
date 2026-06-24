import random
import socket
import threading

HOST = "0.0.0.0"
PORT = 5025

running = True

voltage = 0.0
current = 0.0
power = 0.0
input = "OFF"

def jitter(value):
    return round(value + (0.5 - random.random()) / 4, 2)

def process_command(cmd):
    global voltage
    global current
    global power
    global input

    cmd = cmd.strip()

    print(f"RX: {cmd}")

    if cmd == "*IDN?":
        return "Elekro-Automatik, EL 9080-340"

    elif cmd == "*RST":
        return None

    elif cmd == "INP OFF":
        input = "OFF"
        return None

    elif cmd == "INP ON":
        input = "ON"
        return None

    elif cmd == "MEAS:VOLT?":
        return str(jitter(voltage)) + " V"

    elif cmd == "MEAS:CURR?":
        return str(jitter(current)) + " A"

    elif cmd == "MEAS:POW?":
        return str(jitter(power)) + " W"

    elif cmd == "INP?":
        return input

    elif cmd.startswith("VOLT "):
        value = float(cmd.split()[1])
        voltage = value
        print(f"Voltage set to {value}")
        return None

    elif cmd.startswith("CURR "):
        value = float(cmd.split()[1])
        current = value
        print(f"Current set to {value}")
        return None
        
    elif cmd.startswith("POW "):
        value = float(cmd.split()[1])
        power = value
        print(f"Power set to {value}")
        return None

    else:
        return "ERROR"


def client_thread(conn, addr):
    print(f"Client connected: {addr}")

    buffer = ""

    try:
        while True:
            data = conn.recv(1024)

            if not data:
                break

            buffer += data.decode()

            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)

                print(f"line: {line}")
                response = ""

                cmds = line.split(";")

                for i, cmd in enumerate(cmds):
                    result = process_command(cmd)

                    if i > 0 and result is not None:
                        response += ";"

                    if result is not None:
                        response += result

                print(f"response: {response}")

                if response is not None and response != "":
                    conn.sendall((response + "\n").encode())

    except ConnectionResetError:
        pass

    finally:
        conn.close()
        print(f"Client disconnected: {addr}")


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()

        print(f"Listening on {HOST}:{PORT}")

        while running:
            conn, addr = s.accept()
            threading.Thread(
                target=client_thread,
                args=(conn, addr),
                daemon=True
            ).start()


if __name__ == "__main__":
    main()
