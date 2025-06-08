package ac.kr.hufs.wider.model.Service.impl;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import ac.kr.hufs.wider.model.DTO.ConversationHistoryDTO;
import ac.kr.hufs.wider.model.DTO.ConversationMessageDTO;
import ac.kr.hufs.wider.model.Service.ChatbotService;

@Service
public class ChatbotServiceImpl implements ChatbotService {

    @Value("${chatbot.api.url}")
    private String chatbotApiUrl;

    @Autowired
    private RestTemplate restTemplate;

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