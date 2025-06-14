package ac.kr.hufs.wider.controller;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import ac.kr.hufs.wider.model.DTO.LevelProgressResponseDTO;
import ac.kr.hufs.wider.model.Service.LevelProgressService;
import ac.kr.hufs.wider.service.JwtService;
import lombok.extern.slf4j.Slf4j;

@RestController
@RequestMapping("/api/level-progress")
@Slf4j
public class LevelProgressController {

    private final LevelProgressService levelProgressService;
    private final JwtService jwtService;

    @Autowired
    public LevelProgressController(
            LevelProgressService levelProgressService,
            JwtService jwtService) {
        this.levelProgressService = levelProgressService;
        this.jwtService = jwtService;
    }

    @GetMapping
    public ResponseEntity<?> getLevelProgressByDate(
            @RequestHeader("Authorization") String token) {
        try {
            String userId = jwtService.extractUserId(token);
            List<LevelProgressResponseDTO> progress = levelProgressService.getLevelProgressByDate(userId);
            return ResponseEntity.ok(progress);
        } catch (Exception e) {
            log.error("Error retrieving level progress: {}", e.getMessage(), e);
            return ResponseEntity.badRequest().body("레벨 진행도를 가져오는 중 오류가 발생했습니다.");
        }
    }
} 