package ac.kr.hufs.wider.model.Service.impl;

import java.util.List;
import java.util.Optional;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import ac.kr.hufs.wider.model.DAO.ConversationHistoryDao;
import ac.kr.hufs.wider.model.Entity.ConversationHistory;
import ac.kr.hufs.wider.model.Entity.ConversationId;
import ac.kr.hufs.wider.model.Service.ConversationService;

@Service
@Transactional
public class ConversationServiceImpl implements ConversationService {

    private final ConversationHistoryDao conversationHistoryDao;

    @Autowired
    public ConversationServiceImpl(ConversationHistoryDao conversationHistoryDao) {
        this.conversationHistoryDao = conversationHistoryDao;
    }

    @Override
    public ConversationHistory createConversation(ConversationHistory conversation) {
        return conversationHistoryDao.save(conversation);
    }

    @Override
    public Optional<ConversationHistory> getConversationById(ConversationId conversationId) {
        return conversationHistoryDao.findById(conversationId);
    }

    @Override
    public List<ConversationHistory> getConversationsBySessionId(String sessionId) {
        return conversationHistoryDao.findBySessionIdOrderByTimestampAsc(sessionId);
    }

    @Override
    public ConversationHistory updateConversation(ConversationHistory conversation) {
        if (!conversationHistoryDao.findById(conversation.getId()).isPresent()) {
            throw new IllegalArgumentException("Conversation not found with id: " + conversation.getId());
        }
        return conversationHistoryDao.save(conversation);
    }

    @Override
    public void deleteConversation(ConversationId conversationId) {
        conversationHistoryDao.deleteById(conversationId);
    }

    @Override
    public void deleteConversationsBySessionId(String sessionId) {
        List<ConversationHistory> conversations = getConversationsBySessionId(sessionId);
        conversationHistoryDao.deleteAll(conversations);
    }
} 