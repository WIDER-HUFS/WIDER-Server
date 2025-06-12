package ac.kr.hufs.wider.model.DTO;

import java.util.List;

import com.fasterxml.jackson.annotation.JsonProperty;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ConversationHistoryDTO {
    @JsonProperty("session_id")
    private String sessionId;
    
    private String topic;
    
    @JsonProperty("current_level")
    private Integer currentLevel;
    
    @JsonProperty("is_complete")
    private Boolean isComplete;
    
    private List<ConversationMessageDTO> messages;
    
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class ConversationMessageDTO {
        private String speaker;
        private String content;
        private String timestamp;
        
        @JsonProperty("message_order")
        private Integer messageOrder;
    }
} 