package ac.kr.hufs.wider.model.DTO;

import java.util.Map;

import com.fasterxml.jackson.annotation.JsonProperty;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class EndChatResponseDTO {
    @JsonProperty("session_id")
    private String sessionId;
    @JsonProperty("summary")
    private Map<String, Object> summary;
    @JsonProperty("feedback")
    private String feedback;
    @JsonProperty("message")
    private String message;
}
