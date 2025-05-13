package ac.kr.hufs.wider.model.DAO;

import java.util.List;
import java.util.Optional;

import ac.kr.hufs.wider.model.Entity.ConversationHistory;
import ac.kr.hufs.wider.model.Entity.ConversationId;

public interface ConversationHistoryDao {
    List<ConversationHistory> findAll(String sessionId);
    int countBySession(String sessionId);
    ConversationHistory save(ConversationHistory history);
    Optional<ConversationHistory> findById(ConversationId id);
    List<ConversationHistory> findBySessionIdOrderByTimestampAsc(String sessionId);
    void deleteById(ConversationId id);
    void deleteAll(List<ConversationHistory> conversations);
}
