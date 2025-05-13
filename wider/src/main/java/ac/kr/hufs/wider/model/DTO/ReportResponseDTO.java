package ac.kr.hufs.wider.model.DTO;

import java.time.LocalDateTime;

import com.fasterxml.jackson.annotation.JsonProperty;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ReportResponseDTO {
    @JsonProperty("report_id")
    private String reportId;
    @JsonProperty("session_id")
    private String sessionId;
    @JsonProperty("user_id")
    private String userId;
    @JsonProperty("topic")
    private String topic;
    @JsonProperty("summary")
    private String summary;
    @JsonProperty("strengths")
    private String strengths;
    @JsonProperty("weaknesses")
    private String weaknesses;
    @JsonProperty("suggestions")
    private String suggestions;
    @JsonProperty("revised_suggestion")
    private String revisedSuggestion;
    @JsonProperty("created_at")
    private LocalDateTime createdAt;
}
