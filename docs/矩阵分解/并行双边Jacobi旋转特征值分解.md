# 基于FPGA的并行双边Jacobi旋转的矩阵特征值分解

> 本章整理自《基于FPGA的阵列信号处理算法中关键矩阵算子的高性能实现研究》（闫迪，长安大学，2024）第二章

## 2.1 问题描述

矩阵特征值分解（EVD）是阵列信号处理中的核心数学工具。实际工程中常用两种算法：QR 算法和 Jacobi 旋转算法。由于 Jacobi 算法比 QR 算法更精确、数值稳定性更好，且具有先天的高度并行性，本章选择以双边 Jacobi 旋转算法为基础进行 FPGA 高性能实现。

当前基于 Jacobi 旋转的硬件实现方案存在以下不足：

- 主要基于 CORDIC（坐标旋转数字计算）的定点运算，精度较低
- 依赖 BLV（Brent-Luk-Van）脉动阵列，需将矩阵分块为多个 $2 \times 2$ 子矩阵，Jacobi 因子传递和数据交换使并行性和效率受限
- 一次 Jacobi 旋转需执行三次 CORDIC 计算周期（一次矢量模式 + 两次旋转模式），时延较大

本章提出了一种充分利用旋转矩阵稀疏特性的并行双边 Jacobi 旋转新方法，核心思路：使用 FPGA 乘法器进行单精度浮点运算，通过行式读取方式提高并行处理灵活性。

## 2.2 并行双边 Jacobi 旋转新方法

### 2.2.1 双边 Jacobi 旋转算法

设 $\mathbf{B} \in \mathbb{R}^{N \times N}$ 为实对称矩阵，双边 Jacobi 旋转算法通过一系列平面旋转矩阵 $\mathbf{U}$ 将其对角化：

$$
\mathbf{B}_{i+1} = \mathbf{U}^T \mathbf{B}_i \mathbf{U} \tag{2.2}
$$

其中：
- $\mathbf{B}_1 = \mathbf{B}$：原始实对称矩阵
- $[\cdot]^T$：矩阵转置
- $\mathbf{U}$：Jacobi 旋转矩阵
- $S$（$1 \leq i \leq S$）：扫描次数

旋转矩阵 $\mathbf{U}$ 是一类特殊的稀疏矩阵，行、列向量中只有两个非零元素：

$$
\mathbf{U} = \begin{pmatrix}
1 & \dots & 0 & \dots & 0 & \dots & 0 \\
\vdots & \ddots & \vdots & & \vdots & & \vdots \\
0 & \dots & c_{p,p} & \dots & s_{p,q} & \dots & 0 \\
\vdots & & \vdots & \ddots & \vdots & & \vdots \\
0 & \dots & s_{q,p} & \dots & c_{q,q} & \dots & 0 \\
\vdots & & \vdots & & \vdots & \ddots & \vdots \\
0 & \dots & 0 & \dots & 0 & \dots & 1
\end{pmatrix} \tag{2.3}
$$

其中 Jacobi 旋转因子为：

$$
c_{p,p} = \cos\theta = c, \quad s_{p,q} = \sin\theta = s, \quad s_{q,p} = -\sin\theta = -s, \quad c_{q,q} = \cos\theta = c \tag{2.4, 2.5}
$$

旋转因子的计算涉及三角函数：

$$
c = 1 / \sqrt{1 + t^2}, \quad s = t \times c \tag{2.7a, 2.7b}
$$

$$
t = \tan\theta = \frac{\operatorname{sign}(\tau)}{|\tau| + \sqrt{1 + \tau^2}}, \quad \tau = \cot 2\theta = \frac{b_{p,p} - b_{q,q}}{2b_{p,q}} \tag{2.7c, 2.7d}
$$

#### 符号说明

- $b_{p,p}, b_{q,q}, b_{p,q}$：矩阵 $\mathbf{B}$ 中的三个元素
- $\theta$：Jacobi 旋转角度
- CORDIC 将三角函数转换为移位运算，通过不断逼近旋转角度实现：$x_{i+1} = x_i - y_i d_i 2^{-i}$，$y_{i+1} = y_i - y_i d_i 2^{-i}$，$z_{i+1} = z_i - d_i \arctan 2^{-i}$

当前主流的 BLV 脉动阵列结构包含对角处理器（计算 Jacobi 旋转因子）和非对角处理器（完成 $2\times 2$ 子矩阵的平面旋转），通过矩阵数据交换和多次迭代完成特征值分解。

![](../kb_material/基于FPGA的阵列信号处理算法中关键矩阵算子的高性能实现研究_闫迪.pdf-0744ff48-8b86-4f31-af9c-38c0ad8d1d4d/images/5e58b754c78696d6023b92c103d48570c20e1029b1a42b3adca8b39cbf02b681.jpg)

**图2.1 改进的BLV脉动阵列结构（$N = 6$）**

### 2.2.2 稀疏旋转矩阵的乘法

新方法的核心思想是利用旋转矩阵 $\mathbf{U}$ 行、列向量仅含两个非零元素的稀疏特性，简化矩阵乘法运算。

**矩阵左乘**：$\mathbf{U}^T$ 的第一行向量乘以 $\mathbf{B}$，等效于仅用非零元素 $c_1$、$s_1$ 乘以对应行向量：

$$
c_1 \times [b_1\ b_2\ b_3\ b_4\ b_5\ b_6] + s_1 \times [b_2\ b_7\ b_8\ b_9\ b_{10}\ b_{11}]
$$

**矩阵右乘**：类似地，$\mathbf{B}$ 右乘 $\mathbf{U}$ 的列向量也仅需非零元素参与计算。

新方法可同时执行多个 Jacobi 旋转因子的平面旋转，无需矩阵分块和 Jacobi 因子传递。特征向量通过迭代累积旋转矩阵得到：

$$
\mathbf{U} = \mathbf{U}_S \times \mathbf{U}_{S-1} \times \dots \times \mathbf{U}_2 \times \mathbf{U}_1 \tag{2.14}
$$

### 2.2.3 复厄米特矩阵特征值分解新方法

经典双边 Jacobi 算法仅适用于实对称矩阵，而实际工程中经常遇到的协方差矩阵实则是复厄米特矩阵。为此，本节给出了一种可基于双边 Jacobi 旋转处理复厄米特矩阵的特征值分解新方法。

设 $\mathbf{B} \in \mathbb{C}^{N \times N}$ 是一个复厄米特矩阵，其特征值分解表示为：

$$
\mathbf{B}\mathbf{V} = \lambda\mathbf{V}
= \left(\mathbf{B}_{real} + j\mathbf{B}_{imag}\right)\left(\mathbf{V}_{real} + j\mathbf{V}_{imag}\right)
= \lambda\left(\mathbf{V}_{real} + j\mathbf{V}_{imag}\right) \tag{2.15}
$$

其中 $\lambda$ 和 $\mathbf{V}$ 分别是 $\mathbf{B}$ 的一个特征值和对应的特征向量，$[\cdot]_{real}$ 和 $[\cdot]_{imag}$ 分别表示复厄米特矩阵的实部和虚部。

将式（2.15）写成块矩阵形式：

$$
\begin{bmatrix}
\mathbf{B}_{real} & \mathbf{B}_{imag}^T \\
\mathbf{B}_{imag} & \mathbf{B}_{real}
\end{bmatrix}
\begin{bmatrix}
\mathbf{V}_{real} \\
\mathbf{V}_{imag}
\end{bmatrix}
=
\begin{bmatrix}
\mathbf{B}_{real} & -\mathbf{B}_{imag} \\
\mathbf{B}_{imag} & \mathbf{B}_{real}
\end{bmatrix}
\begin{bmatrix}
\mathbf{V}_{real} \\
\mathbf{V}_{imag}
\end{bmatrix}
=
\lambda
\begin{bmatrix}
\mathbf{V}_{real} \\
\mathbf{V}_{imag}
\end{bmatrix} \tag{2.16a}
$$

由此定义变形后的实矩阵形式：

$$
\mathbf{B}_{new} =
\begin{bmatrix}
\mathbf{B}_{real} & \mathbf{B}_{imag}^T \\
\mathbf{B}_{imag} & \mathbf{B}_{real}
\end{bmatrix}
=
\begin{bmatrix}
\mathbf{B}_{real} & -\mathbf{B}_{imag} \\
\mathbf{B}_{imag} & \mathbf{B}_{real}
\end{bmatrix}
\in \mathbb{R}^{2N \times 2N} \tag{2.16b}
$$

$$
\mathbf{V}_{new} =
\begin{bmatrix}
\mathbf{V}_{real} \\
\mathbf{V}_{imag}
\end{bmatrix}
\in \mathbb{R}^{2N \times 1} \tag{2.16c}
$$

由于 $\mathbf{B}_{new}$ 是实对称矩阵，可以将其通过并行双边 Jacobi 旋转新方法进行矩阵特征值分解。

#### 符号说明

- $\mathbf{B}_{real}$：复厄米特矩阵 $\mathbf{B}$ 的实部
- $\mathbf{B}_{imag}$：复厄米特矩阵 $\mathbf{B}$ 的虚部
- $\mathbf{V}_{real}$：特征向量 $\mathbf{V}$ 的实部
- $\mathbf{V}_{imag}$：特征向量 $\mathbf{V}$ 的虚部
- $\mathbf{B}_{new}$：变形后的 $2N \times 2N$ 维实对称矩阵
- $\mathbf{V}_{new}$：变形后的 $2N \times 1$ 维特征向量

#### 处理流程

计算复厄米特矩阵特征值和特征向量的完整过程如下：

**步骤 1：矩阵变形**

将复厄米特矩阵 $\mathbf{B}$ 变形为新形式的实对称矩阵 $\mathbf{B}_{new}$，即将实部和虚部按式（2.16b）拼接为 $2N \times 2N$ 的实矩阵。

**步骤 2：特征值分解**

通过并行双边 Jacobi 旋转新方法计算 $\mathbf{V}_{new}$ 和 $\boldsymbol{\Sigma}$，其中 $\boldsymbol{\Sigma}$ 是由 $\mathbf{B}_{new}$ 的特征值组成的对角矩阵。

**步骤 3：特征值排序**

按降序对 $\boldsymbol{\Sigma}$ 的对角元素进行排序，排序是为了便于步骤 4 中特征值的选择。

**步骤 4：提取特征值**

选择对角矩阵 $\boldsymbol{\Sigma}$ 在奇数（或偶数）位置的主对角元素作为复厄米特矩阵 $\mathbf{B}$ 的特征值。

**步骤 5：提取特征向量**

根据步骤 4 选择与 $\boldsymbol{\Sigma}$ 中特征值位置相对应的 $\mathbf{V}_{new}$ 列向量，变形后作为复厄米特矩阵 $\mathbf{B}$ 的特征向量。

#### $2 \times 2$ 复厄米特矩阵验证示例

以 $2 \times 2$ 的复厄米特矩阵 $\mathbf{B}$ 为例验证上述过程的正确性：

$$
\begin{bmatrix}
b_1 & b_2 \\
b_2^H & b_3
\end{bmatrix}
=
\begin{bmatrix}
c_1 & c_2 \\
c_3 & c_4
\end{bmatrix}
\begin{bmatrix}
\lambda_1 & 0 \\
0 & \lambda_2
\end{bmatrix}
\begin{bmatrix}
c_1^H & c_3^H \\
c_2^H & c_4^H
\end{bmatrix} \tag{2.17}
$$

其中 $b_1$、$b_3$、$\lambda_1$ 和 $\lambda_2$ 均为实数，其余为复数。设 $b_2 = d_1 - d_3i$，根据式（2.16）将 $\mathbf{B}$ 变形为 $4 \times 4$ 实对称矩阵：

$$
\begin{bmatrix}
b_1 & d_1 & 0 & -d_3 \\
d_1 & b_3 & d_3 & 0 \\
0 & d_3 & b_1 & d_1 \\
-d_3 & 0 & d_1 & b_3
\end{bmatrix}
=
\begin{bmatrix}
f_1 & f_2 & f_3 & f_4 \\
f_5 & f_6 & f_7 & f_8 \\
f_9 & f_{10} & f_{11} & f_{12} \\
f_{13} & f_{14} & f_{15} & f_{16}
\end{bmatrix}
\begin{bmatrix}
e_1 & 0 & 0 & 0 \\
0 & e_2 & 0 & 0 \\
0 & 0 & e_3 & 0 \\
0 & 0 & 0 & e_4
\end{bmatrix}
\begin{bmatrix}
f_1 & f_2 & f_3 & f_4 \\
f_5 & f_6 & f_7 & f_8 \\
f_9 & f_{10} & f_{11} & f_{12} \\
f_{13} & f_{14} & f_{15} & f_{16}
\end{bmatrix}^H \tag{2.18}
$$

其中 $e_i(i = 1,2,3,4)$ 是特征值。求解方程得到：

$$
e_1 = e_2 \tag{2.19}
$$

$$
e_3 = e_4 \tag{2.20}
$$

即 $4 \times 4$ 实对称矩阵只有两个不相等的特征值，与原始 $2 \times 2$ 复厄米特矩阵 $\mathbf{B}$ 只有两个特征值 $\lambda_1$ 和 $\lambda_2$ 一致，验证了新方法的正确性。

## 2.3 关键硬件体系架构

### 2.3.1 顶层描述

图2.2 给出了基于 FPGA 的并行双边 Jacobi 旋转新方法的顶层描述，其中标明了模块之间的关键信号通路。

![](../kb_material/基于FPGA的阵列信号处理算法中关键矩阵算子的高性能实现研究_闫迪.pdf-0744ff48-8b86-4f31-af9c-38c0ad8d1d4d/images/c0c11f84c7b6d3f7944e1a2827371cb550c3db6be02dda44c2f7a61fb621eeb1.jpg)

**图2.2 基于FPGA的并行双边Jacobi旋转新方法的顶层描述**

#### 12 个硬件模块及其功能

根据图 2.2，新方法的硬件架构共计 12 个模块，各模块功能如下：

**模块 1 — 协方差矩阵计算**

用于计算输入数据的协方差矩阵，作为后续特征值分解的输入矩阵。

**模块 2 — 实对称矩阵缓存**

缓存模块 1 输出的实对称矩阵数据，为后续 Jacobi 旋转提供数据访问。

**模块 3 — 调度序列缓存**

缓存奇偶固定数据调度序列的编号，用于确定每次 Jacobi 旋转所影响的行和列。

**模块 5 — Jacobi 旋转因子计算**

根据调度序列选取矩阵中对应的元素，按式（2.7a）—（2.7d）计算 Jacobi 旋转因子 $c$ 和 $s$，并输出给乘加模块。

**模块 4 — 矩阵左乘**

接收 Jacobi 旋转因子，读取对应的行向量，按照式（2.11）完成矩阵 $\mathbf{B}$ 的左乘旋转操作（$\mathbf{U}^T \mathbf{B}$）。

**模块 6 — 矩阵右乘**

接收 Jacobi 旋转因子，读取对应的列向量，按照式（2.13）完成矩阵 $\mathbf{B}$ 的右乘旋转操作（$\mathbf{B} \mathbf{U}$），一次平面旋转完成。

**模块 9 — 特征向量左乘**

与模块 4 功能相同，用于完成特征向量矩阵的迭代累乘运算（$\mathbf{U} = \mathbf{U}_i \cdots \mathbf{U}_1 \mathbf{U}_0$）。

**模块 7 — 特征向量中间结果缓存**

缓存模块 9 输出的旋转矩阵乘法的中间结果。

**模块 8 — 矩阵旋转中间结果缓存**

缓存模块 6 输出的矩阵右乘中间计算结果，供下一次迭代和后续模块使用。

**模块 10 — 特征值降序排序**

对最终对角矩阵的对角元素（特征值）按降序进行排列。

**模块 11 — 特征向量选择**

通过模块 8 中缓存的对角元素的奇数（或偶数）位置，选择对应的特征向量。

**模块 12 — 有限状态机（FSM）**

用于控制和监控其他所有模块。对于一个固定维度的对称矩阵，扫描次数 $S$ 是固定的，可通过 MATLAB 或其他数学软件预先确定。FSM 根据设定的扫描次数控制整个计算过程的启动、迭代和终止。

#### 整体处理流程

基于上述模块，对协方差矩阵 $\mathbf{B}$ 实现复厄米特矩阵特征值分解的整体过程共 7 个步骤：

**步骤 1：矩阵变形输入**

将输入矩阵 $\mathbf{B}$ 按式（2.16b）变形为实对称矩阵：

$$
\mathbf{B}_{new} = \begin{bmatrix} \mathbf{B}_{real} & \mathbf{B}_{imag}^T \\ \mathbf{B}_{imag} & \mathbf{B}_{real} \end{bmatrix}
$$

**步骤 2：执行一次 Jacobi 旋转**，包含以下子步骤：

- 步骤 2a：依照选定的数据调度序列规则，根据设置好的并行度 $P$，选择 $\mathbf{B}_{new}$ 中对应的元素，计算 Jacobi 旋转矩阵 $\mathbf{U}_1$
- 步骤 2b：按照式（2.11）实现矩阵左旋转操作 $\mathbf{B}_1 = \mathbf{U}_1^T \mathbf{B}_{new}$
- 步骤 2c：按照式（2.13）实现矩阵右旋转操作 $\mathbf{B}_2 = \mathbf{B}_1 \mathbf{U}_1$
- 步骤 2d：按照式（2.14）完成特征矢量矩阵的迭代运算 $\mathbf{U} = \mathbf{U}_1 \mathbf{U}_0$，其中 $\mathbf{U}_0$ 为单位阵

**步骤 3：迭代旋转**

在完成步骤 2 后，更新矩阵 $\mathbf{B}_{new}$ 为 $\mathbf{B}_2$，同时按照设置好的并行度读取新的调度序列，选择 $\mathbf{B}_{new}$ 中对应的元素计算 Jacobi 旋转矩阵 $\mathbf{U}_2$，重复步骤 2。

**步骤 4：判断终止条件**

如果步骤 2 的迭代次数达到预设的迭代次数 $s$，则停止迭代，输出特征矢量矩阵 $\mathbf{U} = \mathbf{U}_s \cdots \mathbf{U}_1 \mathbf{U}_0$ 和对角矩阵 $\boldsymbol{\Sigma} = \mathbf{B}_s$。

**步骤 5：特征值降序排列**

对矩阵 $\boldsymbol{\Sigma}$ 的对角元素按降序排列。

**步骤 6：提取复矩阵特征值**

选择排序后奇数（或偶数）位置处矩阵 $\boldsymbol{\Sigma}$ 的对角元素，即为复厄米特矩阵 $\mathbf{B}$ 的特征值。这是由于变形后的矩阵维数翻倍，每对相邻特征值相等（见式 2.19、2.20），因此只需取间隔位置的值。

**步骤 7：提取复矩阵特征向量**

根据步骤 6 所选特征值对应的特征矢量矩阵 $\mathbf{U}$ 的列矢量，将其变形后作为复厄米特矩阵 $\mathbf{B}$ 的特征向量。

整体而言，该硬件实现的流程与式（2.1）—（2.7）的数学过程基本一致，结构清晰，便于硬件工程师理解和实现。

### 2.3.2 数据缓存

**（1）调度序列缓存**

采用奇偶固定调度序列确定每次 Jacobi 旋转影响的行和列。以 $8 \times 8$ 矩阵为例，一次循环需 8 步完成。优化规则：偶数步的行列编号可由奇数步的前 3 个和后 3 个元素推导得到，省去偶数步调度序列的缓存，节省硬件资源。

![](../kb_material/基于FPGA的阵列信号处理算法中关键矩阵算子的高性能实现研究_闫迪.pdf-0744ff48-8b86-4f31-af9c-38c0ad8d1d4d/images/6dbf6aadc63c4a74f40a5c944a6432b1fa8479cacd2abf75ef634274d42681f6.jpg)

**图2.3 标准奇偶固定调度序列**

![](../kb_material/基于FPGA的阵列信号处理算法中关键矩阵算子的高性能实现研究_闫迪.pdf-0744ff48-8b86-4f31-af9c-38c0ad8d1d4d/images/889a6347a0bce182f9db3e6defb42ed1ce001ebe540ae4685ee75d4e080b6139.jpg)

**图2.4 缓存的奇偶固定调度序列**

**（2）矩阵数据行式读取**

采用逐行方式读取矩阵数据，支持灵活的并行度：
- $P = 2$：每次读取 2 行（并行度 1）
- $P = 4$：每次读取 4 行（并行度 2）
- $P = 8$：每次读取 8 行（并行度 4）

可根据硬件资源、实时性需求灵活选择并行度。

![](../kb_material/基于FPGA的阵列信号处理算法中关键矩阵算子的高性能实现研究_闫迪.pdf-0744ff48-8b86-4f31-af9c-38c0ad8d1d4d/images/58f3802894971bc0423d01f503913c608f081f5f20d020306464c0a36f12f5cf.jpg)

**图2.6 变形后的 $8 \times 8$ 实对称矩阵的两种读取方式**

### 2.3.3 矩阵乘法

矩阵乘法硬件结构主要包括乘法器和加法器，可通过 FPGA 上的 DSP48E1 实现。矩阵左乘处理行向量，矩阵右乘处理列向量。

![](../kb_material/基于FPGA的阵列信号处理算法中关键矩阵算子的高性能实现研究_闫迪.pdf-0744ff48-8b86-4f31-af9c-38c0ad8d1d4d/images/c370b447555b14c2f4e71093a5de21f1cb49e81352dacdfafc10f676cdf52b01.jpg)

**图2.7 矩阵乘法的硬件架构**

## 2.4 实验结果与分析

实验平台：Xilinx XC7V690T-FPGA，测试矩阵维数为 $8 \times 8$ 复厄米特矩阵，与四种方法对比。

参与比较的五种方法：
- **QR algorithm**：修正的 Gram-Schmidt 方法（单精度浮点）
- **Improved QR algorithm [119]**：改进 QR 算法（单精度浮点）
- **Fast CORDIC [126]**：基于改进 CORDIC 的 BLV 脉动阵列（定点）
- **Improved Jacobi's method [130]**：DSP48E1 定点 $2\times 2$ 分块（定点）
- **New method**：本章提出的并行双边 Jacobi 旋转新方法（单精度浮点）

### 2.4.1 硬件资源消耗

| 方法                    | LUTs    | BRAM | DSP48E1 | 频率     | 时延（一次扫描）   |
| --------------------- | ------- | ---- | ------- | ------ | ---------- |
| QR algorithm          | 46k     | 36   | 1964    | 250MHz | 50μs       |
| Improved QR [119]     | 50k     | 38   | 2004    | 250MHz | 43μs       |
| Fast CORDIC [126]     | 81k     | 48   | 378     | 200MHz | 55μs       |
| Improved Jacobi [130] | 65k     | 48   | 352     | 200MHz | 52μs       |
| **New method (P=2)**  | **28k** | 48   | 288     | 250MHz | **41.8μs** |
| New method (P=4)      | 46k     | 90   | 640     | 250MHz | 38μs       |
| New method (P=8)      | 73k     | 128  | 1740    | 250MHz | 36μs       |

**表2.1 五种高性能方法的硬件资源消耗**

- $P=2$ 时新方法的 LUT 消耗最少（28k），因为主要操作为矩阵乘法而非逻辑电路
- Fast CORDIC 的 LUT 最多（81k），因为 CORDIC 主要由 LUT 逻辑电路实现
- DSP48E1 消耗：新方法显著低于 QR 类方法（利用了旋转矩阵稀疏性减少冗余计算）
- 时延随并行度增大而减小（$P=2$：41.8μs → $P=8$：36μs）

### 2.4.2 数值性能

**矩阵重建误差**定义为：

$$
\mathbf{E}_r = | \mathbf{B} - \mathbf{V}^H \boldsymbol{\Sigma} \mathbf{V} | \tag{2.21}
$$

**特征值计算误差**定义为：

$$
\mathbf{E}_{eig} = | \operatorname{diag}(\boldsymbol{\Sigma}_M) - \operatorname{diag}(\boldsymbol{\Sigma}_F) | \tag{2.22}
$$

**特征向量正交性**定义为：

$$
\mathbf{E}_v = | \mathbf{I} - \mathbf{V}^H \mathbf{V} | \tag{2.23}
$$

其中 $\boldsymbol{\Sigma}_M$ 和 $\boldsymbol{\Sigma}_F$ 分别是 MATLAB EIG 和 FPGA 得到的特征值矩阵。

![](../kb_material/基于FPGA的阵列信号处理算法中关键矩阵算子的高性能实现研究_闫迪.pdf-0744ff48-8b86-4f31-af9c-38c0ad8d1d4d/images/dcefeb6247585ad432fa53add61422573694f6aaf9023430283496638c70dab1.jpg)

**(a) QR algorithm 矩阵重建误差**

![](../kb_material/基于FPGA的阵列信号处理算法中关键矩阵算子的高性能实现研究_闫迪.pdf-0744ff48-8b86-4f31-af9c-38c0ad8d1d4d/images/7ca11101e8b95df36d1e9c4ef3927941d0ebfc81fe6047baae34a4f0b7f515c8.jpg)

**(b) Improved QR algorithm [119] 矩阵重建误差**

![](../kb_material/基于FPGA的阵列信号处理算法中关键矩阵算子的高性能实现研究_闫迪.pdf-0744ff48-8b86-4f31-af9c-38c0ad8d1d4d/images/8099b57ff1306e8086d2508c65ada0fb42421649f87c868e510561fba83a009f.jpg)

**(c) 本章新方法 矩阵重建误差**

**图2.8 矩阵重建误差对比**

实验结论：
- **矩阵重建误差**：新方法 < Improved QR < QR（新方法性能最佳）
- **特征值计算误差**：新方法 < Improved QR < QR（新方法精度最高）
- **特征向量正交性**：QR 算法最优，但新方法的特征值精度显著优于 QR 类方法

## 2.5 基于 DOA 估计的应用结果

将新方法应用于 16 通道、8 信源的 MUSIC 算法 DOA 估计（SNR = -10dB，快拍数 1024，步长 0.01°）。

#### 硬件资源消耗（$16 \times 16$ 复矩阵）

| 方法 | LUTs | DSP48E1 | 时延 |
|------|------|---------|------|
| QR algorithm | 64k | 2210 | 620μs |
| Improved QR | 60k | 2184 | 584μs |
| Improved Jacobi | 72k | 1264 | 600μs |
| **New method (P=2)** | **50k** | 1840 | **566μs** |

**表2.2 DOA估计实验硬件资源消耗**

新方法的硬件资源消耗最少，时延最小。数值计算结果显示：新方法得到特征向量正交性最佳，伪倒谱误差幅值最小，谱峰最尖锐（噪声子空间与信号子空间正交性最好）。

![](../kb_material/基于FPGA的阵列信号处理算法中关键矩阵算子的高性能实现研究_闫迪.pdf-0744ff48-8b86-4f31-af9c-38c0ad8d1d4d/images/641bb5ec6af960946ac99f53bfb5698b66d2b70f06e0919525d4dcbc81fbdc50.jpg)

**(a) QR algorithm 的伪倒谱**

![](../kb_material/基于FPGA的阵列信号处理算法中关键矩阵算子的高性能实现研究_闫迪.pdf-0744ff48-8b86-4f31-af9c-38c0ad8d1d4d/images/c890e0004ac4072082bba580e4060f4644b261c37715def8b5b891be374b9676.jpg)

**(b) Improved QR algorithm [119] 的伪倒谱**

![](../kb_material/基于FPGA的阵列信号处理算法中关键矩阵算子的高性能实现研究_闫迪.pdf-0744ff48-8b86-4f31-af9c-38c0ad8d1d4d/images/42e46a2032a205c76aa735a59c0f4598142c3796e33da31cd723a6e7fd6b0e62.jpg)

**(c) 本章新方法的伪倒谱**

**图2.12(a)-(c) 基于三种方法实现MUSIC算法的伪倒谱**

## 2.6 结论

本章提出了一种基于 FPGA 的并行双边 Jacobi 旋转矩阵特征值分解新方法，核心创新点：

1. **利用旋转矩阵稀疏性**：无需 CORDIC 和 BLV 脉动阵列，通过非零元素与对应行/列向量相乘简化矩阵乘法，显著降低运算量
2. **复厄米特矩阵支持**：通过变形处理使双边 Jacobi 算法适用于复矩阵特征值分解
3. **灵活并行度**：行式读取方式支持 $P = 2, 4, 8$ 等不同并行度，适应不同硬件资源约束
4. **单精度浮点运算**：充分利用 FPGA 乘法器提高数值精度

实验结果表明，新方法在硬件资源消耗（LUT 减少 40%~65%）、时延（降低 15%~25%）和数值精度（重建误差和特征值误差均小于对比方法）方面均具有明显优势。应用于 DOA 估计问题时，新方法的伪倒谱谱峰最尖锐，噪声子空间正交性最佳。
