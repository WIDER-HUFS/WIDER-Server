package ac.kr.hufs.wider.model.Service.impl;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import ac.kr.hufs.wider.model.DAO.LevelProgressDao;
import ac.kr.hufs.wider.model.DTO.LevelProgressResponseDTO;
import ac.kr.hufs.wider.model.Service.LevelProgressService;

@Service
public class LevelProgressServiceImpl implements LevelProgressService {

    @Autowired
    private LevelProgressDao levelProgressDao;

    @Override
    public List<LevelProgressResponseDTO> getLevelProgressByDate(String userId) {
        return levelProgressDao.getLevelProgressByDate(userId);
    }
} 