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
    @JsonProperty("messages")
    private List<ConversationMessageDTO> messages;
}
