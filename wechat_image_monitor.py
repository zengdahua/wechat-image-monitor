import os
import sys
import time
import traceback
from datetime import datetime
from wcferry import Wcf, WxMsg

class WeChatImageMonitor:
    def __init__(self):
        try:
            print("正在初始化...")
            print("正在检查环境...")
            print("=" * 50)
            print("使用说明：")
            print("1. 确保已安装微信 3.9.11.25 版本")
            print("2. 以管理员身份运行本程序")
            print("=" * 50)
            
            # 检查微信安装路径
            self.check_wechat_installation()
            
            print("正在连接微信...")
            # 使用本地的 wcferry 库
            self.wcf = Wcf(debug=False)
            
            # 检查微信连接状态
            if not self.check_wechat_connection():
                print("错误：无法连接到微信")
                input("按回车键退出...")
                sys.exit(1)
                
            self.base_path = "C:\\photo"
            
            # 检查并创建保存目录
            if not os.path.exists(self.base_path):
                os.makedirs(self.base_path)
                
        except Exception as e:
            self.log_error(f"初始化失败: {str(e)}")
            print(f"初始化失败: {str(e)}")
            input("按回车键退出...")
            sys.exit(1)

    def check_wechat_installation(self):
        """检查微信安装路径"""
        try:
            wechat_path = "C:\\Program Files\\Tencent\\WeChat\\"
            if not os.path.exists(wechat_path):
                print("警告：未找到默认微信安装路径")
                return False
            
            print(f"找到微信安装路径: {wechat_path}")
            return True
            
        except Exception as e:
            self.log_error(f"检查微信安装路径失败: {str(e)}")
            print(f"检查微信安装路径失败: {str(e)}")
            return False

    def check_wechat_connection(self):
        """检查微信连接状态"""
        try:
            print("正在测试微信连接...")
            if not self.wcf.is_login():
                print("错误: 微信未登录")
                return False

            self_wxid = self.wcf.get_self_wxid()
            if not self_wxid:
                print("错误: 无法获取微信 ID")
                return False

            print(f"微信 ID: {self_wxid}")
            
            try:
                user_info = self.wcf.get_info_by_wxid(self_wxid)
                print(f"已连接到微信账号: {user_info.get('name', 'Unknown')}")
            except Exception as e:
                print(f"警告: 无法获取用户信息 ({str(e)})")
                print("继续运行...")

            return True

        except Exception as e:
            self.log_error(f"微信连接测试失败: {str(e)}")
            print(f"微信连接测试失败: {str(e)}")
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

    def start(self):
        try:
            print("开始监控微信图片消息...")
            print(f"保存路径: {self.base_path}")
            
            print("正在启用消息接收...")
            try:
                self.wcf.enable_receiving_msg()
                print("消息接收已启用")
                
                while True:
                    try:
                        msg = self.wcf.get_msg()
                        if msg and msg.type == 3:  # 图片消息
                            print(f"\n收到图片消息: {msg.id}")
                            try:
                                # 获取发送者信息
                                sender_name = msg.sender
                                try:
                                    sender_info = self.wcf.get_info_by_wxid(msg.sender)
                                    if sender_info:
                                        sender_name = sender_info.get('name', msg.sender)
                                except:
                                    pass
                                
                                folder_path = os.path.join(self.base_path, sender_name)
                                if not os.path.exists(folder_path):
                                    os.makedirs(folder_path)
                                
                                try:
                                    # 下载图片 - 使用新的 API
                                    image_data = self.wcf.get_image(msg.id)
                                    if image_data:
                                        number = len([f for f in os.listdir(folder_path) if f.endswith('.jpg')]) + 1
                                        save_path = os.path.join(folder_path, f"{number}.jpg")
                                        
                                        # 保存图片
                                        with open(save_path, 'wb') as f:
                                            f.write(image_data)
                                        print(f"已保存图片: {save_path}")
                                    else:
                                        print("获取图片失败")
                                except Exception as e:
                                    print(f"下载图片失败: {e}")
                                    # 尝试备用方法
                                    try:
                                        print("尝试备用方法下载图片...")
                                        image_data = self.wcf.download_image(msg.id)
                                        if image_data:
                                            number = len([f for f in os.listdir(folder_path) if f.endswith('.jpg')]) + 1
                                            save_path = os.path.join(folder_path, f"{number}.jpg")
                                            
                                            with open(save_path, 'wb') as f:
                                                f.write(image_data)
                                            print(f"已保存图片: {save_path}")
                                        else:
                                            print("获取图片数据失败")
                                    except Exception as e2:
                                        print(f"备用方法下载图片失败: {e2}")
                            except Exception as e:
                                print(f"处理图片消息失败: {e}")
                                
                        time.sleep(0.1)
                            
                    except KeyboardInterrupt:
                        print("\n收到停止信号，程序退出...")
                        break
                    except Exception as e:
                        print(f"处理消息失败: {e}")
                        time.sleep(0.5)
                        
            except Exception as e:
                print(f"启用消息接收时出错: {e}")
                return
                
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
    monitor = WeChatImageMonitor()
    monitor.start() 