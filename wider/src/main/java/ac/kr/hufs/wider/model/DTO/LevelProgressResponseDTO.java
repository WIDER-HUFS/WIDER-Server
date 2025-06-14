package ac.kr.hufs.wider.model.DTO;

import java.time.LocalDateTime;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class LevelProgressResponseDTO {
    private String sessionId;
    private LocalDateTime startedAt;
    private Integer maxBloomLevel;
} 