---
tags:
  - Python
  - 语法
  - 入门
created: 2026-05-30
---

# Python 语法全览 —— 基于雷达 UDP 上位机项目

> 本文从 `radar_udp_python_fixed_78bytes` 项目中提取所有 Python 语法，用**大白话 + 生活比喻**讲清楚。每一节都附上了项目里的真实代码，看完就能读懂项目。

---

## 零、先认识两个"大管家"

在正式学语法之前，有些朋友会好奇：Python 代码写完以后，是怎么跑起来的？

### Python 解释器 —— 你的"同声传译"

- C 语言需要一个**编译器**，把代码一口气全翻译成机器语言（0 和 1），生成一个 `.exe` 文件，然后才能运行。
- Python 不需要这一步。它用的是**解释器**，就像一个**同声传译**：你写一行，它当场找操作系统翻译执行一行。所以你改完代码立刻就能跑，不用等"编译"。

### 装饰器（`@` 符号）—— "汽车改装厂"

Python 里带有 `@` 符号的语法叫做**装饰器**。

**通俗比喻**：你把一辆"基础款汽车"（你写好的函数或类）开进 `@改装厂`，Python 会**在你使用它之前**自动给它加上防撞梁、倒车雷达、真皮座椅……然后你再开走。车还是那辆车，但功能变强了。

项目里的例子：`@dataclass(frozen=True)` 就是一个改装厂，它自动给类装上数据管理的能力（`frozen=True` 是改装图纸：把数据"冻住"，变成只读的）。

---

## 一、基础语法

### 1. 编码声明 —— "请用 UTF-8 读我"

```python
# -*- coding: utf-8 -*-
```

相当于在文件第一行贴了一张便条："嘿，解释器，这里面有中文，请用 UTF-8 编码读，别乱码！"Python 3 默认已经是 UTF-8，但这行保留着就像门口挂个招牌——清楚、放心。

### 2. 注释 —— 写给"未来自己"的小纸条

```python
# 这是单行注释
# 以后如果只想改颜色、边框、字体、按钮样式，改这个文件即可。
```

`#` 后面写的东西，Python 解释器会**假装看不见**。注释是写给人看的——尤其是三个月后已经忘了这段代码在干嘛的你自己。**好注释解释"为什么这么做"，而不是复述"做了什么"**。

### 3. 变量与常量 —— "贴标签"和"刻石碑"

```python
# 变量：可以随时换内容的标签
ip = "192.168.10.10"       # 给这个值贴个标签叫 ip
port = 9001                 # 给这个值贴个标签叫 port

# 常量：约定俗成"不要改"，用全大写提醒自己
RADAR_HEAD = 0x55AA
RADAR_TAIL = 0xAA55
```

**变量**就像便利贴，你可以撕下来重新贴到另一个值上。**常量**更像刻在石碑上的字——你约定好不去改它（全靠自觉，Python 不会拦你，但大写命名是程序员的"君子协定"）。

Python 是**动态类型**语言，不像 C 语言那样需要先声明 `int x;` 再赋值。你直接写 `x = 5`，Python 自动知道它是整数——就像超市收银员不需要你提前告诉他"我要给的是人民币"。

### 4. 数据类型 —— 工具箱里不同形状的"零件"

```python
# 整数（int）—— 就像完整的苹果
frame_id = 1
hex_value = 0xFFFFFFFF    # 十六进制写法，等于 4294967295

# 浮点数（float）—— 带小数点的数
ratio = 3.14

# 字符串（str）—— 一串文字
title = "雷达参数 UDP 上位机"
multi_line = """
    这是多行文字，
    就像写小作文一样
"""

# 布尔值（bool）—— 只有"对"和"错"两种状态
is_checked = True       # 开了
is_empty = False        # 关了

# None —— 表示"啥也没有"，类似于快递单上写"空"
result = None
```

这些就像五金店里的零件：整数是钉子，浮点数是带刻度的螺丝，字符串是标签纸，布尔值是开关，`None` 是个空盒子。写代码就是你从工具箱里挑合适的零件拼装。

### 5. 算术运算符 —— 就是小学数学

```python
a = 10 + 3     # 加法 → 13
a = 10 - 3     # 减法 → 7
a = 10 * 3     # 乘法 → 30
a = 10 / 3     # 除法（带小数）→ 3.333...
a = 10 // 3    # 地板除（只要整数部分）→ 3
a = 10 % 3     # 取余数（10 除以 3 余 1）→ 1
a = 2 ** 3     # 2 的 3 次方 → 8
```

`//` 和 `%` 是写界面布局时的好帮手。项目里用 `row = idx // 2` 算"这个控件在第几行"，用 `col = (idx % 2) * 2` 算"在第几列"——就像在 Excel 里排格子。

### 6. 比较运算符 —— "问判断题"

```python
if value < 0 or value > 0xFFFFFFFF:   # 这个数是不是超出范围了？
if len(packet) != PACKET_BYTES:       # 包的长度和预期不一样？
if sigpayload == SIGPAYLOAD_DELAY:    # 当前是延迟模式吗？
```

这些运算符就是在问"是非题"，答案永远是 `True`（对）或 `False`（错）。就像考卷上的判断题，你只能打 √ 或 ×。

### 7. 逻辑运算符 —— "and = 并且，or = 或者，not = 不是"

```python
if value < 0 or value > 0xFFFFFFFF:   # 小于 0 "或者" 大于最大值 → 任一成立就报警
if not path:                          # 路径为空？ → "不是"有路径
if a and b:                           # a "并且" b 都成立才行
```

Python 里有一个"潜规则"：**空的东西默认为 `False`**。空字符串 `""`、空列表 `[]`、`None`、数字 `0`，放在 `if` 后面都等价于"假"。所以 `if not path` 就是问"路径是不是空的？"——非常自然。

### 8. 字符串操作 —— "文字编辑的瑞士军刀"

```python
# 拼接 —— 就像用胶水把两段话粘起来
ip = "192.168.10.10"
full = ip + ":" + str(port)          # → "192.168.10.10:9001"

# 去除首尾空白 —— 把两头的空格剪掉
clean = text.strip()

# f-string —— 这是字符串界的"填空题"
# 把花括号 {} 当成空白格子，Python 自动帮你填
name = f"发送 {sent} 字节 -> {ip}:{port}"
error = f"包长度异常：{len(packet)}，期望 {PACKET_BYTES}"

# 数字格式化 —— 告诉 Python "怎么显示这个数"
f"{byte:02X}"     # 显示成 2 位大写十六进制，不足补零
                  # 比如 10 → "0A"，255 → "FF"
f"{ratio:.2f}"    # 保留 2 位小数：3.14159 → "3.14"
```

**f-string 是 Python 里最常用的黑科技**。把它想象成一份"填空题模板"：`f"你好，{name}，你考了{score}分"`——花括号里的变量会被自动替换成实际值。比用 `+` 拼接优雅 100 倍。

### 9. 列表（list）—— "带编号的收纳盒"

```python
# 创建列表 —— 就像一个按序号排列的抽屉柜
names = ["chan_dly0", "chan_dly1", "chan_dly2"]
zeros = [0] * 8          # 8 个 0：相当于"复制粘贴 8 份"

# 取东西 —— 编号从 0 开始！（这是程序员的祖传规矩）
first = names[0]          # 第一个 → "chan_dly0"
last = names[-1]          # 倒数第一个 → "chan_dly2"

# 切片 —— 切一段出来，像切蛋糕
subset = names[0:2]       # 第 0 到第 2 个（不含第 2 个）→ ["chan_dly0", "chan_dly1"]
tail = names[1:]          # 从第 1 个到末尾

# 拼接和追加
combined = [1, 2] + [0, 0]   # 两个抽屉柜拼一起
my_list.append("新东西")      # 往末尾塞一个
my_list.extend([a, b, c])    # 往末尾塞一堆

# 数一数有几个
count = len(my_list)
```

> ⚠️ **新手陷阱**：列表编号从 **0** 开始，不是从 1 开始！`names[0]` 是第一个，`names[1]` 是第二个。习惯了就好——可以理解成"偏移量"：第 0 个偏移是起点，第 1 个偏移是往后走一步。

### 10. 元组（tuple）—— "封了胶带的收纳盒"

```python
# 元组：创建之后就不能改（加固版列表）
point = (3, 5)
fields = ("con_pinc", "con_pw", "con_pri")
single = (1,)              # ⚠️ 单元素必须加逗号，否则 Python 以为你只是打个括号

# 元组解包 —— 一口气把里面的东西倒出来
a, b = (1, 2)              # a=1, b=2
path, _ = func()           # _ 是"垃圾桶变量"：这个值我不要了
checksum, tail = struct.unpack("<HH", data)  # 一把拆出两个数
```

**列表 vs 元组**：列表像开放式收纳盒，随时可以增减东西；元组像用胶带封死的快递箱，装好了就不能改。项目里用元组存"雷达参数列表"——这些参数是定好的，不该被中途篡改。

### 11. 字典（dict）—— "通讯录"

```python
# 创建字典 —— 就像存联系人的手机通讯录
cfg = {
    "ip": "192.168.10.10",    # "名字" → "电话号码"
    "port": 9001,
    "frame_id": 1,
}

# 查号码
ip = cfg["ip"]                     # 直接查，但名字不存在会报错
ip = cfg.get("ip", "127.0.0.1")    # 安全查法：名字不存在就返回默认值 "127.0.0.1"

# 加新联系人、改号码
cfg["period_ms"] = 500

# 遍历整个通讯录
for name, number in cfg.items():
    print(f"{name} 的号码是 {number}")

# 查一下通讯录里有没有这个人
if "ip" in cfg:
    ...
```

字典就是"键 → 值"的映射表。**推荐用 `.get()` 而不是 `[]`** 来读取——就像你打电话前先查通讯录，找不到也不慌，用个默认号码代替，而不是直接崩溃。

### 12. 条件语句 if / elif / else —— "人生的分岔路口"

```python
if sigpayload == SIGPAYLOAD_DELAY:
    # 如果是延迟模式，这样打包
    delay_block = pad_u32(delay_values, DELAY_WORDS)
    phi_one_block = [0] * PHI_WORDS
elif sigpayload == SIGPAYLOAD_PHASE:
    # 否则如果是相位模式，那样打包
    delay_block = [0] * DELAY_WORDS
    phi_one_block = pad_u32(phi_one_values, PHI_WORDS)
else:
    # 都不是？兜底方案：全部填 0
    delay_block = [0] * DELAY_WORDS
    phi_one_block = [0] * PHI_WORDS
```

想象你开车到三岔路口：
- `if`：第一条路，符合条件就走这里
- `elif`（else + if）：第一条不满足？再看第二条
- `else`：都不满足？走这条默认道

### 13. 循环 for —— "流水线工人"

```python
# 遍历列表 —— 把每个零件都加工一遍
for mode in RADAR_MODES:
    print(mode.title)

# range() —— 生成一串数字：0, 1, 2, 3, 4, 5, 6, 7
for i in range(8):
    print(f"第 {i} 次")

# enumerate() —— 给你一个"计数器"+"零件"
for idx, name in enumerate(names):
    print(f"第 {idx} 个叫 {name}")

# break —— "老板说停！"立刻退出流水线
for i in range(self.mode_combo.count()):
    if int(self.mode_combo.itemData(i)) == target:
        self.mode_combo.setCurrentIndex(i)
        break   # 找到了，不用继续找了
```

`for` 循环就像一个**流水线工人**：你给他一筐零件（列表），他会逐个取出来加工，直到筐空了为止。`enumerate` 相当于一边干活一边数"这是第几个"。

### 14. 函数 def —— "把配方写成菜谱"

```python
# 函数就是把一段"配方"封装起来，取个名字，以后随时调用
def calc_checksum(data):              # 定义：输入 data，算出一个校验值
    return sum(data) & 0xFFFF         # 返回结果

# 带默认值的参数 —— "如果顾客没说偏好，就按默认来"
def load_config(path, encoding="utf-8"):
    ...

# 调用
checksum = calc_checksum(packet_data)  # 跟订购外卖一样：喊名字，给材料，拿结果
```

函数就是**菜谱**：
- 函数名 = 菜名（`calc_checksum`）
- 参数 = 原材料（`data`）
- `return` = 出锅上菜（把计算结果交出来）

写一次，到处调用。不用每次都把步骤抄一遍。

### 15. 类 class —— "制造模具"

```python
# 类就像制造汽车的模具，实例就是按照模具造出来的一辆辆车
class RadarControlWindow(QMainWindow):   # 继承 QMainWindow 的"基因"
    """雷达 UDP 上位机主窗口。"""

    def __init__(self):                  # 初始化：给每辆"新车"装零件
        super().__init__()               # 先装父类的零件
        self.title = "雷达参数 UDP 上位机"  # self 指"当前这辆车"
        self.udp_socket = socket.socket(...)  # 装一个网络插座

# 用模具造一辆车
window = RadarControlWindow()    # 造车
window.show()                    # 开车
```

**核心概念**：
- `class` = 模具/图纸
- 实例 = 按图纸造出的实物
- `self` = "我（当前这个实例）"。每个方法里的 `self` 都是在说"我自己这辆车的属性"
- `__init__` = 出厂初始化，造车时自动执行，给车装好轮子方向盘
- `super()` = 父类，就像你继承了老爸的车厂，先继承他的产线，再加你自己的升级

### 16. import 导入 —— "去隔壁仓库拿工具"

```python
# 把整个工具箱搬过来
import json
import struct

# 只拿需要的几件工具
from pathlib import Path
from dataclasses import dataclass

# 一次拿一堆
from PySide6.QtCore import Qt, QTimer

# 东西太多？分行写，清清爽爽
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QLabel,
    QMainWindow,
)

# 给工具起个外号
import numpy as np    # 以后写 np.xxx 就行了
```

`import` 就是去别人写好的代码库（叫"模块"或"库"）里借工具。你不用重新发明轮子——别人已经造好了 `json` 解析器、`struct` 打包器，你 `import` 一下就能用。

---

## 二、中级语法

### 17. 列表推导式 —— "传送带上的自动贴标机"

```python
# 普通写法（啰嗦版）：手动逐个贴标签
results = []
for name in names:
    results.append(editor[name].value())

# 列表推导式（优雅版）：传送带自动过一遍，一行搞定
results = [editor[name].value() for name in names]

# 还能加过滤条件：只挑偶数
evens = [x for x in range(20) if x % 2 == 0]   # [0, 2, 4, ..., 18]

# 项目里的例子：一口气生成 8 个通道名
DELAY_FIELD_NAMES = [f"chan_dly{i}" for i in range(8)]
# → ["chan_dly0", "chan_dly1", "chan_dly2", ..., "chan_dly7"]
```

**列表推导式是 Python 的招牌绝活**。把它理解为一条传送带：`[加工方式 for 原料 in 原料筐]`——每个原料过一遍加工方式，成品自动收集成新列表。一行顶五行，代码瞬间清爽。

### 18. 字典推导式 —— "自动生成通讯录"

```python
# 把一堆雷达模式瞬间变成"编号→模式"的速查表
self.mode_by_type = {mode.radar_type: mode for mode in RADAR_MODES}

# 把编辑框的值统统提取出来
{name: editor.value() for name, editor in self.delay_editors.items()}
```

和列表推导式一样的思路，只是产出的是字典（通讯录）。格式：`{key: value for 原料 in 原料筐}`。

### 19. 三元表达式 —— "一句话的 if/else"

```python
# 语法：选A if 条件 else 选B
mode_name = "延迟" if sigpayload == SIGPAYLOAD_DELAY else "相位"
```

这是 Python 的"二选一"快捷键。等价于：

```python
if sigpayload == SIGPAYLOAD_DELAY:
    mode_name = "延迟"
else:
    mode_name = "相位"
```

六行变一行，适合简短的选择逻辑。但如果条件很复杂，还是老老实实用 `if/else`，别为了炫技让代码难读。

### 20. f-string 深入 —— "填空题的进阶玩法"

```python
# 花括号里不只能放变量，还能放任何表达式
f"包长：{len(packet)} 字节，期望 {PACKET_BYTES} 字节"

# 数字格式化 —— 规定显示格式
f"{byte:02X}"        # 十六进制大写，不足 2 位补零：255 → "FF"，10 → "0A"
f"{ratio:.2f}"       # 保留 2 位小数：3.14159 → "3.14"
f"{num:04d}"         # 十进制补零到 4 位：5 → "0005"
```

格式说明符的规律：`{变量:修饰符}`。`02X` = 补零到 2 位 + 十六进制大写。`:.2f` = 保留 2 位小数。记几个常用的就够了，其余的用到再查。

### 21. 切片 —— "精准切割手术刀"

```python
data = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

data[0:5]    # 切第 0~4 个 → [0, 1, 2, 3, 4]
data[:5]     # 从开头切到第 4 个 → 同上
data[5:]     # 从第 5 个切到末尾 → [5, 6, 7, 8, 9]
data[-3:]    # 切最后 3 个 → [7, 8, 9]
data[:-3]    # 扔掉最后 3 个 → [0, 1, 2, 3, 4, 5, 6]
data[::2]    # 每隔一个取一个 → [0, 2, 4, 6, 8]

# 项目里用来拆网络包：
packet[:10]                         # 包头（前 10 字节）
packet[-4:]                         # 包尾（最后 4 字节）
packet[10:-4]                       # 中间载荷（去头去尾）
```

切片的规律：`[起点:终点:步长]`。**起点算在内，终点不算**（就像"第 2 到第 5 个"不含第 5 个）。负数从末尾往前数。

### 22. 异常处理 try/except —— "安全气囊"

```python
# 把可能出错的代码放进 try 块，像给易碎品裹上泡沫纸
try:
    packet = self.current_packet()       # 尝试打包
except Exception as exc:                 # 万一炸了，别让整个程序崩掉
    self.hex_preview.setPlainText(f"预览失败：{exc}")  # 优雅地显示错误
    return                                # 然后退出来

# 捕获特定类型的异常
try:
    sent = self.udp_socket.sendto(packet, (ip, port))  # 尝试发送
except OSError as exc:                                   # 只抓网络错误
    self.append_log(f"发送失败：{exc}")
```

没有 `try/except` 的话，程序遇到错误就**原地爆炸**——直接闪退。套上 `try/except` 就像给车装了**安全气囊**：撞了不会死人，弹出错误提示，你还能继续开。

`except Exception as exc` 中的 `exc` 是"错误详情"，你可以打印出来看看到底出了什么问题。

### 23. raise 抛出异常 —— "主动按报警铃"

```python
# 不是等程序崩，而是你主动喊"停！这里不对劲！"
if len(packet) != PACKET_BYTES:
    raise RuntimeError(f"包长度不对：{len(packet)}，应该是 {PACKET_BYTES}")

if value < 0 or value > 0xFFFFFFFF:
    raise ValueError(f"{name} 必须在 0~4294967295 之间")
```

`raise` 就是工厂里的**紧急制动按钮**。当你检测到数据不合理（包长度不对、数值越界），主动拉闸，阻止错误数据继续往下流。配合上面的 `try/except` 一起用：你按铃（`raise`），上层代码接住（`except`）。

### 24. 生成器表达式 —— "现做现卖的煎饼摊"

```python
# 把每个字节转成十六进制字符串，用空格拼起来
" ".join(f"{byte:02X}" for byte in data)
```

这里 `(f"{byte:02X}" for byte in data)` 是一个**生成器表达式**——和列表推导式长得很像，但用的是圆括号 `()`。

**区别**：列表推导式是一口气把所有煎饼摊好摆桌上（占内存）；生成器表达式是**你买一个我做一个**（现做现卖，省内存）。当数据量很大时，生成器更省空间。

> 有趣的是：当生成器表达式是函数的**唯一参数**时，可以省略外层的圆括号。所以上面写成了 `join(f"...")` 而不是 `join((f"..."))`。

### 25. `*` 解包运算符 —— "拆快递"

```python
# 你有一个装满了值的列表，但函数要的是"一个一个传进来"
# * 就是把列表"拆箱"，把里面的东西一个个拿出来

values = [header, sigpayload, radar_type, frame_id, *payload_values]
packed = struct.pack("<HHHI" + "I" * 33, *values)
# *values 等价于：struct.pack(..., header, sigpayload, radar_type, frame_id, val0, val1, ..., val32)
```

`*` 就像**拆快递**：你收到一个箱子（列表），但收件人要求你把里面的东西一件件摆桌上。`*` 帮你"嘶啦"一下拆开箱子，把内容物逐个掏出来。

### 26. `if __name__ == "__main__"` —— "你是主角还是配角？"

```python
if __name__ == "__main__":
    raise SystemExit(main())
```

这是 Python 程序里最常见的"**身份验证关卡**"。理解它需要一个比喻：

- 每个 `.py` 文件既可以**自己单独运行**（当主角），也可以**被别人 import 借用**（当配角）。
- 当文件是**主角**（被直接运行）时，`__name__` 会自动变成 `"__main__"`。
- 当文件是**配角**（被别人 import）时，`__name__` 会变成这个文件的名字。

所以这段代码的意思是：**"如果我是主角，就开演；如果只是被借来跑龙套的，就别抢戏。"** 这防止了 `import` 时不小心触发全盘代码。

### 27. `dict.get()` 带默认值 —— "找不到也不慌"

```python
# 危险查法：键不存在直接炸
ip = cfg["ip"]

# 安全查法：找不到就给你个备用的
ip = str(cfg.get("ip", "192.168.10.10"))
port = int(cfg.get("port", 9001))
auto = bool(cfg.get("auto_frame", True))
```

就像你去前台查一个访客：直接查（`[]`），如果访客没登记，前台会慌张崩溃。用 `.get()` 查，前台会说"这个访客没登记哦，不过我可以帮你登记为 `127.0.0.1`"。

**项目里大量用 `.get()`** 来加载配置文件——配置文件里可能缺字段，你不能因为少了一项就让整个程序崩掉。

### 28. `del` 删除 —— "撕掉标签"

```python
del attr_name   # 这个变量我不要了，回收！
```

Python 里 `del` 不是删除那个值本身，而是**撕掉变量名和值之间的"标签"**。如果这个值没有别的标签了，Python 的垃圾回收工会默默把它收走。

项目里用 `del attr_name` 标记"这个参数只是为了让代码好读，实际上用不到"。

### 29. `pathlib.Path` —— "文件路径万能遥控器"

```python
from pathlib import Path

# 看当前在哪
here = Path.cwd()                          # → 当前目录的绝对路径

# 拼接路径 —— 用 / 号！就像在浏览器地址栏打字
config_path = Path.cwd() / "radar_udp_config.json"

# 读写文件，一行搞定
Path("config.json").write_text(content, encoding="utf-8")
data = Path("config.json").read_text(encoding="utf-8")
```

`pathlib` 是 Python 处理文件路径的**现代做法**。最大的亮点是**用 `/` 拼接路径**——就像你在文件夹里一层层点进去，比老式的 `os.path.join(a, b, c)` 直观太多。

`write_text` 和 `read_text` 一行就完成读写，不用手动 `open()` → 读写 → `close()`。

### 30. `json` 序列化 —— "把字典装进信封，寄出去再拆开"

```python
import json

# 字典 → JSON 字符串（打包寄出）
json.dumps(data, ensure_ascii=False, indent=2)
# ensure_ascii=False：中文别转成 \uXXXX，保持原样
# indent=2：2 空格缩进，不然全挤在一行根本没法看

# JSON 字符串 → 字典（收信拆开）
cfg = json.loads(text)
```

JSON 是通行全世界的"数据信封格式"。你的 Python 字典（`dict`）只能在 Python 里用，但把它 `dumps` 成 JSON 字符串后，任何语言都能读。保存配置文件、前后端通信、导出数据，全用这个。

项目里用 `json` 来**保存/加载用户配置**——把界面上的所有参数打包成 JSON 文件存到硬盘，下次打开时恢复。

### 31. `struct` —— "Python 数字 ↔ 二进制字节流的翻译官"

```python
import struct

# 打包：把 Python 数字装进二进制字节（准备发出去）
packed = struct.pack("<HHHI", 0x55AA, 0, 1, 7)
# < = 小端字节序（低位在前，x86 CPU 的"母语"）
# H = unsigned short（2 字节）
# I = unsigned int（4 字节）

# 解包：把收到的二进制字节还原成 Python 数字
header, sigpayload, radar_type, frame_id = struct.unpack("<HHHI", packet[:10])
```

这是网络编程的核心：在电缆上跑的是**字节流**（010101...），但 Python 里你操作的是 **int 数字**。`struct` 就是中间的翻译官——"把数字变成字节"叫打包（pack），"把字节变成数字"叫解包（unpack）。

格式字符串 `"<HHHI"` 相当于告诉翻译官："后面这四个东西，小端序，前三个是 2 字节的，最后一个是 4 字节的。"就像你给快递员一张货单："第一箱是 H 规格，第二箱也是 H，第三箱 I 规格。"

---

## 三、高级语法

### 32. 类型注解（Type Hints）—— "给变量贴上'型号标签'"

```python
# 变量类型注解：声明"这个变量的型号是..."
self.mode_editors: dict[int, dict[str, UInt32Edit]] = {}

# 参数类型注解：声明"这个函数收什么型号的零件，产出什么型号的成品"
def build_packet(
    sigpayload: int,          # 收 int 型
    radar_type: int,
    frame_id: int,
    delay_values: list[int],  # 收 int 列表
) -> bytes:                   # 产出 bytes 型
    ...

def get_delay_values(self) -> list[int]:
    ...
```

类型注解就像在零件上贴的**型号标签**。重点：**Python 不会强制执行这些标签**——你贴了 `int` 的标签但塞了个 `str` 进去，Python 照样运行。但你的 IDE（比如 VS Code、PyCharm）会利用这些标签给你自动补全、提前标红错误——就像导航地图上的限速提醒，没人拦着你超速，但提醒本身就很有用。

### 33. `from __future__ import annotations` —— "提前使用下一代功能"

```python
from __future__ import annotations
```

这行代码的意思是：**"我现在就想用未来版本 Python 的类型注解方式"**。放在文件最顶部（仅在编码声明之后），它让你可以用更新潮的写法（比如 `list[int]` 而不是 `List[int]`），并且性能更好。Python 3.10+ 推荐加这行。

### 34. Union 类型（`|` 语法）—— "或者"

```python
# 老写法（啰嗦）
from typing import Union
def __init__(self, name: str, parent: Union[QWidget, None]) -> None: ...

# 新写法（Python 3.10+，简洁）
def __init__(self, name: str, parent: QWidget | None = None) -> None: ...
```

`QWidget | None` 读作"QWidget 或者 None"——这个参数你可以传一个窗口控件进来，也可以什么都不传（`None`）。就像快递单上的"手机号或座机号，选填"。

### 35. `Callable` 类型 —— "我需要的是一段'操作步骤'"

```python
from collections.abc import Callable

def build_u32_grid_box(
    title: str,
    names: list[str],
    on_change: Callable[[], None],   # 👈 我需要一个"无参数、无返回值"的操作
) -> tuple[QGroupBox, dict[str, UInt32Edit]]:
```

`Callable[[参数类型], 返回值类型]` 就是在说："这个参数不要数据，要一个**函数**（一段操作步骤）。到时候我会调它。"

`Callable[[], None]` = "一个不需要输入、也不产出结果的函数"。项目里它就是 `self.refresh_preview`——用户改了输入框，调用方就帮你刷新预览，至于具体怎么刷新的，调用方不关心。

### 36. 变长元组类型 —— "一堆同型号零件，不知道几个"

```python
@dataclass(frozen=True)
class RadarMode:
    radar_type: int
    title: str
    fields: tuple[str, ...]    # 👈 元素全是 str，但不确定有几个
```

`tuple[str, ...]` 表示：都是字符串，但数量不固定。区别于 `tuple[str, str, str]`（恰好 3 个，不多不少）。项目里每种雷达模式的参数字段数量不同，用这个表示再合适不过。

### 37. 位运算 —— "操作二进制位的显微手术"

```python
# 按位与 & —— "只保留我想要的那几位"
checksum = sum(data) & 0xFFFF        # 0xFFFF = 16 个 1 → 只要低 16 位
truncated = int(value) & 0xFFFFFFFF   # 0xFFFFFFFF = 32 个 1 → 只要低 32 位

# 其他位运算符
a & b    # 按位与：两位都是 1 才是 1
a | b    # 按位或：任一位是 1 就是 1
a ^ b    # 按位异或：两位不一样才是 1
~a       # 按位取反：0 变 1，1 变 0
a << 2   # 左移：整体往左挪 2 位（末尾补 0，相当于 ×4）
a >> 2   # 右移：整体往右挪 2 位（相当于 ÷4）
```

**为什么项目里用这个？** 网络协议规定校验和只取低 16 位，你就用 `& 0xFFFF` 把多余的高位"咔嚓"截掉。就像用剪刀把照片多余的边缘裁掉——只保留协议要求的那一部分。`0xFFFF` 就是一个"16 位全 1"的裁剪刀模板。

### 38. `@dataclass` —— "自动写代码的机器人助手"

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class RadarMode:
    """雷达模式定义。"""
    radar_type: int
    title: str
    fields: tuple[str, ...]
```

这是 Python 里最实用的"**偷懒神器**"。正常情况下，定义一个存数据的类要手写 `__init__`（初始化函数）、`__repr__`（打印函数）、`__eq__`（比较函数）…… 冗长又枯燥。

而一旦戴上 `@dataclass` 这顶帽子，你只需要**声明有哪些字段**，Python 就在后台自动帮你把那些啰嗦代码全部生成好。代码量缩水 80%，清爽到不像话。

`frozen=True` 是这顶帽子的一个"加强配件"：它把数据**冻住**——创建之后就不能修改了。就像 C 语言里的 `const`，或者银行存折——存进去就不能涂改，保证数据安全。

> 在 `@` 符号见第一节最后的解释：它叫**装饰器**，相当于把类开进"改装厂"，自动加装功能。

### 39. `@classmethod` —— "属于整个公司，不属于某个员工"

```python
class MainWindowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        """整个测试类跑之前，做一次全局准备。"""
        cls.app = QApplication.instance() or QApplication([])
```

- 普通方法（`def method(self)`）：属于**某个实例**（某个员工自己的事情）
- 类方法（`@classmethod`，`def method(cls)`）：属于**整个类**（整个公司的事情，不管哪个员工都可以调用）

项目里用它做**一次性全局初始化**：测试类里有很多测试用例，但 `QApplication` 只需要创建一个，所以用 `@classmethod` 在类级别创建一次，全部测试用例共享。

`cls` 就是"类本身"的意思，和 `self`（实例本身）是同一个道理。

### 40. 运算符重载 —— "让 `/` 变成'路径拼接'"

```python
# Path 重载了 / 运算符：不是做除法，而是拼路径
config_path = Path.cwd() / "project" / "config.json"
# → Path("当前目录/project/config.json")

# 列表的 + 和 * 也是运算符重载
combined = [1, 2] + [3, 4]    # + = 拼接
repeated = [0] * 8             # * = 重复
```

Python 允许**自定义运算符的行为**。`Path` 类把 `/` 重新定义为"路径拼接"，所以你写 `a / b` 就像在文件夹里逐层点进去。同理，列表的 `+` 是拼接，`*` 是重复。这叫"运算符重载"——同一把刀，在不同的案板上切不同的菜。

### 41. Qt 信号/槽 —— "办公室的内部电话系统"

```python
# 信号（signal）= 事件发生 → 自动拨号给对应的人
self.send_button.clicked.connect(self.send_current_packet)
self.loop_button.toggled.connect(self.toggle_loop_send)
self.send_timer.timeout.connect(self.send_current_packet)
self.ip_edit.textChanged.connect(self.refresh_preview)
```

这是 Qt 框架最核心的通信方式。把它想象成办公室里的**内部电话系统**：

- **信号** = 某个事件发生（有人按了按钮、文本被改了、计时器到点了）→ 相当于"电话响了"
- **槽** = 接到电话后具体做什么 → 相当于"接电话的人"
- `connect` = 把某个电话线路接通 → "你办公室的铃响了就打到我这来"

这样你不需要写"一直盯着按钮看它有没有被点"的死循环——Qt 帮你盯，有事件了自动呼叫。

### 42. `or` 短路求值 —— "有现成的就用，没有就造一个"

```python
cls.app = QApplication.instance() or QApplication([])
```

这行代码的意思是：**"先看有没有已经存在的 QApplication 实例？有就直接拿来用；没有（返回 None）就新建一个。"**

等价于：
```python
existing = QApplication.instance()
if existing is None:
    cls.app = QApplication([])
else:
    cls.app = existing
```

五行变成一个表达式。"短路"的意思是：如果 `or` 左边已经是"真"的了，右边就不执行了——就像你已经找到车位了，就不需要继续绕圈。

### 43. 下划线前缀参数 —— "假装没看见，但得留着"

```python
def on_payload_mode_changed(self, _index: int | None = None) -> None:
```

参数名前加一个下划线 `_index`，是 Python 社区的暗号：**"这个参数我当前用不到，但因为某些原因（比如信号槽签名要求），我必须接收它。"** 下划线告诉读代码的人："别看它，它就是个占座的。"

---

## 四、速查对照表

| 类别 | 语法 | 画线比喻 |
|------|------|----------|
| 基础 | `#` | 写给自己看的小纸条 |
| 基础 | `= + - * / // % **` | 计算器按钮 |
| 基础 | `== != < > <= >=` | 判断题 |
| 基础 | `and or not` | "并且""或者""不是" |
| 基础 | `[]` | 带编号的收纳抽屉 |
| 基础 | `()` | 封了胶带的收纳盒 |
| 基础 | `{}` | 手机通讯录 |
| 基础 | `f"{x}"` | 填空题模板 |
| 基础 | `if/elif/else` | 三岔路口 |
| 基础 | `for ... in` | 流水线工人 |
| 基础 | `def` `return` | 菜谱配方 |
| 基础 | `class` `self` | 汽车模具 |
| 基础 | `import` | 去隔壁仓库借工具 |
| 中级 | `[x for x in list]` | 传送带自动贴标 |
| 中级 | `{k: v for ...}` | 自动生成通讯录 |
| 中级 | `x if cond else y` | 二选一快捷键 |
| 中级 | `list[start:stop]` | 精准切割手术刀 |
| 中级 | `try/except` | 安全气囊 |
| 中级 | `raise` | 紧急制动按钮 |
| 中级 | `*args` | 拆快递 |
| 中级 | `a, b = tuple` | 一把倒出来 |
| 中级 | `dict.get(key, default)` | 找不到也不慌 |
| 中级 | `__name__ == "__main__"` | 主角还是配角？ |
| 中级 | `Path / "file"` | 路径遥控器 |
| 中级 | `json.dumps/loads` | 装信封寄出去 |
| 中级 | `struct.pack/unpack` | 数字↔字节翻译官 |
| 高级 | `x: int` `-> int` | 型号标签 |
| 高级 | `from __future__ import` | 提前用下一代功能 |
| 高级 | `X | None` | "或者" |
| 高级 | `Callable[[], None]` | "一段操作步骤" |
| 高级 | `tuple[str, ...]` | 一堆同型号，数量不定 |
| 高级 | `&` `|` `^` `<<` `>>` | 二进制显微手术 |
| 高级 | `@dataclass` | 自动写代码的机器人 |
| 高级 | `@classmethod` | 属于公司，不属于员工 |
| 高级 | `super().__init__()` | 继承老爸的产线 |
| 高级 | `signal.connect(slot)` | 办公室内部电话 |
| 高级 | `a or b` | 有现成的就用 |

---

## 五、从项目学语法的建议

如果你是 Python 小白，建议按以下顺序边看代码边学：

1. **先看** `radar_modes.py` —— 只有数据定义，用到了 `=`、`class`、`@dataclass`，最温柔的开局
2. **再看** `styles.py` —— 就是一个巨大的字符串，零压力
3. **再看** `udp_protocol.py` —— 学函数、`if/elif/else`、位运算、`struct` 打包
4. **再看** `ui_components.py` —— 学类、类型注解、Qt 信号槽、`for` 循环
5. **再看** `main.py` —— 程序的"总开关"，不到 30 行
6. **最后看** `main_window.py` —— 主窗口大本营，前面学的全用上了
7. **测试文件** `test_main_window.py` 和 `test_udp_protocol.py` —— 学 `unittest`，看别人怎么写"验证代码"

遇到不认识的语法，回来翻本文的**速查对照表**，看"画线比喻"那列，一秒回忆起来。
