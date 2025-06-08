package ac.kr.hufs.wider.model.Service.impl;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.client.RestTemplate;

import ac.kr.hufs.wider.model.DAO.ConversationHistoryDao;
import ac.kr.hufs.wider.model.DTO.ConversationHistoryDTO;
import ac.kr.hufs.wider.model.DTO.ConversationMessageDTO;
import ac.kr.hufs.wider.model.Entity.ConversationHistory;
import ac.kr.hufs.wider.model.Entity.ConversationId;
import ac.kr.hufs.wider.model.Service.ConversationService;

@Service
@Transactional
public class ConversationServiceImpl implements ConversationService {

    private final ConversationHistoryDao conversationHistoryDao;

    @Value("${chatbot.api.url}")
    private String chatbotApiUrl;

    @Autowired
    private RestTemplate restTemplate;

    @Autowired
    public ConversationServiceImpl(ConversationHistoryDao conversationHistoryDao) {
        this.conversationHistoryDao = conversationHistoryDao;
    }

    @Override
    public ConversationHistory createConversation(ConversationHistory conversation) {
        return conversationHistoryDao.save(conversation);
    }

    @Override
    public Optional<ConversationHistory> getConversationById(ConversationId conversationId) {
        return conversationHistoryDao.findById(conversationId);
    }

    @Override
    public List<ConversationHistory> getConversationsBySessionId(String sessionId) {
        return conversationHistoryDao.findBySessionIdOrderByTimestampAsc(sessionId);
    }

    @Override
    public ConversationHistory updateConversation(ConversationHistory conversation) {
        if (!conversationHistoryDao.findById(conversation.getId()).isPresent()) {
            throw new IllegalArgumentException("Conversation not found with id: " + conversation.getId());
        }
        return conversationHistoryDao.save(conversation);
    }

    @Override
    public void deleteConversation(ConversationId conversationId) {
        conversationHistoryDao.deleteById(conversationId);
    }

    @Override
    public void deleteConversationsBySessionId(String sessionId) {
        List<ConversationHistory> conversations = getConversationsBySessionId(sessionId);
        conversationHistoryDao.deleteAll(conversations);
    }

    @Override
    public ConversationHistoryDTO getConversationHistory(String sessionId, String token) {
        try {
            HttpHeaders headers = new HttpHeaders();
            headers.set("Authorization", "Bearer " + token);
            
            HttpEntity<?> entity = new HttpEntity<>(headers);
            
            ResponseEntity<Map> response = restTemplate.exchange(
                chatbotApiUrl + "/chat/history/" + sessionId,
                HttpMethod.GET,
                entity,
                Map.class
            );
            
            Map<String, Object> responseBody = response.getBody();
            if (responseBody == null) {
                throw new RuntimeException("Failed to get conversation history");
            }
            
            ConversationHistoryDTO history = new ConversationHistoryDTO();
            history.setSessionId((String) responseBody.get("session_id"));
            
            List<Map<String, Object>> messages = (List<Map<String, Object>>) responseBody.get("messages");
            List<ConversationMessageDTO> messageDTOs = new ArrayList<>();
            
            for (Map<String, Object> message : messages) {
                ConversationMessageDTO messageDTO = new ConversationMessageDTO();
                messageDTO.setSpeaker((String) message.get("speaker"));
                messageDTO.setContent((String) message.get("content"));
                messageDTO.setTimestamp((String) message.get("timestamp"));
                messageDTO.setMessageOrder(((Number) message.get("message_order")).intValue());
                messageDTOs.add(messageDTO);
            }
            
            history.setMessages(messageDTOs);
            return history;
            
        } catch (Exception e) {
            throw new RuntimeException("Failed to get conversation history: " + e.getMessage(), e);
        }
    }
} 