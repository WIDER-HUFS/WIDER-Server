package ac.kr.hufs.wider.model.DTO;

import com.fasterxml.jackson.annotation.JsonProperty;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class UserResponseRequestDTO {
    @JsonProperty("session_id")
    private String sessionId;
    @JsonProperty("user_answer")
    private String userAnswer;
    @JsonProperty("current_level")
    private int currentLevel;
    @JsonProperty("topic")
    private String topic;
}
