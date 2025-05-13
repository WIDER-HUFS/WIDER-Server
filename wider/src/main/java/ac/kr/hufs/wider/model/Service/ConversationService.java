package ac.kr.hufs.wider.model.Service;

import java.util.List;
import java.util.Optional;

import ac.kr.hufs.wider.model.Entity.ConversationHistory;
import ac.kr.hufs.wider.model.Entity.ConversationId;

public interface ConversationService {
    // 대화 기록 생성
    ConversationHistory createConversation(ConversationHistory conversation);
    
    // 대화 기록 조회
    Optional<ConversationHistory> getConversationById(ConversationId conversationId);
    
    // 세션 ID로 대화 기록 목록 조회
    List<ConversationHistory> getConversationsBySessionId(String sessionId);
    
    // 대화 기록 업데이트
    ConversationHistory updateConversation(ConversationHistory conversation);
    
    // 대화 기록 삭제
    void deleteConversation(ConversationId conversationId);
    
    // 세션의 모든 대화 기록 삭제
    void deleteConversationsBySessionId(String sessionId);
} 