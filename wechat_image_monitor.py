from wcferry import Wcf
import os
from datetime import datetime
import sys
import traceback
import time
import shutil
import wcferry
import base64

class WeChatImageMonitor:
    def __init__(self):
        try:
            print("正在初始化...")
            print("正在检查环境...")
            print("=" * 50)
            print("使用说明：")
            print("1. 确保已安装微信 3.9.11.25 版本")
            print("2. 以管理员身份安装 WeChatSetup.exe")
            print("3. 以管理员身份运行本程序")
            print("=" * 50)
            
            # 检查微信安装路径
            self.check_wechat_installation()
            
            # 设置 SDK 路径
            if not self.setup_sdk():
                print("\n错误：未能找到或复制 sdk.dll 文件")
                print("请确保：")
                print("1. 已经安装最新版本的 WeChatSetup")
                print("2. 微信版本为 3.9.11.25")
                print("3. 以管理员身份运行本程序")
                input("按回车键退出...")
                sys.exit(1)
            
            print("正在连接微信...")
            self.wcf = Wcf()
            
            # 检查微信连接状态
            if not self.check_wechat_connection():
                print("错误：无法连接到微信，请确保：")
                print("1. 微信已经登录")
                print("2. 使用的是微信 3.9.11.25 版本")
                print("3. 已经安装最新版本的 WeChatSetup")
                input("按回车键退出...")
                sys.exit(1)
                
            self.base_path = "C:\\photo"
            print("WeChat Image Monitor Started...")
            print("=" * 50)
            print("请确保：")
            print("1. 已经以管理员身份运行")
            print("2. 微信已经登录")
            print("3. 已安装 WeChatSetup.exe")
            print("=" * 50)
            
        except Exception as e:
            self.log_error(f"初始化失败: {str(e)}")
            print(f"初始化失败: {str(e)}")
            input("按回车键退出...")
            sys.exit(1)

    def check_wechat_installation(self):
        """检查微信安装路径"""
        try:
            # 常见的微信安装路径
            possible_paths = [
                "C:\\Program Files (x86)\\Tencent\\WeChat\\",
                "C:\\Program Files\\Tencent\\WeChat\\",
                os.path.expanduser("~\\AppData\\Local\\Tencent\\WeChat\\"),
                "D:\\Program Files (x86)\\Tencent\\WeChat\\",
                "D:\\Program Files\\Tencent\\WeChat\\",
                "D:\\WeChat\\"
            ]
            
            wechat_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    if os.path.exists(os.path.join(path, "WeChat.exe")):
                        wechat_path = path
                        break
            
            if not wechat_path:
                print("警告：未找到微信安装路径")
                print("请确保微信已正确安装")
                print("推荐的安装位置：")
                for path in possible_paths:
                    print(f"- {path}")
                return False
            
            print(f"找到微信安装路径: {wechat_path}")
            # 将微信路径添加到环境变量
            os.environ["PATH"] = wechat_path + os.pathsep + os.environ.get("PATH", "")
            return True
            
        except Exception as e:
            self.log_error(f"检查微信安装路径失败: {str(e)}")
            print(f"检查微信安装路径失败: {str(e)}")
            return False

    def setup_sdk(self):
        """设置 SDK 环境"""
        try:
            # 获取 exe 所在目录
            if getattr(sys, 'frozen', False):
                # 如果是打包后的 exe
                current_dir = os.path.dirname(sys.executable)
            else:
                # 如果是 Python 脚本
                current_dir = os.path.dirname(os.path.abspath(__file__))
            
            print(f"程序运行目录: {current_dir}")

            # 需要检查的文件列表
            required_files = ['sdk.dll', 'spy.dll', 'spy_debug.dll']
            
            # 检查文件是否存在
            missing_files = []
            for file_name in required_files:
                file_path = os.path.join(current_dir, file_name)
                if not os.path.exists(file_path):
                    missing_files.append(file_name)

            if missing_files:
                print("\n以下文件缺失，请将它们复制到程序目录:")
                for f in missing_files:
                    print(f"- {f}")
                print(f"\n目标目录: {current_dir}")
                return False

            # 设置环境变量，将当前目录放在最前面
            os.environ["PATH"] = current_dir + os.pathsep + os.environ.get("PATH", "")
            
            # 尝试预加载 DLL
            try:
                import ctypes
                for dll_file in required_files:
                    dll_path = os.path.join(current_dir, dll_file)
                    try:
                        ctypes.CDLL(dll_path)
                        print(f"成功加载: {dll_file}")
                    except Exception as e:
                        print(f"加载 {dll_file} 失败: {e}")
                        return False
            except Exception as e:
                print(f"DLL 预加载失败: {e}")
                return False

            print("所有必需文件已就绪")
            return True
            
        except Exception as e:
            self.log_error(f"设置 SDK 环境失败: {str(e)}")
            print(f"设置 SDK 环境失败: {str(e)}")
            return False

    def check_wechat_connection(self):
        """检查微信连接状态"""
        try:
            # 尝试获取自己的信息作为连接测试
            self.wcf.enable_receiving_msg()
            return True
        except Exception as e:
            self.log_error(f"微信连接测试失败: {str(e)}")
            return False
            
    def log_error(self, error_msg):
        """记录错误日志"""
        try:
            log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'error.log')
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(f"\n[{timestamp}] {error_msg}")
                if isinstance(error_msg, Exception):
                    f.write(f"\n{traceback.format_exc()}")
                f.write("\n" + "="*50 + "\n")
        except Exception as e:
            print(f"写入日志失败: {str(e)}")

    def create_folder(self, nickname):
        try:
            folder_path = os.path.join(self.base_path, nickname)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                print(f"Created folder for: {nickname}")
            return folder_path
        except Exception as e:
            self.log_error(f"创建文件夹失败: {str(e)}")
            print(f"创建文件夹失败: {str(e)}")
            return None

    def get_next_image_number(self, folder_path):
        try:
            existing_files = [f for f in os.listdir(folder_path) if f.endswith('.jpg') or f.endswith('.png')]
            if not existing_files:
                return 1
            numbers = [int(f.split('.')[0]) for f in existing_files]
            return max(numbers) + 1
        except Exception as e:
            self.log_error(f"获取图片序号失败: {str(e)}")
            print(f"获取图片序号失败: {str(e)}")
            return 1

    def on_message(self, msg):
        try:
            if msg.type == 3:  # 图片消息类型
                print(f"收到新图片消息...")
                sender = self.wcf.get_info_by_wxid(msg.sender).name
                print(f"发送者: {sender}")
                
                folder_path = self.create_folder(sender)
                if not folder_path:
                    return
                
                number = self.get_next_image_number(folder_path)
                print(f"正在下载图片...")
                image_data = self.wcf.get_msg_image(msg.id)
                
                if image_data:
                    file_ext = '.jpg'
                    save_path = os.path.join(folder_path, f"{number}{file_ext}")
                    
                    with open(save_path, 'wb') as f:
                        f.write(image_data)
                    print(f"已保存图片: {save_path}")
                else:
                    print("获取图片数据失败")
        except Exception as e:
            self.log_error(f"处理消息失败: {str(e)}")
            print(f"处理消息失败: {str(e)}")

    def start(self):
        try:
            print("开始监控微信图片消息...")
            print(f"保存路径: {self.base_path}")
            
            if not os.path.exists(self.base_path):
                os.makedirs(self.base_path)
                print(f"创建主文件夹: {self.base_path}")
            
            print("正在启用消息接收...")
            self.wcf.enable_receiving_msg()
            print("正在注册消息回调...")
            self.wcf.register_msg_callback(self.on_message)
            
            print("\n程序正在运行中，请不要关闭此窗口...")
            print("按 Ctrl+C 停止程序")
            
            while True:
                time.sleep(1)  # 减少 CPU 使用率
                
        except Exception as e:
            self.log_error(f"程序运行错误: {str(e)}")
            print(f"\n发生错误: {str(e)}")
            print("请查看 error.log 文件获取详细信息")
        finally:
            try:
                print("\n正在清理资源...")
                self.wcf.cleanup()
            except:
                pass
            input("\n按回车键退出...")

if __name__ == "__main__":
    try:
        print("正在启动程序...")
        monitor = WeChatImageMonitor()
        monitor.start()
    except Exception as e:
        print(f"程序启动失败: {str(e)}")
        with open('error.log', 'a', encoding='utf-8') as f:
            f.write(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 程序启动失败: {str(e)}\n")
            f.write(traceback.format_exc())
        input("程序启动失败，请查看 error.log 文件。按回车键退出...") 