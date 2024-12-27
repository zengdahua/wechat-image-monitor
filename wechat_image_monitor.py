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
            
            # 初始化保存路径
            self.base_path = "C:\\photo"
            if not os.path.exists(self.base_path):
                os.makedirs(self.base_path)
                print(f"创建主文件夹: {self.base_path}")
            
            # 连接微信，增加重试机制
            print("正在连接微信...")
            self.connect_wechat()
                
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

    def ensure_folder_permissions(self, folder_path):
        """确保文件夹存在且有正确的权限"""
        try:
            if not os.path.exists(folder_path):
                os.makedirs(folder_path, exist_ok=True)
            # 尝试创建测试文件以验证权限
            test_file = os.path.join(folder_path, '.test')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            return True
        except Exception as e:
            print(f"❌ 文件夹权限检查失败: {e}")
            return False

    def start(self):
        try:
            print("开始监控微信图片消息...")
            print(f"保存路径: {self.base_path}")
            
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
                                
                                # 创建保存目录
                                folder_path = os.path.join(self.base_path, sender_name)
                                try:
                                    if not os.path.exists(folder_path):
                                        os.makedirs(folder_path)
                                        print(f"创建文件夹: {folder_path}")
                                except Exception as e:
                                    print(f"创建文件夹失败: {e}")
                                    continue
                                
                                try:
                                    # 获取下一个图片序号
                                    next_number = 1
                                    try:
                                        existing_files = [f for f in os.listdir(folder_path) if f.endswith('.jpg') or f.endswith('.png')]
                                        if existing_files:
                                            numbers = [int(f.split('.')[0]) for f in existing_files if f.split('.')[0].isdigit()]
                                            if numbers:
                                                next_number = max(numbers) + 1
                                    except Exception as e:
                                        print(f"获取文件序号失败: {e}")
                                    
                                    # 确定文件扩展名
                                    ext = '.jpg'
                                    if msg.extra and msg.extra.lower().endswith('.png'):
                                        ext = '.png'
                                    
                                    # 确保文件夹权限正确
                                    if not self.ensure_folder_permissions(folder_path):
                                        print("❌ 无法访问保存目录，请检查权限")
                                        continue
                                    
                                    save_path = os.path.join(folder_path, f"{next_number}{ext}")
                                    temp_path = os.path.join(folder_path, f"temp_{next_number}{ext}")
                                    
                                    # 下载图片
                                    print(f"开始下载图片... (ID: {msg.id})")
                                    print(f"目标路径: {save_path}")
                                    
                                    try:
                                        # 先下载到临时文件
                                        result = self.wcf.download_image(msg.id, msg.extra, folder_path)
                                        if result == 0:  # 下载成功
                                            print("✅ 下载成功，开始解密...")
                                            # 解密图片
                                            decrypted_path = self.wcf.decrypt_image(msg.extra, folder_path)
                                            if decrypted_path and os.path.exists(decrypted_path):
                                                print(f"✅ 解密成功: {decrypted_path}")
                                                try:
                                                    # 如果目标文件已存在，先删除
                                                    if os.path.exists(save_path):
                                                        os.remove(save_path)
                                                    
                                                    # 使用 shutil 来复制文件而不是重命名
                                                    import shutil
                                                    shutil.copy2(decrypted_path, save_path)
                                                    
                                                    # 删除原始文件
                                                    try:
                                                        os.remove(decrypted_path)
                                                    except:
                                                        pass
                                                        
                                                    print(f"✅ 已保存图片: {save_path}")
                                                except Exception as e:
                                                    print(f"❌ 保存文件失败: {e}")
                                            else:
                                                print(f"❌ 解密失败或文件不存在: {decrypted_path}")
                                        else:
                                            print(f"❌ 下载失败，错误码: {result}")
                                        
                                    except Exception as e:
                                        print(f"❌ 处理图片失败: {e}")
                                        # 清理可能的临时文件
                                        try:
                                            if os.path.exists(temp_path):
                                                os.remove(temp_path)
                                        except:
                                            pass
                                    
                                except Exception as e:
                                    print(f"❌ 处理图片失败: {e}")
                                    
                            except Exception as e:
                                print(f"❌ 处理图片消息失败: {e}")
                                
                        time.sleep(0.1)  # 短暂休眠，减少 CPU 占用
                            
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
            except:
                pass

if __name__ == "__main__":
    monitor = WeChatImageMonitor()
    monitor.start() 