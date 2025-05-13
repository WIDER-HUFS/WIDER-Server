package ac.kr.hufs.wider.model.Service;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

import ac.kr.hufs.wider.model.Entity.BloomProgressStats;

public interface StatsService {
    // 통계 기록 생성
    BloomProgressStats createStats(BloomProgressStats stats);
    
    // ID로 통계 조회
    Optional<BloomProgressStats> getStatsById(Long id);
    
    // 사용자 ID로 통계 목록 조회
    List<BloomProgressStats> getStatsByUserId(String userId);
    
    // 세션 ID로 통계 조회
    Optional<BloomProgressStats> getStatsBySessionId(String sessionId);
    
    // 사용자 ID와 월로 통계 조회
    List<BloomProgressStats> getStatsByUserIdAndMonth(String userId, LocalDate month);
    
    // 통계 업데이트
    BloomProgressStats updateStats(BloomProgressStats stats);
    
    // 통계 삭제
    void deleteStats(Long id);
    
    // 사용자의 모든 통계 삭제
    void deleteStatsByUserId(String userId);
} 