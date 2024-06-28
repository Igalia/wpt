import json
import time

from ..executors.ia2.constants import *

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

CHILDID_SELF = 0
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
    os.path.dirname(os.path.realpath(__file__)),
    "ia2",
    "ia2_api_all.tlb",
)
ia2Mod = comtypes.client.GetModule(ia2Tlb)
del ia2Tlb

### This was done by Firefox:
# Shove all the IAccessible* interfaces and IA2_* constants directly
# into our namespace for convenience.
globals().update((k, getattr(ia2Mod, k)) for k in ia2Mod.__all__)

## TEST BEFORE REMOVE
## Maybe we can remove this because we don't have the same linter? try deleting this line later.
# We use this below. The linter doesn't understand our globals() update hack.
IAccessible2 = ia2Mod.IAccessible2 
del ia2Mod

## TEST BEFORE REMOVE
## Do we need to do this even when we are only querying IA2?
uiaMod = comtypes.client.GetModule("UIAutomationCore.dll")
globals().update((k, getattr(uiaMod, k)) for k in uiaMod.__all__)
uiaClient = comtypes.CoCreateInstance(
    uiaMod.CUIAutomation._reg_clsid_,
    interface=uiaMod.IUIAutomation,
    clsctx=comtypes.CLSCTX_INPROC_SERVER,
)

role_to_string = {
  ROLE_SYSTEM_TITLEBAR: "ROLE_SYSTEM_TITLEBAR",
  ROLE_SYSTEM_MENUBAR: "ROLE_SYSTEM_MENUBAR",
  ROLE_SYSTEM_SCROLLBAR: "ROLE_SYSTEM_SCROLLBAR",
  ROLE_SYSTEM_GRIP: "ROLE_SYSTEM_GRIP",
  ROLE_SYSTEM_SOUND: "ROLE_SYSTEM_SOUND",
  ROLE_SYSTEM_CURSOR: "ROLE_SYSTEM_CURSOR",
  ROLE_SYSTEM_CARET: "ROLE_SYSTEM_CARET",
  ROLE_SYSTEM_ALERT: "ROLE_SYSTEM_ALERT",
  ROLE_SYSTEM_WINDOW: "ROLE_SYSTEM_WINDOW",
  ROLE_SYSTEM_CLIENT: "ROLE_SYSTEM_CLIENT",
  ROLE_SYSTEM_MENUPOPUP: "ROLE_SYSTEM_MENUPOPUP",
  ROLE_SYSTEM_MENUITEM: "ROLE_SYSTEM_MENUITEM",
  ROLE_SYSTEM_TOOLTIP: "ROLE_SYSTEM_TOOLTIP",
  ROLE_SYSTEM_APPLICATION: "ROLE_SYSTEM_APPLICATION",
  ROLE_SYSTEM_DOCUMENT: "ROLE_SYSTEM_DOCUMENT",
  ROLE_SYSTEM_PANE: "ROLE_SYSTEM_PANE",
  ROLE_SYSTEM_CHART: "ROLE_SYSTEM_CHART",
  ROLE_SYSTEM_DIALOG: "ROLE_SYSTEM_DIALOG",
  ROLE_SYSTEM_BORDER: "ROLE_SYSTEM_BORDER",
  ROLE_SYSTEM_GROUPING: "ROLE_SYSTEM_GROUPING",
  ROLE_SYSTEM_SEPARATOR: "ROLE_SYSTEM_SEPARATOR",
  ROLE_SYSTEM_TOOLBAR: "ROLE_SYSTEM_TOOLBAR",
  ROLE_SYSTEM_STATUSBAR: "ROLE_SYSTEM_STATUSBAR",
  ROLE_SYSTEM_TABLE: "ROLE_SYSTEM_TABLE",
  ROLE_SYSTEM_COLUMNHEADER: "ROLE_SYSTEM_COLUMNHEADER",
  ROLE_SYSTEM_ROWHEADER: "ROLE_SYSTEM_ROWHEADER",
  ROLE_SYSTEM_COLUMN: "ROLE_SYSTEM_COLUMN",
  ROLE_SYSTEM_ROW: "ROLE_SYSTEM_ROW",
  ROLE_SYSTEM_CELL: "ROLE_SYSTEM_CEL",
  ROLE_SYSTEM_LINK: "ROLE_SYSTEM_LINK",
  ROLE_SYSTEM_HELPBALLOON: "ROLE_SYSTEM_HELPBALLOON",
  ROLE_SYSTEM_CHARACTER: "ROLE_SYSTEM_CHARACTER",
  ROLE_SYSTEM_LIST: "ROLE_SYSTEM_LIST",
  ROLE_SYSTEM_LISTITEM: "ROLE_SYSTEM_LISTITEM",
  ROLE_SYSTEM_OUTLINE: "ROLE_SYSTEM_OUTLINE",
  ROLE_SYSTEM_OUTLINEITEM: "ROLE_SYSTEM_OUTLINEITEM",
  ROLE_SYSTEM_PAGETAB: "ROLE_SYSTEM_PAGETAB",
  ROLE_SYSTEM_PROPERTYPAGE: "ROLE_SYSTEM_PROPERTYPAGE",
  ROLE_SYSTEM_INDICATOR: "ROLE_SYSTEM_INDICATOR",
  ROLE_SYSTEM_GRAPHIC: "ROLE_SYSTEM_GRAPHIC",
  ROLE_SYSTEM_STATICTEXT: "ROLE_SYSTEM_STATICTEXT",
  ROLE_SYSTEM_TEXT: "ROLE_SYSTEM_TEXT",
  ROLE_SYSTEM_PUSHBUTTON: "ROLE_SYSTEM_PUSHBUTTON",
  ROLE_SYSTEM_CHECKBUTTON: "ROLE_SYSTEM_CHECKBUTTON",
  ROLE_SYSTEM_RADIOBUTTON: "ROLE_SYSTEM_RADIOBUTTON",
  ROLE_SYSTEM_COMBOBOX: "ROLE_SYSTEM_COMBOBOX",
  ROLE_SYSTEM_DROPLIST: "ROLE_SYSTEM_DROPLIST",
  ROLE_SYSTEM_PROGRESSBAR: "ROLE_SYSTEM_PROGRESSBAR",
  ROLE_SYSTEM_DIAL: "ROLE_SYSTEM_DIAL",
  ROLE_SYSTEM_HOTKEYFIELD: "ROLE_SYSTEM_HOTKEYFIELD",
  ROLE_SYSTEM_SLIDER: "ROLE_SYSTEM_SLIDER",
  ROLE_SYSTEM_SPINBUTTON: "ROLE_SYSTEM_SPINBUTTON",
  ROLE_SYSTEM_DIAGRAM: "ROLE_SYSTEM_DIAGRAM",
  ROLE_SYSTEM_ANIMATION: "ROLE_SYSTEM_ANIMATION",
  ROLE_SYSTEM_EQUATION: "ROLE_SYSTEM_EQUATION",
  ROLE_SYSTEM_BUTTONDROPDOWN: "ROLE_SYSTEM_BUTTONDROPDOWN",
  ROLE_SYSTEM_BUTTONMENU: "ROLE_SYSTEM_BUTTONMENU",
  ROLE_SYSTEM_BUTTONDROPDOWNGRID: "ROLE_SYSTEM_BUTTONDROPDOWNGRID",
  ROLE_SYSTEM_WHITESPACE: "ROLE_SYSTEM_WHITESPACE",
  ROLE_SYSTEM_PAGETABLIST: "ROLE_SYSTEM_PAGETABLIST",
  ROLE_SYSTEM_CLOCK: "ROLE_SYSTEM_CLOCK",
  ROLE_SYSTEM_SPLITBUTTON: "ROLE_SYSTEM_SPLITBUTTON",
  ROLE_SYSTEM_IPADDRESS: "ROLE_SYSTEM_IPADDRESS",
  ROLE_SYSTEM_OUTLINEBUTTON: "ROLE_SYSTEM_OUTLINEBUTTON",
  IA2_ROLE_CANVAS: "IA2_ROLE_CANVAS",
  IA2_ROLE_CAPTION: "IA2_ROLE_CAPTION",
  IA2_ROLE_CHECK_MENU_ITEM: "IA2_ROLE_CHECK_MENU_ITEM",
  IA2_ROLE_COLOR_CHOOSER: "IA2_ROLE_COLOR_CHOOSER",
  IA2_ROLE_DATE_EDITOR: "IA2_ROLE_DATE_EDITOR",
  IA2_ROLE_DESKTOP_ICON: "IA2_ROLE_DESKTOP_ICON",
  IA2_ROLE_DESKTOP_PANE: "IA2_ROLE_DESKTOP_PANE",
  IA2_ROLE_DIRECTORY_PANE: "IA2_ROLE_DIRECTORY_PANE",
  IA2_ROLE_EDITBAR: "IA2_ROLE_EDITBAR",
  IA2_ROLE_EMBEDDED_OBJECT: "IA2_ROLE_EMBEDDED_OBJECT",
  IA2_ROLE_ENDNOTE: "IA2_ROLE_ENDNOTE",
  IA2_ROLE_FILE_CHOOSER: "IA2_ROLE_FILE_CHOOSER",
  IA2_ROLE_FONT_CHOOSER: "IA2_ROLE_FONT_CHOOSER",
  IA2_ROLE_FOOTER: "IA2_ROLE_FOOTER",
  IA2_ROLE_FOOTNOTE: "IA2_ROLE_FOOTNOTE",
  IA2_ROLE_FORM: "IA2_ROLE_FORM",
  IA2_ROLE_FRAME: "IA2_ROLE_FRAME",
  IA2_ROLE_GLASS_PANE: "IA2_ROLE_GLASS_PANE",
  IA2_ROLE_HEADER: "IA2_ROLE_HEADER",
  IA2_ROLE_HEADING: "IA2_ROLE_HEADING",
  IA2_ROLE_ICON: "IA2_ROLE_ICON",
  IA2_ROLE_IMAGE_MAP: "IA2_ROLE_IMAGE_MAP",
  IA2_ROLE_INPUT_METHOD_WINDOW: "IA2_ROLE_INPUT_METHOD_WINDOW",
  IA2_ROLE_INTERNAL_FRAME: "IA2_ROLE_INTERNAL_FRAME",
  IA2_ROLE_LABEL: "IA2_ROLE_LABEL",
  IA2_ROLE_LAYERED_PANE: "IA2_ROLE_LAYERED_PANE",
  IA2_ROLE_NOTE: "IA2_ROLE_NOTE",
  IA2_ROLE_OPTION_PANE: "IA2_ROLE_OPTION_PANE",
  IA2_ROLE_PAGE: "IA2_ROLE_PAGE",
  IA2_ROLE_PARAGRAPH: "IA2_ROLE_PARAGRAPH",
  IA2_ROLE_RADIO_MENU_ITEM: "IA2_ROLE_RADIO_MENU_ITEM",
  IA2_ROLE_REDUNDANT_OBJECT: "IA2_ROLE_REDUNDANT_OBJECT",
  IA2_ROLE_ROOT_PANE: "IA2_ROLE_ROOT_PANE",
  IA2_ROLE_RULER: "IA2_ROLE_RULER",
  IA2_ROLE_SCROLL_PANE: "IA2_ROLE_SCROLL_PANE",
  IA2_ROLE_SECTION: "IA2_ROLE_SECTION",
  IA2_ROLE_SHAPE: "IA2_ROLE_SHAPE",
  IA2_ROLE_SPLIT_PANE: "IA2_ROLE_SPLIT_PANE",
  IA2_ROLE_TEAR_OFF_MENU: "IA2_ROLE_TEAR_OFF_MENU",
  IA2_ROLE_TERMINAL: "IA2_ROLE_TERMINAL",
  IA2_ROLE_TEXT_FRAME: "IA2_ROLE_TEXT_FRAME",
  IA2_ROLE_TOGGLE_BUTTON: "IA2_ROLE_TOGGLE_BUTTON",
  IA2_ROLE_UNKNOWN: "IA2_ROLE_UNKNOWN",
  IA2_ROLE_VIEW_PORT: "IA2_ROLE_VIEW_PORT",
  IA2_ROLE_COMPLEMENTARY_CONTENT: "IA2_ROLE_COMPLEMENTARY_CONTENT",
  IA2_ROLE_LANDMARK: "IA2_ROLE_LANDMARK",
  IA2_ROLE_LEVEL_BAR: "IA2_ROLE_LEVEL_BAR",
  IA2_ROLE_CONTENT_DELETION: "IA2_ROLE_CONTENT_DELETION",
  IA2_ROLE_CONTENT_INSERTION: "IA2_ROLE_CONTENT_INSERTION",
  IA2_ROLE_BLOCK_QUOTE: "IA2_ROLE_BLOCK_QUOTE",
  IA2_ROLE_MARK: "IA2_ROLE_MARK",
  IA2_ROLE_SUGGESTION: "IA2_ROLE_SUGGESTION",
  IA2_ROLE_COMMENT: "IA2_ROLE_COMMENT"
}

def accessible_object_from_window(hwnd, objectID=OBJID_CLIENT):
    p = POINTER(IAccessible)()
    oleacc.AccessibleObjectFromWindow(
        hwnd, objectID, byref(IAccessible._iid_), byref(p)
    )
    return p


def name_from_hwnd(hwnd):
    MAX_CHARS = 257
    buffer = ctypes.create_unicode_buffer(MAX_CHARS)
    user32.GetWindowTextW(hwnd, buffer, MAX_CHARS)
    return buffer.value
    

def get_browser_hwnd(product_name):
    found = []

    @ctypes.WINFUNCTYPE(BOOL, HWND, LPARAM)
    def callback(hwnd, lParam):
        name = name_from_hwnd(hwnd)
        if product_name not in name.lower():
            return True
        found.append(hwnd)
        return False

    user32.EnumWindows(callback, LPARAM(0))
    if not found:
        raise LookupError(f"Couldn't find {product_name} HWND")
    return found[0]


def to_ia2(obj):
    serv = obj.QueryInterface(IServiceProvider)
    return serv.QueryService(IAccessible2._iid_, IAccessible2)


def find_browser(product_name):
    """Get the IAccessible2 for the document being tested."""
    time.sleep(2)
    
    hwnd = get_browser_hwnd(product_name)
    root = accessible_object_from_window(hwnd)
    return to_ia2(root)


def find_ia2_node(root, id, depth):
    print("??????????????????????????????????????????????????????")
    print(root)
    search = f"id:{id};"
    # Child ids begin at 1.
    #roleint = root.accRole(CHILDID_SELF)
    #print("--" * depth + " " + role_to_string[roleint])
    for i in range(1, root.accChildCount + 1):
        child = to_ia2(root.accChild(i))
        if search in child.attributes:
            return child
        descendant = find_ia2_node(child, id, depth+1)
        if descendant:
            return descendant

def serialize_node(node):
    node_dictionary = {}
    node_dictionary["API"] = "windows"
    # todo: this is not necesarially the msaa role -- test!! 
    node_dictionary["msaa_role"] = role_to_string[node.accRole(CHILDID_SELF)]
    #node_dictionary["name"] = Atspi.Accessible.get_name(node)
    return node_dictionary

class WindowsAccessibilityExecutorImpl:
    def setup(self, product_name):
        self.product_name = product_name
        #self.root = find_browser(self.product_name)

        #if not self.root:
        #    raise Exception(f"Couldn't find application: {product_name}")


    def get_accessibility_api_node(self, dom_id):
        self.root = find_browser(self.product_name)
        if not self.root:
            raise Exception(f"Couldn't find browser {self.product_name}.")
        node = find_ia2_node(self.root, dom_id, 0)
        if not node:
            raise Exception(f"Couldn't find node with ID {dom_id}.")
        return json.dumps(serialize_node(node))
