package ac.kr.hufs.wider.model.DAO.Impl;

import java.util.List;
import java.util.Optional;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import ac.kr.hufs.wider.model.DAO.ReportDao;
import ac.kr.hufs.wider.model.Entity.Report;
import ac.kr.hufs.wider.model.Repository.ReportRepository;

@Service
public class ReportDaoImpl implements ReportDao{
    @Autowired
    private ReportRepository reportRepository;

    @Override
    public void deleteById(String reportId) {
        reportRepository.deleteById(reportId);
    }

    @Override
    public List<Report> findBySessionId(String sessionId) {
        return reportRepository.findBySession_SessionId(sessionId);
    }

    @Override
    public List<Report> findByUserId(String userId) {
        return reportRepository.findByUser_UserId(userId);
    }

    @Override
    public Report save(Report report) {
        return reportRepository.save(report);
    }

    @Override
    public Optional<Report> findById(String reportId) {
        return reportRepository.findById(reportId);
    }

    @Override
    public void deleteAll(List<Report> reports) {
        reportRepository.deleteAll(reports);
    }
}
