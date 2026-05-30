---
tags:
  - pytorch
  - deep-learning
  - 入门
created: 2026-05-21
updated: 2026-05-25
---

# PyTorch 入门笔记

> 面向初学者的 PyTorch 实战手册。以代码为核心，按"会用 → 理解 → 熟练"的节奏展开。
> 概念性的深度学习问题（为什么需要激活函数、反向传播怎么算等）见 [ML/一些疑惑解答](一些疑惑解答.md)。

---

## 一、核心哲学：PyTorch 在干什么

PyTorch 只做三件事：

| 能力            | 对应模块             | 大白话                 |
| ------------- | ---------------- | ------------------- |
| **存数据 + 算矩阵** | `torch.Tensor`   | 替代 NumPy，还能跑在 GPU 上 |
| **自动求导**      | `torch.autograd` | 你写前向计算，它自动算梯度       |
| **搭积木式建网络**   | `torch.nn`       | 像搭乐高一样拼出神经网络        |

一个网络从无到有的完整流程：

```
定义模型结构 → 准备数据 → 前向传播(算预测) → 算误差(loss)
    ↖                                              ↓
      optimizer.step() 改参数  ←  backward() 算梯度
```

---

## 二、Tensor：一切的基础

### 2.1 创建 Tensor

```python
import torch

# 从列表创建
a = torch.tensor([1, 2, 3])                # [1, 2, 3]
b = torch.tensor([[1, 2], [3, 4]])          # 2×2 矩阵

# 常用快捷创建
c = torch.zeros(3, 4)        # 全 0，形状 (3, 4)
d = torch.ones(2, 3)         # 全 1
e = torch.randn(3, 3)        # 标准正态分布随机数（最常用于初始化权重）
f = torch.arange(0, 10, 2)   # [0, 2, 4, 6, 8]
g = torch.eye(3)             # 3×3 单位矩阵

# 从 NumPy 互转
import numpy as np
arr = np.array([1, 2, 3])
t = torch.from_numpy(arr)    # NumPy → Tensor
back = t.numpy()             # Tensor → NumPy（仅 CPU tensor）
```

### 2.2 核心属性

```python
x = torch.randn(2, 3, 4)
print(x.shape)      # torch.Size([2, 3, 4]) — 形状
print(x.dtype)      # torch.float32 — 数据类型
print(x.device)     # cpu — 在哪个设备上
print(x.ndim)       # 3 — 几维
```

### 2.3 索引和切片（和 NumPy 一样，左闭右开）

```python
x = torch.randn(4, 5)

x[0, 0]          # 第 0 行第 0 列
x[0, :]          # 第 0 行全部
x[:, 1]          # 第 1 列全部
x[:2, 1:4]       # 行 0~1（不含2），列 1~3（不含4）——左闭右开
x[x > 0]         # 布尔索引：所有正数
```

**"左闭右开"是什么意思？**

```python
t = torch.tensor([10, 20, 30, 40, 50])

t[1:4]   # → tensor([20, 30, 40])
         # 包含索引 1（左闭），不包含索引 4（右开）
         # 所以取出的是索引 1、2、3 这三个元素
```

简单记：`[start:end]` 就是**从 start 开始取，取到 end 之前停止**。

| 写法 | 实际取到的索引 | 结果 |
|------|--------------|------|
| `t[1:4]` | 1, 2, 3 | `[20, 30, 40]` |
| `t[:3]` | 0, 1, 2 | `[10, 20, 30]` |
| `t[2:]` | 2, 3, 4 | `[30, 40, 50]` |
| `t[:]` | 全部 | `[10, 20, 30, 40, 50]` |

这和 Python 原生的 `list` 切片、NumPy 切片规则完全一致，PyTorch 没有另搞一套。

### 2.4 变形操作（高频）

```python
x = torch.randn(2, 3, 4)    # (2, 3, 4)

x.view(2, 12)                # (2, 12) — 改形状（要求内存连续）
x.view(-1, 12)               # -1 = "你帮我算这维多大"
x.reshape(6, 4)              # (6, 4) — 功能更强，不要求内存连续
x.unsqueeze(0)               # (1, 2, 3, 4) — 在最前面插一维（加 batch 维）
x.unsqueeze(-1)              # (2, 3, 4, 1) — 在最后加一维
x.squeeze()                  # 去掉所有大小为 1 的维度
x.permute(2, 0, 1)           # (4, 2, 3) — 重排维度顺序（类似 NumPy transpose）
x.flatten()                  # 展平成一维
```

### 2.5 运算（和 NumPy 一样，但支持 GPU）

```python
a = torch.randn(2, 3)
b = torch.randn(2, 3)

# 逐元素运算
a + b            # 加法
a * b            # 逐元素乘法（不是矩阵乘！）
a / b            # 除法
torch.relu(a)    # ReLU 激活

# 矩阵乘法（三种写法）
a @ b.T          # @ 运算符（推荐）
torch.matmul(a, b.T)
torch.mm(a, b.T)

# 广播
a = torch.randn(3, 4)
b = torch.randn(4)       # (4,) 自动广播成 (3, 4)
c = a + b                # 每一行都加 b

# 聚合
x.sum()           # 所有元素和
x.mean(dim=0)     # 沿第 0 维求均值
x.max()           # 最大值
x.argmax(dim=1)   # 沿第 1 维最大值的索引（分类任务最常用！）
```

---

## 三、自动求导 Autograd

**核心逻辑**：你只写前向计算，PyTorch 自动帮你算出每个参数对 Loss 的梯度。

### 3.1 一个最小示例

```python
import torch

# 创建一个需要求导的 Tensor（注意 requires_grad=True）
x = torch.tensor([2.0], requires_grad=True)
w = torch.tensor([3.0], requires_grad=True)
b = torch.tensor([1.0], requires_grad=True)

# 前向计算：y = w * x + b
y = w * x + b      # y = 3*2 + 1 = 7

# 手动算：dy/dw = x = 2, dy/db = 1
y.backward()       # 自动算所有 requires_grad=True 的张量的梯度

print(w.grad)      # tensor([2.]) ✓ dy/dw = x
print(b.grad)      # tensor([1.]) ✓ dy/db = 1
print(x.grad)      # tensor([3.])   dy/dx = w
```

### 3.2 三个关键规则

```python
# 规则 1：梯度会累加，每次 backward 前要清零
optimizer.zero_grad()   # 手动清零所有参数的 .grad

# 规则 2：不需要梯度时用 no_grad，省内存 + 加速
with torch.no_grad():
    predictions = model(x)   # 推理时用，不会建计算图

# 规则 3：detach() 把张量从计算图剥离
x_detached = x.detach()      # 返回一个不需要梯度的副本
```

---

## 四、搭积木：nn.Module

### 4.1 最小网络模板

```python
import torch.nn as nn

class MyNet(nn.Module):
    def __init__(self, input_size, hidden_size, num_classes):
        super().__init__()   # 必须！调用父类初始化

        # 定义层（在 __init__ 里只定义，不写数据流向）
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, num_classes)

    def forward(self, x):
        # 写数据流向：输入 → fc1 → relu → fc2 → 输出
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        return x

# 实例化
model = MyNet(input_size=784, hidden_size=128, num_classes=10)
print(model)
```

> **关键规则**：
> - 带可学习参数的层（Linear、Conv2d、BatchNorm）**必须在 `__init__` 里用 `self.xxx = nn.Xxx(...)` 定义**。
> - 不带参数的（ReLU、Dropout、Flatten）可以放 `__init__` 也可以在 `forward` 里直接用 `nn.functional.relu(x)` 调用。
> - PyTorch 自动追踪 `__init__` 里赋给 `self` 的 `nn.Module`，所以 `model.parameters()` 能自动收集所有权重。

### 4.2 两种写法：nn.ReLU() vs F.relu()

```python
import torch.nn.functional as F

# 风格 A：放 __init__，forward 里 self.relu(x)
class NetA(nn.Module):
    def __init__(self):
        super().__init__()
        self.relu = nn.ReLU()    # 创建一个对象，可复用
    def forward(self, x):
        return self.relu(x)

# 风格 B：forward 里直接调用 F.relu(x)
class NetB(nn.Module):
    def forward(self, x):
        return F.relu(x)         # 直接函数调用，更简洁
```

> 两种都可以。**有参数的（Linear、Conv2d）必须用风格 A**，无参数的看个人偏好。

---

## 五、常用层速查表

| 层 | 用法 | 什么时候用 |
|----|------|-----------|
| `nn.Linear(in, out)` | 全连接层 | 分类头、MLP、特征变换 |
| `nn.Conv2d(in_ch, out_ch, kernel_size)` | 2D 卷积 | 图像特征提取 |
| `nn.MaxPool2d(kernel_size)` | 最大池化 | 下采样、降维 |
| `nn.AdaptiveAvgPool2d((1,1))` | 自适应平均池化到固定大小 | 替代 Flatten，接全连接层 |
| `nn.BatchNorm1d/2d(num_features)` | 批归一化 | 加速收敛、稳定训练 |
| `nn.Dropout(p=0.5)` | 随机失活 | 防过拟合 |
| `nn.ReLU()` | ReLU 激活 | 隐藏层首选 |
| `nn.Sigmoid()` | Sigmoid 激活 | 二分类输出层 |
| `nn.Softmax(dim=1)` | Softmax | 多分类输出（CrossEntropyLoss 内置，通常不需要手动加） |
| `nn.Flatten()` | 展平 | CNN → FC 过渡 |
| `nn.Embedding(vocab_size, dim)` | 词嵌入 | NLP 输入层 |
| `nn.LSTM(input_size, hidden_size)` | LSTM 层 | 序列建模 |
| `nn.Sequential(...)` | 顺序容器 | 简单的前馈结构 |

### Sequential 快捷写法

```python
# 当网络就是一层接一层时，可以一行写完
model = nn.Sequential(
    nn.Linear(784, 256),
    nn.ReLU(),
    nn.Dropout(0.3),
    nn.Linear(256, 128),
    nn.ReLU(),
    nn.Linear(128, 10)
)
```

---

## 六、损失函数 Loss Functions

| 任务 | 损失函数 | 注释 |
|------|---------|------|
| **多分类** | `nn.CrossEntropyLoss()` | **自带 Softmax + log + NLLLoss**，所以网络最后一层**不要加 Softmax** |
| **二分类** | `nn.BCEWithLogitsLoss()` | **自带 Sigmoid**，所以最后一层不要加 Sigmoid |
| **回归** | `nn.MSELoss()` | 均方误差 |
| **回归（抗异常值）** | `nn.L1Loss()` | 绝对误差 |

```python
# 多分类示例
criterion = nn.CrossEntropyLoss()

# outputs 形状: (batch_size, num_classes) — 原始 logits
# labels 形状: (batch_size,) — 整数标签，不是 one-hot！
outputs = model(images)            # (64, 10)
loss = criterion(outputs, labels)  # labels: (64,)，每个是 0~9 的整数
```

> ⚠️ **新手第一大坑**：`CrossEntropyLoss` 的输入必须是**原始 logits**，网络最后一层不要加 Softmax。labels 传整数标签，不要传 one-hot。

---

## 七、优化器 Optimizers

```python
# 最常用的两个
optimizer = torch.optim.SGD(model.parameters(), lr=0.01, momentum=0.9)
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)  # 推荐入门首选

# 学习率调度器（训练中途自动降 lr）
scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=30, gamma=0.1)
# 每 30 个 epoch 将 lr 乘 0.1
```

| 优化器 | 特点 | 推荐场景 |
|--------|------|---------|
| **SGD** | 经典、稳定，需要手动调参 | 学术研究、追求 SOTA |
| **Adam** | 自适应学习率，收敛快 | 入门首选、快速实验 |
| **AdamW** | Adam + 更好的权重衰减 | Transformer、大模型 |

---

## 八、完整训练流程

### 8.1 训练四步曲（最重要）

```python
# ① 前向传播 + 算 Loss
outputs = model(inputs)              # 模型预测
loss = criterion(outputs, labels)    # 算误差

# ② 清零梯度（PyTorch 梯度默认累加！）
optimizer.zero_grad()

# ③ 反向传播（算梯度）
loss.backward()

# ④ 更新参数
optimizer.step()
```

> 详细解释见 [ML/一些疑惑解答](一些疑惑解答.md)。

### 8.2 完整训练 + 验证示例（MNIST）

```python
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

# ========== 1. 超参数 ==========
BATCH_SIZE = 64
LR = 0.001
EPOCHS = 10
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ========== 2. 数据准备 ==========
transform = transforms.Compose([
    transforms.ToTensor(),                     # PIL Image → Tensor + 归一化到 [0,1]
    transforms.Normalize((0.1307,), (0.3081,)) # MNIST 的均值和标准差
])

train_dataset = datasets.MNIST(root="./data", train=True,  download=True, transform=transform)
test_dataset  = datasets.MNIST(root="./data", train=False, download=True, transform=transform)

train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
test_loader  = DataLoader(test_dataset,  batch_size=BATCH_SIZE, shuffle=False)

# ========== 3. 定义模型 ==========
class CNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)                      # 28→14→7
        self.fc1 = nn.Linear(64 * 7 * 7, 128)               # 展平后 64*7*7
        self.fc2 = nn.Linear(128, 10)
        self.dropout = nn.Dropout(0.5)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.relu(self.conv1(x))    # (B, 1, 28, 28) → (B, 32, 28, 28)
        x = self.pool(x)                # (B, 32, 14, 14)
        x = self.relu(self.conv2(x))    # (B, 64, 14, 14)
        x = self.pool(x)                # (B, 64, 7, 7)
        x = x.view(x.size(0), -1)       # 展平: (B, 64*7*7)
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)                 # 输出 logits，不加 Softmax
        return x

model = CNN().to(DEVICE)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=LR)

# ========== 4. 训练和验证 ==========
for epoch in range(EPOCHS):
    # --- 训练阶段 ---
    model.train()   # 开启 Dropout、BatchNorm 的训练行为
    train_loss = 0
    correct = 0
    total = 0

    for images, labels in train_loader:
        images, labels = images.to(DEVICE), labels.to(DEVICE)

        # 训练四步曲
        outputs = model(images)
        loss = criterion(outputs, labels)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        # 统计
        train_loss += loss.item()
        _, predicted = outputs.max(1)          # argmax
        total += labels.size(0)
        correct += predicted.eq(labels).sum().item()

    # --- 验证阶段 ---
    model.eval()    # 关闭 Dropout，冻结 BatchNorm
    test_loss = 0
    test_correct = 0
    test_total = 0

    with torch.no_grad():   # 不建计算图，省显存
        for images, labels in test_loader:
            images, labels = images.to(DEVICE), labels.to(DEVICE)
            outputs = model(images)
            loss = criterion(outputs, labels)

            test_loss += loss.item()
            _, predicted = outputs.max(1)
            test_total += labels.size(0)
            test_correct += predicted.eq(labels).sum().item()

    # --- 打印 ---
    print(f"Epoch [{epoch+1}/{EPOCHS}] | "
          f"Train Loss: {train_loss/len(train_loader):.4f} "
          f"Train Acc: {100.*correct/total:.2f}% | "
          f"Test Loss: {test_loss/len(test_loader):.4f} "
          f"Test Acc: {100.*test_correct/test_total:.2f}%")
```

### 8.3 `model.train()` 和 `model.eval()` 的区别

| | `model.train()` | `model.eval()` |
|---|---|---|
| **Dropout** | 正常工作（随机丢弃神经元） | 关闭（全部保留） |
| **BatchNorm** | 用当前 batch 的均值/方差更新 | 用训练时积累的全局均值/方差 |
| **什么时候用** | 训练循环内 | 验证/测试循环内 |

> ⚠️ 忘记切 `model.eval()` 的后果：验证结果波动大、不准确。

---

## 九、数据加载 Dataset & DataLoader

### 9.1 用现成的数据集

```python
from torchvision import datasets, transforms

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),                     # 自动把 [0,255] 归一化到 [0,1]
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])  # ImageNet 统计值
])

dataset = datasets.CIFAR10(root="./data", train=True,
                           download=True, transform=transform)
loader = DataLoader(dataset, batch_size=32, shuffle=True, num_workers=2)
```

### 9.2 自定义数据集

```python
from torch.utils.data import Dataset, DataLoader
from PIL import Image
import os

class CatDogDataset(Dataset):
    def __init__(self, image_dir, transform=None):
        self.image_paths = [os.path.join(image_dir, f)
                           for f in os.listdir(image_dir)]
        self.transform = transform

    def __len__(self):
        return len(self.image_paths)   # 必须实现

    def __getitem__(self, idx):
        img_path = self.image_paths[idx]
        image = Image.open(img_path).convert("RGB")
        # 假设文件名 "cat.0.jpg" → 标签 0, "dog.1.jpg" → 标签 1
        label = 0 if "cat" in os.path.basename(img_path) else 1

        if self.transform:
            image = self.transform(image)

        return image, label            # 必须返回 (数据, 标签)

# 使用
dataset = CatDogDataset("./cats_and_dogs", transform=transform)
loader = DataLoader(dataset, batch_size=32, shuffle=True)
```

### 9.3 DataLoader 常用参数

```python
DataLoader(
    dataset,
    batch_size=64,       # 每批多少样本
    shuffle=True,         # 训练集打乱，验证集 False
    num_workers=4,        # 用几个子进程加载数据（Windows 上小心设 >0 可能出问题）
    pin_memory=True,      # GPU 训练时设为 True，加速数据传输
    drop_last=True,       # 丢弃最后不足一个 batch 的数据（BatchNorm 要求 batch>1 时有用）
)
```

---

## 十、模型保存与加载

```python
# ========== 保存 ==========
# 方法 1：只保存参数（推荐，更轻量）
torch.save(model.state_dict(), "model_weights.pth")

# 方法 2：保存整个模型（不推荐，耦合性强）
torch.save(model, "model_full.pth")

# 保存 checkpoint（含优化器状态，方便恢复训练）
checkpoint = {
    "epoch": epoch,
    "model_state_dict": model.state_dict(),
    "optimizer_state_dict": optimizer.state_dict(),
    "loss": loss,
}
torch.save(checkpoint, "checkpoint.pth")

# ========== 加载 ==========
# 加载参数
model = CNN()                                    # 先建一个同结构的空模型
model.load_state_dict(torch.load("model_weights.pth"))
model.eval()                                     # 推理前切 eval 模式

# 恢复训练
checkpoint = torch.load("checkpoint.pth")
model.load_state_dict(checkpoint["model_state_dict"])
optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
start_epoch = checkpoint["epoch"] + 1
```

---

## 十一、GPU 使用

```python
# 检测 GPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# 模型搬到 GPU
model = model.to(device)    # model.to("cuda") 也行

# 数据搬到 GPU（必须在同一个 device 上！）
images = images.to(device)
labels = labels.to(device)

# 多 GPU 训练（最简单的方式）
if torch.cuda.device_count() > 1:
    model = nn.DataParallel(model)
```

> ⚠️ 模型和数据必须在**同一个设备**上，否则报错 `Expected all tensors to be on the same device`。

---

## 十二、常用技巧和常见坑

### 12.1 打印和调试

```python
# 查看模型参数量
total_params = sum(p.numel() for p in model.parameters())
trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
print(f"Total: {total_params:,} | Trainable: {trainable_params:,}")

# 打印每层输出形状
for name, param in model.named_parameters():
    print(f"{name:30} {str(list(param.shape)):20} {param.numel():,}")

# 用 torchinfo 看完整结构（需要 pip install torchinfo）
from torchinfo import summary
summary(model, input_size=(1, 1, 28, 28))   # (batch, channels, H, W)
```

### 12.2 梯度裁剪（防梯度爆炸）

```python
# RNN/LSTM 训练时常用
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
```

### 12.3 冻结层（迁移学习）

```python
# 冻结 backbone，只训练分类头
for param in model.backbone.parameters():
    param.requires_grad = False

# 优化器只传需要训练的层
optimizer = optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=0.001)
```

### 12.4 常见报错速查

| 报错 | 原因 | 解决 |
|------|------|------|
| `shape mismatch` | 输入/输出维度不匹配 | 打印 `x.shape`，检查每层 in/out |
| `Expected all tensors on same device` | 模型和数据不在同一个设备 | 都加 `.to(device)` |
| `RuntimeError: CUDA out of memory` | 显存不足 | 减小 batch_size；`torch.cuda.empty_cache()` |
| `CrossEntropyLoss received 2D target` | label 传成了 one-hot | 传整数标签：`labels = torch.tensor([0,1,2])` |
| `grad can be implicitly created only for scalar outputs` | `backward()` 只接受标量 | `loss` 没取标量；或用 `loss.backward(torch.ones_like(loss))` |
| `Can't call numpy() on Tensor that requires grad` | 带梯度的张量不能直接转 NumPy | 先 `.detach().cpu().numpy()` |

### 12.5 固定随机种子（可复现实验）

```python
import random
import numpy as np

def set_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True   # 牺牲一点速度换可复现
    torch.backends.cudnn.benchmark = False
```

---

## 十三、完整实战：手写数字识别（纯 MLP 版本）

一份可以直接复制粘贴运行的完整代码：

```python
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

# 配置
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
BATCH_SIZE, LR, EPOCHS = 128, 0.001, 5

# 数据
transform = transforms.Compose([transforms.ToTensor(),
                                transforms.Normalize((0.1307,), (0.3081,))])
train_loader = DataLoader(
    datasets.MNIST("./data", train=True,  download=True, transform=transform),
    batch_size=BATCH_SIZE, shuffle=True)
test_loader = DataLoader(
    datasets.MNIST("./data", train=False, download=True, transform=transform),
    batch_size=BATCH_SIZE, shuffle=False)

# 模型
class MLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Flatten(),              # (B, 1, 28, 28) → (B, 784)
            nn.Linear(784, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, 10),
        )

    def forward(self, x):
        return self.net(x)

model = MLP().to(DEVICE)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=LR)

# 训练
for epoch in range(EPOCHS):
    model.train()
    for images, labels in train_loader:
        images, labels = images.to(DEVICE), labels.to(DEVICE)
        optimizer.zero_grad()
        loss = criterion(model(images), labels)
        loss.backward()
        optimizer.step()

    # 验证
    model.eval()
    correct = 0
    with torch.no_grad():
        for images, labels in test_loader:
            images, labels = images.to(DEVICE), labels.to(DEVICE)
            pred = model(images).argmax(dim=1)
            correct += pred.eq(labels).sum().item()

    print(f"Epoch {epoch+1}: Test Accuracy = {100.*correct/len(test_loader.dataset):.2f}%")
```

训练 5 个 epoch 通常能达到 97%+ 的准确率。

---

## 十四、学习路线建议

```
1. 跑通上面的 MLP MNIST → 理解训练四步曲
2. 把 MLP 改成 CNN → 理解卷积层怎么替代全连接
3. 在 CIFAR-10 上训练 → 接触更复杂的图像分类
4. 学习 torchvision.models 的预训练模型 → 迁移学习
5. 写一个自定义 Dataset → 训练自己的数据
```

需要继续深入的概念（反向传播数学、激活函数原理、LSTM 机制等）见 [ML/一些疑惑解答](一些疑惑解答.md)。

---

## 速查卡片

| 操作 | 代码 |
|------|------|
| 创建网络 | `class Net(nn.Module)` + `__init__` + `forward` |
| 训练四步 | `loss → zero_grad → backward → step` |
| 损失函数 | `nn.CrossEntropyLoss()` (多分类) / `nn.MSELoss()` (回归) |
| 优化器 | `optim.Adam(model.parameters(), lr=0.001)` |
| 搬到 GPU | `model.to(device)` + `data.to(device)` |
| 训练模式 | `model.train()` |
| 推理模式 | `model.eval()` + `with torch.no_grad():` |
| 保存 | `torch.save(model.state_dict(), "xxx.pth")` |
| 加载 | `model.load_state_dict(torch.load("xxx.pth"))` |
| 获取预测类别 | `outputs.argmax(dim=1)` |
| 固定随机 | `torch.manual_seed(42)` |
