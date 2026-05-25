---
tags:
  - 信号处理
  - 阵列信号处理
  - DOA估计
  - 谱估计
created: 2026-05-25
---

# 空间谱估计与 MUSIC 算法

## 1. 背景与问题描述

**空间谱估计**（Spatial Spectrum Estimation）是指利用天线阵列接收信号，估计不同来波方向（DOA, Direction of Arrival）上信号功率分布的技术。其核心问题是：

> 给定 $M$ 个阵元接收到的数据 $\mathbf{x}(t)$，估计 $K$ 个信号源的方向 $\{\theta_1,\theta_2,\dots,\theta_K\}$。

MUSIC（**MU**ltiple **SI**gnal **C**lassification）算法由 Schmidt 于 1979 年提出，是**子空间类方法**的奠基之作，突破了传统波束形成方法的瑞利限（Rayleigh Resolution Limit），实现了**超分辨**测向。

---

## 2. 阵列信号模型

### 2.1 远场窄带假设

- **远场**：信源距离远大于阵列孔径，入射波可视为平面波
- **窄带**：信号带宽远小于载频，包络在各阵元间可视为不变（仅有相移）

### 2.2 数学模型

设 $M$ 个阵元，$K$ 个不相关的远场窄带信源（$K < M$），则阵列接收数据为：

$$
\mathbf{x}(t) = \mathbf{A}(\theta)\,\mathbf{s}(t) + \mathbf{n}(t)
$$

其中：

| 符号 | 维度 | 含义 |
|------|------|------|
| $\mathbf{x}(t)$ | $M \times 1$ | 阵列接收数据向量 |
| $\mathbf{A}(\theta) = [\mathbf{a}(\theta_1),\dots,\mathbf{a}(\theta_K)]$ | $M \times K$ | 阵列流型矩阵 (Array Manifold) |
| $\mathbf{a}(\theta_k)$ | $M \times 1$ | 第 $k$ 个信源的方向向量/导向矢量 (Steering Vector) |
| $\mathbf{s}(t)$ | $K \times 1$ | 信号复包络向量 |
| $\mathbf{n}(t)$ | $M \times 1$ | 加性噪声向量 |

### 2.3 导向矢量（均匀线阵 ULA）

对于 $M$ 阵元的均匀线阵（阵元间距 $d$），导向矢量为：

$$
\mathbf{a}(\theta) = \begin{bmatrix}
1 \\
e^{-j\frac{2\pi}{\lambda}d\sin\theta} \\
e^{-j\frac{2\pi}{\lambda}2d\sin\theta} \\
\vdots \\
e^{-j\frac{2\pi}{\lambda}(M-1)d\sin\theta}
\end{bmatrix} = \begin{bmatrix}
1 \\
e^{-j\omega} \\
e^{-j2\omega} \\
\vdots \\
e^{-j(M-1)\omega}
\end{bmatrix}
$$

其中 $\omega = \frac{2\pi}{\lambda}d\sin\theta$ 为空间角频率。

---

## 3. 协方差矩阵与特征分解

### 3.1 数据协方差矩阵

假设信号 $\mathbf{s}(t)$ 与噪声 $\mathbf{n}(t)$ 统计独立，噪声为空间白噪声（$\mathbf{R}_n = \sigma^2\mathbf{I}$），则：

$$
\mathbf{R} = \mathbb{E}[\mathbf{x}(t)\mathbf{x}^H(t)] = \mathbf{A}\mathbf{R}_s\mathbf{A}^H + \sigma^2\mathbf{I}
$$

其中：
- $\mathbf{R}_s = \mathbb{E}[\mathbf{s}(t)\mathbf{s}^H(t)]$ 为 $K \times K$ 信号协方差矩阵（满秩 $K$）
- $\sigma^2$ 为噪声功率

实际中，用 $N$ 次快拍估计：

$$
\hat{\mathbf{R}} = \frac{1}{N}\sum_{t=1}^{N}\mathbf{x}(t)\mathbf{x}^H(t)
$$

### 3.2 特征分解

对 $\mathbf{R}$ 做特征分解：

$$
\mathbf{R} = \sum_{i=1}^{M}\lambda_i\,\mathbf{u}_i\mathbf{u}_i^H = \mathbf{U}_s\mathbf{\Lambda}_s\mathbf{U}_s^H + \mathbf{U}_n\mathbf{\Lambda}_n\mathbf{U}_n^H
$$

将 $M$ 个特征值降序排列：

$$
\lambda_1 \ge \lambda_2 \ge \dots \ge \lambda_K > \lambda_{K+1} = \dots = \lambda_M = \sigma^2
$$

| 子空间 | 基向量 | 特征值 | 维度 |
|--------|--------|--------|------|
| **信号子空间** $\mathbf{U}_s$ | $\mathbf{u}_1,\dots,\mathbf{u}_K$ | $\lambda_1,\dots,\lambda_K$ | $M \times K$ |
| **噪声子空间** $\mathbf{U}_n$ | $\mathbf{u}_{K+1},\dots,\mathbf{u}_M$ | $\lambda_{K+1},\dots,\lambda_M$ | $M \times (M-K)$ |

> **💡 硬件加速实现**：特征分解是 MUSIC 算法中计算量最大的步骤（$O(M^3)$）。在 FPGA 等硬件平台上，可采用**并行双边 Jacobi 旋转**算法实现高效的特征值分解，相比传统 QR 算法和 CORDIC 方案，LUT 资源减少 40%~65%，时延降低 15%~25%。详见 [[并行双边Jacobi旋转特征值分解]]。

---

## 4. MUSIC 算法核心原理

### 4.1 核心结论

> **信号导向矢量 $\mathbf{a}(\theta_k)$ 与噪声子空间 $\mathbf{U}_n$ 正交。**

证明思路：
1. $\mathbf{R} = \mathbf{A}\mathbf{R}_s\mathbf{A}^H + \sigma^2\mathbf{I}$
2. $\mathbf{R}\mathbf{U}_n = \sigma^2\mathbf{U}_n$（噪声子空间定义）
3. 代入得 $\mathbf{A}\mathbf{R}_s\mathbf{A}^H\mathbf{U}_n = 0$
4. 由 $\mathbf{A}$ 和 $\mathbf{R}_s$ 均满列秩 $\Rightarrow$ $\mathbf{A}^H\mathbf{U}_n = 0$
5. 即 $\mathbf{a}^H(\theta_k)\mathbf{U}_n = 0,\quad k=1,\dots,K$

### 4.2 正交性条件

$$
\mathbf{a}^H(\theta_k)\,\mathbf{U}_n\mathbf{U}_n^H\,\mathbf{a}(\theta_k) = 0 \quad\Longleftrightarrow\quad \theta = \theta_k
$$

因此，**MUSIC 空间谱**定义为：

$$
\boxed{P_{\text{MUSIC}}(\theta) = \frac{1}{\mathbf{a}^H(\theta)\,\mathbf{U}_n\mathbf{U}_n^H\,\mathbf{a}(\theta)}}
$$

或等价地：

$$
P_{\text{MUSIC}}(\theta) = \frac{\mathbf{a}^H(\theta)\mathbf{a}(\theta)}{\mathbf{a}^H(\theta)\,\mathbf{U}_n\mathbf{U}_n^H\,\mathbf{a}(\theta)}
$$

当 $\theta$ 等于真实 DOA 时，分母趋向 0，$P_{\text{MUSIC}}(\theta)$ 产生尖锐的**谱峰**。

---

## 5. MUSIC 算法步骤（完整流程）

### 步骤 1：估计协方差矩阵

由 $N$ 次快拍数据 $\{\mathbf{x}(1),\mathbf{x}(2),\dots,\mathbf{x}(N)\}$ 计算：

$$
\hat{\mathbf{R}} = \frac{1}{N} \sum_{t=1}^{N}\mathbf{x}(t)\mathbf{x}^H(t)
$$

### 步骤 2：特征分解

对 $\hat{\mathbf{R}}$ 做特征值分解，得到 $M$ 个特征值及对应的特征向量：

$$
\lambda_1 \ge \lambda_2 \ge \dots \ge \lambda_M
$$

### 步骤 3：信源数估计

确定信源数量 $K$。常用准则：

- **信息论准则**（AIC / MDL）：

$$
\begin{aligned}
\text{AIC}(k) &= -2N(M-k)\ln\frac{g(k)}{a(k)} + 2k(2M-k) \\[6pt]
\text{MDL}(k) &= -N(M-k)\ln\frac{g(k)}{a(k)} + \frac{1}{2}k(2M-k)\ln N
\end{aligned}
$$

其中 $g(k)$ 为特征值几何均值，$a(k)$ 为算术均值。取使准则最小的 $k$ 作为 $\hat{K}$。

- **特征值比值法**：寻找特征值序列中最大的"跳变"点。

### 步骤 4：构造噪声子空间

取最小的 $M-K$ 个特征值对应的特征向量构成噪声子空间：

$$
\mathbf{U}_n = [\mathbf{u}_{K+1},\,\mathbf{u}_{K+2},\,\dots,\,\mathbf{u}_M] \in \mathbb{C}^{M \times (M-K)}
$$

### 步骤 5：搜索 MUSIC 谱

在角度搜索范围 $[\theta_{\min},\theta_{\max}]$ 内，以步长 $\Delta\theta$ 遍历：

1. 对每个 $\theta$ 计算导向矢量 $\mathbf{a}(\theta)$
2. 计算 MUSIC 伪谱：

$$
P_{\text{MUSIC}}(\theta) = \frac{1}{\mathbf{a}^H(\theta)\,\mathbf{U}_n\mathbf{U}_n^H\,\mathbf{a}(\theta)}
$$

3. 频谱扫描，寻找 $K$ 个最大的峰值，其对应的 $\theta$ 即为 DOA 估计值。

---

## 6. MATLAB / Python 伪代码

```python
import numpy as np

def music_algorithm(X, M, d, wavelength, angle_grid, K):
    """
    MUSIC 算法实现
    
    参数:
        X: 阵列接收数据, shape = (M, N), M阵元数, N快拍数
        M: 阵元数
        d: 阵元间距
        wavelength: 波长
        angle_grid: 角度搜索网格 (弧度)
        K: 信源数
    
    返回:
        P_music: MUSIC 伪谱
        doa_estimates: 估计的DOA
    """
    # Step 1: 协方差矩阵估计
    N = X.shape[1]
    R_hat = (X @ X.conj().T) / N  # M × M
    
    # Step 2: 特征分解
    eigenvalues, eigenvectors = np.linalg.eigh(R_hat)
    # eigh 返回升序，需要降序
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]
    
    # Step 3: 信源数 (此处直接使用已知K)
    # Step 4: 噪声子空间 (最小的 M-K 个特征向量)
    Un = eigenvectors[:, K:]  # M × (M-K)
    
    # Step 5: MUSIC 谱搜索
    P_music = np.zeros(len(angle_grid))
    for i, theta in enumerate(angle_grid):
        # 导向矢量
        a = np.exp(-1j * 2 * np.pi * d / wavelength 
                    * np.sin(theta) * np.arange(M))
        a = a.reshape(-1, 1)
        # MUSIC 伪谱
        denom = a.conj().T @ Un @ Un.conj().T @ a
        P_music[i] = 1.0 / np.abs(denom.item())
    
    # 找K个峰值
    peak_indices = np.argsort(P_music)[-K:]
    doa_estimates = np.sort(angle_grid[peak_indices])
    
    return P_music, doa_estimates
```

---

## 7. 关键性质与注意事项

### 7.1 分辨率优势

- 传统波束形成受**瑞利限**约束（~ 波束宽度）
- MUSIC 的分辨率不受瑞利限限制，取决于**信噪比**和**快拍数**
- 在高 SNR / 多快拍条件下，可分辨角度差远小于波束宽度的两个信源

### 7.2 信源数估计的重要性

- $K$ 的估计错误会导致严重后果：
  - **欠估计**（$\hat{K} < K$）：部分信源被淹没在噪声子空间中 → 漏检
  - **过估计**（$\hat{K} > K$）：噪声子空间被污染 → 出现虚假谱峰

### 7.3 相干信源问题

- MUSIC **不能直接处理**相干信源（如多径信号）
- 相干信源导致信号协方差矩阵 $\mathbf{R}_s$ 秩亏损
- **解决方案**：空间平滑（Spatial Smoothing）预处理

### 7.4 阵列校准

- 导向矢量 $\mathbf{a}(\theta)$ 依赖精确的阵列几何
- 通道幅相不一致、阵元位置误差会导致性能严重下降

### 7.5 计算复杂度

- 主要开销：协方差估计 $O(M^2N)$ + 特征分解 $O(M^3)$
- 搜索 MUSIC 中引入 **Root-MUSIC**可进一步降低计算开销

---

## 8. 变种与改进算法

| 算法 | 特点 |
|------|------|
| **Root-MUSIC** | ULA 下将谱搜索转为多项式求根，计算量小，无网格量化误差 |
| **Cyclic MUSIC** | 利用循环平稳特性，可处理多于阵元数的信源 |
| **MUSIC with Spatial Smoothing** | 通过子阵平均去相关，解决相干信源问题 |
| **Weighted MUSIC** | 在噪声子空间投影中加入加权，改善低 SNR 性能 |
| **Tensor MUSIC** | 将阵列数据建模为张量，利用多维结构提高分辨能力 |

---

## 9. 与 ESPRIT 的对比

| 特性 | MUSIC | ESPRIT |
|------|-------|--------|
| 原理 | 噪声子空间正交性 | 信号子空间旋转不变性 |
| 计算 | 需谱搜索（Root-MUSIC 除外） | 闭式解，无需搜索 |
| 阵列要求 | 任意阵列（已知流型） | 需阵列具有平移不变结构 |
| 阵列校准 | 需精确校准 | 对校准误差更鲁棒 |
| 计算量 | 较大（谱搜索） | 较小（直接求解） |

---

## 10. 参考文献

- Schmidt, R.O., "Multiple Emitter Location and Signal Parameter Estimation," *IEEE Trans. AP*, 1986.
- Van Trees, H.L., *Optimum Array Processing*, Wiley, 2002.
- Krim, H. & Viberg, M., "Two Decades of Array Signal Processing Research," *IEEE Signal Processing Magazine*, 1996.
- Wax, M. & Kailath, T., "Detection of Signals by Information Theoretic Criteria," *IEEE Trans. ASSP*, 1985.
