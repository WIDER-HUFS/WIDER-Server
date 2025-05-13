package ac.kr.hufs.wider.model.DTO;

import java.time.LocalDateTime;

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
    @JsonProperty("message_order")
    private int messageOrder;
    @JsonProperty("speaker")
    private String speaker;
    @JsonProperty("content")
    private String content;
    @JsonProperty("timestamp")
    private LocalDateTime timestamp;
}
