package ac.kr.hufs.wider.controller;

import java.util.List;

import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import ac.kr.hufs.wider.model.DTO.MonthlyBloomLevelCountDTO;
import ac.kr.hufs.wider.model.Entity.Users;
import ac.kr.hufs.wider.model.Service.StatisticsService;

@RestController
@RequestMapping("/api/statistics")
public class StatisticsController {
    private final StatisticsService service;

    public StatisticsController(StatisticsService service) {
        this.service = service;
    }

    /** GET /api/statistics/histogram
      * @return 사용자별 월별·레벨별 Bloom 단계 건수 리스트
      */
    @GetMapping("/histogram")
    public ResponseEntity<List<MonthlyBloomLevelCountDTO>> getHistogram(
            @AuthenticationPrincipal Users currentUser) {

        String userId = currentUser.getUserId();  // Users 엔티티의 PK가 String userId 라면
        List<MonthlyBloomLevelCountDTO> data = service.getMonthlyHistogram(userId);
        return ResponseEntity.ok(data);
    }

    @GetMapping("/histogram/test")
    public ResponseEntity<List<MonthlyBloomLevelCountDTO>> getHistogramTest(
            @RequestParam String userId) {
        return ResponseEntity.ok(service.getMonthlyHistogram(userId));
    }
}
