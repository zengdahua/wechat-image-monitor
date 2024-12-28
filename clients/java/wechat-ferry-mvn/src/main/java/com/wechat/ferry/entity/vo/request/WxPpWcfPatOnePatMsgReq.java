package com.wechat.ferry.entity.vo.request;

import io.swagger.annotations.ApiModel;
import io.swagger.annotations.ApiModelProperty;
import lombok.Data;

/**
 * 请求入参-个微WCF发送拍一拍消息
 *
 * @author chandler
 * @date 2024-10-06 15:50
 */
@Data
@ApiModel(value = "wxPpWcfPatOnePatMsgReq", description = "个微WCF发送拍一拍消息请求入参")
public class WxPpWcfPatOnePatMsgReq {

    /**
     * 消息接收人
     * 消息接收人，私聊为 wxid（wxid_xxxxxxxxxxxxxx）
     * 群聊为 roomid（xxxxxxxxxx@chatroom）
     */
    @ApiModelProperty(value = "消息接收人")
    private String recipient;

    /**
     * 要拍的wxid
     */
    @ApiModelProperty(value = "要拍的wxid")
    private String patUser;

}
