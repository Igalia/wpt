import json

### From https://searchfox.org/mozilla-central/source/accessible/tests/browser/windows/a11y_setup.py
import ctypes
import os
from ctypes import POINTER, byref
from ctypes.wintypes import BOOL, HWND, LPARAM, POINT
#from dataclasses import dataclass

#import comtypes.automation
import comtypes.client
import psutil
from comtypes import COMError, IServiceProvider

#CHILDID_SELF = 0
#COWAIT_DEFAULT = 0
#EVENT_OBJECT_FOCUS = 0x8005
#GA_ROOT = 2
NAVRELATION_EMBEDS = 0x1009
OBJID_CLIENT = -4
#RPC_S_CALLPENDING = -2147417835
#WINEVENT_OUTOFCONTEXT = 0
#WM_CLOSE = 0x0010

user32 = ctypes.windll.user32
oleacc = ctypes.oledll.oleacc
oleaccMod = comtypes.client.GetModule("oleacc.dll")
IAccessible = oleaccMod.IAccessible
del oleaccMod


ia2Tlb = os.path.join(
    os.getcwd(),
    "ia2",
    "IA2Typelib.tlb",
)
if not os.path.isfile(ia2Tlb):
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

ia2Mod = comtypes.client.GetModule(ia2Tlb)
del ia2Tlb

print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ia2Mod")
print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ia2Mod")

### This was done by Firefox:
# Shove all the IAccessible* interfaces and IA2_* constants directly
# into our namespace for convenience.
globals().update((k, getattr(ia2Mod, k)) for k in ia2Mod.__all__)

for k in ia2Mod.__all__:
    print(k)

# We use this below. The linter doesn't understand our globals() update hack.
IAccessible2 = ia2Mod.IAccessible2 ## Maybe we can remove this because we don't have the same linter?
del ia2Mod

# uiaMod = comtypes.client.GetModule("UIAutomationCore.dll")
# globals().update((k, getattr(uiaMod, k)) for k in uiaMod.__all__)
# uiaClient = comtypes.CoCreateInstance(
#     uiaMod.CUIAutomation._reg_clsid_,
#     interface=uiaMod.IUIAutomation,
#     clsctx=comtypes.CLSCTX_INPROC_SERVER,
# )


def AccessibleObjectFromWindow(hwnd, objectID=OBJID_CLIENT):
    p = POINTER(IAccessible)()
    oleacc.AccessibleObjectFromWindow(
        hwnd, objectID, byref(IAccessible._iid_), byref(p)
    )
    return p


def getWindowClass(hwnd):
    MAX_CHARS = 257
    buffer = ctypes.create_unicode_buffer(MAX_CHARS)
    user32.GetClassNameW(hwnd, buffer, MAX_CHARS)
    return buffer.value


def getBrowserHwnd(platform):
    """Search all top level windows for the Firefox instance being
    tested.
    We search by window class name and window title prefix.
    """
    # We can compare the grandparent process ids to find the Firefox started by
    # the test harness.
    commonPid = psutil.Process().parent().ppid()
    # We need something mutable to store the result from the callback.
    found = []

    @ctypes.WINFUNCTYPE(BOOL, HWND, LPARAM)
    def callback(hwnd, lParam):
        if getWindowClass(hwnd) != "MozillaWindowClass":
            return True
        pid = ctypes.wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, byref(pid))
        if psutil.Process(pid.value).parent().ppid() != commonPid:
            return True  # Not the Firefox being tested.
        found.append(hwnd)
        return False

    user32.EnumWindows(callback, LPARAM(0))
    if not found:
        raise LookupError("Couldn't find browser HWND")
    return found[0]


def toIa2(obj):
    serv = obj.QueryInterface(IServiceProvider)
    return serv.QueryService(IAccessible2._iid_, IAccessible2)


def getDocIa2():
    """Get the IAccessible2 for the document being tested."""
    hwnd = getFirefoxHwnd()
    root = AccessibleObjectFromWindow(hwnd)
    doc = root.accNavigate(NAVRELATION_EMBEDS, 0)
    try:
        child = toIa2(doc.accChild(1))
        if "id:default-iframe-id;" in child.attributes:
            # This is an iframe or remoteIframe test.
            doc = child.accChild(1)
    except COMError:
        pass  # No child.
    return toIa2(doc)


def findIa2ByDomId(root, id):
    search = f"id:{id};"
    # Child ids begin at 1.
    for i in range(1, root.accChildCount + 1):
        child = toIa2(root.accChild(i))
        if search in child.attributes:
            return child
        descendant = findIa2ByDomId(child, id)
        if descendant:
            return descendant

def find_browser(product_name):
    return None

class WindowsAccessibilityExecutorImpl:
    def setup(self, product_name):
        self.product_name = product_name
        self.root = find_browser(self.product_name)

        #if not self.root:
        #    raise Exception(f"Couldn't find application: {product_name}")


    def get_accessibility_api_node(self, dom_id):
        #tab = find_active_tab(self.root)
        #node = find_node(tab, "AXDOMIdentifier", dom_id)
        #if not node:
        #    raise Exception(f"Couldn't find node with ID {dom_id}. Try passing --force-renderer-accessibility.")
        return json.dumps({"API": "windows", "role": "working on it!"})
