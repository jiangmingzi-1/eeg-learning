"""
第一关体检：切片 / 循环 / 函数 / 字符串
=========================================
用法：
  1. 不要看下面的参考答案（在文件最后，用注释隔开了）
  2. 从上往下，每道题自己写代码，用 print 打印结果
  3. 全部写完再对照答案

判定标准：
  - 30 分钟内全部写对  -> 立刻停止看黑马课，进入 numpy / 脑电阶段
  - 第 6、7、8 题写不出来 -> 再花 3 天只练这三类

为什么是这几道题：
  第 6 题（滑窗切片）= 脑电 epoch 分段的原型
  第 7 题（循环找极值）= 特征提取的原型
  第 8 题（join）= 写日志/输出结果文件的基础
"""

data = [3, 7, 1, 9, 4, 8, 2, 6, 5, 0]

print("=" * 50)
print("  CHECK START - if you see this, your setup works!")
print("=" * 50)
print()
print("data:", data)
print()
print("All 9 answers below are None because you have not")
print("solved them yet. Edit q1/q2/... in the file, then")
print("run this script again to check your answer.")
print()
print("-" * 50)

# ---- 1. 取出前 5 个数，赋值给 q1 ----
q1 = data[0:5]
print("1.", q1)


# ---- 2. 取出后 3 个数，赋值给 q2 ----
q2 = data[-3:]
print("2.", q2)


# ---- 3. 反转整个列表，赋值给 q3 ----
q3 = data[::-1]
print("3.", q3)


# ---- 4. 取出索引 2 到 7（含 2 不含 7）之间的所有偶数，赋值给 q4 ----
# 提示：先切片，再用条件筛选。可以用列表推导式，也可以用循环
q4 = [n for n in data[2:7] if n % 2 == 0]
print("4.", q4)


# ---- 5. 从第 1 个开始，每隔 2 个取一个，赋值给 q5 ----
q5 = data[::2]
print("5.", q5)


# ---- 6. 把这 10 个数按 2 个一组，切成 5 组，赋值给 q6 ----
# 期望结果: [[3, 7], [1, 9], [4, 8], [2, 6], [5, 0]]
# 这就是"滑窗"：脑电里把 10 秒信号切成 1 秒一段，用的是同一套逻辑
q6 = [data[i:i+2] for i in range(0, len(data), 2)]
print("6.", q6)


# ---- 7. 找出最大值和它的索引，赋值给 q7_max 和 q7_index ----
# 不许用 max() 和 index()，必须用循环
q7_max = 
q7_index = None
print("7. 最大值 =", q7_max, "索引 =", q7_index)


# ---- 8. 把列表转成字符串 "3-7-1-9-4-8-2-6-5-0"，赋值给 q8 ----
# 提示：str.join()，但列表里是整数，要先转成字符串
q8 = None
print("8.", q8)


# ---- 9. 写一个函数 moving_average(x, k)，返回 x 的 k 点滑动平均 ----
# 提示：对每个 i，取 x[i:i+k] 求平均。这就是脑电里最基础的平滑滤波
def moving_average(x, k):
    pass


print("9.", moving_average([1, 2, 3, 4, 5, 6], 3))  # 期望 [2.0, 3.0, 4.0, 5.0]


# =====================================================================
# 参考答案 —— 写完之后再看
# =====================================================================
#
# q1 = data[:5]                          # [3, 7, 1, 9, 4]
# q2 = data[-3:]                         # [2, 6, 5]
# q3 = data[::-1]                        # [0, 5, 6, 2, 8, 4, 9, 1, 7, 3]
# q4 = [n for n in data[2:7] if n % 2 == 0]   # [4, 8, 2]
# q5 = data[::2]                         # [3, 1, 4, 2, 5]
#
# q6 = []                                 # 手写版
# for i in range(0, len(data), 2):
#     q6.append(data[i:i+2])
# # 或一行版:
# # q6 = [data[i:i+2] for i in range(0, len(data), 2)]
#
# q7_max = data[0]
# q7_index = 0
# for i in range(len(data)):
#     if data[i] > q7_max:
#         q7_max = data[i]
#         q7_index = i
# # q7_max = 9, q7_index = 3
#
# q8 = "-".join(str(n) for n in data)
#
# def moving_average(x, k):
#     out = []
#     for i in range(len(x) - k + 1):
#         window = x[i:i+k]
#         out.append(sum(window) / k)
#     return out
# # 注意：这就是脑电里"滑动窗"的写法，
# #      len(x) - k + 1 这个边界后面做 epoch 分段会反复遇到
