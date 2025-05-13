package ac.kr.hufs.wider.model.DAO.Impl;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import ac.kr.hufs.wider.model.DAO.TopicDao;
import ac.kr.hufs.wider.model.Entity.DailyTopic;
import ac.kr.hufs.wider.model.Repository.TopicRepository;

@Service
public class TopicDaoImpl implements TopicDao {
    @Autowired
    private TopicRepository topicRepository;

    @Override
    public DailyTopic save(DailyTopic topic) {
        return topicRepository.save(topic);
    }

    @Override
    public Optional<DailyTopic> findById(LocalDate date) {
        return topicRepository.findById(date);
    }

    @Override
    public List<DailyTopic> findAll() {
        return topicRepository.findAll();
    }

    @Override
    public boolean existsById(LocalDate date) {
        return topicRepository.existsById(date);
    }

    @Override
    public void deleteById(LocalDate date) {
        topicRepository.deleteById(date);
    }

    @Override
    public Optional<DailyTopic> findFirstByOrderByTopicDateDesc() {
        return topicRepository.findFirstByOrderByTopicDateDesc();
    }
} 