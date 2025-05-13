package ac.kr.hufs.wider.model.DTO;

import com.fasterxml.jackson.annotation.JsonProperty;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ChatResponseDTO {
    @JsonProperty("session_id")
    private String sessionId;
    @JsonProperty("topic")
    private String topic;
    @JsonProperty("current_level")
    private int currentLevel;
    @JsonProperty("question")
    private String question;
    @JsonProperty("message")
    private String message;
    @JsonProperty("is_complete")
    private boolean isComplete;
}
