package ac.kr.hufs.wider.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;

import ac.kr.hufs.wider.model.DTO.ChatResponseDTO;
import ac.kr.hufs.wider.model.DTO.EndChatRequestDTO;
import ac.kr.hufs.wider.model.DTO.EndChatResponseDTO;
import ac.kr.hufs.wider.model.DTO.StartChatRequestDTO;
import ac.kr.hufs.wider.model.DTO.StartChatResponseDTO;
import ac.kr.hufs.wider.model.DTO.UserResponseRequestDTO;


@RestController
@RequestMapping("/api/chat")
public class ChatController {

    @Autowired
    private RestTemplate restTemplate;

    @PostMapping("/start")
    public ResponseEntity<?> startChat(
        @RequestHeader("Authorization") String token,
        @RequestBody StartChatRequestDTO request
    ) {
        // String fastApiUrl = "http://localhost:8000/chat/start";
        String fastApiUrl = "https://www.widerhufs.xyz/chat/start";

        HttpHeaders headers = new HttpHeaders();
        headers.set("Authorization", token);

        HttpEntity<StartChatRequestDTO> requestEntity = new HttpEntity<>(request, headers);

        try {
            ResponseEntity<StartChatResponseDTO> response = restTemplate.exchange(
                fastApiUrl,
                HttpMethod.POST,
                requestEntity,
                StartChatResponseDTO.class
            );
            
            if (response.getStatusCode() == HttpStatus.OK && response.getBody() != null) {
                return ResponseEntity.ok(response.getBody());
            } else {
                return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Invalid response from chat service");
            }
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body("Failed to communicate with chat service: " + e.getMessage());
        }
    }


    @PostMapping("/respond")
    public ResponseEntity<?> respondToQuestion(
        @RequestHeader("Authorization") String token,
        @RequestBody UserResponseRequestDTO request
    ) {
        // String fastApiUrl = "http://localhost:8000/chat/respond";
        String fastApiUrl = "https://www.widerhufs.xyz/chat/respond";
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

            if (response.getStatusCode() == HttpStatus.OK && response.getBody() != null) {
                return ResponseEntity.ok(response.getBody());
            } else {
                return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Invalid response from chat service");
            }
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body("Failed to communicate with chat service: " + e.getMessage());
        }
    }

    @PostMapping("/end")
    public ResponseEntity<?> endChat(
        @RequestHeader("Authorization") String token,
        @RequestBody EndChatRequestDTO request
    ) {
        // String fastApiUrl = "http://localhost:8000/chat/end";
        String fastApiUrl = "https://www.widerhufs.xyz/chat/end";

        HttpHeaders headers = new HttpHeaders();
        headers.set("Authorization", token);

        HttpEntity<EndChatRequestDTO> requestEntity = new HttpEntity<>(request, headers);

        return restTemplate.exchange(
            fastApiUrl,
            HttpMethod.POST,
            requestEntity,
            EndChatResponseDTO.class
        );
    }
}
//     @PostMapping
//     public ResponseEntity<?> chat(@RequestBody ChatRequest request, 
//                                 @RequestHeader("Authorization") String token) {
//         // FastAPI 서버 호출
//         String fastApiUrl = "http://localhost:8000/chat";
        
//         HttpHeaders headers = new HttpHeaders();
//         headers.set("Authorization", token); // 이미 Bearer가 포함된 토큰을 그대로 전달
        
//         HttpEntity<ChatRequest> requestEntity = new HttpEntity<>(request, headers);
        
//         ResponseEntity<ChatResponse> response = restTemplate.exchange(
//             fastApiUrl,
//             HttpMethod.POST,
//             requestEntity,
//             ChatResponse.class
//         );
        
//         return response;
//     }
// }

// @Data
// class ChatRequest {
//     private String sessionId;
//     private String userAnswer;
// }

// @Data
// class ChatResponse {
//     private String sessionId;
//     private String topicPrompt;
//     private String question;
//     private String message;
// }