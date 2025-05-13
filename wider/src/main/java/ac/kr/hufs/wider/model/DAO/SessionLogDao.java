package ac.kr.hufs.wider.model.DAO;

import java.util.List;
import java.util.Optional;

import ac.kr.hufs.wider.model.Entity.SessionLog;

public interface SessionLogDao {
    Optional<SessionLog> findById(String sessionId);
    List<SessionLog> findByUserId(String userId);
    SessionLog save(SessionLog log);
    void deleteById(String sessionId);
    void deleteAll(List<SessionLog> sessions);
}
