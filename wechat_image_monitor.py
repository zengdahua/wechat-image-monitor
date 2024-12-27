import os
import sys
import time
import stat
import shutil
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
            
            # 初始化保存路径
            self.base_path = "C:\\photo"
            self.temp_path = os.path.join(os.environ.get('TEMP'), 'wechat_images')
            
            # 确保目录存在并设置权限
            self.setup_directories()
            
            # 连接微信，增加重试机制
            print("正在连接微信...")
            self.connect_wechat()
                
        except Exception as e:
            self.log_error(f"初始化失败: {str(e)}")
            print(f"初始化失败: {str(e)}")
            input("按回车键退出...")
            sys.exit(1)

    def setup_directories(self):
        """设置并确保目录权限"""
        try:
            # 创建主目录
            if not os.path.exists(self.base_path):
                os.makedirs(self.base_path)
            
            # 创建临时目录
            if not os.path.exists(self.temp_path):
                os.makedirs(self.temp_path)
            
            # 设置目录权限
            def set_permissions(path):
                try:
                    # 给予完全控制权限
                    os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)  # 777 权限
                    
                    # 遍历子目录
                    for root, dirs, files in os.walk(path):
                        for d in dirs:
                            os.chmod(os.path.join(root, d), stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
                        for f in files:
                            os.chmod(os.path.join(root, f), stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
                except Exception as e:
                    print(f"设置权限失败: {e}")

            # 设置主目录和临时目录的权限
            set_permissions(self.base_path)
            set_permissions(self.temp_path)
            
            print(f"✅ 目录权限设置完成")
            
        except Exception as e:
            print(f"❌ 设置目录失败: {e}")
            raise

    def create_directory_with_permissions(self, path):
        """创建目录并设置权限"""
        try:
            if not os.path.exists(path):
                os.makedirs(path)
            os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
            return True
        except Exception as e:
            print(f"❌ 创建目录失败: {e}")
            return False

    def save_image(self, msg, sender_name):
        """保存图片的核心逻辑"""
        try:
            # 创建日期文件夹
            today = datetime.now().strftime('%Y-%m-%d')
            sender_path = os.path.join(self.base_path, sender_name)
            date_path = os.path.join(sender_path, today)
            
            # 创建所需的目录
            for path in [sender_path, date_path]:
                if not self.create_directory_with_permissions(path):
                    return False
            
            # 使用更简单的临时目录路径
            temp_dir = os.path.join(self.temp_path, str(msg.id))
            if not self.create_directory_with_permissions(temp_dir):
                return False
            
            try:
                # 下载到临时目录
                print(f"开始下载图片... (ID: {msg.id})")
                print(f"临时目录: {temp_dir}")
                
                # 确保路径格式正确
                download_path = temp_dir.replace('\\', '/')
                result = self.wcf.download_image(msg.id, msg.extra, download_path)
                
                if result == 0:  # 下载成功
                    print("✅ 下载成功，开始解密...")
                    
                    # 解密图片
                    decrypted_path = self.wcf.decrypt_image(msg.extra, download_path)
                    if decrypted_path and os.path.exists(decrypted_path):
                        print(f"✅ 解密成功: {decrypted_path}")
                        
                        # 确定最终的保存路径
                        original_name = os.path.basename(msg.extra) if msg.extra else f"{msg.id}.jpg"
                        save_path = os.path.join(date_path, original_name)
                        
                        # 如果文件已存在，添加序号
                        if os.path.exists(save_path):
                            name, ext = os.path.splitext(original_name)
                            counter = 1
                            while os.path.exists(save_path):
                                save_path = os.path.join(date_path, f"{name}_{counter}{ext}")
                                counter += 1
                        
                        try:
                            # 复制文件到最终位置
                            shutil.copy2(decrypted_path, save_path)
                            # 设置目标文件权限
                            os.chmod(save_path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
                            print(f"✅ 已保存图片: {save_path}")
                            return True
                        except Exception as e:
                            print(f"❌ 复制文件失败: {e}")
                    else:
                        print(f"❌ 解密失败或文件不存在: {decrypted_path}")
                else:
                    print(f"❌ 下载失败，错误码: {result}")
                    print(f"下载参数: id={msg.id}, extra={msg.extra}, path={download_path}")
            finally:
                # 清理临时目录
                try:
                    shutil.rmtree(temp_dir, ignore_errors=True)
                except:
                    pass
                
            return False
            
        except Exception as e:
            print(f"❌ 保存图片失败: {e}")
            return False

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
            print(f"检查微信安装路径失败: {e}")
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
            print(f"写入日志失败: {e}")

    def connect_wechat(self, max_retries=5):
        """连接微信，带重试机制"""
        for i in range(max_retries):
            try:
                self.wcf = Wcf(debug=False)
                if self.check_wechat_connection():
                    print("✅ 微信连接成功")
                    return True
            except Exception as e:
                print(f"第 {i+1} 次连接失败: {e}")
                if i < max_retries - 1:
                    print(f"3秒后重试...")
                    time.sleep(3)
                continue
        
        print("\n❌ 无法连接到微信，请检查：")
        print("1. 是否以管理员身份运行")
        print("2. 微信是否正常运行")
        print("3. 是否安装了正确版本的微信(3.9.11.25)")
        input("\n按回车键退出...")
        sys.exit(1)

    def check_wechat_connection(self):
        """检查微信连接状态"""
        try:
            # 检查登录状态
            if not self.wcf.is_login():
                print("等待微信登录...")
                return False

            # 获取微信ID
            self_wxid = self.wcf.get_self_wxid()
            if not self_wxid:
                print("无法获取微信ID")
                return False

            print(f"微信 ID: {self_wxid}")
            return True

        except Exception as e:
            print(f"连接测试失败: {e}")
            return False

    def start(self):
        try:
            print("开始监控微信图片消息...")
            print(f"保存路径: {self.base_path}")
            print(f"临时路径: {self.temp_path}")
            
            print("正在启用消息接收...")
            try:
                self.wcf.enable_receiving_msg()
                print("消息接收已启用")
                print("\n等待接收图片消息中...")
                
                while True:
                    try:
                        msg = self.wcf.get_msg()
                        if msg and msg.type == 3:  # 图片消息
                            print(f"\n收到图片消息: {msg.id}")
                            try:
                                # 获取发送者信息
                                sender_name = msg.sender
                                try:
                                    friend_info = self.wcf.query_sql("MicroMsg.db", 
                                        f"SELECT NickName FROM Contact WHERE UserName='{msg.sender}' LIMIT 1")
                                    if friend_info and friend_info[0] and friend_info[0].get("NickName"):
                                        sender_name = friend_info[0]["NickName"]
                                except Exception as e:
                                    print(f"获取好友信息失败: {e}")
                                
                                print(f"发送者: {sender_name}")
                                
                                # 保存图片
                                self.save_image(msg, sender_name)
                                
                            except Exception as e:
                                print(f"❌ 处理图片消息失败: {e}")
                                
                        time.sleep(0.1)
                            
                    except KeyboardInterrupt:
                        print("\n收到停止信号，程序退出...")
                        break
                    except Exception as e:
                        time.sleep(0.1)
                        continue
                        
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
                # 清理临时目录
                shutil.rmtree(self.temp_path, ignore_errors=True)
            except:
                pass

if __name__ == "__main__":
    monitor = WeChatImageMonitor()
    monitor.start() 