#!/bin/bash

# 确保在正确的目录
cd "$(dirname "$0")"

# 使用PyInstaller打包
pyinstaller wcferry.spec --clean --workpath build --distpath dist

# 创建zip包（方便传输）
cd dist
zip -r WeChatFerry-Windows.zip WeChatFerry 