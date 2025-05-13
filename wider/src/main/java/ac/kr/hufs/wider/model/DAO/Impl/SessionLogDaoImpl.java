package ac.kr.hufs.wider.model.DAO.Impl;

import java.util.List;
import java.util.Optional;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import ac.kr.hufs.wider.model.DAO.SessionLogDao;
import ac.kr.hufs.wider.model.Entity.SessionLog;
import ac.kr.hufs.wider.model.Repository.SessionLogRepository;

@Service
public class SessionLogDaoImpl implements SessionLogDao{
    @Autowired
    private SessionLogRepository sessionLogRepository;

    @Override
    public Optional<SessionLog> findById(String sessionId) {
        return sessionLogRepository.findById(sessionId);
    }

    @Override
    public List<SessionLog> findByUserId(String userId) {
        return sessionLogRepository.findByUser_UserId(userId);
    }

    @Override
    public SessionLog save(SessionLog log) {
        return sessionLogRepository.save(log);
    }

    @Override
    public void deleteById(String sessionId) {
        sessionLogRepository.deleteById(sessionId);
    }

    @Override
    public void deleteAll(List<SessionLog> sessions) {
        sessionLogRepository.deleteAll(sessions);
    }
}
