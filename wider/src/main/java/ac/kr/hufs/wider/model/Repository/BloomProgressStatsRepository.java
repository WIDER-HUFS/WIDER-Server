package ac.kr.hufs.wider.model.Repository;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import ac.kr.hufs.wider.model.DTO.MonthlyBloomLevelCountDTO;
import ac.kr.hufs.wider.model.Entity.BloomProgressStats;

@Repository
public interface BloomProgressStatsRepository extends JpaRepository<BloomProgressStats, Long> {
    // Spring Data JPA 네이밍 컨벤션에 맞춰 메서드명 변경
    List<BloomProgressStats> findByUserUserId(String userId);

    @Query("""
        SELECT new ac.kr.hufs.wider.model.DTO.MonthlyBloomLevelCountDTO(
             b.completedMonth,
             b.finalBloomLevel,
             COUNT(b)
        )
        FROM BloomProgressStats b
        WHERE b.user.userId = :userId
        GROUP BY b.completedMonth, b.finalBloomLevel
        ORDER BY b.completedMonth, b.finalBloomLevel
    """)
    List<MonthlyBloomLevelCountDTO> findMonthlyBloomLevelStatsByUser(
        @Param("userId") String userId
    );
}