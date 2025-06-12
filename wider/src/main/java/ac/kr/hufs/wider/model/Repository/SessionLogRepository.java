package ac.kr.hufs.wider.model.Repository;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import ac.kr.hufs.wider.model.Entity.SessionLog;

@Repository
public interface SessionLogRepository extends JpaRepository<SessionLog, String> {
    List<SessionLog> findByUser_UserId(String userId);
    
    @Query("""
        SELECT s FROM SessionLog s
        WHERE s.user.userId = :userId
        AND s.sessionId IN (
            SELECT MAX(s2.sessionId)
            FROM SessionLog s2
            WHERE s2.user.userId = :userId
            GROUP BY s2.topic
        )
        ORDER BY s.startedAt DESC
    """)
    List<SessionLog> findLatestSessionsByUserId(@Param("userId") String userId);
}
