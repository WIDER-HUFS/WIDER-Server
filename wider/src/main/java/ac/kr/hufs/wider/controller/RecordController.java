package ac.kr.hufs.wider.controller;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;

import ac.kr.hufs.wider.model.DTO.ConversationHistoryDTO;
import ac.kr.hufs.wider.model.DTO.RecordResponseDTO;
import ac.kr.hufs.wider.model.Service.RecordService;
import ac.kr.hufs.wider.service.JwtService;
import lombok.extern.slf4j.Slf4j;

@RestController
@RequestMapping("/api/records")
@Slf4j
public class RecordController {

    private final RecordService recordService;
    private final JwtService jwtService;
    private final RestTemplate restTemplate;
    private final String chatbotApiUrl;

    @Autowired
    public RecordController(
            RecordService recordService,
            JwtService jwtService,
            RestTemplate restTemplate,
            @Value("${chatbot.api.url}") String chatbotApiUrl) {
        this.recordService = recordService;
        this.jwtService = jwtService;
        this.restTemplate = restTemplate;
        this.chatbotApiUrl = chatbotApiUrl;
    }

    @GetMapping
    public ResponseEntity<?> getUserSessions(
            @RequestHeader("Authorization") String token) {
        try {
            String userId = jwtService.extractUserId(token);
            List<RecordResponseDTO> sessions = recordService.getUserSessions(userId);
            return ResponseEntity.ok(sessions);
        } catch (Exception e) {
            log.error("Error retrieving user sessions: {}", e.getMessage(), e);
            return ResponseEntity.badRequest().body("세션 기록을 가져오는 중 오류가 발생했습니다.");
        }
    }

    @GetMapping("/{sessionId}")
    public ResponseEntity<?> getSession(
            @PathVariable String sessionId,
            @RequestHeader("Authorization") String token) {
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

            if (response.getStatusCode() == HttpStatus.OK && response.getBody() != null) {
                return ResponseEntity.ok(response.getBody());
            } else {
                return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Invalid response from chat service");
            }
        } catch (Exception e) {
            log.error("Error retrieving session: {}", e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body("Failed to communicate with chat service: " + e.getMessage());
        }
    }
} 