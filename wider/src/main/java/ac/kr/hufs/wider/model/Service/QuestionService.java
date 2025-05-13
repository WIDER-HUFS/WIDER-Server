package ac.kr.hufs.wider.model.Service;

import java.util.List;
import java.util.Optional;

import ac.kr.hufs.wider.model.Entity.Question;
import ac.kr.hufs.wider.model.Entity.QuestionId;

public interface QuestionService {
    // 질문 생성
    Question createQuestion(Question question);
    
    // 세션 ID로 질문 목록 조회 (Bloom 레벨 순)
    List<Question> getQuestionsBySessionId(String sessionId);
    
    // 세션 ID와 Bloom 레벨로 특정 질문 조회
    Optional<Question> getQuestionBySessionIdAndBloomLevel(String sessionId, int bloomLevel);
    
    // 질문 업데이트
    Question updateQuestion(Question question);
    
    // 질문 삭제
    void deleteQuestion(QuestionId questionId);
    
    // 세션의 모든 질문 삭제
    void deleteQuestionsBySessionId(String sessionId);
} 