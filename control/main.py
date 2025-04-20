import network
import socket

SSID = "POCOkopec"
PASSWORD = "12345679"
VEDLEJSI_IP = "192.168.63.145"

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    while not wlan.isconnected():
        pass
    ip = wlan.ifconfig()[0]
    print("Connected! IP:", ip)
    print("Web běží na: http://{}".format(ip))
    return ip

def send_command(command):
    addr = (VEDLEJSI_IP, 80)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    response = ""
    try:
        s.connect(addr)
        s.send(command.encode())
        response = s.recv(1024).decode().strip()
    except Exception as e:
        print("Chyba:", e)
    finally:
        s.close()
    return response

# Webový server
def start_web():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("0.0.0.0", 80))
    s.listen(5)
    stav = "INIT"

    while True:
        conn, addr = s.accept()
        request = conn.recv(1024).decode()

        if "GET /LEFT" in request:
            resp = send_command("LEFT")
            if resp == "LEFT TRUE":
                stav = "LEFT"
        elif "GET /RIGHT" in request:
            resp = send_command("RIGHT")
            if resp == "RIGHT TRUE":
                stav = "RIGHT"

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
<head>
    <title>Motor Control</title>
</head>
<body>
    <h1>Motor Control</h1>
    <a href="/LEFT" style="{left_style}padding:10px 20px;border-radius:8px;text-decoration:none;display:inline-block;">LEFT</a>
    <a href="/RIGHT" style="{right_style}padding:10px 20px;border-radius:8px;text-decoration:none;display:inline-block;">RIGHT</a>
</body>
</html>
""".format(left_style=left_color, right_style=right_color)


        conn.send(response)
        conn.close()

ip_address = connect_wifi()
start_web()

