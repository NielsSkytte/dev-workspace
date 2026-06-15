<#
.SYNOPSIS
  Open an HTML email body as an editable Outlook draft (formatting intact, ready to send).
.DESCRIPTION
  Uses classic Outlook desktop via COM. Creates a mail item, sets the HTML body / subject /
  recipients, and Display()s it — an editable compose window, NOT sent. No security prompt is
  triggered (that only happens on .Send() or address-book access).
  Requires classic Outlook (desktop). The "new Outlook" app does not expose COM — use the
  VS Code Live Preview fallback there.
.EXAMPLE
  open-in-outlook.ps1 -HtmlPath "emails\02-x.html" -Subject "My subject"
#>
param(
  [Parameter(Mandatory = $true)][string]$HtmlPath,
  [string]$Subject = "",
  [string]$To = "",
  [string]$Cc = ""
)
$ErrorActionPreference = 'Stop'
if (-not (Test-Path -LiteralPath $HtmlPath)) { throw "HTML not found: $HtmlPath" }
$html = Get-Content -LiteralPath $HtmlPath -Raw -Encoding UTF8

try {
  $ol = New-Object -ComObject Outlook.Application
} catch {
  throw "Could not start Outlook via COM. This needs classic Outlook desktop (the 'new Outlook' app has no COM). Fall back to the VS Code Live Preview workflow. Original error: $($_.Exception.Message)"
}

$mail = $ol.CreateItem(0)            # 0 = olMailItem
if ($Subject) { $mail.Subject = $Subject }
if ($To)      { $mail.To = $To }
if ($Cc)      { $mail.CC = $Cc }
$mail.HTMLBody = $html
$mail.Display()                      # editable draft, not sent

"Outlook draft opened$(if ($Subject) { ": $Subject" })."
