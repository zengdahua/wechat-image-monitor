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
            self.display_instructions()
            self.base_path = self.setup_save_path()
            self.connect_wechat()
        except Exception as e:
            self.handle_initialization_error(e)

    def display_instructions(self):
        """显示使用说明"""
        print("正在初始化...")
        print("正在检查环境...")
        print("=" * 50)
        print("使用说明：")
        print("1. 确保已安装微信 3.9.11.25 版本")
        print("2. 以管理员身份运行本程序")
        print("=" * 50)

    def setup_save_path(self):
        """设置保存路径"""
        documents_path = os.path.join(os.path.expanduser('~'), 'Documents')
        base_path = os.path.join(documents_path, 'WeChatImages')
        try:
            os.makedirs(base_path, exist_ok=True)
            os.chmod(base_path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
            print(f"图片将保存到: {base_path}")
            return base_path
        except Exception as e:
            raise RuntimeError(f"设置保存路径失败: {e}")

    def connect_wechat(self):
        """连接微信，带重试机制"""
        for attempt in range(5):
            try:
                self.wcf = Wcf(debug=False)
                if self.check_wechat_connection():
                    print("✅ 微信连接成功")
                    return
            except Exception as e:
                print(f"第 {attempt + 1} 次连接失败: {e}")
                time.sleep(3)
        self.handle_connection_failure()

    def check_wechat_connection(self):
        """检查微信连接状态"""
        if not self.wcf.is_login():
            print("等待微信登录...")
            return False
        self_wxid = self.wcf.get_self_wxid()
        if not self_wxid:
            print("无法获取微信ID")
            return False
        print(f"微信 ID: {self_wxid}")
        return True

    def handle_initialization_error(self, error):
        """处理初始化错误"""
        self.log_error(f"初始化失败: {str(error)}")
        print(f"初始化失败: {str(error)}")
        input("按回车键退出...")
        sys.exit(1)

    def handle_connection_failure(self):
        """处理连接失败情况"""
        print("\n❌ 无法连接到微信，请检查：")
        print("1. 是否以管理员身份运行")
        print("2. 微信是否正常运行")
        print("3. 是否安装了正确版本的微信(3.9.11.25)")
        sys.exit(1)

    def log_error(self, error_msg):
        """记录错误日志"""
        log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'error.log')
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(f"\n[{timestamp}] {error_msg}")
                if isinstance(error_msg, Exception):
                    f.write(f"\n{traceback.format_exc()}")
                f.write("\n" + "=" * 50 + "\n")
        except Exception as e:
            print(f"写入日志失败: {e}")

    def create_directory_with_permissions(self, path):
        """创建目录并设置权限"""
        try:
            os.makedirs(path, exist_ok=True)
            os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
            return True
        except Exception as e:
            print(f"❌ 创建目录失败: {e}")
            return False

    def save_image(self, msg, sender_name):
        """保存图片的核心逻辑"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            sender_path = os.path.join(self.base_path, sender_name)
            date_path = os.path.join(sender_path, today)

            # 创建所需的目录
            for path in [sender_path, date_path]:
                if not self.create_directory_with_permissions(path):
                    self.log_error(f"创建目录失败: {path}")
                    return False

            original_name = os.path.basename(msg.extra)
            base_name = os.path.splitext(original_name)[0]
            final_path = os.path.join(date_path, f"{base_name}.jpg")

            # 如果文件已存在，添加序号
            counter = 1
            while os.path.exists(final_path):
                final_path = os.path.join(date_path, f"{base_name}_{counter}.jpg")
                counter += 1

            temp_dir = os.path.join(os.environ.get('TEMP', '/tmp'), f'wechat_img_{msg.id}')
            os.makedirs(temp_dir, exist_ok=True)

            # 下载并解密图片
            for attempt in range(5):
                try:
                    print(f"尝试下载图片 (第 {attempt + 1} 次)")
                    result = self.wcf.download_image(msg.id, msg.extra, temp_dir)

                    if result == 0:
                        decrypted_path = self.wcf.decrypt_image(msg.extra, temp_dir)
                        if decrypted_path and os.path.exists(decrypted_path):
                            shutil.copy2(decrypted_path, final_path)
                            if os.path.exists(final_path) and os.path.getsize(final_path) > 0:
                                print(f"✅ 已保存图片: {final_path}")
                                return True
                        else:
                            self.log_error(f"图片解密失败: {decrypted_path}")
                    else:
                        self.log_error(f"图片下载失败，错误码: {result}")

                except Exception as e:
                    self.log_error(f"处理图片出错 (第 {attempt + 1} 次): {str(e)}")
                    time.sleep(2)
                finally:
                    # 清理临时文件
                    try:
                        shutil.rmtree(temp_dir, ignore_errors=True)
                    except Exception as e:
                        self.log_error(f"清理临时文件失败: {str(e)}")

            self.log_error("图片处理失败：所有尝试均失败")
            return False

        except Exception as e:
            self.log_error(f"保存图片过程中发生错误: {str(e)}")
            return False

    def start(self):
        """启动监控"""
        try:
            print("开始监控微信图片消息...")
            self.wcf.enable_receiving_msg()
            print("消息接收已启用")

            while True:
                try:
                    msg = self.wcf.get_msg()
                    if msg and msg.type == 3:  # 图片消息
                        sender_name = self.get_sender_name(msg.sender)
                        print(f"收到图片消息，发送者: {sender_name}")
                        self.save_image(msg, sender_name)

                except KeyboardInterrupt:
                    print("\n收到停止信号，程序退出...")
                    break
                except Exception as e:
                    self.log_error(f"消息处理出错: {str(e)}")
                    time.sleep(0.1)
                    
        except Exception as e:
            self.log_error(f"程序运行错误: {str(e)}")
            print(f"\n发生错误: {str(e)}")

    def get_sender_name(self, sender):
        # This method is not defined in the original code, so it's left unchanged
        pass

 