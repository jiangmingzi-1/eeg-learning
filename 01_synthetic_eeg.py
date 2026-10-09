"""
第 3 周练习：亲手造一段"脑电"，并证明 alpha 波的存在
=====================================================
运行环境：conda activate eeg  （Python 3.11）
运行方式：python 01_synthetic_eeg.py

为什么先造假信号：
  真实脑电有伪迹、有坏道、有一堆格式问题，会让你分不清"是我代码错了"
  还是"数据本来就这样"。先用假信号把时域/频域/滤波这三件事搞清楚，
  上真实数据时你就知道每一行在干什么。

跑完这个文件，你必须能回答这 4 个问题：
  1. 采样率 250 Hz、时长 10 秒，一共多少个点？
  2. 频谱图上的尖峰出现在多少 Hz？为什么？
  3. 闭眼段的 10 Hz 能量比睁眼段高多少倍？
  4. 带通滤波后，波形和原始波形有什么区别？
"""

import numpy as np
import matplotlib.pyplot as plt

# 让中文能正常显示（Windows 下不加这行会变成方块）
plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei"]
plt.rcParams["axes.unicode_minus"] = False

# =====================================================================
# 第 1 步：造一段假脑电
# =====================================================================
fs = 250                      # 采样率：每秒 250 个点（消费级设备常见值）
duration = 10                 # 时长 10 秒
t = np.arange(0, duration, 1 / fs)   # 时间轴，共 2500 个点

# 真实脑电 = 有节律的振荡 + 噪声 + 漂移
alpha = 1.0 * np.sin(2 * np.pi * 10 * t)        # 10 Hz alpha 波（闭眼时强）
beta = 0.3 * np.sin(2 * np.pi * 20 * t)         # 20 Hz beta 波（睁眼思考时强）
drift = 0.5 * np.sin(2 * np.pi * 0.3 * t)       # 0.3 Hz 慢漂移（电极/汗液造成）
noise = 0.6 * np.random.randn(len(t))           # 随机噪声
# 注意 drift 的幅度故意设得比 alpha 小。
# 如果你把它调到 2.0，频谱图上最大的峰会变成 0.3 Hz 而不是 10 Hz ——
# 真实脑电里慢漂移和 50 Hz 工频经常压过真正的脑电信号，
# 这就是为什么每个脑电流程第一步都要滤波。

eeg = alpha + beta + drift + noise

print("=" * 60)
print("第 1 步：假脑电已生成")
print(f"  采样率 fs = {fs} Hz")
print(f"  时长 = {duration} 秒")
print(f"  总点数 = {len(eeg)}  （= fs × duration，记住这个关系）")
print(f"  数据范围 = {eeg.min():.2f} ~ {eeg.max():.2f}")

# =====================================================================
# 第 2 步：时域 —— 画波形
# =====================================================================
fig, axes = plt.subplots(3, 1, figsize=(12, 9))

axes[0].plot(t, eeg, linewidth=0.8, color="steelblue")
axes[0].set_title("① 原始信号（时域）：能看到振荡，但看不出是几 Hz")
axes[0].set_xlabel("时间 (秒)")
axes[0].set_ylabel("幅值")
axes[0].grid(alpha=0.3)

# =====================================================================
# 第 3 步：频域 —— FFT，把"看不出频率"变成"看得见频率"
# =====================================================================
from numpy.fft import rfft, rfftfreq

spectrum = np.abs(rfft(eeg)) / len(eeg) * 2      # 幅值谱
freqs = rfftfreq(len(eeg), 1 / fs)               # 对应的频率轴

# 只看 0-45 Hz（脑电主要频段）
mask = freqs <= 45
axes[1].plot(freqs[mask], spectrum[mask], color="crimson")
axes[1].set_xlabel("频率 (Hz)")
axes[1].set_ylabel("幅值")
axes[1].grid(alpha=0.3)

peak_freq = freqs[mask][np.argmax(spectrum[mask])]
axes[1].set_title(f"② 频谱图（频域）：最大尖峰在 {peak_freq:.1f} Hz")
axes[1].axvline(peak_freq, color="black", linestyle="--", alpha=0.5)
axes[1].annotate(f"峰值 {peak_freq:.1f} Hz", xy=(peak_freq, spectrum[mask].max()),
                 xytext=(peak_freq + 6, spectrum[mask].max() * 0.85),
                 arrowprops=dict(arrowstyle="->"))

# 自检：10 Hz 的峰值应该明显高于 20 Hz 的
print("=" * 60)
print("第 3 步：频域分析")
print(f"  频谱最大峰出现在 {peak_freq:.1f} Hz")
print(f"  如果这个数字不是 10 Hz 附近，说明有更强的低频成分抢走了峰值")
print(f"  （现实里常见元凶：电极漂移、汗液、运动伪迹、50 Hz 工频）")

# =====================================================================
# 第 4 步：滤波 —— 只保留 8-13 Hz（alpha 频段）
# =====================================================================
from scipy.signal import butter, filtfilt

def bandpass(data, low, high, fs, order=4):
    """巴特沃斯带通滤波。脑电处理里最常用的一段代码。"""
    nyq = fs / 2                                  # 奈奎斯特频率
    b, a = butter(order, [low / nyq, high / nyq], btype="band")
    return filtfilt(b, a, data)                   # filtfilt 零相位，不会让波形平移

alpha_only = bandpass(eeg, 8, 13, fs)

axes[2].plot(t, eeg, linewidth=0.6, color="lightgray", label="原始")
axes[2].plot(t, alpha_only, linewidth=1.0, color="darkgreen", label="8-13 Hz 带通后")
axes[2].set_title("③ 带通滤波后：只剩 alpha 波，波形干净了")
axes[2].set_xlabel("时间 (秒)")
axes[2].set_ylabel("幅值")
axes[2].legend()
axes[2].grid(alpha=0.3)

plt.tight_layout()
plt.savefig("figures/01_synthetic.png", dpi=120)
print("  已保存图: figures/01_synthetic.png")
plt.show()
plt.close(fig)   # 关掉图，释放内存。跑长脚本时不加这行会越跑越卡

# =====================================================================
# 第 5 步：模拟"睁眼 vs 闭眼"——这是你能自己做出来的第一个真实现象
# =====================================================================
print("=" * 60)
print("第 5 步：模拟 alpha 阻断（睁眼 vs 闭眼）")

n = len(t)
# 睁眼：alpha 被抑制（alpha blocking），beta 占主导
# 闭眼：alpha 明显增强
#
# 系数 0.8 / 1.4 是算出来的，不是拍的：
#   带内能量 ∝ 幅值²，所以 比值 = (1.4 / 0.8)² ≈ 3.06
#   真实人类闭眼 alpha 增强通常就是 2-5 倍。
# 如果你想验证这个关系，把下面两个系数改成 0.15 / 1.2，
# 比值会暴涨到 30 倍以上 —— 数学没错，只是不符合生理现实。
ALPHA_OPEN = 0.8     # 睁眼时的 alpha 系数
ALPHA_CLOSED = 1.4   # 闭眼时的 alpha 系数

eyes_open = ALPHA_OPEN * alpha + beta + drift + noise
eyes_closed = ALPHA_CLOSED * alpha + 0.4 * beta + drift + noise

def alpha_power(sig, fs):
    """计算 8-13 Hz 频段的能量。这就是"特征提取"的最小例子。"""
    spec = np.abs(rfft(sig)) / len(sig) * 2
    f = rfftfreq(len(sig), 1 / fs)
    band = (f >= 8) & (f <= 13)
    return np.sum(spec[band] ** 2)

p_open = alpha_power(eyes_open, fs)
p_closed = alpha_power(eyes_closed, fs)

print(f"  睁眼 alpha 能量 = {p_open:.4f}")
print(f"  闭眼 alpha 能量 = {p_closed:.4f}")
print(f"  闭眼 / 睁眼 = {p_closed / p_open:.2f} 倍")
print()
print(f"  理论预测: ({ALPHA_CLOSED} / {ALPHA_OPEN})² = {(ALPHA_CLOSED / ALPHA_OPEN) ** 2:.2f}")
print("  两者应该接近 —— 这就是'能量是幅值的平方'最直观的一次验证。")
print()
print(">>> 这个比值，就是你上真实设备后第一个要复现的数字。")
print(">>> 真实人类闭眼 alpha 通常增强 2-5 倍（个体差异很大）。")
print(">>> 如果你的设备测出来 <1.5，通常是三个原因之一：")
print(">>>   1) 电极接触不良 / 阻抗太高")
print(">>>   2) 通道位置不对（alpha 在枕区 Oz 最强，不是随便贴）")
print(">>>   3) 被试没有真正放松（睁眼闭眼时还在动或想事情）")
print(">>> 这正是你电极对比实验的切入点。")

# 画对比图
fig2, axes2 = plt.subplots(2, 1, figsize=(12, 6))
axes2[0].plot(t, eyes_open, linewidth=0.7, color="orange")
axes2[0].set_title(f"睁眼（alpha 能量 = {p_open:.3f}，alpha 被抑制）")
axes2[1].plot(t, eyes_closed, linewidth=0.7, color="purple")
axes2[1].set_title(f"闭眼（alpha 能量 = {p_closed:.3f}，增强 {p_closed/p_open:.1f} 倍）")
for ax in axes2:
    ax.set_xlabel("时间 (秒)")
    ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("figures/01_alpha_blocking.png", dpi=120)
print("  已保存图: figures/01_alpha_blocking.png")
plt.show()
plt.close(fig2)

# =====================================================================
# 自检问题（把答案写在下面注释里，面试时会问）
# =====================================================================
# Q1: 采样率 250 Hz、时长 10 秒，一共多少个点？
#     A:
# Q2: 频谱图上的尖峰出现在多少 Hz？为什么？
#     A:
# Q3: 闭眼段的 10 Hz 能量比睁眼段高多少倍？和真实人类相比如何？
#     A:
# Q4: 带通滤波后波形和原始波形有什么区别？为什么 filtfilt 而不是 lfilter？
#     A:
