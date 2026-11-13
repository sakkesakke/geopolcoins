# Mindveto for Windows - the AI kill switch
# Copyright (c) 2026 Amghar Said. All rights reserved.
# Blocks AI services for every browser and app on this PC by adding them to the Windows hosts file.
# Only needs administrator rights. Sends nothing about you anywhere; it only downloads the public list.
$ErrorActionPreference = 'Stop'
$Hosts = "$env:SystemRoot\System32\drivers\etc\hosts"
$Start = '# >>> Human Override (do not edit this block)'
$End   = '# <<< Human Override'
$ListUrl = 'https://geopolcoins.xyz/human-override/hosts.txt'
$FamStart = '# >>> Mindveto family filter (do not edit this block)'
$FamEnd   = '# <<< Mindveto family filter'
$AdultUrl = 'https://geopolcoins.xyz/human-override/adult/hosts.txt'
$BypassUrl = 'https://geopolcoins.xyz/human-override/bypass/hosts.txt'
# SafeSearch: the search engines' own strict servers (official names). Their addresses are looked up when you switch it on.
$SafeMap = [ordered]@{
  'forcesafesearch.google.com' = @('google.com','www.google.com','www.google.be','www.google.nl','www.google.fr','www.google.de','www.google.es','www.google.it','www.google.pt','www.google.co.uk','www.google.co.ma','www.google.com.br','www.google.ca')
  'strict.bing.com'            = @('bing.com','www.bing.com')
  'safe.duckduckgo.com'        = @('duckduckgo.com','www.duckduckgo.com','start.duckduckgo.com','html.duckduckgo.com')
  'restrict.youtube.com'       = @('www.youtube.com','m.youtube.com','youtubei.googleapis.com','youtube.googleapis.com','www.youtube-nocookie.com')
}
# Official browser policies for SafeSearch (Chrome and Edge); saved first, restored exactly on switch-off
$SafePolicies = @(
  @('HKLM:\SOFTWARE\Policies\Google\Chrome', 'ForceGoogleSafeSearch', 1),
  @('HKLM:\SOFTWARE\Policies\Google\Chrome', 'ForceYouTubeRestrict', 2),
  @('HKLM:\SOFTWARE\Policies\Microsoft\Edge', 'ForceGoogleSafeSearch', 1),
  @('HKLM:\SOFTWARE\Policies\Microsoft\Edge', 'ForceYouTubeRestrict', 2),
  @('HKLM:\SOFTWARE\Policies\Microsoft\Edge', 'ForceBingSafeSearch', 2),
  # anti-bypass: switch off "secure DNS" (DNS-over-HTTPS) in the browsers, so the hosts block cannot be skipped
  @('HKLM:\SOFTWARE\Policies\Google\Chrome', 'DnsOverHttpsMode', 'off'),
  @('HKLM:\SOFTWARE\Policies\Microsoft\Edge', 'DnsOverHttpsMode', 'off'),
  @('HKLM:\SOFTWARE\Policies\Mozilla\Firefox\DNSOverHTTPS', 'Enabled', 0),
  @('HKLM:\SOFTWARE\Policies\Mozilla\Firefox\DNSOverHTTPS', 'Locked', 1)
)

function Test-Admin { ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator) }
if (-not (Test-Admin)) {
  Start-Process powershell.exe -Verb RunAs -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`""
  exit
}

function Remove-Block([string]$text, [string]$s = $Start, [string]$e = $End) {
  $pattern = [regex]::Escape($s) + '[\s\S]*?' + [regex]::Escape($e) + '\r?\n?'
  return [regex]::Replace($text, $pattern, '')
}

function Get-AdultList {
  try { $raw = (Invoke-WebRequest -Uri $AdultUrl -UseBasicParsing -TimeoutSec 60).Content }
  catch {
    $local = Join-Path $PSScriptRoot 'adult-hosts.txt'
    if (Test-Path $local) { $raw = Get-Content $local -Raw } else { throw 'Could not download the family filter list and no local adult-hosts.txt found.' }
  }
  $lines = $raw -split "`n" | ForEach-Object { $_.Trim() } | Where-Object { $_ -match '^0\.0\.0\.0 ([a-z0-9-]{1,63}\.)+[a-z]{2,24}$' }
  if ($lines.Count -lt 1000) { throw 'The family filter list looks wrong. Nothing was changed.' }
  return $lines
}

function Get-BypassList {
  try { $raw = (Invoke-WebRequest -Uri $BypassUrl -UseBasicParsing -TimeoutSec 30).Content }
  catch { $local = Join-Path $PSScriptRoot 'bypass-hosts.txt'; if (Test-Path $local) { $raw = Get-Content $local -Raw } else { return @() } }
  $lines = $raw -split "`n" | ForEach-Object { $_.Trim() } | Where-Object { $_ -match '^0\.0\.0\.0 ([a-z0-9-]{1,63}\.)+[a-z]{2,24}$' }
  if ($lines.Count -lt 20) { return @() }
  return $lines
}

function Get-SafeLines {
  $out = @()
  foreach ($target in $SafeMap.Keys) {
    $ip = $null
    try { $ip = (Resolve-DnsName -Name $target -Type A -ErrorAction Stop | Where-Object { $_.Type -eq 'A' } | Select-Object -First 1).IPAddress } catch { }
    if ($ip -and $ip -match '^\d{1,3}(\.\d{1,3}){3}$') { foreach ($n in $SafeMap[$target]) { $out += "$ip $n" } }
  }
  return $out
}

function Set-Policies($list, [string]$backupName) {
  $saved = @()
  if (Test-Path $BackupKey) { $old = (Get-ItemProperty $BackupKey -ErrorAction SilentlyContinue).$backupName; if ($old) { $saved = @($old | ConvertFrom-Json) } }
  foreach ($p in $list) {
    $key, $name, $val = $p
    if (-not ($saved | Where-Object { $_.k -eq $key -and $_.n -eq $name })) {
      $prev = $null
      if (Test-Path $key) { $prev = (Get-ItemProperty $key -Name $name -ErrorAction SilentlyContinue).$name }
      $saved += [pscustomobject]@{ k = $key; n = $name; v = $prev; s = ($prev -is [string]) }
    }
    if (-not (Test-Path $key)) { New-Item -Path $key -Force | Out-Null }
    $type = if ($val -is [string]) { 'String' } else { 'DWord' }
    New-ItemProperty -Path $key -Name $name -Value $val -PropertyType $type -Force | Out-Null
  }
  if (-not (Test-Path $BackupKey)) { New-Item -Path $BackupKey -Force | Out-Null }
  New-ItemProperty -Path $BackupKey -Name $backupName -Value ($saved | ConvertTo-Json -Compress) -PropertyType String -Force | Out-Null
}

function Restore-Policies([string]$backupName) {
  if (-not (Test-Path $BackupKey)) { return 0 }
  $raw = (Get-ItemProperty $BackupKey -ErrorAction SilentlyContinue).$backupName
  if (-not $raw) { return 0 }
  $n = 0
  foreach ($e in @($raw | ConvertFrom-Json)) {
    if (-not (Test-Path $e.k)) { continue }
    if ($null -eq $e.v) { Remove-ItemProperty -Path $e.k -Name $e.n -ErrorAction SilentlyContinue }
    elseif ($e.s) { New-ItemProperty -Path $e.k -Name $e.n -Value ([string]$e.v) -PropertyType String -Force | Out-Null }
    else { New-ItemProperty -Path $e.k -Name $e.n -Value ([int]$e.v) -PropertyType DWord -Force | Out-Null }
    $n++
  }
  Remove-ItemProperty -Path $BackupKey -Name $backupName -ErrorAction SilentlyContinue
  return $n
}

function Get-List {
  try {
    $raw = (Invoke-WebRequest -Uri $ListUrl -UseBasicParsing -TimeoutSec 20).Content
  } catch {
    $local = Join-Path $PSScriptRoot 'hosts.txt'
    if (Test-Path $local) { $raw = Get-Content $local -Raw } else { throw 'Could not download the list and no local hosts.txt found.' }
  }
  # accept only safe lines: "0.0.0.0 domain"
  $lines = $raw -split "`n" | ForEach-Object { $_.Trim() } | Where-Object { $_ -match '^0\.0\.0\.0 ([a-z0-9-]{1,63}\.)+[a-z]{2,24}$' }
  if ($lines.Count -lt 20) { throw 'The downloaded list looks wrong. Nothing was changed.' }
  return $lines
}

# Windows' own AI features, switched off with official policies (Microsoft Policy CSP WindowsAI,
# Microsoft Edge and Google Chrome enterprise policies). The previous values are saved first,
# so option 4 restores exactly what was there before (an IT admin's own settings stay intact).
$AiPolicies = @(
  @('HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsCopilot', 'TurnOffWindowsCopilot', 1),
  @('HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsAI', 'AllowRecallEnablement', 0),
  @('HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsAI', 'DisableAIDataAnalysis', 1),
  @('HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsAI', 'DisableClickToDo', 1),
  @('HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsAI', 'DisableSettingsAgent', 1),
  @('HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Paint', 'DisableCocreator', 1),
  @('HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Paint', 'DisableGenerativeFill', 1),
  @('HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Paint', 'DisableImageCreator', 1),
  @('HKLM:\SOFTWARE\Policies\Microsoft\Edge', 'HubsSidebarEnabled', 0),
  @('HKLM:\SOFTWARE\Policies\Microsoft\Edge', 'Microsoft365CopilotChatIconEnabled', 0),
  @('HKLM:\SOFTWARE\Policies\Microsoft\Edge', 'ComposeInlineEnabled', 0),
  @('HKLM:\SOFTWARE\Policies\Microsoft\Edge', 'GenAILocalFoundationalModelSettings', 1),
  @('HKLM:\SOFTWARE\Policies\Google\Chrome', 'GeminiSettings', 1),
  @('HKLM:\SOFTWARE\Policies\Google\Chrome', 'AIModeSettings', 1),
  @('HKLM:\SOFTWARE\Policies\Google\Chrome', 'HelpMeWriteSettings', 2),
  @('HKLM:\SOFTWARE\Policies\Google\Chrome', 'TabCompareSettings', 2),
  @('HKLM:\SOFTWARE\Policies\Google\Chrome', 'HistorySearchSettings', 2),
  @('HKLM:\SOFTWARE\Policies\Google\Chrome', 'CreateThemesSettings', 2),
  @('HKLM:\SOFTWARE\Policies\Google\Chrome', 'DevToolsGenAiSettings', 2),
  @('HKLM:\SOFTWARE\Policies\Google\Chrome', 'GenAILocalFoundationalModelSettings', 1)
)
$BackupKey = 'HKLM:\SOFTWARE\HumanOverride'

function Disable-BuiltinAI {
  $saved = @()
  if (Test-Path $BackupKey) { $old = (Get-ItemProperty $BackupKey -ErrorAction SilentlyContinue).BuiltinAIBackup; if ($old) { $saved = @($old | ConvertFrom-Json) } }
  foreach ($p in $AiPolicies) {
    $key, $name, $val = $p
    $already = $saved | Where-Object { $_.k -eq $key -and $_.n -eq $name }
    if (-not $already) {   # remember the value from BEFORE Mindveto (only the first time)
      $prev = $null
      if (Test-Path $key) { $prev = (Get-ItemProperty $key -Name $name -ErrorAction SilentlyContinue).$name }
      $saved += [pscustomobject]@{ k = $key; n = $name; v = $prev; s = ($prev -is [string]) }
    }
    if (-not (Test-Path $key)) { New-Item -Path $key -Force | Out-Null }
    $type = if ($val -is [string]) { 'String' } else { 'DWord' }
    New-ItemProperty -Path $key -Name $name -Value $val -PropertyType $type -Force | Out-Null
  }
  if (-not (Test-Path $BackupKey)) { New-Item -Path $BackupKey -Force | Out-Null }
  New-ItemProperty -Path $BackupKey -Name 'BuiltinAIBackup' -Value ($saved | ConvertTo-Json -Compress) -PropertyType String -Force | Out-Null
  return $AiPolicies.Count
}

function Restore-BuiltinAI {
  if (-not (Test-Path $BackupKey)) { return 0 }
  $raw = (Get-ItemProperty $BackupKey -ErrorAction SilentlyContinue).BuiltinAIBackup
  if (-not $raw) { return 0 }
  $n = 0
  foreach ($e in @($raw | ConvertFrom-Json)) {
    if (-not (Test-Path $e.k)) { continue }
    if ($null -eq $e.v) { Remove-ItemProperty -Path $e.k -Name $e.n -ErrorAction SilentlyContinue }
    elseif ($e.s) { New-ItemProperty -Path $e.k -Name $e.n -Value ([string]$e.v) -PropertyType String -Force | Out-Null }
    else { New-ItemProperty -Path $e.k -Name $e.n -Value ([int]$e.v) -PropertyType DWord -Force | Out-Null }
    $n++
  }
  Remove-ItemProperty -Path $BackupKey -Name 'BuiltinAIBackup' -ErrorAction SilentlyContinue
  return $n
}

Clear-Host
Write-Host ''
Write-Host '  MINDVETO  -  the AI kill switch' -ForegroundColor Red
Write-Host '  (c) 2026 Amghar Said  ·  mindveto.app'
Write-Host ''
Write-Host '  Terms: Mindveto is provided "as is". It cannot guarantee that every AI is blocked.'
Write-Host '  To the maximum extent permitted by law, Amghar Said is not liable for any damage or'
Write-Host '  consequence of using it. Full terms: https://mindveto.app/terms/'
$agree = Read-Host '  Type Y to agree and continue'
if ($agree -notmatch '^[YyJj]') { Write-Host '  Nothing was changed.'; Read-Host '  Press Enter to close'; exit }
Write-Host ''
Write-Host '  1) Block AI on this PC (or update the list)'
Write-Host '  2) Allow AI again (remove the block)'
Write-Host '  3) Turn off the AI built into Windows, Edge and Chrome (Copilot, Recall, Click to Do, Paint AI, Gemini)'
Write-Host '  4) Turn that built-in AI back on (restores the settings from before)'
Write-Host '  5) Family filter ON: block adult sites (18+), force SafeSearch, block VPN/proxy sites and secure DNS'
Write-Host '  6) Family filter OFF'
Write-Host '  7) Quit'
$c = Read-Host '  Choose 1, 2, 3, 4, 5, 6 or 7'
$current = Get-Content $Hosts -Raw -ErrorAction SilentlyContinue
if ($null -eq $current) { $current = '' }
if ($c -eq '1') {
  $lines = Get-List
  Copy-Item $Hosts "$Hosts.human-override-backup" -Force
  $clean = (Remove-Block $current).TrimEnd()
  $block = @($Start) + $lines + @($End)
  Set-Content -Path $Hosts -Value ($clean + "`r`n`r`n" + ($block -join "`r`n") + "`r`n") -Encoding ASCII
  ipconfig /flushdns | Out-Null
  Write-Host ''
  Write-Host ("  Done: {0} AI addresses are blocked on this PC. Restart your browser." -f $lines.Count) -ForegroundColor Green
  Write-Host '  Tip: give children a normal (non-admin) Windows account, then they cannot undo it.'
} elseif ($c -eq '2') {
  Set-Content -Path $Hosts -Value ((Remove-Block $current).TrimEnd() + "`r`n") -Encoding ASCII
  ipconfig /flushdns | Out-Null
  Write-Host ''
  Write-Host '  AI is allowed again on this PC.' -ForegroundColor Yellow
} elseif ($c -eq '3') {
  $n = Disable-BuiltinAI
  Write-Host ''
  Write-Host ("  Done: {0} built-in AI settings are switched off. Restart Edge and Chrome; sign out and in again for Windows." -f $n) -ForegroundColor Green
  Write-Host '  Note: Edge and Chrome may show "Managed by your organisation". That is normal: it means these settings are locked.'
} elseif ($c -eq '4') {
  $n = Restore-BuiltinAI
  Write-Host ''
  if ($n -gt 0) { Write-Host ("  Built-in AI settings restored ({0})." -f $n) -ForegroundColor Yellow } else { Write-Host '  Nothing to restore.' }
} elseif ($c -eq '5') {
  Write-Host '  Downloading the family filter list (about 2 MB)...'
  $adult = Get-AdultList
  $safe = Get-SafeLines
  $bypass = Get-BypassList
  Copy-Item $Hosts "$Hosts.human-override-backup" -Force
  $clean = (Remove-Block $current $FamStart $FamEnd).TrimEnd()
  $block = @($FamStart) + $safe + $adult + $bypass + @($FamEnd)
  Set-Content -Path $Hosts -Value ($clean + "`r`n`r`n" + ($block -join "`r`n") + "`r`n") -Encoding ASCII
  Set-Policies $SafePolicies 'SafeSearchBackup'
  ipconfig /flushdns | Out-Null
  Write-Host ''
  Write-Host ("  Done: {0} adult addresses blocked and SafeSearch forced in Chrome and Edge. Restart your browser." -f $adult.Count) -ForegroundColor Green
  Write-Host ("  Anti-bypass: {0} VPN, proxy and secure-DNS addresses blocked; secure DNS switched off in Chrome, Edge and Firefox." -f ($bypass.Count / 2))
  if ($safe.Count -eq 0) { Write-Host '  SafeSearch for other browsers could not be set (no internet?). Choose 5 again later.' -ForegroundColor Yellow }
  Write-Host '  If opening websites becomes slow on this PC, choose 6 and use the Mindveto browser extension instead.'
} elseif ($c -eq '6') {
  Set-Content -Path $Hosts -Value ((Remove-Block $current $FamStart $FamEnd).TrimEnd() + "`r`n") -Encoding ASCII
  $n = Restore-Policies 'SafeSearchBackup'
  ipconfig /flushdns | Out-Null
  Write-Host ''
  Write-Host '  Family filter switched off on this PC.' -ForegroundColor Yellow
}
Write-Host ''
Read-Host '  Press Enter to close'
