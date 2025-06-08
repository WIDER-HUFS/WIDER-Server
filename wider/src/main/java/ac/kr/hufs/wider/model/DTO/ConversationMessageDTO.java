package ac.kr.hufs.wider.model.DTO;

import lombok.Data;

@Data
public class ConversationMessageDTO {
    private String speaker;
    private String content;
    private String timestamp;
    private int messageOrder;
} 