# Ninja Unauthenticated Arbitrary File Write RCE

Ninja C2 is vulnerable to unauthenticated arbitrary file write. This can immediately be used to gain RCE against the Teamserver if running as root, if not RCE can be gained next time a C2 operator restarts the C2 server.

The vulnerability is reminiscent of the [Skywalker](https://github.com/rapid7/metasploit-framework/blob/master/modules/exploits/linux/http/empire_skywalker.rb) vulnerability against Empire C2 from 2016.  

![](poc.gif)


## Reproduction

The vulnerability is in the [download route](https://github.com/ahmedkhlief/Ninja/blob/master/core/webserver.py#L321) of the public-facing C2 webserver, which does not check for filepath traversal from a `filename` provided by a connected C2 agent.

First, a malicious agent needs to register with the C2 server at the [info route](https://github.com/ahmedkhlief/Ninja/blob/master/core/webserver.py#L179). The C2 webserver obfuscates itself by randomizing the URL paths of each endpoint from the following [list](https://github.com/ahmedkhlief/Ninja/blob/master/utils/links.txt), so we try each path until one returns an AES encryption key.

Next we encrypt the target file, specify a path traversal sequence to overwrite an arbitrary filepath on the server, and try URL paths again until hitting the download endpoint. 

The `ninja_poc.py` script automates these steps. The example endpoint assumes the server is running as root and uses the same exploit as the Skywalker vulnerability which writes a Python reverse shell to `/etc/cron.d`. If not running as root, an alternative would be to overwrite a server source file and wait until the server is restarted.