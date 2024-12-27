from wcferry import Wcf
import os
from datetime import datetime

class WeChatImageMonitor:
    def __init__(self):
        self.wcf = Wcf()
        self.base_path = "C:\\photo"
        
    def create_folder(self, nickname):
        """为每个联系人创建独立文件夹"""
        folder_path = os.path.join(self.base_path, nickname)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        return folder_path

    def get_next_image_number(self, folder_path):
        """获取下一个图片序号"""
        existing_files = [f for f in os.listdir(folder_path) if f.endswith('.jpg') or f.endswith('.png')]
        if not existing_files:
            return 1
        numbers = [int(f.split('.')[0]) for f in existing_files]
        return max(numbers) + 1

    def on_message(self, msg):
        """消息处理回调函数"""
        if msg.type == 3:  # 图片消息类型
            # 获取发送者昵称
            sender = self.wcf.get_info_by_wxid(msg.sender).name
            
            # 创建文件夹
            folder_path = self.create_folder(sender)
            
            # 获取下一个图片序号
            number = self.get_next_image_number(folder_path)
            
            # 保存图片
            image_data = self.wcf.get_msg_image(msg.id)
            if image_data:
                file_ext = '.jpg'  # 默认扩展名
                save_path = os.path.join(folder_path, f"{number}{file_ext}")
                
                with open(save_path, 'wb') as f:
                    f.write(image_data)
                print(f"已保存图片: {save_path}")

    def start(self):
        """启动监控"""
        print("开始监控微信图片消息...")
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)
            
        self.wcf.enable_receiving_msg()
        self.wcf.register_msg_callback(self.on_message)
        
        try:
            while True:
                pass
        except KeyboardInterrupt:
            print("停止监控")
            self.wcf.cleanup()

if __name__ == "__main__":
    monitor = WeChatImageMonitor()
    monitor.start() 