package ac.kr.hufs.wider.model.DAO;

import java.util.List;

import ac.kr.hufs.wider.model.DTO.LevelProgressResponseDTO;

public interface LevelProgressDao {
    List<LevelProgressResponseDTO> getLevelProgressByDate(String userId);
} 