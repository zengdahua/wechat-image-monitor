package com.wechat.ferry.config;

import javax.annotation.Resource;

import org.springframework.boot.autoconfigure.web.ServerProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import com.wechat.ferry.handle.WeChatSocketClient;

import lombok.extern.slf4j.Slf4j;

/**
 * 配置类-注入微信客户端
 *
 * @author chandler
 * @date 2024-09-30 12:21
 */
@Slf4j
@Configuration
public class WeChatConfiguration {

    @Resource
    private WeChatFerryProperties properties;

    @Resource
    private ServerProperties serverProperties;

    @Bean
    public WeChatSocketClient weChatSocketClient() {
        log.debug("[读取配置文件]-端口：{}，地址：{}", properties.getSocketPort(), properties.getDllPath());
        // 连接远程 RPC
        // Client client = new Client("127.0.0.1", 10086);

        // 本地启动 RPC
        WeChatSocketClient wechatSocketClient = new WeChatSocketClient(properties.getSocketPort(), properties.getDllPath());

        // 是否已登录
        // log.info("isLogin: {}", client.isLogin());

        // 登录账号 wxid
        // log.info("wxid: {}", client.getSelfWxid());

        // 消息类型
        // log.info("message types: {}", client.getMsgTypes());

        // 所有联系人（包括群聊、公众号、好友……）
        // client.printContacts(client.getContacts());

        // 获取数据库
        log.info("dbs: {}", wechatSocketClient.getDbNames());

        // 获取数据库下的表
        String db = "MicroMsg.db";
        // log.info("tables in {}: {}", db, client.getDbTables(db));

        // 发送文本消息，aters 是要 @ 的 wxid，多个用逗号分隔；消息里@的数量要与aters里的数量对应
        // client.sendText("Hello", "filehelper", "");
        // client.sendText("Hello @某人1 @某人2", "xxxxxxxx@chatroom", "wxid_xxxxxxxxxxxxx1,wxid_xxxxxxxxxxxxx2");

        // 发送图片消息，图片必须要存在
        // client.sendImage("C:\\Projs\\WeChatFerry\\TEQuant.jpeg", "filehelper");

        // 发送文件消息，文件必须要存在
        // client.sendFile("C:\\Projs\\WeChatFerry\\README.MD", "filehelper");

        String xml =
            "<?xml version=\"1.0\"?><msg><appmsg appid=\"\" sdkver=\"0\"><title>叮当药房，24小时服务，28分钟送药到家！</title><des>叮当快药首家承诺范围内28分钟送药到家！叮当快药核心区域内7*24小时全天候服务，送药上门！叮当快药官网为您提供快捷便利，正品低价，安全放心的购药、送药服务体验。</des><action>view</action><type>33</type><showtype>0</showtype><content /><url>https://mp.weixin.qq.com/mp/waerrpage?appid=wxc2edadc87077fa2a&amp;type=upgrade&amp;upgradetype=3#wechat_redirect</url><dataurl /><lowurl /><lowdataurl /><recorditem /><thumburl /><messageaction /><md5>7f6f49d301ebf47100199b8a4fcf4de4</md5><extinfo /><sourceusername>gh_c2b88a38c424@app</sourceusername><sourcedisplayname>叮当快药 药店送药到家夜间买药</sourcedisplayname><commenturl /><appattach><totallen>0</totallen><attachid /><emoticonmd5></emoticonmd5><fileext>jpg</fileext><filekey>da0e08f5c7259d03da150d5e7ca6d950</filekey><cdnthumburl>3057020100044b30490201000204e4c0232702032f4ef20204a6bace6f02046401f62d042430326337303430352d333734332d343362652d623335322d6233333566623266376334620204012400030201000405004c537600</cdnthumburl><aeskey>0db26456caf243fbd4efb99058a01d66</aeskey><cdnthumbaeskey>0db26456caf243fbd4efb99058a01d66</cdnthumbaeskey><encryver>1</encryver><cdnthumblength>61558</cdnthumblength><cdnthumbheight>100</cdnthumbheight><cdnthumbwidth>100</cdnthumbwidth></appattach><weappinfo><pagepath>pages/index/index.html</pagepath><username>gh_c2b88a38c424@app</username><appid>wxc2edadc87077fa2a</appid><version>197</version><type>2</type><weappiconurl>http://wx.qlogo.cn/mmhead/Q3auHgzwzM4727n0NQ0ZIPQPlfp15m1WLsnrXbo1kLhFGcolgLyc0A/96</weappiconurl><appservicetype>0</appservicetype><shareId>1_wxc2edadc87077fa2a_29177e9a9b918cb9e75964f80bb8f32e_1677849476_0</shareId></weappinfo><websearch /></appmsg><fromusername>wxid_eob5qfcrv4zd22</fromusername><scene>0</scene><appinfo><version>1</version><appname /></appinfo><commenturl /></msg>";
        // client.sendXml("filehelper", xml, "", 0x21);

        // 发送表情消息，gif 必须要存在
        // client.sendEmotion("C:\\Projs\\WeChatFerry\\emo.gif", "filehelper");

        // 使用本机打印
        String url = "http://localhost:" + serverProperties.getPort() + "/wechat/msg/receive";
        // 接收消息，并调用 printWxMsg 处理
        wechatSocketClient.enableRecvMsg(100);
        Thread thread = new Thread(new Runnable() {
            public void run() {
                while (wechatSocketClient.getIsReceivingMsg()) {
                    // 只打印
                    // wechatSocketClient.printWxMsg(wechatSocketClient.getMsg());
                    // 转发到boot项目进行消息处理
                    wechatSocketClient.forwardMsg(wechatSocketClient.getMsg(), url);
                }
            }
        });
        thread.start();
        // client.diableRecvMsg(); // 需要停止时调用

        new Thread(new Runnable() {
            public void run() {
                wechatSocketClient.keepRunning();
            }
        }).start();

        return wechatSocketClient;
    }

}
