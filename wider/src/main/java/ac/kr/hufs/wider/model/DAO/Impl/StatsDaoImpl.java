package ac.kr.hufs.wider.model.DAO.Impl;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import ac.kr.hufs.wider.model.DAO.StatsDao;
import ac.kr.hufs.wider.model.Entity.BloomProgressStats;
import ac.kr.hufs.wider.model.Repository.StatsRepository;

@Service
public class StatsDaoImpl implements StatsDao {
    @Autowired
    private StatsRepository statsRepository;

    @Override
    public BloomProgressStats save(BloomProgressStats stats) {
        return statsRepository.save(stats);
    }

    @Override
    public Optional<BloomProgressStats> findById(Long id) {
        return statsRepository.findById(id);
    }

    @Override
    public List<BloomProgressStats> findByUser_UserId(String userId) {
        return statsRepository.findByUser_UserId(userId);
    }

    @Override
    public Optional<BloomProgressStats> findBySession_SessionId(String sessionId) {
        return statsRepository.findBySession_SessionId(sessionId);
    }

    @Override
    public List<BloomProgressStats> findByUser_UserIdAndCompletedMonth(String userId, LocalDate month) {
        return statsRepository.findByUser_UserIdAndCompletedMonth(userId, month);
    }

    @Override
    public boolean existsById(Long id) {
        return statsRepository.existsById(id);
    }

    @Override
    public void deleteById(Long id) {
        statsRepository.deleteById(id);
    }

    @Override
    public void deleteAll(List<BloomProgressStats> stats) {
        statsRepository.deleteAll(stats);
    }
} 