from ApplicationServices import (
    AXUIElementCopyAttributeNames,
    AXUIElementCopyAttributeValue,
    AXUIElementCreateApplication,
)

from Cocoa import (
    NSApplicationActivationPolicyRegular,
    NSPredicate,
    NSWorkspace,
)

import json
import time

def find_browser(name):
    ws = NSWorkspace.sharedWorkspace()
    regular_predicate = NSPredicate.predicateWithFormat_(f"activationPolicy == {NSApplicationActivationPolicyRegular}")
    running_apps = ws.runningApplications().filteredArrayUsingPredicate_(regular_predicate)
    name_predicate = NSPredicate.predicateWithFormat_(f"localizedName contains[c] '{name}'")
    filtered_apps = running_apps.filteredArrayUsingPredicate_(name_predicate)
    if filtered_apps.count() == 0:
        return None
    app = filtered_apps[0]
    pid = app.processIdentifier()
    if pid == -1:
        return None
    return AXUIElementCreateApplication(pid)

def poll_for_tab(root, product, url):
    tab = find_tab(root, product, url)
    loops = 0
    while not tab:
        loops += 1
        time.sleep(0.01)
        tab = find_tab(root, product, url)

    return tab

def find_tab(root, product, url):
    stack = [root]
    tabs = []
    while stack:
        node = stack.pop()

        (err, role) = AXUIElementCopyAttributeValue(node, "AXRole", None)
        if err:
            continue
        if role == "AXWebArea":
            (err, tab_url) = AXUIElementCopyAttributeValue(node, "AXURL", None)
            if (str(tab_url) == url):
              return node
            else:
              continue

        (err, children) = AXUIElementCopyAttributeValue(node, "AXChildren", None)
        if err:
            continue
        stack.extend(children)

    return None


def find_node(root, attribute, expected_value):
    stack = [root]
    while stack:
        node = stack.pop()

        (err, attributes) = AXUIElementCopyAttributeNames(node, None)
        if err:
            continue
        if attribute in attributes:
            (err, value) = AXUIElementCopyAttributeValue(node, attribute, None)
            if err:
                continue
            if value == expected_value:
                return node

        (err, children) = AXUIElementCopyAttributeValue(node, "AXChildren", None)
        if err:
            continue
        stack.extend(children)
    return None


def serialize_node(node):
    props = {}
    props["API"] = "axapi"
    (err, role) = AXUIElementCopyAttributeValue(node, "AXRole", None)
    props["role"] = role
    (err, name) = AXUIElementCopyAttributeValue(node, "AXTitle", None)
    props["name"] = name
    (err, description) = AXUIElementCopyAttributeValue(node, "AXDescription", None)
    props["description"] = description

    return props


class AXAPIExecutorImpl:
    def setup(self, product_name):
        self.product_name = product_name
        self.root = None
        self.document = None
        self.test_url = None


    def get_platform_accessibility_node(self, dom_id, url):
        if not self.root:
            self.root = find_browser(self.product_name)
            if not self.root:
                raise Exception(
                    f"Couldn't find browser {self.product_name} in accessibility API: AX API. Did you turn on accessibility?"
                )

        if self.test_url != url or not self.document:
           self.test_url = url
           self.document = poll_for_tab(self.root, self.product_name, url)

        node = find_node(self.document, "AXDOMIdentifier", dom_id)
        if not node:
            raise Exception(f"Couldn't find node with ID {dom_id}.")
        return json.dumps(serialize_node(node))
