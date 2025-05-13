package ac.kr.hufs.wider.model.Service.impl;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import ac.kr.hufs.wider.model.DAO.TopicDao;
import ac.kr.hufs.wider.model.Entity.DailyTopic;
import ac.kr.hufs.wider.model.Service.TopicService;

@Service
@Transactional
public class TopicServiceImpl implements TopicService {

    private final TopicDao topicDao;

    @Autowired
    public TopicServiceImpl(TopicDao topicDao) {
        this.topicDao = topicDao;
    }

    @Override
    public DailyTopic createTopic(DailyTopic topic) {
        return topicDao.save(topic);
    }

    @Override
    public Optional<DailyTopic> getTopicByDate(LocalDate date) {
        return topicDao.findById(date);
    }

    @Override
    public List<DailyTopic> getAllTopics() {
        return topicDao.findAll();
    }

    @Override
    public DailyTopic updateTopic(DailyTopic topic) {
        if (!topicDao.existsById(topic.getTopicDate())) {
            throw new IllegalArgumentException("Topic not found for date: " + topic.getTopicDate());
        }
        return topicDao.save(topic);
    }

    @Override
    public void deleteTopic(LocalDate date) {
        topicDao.deleteById(date);
    }

    @Override
    public Optional<DailyTopic> getTodayTopic() {
        return topicDao.findFirstByOrderByTopicDateDesc();
    }
} 