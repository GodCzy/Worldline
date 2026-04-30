# Docker Desktop Virtualization Blocker

## Goal
Restore Docker Desktop to a usable state so the repository can run `docker compose up --build`.

## Stable Findings
- Date checked: 2026-03-17
- OS: Windows 11 Home China, build 26200.8037
- CPU virtualization capability is present:
  - `VirtualizationFirmwareEnabled = True`
  - `VMMonitorModeExtensions = True`
  - `SecondLevelAddressTranslationExtensions = True`
- Windows currently reports `HypervisorPresent = False`
- Docker Desktop status is `stopped`
- Docker context is already `desktop-linux`
- Docker Desktop backend logs repeatedly report:
  - `hasNoVirtualization: true`
  - `docker: stopped`
  - `dockerAPI: stopped`
- Optional feature state observed through `Win32_OptionalFeature`:
  - `Microsoft-Windows-Subsystem-Linux = 1` (enabled)
  - `VirtualMachinePlatform = 1` (enabled)
  - `Microsoft-Hyper-V-All = 2` (disabled, acceptable on Home edition)
- `vmcompute` and `com.docker.service` are both stopped
- Starting `vmcompute` or `com.docker.service` from the current session fails because service control requires admin rights
- Docker VM logs under `C:\Users\godcz\AppData\Local\Docker\log\vm\init.log` contain historical normal engine activity from 2025-11-08, so this machine has run Docker successfully before
- Docker custom WSL storage path exists and is healthy:
  - `E:\dokcer disk\DockerDesktopWSL`
- Post-reboot recheck on 2026-03-17 still shows:
  - `HyperVisorPresent = False`
  - `docker desktop status` cannot retrieve status
  - `docker version` still returns only the client section
  - `com.docker.service` and `vmcompute` remain stopped
  - `HypervisorPlatform = 2` in `Win32_OptionalFeature` (disabled)

## Interpretation
- This is not a hardware virtualization problem.
- The most likely blocker is that the Windows hypervisor is not actually starting at boot even though firmware virtualization is enabled and WSL/VirtualMachinePlatform are installed.
- The highest-probability causes are:
  - a disabled boot setting such as `hypervisorlaunchtype`
  - the hypervisor platform component is still not enabled on the running system
  - a Windows update / Docker update left the virtualization stack in a stale state and the machine needs an admin-level repair plus reboot

## Low-Risk Facts
- Business code is not involved.
- Docker Desktop settings and context are not the primary blocker.
- The custom Docker WSL storage path is not obviously broken.

## Admin Repair Steps
Run the following in an Administrator PowerShell window:

```powershell
bcdedit /enum {current}
bcdedit /set hypervisorlaunchtype auto
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:HypervisorPlatform /all /norestart
wsl --update
```

Then fully reboot Windows.

Expected `bcdedit /enum {current}` output should include:

```text
hypervisorlaunchtype    Auto
```

## Post-Reboot Validation
Run:

```powershell
Get-ComputerInfo | Select-Object HyperVisorPresent
Get-CimInstance Win32_OptionalFeature | Where-Object { $_.Name -match 'HypervisorPlatform|VirtualMachinePlatform|Microsoft-Windows-Subsystem-Linux' } | Format-Table Name,InstallState -Auto
docker desktop status
docker version
docker compose version
```

Expected:
- `HyperVisorPresent` becomes `True`
- `HypervisorPlatform`, `VirtualMachinePlatform`, and `Microsoft-Windows-Subsystem-Linux` all show enabled
- Docker Desktop no longer shows the virtualization warning
- `docker version` returns both client and server sections

## Last-Resort Recovery
Only if the reboot and admin repair steps fail:
- Docker Desktop -> Troubleshoot -> Restart / Repair
- Docker Desktop -> Troubleshoot -> Clean / Reset to factory defaults
- Reinstall Docker Desktop
- Destructive option, only if you accept losing local Docker data:
  - `wsl --unregister docker-desktop`
  - `wsl --unregister docker-desktop-data`

## Next Step
Complete the admin repair + reboot path first, then re-check Docker engine status before touching any repository runtime commands.
