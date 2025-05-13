package ac.kr.hufs.wider.model.DAO;

import java.util.List;
import java.util.Optional;

import ac.kr.hufs.wider.model.Entity.Question;
import ac.kr.hufs.wider.model.Entity.QuestionId;

public interface QuestionDao {
    Question save(Question question);
    List<Question> findBySessionIdOrderByBloomLevelAsc(String sessionId);
    Optional<Question> findBySessionIdAndBloomLevel(String sessionId, int bloomLevel);
    boolean existsById(QuestionId questionId);
    void deleteById(QuestionId questionId);
    void deleteAll(List<Question> questions);
}
