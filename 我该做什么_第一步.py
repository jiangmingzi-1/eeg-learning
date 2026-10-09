# 复制这一整段，粘进 Jupyter 的一个 cell，然后按 Shift + Enter
# 这个文件本身不用运行，用 Jupyter 更方便

# ===== 第 1 步：检查你用的是哪个 Python =====
import sys
print("Python 版本:", sys.version.split()[0])
print("解释器位置:", sys.executable)

# ===== 第 2 步：检查 mne 在不在 =====
try:
    import mne
    print("mne 版本:", mne.__version__)
except ModuleNotFoundError:
    print("mne 没找到！")

# ===== 第 3 步：自动判断 =====
if sys.version.startswith("3.11"):
    print()
    print("✅ 对了！你就在 eeg 环境里，可以开始学脑电了。")
    print("   下一步：打开 check_slicing.py 做那 9 道题。")
else:
    print()
    print("❌ 你还在 base 环境（Python 3.14）里，这里没有 mne。")
    print("   解决：看 Jupyter 右上角，点内核名字 -> 选「Python (eeg)」")
    print("   然后重新运行这个 cell。")
