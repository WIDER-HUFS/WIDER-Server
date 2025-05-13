package ac.kr.hufs.wider.model.DTO;

import java.time.LocalDate;

import com.fasterxml.jackson.annotation.JsonProperty;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class DailyTopicResponseDTO {
    @JsonProperty("topic")
    private String topic;
    @JsonProperty("topic_prompt")
    private String topicPrompt;
    @JsonProperty("topic_date")
    private LocalDate topicDate;
}
