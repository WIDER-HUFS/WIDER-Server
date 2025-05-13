package ac.kr.hufs.wider.model.Repository;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import ac.kr.hufs.wider.model.Entity.BloomProgressStats;

@Repository
public interface StatsRepository extends JpaRepository<BloomProgressStats, Long> {
    List<BloomProgressStats> findByUser_UserId(String userId);
    Optional<BloomProgressStats> findBySession_SessionId(String sessionId);
    List<BloomProgressStats> findByUser_UserIdAndCompletedMonth(String userId, LocalDate month);
} 