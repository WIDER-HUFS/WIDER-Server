package ac.kr.hufs.wider.model.DTO;

import java.time.LocalDateTime;

import com.fasterxml.jackson.annotation.JsonProperty;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class SessionLogResponseDTO {
    @JsonProperty("session_id")
    private String sessionId;
    @JsonProperty("user_id")
    private String userId;
    @JsonProperty("topic")
    private String topic;
    @JsonProperty("started_at")
    private LocalDateTime startedAt;
    @JsonProperty("completed")
    private boolean completed;
    @JsonProperty("completed_at")
    private LocalDateTime completedAt;
}
