package ac.kr.hufs.wider.model.DAO.Impl;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import ac.kr.hufs.wider.model.DAO.BloomProgressStatsDao;
import ac.kr.hufs.wider.model.Entity.BloomProgressStats;
import ac.kr.hufs.wider.model.Repository.BloomProgressStatsRepository;

@Service
public class BloomProgressStatsDaoImpl implements BloomProgressStatsDao{
    @Autowired
    private BloomProgressStatsRepository bloomProgressStatsRepository;

    // @Override
    // public List<BloomProgressStats> findByUserId(String userId) {
    //     return bloomProgressStatsRepository.findByUser_UserId(userId);
    // }

    // @Override
    // public List<Map<String, Object>> findStats(int month) {
    //     return bloomProgressStatsRepository.findMonthlyBloomLevelStats(month);
    // }

    @Override
    public BloomProgressStats save(BloomProgressStats stat) {
        return bloomProgressStatsRepository.save(stat);
    }

    
}
