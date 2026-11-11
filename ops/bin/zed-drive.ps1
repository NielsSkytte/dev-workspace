# Drives the Zed window for self-tests: optional click (window-relative), SendKeys
# sequence separated by |, then a screenshot of the window to -Out.
# Keys go to whatever pane has focus: click a non-terminal spot first.
param([string]$Keys = '', [string]$Out = (Join-Path $env:TEMP 'zed-shot.png'), [int]$ClickX = 0, [int]$ClickY = 0)
Add-Type -AssemblyName System.Windows.Forms, System.Drawing
Add-Type @"
using System; using System.Runtime.InteropServices;
public class W { [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
[DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
[DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
[DllImport("user32.dll")] public static extern void mouse_event(int f, int x, int y, int d, int e);
public struct RECT { public int L, T, R, B; } }
"@
$p = Get-Process zed | Where-Object { $_.MainWindowHandle -ne 0 } | Select-Object -First 1
[W]::SetForegroundWindow($p.MainWindowHandle) | Out-Null
Start-Sleep -Milliseconds 500
# Guard: Windows may refuse to bring Zed forward; never send input to another window.
if ([W]::GetForegroundWindow() -ne $p.MainWindowHandle) { 'ABORT: Zed is not the foreground window, no input sent'; exit 1 }
if ($ClickX) {
    $r0 = New-Object W+RECT; [W]::GetWindowRect($p.MainWindowHandle, [ref]$r0) | Out-Null
    [System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point ($r0.L + $ClickX), ($r0.T + $ClickY)
    [W]::mouse_event(2, 0, 0, 0, 0); [W]::mouse_event(4, 0, 0, 0, 0); Start-Sleep -Milliseconds 800
}
foreach ($k in ($Keys -split '\|')) { if ($k) { if ([W]::GetForegroundWindow() -ne $p.MainWindowHandle) { 'ABORT: focus left Zed'; exit 1 }; [System.Windows.Forms.SendKeys]::SendWait($k); Start-Sleep -Milliseconds 1500 } }
Start-Sleep -Seconds 2
$r = New-Object W+RECT; [W]::GetWindowRect($p.MainWindowHandle, [ref]$r) | Out-Null
$bmp = New-Object System.Drawing.Bitmap ($r.R - $r.L), ($r.B - $r.T)
$g = [System.Drawing.Graphics]::FromImage($bmp); $g.CopyFromScreen($r.L, $r.T, 0, 0, $bmp.Size)
$bmp.Save($Out); "saved $($p.MainWindowTitle)"
