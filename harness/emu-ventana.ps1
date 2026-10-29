# Native window channel used by the original harness. No focus or SendInput.
if (-not ('EmuBanco' -as [type])) {
    Add-Type -AssemblyName System.Drawing
    Add-Type -ReferencedAssemblies System.Drawing -TypeDefinition @'
using System;
using System.Text;
using System.Drawing;
using System.Collections.Generic;
using System.Runtime.InteropServices;
public static class EmuBanco {
    private delegate bool Callback(IntPtr h, IntPtr l);
    [DllImport("user32.dll")] static extern bool EnumWindows(Callback c, IntPtr l);
    [DllImport("user32.dll")] static extern uint GetWindowThreadProcessId(IntPtr h, out uint p);
    [DllImport("user32.dll", CharSet=CharSet.Unicode)] static extern int GetWindowText(IntPtr h, StringBuilder b, int n);
    [DllImport("user32.dll")] static extern bool IsWindowVisible(IntPtr h);
    [DllImport("user32.dll")] static extern bool PostMessage(IntPtr h, uint m, IntPtr w, IntPtr l);
    [DllImport("user32.dll")] static extern bool ShowWindow(IntPtr h, int cmd);
    public static void ShowWithoutFocus(IntPtr h) { ShowWindow(h,4); }
    [DllImport("user32.dll")] static extern bool PrintWindow(IntPtr h, IntPtr d, uint f);
    [DllImport("user32.dll")] static extern bool GetClientRect(IntPtr h, out Rect r);
    [StructLayout(LayoutKind.Sequential)] struct Rect { public int L,T,R,B; }
    public static string[] Titles(uint pid) {
        var rows=new List<string>();EnumWindows((h,l)=>{uint p;GetWindowThreadProcessId(h,out p);
        if(p==pid){var b=new StringBuilder(1024);GetWindowText(h,b,1024);rows.Add(h+" visible="+IsWindowVisible(h)+" "+b);}return true;},IntPtr.Zero);return rows.ToArray();
    }
    public static IntPtr Window(uint pid) {
        var found = new List<IntPtr>();
        var hidden = new List<IntPtr>();
        EnumWindows((h,l)=>{uint p;GetWindowThreadProcessId(h,out p);
            if(p==pid) {var b=new StringBuilder(1024);GetWindowText(h,b,1024);
                string t=b.ToString();if(t.EndsWith(".E49",StringComparison.OrdinalIgnoreCase) || t.EndsWith(".E48",StringComparison.OrdinalIgnoreCase)) { if(IsWindowVisible(h))found.Add(h);else hidden.Add(h); }}
            return true;},IntPtr.Zero);
        if(found.Count==0)found=hidden;
        if(found.Count!=1)throw new InvalidOperationException("Expected one loaded emulator window; found "+found.Count);
        return found[0];
    }
    public static void Key(IntPtr h,int vk) {
        if(h==IntPtr.Zero)throw new ArgumentException("Null emulator handle");
        if(!PostMessage(h,0x100,(IntPtr)vk,IntPtr.Zero))throw new InvalidOperationException("Key down failed");
        System.Threading.Thread.Sleep(90);
        if(!PostMessage(h,0x101,(IntPtr)vk,IntPtr.Zero))throw new InvalidOperationException("Key up failed");
        System.Threading.Thread.Sleep(120);
    }
    public static void Capture(IntPtr h,string path) {
        Rect r;if(!GetClientRect(h,out r) || r.R<=0 || r.B<=0)throw new InvalidOperationException("No client rectangle");
        using(var b=new Bitmap(r.R,r.B)) {
            using(var g=Graphics.FromImage(b)) {IntPtr dc=g.GetHdc();bool ok=PrintWindow(h,dc,1);g.ReleaseHdc(dc);
                if(!ok)throw new InvalidOperationException("PrintWindow failed");}
            b.Save(path,System.Drawing.Imaging.ImageFormat.Png);
        }
    }
}
'@
}
