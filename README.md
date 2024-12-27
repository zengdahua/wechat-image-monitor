# WeChat Image Monitor

自动保存微信聊天中的图片。

## 使用要求

1. 微信版本：3.9.11.25
   - 下载链接：https://github.com/tom-snow/wechat-windows-versions/releases/download/v3.9.11.25/WeChatSetup-3.9.11.25.exe

2. wcferry 组件
   - 下载链接：https://github.com/lich0821/WeChatFerry/releases/tag/v39.3.3
   - 下载 v39.3.3.zip 并解压，获取以下文件：
     - sdk.dll
     - spy.dll
     - spy_debug.dll

3. 管理员权限

## 安装步骤

1. 安装微信 3.9.11.25
   - 如果已安装其他版本，请先卸载
   - 安装完成后登录微信

2. 准备 DLL 文件
   - 解压下载的 v39.3.3.zip
   - 获取三个 DLL 文件：
     - sdk.dll
     - spy.dll
     - spy_debug.dll

## 使用方法

1. 下载最新发布的程序包
2. 解压后确保以下文件在同一目录：
   - wechat_image_monitor.exe
   - sdk.dll
   - spy.dll
   - spy_debug.dll
3. 以管理员身份运行 wechat_image_monitor.exe
4. 图片将自动保存到 C:\photo 目录

## 注意事项

- 程序运行时请不要关闭命令行窗口
- 图片按发送者分类保存
- 如遇问题，查看 error.log 获取详细信息
