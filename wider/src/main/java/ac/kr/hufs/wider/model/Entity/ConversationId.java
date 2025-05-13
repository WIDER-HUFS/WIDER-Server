package ac.kr.hufs.wider.model.Entity;

import java.io.Serializable;

import jakarta.persistence.Embeddable;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ConversationId implements Serializable{
    private String sessionId; // 세션 ID
    private int messageOrder;
}
