---
tags:
  - 数字IC
  - 验证
  - VCS
  - Verdi
  - 仿真
created: 2026-08-07
---

# VCS 与 Verdi 仿真指南

> VCS 编译仿真 + Verdi 看波形调试，是数字 IC 验证的**标配工具链**（工业界事实标准）。本篇讲清**基本原理 → filelist → testbench 波形代码 → Makefile（含 clean）→ 完整小例子 → 常用选项 → Verdi 操作 → 踩坑**。前置见 [[数字IC/数字芯片设计与验证概述.md|数字芯片设计与验证概述]]、[[数字IC/SystemVerilog核心特性.md|SystemVerilog 核心特性]]。

---

## 一、是什么 & 为什么用

| 工具 | 全称 | 作用 |
|------|------|------|
| **VCS** | Synopsys VCS | 商业 **Verilog/SystemVerilog 仿真器**，把 RTL + TB 编译成可执行文件再运行，工业界事实标准 |
| **Verdi** | Synopsys Verdi | **调试工具**：看波形（nWave）、源码、状态机、反推信号来源；配合 VCS 使用 |
| **fsdb** | Fast Signal Database | Verdi 的波形格式，**压缩小、只记录信号变化**，比标准 VCD 高效得多 |

**一句话流程**：

```
写 RTL + testbench → VCS 编译（生成 simv）→ 跑仿真（生成 .fsdb 波形）
→ Verdi 打开波形/源码 → 定位 bug → 改代码 → 重编重跑
```

---

## 二、仿真基本原理

### 2.1 编译 + 运行两步

VCS 不是"解释执行"，而是：

1. **编译**：`vcs ...` 把 Verilog/SV 代码 + 时间模型翻译成 C++，再编成**可执行文件 simv**。
2. **运行**：`./simv` 执行仿真，**事件驱动**——仿真器维护一个事件队列，按"当前时刻"取出事件处理，产生新事件排到未来时刻，直到没有事件或遇到 `$finish`。

### 2.2 时间单位：timescale

```verilog
`timescale 1ns/1ps   // 时间单位/精度
```
- 前一个数 = 时间单位（`#10` 表示 10 个时间单位），后一个 = 仿真精度（最小时间粒度）。
- **单位不匹配**是仿真和实际时序对不上的常见原因，建议全工程统一。

### 2.3 波形格式对比

| | fsdb | vcd |
|---|---|---|
| 工具 | Verdi 原生 | 通用标准 |
| 体积 | 小（仅记录变化，压缩） | 巨大（记录全部） |
| 生成 | `$fsdbDump*` | `$dumpvars` |
| 用途 | 调试首选 | 通用交换 |

---

## 三、filelist（文件列表）

**为什么用**：仿真文件一多，手敲命令太长。把**按编译顺序**列好的文件写进一个 `.f` 文件，用 `-f filelist.f` 引用。

### filelist.f 示例

```
+incdir+./rtl            # include 目录（可多个 +incdir+）
+incdir+./tb
+define+WIDTH=8          # 定义宏

./rtl/adder.v            # RTL 文件，先放被例化的底层
./rtl/sub.v
./tb/tb_adder.v          # testbench 最后放
```

**要点**：
- 文件**顺序**重要：被 `include`/例化的模块一般先列出（VCS 大多能自动解析，但规范上按层次顺序更稳）。
- 用 `+incdir+` 而不是在代码里写绝对路径；用 `+define+` 传宏，不要在 RTL 里改。
- `-f` 里还可以再 `-f` 嵌套子文件列表。

---

## 四、testbench 文件中需要添加（波形相关）

**这是 Verdi 能出波形的关键**——TB 里必须有这几行：

```verilog
`timescale 1ns/1ps

module tb_adder;
    // ... 信号定义、例化 DUT ...

    // ★★★ 生成 fsdb 波形（Verdi 专用）★★★
    initial begin
        $fsdbDumpfile("wave.fsdb");   // ① 指定波形文件名
        $fsdbDumpvars(0, tb_adder);    // ② 记录波形：参数1=深度0(全层次)，参数2=起点模块tb_adder
    end

    // 激励
    initial begin
        // ... 施加激励 ...
    end

    // 结束仿真
    initial begin
        #1000;
        $finish;
    end
endmodule
```

| 语句 | 含义 | 备注 |
|------|------|------|
| `$fsdbDumpfile("wave.fsdb")` | 指定波形文件名 | 不写默认 `novas.fsdb` |
| `$fsdbDumpvars(0, tb_adder)` | 从 tb_adder 开始，dump 全部层次 | 最常用 |
| `$fsdbDumpvars(0)` | 从当前模块开始 dump 全部层次 | 简单粗暴 |

**`$fsdbDumpvars(level, instance)` 两个参数逐个解释**：

```text
$fsdbDumpvars(  深度  ,  起点模块  )
               ↑          ↑
             参数1       参数2
```

| 参数 | 含义 | 例子 |
|------|------|------|
| **参数1：深度 level** | 从起点往下记录**多少层** | `0` = 一路到底（所有子模块全记录）；`2` = 只记录往下 2 层 |
| **参数2：起点 instance**（可省略） | 从**哪个模块**开始记录 | `tb_adder` = 整个测试平台；`u_dut` = 只记录被测模块内部 |

**为什么写 `tb_adder`**：tb 是顶层，里面例化了被测模块 DUT（这里是 `u_dut`）。"从 tb_adder 开始全层次记录" = testbench + DUT 内部**所有信号**都进波形。

**常见变体**：
- `$fsdbDumpvars(0)` —— 不写起点，默认从**当前所在模块**开始（若在 tb 里写，效果同 `tb_adder`）。
- `$fsdbDumpvars(0, u_dut)` —— **只记录 DUT 内部**，不要 TB 的辅助信号（波形更小、更聚焦）。
- `$fsdbDumpvars(2, tb_adder)` —— 只记录往下 2 层（省空间，但内部深层次信号没有）。
| `$finish` | 结束仿真 | 不结束则仿真"跑不完"、波形写不完整 |

> 若用标准 VCD：`$dumpfile("wave.vcd"); $dumpvars;`——但 VCD 巨大，Verdi 调试优先 fsdb。

---

## 五、Makefile 基础（初学者必读）

### 5.1 基本语法

Makefile 就是"**告诉 make 怎么一步步干活**"的脚本。核心只有一条规则：

```makefile
目标: 依赖
	命令        # ← 命令前面必须是一个 Tab（制表符），不是空格！
```

**三要素**：

| 要素 | 作用 | 例子 |
|------|------|------|
| **目标 target** | 要生成的东西 / 动作名 | `simv`、`clean`、`sim` |
| **依赖 prerequisites** | 做这件事前必须已存在的东西（文件或其他目标） | `sim: compile` 表示先做 compile |
| **命令 recipe** | 真正执行的 shell 命令 | `./simv`、`rm -rf ...` |

**四个必懂知识点**：

**① Tab 缩进（最易踩的坑）**：命令必须以 **Tab** 开头，用空格会报错：
```
Makefile:3: *** missing separator. Stop.
```

**② 执行规则**：
- `make` 默认执行**第一个目标**。
- 目标比依赖**旧**（依赖更新了）→ 重新执行命令。
- 若目标对应一个**文件**且已存在、依赖没变 → **什么都不做**（这就是增量编译的原理）。

**③ 变量**：
```makefile
VCS = vcs          # 定义，用 $(VCS) 引用
CMP = -sverilog    # 字符串可以很长，多行用 \ 续行
```
- `=` 递归展开（用到时才展开）；`:=` 立即展开；`+=` 追加；`?=` 未定义才赋值。
- 自动变量（最常用）：`$@` = 当前目标名，`$<` = 第一个依赖，`$^` = 所有依赖。

**④ .PHONY 伪目标**：声明某目标**不是文件**（如 `clean`），否则若目录里碰巧有个叫 `clean` 的文件，`make clean` 就会误以为"已经最新"而不执行：
```makefile
.PHONY: clean
```

### 5.2 VCS 仿真 Makefile 实例（逐行讲解）

```makefile
# ========== 1. 变量定义区（方便统一改） ==========
VCS      = vcs              # 仿真器命令
VERDI    = verdi            # 调试工具命令
FILELIST = filelist.f       # 源文件列表
TOP      = tb_adder         # 顶层模块名（Verdi 打开用）
SIMV     = simv             # 编译输出的可执行文件名
DUMP     = wave.fsdb        # 波形文件名

# 编译选项：-f 读文件列表，-o 指定输出名
CMP_OPT  = -sverilog -debug_access+all -timescale=1ns/1ps -f $(FILELIST) -o $(SIMV)

# ========== 2. 伪目标声明 ==========
.PHONY: all compile sim wave clean

# ========== 3. 规则 ==========
# make（或 make all）：先编译，再仿真
all: compile sim

# 目标 compile：没有依赖，执行编译命令
compile:
	$(VCS) $(CMP_OPT) -l compile.log    # vcs ... -o simv

# 目标 sim：依赖 compile（先编译），再跑仿真生成波形
sim: compile
	./$(SIMV) -l sim.log

# 目标 wave：依赖 sim（先跑出 fsdb），再开 Verdi 看波形
wave: sim
	$(VERDI) -sv -f $(FILELIST) -top $(TOP) -ssf $(DUMP) &

# ★★★ 清理指令：删除编译/仿真所有产物 ★★★
clean:
	rm -rf $(SIMV) simv.daidir simv.db csrc \
	       *.log *.fsdb *.vpd *.vcd \
	       verdiLog novas.rc .vcsmx_rebuild
```

**日常用法**：

| 命令 | 执行内容 |
|------|----------|
| `make` 或 `make all` | 编译 → 仿真（最常用） |
| `make compile` | 只编译，不跑仿真 |
| `make sim` | 先编译（若需要）再仿真 |
| `make wave` | 编译 → 仿真 → 打开 Verdi |
| `make clean` | **清掉所有产物**（重编/提交前必用） |

### 5.3 为什么 clean 很重要

- VCS 编译会生成 `simv.daidir`、`csrc` 等中间目录，**不清干净就重编**会报"仿真器/文件冲突"或结果不更新。
- 波形、日志是垃圾大户，提交代码前必须清。
- 养成习惯：**改代码前 `make clean`**，避免旧产物干扰。
- 面试小问："Makefile 里 clean 的作用？" → 删掉编译/仿真中间产物，保证 `make` 从干净状态重新编译，避免增量编译用了过期文件。

---

## 六、完整工作流小例子

### 目录结构

```
proj/
├── rtl/
│   └── adder.v
├── tb/
│   └── tb_adder.v
├── filelist.f
└── Makefile
```

### rtl/adder.v（8 位加法器）

```verilog
module adder #(parameter W = 8)(
    input  [W-1:0] a, b,
    output [W-1:0] sum
);
    assign sum = a + b;
endmodule
```

### tb/tb_adder.v

```verilog
`timescale 1ns/1ps
module tb_adder;
    reg  [7:0] a, b;
    wire [7:0] sum;
    integer errors = 0;

    adder u_dut(.a(a), .b(b), .sum(sum));

    initial begin
        $fsdbDumpfile("wave.fsdb");
        $fsdbDumpvars(0, tb_adder);
    end

    initial begin
        a = 8'd0; b = 8'd0;
        repeat (10) begin
            #10;
            a = $random; b = $random;
            #10;
            if (sum !== a + b) begin
                $display("FAIL: %0d+%0d=%0d", a, b, sum);
                errors = errors + 1;
            end
        end
        $display("Test %0s, errors=%0d", errors ? "FAIL" : "PASS", errors);
        #10;
        $finish;
    end
endmodule
```

### 命令步骤

```bash
make compile          # vcs -sverilog -debug_access+all ... -o simv
make sim              # ./simv -> 生成 wave.fsdb + sim.log
make wave             # verdi 打开波形（后台）
make clean            # 清掉 simv/波形/日志，准备重编或提交
```

---

## 七、VCS 常用选项速查

| 选项 | 作用 |
|------|------|
| `-sverilog` | 支持 SystemVerilog |
| `+v2k` | 支持 Verilog-2001 |
| `-f filelist.f` | 读文件列表 |
| `+incdir+./dir` | 加 include 目录 |
| `+define+NAME` | 定义宏 |
| `-timescale=1ns/1ps` | 全局时间单位/精度 |
| `-o simv` | 指定输出可执行文件名 |
| `-l compile.log` | 编译日志 |
| `-debug_access+all` | **开调试信息（Verdi 必需）** |
| `-kdb` | 生成高级调试数据库（配 Verdi 查状态机/信号），常与上面同用 |
| `-f` 嵌套 | 文件列表套文件列表 |
| 仿真 `./simv` | 加 `-l sim.log` 记日志 |

> **Verdi 配合重点**：编译必须带 `-debug_access+all`（老版本写 `-debug_pp`），否则 Verdi 打开**看不到内部信号**。要查 RTL 状态机/寄存器需再加 `-kdb`。

---

## 八、Verdi 常用操作

### 打开

```bash
# 编译后开源码 + 波形
verdi -sv -f filelist.f -top tb_adder -ssf wave.fsdb &
```

### nWave 波形窗口常用

| 操作 | 效果 |
|------|------|
| 拖信号进来 | 添加信号波形 |
| `z` / `shift+z` | 缩小 / 放大 |
| `f` | 全屏显示所有波形 |
| `c` | 居中到光标 |
| 左键 | 加标尺/测量两点间隔 |
| `h` | 信号高亮 |

### 源码窗口

- 点信号 → 右键 → **Trace**，可反推这个信号由谁驱动（**反推 debug** 是 Verdi 最大价值）。
- 波形上双击信号 → 跳到源码赋值处。

---

## 九、常见问题排查

| 现象 | 原因 / 解决 |
|------|-------------|
| **没生成 .fsdb** | TB 里忘写 `$fsdbDumpfile/$fsdbDumpvars`，或 `$finish` 前仿真被打断 |
| **Verdi 打开看不到内部信号** | 编译缺 `-debug_access+all`（或 `-kdb`） |
| **timescale 警告/时序不对** | 代码没 `\`timescale`，或全局用 `-timescale=` 统一 |
| **重复编译报错（simv 已存在/daidir）** | 没 `make clean`，旧的编译产物冲突 |
| **波形只有顶层没内部** | `$fsdbDumpvars(0, tb)` 的 0 丢了，默认只 dump 顶层 |
| **仿真一直"跑不完"** | 没 `$finish`，事件队列永不为空 |
| **结果与预期不符** | 检查单位、阻塞/非阻塞、`#` 延时位置 |

---

## 相关笔记

- [[数字IC/数字芯片设计与验证概述.md|数字芯片设计与验证概述]] —— 验证流程与工具栈
- [[数字IC/SystemVerilog核心特性.md|SystemVerilog 核心特性]] —— 仿真调度、断言、覆盖率
- [[数字IC/UVM验证方法学入门.md|UVM 验证方法学入门]] —— 大规模验证环境
- [[数字IC/Verilog HDL核心语法与建模.md|Verilog HDL 核心语法与建模]]
