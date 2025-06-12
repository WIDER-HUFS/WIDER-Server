package ac.kr.hufs.wider.model.Service;

import java.util.List;
import java.util.Optional;

import ac.kr.hufs.wider.model.DTO.ChatResponseDTO;
import ac.kr.hufs.wider.model.DTO.ConversationHistoryDTO;
import ac.kr.hufs.wider.model.DTO.EndChatRequestDTO;
import ac.kr.hufs.wider.model.DTO.StartChatRequestDTO;
import ac.kr.hufs.wider.model.DTO.UserResponseRequestDTO;
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

    ConversationHistoryDTO getConversationHistory(String sessionId, String token);

    ChatResponseDTO startChat(StartChatRequestDTO request, String token);
    ChatResponseDTO respondToQuestion(UserResponseRequestDTO request, String token);
    void endChat(EndChatRequestDTO request, String token);
} 