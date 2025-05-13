package ac.kr.hufs.wider.model.Service.impl;

import java.util.List;
import java.util.Optional;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import ac.kr.hufs.wider.model.DAO.ReportDao;
import ac.kr.hufs.wider.model.Entity.Report;
import ac.kr.hufs.wider.model.Service.ReportService;

@Service
@Transactional
public class ReportServiceImpl implements ReportService {

    private final ReportDao reportDao;

    @Autowired
    public ReportServiceImpl(ReportDao reportDao) {
        this.reportDao = reportDao;
    }

    @Override
    public Report createReport(Report report) {
        return reportDao.save(report);
    }

    @Override
    public Optional<Report> getReportById(String reportId) {
        return reportDao.findById(reportId);
    }

    @Override
    public List<Report> getReportsBySessionId(String sessionId) {
        return reportDao.findBySessionId(sessionId);
    }

    @Override
    public List<Report> getReportsByUserId(String userId) {
        return reportDao.findByUserId(userId);
    }

    @Override
    public Report updateReport(Report report) {
        if (!reportDao.findById(report.getReportId()).isPresent()) {
            throw new IllegalArgumentException("Report not found with id: " + report.getReportId());
        }
        return reportDao.save(report);
    }

    @Override
    public void deleteReport(String reportId) {
        reportDao.deleteById(reportId);
    }

    @Override
    public void deleteReportsBySessionId(String sessionId) {
        List<Report> reports = getReportsBySessionId(sessionId);
        reportDao.deleteAll(reports);
    }
} 