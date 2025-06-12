package ac.kr.hufs.wider.model.Entity;

import java.time.LocalDateTime;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "session_logs")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class SessionLog {
    @Id
    private String sessionId; // 대화 세션 고유 식별자

    @ManyToOne
    @JoinColumn(name = "user_id")
    private Users user; // 이 세션을 만든 사용자(대화를 하는 사람)
    
    private String topic; // 해당 세션의 주제
    private LocalDateTime startedAt = LocalDateTime.now(); // 세션 시작 시간
    private boolean completed = false; // 대화 종료 여부
    private LocalDateTime completedAt; // 세션 종료된 시간
    private String bloomLevel; // Bloom's Taxonomy level
}
