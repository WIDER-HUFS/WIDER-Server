package ac.kr.hufs.wider.model.DAO;

import java.util.List;
import java.util.Optional;

import ac.kr.hufs.wider.model.Entity.Report;

public interface ReportDao {
    List<Report> findByUserId(String userId);
    List<Report> findBySessionId(String sessionId);
    Report save(Report report);
    void deleteById(String reportId);
    Optional<Report> findById(String reportId);
    void deleteAll(List<Report> reports);
}
