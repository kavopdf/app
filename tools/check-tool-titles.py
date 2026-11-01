#!/usr/bin/env python3
"""Fails the build if any tool would open with the wrong heading.

Every action either runs in its own activity (which carries a label in the
manifest) or is hosted by ToolsActivity, where the heading comes from a branch in
applyToolChrome(). A missing branch silently falls back to the app name - which is
exactly how the "Extract images" screen ended up titled "KavoPDF".
"""
import re
import sys

KT = "app/src/main/java/com/kavopdf/app"

enum = re.search(r"enum class Action \{([^}]*)\}", open(f"{KT}/model/ToolItem.kt").read()).group(1)
actions = [a.strip() for a in enum.replace("\n", " ").split(",") if a.strip()]

main = open(f"{KT}/MainActivity.kt").read()
tools = open(f"{KT}/ToolsActivity.kt").read()

# actions that get their own screen:  Action.X -> Intent(this, YActivity::class.java)
own = set(re.findall(r"Action\.([A-Z_]+)\s*->\s*Intent\(this[@\w]*, \w+Activity::class\.java\)", main))

# actions ToolsActivity gives a heading to
block = tools[tools.index("private fun applyToolChrome"):]
block = block[: block.index("\n    }")]
titled = set(re.findall(r"Action\.([A-Z_]+)", block))

# The Protect screen has no permission picker any more: the engine sets no PDF permission
# bits at all, so a description promising "permissions" is a lie and the old four-item
# perm_choices array was left behind as a dead resource. Neither may come back.
strings = open("app/src/main/res/values/strings.xml", encoding="utf-8").read()
leftovers = []
if "perm_choices" in strings:
    leftovers.append("the dead perm_choices array is back - nothing references it")
if re.search(r'<string name="tool_protect_desc">[^<]*permission', strings):
    leftovers.append("tool_protect_desc promises permissions the engine cannot set")
if leftovers:
    for l in leftovers:
        print("FAIL:", l)
    sys.exit(1)

uncovered = [a for a in actions if a not in own and a not in titled]
print(f"actions: {len(actions)} | own screen: {len(own)} | titled by ToolsActivity: {len(titled)}")
if uncovered:
    print("FAIL: these would open with no proper heading:", uncovered)
    sys.exit(1)
print("PASS: every tool has a heading")
