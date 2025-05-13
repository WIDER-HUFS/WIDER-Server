package ac.kr.hufs.wider.model.DAO.Impl;

import java.util.List;
import java.util.Optional;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import ac.kr.hufs.wider.model.DAO.ConversationHistoryDao;
import ac.kr.hufs.wider.model.Entity.ConversationHistory;
import ac.kr.hufs.wider.model.Entity.ConversationId;
import ac.kr.hufs.wider.model.Repository.ConversationHistoryRepository;

@Service
public class ConversationHistoryDaoImpl implements ConversationHistoryDao{
    @Autowired
    private ConversationHistoryRepository conversationHistoryRepository;

    @Override
    public int countBySession(String sessionId) {
        return conversationHistoryRepository.countById_SessionId(sessionId);
    }

    @Override
    public List<ConversationHistory> findAll(String sessionId) {
        return conversationHistoryRepository.findById_SessionIdOrderById_MessageOrderAsc(sessionId);
    }

    @Override
    public ConversationHistory save(ConversationHistory history) {
        return conversationHistoryRepository.save(history);
    }

    @Override
    public Optional<ConversationHistory> findById(ConversationId id) {
        return conversationHistoryRepository.findById(id);
    }

    @Override
    public List<ConversationHistory> findBySessionIdOrderByTimestampAsc(String sessionId) {
        return conversationHistoryRepository.findById_SessionIdOrderById_MessageOrderAsc(sessionId);
    }

    @Override
    public void deleteById(ConversationId id) {
        conversationHistoryRepository.deleteById(id);
    }

    @Override
    public void deleteAll(List<ConversationHistory> conversations) {
        conversationHistoryRepository.deleteAll(conversations);
    }
}
