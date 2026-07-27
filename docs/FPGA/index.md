---
tags:
  - FPGA
  - 索引
created: 2026-05-25
---

# FPGA

这里记录 FPGA 开发相关知识。

## 信号处理基础

- [DFT 中的旋转因子 W 的理解](DFT中的旋转因子W的理解.md) — 旋转因子的定义、几何直观与 FPGA 实现

## 接口协议

常用串行通信协议的原理、时序、Verilog 实现：

- [UART 串行通信协议](UART串行通信协议.md) — 异步串口：原理、帧格式、收发 Verilog 代码
- [SPI 串行通信协议](SPI串行通信协议.md) — 同步高速：四线全双工、CPOL/CPHA 模式、Master/Slave 实现
- [I2C 串行通信协议](I2C串行通信协议.md) — 两线半双工：地址寻址、开漏上拉、仲裁机制、EEPROM 读写示例

## 芯片设计流程

- [数字芯片设计与验证全流程](数字芯片设计与验证全流程.md) — 从 Specification 到 Silicon 的五层抽象、验证手段、UPF 低功耗流程、FPGA 工程师视角

