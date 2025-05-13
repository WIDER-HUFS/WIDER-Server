package ac.kr.hufs.wider.model.DAO;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

import ac.kr.hufs.wider.model.Entity.BloomProgressStats;

public interface StatsDao {
    BloomProgressStats save(BloomProgressStats stats);
    Optional<BloomProgressStats> findById(Long id);
    List<BloomProgressStats> findByUser_UserId(String userId);
    Optional<BloomProgressStats> findBySession_SessionId(String sessionId);
    List<BloomProgressStats> findByUser_UserIdAndCompletedMonth(String userId, LocalDate month);
    boolean existsById(Long id);
    void deleteById(Long id);
    void deleteAll(List<BloomProgressStats> stats);
} 