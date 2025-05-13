package ac.kr.hufs.wider.model.DTO;

import com.fasterxml.jackson.annotation.JsonProperty;

import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class QuestionRequestDTO { // 사용자의 답변 제출을 위한 DTO (POST)
    @JsonProperty("session_id")
    private String sessionId;
    @JsonProperty("bloom_level")
    private int bloomLevel;
    @JsonProperty("user_answer")
    @NotBlank(message = "답변을 입력해주세요.")
    private String userAnswer;
}
