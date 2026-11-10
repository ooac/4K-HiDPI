---
name: uu-headless-mac-4k
description: 为通过网易 UU 控制的无屏 Mac mini 配置 BetterDisplay 4K HiDPI，修复 Dock 丢失和虚拟屏断开；按需安装随登录启动的自动修复程序，应对 UU 重连更换屏幕标识。
---

# 无显示器 Mac mini：UU 远程 4K HiDPI

在被控 Mac 上操作。默认目标是实际渲染 3840×2160、桌面逻辑尺寸 1920×1080、60Hz。用户要求其他缩放时按其要求调整。

区分三层：macOS 渲染分辨率、UU 编码/传输分辨率、控制端显示缩放。系统输出 4K 不能证明 UU 传输了 4K，也不能证明用户看到的文字清晰。不要承诺永远正常或未经测试的重启/重连可靠性。

## 先读当前状态

使用终端读取，不需要控制端账号、连接密码或设备验证码：

```sh
system_profiler SPDisplaysDataType
sw_vers
ls /Applications
defaults read com.apple.dock orientation
defaults read com.apple.dock autohide
```

只在需要时读取硬件型号，避免输出整份硬件身份信息。确认操作对象确实是被控 Mac，而不是带实体 4K 显示器的控制端。

若 BetterDisplay 已安装，优先使用其自带 CLI。不同版本能力可能变化，先读取本机帮助和设备清单：

```sh
/Applications/BetterDisplay.app/Contents/MacOS/BetterDisplay help
/Applications/BetterDisplay.app/Contents/MacOS/BetterDisplay get -identifiers
```

`get -list` 不是本次验证过的有效命令；设备列表应使用 `get -identifiers`。保存修改前的显示输出、分辨率、主屏和镜像关系，供恢复。不要把此文中的 displayID、tagID 或 UUID 当作另一台机器的真实值；连接后 displayID 可能变化。设备名称有重复时用现场获取的唯一标识。

未安装 BetterDisplay 时，从 [官方仓库](https://github.com/waydabber/BetterDisplay) 确认当前兼容版本及安装方式。遵循当前环境的安装权限规则；不要购买许可证、绕过激活或默认开启试用。若 CLI 不响应，通过可用的原生 UI 工具检查应用是否运行、集成接口是否启用或存在提示，不要无限重试。

## 建立或复用虚拟屏幕

优先复用用户已有的适合的虚拟屏幕，不重复创建。以下使用唯一名称 `Remote 4K`，执行前根据实际设备调整。命令逐步执行并检查退出码，出错立即检查原因，不要在中间步骤失败后继续修改。

仅在没有可复用屏幕时创建：

```sh
/Applications/BetterDisplay.app/Contents/MacOS/BetterDisplay create -type=VirtualScreen -virtualScreenName='Remote 4K' -aspectWidth=16 -aspectHeight=9 -useResolutionList=on -resolutionList=1920x1080,2560x1440,3840x2160 -virtualScreenHiDPI=on
```

配置前检查下面的“关联导致自动断开”规则，确保无屏常驻桌面不会依赖临时 UU 显示器的在线状态。执行连接命令后先重新读取设备列表及系统显示输出，确认虚拟屏仍在线，再设置桌面逻辑尺寸及 HiDPI：

```sh
/Applications/BetterDisplay.app/Contents/MacOS/BetterDisplay set -name='Remote 4K' -connected=on
/Applications/BetterDisplay.app/Contents/MacOS/BetterDisplay get -identifiers
system_profiler SPDisplaysDataType
/Applications/BetterDisplay.app/Contents/MacOS/BetterDisplay set -name='Remote 4K' -resolution=1920x1080 -hiDPI=on
/Applications/BetterDisplay.app/Contents/MacOS/BetterDisplay set -name='Remote 4K' -main=on
system_profiler SPDisplaysDataType
```

**关键：** `-resolution=1920x1080 -hiDPI=on` 才是这里的 4K 渲染目标。`-resolution=3840x2160 -hiDPI=on` 可能变成实际 7680×4320、逻辑 3840×2160，让字体很小。不要把逻辑 4K HiDPI 当成实际 4K。

默认保留原来的可用显示路径，先验证新屏已在线。不要重启 UU、退出 BetterDisplay、注销或重启电脑来做未经协调的测试，这可能中断唯一的远程连接。

## 关联导致自动断开：4K 再次消失时优先检查

已验证的故障：系统只剩 `Display` / `Generic Display` 普通 1920×1080；BetterDisplay 仍列出 `Remote 4K`，但 displayID 为 0。执行 `connected=on` 返回成功，屏幕却很快再次离线，后续分辨率命令失败。此时不要重复创建虚拟屏、连续重试连接，或仅凭退出码宣布恢复。

2026-09-14 在本机发现：Remote 4K 关联 `UU远程 1`，并启用了“自动连接虚拟屏幕”。该选项实际根据关联屏幕状态**自动连接和断开**；当 UU 屏不在线时，它会关闭 Remote 4K。关闭这项联动后，原有虚拟屏成功恢复 4K。此结论来自设置界面及修改后系统输出，不能未经检查套用为所有机器的原因。

使用 BetterDisplay 自带接口打开设置（先确认当前版本 help 支持）：

```sh
/Applications/BetterDisplay.app/Contents/MacOS/BetterDisplay set -settingsWindow=on
```

通过原生 UI 打开 **显示器 → Remote 4K → 已关联显示器 → 关联设置**，检查关联对象的在线状态和规则。对于本技能的无屏常驻桌面目标，将“自动连接虚拟屏幕”（说明为根据关联显示器状态自动连接/断开）关闭，读回 UI 确认 off，然后手动连接原有虚拟屏并重新设置 HiDPI。不要打开“当所有关联屏幕离线时，自动连接虚拟屏幕”：其说明还包含关联屏恢复在线时关闭，这同样不适合常驻桌面。

保留用户其他有用的关联及镜像设置；修复自动断开不要求解除全部关联。镜像桌面与按关联对象在线状态控制连接是不同设置，不要为修复 Dock 顺便打开连接联动。若用户明确要求随另一块屏幕出现/消失的副屏行为，保留其意图而不是一律关闭联动。

若 UI 工具提示应用标识不唯一（应用目录和安装磁盘映像各有一份），用 `/Applications/BetterDisplay.app` 完整路径选择已安装应用，不必删除或卸载另一份。界面元素变化后重新读取 UI，不能复用旧元素编号。

如果联动已关闭而仍无法保持连接，继续检查应用提示、版本和其他连接规则，不宣称已找到相同原因。不要猜测偏好键写入。只读偏好可用于定位，但 UI 和系统输出才用于确认修复。

## UU 创建了另一块虚拟屏幕时

UU 连接或重连可能出现 `UU远程 1` 等新屏。再次发现设备，不能假定该名称必定存在。若用户需要的是单桌面远程使用，让 UU 屏镜像 BetterDisplay 的主屏，避免形成扩展桌面，把右侧 Dock 留在另一块屏幕上。用户明确需要多屏时不要强制镜像。

本次在 BetterDisplay 4.0.4 / M4 Mac mini 上验证的方向如下：

```sh
/Applications/BetterDisplay.app/Contents/MacOS/BetterDisplay set -name='Remote 4K' -mirror=on -targetName='UU远程 1'
system_profiler SPDisplaysDataType
```

此命令应使 **Remote 4K 成为 Master Mirror**，UU 屏成为 Hardware Mirror。反方向曾使 UU 的 1080p 成为镜像源，并将整个桌面降到普通 1080p。**不能仅凭 CLI 返回成功就认定方向或分辨率正确。**

如方向错误，按当前版本帮助解除刚建立的镜像，再恢复 Remote 4K 的 1920×1080 HiDPI 和主屏状态，按上述方向重新建立镜像。每次改变关系后读取系统输出。若仍错误，停止反复切换，检查系统显示器设置的镜像优化来源或版本文档。不要通过删除所有虚拟屏来“重置”。

## 验收、持久化与重连

系统输出应明确显示：

- Remote 4K：Resolution 3840×2160；UI Looks like 1920×1080 @ 60Hz；Main Display Yes。
- 若 UU 屏存在且使用单桌面镜像：两块屏幕均为实际 4K、逻辑 1080p；Remote 4K 为 Master Mirror。
- 只有 Remote 4K 在线且 Mirror Off 也可以正常；UU 会话不一定创建独立的 UU 显示器。不要因 UU 屏缺席就断言会话未连接，也不要凭空创建 UU 屏或强制镜像 Generic Display。是否完成远程验收取决于实际会话和用户观感。

检查 BetterDisplay 的登录自动启动以及虚拟屏幕连接状态保存，可用应用设置，或用 `sfltool dumpbtm` 只筛选 BetterDisplay 条目读取启动状态。通过受支持的 UI/接口配置，不直接猜测偏好键写入。用户要求自动修复、长期保持或解决反复重连故障时，按下面的“安装自动修复”执行；只要求一次检查或临时修复时不额外安装后台服务。

验收还需确认常驻虚拟屏的自动连接/断开联动已关闭。自启动开启不代表虚拟屏不会被关联规则自动关闭。恢复后再次读取系统状态确认屏幕没有立刻离线；这不能替代用户实际重连测试。

可选的 `protectResolution` 属于 Pro 功能：只有现场确认功能可用且读回或 UI 验证成功时才说已保护分辨率。CLI 的成功退出码本身不够；曾出现返回成功但读取值异常的情况。不把 Pro 功能作为基础配置的前提。

尽可能通过原生 UI 检查完整桌面和 Dock。单独的 Finder 窗口截图无法证明 Dock 是否可见；不要把 Dock 的 right / autohide=false 偏好值当成可见性证据。

让用户在控制端断开再重连，并在其回复后重新读取系统状态。不要自己断开用户的唯一远程会话。记录实际是否保留缩放、主屏和镜像，不重复宣称未经验证的状态。重连测试通过只证明这次重连；重启、升级后未测试就明说。

## 安装自动修复

UU 重连可能创建**名字相同但 UUID、serial、tagID 均不同**的新虚拟屏。旧镜像关系不一定自动沿用。关闭关联断开规则只解决 4K 屏掉线，不能解决新 UU 屏变成扩展桌面的问题。

本技能附带 [scripts/repair.py](scripts/repair.py) 和 [scripts/install.py](scripts/install.py)。前者每次发现当前屏幕，健康时不修改；异常时恢复 Remote 4K 的 1920×1080 HiDPI、主屏和到当前 UU 屏的镜像。目标 UU 屏必须符合名称前缀 `UU远程`、vendor `21828` 且在线，不绑定此机器的 UUID 或 tagID。后者为当前用户生成路径并安装每 15 秒执行一次的 LaunchAgent，无需 sudo、定时对话任务或账号密码。

### 前提与安装

先完成上面的手动配置、关闭自动断开联动，并确认系统基线健康。此脚本适用默认单桌面目标、`Remote 4K` 唯一名称、BetterDisplay 位于 `/Applications` 的场景。如果用户使用其他虚拟屏名称、分辨率、多屏策略或设备标识格式，应先调整脚本并验证，不能直接安装覆盖其意图。脚本不安装 BetterDisplay，不创建虚拟屏，也不自动更改关联 UI。

确认目标 Mac 有可执行的 Python 3。安装器记录当前 Python 的绝对路径，因此使用长期保留的解释器，不使用临时 venv。未安装时先按当前环境规则取得可用运行时，不能假定每台 Mac 都自带 Python。脚本仅需标准库。

以下路径相对本技能文件夹，执行时展开为实际绝对路径：

```sh
python3 scripts/repair.py --check
python3 scripts/install.py --dry-run
python3 scripts/install.py
```

`--check` 和 `--dry-run` 不改显示设置、不安装服务。正式安装先验证健康基线，再复制程序、生成 plist、加载服务；若同标签服务已加载，先卸载旧服务再更新，不创建重复后台任务。不要复制原电脑的 plist（其中有用户名和解释器绝对路径）。安装失败应显示具体错误并处理，不能说安装成功。

安装位置：

- 程序：`~/Library/Application Support/UU4KRepair/repair.py`
- LaunchAgent：`~/Library/LaunchAgents/local.mc.uu4k-repair.plist`，标签固定用于兼容此前版本，与用户名无关。
- 日志：`~/Library/Logs/UU4KRepair/repair.log` 和 `error.log`
- 故障暂停标记：`~/Library/Application Support/UU4KRepair/paused-error.txt`

### 验证与故障处理

检查 `launchctl print gui/$(id -u)/local.mc.uu4k-repair` 的 interval、runs 和 last exit code。周期性服务正常等待时显示 `not running`，不代表被禁用。还需检查错误日志和暂停标记：暂停后的后续空运行可返回 0，不能只看最后退出码。

本机曾实测：解除镜像后，后台程序在下一检查周期自动恢复了两屏 4K HiDPI 镜像。其他机器仍要验证，不能把此测试当作所有机器均通过。先运行 [scripts/test_repair.py](scripts/test_repair.py) 验证健康状态无修改、新屏 tagID 动态发现及错误检测，再在适当时进行故障模拟或请用户真实重连。不要自己断开唯一远程会话。用户重连后等待约 20 秒，再检查系统分辨率、镜像和 Dock；调度及系统忙碌可能延迟执行，不承诺严格 15 秒完成。

程序遇到命令错误、数据错误或修复后验证失败，会将具体错误写入日志及暂停标记，停止后续自动修改，避免持续闪屏。它不是无限自愈：应用未就绪、关联规则反复断开、版本改变等都可能需要人工诊断。发现暂停时先读取标记、解决根因、手动恢复健康基线，再将标记重命名保存，然后用 `launchctl kickstart gui/$(id -u)/local.mc.uu4k-repair` 恢复。不要未经分析删除标记形成重试循环。

### 暂停或移除

用户要临时使用扩展屏、修改目标缩放或停止自动修复时，先执行：

```sh
launchctl bootout gui/$(id -u)/local.mc.uu4k-repair
```

要跨登录停用，将对应 plist 移出 `~/Library/LaunchAgents` 保存。只卸载后台修复服务，不退出 BetterDisplay、不删除虚拟屏，当前桌面继续保留。卸载后再按用户意图调整布局。更新技能文件不会自动升级已安装的后台程序；只有用户要求升级服务时重新运行安装器，并重新验收。

## 仍然模糊时

先重新读取系统分辨率。如果系统状态正确，不继续盲目提高渲染到 8K，也不关闭 HiDPI。

检查**控制端** UU 的画质菜单及实际连接/性能统计，重点核对视频分辨率、画质档位，以及窗口是否适配缩放或裁切。按当前界面选择最高合适画质，不虚构菜单名称、码率或编解码设置。另一台电脑不可访问时，请用户提供对应菜单/统计截图；被控端锁定界面不能提供控制端传输参数，也不需要解锁账号来猜测这些参数。

在控制端检查全屏/适配模式、显示器实际分辨率与 macOS 缩放，区分压缩模糊与窗口缩放。最终分别报告“已验证的系统输出”“已验证的远程传输”“用户实际观感”，缺少哪层证据就明确说明。

## 恢复与范围

修改导致更差时，根据修改前记录恢复分辨率、主屏及镜像关系。先恢复并验证可用显示路径，再断开本次新增的虚拟屏；不要直接退出 BetterDisplay 或删除其他屏幕。仅处理当前用户授权的显示问题，不改网络、安全设置、UU 账号或远程权限。

CLI 参考：[BetterDisplay 官方集成文档](https://github.com/waydabber/BetterDisplay/wiki/Integration-features,-CLI)。以已安装版本的 `help` 和现场系统验证为准。
