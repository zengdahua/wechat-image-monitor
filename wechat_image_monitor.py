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
            print("2. 以管理员身份运行本程序")
            print("=" * 50)
            
            # 检查微信安装路径
            self.check_wechat_installation()
            
            print("正在连接微信...")
            self.wcf = Wcf(debug=False)  # 关闭调试模式以提高速度
            
            # 检查微信连接状态
            if not self.check_wechat_connection():
                print("错误：无法连接到微信")
                input("按回车键退出...")
                sys.exit(1)
                
            self.base_path = "C:\\photo"
            
            # 检查并设置目录权限
            if not self.check_and_create_photo_dir():
                print("\n错误：无法访问或创建保存目录")
                input("按回车键退出...")
                sys.exit(1)
            
            print("WeChat Image Monitor Started...")
            
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

    def check_wechat_connection(self):
        """检查微信连接状态"""
        try:
            print("正在测试微信连接...")
            # 检查微信是否登录
            if not self.wcf.is_login():
                print("错误: 微信未登录")
                return False

            # 获取自己的微信 ID
            self_wxid = self.wcf.get_self_wxid()
            if not self_wxid:
                print("错误: 无法获取微信 ID")
                return False

            print(f"微信 ID: {self_wxid}")
            
            # 获取用户信息 - 修复参数问题
            try:
                user_info = self.wcf.get_user_info()  # 不传参数
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
        """处理接收到的消息"""
        try:
            print(f"\n收到新消息，类型: {msg.type}")
            
            if msg.type == 3:  # 图片消息类型
                print(f"收到新图片消息...")
                print(f"消息ID: {msg.id}")
                print(f"发送者ID: {msg.sender}")
                
                try:
                    # 修改获取用户信息的方式
                    sender_name = msg.sender
                    try:
                        sender_info = self.wcf.get_user_info()  # 不传参数
                        if sender_info:
                            sender_name = sender_info.get('name', msg.sender)
                    except:
                        pass
                    print(f"发送者昵称: {sender_name}")
                    
                    folder_path = self.create_folder(sender_name)
                    if not folder_path:
                        print("创建文件夹失败")
                        return
                    
                    print(f"保存目录: {folder_path}")
                    number = self.get_next_image_number(folder_path)
                    print(f"图片序号: {number}")
                    
                    print(f"正在下载图片...")
                    try:
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
                        print(f"下载图片失败: {e}")
                except Exception as e:
                    print(f"处理图片消息失败: {e}")
            else:
                print(f"忽略非图片消息")
            
        except Exception as e:
            self.log_error(f"处理消息失败: {str(e)}")
            print(f"处理消息失败: {str(e)}")
            print(f"错误详情: {traceback.format_exc()}")

    def start(self):
        try:
            print("开始监控微信图片消息...")
            print(f"保存路径: {self.base_path}")
            
            if not os.path.exists(self.base_path):
                os.makedirs(self.base_path)
            
            print("正在启用消息接收...")
            try:
                result = self.wcf.enable_receiving_msg()
                print(f"启用消息接收结果: {result}")
                
                while True:
                    try:
                        msg = self.wcf.get_msg()
                        if msg:
                            if msg.type == 3:  # 图片消息
                                print(f"\n收到图片消息: {msg.id}")
                                try:
                                    # 获取发送者信息
                                    sender_name = msg.sender
                                    try:
                                        # 直接从消息中获取发送者信息
                                        friend_info = self.wcf.query_sql("MicroMsg.db", 
                                            f"SELECT NickName FROM Contact WHERE UserName='{msg.sender}' LIMIT 1")
                                        if friend_info and friend_info[0]:
                                            sender_name = friend_info[0][0]
                                    except:
                                        pass
                                    
                                    folder_path = os.path.join(self.base_path, sender_name)
                                    if not os.path.exists(folder_path):
                                        os.makedirs(folder_path)
                                    
                                    try:
                                        # 使用正确的参数调用 download_image
                                        image_data = self.wcf.download_image(msg.id, msg, folder_path)
                                        if image_data:
                                            number = len([f for f in os.listdir(folder_path) if f.endswith('.jpg')]) + 1
                                            save_path = os.path.join(folder_path, f"{number}.jpg")
                                            
                                            with open(save_path, 'wb') as f:
                                                f.write(image_data)
                                            print(f"已保存图片: {save_path}")
                                        else:
                                            print("获取图片数据失败")
                                    except Exception as e:
                                        print(f"下载图片失败: {e}")
                                except Exception as e:
                                    print(f"处理图片消息失败: {e}")
                            time.sleep(0.1)  # 减少延迟
                            
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

    def check_and_create_photo_dir(self):
        """检查并创建照片保存目录，确保有写入权限"""
        try:
            # 检查目录是否存在
            if not os.path.exists(self.base_path):
                try:
                    # 尝试创建目录
                    os.makedirs(self.base_path)
                    print(f"创建目录成功: {self.base_path}")
                except Exception as e:
                    print(f"创建目录失败: {e}")
                    print("请以管理员身份手动创建目录：")
                    print("1. 打开命令提示符(CMD)，以管理员身份运行")
                    print("2. 执行以下命令：")
                    print("   mkdir C:\\photo")
                    print("   icacls C:\\photo /grant Users:(OI)(CI)F")
                    return False

            # 测试写入权限
            test_file = os.path.join(self.base_path, "test_write.tmp")
            try:
                with open(test_file, 'w') as f:
                    f.write("test")
                os.remove(test_file)
                print(f"目录 {self.base_path} 写入权限正常")
                return True
            except Exception as e:
                print(f"目录无写入权限: {e}")
                print("\n请手动设置目录权限：")
                print("1. 右键点击 C:\\photo 文件夹")
                print("2. 选择属性")
                print("3. 点击安全标签")
                print("4. 点击编辑")
                print("5. 选择Users或你的用户名")
                print("6. 勾选完全控制的允许")
                print("7. 点击应用和确定")
                return False

        except Exception as e:
            self.log_error(f"检查目录权限失败: {str(e)}")
            print(f"检查目录权限失败: {str(e)}")
            return False

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