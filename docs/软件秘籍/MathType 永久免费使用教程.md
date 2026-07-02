---
title: "MathType 永久免费使用教程"
author:
  - "[[vi226035]]"
published: 2026-05-09
created: 2026-07-02
tags:
  - "软件"
  - "工具"
  - "MathType"
---

# MathType 永久免费使用教程

> 通过删除注册表配置项，无限次重置 MathType 30 天试用期。适用于 **Windows 系统**，MathType 7.11 系列版本。

## 测试环境

- 操作系统：Windows 11
- 办公软件：WPS（Microsoft Office 同理）
- MathType 版本：7.11

![[../kb_material/软件秘籍_image/mathtype_main.jpg]]

## 操作步骤

### 第一步：打开注册表编辑器

按 `Win + R` 打开运行窗口：

![[../kb_material/软件秘籍_image/mathtype_run.jpg]]

输入 `regedit`，回车，打开系统注册表：

![[../kb_material/软件秘籍_image/mathtype_regedit.jpg]]

### 第二步：删除 MathType 配置项

找到以下路径并**删除整个 `Options7.4` 文件夹**：

```
HKEY_CURRENT_USER\Software\Install Options\Options7.4
```

该文件夹存储的是 MathType 的安装配置信息，可以安全删除。

![[../kb_material/软件秘籍_image/mathtype_registry1.jpg]]

### 第三步：删除证书信息

找到证书存放路径，将目录下的证书**全部删除**：

```
HKEY_CURRENT_USER\Software\JavaSoft\Prefs\com\wiris\editor\license
```

这些只是许可证验证文件，可以安全删除。

![[../kb_material/软件秘籍_image/mathtype_registry2.jpg]]

### 第四步：重启 MathType

完成以上操作后，**关闭并重新打开 MathType**，试用期即被重置回 30 天。

![[../kb_material/软件秘籍_image/mathtype_reset.jpg]]

## 温馨提示

- 建议每隔 **20 多天**操作一次，避免到期影响使用。
- MathType 更新大版本后，注册表路径可能变化，需自行调整。
