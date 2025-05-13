package ac.kr.hufs.wider.model.DAO.Impl;

import java.util.List;
import java.util.Optional;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import ac.kr.hufs.wider.model.DAO.QuestionDao;
import ac.kr.hufs.wider.model.Entity.Question;
import ac.kr.hufs.wider.model.Entity.QuestionId;
import ac.kr.hufs.wider.model.Repository.QuestionRepository;

@Service
public class QuestionDaoImpl implements QuestionDao {
    @Autowired
    private QuestionRepository questionRepository;

    @Override
    public Question save(Question question) {
        return questionRepository.save(question);
    }

    @Override
    public List<Question> findBySessionIdOrderByBloomLevelAsc(String sessionId) {
        return questionRepository.findBySessionIdOrderByBloomLevelAsc(sessionId);
    }

    @Override
    public Optional<Question> findBySessionIdAndBloomLevel(String sessionId, int bloomLevel) {
        return questionRepository.findBySessionIdAndBloomLevel(sessionId, bloomLevel);
    }

    @Override
    public boolean existsById(QuestionId questionId) {
        return questionRepository.existsById(questionId);
    }

    @Override
    public void deleteById(QuestionId questionId) {
        questionRepository.deleteById(questionId);
    }

    @Override
    public void deleteAll(List<Question> questions) {
        questionRepository.deleteAll(questions);
    }
}
