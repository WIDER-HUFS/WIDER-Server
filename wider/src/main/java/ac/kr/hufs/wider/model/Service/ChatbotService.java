package ac.kr.hufs.wider.model.Service;

import ac.kr.hufs.wider.model.DTO.ConversationHistoryDTO;

public interface ChatbotService {
    ConversationHistoryDTO getConversationHistory(String sessionId, String token);
} 