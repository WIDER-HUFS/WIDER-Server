package ac.kr.hufs.wider.controller;

import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/health")
public class HealthCheckController {
    @GetMapping("/check")
    @CrossOrigin(origins = "*")
    public String healthCheck() {
        return "OK";
    }
}