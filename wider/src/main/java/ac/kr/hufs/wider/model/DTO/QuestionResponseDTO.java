package ac.kr.hufs.wider.model.DTO;

import com.fasterxml.jackson.annotation.JsonProperty;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class QuestionResponseDTO { // 클라이언트에게 질문 전달 (GET)
    @JsonProperty("session_id")
    private String sessionId;
    @JsonProperty("bloom_level")
    private int bloomLevel;
    @JsonProperty("question")
    private String question;
    @JsonProperty("is_answered")
    private boolean isAnswered;
}
