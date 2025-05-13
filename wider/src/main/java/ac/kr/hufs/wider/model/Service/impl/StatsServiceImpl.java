package ac.kr.hufs.wider.model.Service.impl;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import ac.kr.hufs.wider.model.DAO.StatsDao;
import ac.kr.hufs.wider.model.Entity.BloomProgressStats;
import ac.kr.hufs.wider.model.Service.StatsService;

@Service
@Transactional
public class StatsServiceImpl implements StatsService {

    private final StatsDao statsDao;

    @Autowired
    public StatsServiceImpl(StatsDao statsDao) {
        this.statsDao = statsDao;
    }

    @Override
    public BloomProgressStats createStats(BloomProgressStats stats) {
        return statsDao.save(stats);
    }

    @Override
    public Optional<BloomProgressStats> getStatsById(Long id) {
        return statsDao.findById(id);
    }

    @Override
    public List<BloomProgressStats> getStatsByUserId(String userId) {
        return statsDao.findByUser_UserId(userId);
    }

    @Override
    public Optional<BloomProgressStats> getStatsBySessionId(String sessionId) {
        return statsDao.findBySession_SessionId(sessionId);
    }

    @Override
    public List<BloomProgressStats> getStatsByUserIdAndMonth(String userId, LocalDate month) {
        return statsDao.findByUser_UserIdAndCompletedMonth(userId, month);
    }

    @Override
    public BloomProgressStats updateStats(BloomProgressStats stats) {
        if (!statsDao.existsById(stats.getId())) {
            throw new IllegalArgumentException("Stats not found with id: " + stats.getId());
        }
        return statsDao.save(stats);
    }

    @Override
    public void deleteStats(Long id) {
        statsDao.deleteById(id);
    }

    @Override
    public void deleteStatsByUserId(String userId) {
        List<BloomProgressStats> stats = getStatsByUserId(userId);
        statsDao.deleteAll(stats);
    }
} 