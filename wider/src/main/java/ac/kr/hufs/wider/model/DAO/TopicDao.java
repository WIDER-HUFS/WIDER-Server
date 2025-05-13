package ac.kr.hufs.wider.model.DAO;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

import ac.kr.hufs.wider.model.Entity.DailyTopic;

public interface TopicDao {
    DailyTopic save(DailyTopic topic);
    Optional<DailyTopic> findById(LocalDate date);
    List<DailyTopic> findAll();
    boolean existsById(LocalDate date);
    void deleteById(LocalDate date);
    Optional<DailyTopic> findFirstByOrderByTopicDateDesc();
} 