package ac.kr.hufs.wider.model.Service;

import java.util.List;
import java.util.Optional;

import ac.kr.hufs.wider.model.Entity.SessionLog;

public interface SessionService {
    // 세션 생성
    SessionLog createSession(SessionLog session);
    
    // 세션 ID로 세션 조회
    Optional<SessionLog> getSessionById(String sessionId);
    
    // 사용자 ID로 세션 목록 조회
    List<SessionLog> getSessionsByUserId(String userId);
    
    // 세션 업데이트
    SessionLog updateSession(SessionLog session);
    
    // 세션 완료 처리
    SessionLog completeSession(String sessionId);
    
    // 세션 삭제
    void deleteSession(String sessionId);
    
    // 사용자의 모든 세션 삭제
    void deleteSessionsByUserId(String userId);
} 