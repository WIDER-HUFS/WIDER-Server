package ac.kr.hufs.wider.controller;

import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;

import lombok.extern.slf4j.Slf4j;

@RestController
@RequestMapping("/api/report")
@Slf4j
public class ReportController {

    @Autowired
    private RestTemplate restTemplate;

    @PostMapping("/generate/{sessionId}")
    public ResponseEntity<?> generateReport(
        @PathVariable String sessionId,
        @RequestHeader("Authorization") String token
    ) {
        String fastApiUrl = "http://127.0.0.1:8000/chat/report/generate/" + sessionId;
        // String fastApiUrl = "https://www.widerhufs.xyz/chat/report/generate/" + sessionId;
        log.info("Generating report for sessionId: {}", sessionId);

        HttpHeaders headers = new HttpHeaders();
        headers.set("Authorization", token);

        HttpEntity<String> requestEntity = new HttpEntity<>(headers);

        try {
            ResponseEntity<Map> response = restTemplate.exchange(
                fastApiUrl,
                HttpMethod.POST,
                requestEntity,
                Map.class
            );

            if (response.getStatusCode() == HttpStatus.OK && response.getBody() != null) {
                return ResponseEntity.ok(response.getBody());
            } else {
                return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Failed to generate report");
            }
        } catch (Exception e) {
            log.error("Error generating report: {}", e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body("Error: " + e.getMessage());
        }
    }

    @GetMapping("/{sessionId}")
    public ResponseEntity<?> getReport(
        @PathVariable String sessionId,
        @RequestHeader("Authorization") String token
    ) {
        String fastApiUrl = "http://127.0.0.1:8000/chat/report/" + sessionId;
        // String fastApiUrl = "https://www.widerhufs.xyz/chat/report/" + sessionId;
        log.info("Getting report for sessionId: {}", sessionId);

        HttpHeaders headers = new HttpHeaders();
        headers.set("Authorization", token);

        HttpEntity<String> requestEntity = new HttpEntity<>(headers);

        try {
            ResponseEntity<Map> response = restTemplate.exchange(
                fastApiUrl,
                HttpMethod.GET,
                requestEntity,
                Map.class
            );

            if (response.getStatusCode() == HttpStatus.OK && response.getBody() != null) {
                return ResponseEntity.ok(response.getBody());
            } else {
                return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Failed to get report");
            }
        } catch (Exception e) {
            log.error("Error getting report: {}", e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body("Error: " + e.getMessage());
        }
    }
}
