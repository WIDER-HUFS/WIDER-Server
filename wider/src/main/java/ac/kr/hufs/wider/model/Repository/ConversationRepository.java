package ac.kr.hufs.wider.model.Repository;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import ac.kr.hufs.wider.model.Entity.ConversationHistory;
import ac.kr.hufs.wider.model.Entity.ConversationId;

@Repository
public interface ConversationRepository extends JpaRepository<ConversationHistory, ConversationId> {
    List<ConversationHistory> findBySessionLog_SessionIdOrderByTimestampAsc(String sessionId);
} 