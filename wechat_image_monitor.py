from wcferry import Wcf
import os
from datetime import datetime
import sys
import traceback
import time

class WeChatImageMonitor:
    def __init__(self):
        try:
            self.wcf = Wcf()
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
            input("按回车键退出...")
            sys.exit(1)
        
    def log_error(self, error_msg):
        """记录错误日志"""
        log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'error.log')
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(f"\n[{timestamp}] {error_msg}")
            if isinstance(error_msg, Exception):
                f.write(f"\n{traceback.format_exc()}")
            f.write("\n" + "="*50 + "\n")

    def create_folder(self, nickname):
        try:
            folder_path = os.path.join(self.base_path, nickname)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                print(f"Created folder for: {nickname}")
            return folder_path
        except Exception as e:
            self.log_error(f"创建文件夹失败: {str(e)}")
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
            return 1

    def on_message(self, msg):
        try:
            if msg.type == 3:  # 图片消息类型
                sender = self.wcf.get_info_by_wxid(msg.sender).name
                folder_path = self.create_folder(sender)
                if not folder_path:
                    return
                
                number = self.get_next_image_number(folder_path)
                image_data = self.wcf.get_msg_image(msg.id)
                
                if image_data:
                    file_ext = '.jpg'
                    save_path = os.path.join(folder_path, f"{number}{file_ext}")
                    
                    with open(save_path, 'wb') as f:
                        f.write(image_data)
                    print(f"已保存图片: {save_path}")
        except Exception as e:
            self.log_error(f"处理消息失败: {str(e)}")

    def start(self):
        try:
            print("开始监控微信图片消息...")
            print(f"保存路径: {self.base_path}")
            
            if not os.path.exists(self.base_path):
                os.makedirs(self.base_path)
                print(f"创建主文件夹: {self.base_path}")
            
            self.wcf.enable_receiving_msg()
            self.wcf.register_msg_callback(self.on_message)
            
            print("\n程序正在运行中，请不要关闭此窗口...")
            print("按 Ctrl+C 停止程序")
            
            while True:
                time.sleep(1)  # 减少 CPU 使用率
                
        except Exception as e:
            self.log_error(f"程序运行错误: {str(e)}")
            print("\n发生错误，请查看 error.log 文件")
        finally:
            try:
                self.wcf.cleanup()
            except:
                pass
            input("\n按回车键退出...")

if __name__ == "__main__":
    try:
        monitor = WeChatImageMonitor()
        monitor.start()
    except Exception as e:
        with open('error.log', 'a', encoding='utf-8') as f:
            f.write(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 程序启动失败: {str(e)}\n")
            f.write(traceback.format_exc())
        input("程序启动失败，请查看 error.log 文件。按回车键退出...") 