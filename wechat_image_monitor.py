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
            
            # 初始化保存路径 - 使用用户的 Documents 目录
            documents_path = os.path.join(os.path.expanduser('~'), 'Documents')
            self.base_path = os.path.join(documents_path, 'WeChatImages')
            
            if not os.path.exists(self.base_path):
                os.makedirs(self.base_path)
            
            # 设置目录权限
            os.chmod(self.base_path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
            
            print(f"图片将保存到: {self.base_path}")
            
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
            
            # 设置目录权限
            os.chmod(self.base_path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
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

    def wait_for_file(self, file_path, max_retries=10, delay=0.5):
        """等待文件出现"""
        for i in range(max_retries):
            if os.path.exists(file_path):
                # 等待文件写入完成
                try:
                    with open(file_path, 'rb') as f:
                        return True
                except:
                    pass
            print(f"等待文件就绪... ({i+1}/{max_retries})")
            time.sleep(delay)
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
            
            try:
                if msg.id and msg.extra:
                    print(f"开始处理图片... (ID: {msg.id})")
                    
                    # 生成文件名（使用原始文件名）
                    original_name = os.path.basename(msg.extra)
                    base_name = os.path.splitext(original_name)[0]
                    save_path = os.path.join(date_path, f"{base_name}.jpg")
                    
                    # 如果文件已存在，添加序号
                    if os.path.exists(save_path):
                        name = base_name
                        counter = 1
                        while os.path.exists(save_path):
                            save_path = os.path.join(date_path, f"{name}_{counter}.jpg")
                            counter += 1
                    
                    print(f"目标路径: {save_path}")
                    
                    # 添加重试机制
                    max_retries = 5
                    retry_delay = 2  # 秒
                    
                    for attempt in range(max_retries):
                        try:
                            print(f"尝试下载图片 (第 {attempt + 1} 次)")
                            
                            # 1. 下载加密图片
                            result = self.wcf.download_image(msg.id, msg.extra, date_path)
                            
                            if result == 0:  # 下载成功
                                print("✅ 下载成功，开始解密...")
                                
                                # 2. 解密图片
                                decrypted_path = self.wcf.decrypt_image(msg.extra, date_path)
                                
                                if decrypted_path and os.path.exists(decrypted_path):
                                    print(f"✅ 解密成功: {decrypted_path}")
                                    
                                    try:
                                        # 3. 移动到最终位置
                                        if os.path.exists(save_path):
                                            os.remove(save_path)
                                        
                                        # 移动文件
                                        shutil.move(decrypted_path, save_path)
                                        
                                        # 验证文件
                                        if os.path.exists(save_path) and os.path.getsize(save_path) > 0:
                                            print(f"✅ 已保存图片: {save_path}")
                                            return True
                                        else:
                                            print("❌ 文件移动后验证失败")
                                    except Exception as e:
                                        print(f"❌ 移动文件失败: {e}")
                                else:
                                    print(f"❌ 解密失败或文件不存在: {decrypted_path}")
                            else:
                                print(f"❌ 下载失败，错误码: {result}")
                            
                            if attempt < max_retries - 1:
                                print(f"等待 {retry_delay} 秒后重试...")
                                time.sleep(retry_delay)
                                
                        except Exception as e:
                            print(f"❌ 第 {attempt + 1} 次尝试失败: {e}")
                            if attempt < max_retries - 1:
                                print(f"等待 {retry_delay} 秒后重试...")
                                time.sleep(retry_delay)
                    
                    print("❌ 所有尝试都失败了")
                    
                else:
                    print("❌ 消息中缺少必要信息")
                    print(f"msg.id: {msg.id}")
                    print(f"msg.extra: {msg.extra}")
                
                return False
                
            except Exception as e:
                print(f"❌ 保存图片失败: {e}")
                return False
            
        except Exception as e:
            print(f"❌ 处理图片失败: {e}")
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