from wcferry import Wcf
import os
from datetime import datetime
import sys
import traceback
import time
import shutil

class WeChatImageMonitor:
    def __init__(self):
        try:
            print("正在初始化...")
            print("正在检查环境...")
            
            # 检查并复制 SDK 文件
            self.check_and_copy_sdk()
            
            print("正在连接微信...")
            self.wcf = Wcf()
            
            # 检查微信连接状态
            if not self.check_wechat_connection():
                print("错误：无法连接到微信，请确保：")
                print("1. 微信已经登录")
                print("2. 使用的是微信 3.9.2.23 版本")
                print("3. 已经安装 WeChatSetup.exe")
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

    def check_and_copy_sdk(self):
        """检查并复制 SDK 文件"""
        try:
            # 获取当前程序所在目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            # 检查 SDK 文件是否存在
            sdk_path = os.path.join(current_dir, "sdk.dll")
            if not os.path.exists(sdk_path):
                print("未找到 SDK 文件，尝试从 Python 包中复制...")
                
                # 从 Python 包目录复制 SDK 文件
                try:
                    import wcferry
                    wcferry_path = os.path.dirname(wcferry.__file__)
                    src_sdk = os.path.join(wcferry_path, "sdk.dll")
                    if os.path.exists(src_sdk):
                        shutil.copy2(src_sdk, sdk_path)
                        print("SDK 文件复制成功")
                    else:
                        raise Exception("无法找到 SDK 文件")
                except Exception as e:
                    raise Exception(f"复制 SDK 文件失败: {str(e)}")
            
            # 设置环境变量
            os.environ["PATH"] = current_dir + os.pathsep + os.environ.get("PATH", "")
            
        except Exception as e:
            raise Exception(f"SDK 检查失败: {str(e)}")

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