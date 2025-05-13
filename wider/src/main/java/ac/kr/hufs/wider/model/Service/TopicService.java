package ac.kr.hufs.wider.model.Service;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

import ac.kr.hufs.wider.model.Entity.DailyTopic;

public interface TopicService {
    // 주제 생성
    DailyTopic createTopic(DailyTopic topic);
    
    // 날짜로 주제 조회
    Optional<DailyTopic> getTopicByDate(LocalDate date);
    
    // 모든 주제 조회
    List<DailyTopic> getAllTopics();
    
    // 주제 업데이트
    DailyTopic updateTopic(DailyTopic topic);
    
    // 주제 삭제
    void deleteTopic(LocalDate date);
    
    // 오늘의 주제 조회
    Optional<DailyTopic> getTodayTopic();
} 