import network
import socket
import machine
import time

SSID = "POCOkopec"
PASSWORD = "12345679"

led = machine.Pin(2, machine.Pin.OUT)

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    while not wlan.isconnected():
        time.sleep(0.1)
    ip, netmask, gateway, dns = wlan.ifconfig()
    print("Connected! IP:", ip)
    return ip, gateway

def send_command(command, ip):
    addr = (ip, 80)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    response = ""
    try:
        s.connect(addr)
        s.settimeout(5)
        s.send(command.encode())
        response = s.recv(1024).decode().strip()
        print("Odpověď od {}: {}".format(ip, response))
    except Exception as e:
        print("Chyba při komunikaci s {}: {}".format(ip, e))
    finally:
        s.close()
    return response

def blink(times):
    for _ in range(times):
        led.value(0)
        time.sleep(0.2)
        led.value(1)
        time.sleep(0.2)

def start_web_and_listen():
    web_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    web_socket.bind(("0.0.0.0", 80))
    web_socket.listen(5)
    web_socket.settimeout(0.1)

    msg_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    msg_socket.bind(("0.0.0.0", 81))
    msg_socket.listen(1)
    msg_socket.settimeout(0.1)

    stav = "INIT"

    while True:
        # Web server
        try:
            conn, addr = web_socket.accept()
            request = conn.recv(1024).decode()

            if "GET /LEFT" in request:
                resp = send_command("LEFT", ESP1_IP)
                if resp == "LEFT TRUE":
                    stav = "LEFT"
            elif "GET /RIGHT" in request:
                resp = send_command("RIGHT", ESP1_IP)
                if resp == "RIGHT TRUE":
                    stav = "RIGHT"
            elif "GET /ON" in request:
                send_command("ON", ESP2_IP)
            elif "GET /OFF" in request:
                send_command("OFF", ESP2_IP)

            if stav == "LEFT":
                left_color = "background-color:red;color:white;"
                right_color = "background-color:green;color:white;"
            elif stav == "RIGHT":
                left_color = "background-color:green;color:white;"
                right_color = "background-color:red;color:white;"
            else:
                left_color = right_color = ""

            response = """\
HTTP/1.1 200 OK
Content-Type: text/html

<!DOCTYPE html>
<html>
<head><title>ESP Ovládání</title></head>
<body>
    <h1>ESP 1 - Smer</h1>
    <a href="/LEFT" style="{left_style}padding:10px 20px;border-radius:8px;text-decoration:none;">LEFT</a>
    <a href="/RIGHT" style="{right_style}padding:10px 20px;border-radius:8px;text-decoration:none;">RIGHT</a>

    <h1>ESP 2 - Vlak</h1>
    <a href="/ON" style="padding:10px 20px;background-color:blue;color:white;border-radius:8px;text-decoration:none;">Zapnout</a>
    <a href="/OFF" style="padding:10px 20px;background-color:gray;color:white;border-radius:8px;text-decoration:none;">Vypnout</a>
    
    <h1>ESP 3 - Vyhybky</h1>
    <a href="/UP" style="padding:10px 20px;background-color:green;color:white;border-radius:8px;text-decoration:none;">Nahoru</a>
    <a href="/DOWN" style="padding:10px 20px;background-color:red;color:white;border-radius:8px;text-decoration:none;">Dolu</a>
</body>
</html>
""".format(left_style=left_color, right_style=right_color)

            conn.sendall(response.encode())
            conn.close()

        except Exception:
            pass  

        try:
            conn, addr = msg_socket.accept()
            message = conn.recv(1024).decode().strip()
            print("Přijatá zpráva:", message)

            if message == "SWE":
                blink(5)
                resp = send_command("RIGHT", ESP1_IP)
                if resp == "RIGHT TRUE":
                    stav = "RIGHT"
                conn.send(b"SWE OK")
            elif message == "SWS":
                blink(10)
                resp = send_command("LEFT", ESP1_IP)
                if resp == "LEFT TRUE":
                    stav = "LEFT"
                conn.send(b"SWS OK")
            else:
                conn.send(b"UNKNOWN")
            conn.close()
        except Exception:
            pass  

ip_address, gateway = connect_wifi()
subnet_prefix = ".".join(gateway.split(".")[:3])
ESP1_IP = f"{subnet_prefix}.145"
ESP2_IP = f"{subnet_prefix}.228"
ESP3_IP = f"{subnet_prefix}.16"

print("ESP1_IP:", ESP1_IP)
print("ESP2_IP:", ESP2_IP)
print("ESP3_IP:", ESP3_IP)
print("Web http://{}/".format(ip_address))
start_web_and_listen()

