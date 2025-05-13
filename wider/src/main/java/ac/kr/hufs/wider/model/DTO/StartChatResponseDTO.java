package ac.kr.hufs.wider.model.DTO;

import com.fasterxml.jackson.annotation.JsonProperty;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class StartChatResponseDTO {
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

// session_id=session_id,
//             topic=topic,
//             current_level=1,
//             question=question,
//             message=f"안녕하세요! 오늘의 주제는 '{topic}'입니다. 첫 번째 질문을 드리겠습니다.",
//             is_complete=False
