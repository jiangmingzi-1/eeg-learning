"""
第 4 周练习：真实脑电数据 + alpha 阻断现象
==========================================
运行环境：conda activate eeg
运行方式：python 02_real_eeg_alpha.py

第一次运行会自动下载约 100 MB 数据，慢是正常的。
下载后会缓存在 ~/mne_data，之后就不需要再下了。

这个脚本做的事：
  1. 下载 PhysioNet EEGBCI 数据集（109 人真实脑电，公开免费）
  2. 只取运动皮层通道（C3/Cz/C4），因为这是 BCI 最常用的位置
  3. 对比"基线（睁眼放松）"和"想象左手/右手运动"两个条件
  4. 画出 PSD（功率谱密度）和 alpha 频段地形图

跑通这个脚本，你就完成了从"假信号"到"真实数据"的跨越。
面试时你可以说：我在 PhysioNet EEGBCI 上跑通了完整的预处理和频域分析流程。
"""

import numpy as np
import matplotlib.pyplot as plt
import mne

plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei"]
plt.rcParams["axes.unicode_minus"] = False

# =====================================================================
# 第 1 步：加载真实脑电数据
# =====================================================================
print("=" * 60)
print("正在加载 PhysioNet EEGBCI 数据（首次运行需下载，请耐心等待）...")

# subject=1, runs=[1, 2] -> run 1 是基线（睁眼/闭眼），run 2 是运动任务
#
# 注意 update_path=True 不能省：
# mne 第一次运行时默认会弹一个交互问题（"要不要把数据路径写入配置？"），
# 在 .py 脚本里没有键盘输入，会直接 EOFError 崩掉。传 True 就是自动回答"是"。
raw = mne.io.read_raw_edf(
    mne.datasets.eegbci.load_data(subjects=1, runs=[1, 2], update_path=True)[0],
    preload=True,
    verbose=False,
)

print(f"  采样率: {raw.info['sfreq']} Hz")
print(f"  通道数: {len(raw.ch_names)}")
print(f"  时长: {raw.n_times / raw.info['sfreq']:.1f} 秒")
print(f"  通道名: {raw.ch_names}")

# =====================================================================
# 第 2 步：预处理 —— 这是每次都要做的一遍，背下来
# =====================================================================
print("=" * 60)
print("预处理流程：")
print("  1) 带通滤波 1-45 Hz   -> 去掉慢漂移和高频肌电")
print("  2) 陷波 50 Hz         -> 去掉工频干扰（中国是 50 Hz，美国是 60 Hz）")

raw.filter(1.0, 45.0, fir_design="firwin", verbose=False)
raw.notch_filter(50.0, verbose=False)
print("  完成")
print()
print(">>> 面试常问：为什么只滤到 45 Hz？")
print(">>> 答：50 Hz 工频及其谐波要滤掉，同时脑电有效成分主要在 0.5-40 Hz，")
print(">>>     45 Hz 留一点余量避免滤波器边缘失真。")

# =====================================================================
# 第 3 步：选通道 —— 只看运动皮层
# =====================================================================
# ⚠️ 这里有个坑：PhysioNet EEGBCI 的通道名是 'C3..'、'Cz..'（带点），
#    不是干净的 'C3'、'Cz'。如果你直接按 'C3' 去找，会一个都匹配不到。
#    更危险的是：如果代码写成"找不到就跳过"，它不会报错，
#    而是安静地选出 0 个通道，然后算出一堆 0 并照常出图 —— 静默失败。
#    所以这里做两件事：归一化通道名 + 找不到就明确报错。
def normalize(name):
    return name.rstrip(".").upper()


name_to_idx = {normalize(ch): i for i, ch in enumerate(raw.ch_names)}
motor_chs = ["C3", "CZ", "C4"]
available = [ch for ch in motor_chs if ch in name_to_idx]

if len(available) < 3:
    raise RuntimeError(
        f"没找齐运动皮层通道！找到的是 {available}。\n"
        f"实际通道名示例: {raw.ch_names[:8]}\n"
        f"不要忽略这个错误 —— 通道选错的话后面所有结果都是假的。"
    )

raw_motor = raw.copy().pick([name_to_idx[ch] for ch in motor_chs])
print(f"  已选通道: {available}  (原始名: {[raw.ch_names[name_to_idx[c]] for c in available]})")

# ⚠️ 单位陷阱（这里我第一版写错了，值得你记住）：
# 这份数据的单位是【伏特 V】，典型标准差 5.87e-05 V = 58.7 uV，
# 正好落在成年人脑电的正常幅值区间（10-100 uV）。
#
# 换算成 uV^2/Hz 要乘 (1e6)^2 = 1e12，但【只能乘一次】。
# 我第一版既对 raw 乘了 1e6、又对 PSD 乘了 1e12 —— 虚高了 1e12 倍，
# 结果 PSD 显示 1e15、占比算出 102%（远超合理范围）。
# 教训：单位换算一定要先确认原始数据的单位，别凭感觉乘系数。
_unit_factor = 1e12   # V^2/Hz -> uV^2/Hz
print(f"  数据单位确认：伏特 V（标准差 {raw_motor.get_data().std():.2e} V = "
      f"{raw_motor.get_data().std() * 1e6:.1f} uV）")

print()
print(">>> 10-20 系统常识（面试会问）:")
print(">>>   C3 = 左半球运动区，C4 = 右半球运动区，Cz = 中央区")
print(">>>   想象左手运动 -> C4 侧 mu 节律（8-13 Hz）下降")
print(">>>   想象右手运动 -> C3 侧 mu 节律下降")
print(">>>   这个现象叫 ERD（事件相关去同步），是运动想象 BCI 的物理基础")

# =====================================================================
# 第 4 步：算 PSD —— 看各个频段有多少能量
# =====================================================================
print("=" * 60)
print("计算功率谱密度 (PSD)...")

spectrum = raw_motor.compute_psd(fmin=1, fmax=45, verbose=False)
psds = spectrum.get_data()          # shape: (通道数, 频率点数)
freqs = spectrum.freqs

# 把 PSD 从 V^2/Hz 换成 uV^2/Hz（只乘这一次）
psds = psds * _unit_factor
print(f"  PSD 单位已换为 uV^2/Hz，数值范围 {psds.min():.3g} ~ {psds.max():.3g}")
print(f"  （正常范围：低频段几百，alpha 峰几十到几百，高频段个位数）")
if psds.max() > 1e6:
    print("  ⚠️ 数值过大，说明单位换算做了两次，检查有没有重复乘系数")

# 各频段能量（脑电五大频段，必须记住）
bands = {
    "delta": (0.5, 4),
    "theta": (4, 8),
    "alpha": (8, 13),
    "beta": (13, 30),
    "gamma": (30, 45),
}

print()
print(f"{'频段':<8}{'范围(Hz)':<14}{'带内平均(uV^2/Hz)':<20}{'相对频段功率':<14}")
print("-" * 58)
# ⚠️ 占比口径很重要：
#   我第一次用"带内平均 ÷ 1-45Hz 全带平均"，结果 delta 算出 780% —— 看着像 bug。
#   原因：脑电功率谱是 1/f 形状，低频功率密度天然很高；
#        而且各频段宽度不同（delta 3.5Hz vs beta 17Hz），
#        拿"平均功率密度"直接当占比，口径是错的。
#   脑电论文里的标准口径是【相对频段功率】：
#        每个频段的积分功率 ÷ 所有频段积分功率之和，加起来正好 100%。
total_power = 0.0
band_power_values = {}
for name, (lo, hi) in bands.items():
    m = (freqs >= lo) & (freqs <= hi)
    # 积分功率 = 平均功率密度 × 带宽
    band_power_values[name] = psds[:, m].mean() * (hi - lo)

total_power = sum(band_power_values.values())
for name, (lo, hi) in bands.items():
    p = band_power_values[name]
    print(f"{name:<8}{f'{lo}-{hi}':<14}{psds[:, (freqs >= lo) & (freqs <= hi)].mean():<20.4g}"
          f"{p / total_power * 100:>8.1f}%")

print()
print("  >>> 相对频段功率加起来 = 100%，这是论文里的标准写法。")
print("  >>> 静息态下 delta 占比高是正常的（1/f 特性 + 残留慢漂移）。")
print("  >>> 更有信息量的是看【alpha 相对 beta】的比值，它随睁眼闭眼变化。")

# =====================================================================
# 第 5 步：出图
# =====================================================================
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# 左：PSD 曲线
for i, ch in enumerate(available):
    axes[0].plot(freqs, psds[i], label=ch, linewidth=1.2)
axes[0].axvspan(8, 13, color="gold", alpha=0.2, label="alpha (8-13 Hz)")
axes[0].set_xlabel("频率 (Hz)")
# 注意：轴标签不要用 µ 和 ² 这两个字符。
# 中文字体（SimHei / Microsoft YaHei）不含这两个字形，图上会显示成方框。
# 画图给中文读者看时，用 ASCII 的 "uV^2/Hz" 比 "µV²/Hz" 保险。
axes[0].set_ylabel("功率谱密度 (uV^2/Hz)")
axes[0].set_title("真实脑电 PSD：找 10 Hz 附近的峰")
axes[0].set_ylim(0, 500)      # 截掉 1/f 的低频巨峰，否则 alpha 峰被压成一条线
axes[0].legend()
axes[0].grid(alpha=0.3)
axes[0].annotate("alpha 峰", xy=(10, 120), xytext=(18, 300),
                 arrowprops=dict(arrowstyle="->", color="black"))

# 右：全 64 通道的 alpha 功率排序
#
# 为什么不用地形图（topomap）？
#   地形图要对电极位置做空间插值，至少需要 4 个以上电极才画得出来。
#   我们只选了 C3/Cz/C4 三个，画出来会失败或者是一张空图。
#   而且"画出来是空图却又不报错"—— 就是你刚才遇到的那类静默失败。
#   所以这里换成一张更直接、也更有用的图。
alpha_psd_all = raw.compute_psd(fmin=8, fmax=13, verbose=False)
alpha_power = alpha_psd_all.get_data().mean(axis=1) * _unit_factor   # 每通道的 alpha 平均功率

order = np.argsort(alpha_power)[::-1][:15]        # 取最强的 15 个通道
top_names = [raw.ch_names[i] for i in order]
top_values = alpha_power[order]

axes[1].barh(range(len(order)), top_values, color="mediumseagreen")
axes[1].set_yticks(range(len(order)))
axes[1].set_yticklabels(top_names, fontsize=8)
axes[1].invert_yaxis()
axes[1].set_xlabel("alpha (8-13 Hz) 平均功率 (uV^2/Hz)")
axes[1].set_title("alpha 最强的 15 个通道")
axes[1].grid(alpha=0.3, axis="x")

# 自检：alpha 通常在后脑（枕区 O1/Oz/O2、顶区 Pz）最强，
# 因为那里离视觉皮层近，闭眼时 alpha 节律最明显。
print()
print("  alpha 最强的 5 个通道:", top_names[:5])
print("  >>> 自检：这些名字应该以 O / P / Po 开头（枕区、顶区）。")
print("  >>> 如果最强的是 F / Ft / T 开头，说明你的分析有问题——")
print("  >>> 额区和颞区被眼电、肌电污染得最严重。")
print("  >>> 记住这个规律，你做电极对比实验时要按它选通道。")

plt.tight_layout()
plt.savefig("figures/02_real_eeg.png", dpi=120)
print()
print("已保存图: figures/02_real_eeg.png")
plt.show()
plt.close(fig)

# =====================================================================
# 第 6 步：接着做什么（这就是你的项目 1 的起点）
# =====================================================================
print("=" * 60)
print("下一步（这是你 eeg-motor-imagery 项目的开始）:")
print("  1. 加载 runs=[4, 8, 12] —— 这些是真实的左右手运动想象任务")
print("  2. mne.Epochs 把连续信号切成一段一段（用 events 和 event_id）")
print("  3. 提特征：CSP 或 各频段功率")
print("  4. 分类器：sklearn 的 LDA 或 SVM")
print("  5. 交叉验证，报准确率、F1、混淆矩阵")
print()
print("  合格线：二分类 65-70%。")
print("  如果一开始只有 55%（接近瞎猜），不要慌 —— 先检查:")
print("     - events 提取对不对（标签有没有错位）")
print("     - 有没有做 baseline 校正")
print("     - 训练集和测试集是不是按被试/按 run 分的（别泄漏）")
