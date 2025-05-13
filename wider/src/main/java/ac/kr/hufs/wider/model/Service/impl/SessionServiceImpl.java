package ac.kr.hufs.wider.model.Service.impl;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import ac.kr.hufs.wider.model.DAO.SessionLogDao;
import ac.kr.hufs.wider.model.Entity.SessionLog;
import ac.kr.hufs.wider.model.Service.SessionService;

@Service
@Transactional
public class SessionServiceImpl implements SessionService {

    private final SessionLogDao sessionLogDao;

    @Autowired
    public SessionServiceImpl(SessionLogDao sessionLogDao) {
        this.sessionLogDao = sessionLogDao;
    }

    @Override
    public SessionLog createSession(SessionLog session) {
        return sessionLogDao.save(session);
    }

    @Override
    public Optional<SessionLog> getSessionById(String sessionId) {
        return sessionLogDao.findById(sessionId);
    }

    @Override
    public List<SessionLog> getSessionsByUserId(String userId) {
        return sessionLogDao.findByUserId(userId);
    }

    @Override
    public SessionLog updateSession(SessionLog session) {
        if (!sessionLogDao.findById(session.getSessionId()).isPresent()) {
            throw new IllegalArgumentException("Session not found with id: " + session.getSessionId());
        }
        return sessionLogDao.save(session);
    }

    @Override
    public SessionLog completeSession(String sessionId) {
        SessionLog session = sessionLogDao.findById(sessionId)
            .orElseThrow(() -> new IllegalArgumentException("Session not found with id: " + sessionId));
        
        session.setCompleted(true);
        session.setCompletedAt(LocalDateTime.now());
        return sessionLogDao.save(session);
    }

    @Override
    public void deleteSession(String sessionId) {
        sessionLogDao.deleteById(sessionId);
    }

    @Override
    public void deleteSessionsByUserId(String userId) {
        List<SessionLog> sessions = getSessionsByUserId(userId);
        sessionLogDao.deleteAll(sessions);
    }
} 