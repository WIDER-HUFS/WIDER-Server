package ac.kr.hufs.wider.model.Controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import ac.kr.hufs.wider.model.DTO.ConversationHistoryDTO;
import ac.kr.hufs.wider.model.Service.ChatbotService;

@RestController
@RequestMapping("/api/chatbot")
public class ChatbotController {

    @Autowired
    private ChatbotService chatbotService;

    @GetMapping("/history/{sessionId}")
    public ResponseEntity<ConversationHistoryDTO> getConversationHistory(
        @PathVariable String sessionId,
        @RequestHeader("Authorization") String token
    ) {
        ConversationHistoryDTO history = chatbotService.getConversationHistory(sessionId, token);
        return ResponseEntity.ok(history);
    }
} 