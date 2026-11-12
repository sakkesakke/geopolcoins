# Mindveto for Windows - the AI kill switch
# Copyright (c) 2026 Amghar Said. All rights reserved.
# Blocks AI services for every browser and app on this PC by adding them to the Windows hosts file.
# Only needs administrator rights. Sends nothing about you anywhere; it only downloads the public list.
$ErrorActionPreference = 'Stop'
$Hosts = "$env:SystemRoot\System32\drivers\etc\hosts"
$Start = '# >>> Human Override (do not edit this block)'
$End   = '# <<< Human Override'
$ListUrl = 'https://geopolcoins.xyz/human-override/hosts.txt'

function Test-Admin { ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator) }
if (-not (Test-Admin)) {
  Start-Process powershell.exe -Verb RunAs -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`""
  exit
}

function Remove-Block([string]$text) {
  $pattern = [regex]::Escape($Start) + '[\s\S]*?' + [regex]::Escape($End) + '\r?\n?'
  return [regex]::Replace($text, $pattern, '')
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
      $saved += [pscustomobject]@{ k = $key; n = $name; v = $prev }
    }
    if (-not (Test-Path $key)) { New-Item -Path $key -Force | Out-Null }
    New-ItemProperty -Path $key -Name $name -Value $val -PropertyType DWord -Force | Out-Null
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
Write-Host '  5) Quit'
$c = Read-Host '  Choose 1, 2, 3, 4 or 5'
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
}
Write-Host ''
Read-Host '  Press Enter to close'
