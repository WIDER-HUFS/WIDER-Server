package ac.kr.hufs.wider.model.Service.impl;

import java.util.List;
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
import ac.kr.hufs.wider.model.DTO.ChatResponseDTO;
import ac.kr.hufs.wider.model.DTO.ConversationHistoryDTO;
import ac.kr.hufs.wider.model.DTO.EndChatRequestDTO;
import ac.kr.hufs.wider.model.DTO.StartChatRequestDTO;
import ac.kr.hufs.wider.model.DTO.UserResponseRequestDTO;
import ac.kr.hufs.wider.model.Entity.ConversationHistory;
import ac.kr.hufs.wider.model.Entity.ConversationId;
import ac.kr.hufs.wider.model.Service.ConversationService;
import ac.kr.hufs.wider.service.JwtService;
import lombok.extern.slf4j.Slf4j;

@Service
@Transactional
@Slf4j
public class ConversationServiceImpl implements ConversationService {

    private final ConversationHistoryDao conversationHistoryDao;
    private final RestTemplate restTemplate;
    private final JwtService jwtService;
    private final String chatbotApiUrl;

    @Autowired
    public ConversationServiceImpl(
            ConversationHistoryDao conversationHistoryDao,
            RestTemplate restTemplate,
            JwtService jwtService,
            @Value("${chatbot.api.url}") String chatbotApiUrl) {
        this.conversationHistoryDao = conversationHistoryDao;
        this.restTemplate = restTemplate;
        this.jwtService = jwtService;
        this.chatbotApiUrl = chatbotApiUrl;
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
    public ChatResponseDTO startChat(StartChatRequestDTO request, String token) {
        String fastApiUrl = chatbotApiUrl + "/chat/start";
        HttpHeaders headers = new HttpHeaders();
        headers.set("Authorization", token);

        HttpEntity<StartChatRequestDTO> requestEntity = new HttpEntity<>(request, headers);
        try {
            ResponseEntity<ChatResponseDTO> response = restTemplate.exchange(
                fastApiUrl,
                HttpMethod.POST,
                requestEntity,
                ChatResponseDTO.class
            );

            if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
                return response.getBody();
            } else {
                throw new RuntimeException("Failed to start chat");
            }
        } catch (Exception e) {
            log.error("Error starting chat: {}", e.getMessage(), e);
            throw new RuntimeException("Failed to start chat: " + e.getMessage());
        }
    }

    @Override
    public ChatResponseDTO respondToQuestion(UserResponseRequestDTO request, String token) {
        String fastApiUrl = chatbotApiUrl + "/chat/respond";
        HttpHeaders headers = new HttpHeaders();
        headers.set("Authorization", token);

        HttpEntity<UserResponseRequestDTO> requestEntity = new HttpEntity<>(request, headers);
        try {
            ResponseEntity<ChatResponseDTO> response = restTemplate.exchange(
                fastApiUrl,
                HttpMethod.POST,
                requestEntity,
                ChatResponseDTO.class
            );

            if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
                return response.getBody();
            } else {
                throw new RuntimeException("Failed to process response");
            }
        } catch (Exception e) {
            log.error("Error processing response: {}", e.getMessage(), e);
            throw new RuntimeException("Failed to process response: " + e.getMessage());
        }
    }

    @Override
    public ConversationHistoryDTO getConversationHistory(String sessionId, String token) {
        String fastApiUrl = String.format("%s/chat/history/%s", chatbotApiUrl, sessionId);
        HttpHeaders headers = new HttpHeaders();
        headers.set("Authorization", token);

        HttpEntity<?> requestEntity = new HttpEntity<>(headers);
        try {
            ResponseEntity<ConversationHistoryDTO> response = restTemplate.exchange(
                fastApiUrl,
                HttpMethod.GET,
                requestEntity,
                ConversationHistoryDTO.class
            );

            if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
                return response.getBody();
            } else {
                throw new RuntimeException("Failed to get conversation history");
            }
        } catch (Exception e) {
            log.error("Error getting conversation history: {}", e.getMessage(), e);
            throw new RuntimeException("Failed to get conversation history: " + e.getMessage());
        }
    }

    @Override
    public void endChat(EndChatRequestDTO request, String token) {
        String fastApiUrl = chatbotApiUrl + "/chat/end";
        HttpHeaders headers = new HttpHeaders();
        headers.set("Authorization", token);

        HttpEntity<EndChatRequestDTO> requestEntity = new HttpEntity<>(request, headers);
        try {
            ResponseEntity<Void> response = restTemplate.exchange(
                fastApiUrl,
                HttpMethod.POST,
                requestEntity,
                Void.class
            );

            if (!response.getStatusCode().is2xxSuccessful()) {
                throw new RuntimeException("Failed to end chat");
            }
        } catch (Exception e) {
            log.error("Error ending chat: {}", e.getMessage(), e);
            throw new RuntimeException("Failed to end chat: " + e.getMessage());
        }
    }
} 