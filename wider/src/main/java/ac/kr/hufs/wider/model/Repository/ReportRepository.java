package ac.kr.hufs.wider.model.Repository;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import ac.kr.hufs.wider.model.Entity.Report;

@Repository
public interface ReportRepository extends JpaRepository<Report, String> {
    List<Report> findBySession_SessionId(String sessionId);
    List<Report> findByUser_UserId(String userId);
}
