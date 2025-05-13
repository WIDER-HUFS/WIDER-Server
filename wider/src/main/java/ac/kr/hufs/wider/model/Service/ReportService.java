package ac.kr.hufs.wider.model.Service;

import java.util.List;
import java.util.Optional;

import ac.kr.hufs.wider.model.Entity.Report;

public interface ReportService {
    // 리포트 생성
    Report createReport(Report report);
    
    // 리포트 ID로 리포트 조회
    Optional<Report> getReportById(String reportId);
    
    // 세션 ID로 리포트 목록 조회
    List<Report> getReportsBySessionId(String sessionId);
    
    // 사용자 ID로 리포트 목록 조회
    List<Report> getReportsByUserId(String userId);
    
    // 리포트 업데이트
    Report updateReport(Report report);
    
    // 리포트 삭제
    void deleteReport(String reportId);
    
    // 세션의 모든 리포트 삭제
    void deleteReportsBySessionId(String sessionId);
} 