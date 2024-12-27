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
            # 使用本地的 wcferry 库，增加超时时间
            retry_count = 0
            max_retries = 3
            
            while retry_count < max_retries:
                try:
                    self.wcf = Wcf(debug=False)
                    # 检查微信连接状态
                    if self.check_wechat_connection():
                        break
                    else:
                        retry_count += 1
                        if retry_count < max_retries:
                            print(f"\n连接失败，{5}秒后重试 ({retry_count}/{max_retries})...")
                            time.sleep(5)
                        else:
                            print("\n多次连接失败，请检查：")
                            print("1. 是否以管理员身份运行")
                            print("2. 微信是否正常运行")
                            print("3. 是否安装了正确版本的微信(3.9.11.25)")
                            input("\n按回车键退出...")
                            sys.exit(1)
                except Exception as e:
                    retry_count += 1
                    if retry_count < max_retries:
                        print(f"\n连接出错: {e}")
                        print(f"5秒后重试 ({retry_count}/{max_retries})...")
                        time.sleep(5)
                    else:
                        print(f"\n连接失败: {e}")
                        print("\n请检查：")
                        print("1. 是否以管理员身份运行")
                        print("2. 微信是否正常运行")
                        print("3. 是否安装了正确版本的微信(3.9.11.25)")
                        input("\n按回车键退出...")
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
            # 多次尝试登录检查
            for i in range(3):
                try:
                    if self.wcf.is_login():
                        break
                    print(f"等待微信登录... ({i+1}/3)")
                    time.sleep(2)
                except:
                    if i == 2:  # 最后一次尝试失败
                        print("错误: 微信未登录")
                        return False
                    time.sleep(2)
                    continue

            # 多次尝试获取微信ID
            for i in range(3):
                try:
                    self_wxid = self.wcf.get_self_wxid()
                    if self_wxid:
                        print(f"微信 ID: {self_wxid}")
                        break
                    print(f"等待获取微信ID... ({i+1}/3)")
                    time.sleep(2)
                except:
                    if i == 2:  # 最后一次尝试失败
                        print("错误: 无法获取微信 ID")
                        return False
                    time.sleep(2)
                    continue

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
                                    # 从数据库获取好友昵称
                                    friend_info = self.wcf.query_sql("MicroMsg.db", 
                                        f"SELECT NickName FROM Contact WHERE UserName='{msg.sender}' LIMIT 1")
                                    if friend_info and friend_info[0] and friend_info[0].get("NickName"):
                                        sender_name = friend_info[0]["NickName"]
                                except Exception as e:
                                    print(f"获取好友信息失败: {e}")
                                
                                print(f"发送者: {sender_name}")
                                
                                # 创建保存目录
                                folder_path = os.path.join(self.base_path, sender_name)
                                if not os.path.exists(folder_path):
                                    os.makedirs(folder_path)
                                    print(f"创建文件夹: {folder_path}")
                                
                                try:
                                    # 获取下一个图片序号
                                    existing_files = [f for f in os.listdir(folder_path) if f.endswith('.jpg') or f.endswith('.png')]
                                    next_number = 1
                                    if existing_files:
                                        numbers = [int(f.split('.')[0]) for f in existing_files if f.split('.')[0].isdigit()]
                                        if numbers:
                                            next_number = max(numbers) + 1
                                    
                                    # 确定文件扩展名
                                    ext = '.jpg'
                                    if msg.extra and msg.extra.lower().endswith('.png'):
                                        ext = '.png'
                                    
                                    save_path = os.path.join(folder_path, f"{next_number}{ext}")
                                    
                                    # 下载图片
                                    print(f"开始下载图片... (ID: {msg.id})")
                                    print(f"保存路径: {save_path}")
                                    
                                    # 先下载
                                    result = self.wcf.download_image(msg.id, msg.extra, folder_path)
                                    if result == 0:  # 下载成功
                                        print("✅ 下载成功，开始解密...")
                                        # 解密图片
                                        decrypted_path = self.wcf.decrypt_image(msg.extra, folder_path)
                                        if decrypted_path:
                                            print(f"✅ 解密成功: {decrypted_path}")
                                            # 重命名文件
                                            if os.path.exists(decrypted_path):
                                                if os.path.exists(save_path):
                                                    os.remove(save_path)  # 如果目标文件已存在，先删除
                                                os.rename(decrypted_path, save_path)
                                                print(f"✅ 已保存图片: {save_path}")
                                            else:
                                                print(f"❌ 解密后的图片不存在: {decrypted_path}")
                                        else:
                                            print("❌ 解密图片失败")
                                    else:
                                        print(f"❌ 下载图片失败，错误码: {result}")
                                    
                                except Exception as e:
                                    print(f"❌ 处理图片失败: {e}")
                                    print(f"消息内容: {msg}")  # 打印完整消息内容以便调试
                                    
                            except Exception as e:
                                print(f"❌ 处理图片消息失败: {e}")
                                
                        time.sleep(0.1)  # 短暂休眠，减少 CPU 占用
                            
                    except KeyboardInterrupt:
                        print("\n收到停止信号，程序退出...")
                        break
                    except Exception as e:
                        time.sleep(0.1)  # 出错时短暂休眠
                        continue  # 继续监听，不打印错误
                        
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