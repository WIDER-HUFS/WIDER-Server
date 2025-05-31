package ac.kr.hufs.wider.model.Service;

import ac.kr.hufs.wider.model.DTO.MonthlyBloomLevelCountDTO;
import ac.kr.hufs.wider.model.Repository.BloomProgressStatsRepository;
import org.springframework.stereotype.Service;
import java.util.List;

@Service
public class StatisticsService {
    private final BloomProgressStatsRepository repo;

    public StatisticsService(BloomProgressStatsRepository repo) {
        this.repo = repo;
    }

    /** 로그인된 사용자(userId)의 월별·레벨별 집계 데이터를 DTO로 조회 */
    public List<MonthlyBloomLevelCountDTO> getMonthlyHistogram(String userId) {
        return repo.findMonthlyBloomLevelStatsByUser(userId);
    }
}
