package ac.kr.hufs.wider.model.DTO;

import java.time.LocalDate;
import java.time.LocalDateTime;

import com.fasterxml.jackson.annotation.JsonProperty;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class BloomProgressStatsResponseDTO {
    @JsonProperty("id")
    private Long id;
    @JsonProperty("user_id")
    private String userId;
    @JsonProperty("session_id")
    private String sessionId;
    @JsonProperty("completed_month")
    private LocalDate completedMonth;
    @JsonProperty("final_bloom_level")
    private int finalBloomLevel;
    @JsonProperty("recorded_at")
    private LocalDateTime recordedAt;
}
