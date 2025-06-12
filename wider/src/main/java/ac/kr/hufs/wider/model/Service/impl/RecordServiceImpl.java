package ac.kr.hufs.wider.model.Service.impl;

import java.util.List;
import java.util.stream.Collectors;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import ac.kr.hufs.wider.model.DAO.SessionLogDao;
import ac.kr.hufs.wider.model.DTO.RecordResponseDTO;
import ac.kr.hufs.wider.model.Entity.SessionLog;
import ac.kr.hufs.wider.model.Service.RecordService;
import lombok.extern.slf4j.Slf4j;

@Service
@Transactional
@Slf4j
public class RecordServiceImpl implements RecordService {

    private final SessionLogDao sessionLogDao;

    @Autowired
    public RecordServiceImpl(SessionLogDao sessionLogDao) {
        this.sessionLogDao = sessionLogDao;
    }

    @Override
    public List<RecordResponseDTO> getUserSessions(String userId) {
        try {
            // 사용자의 모든 세션을 조회하고, 같은 주제에 대해 가장 최신 세션만 선택
            List<SessionLog> sessions = sessionLogDao.findLatestSessionsByUserId(userId);
            
            // SessionLog를 RecordResponseDTO로 변환
            return sessions.stream()
                .map(session -> new RecordResponseDTO(
                    session.getSessionId(),
                    session.getTopic(),
                    session.getStartedAt(),
                    session.isCompleted(),
                    session.getCompletedAt(),
                    session.getBloomLevel()
                ))
                .collect(Collectors.toList());
        } catch (Exception e) {
            log.error("Error getting user sessions: {}", e.getMessage(), e);
            throw new RuntimeException("세션 기록을 가져오는 중 오류가 발생했습니다.", e);
        }
    }
} 